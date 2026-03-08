import requests
from requests.exceptions import HTTPError
from flask import Blueprint, request, jsonify, current_app, make_response
from twilio.twiml.messaging_response import MessagingResponse
import warnings
import datetime
import os
import json
import re

# 导入Meta WhatsApp服务
from meta_whatsapp_service import MetaWhatsAppService

# ✅ 写入调试日志到文件
def log_to_file(msg):
    # 使用当前目录下的日志文件，兼容 Windows 和 Linux
    log_path = os.path.join(os.getcwd(), "whatsapp_debug.log")
    with open(log_path, "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().isoformat()
        f.write(f"[{timestamp}] {msg}\n")

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route("/", methods=["GET", "POST"])
def webhook():
    """处理Meta和Twilio的webhook"""
    if request.method == "GET":
        # Meta webhook验证
        if current_app.config.get('USE_META_API', True):
            return handle_meta_verification()
        else:
            return jsonify({"error": "Meta API未启用"}), 400
    
    elif request.method == "POST":
        if current_app.config.get('USE_META_API', True):
            return handle_meta_message()
        else:
            return handle_twilio_message()

def handle_meta_verification():
    """处理Meta webhook验证"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    log_to_file(f"🔐 Meta webhook验证 - Mode: {mode}, Token: {token}, Challenge: {challenge}")
    
    meta_service = MetaWhatsAppService()
    verification_result = meta_service.verify_webhook(mode, token, challenge)
    
    if verification_result:
        log_to_file("✅ Meta webhook验证成功")
        return challenge
    else:
        log_to_file("❌ Meta webhook验证失败")
        return jsonify({"error": "验证失败"}), 403

def handle_meta_message():
    """处理Meta WhatsApp消息"""
    # 验证签名
    signature = request.headers.get('X-Hub-Signature-256')
    if signature:
        meta_service = MetaWhatsAppService()
        if not meta_service.verify_signature(request.get_data(as_text=True), signature):
            log_to_file("❌ Meta webhook签名验证失败")
            return jsonify({"error": "签名验证失败"}), 403
    else:
        # 本地/测试环境可能没有签名，记录告警但不阻断
        log_to_file("⚠️ 无签名头，按开发模式放行")
    
    try:
        data = request.get_json()
        log_to_file(f"📨 收到Meta消息: {json.dumps(data, indent=2)}")
        
        # 处理Meta的消息格式
        if 'object' in data and data['object'] == 'whatsapp_business_account':
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    if change.get('value', {}).get('messages'):
                        for message in change['value']['messages']:
                            if message.get('type') == 'text':
                                from_number = message.get('from')
                                message_body = message.get('text', {}).get('body', '')
                                
                                if from_number and message_body:
                                    return process_message(from_number, message_body)
        
        return jsonify({"status": "ok"})
        
    except Exception as e:
        log_to_file(f"❌ 处理Meta消息时出错: {str(e)}")
        return jsonify({"error": "处理消息失败"}), 500

def handle_twilio_message():
    """处理Twilio WhatsApp消息（保持原有逻辑）"""
    if request.is_json:
        data: dict = request.get_json()
    else:
        data: dict = request.form.to_dict()

    from_number = data.get("From")
    message_body = data.get("Body")

    log_to_file(f"✅ 收到Twilio消息 - From: {from_number}, Body: {message_body}")

    if not from_number or not message_body:
        log_to_file("❌ 无效的消息格式")
        return jsonify({"error": "无效的消息格式"}), 400

    return process_message(from_number, message_body)

def process_message(from_number: str, message_body: str):
    """处理消息并转发到后端"""
    # --- 严重事件识别（阈值与关键词） ---
    try:
        body_lower = (message_body or "").lower()
        # 关键词（含变体）
        emergency_keywords = [
            "chest pain",
            "breathless",
            "short of breath",
            "difficulty breathing",
            "giddy",
            "giddiness",
            "headache",
            "faint",
            "fainting",
            "muscle ache",
            "muscle pain",
            "fall",
            "fracture",
        ]
        hit_keyword = any(k in body_lower for k in emergency_keywords)

        # 血糖解析：提取形如 "xx mmol/L" 或孤立数值（带小数），做安全范围判断
        hit_glucose = False
        glucose_value = None
        try:
            import re as _re
            # 匹配 3.5 mmol/L 或 18 mmol/l 等
            m = _re.search(r"([0-9]+(?:\.[0-9]+)?)\s*mmol\s*/\s*l", body_lower)
            if m:
                glucose_value = float(m.group(1))
            else:
                # 回退：捕获消息里的第一个数字当可能的血糖（尽量保守）
                m2 = _re.search(r"([0-9]+(?:\.[0-9]+)?)", body_lower)
                if m2:
                    glucose_value = float(m2.group(1))
            if glucose_value is not None and (glucose_value < 4.0 or glucose_value > 16.0):
                hit_glucose = True
        except Exception:
            pass

        if hit_keyword or hit_glucose:
            log_to_file(f"🚨 识别到严重事件: keyword={hit_keyword}, glucose={glucose_value}")
            meta_service = MetaWhatsAppService()
            to_number = re.sub(r'\D', '', from_number or "")
            if len(to_number) == 8:
                to_number = '65' + to_number
            # 尝试模板开窗
            tpl_name = current_app.config.get('FALLBACK_TEMPLATE_NAME', 'hello_world')
            tpl_lang = current_app.config.get('FALLBACK_TEMPLATE_LANG', 'en_US')
            tpl_res = meta_service.send_template_message(to_number, tpl_name, tpl_lang)
            log_to_file(f"📤 严重事件模板发送结果: {tpl_res}")
            # 高优先级安全提示
            alert_msg = (
                "我们注意到您可能正经历紧急状况或异常血糖值。\n"
                "如果您正感到胸痛、呼吸困难、头晕、晕厥、严重肌肉疼痛/受伤等，请立即寻求医疗帮助或拨打当地急救电话。\n"
                "若情况允许，请尽快联系您的医疗团队进行指导。"
            )
            meta_service.send_message(to_number, alert_msg)
            return jsonify({"status": "ok", "emergency": True})
    except Exception as _e:
        log_to_file(f"⚠️ 严重事件识别异常: {_e}")

    payload = {
        "From": from_number,
        "Body": message_body
    }

    log_to_file(f"🔄 转发payload到 {current_app.config['FORWARD_URL']}: {payload}")

    whatsapp_msg_response = "抱歉！我们在处理您的消息时遇到了错误。"

    try:
        res = requests.post(current_app.config["FORWARD_URL"], json=payload)
        res.raise_for_status()

        content_type = res.headers.get("Content-Type", "")
        log_to_file(f"✅ 后端响应状态: {res.status_code}")
        log_to_file(f"🧾 响应头: {res.headers}")
        log_to_file(f"📦 响应体: {res.text}")

        if "application/json" in content_type:
            response_data = res.json()
            whatsapp_msg_response = response_data.get("response", whatsapp_msg_response)
        else:
            whatsapp_msg_response = res.text.strip()

    except HTTPError as err:
        log_to_file(f"❌ 转发时HTTP错误: {err}")
        warnings.warn(f"转发消息失败: {err}")
    except Exception as e:
        log_to_file(f"❌ 转发时异常: {e}")
        warnings.warn(f"转发消息时出错: {e}")

    # 根据API提供商返回不同格式的响应
    if current_app.config.get('USE_META_API', True):
        # Meta API - 直接发送消息
        meta_service = MetaWhatsAppService()
        # 规范化号码为 E.164 纯数字
        to_number = re.sub(r'\D', '', from_number or "")
        if len(to_number) == 8:  # 本地8位（例如SG），自动加国家码65
            to_number = '65' + to_number
        log_to_file(f"📟 规范化后的号码: {to_number}")
        result = meta_service.send_message(to_number, whatsapp_msg_response)
        log_to_file(f"📤 Meta API发送结果: {result}")
        if isinstance(result, dict) and 'error' in result:
            # 24h 窗口外：470/131047 等错误，自动用模板开窗再重试一次文本
            status = result.get('status')
            response_json = result.get('response') if isinstance(result.get('response'), dict) else {}
            error_obj = response_json.get('error', {}) if isinstance(response_json, dict) else {}
            error_code = error_obj.get('code')
            error_subcode = error_obj.get('error_subcode')
            log_to_file(f"❌ 回发失败详情: status={status}, code={error_code}, subcode={error_subcode}")

            should_try_template = False
            
            # 检查多种可能的24小时窗口外错误格式
            error_detail = result.get('error', '')
            
            # 1. 标准错误码检查
            if status in (400, 403) and error_code in (470, 131047):
                should_try_template = True
                log_to_file(f"🔍 检测到24h窗口外错误: 标准错误码 {error_code}")
            
            # 2. 错误消息内容检查
            elif '24' in str(error_detail).lower() or 'window' in str(error_detail).lower():
                should_try_template = True
                log_to_file(f"🔍 检测到24h窗口外错误: 错误消息包含关键词")
            
            # 3. 任何400/403错误都尝试模板（更宽松的策略）
            elif status in (400, 403):
                should_try_template = True
                log_to_file(f"🔍 检测到可能的24h窗口外错误: HTTP {status}")

            if should_try_template:
                tpl_name = current_app.config.get('FALLBACK_TEMPLATE_NAME', 'hello_world')
                tpl_lang = current_app.config.get('FALLBACK_TEMPLATE_LANG', 'en_US')
                log_to_file(f"🧪 尝试模板开窗: {tpl_name}/{tpl_lang}")
                tpl_res = meta_service.send_template_message(to_number, tpl_name, tpl_lang)
                log_to_file(f"📤 模板发送结果: {tpl_res}")
                # 模板成功则重试文本一次
                if isinstance(tpl_res, dict) and 'error' not in tpl_res:
                    log_to_file(f"✅ 模板发送成功，重试发送原消息")
                    retry_res = meta_service.send_message(to_number, whatsapp_msg_response)
                    log_to_file(f"🔁 模板后重试文本结果: {retry_res}")
                else:
                    log_to_file(f"❌ 模板发送失败: {tpl_res}")
            else:
                log_to_file(f"ℹ️ 未检测到24h窗口外错误，跳过模板发送")
        return jsonify({"status": "ok", "message_sent": True})
    else:
        # Twilio - 返回TwiML
        if whatsapp_msg_response.strip().startswith("<Response>"):
            xml_str = whatsapp_msg_response.strip()
            log_to_file("📤 TwiML响应已格式化，直接传递")
        else:
            twilio_response = MessagingResponse()
            twilio_response.message(whatsapp_msg_response)
            xml_str = str(twilio_response)
            log_to_file("📤 通过MessagingResponse生成TwiML响应")

        log_to_file(f"📤 返回给Twilio的最终XML:\n{xml_str}")

    response = make_response(xml_str)
    response.headers['Content-Type'] = 'text/xml'
    return response
