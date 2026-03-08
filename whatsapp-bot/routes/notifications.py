from flask import Blueprint, request, jsonify, current_app
from meta_whatsapp_service import MetaWhatsAppService
import warnings
import re

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route("/send", methods=["POST"])
def send_notification():
    """发送WhatsApp通知消息"""
    data = request.get_json()
    phone_number = data.get("phone_number")
    message = data.get("message", "")
    template_name = data.get("template_name", "hello_world")
    template_lang = data.get("template_lang", "en_US") 
    
    # 如果模板名称为空，禁用模板发送
    if not template_name or template_name.strip() == "":
        template_name = None
    
    # 验证必要参数
    if not phone_number:
        return jsonify({"error": "缺少电话号码参数"}), 400
    
    # 规范化电话号码
    clean_number = re.sub(r'\D', '', str(phone_number))
    if len(clean_number) == 8:  # 本地8位（例如SG），自动加国家码65
        clean_number = '65' + clean_number
    
    try:
        meta_service = MetaWhatsAppService()
        
        # 如果禁用了模板，直接发送文本消息
        if template_name is None:
            if message:
                message_result = meta_service.send_message(clean_number, message)
                from routes.webhook import log_to_file
                log_to_file(f"📤 直接发送文本消息到 {clean_number}: {message_result}")
                
                if isinstance(message_result, dict) and 'error' not in message_result:
                    return jsonify({
                        "status": "success",
                        "message": "文本通知发送成功",
                        "message_result": message_result
                    }), 200
                else:
                    return jsonify({
                        "status": "error",
                        "message": "通知发送失败",
                        "error": message_result
                    }), 500
            else:
                return jsonify({
                    "status": "error",
                    "message": "没有提供消息内容"
                }), 400
        
        # 先发送模板消息（打开24小时窗口）
        template_result = meta_service.send_template_message(
            clean_number, 
            template_name, 
            template_lang
        )
        
        # 记录日志
        from routes.webhook import log_to_file
        log_to_file(f"📤 发送模板消息到 {clean_number}: {template_result}")
        
        if isinstance(template_result, dict) and 'error' not in template_result:
            # 模板发送成功，现在发送文本消息
            if message:
                # 等待一小段时间确保模板消息处理完成
                import time
                time.sleep(1)
                
                message_result = meta_service.send_message(clean_number, message)
                log_to_file(f"📤 发送文本消息到 {clean_number}: {message_result}")
                
                if isinstance(message_result, dict) and 'error' not in message_result:
                    return jsonify({
                        "status": "success",
                        "message": "通知发送成功",
                        "template_result": template_result,
                        "message_result": message_result
                    }), 200
                else:
                    return jsonify({
                        "status": "partial_success",
                        "message": "模板发送成功，但文本消息发送失败",
                        "template_result": template_result,
                        "message_error": message_result
                    }), 200
            else:
                return jsonify({
                    "status": "success", 
                    "message": "模板通知发送成功",
                    "template_result": template_result
                }), 200
        else:
            # 模板发送失败，尝试直接发送文本消息
            if message:
                message_result = meta_service.send_message(clean_number, message)
                log_to_file(f"📤 模板失败，尝试发送文本消息到 {clean_number}: {message_result}")
                
                if isinstance(message_result, dict) and 'error' not in message_result:
                    return jsonify({
                        "status": "success",
                        "message": "文本通知发送成功",
                        "message_result": message_result
                    }), 200
                else:
                    return jsonify({
                        "status": "error",
                        "message": "通知发送失败",
                        "template_error": template_result,
                        "message_error": message_result
                    }), 500
            else:
                return jsonify({
                    "status": "error",
                    "message": "模板发送失败",
                    "error": template_result
                }), 500
                
    except Exception as e:
        from routes.webhook import log_to_file
        log_to_file(f"❌ 发送通知时异常: {str(e)}")
        return jsonify({"error": f"发送通知失败: {str(e)}"}), 500

@notifications_bp.route("/send-batch", methods=["POST"])
def send_batch_notifications():
    """批量发送通知"""
    data = request.get_json()
    phone_numbers = data.get("phone_numbers", [])
    message = data.get("message", "")
    template_name = data.get("template_name", "hello_world")
    template_lang = data.get("template_lang", "en_US")
    
    # 如果模板名称为空，禁用模板发送
    if not template_name or template_name.strip() == "":
        template_name = None
    
    if not phone_numbers or not isinstance(phone_numbers, list):
        return jsonify({"error": "缺少电话号码列表"}), 400
    
    results = []
    success_count = 0
    
    for phone_number in phone_numbers:
        try:
            # 规范化电话号码
            clean_number = re.sub(r'\D', '', str(phone_number))
            if len(clean_number) == 8:
                clean_number = '65' + clean_number
            
            meta_service = MetaWhatsAppService()
            
            # 如果禁用了模板，直接发送文本消息
            if template_name is None:
                if message:
                    message_result = meta_service.send_message(clean_number, message)
                    if isinstance(message_result, dict) and 'error' not in message_result:
                        results.append({
                            "phone_number": clean_number,
                            "status": "success",
                            "message_result": message_result
                        })
                        success_count += 1
                    else:
                        results.append({
                            "phone_number": clean_number,
                            "status": "failed",
                            "error": message_result
                        })
                else:
                    results.append({
                        "phone_number": clean_number,
                        "status": "failed",
                        "error": "没有提供消息内容"
                    })
            else:
                # 先发送模板消息（打开24小时窗口）
                template_result = meta_service.send_template_message(
                    clean_number, 
                    template_name, 
                    template_lang
                )
                
                if isinstance(template_result, dict) and 'error' not in template_result:
                    # 模板成功，现在发送文本消息
                    if message:
                        # 等待一小段时间确保模板消息处理完成
                        import time
                        time.sleep(1)
                        
                        message_result = meta_service.send_message(clean_number, message)
                        
                        if isinstance(message_result, dict) and 'error' not in message_result:
                            results.append({
                                "phone_number": clean_number,
                                "status": "success",
                                "template_result": template_result,
                                "message_result": message_result
                            })
                        else:
                            results.append({
                                "phone_number": clean_number,
                                "status": "partial_success",
                                "template_result": template_result,
                                "message_error": message_result
                            })
                        success_count += 1
                    else:
                        results.append({
                            "phone_number": clean_number,
                            "status": "success",
                            "template_result": template_result
                        })
                        success_count += 1
                else:
                    # 模板失败，尝试直接发送文本消息
                    if message:
                        message_result = meta_service.send_message(clean_number, message)
                        if isinstance(message_result, dict) and 'error' not in message_result:
                            results.append({
                                "phone_number": clean_number,
                                "status": "success",
                                "message_result": message_result
                            })
                            success_count += 1
                        else:
                            results.append({
                                "phone_number": clean_number,
                                "status": "failed",
                                "template_error": template_result,
                                "message_error": message_result
                            })
                    else:
                        results.append({
                            "phone_number": clean_number,
                            "status": "failed",
                            "error": template_result
                        })
                
        except Exception as e:
            results.append({
                "phone_number": phone_number,
                "status": "error",
                "error": str(e)
            })
    
    return jsonify({
        "status": "completed",
        "total": len(phone_numbers),
        "success_count": success_count,
        "failed_count": len(phone_numbers) - success_count,
        "results": results
    }), 200


@notifications_bp.route("/notify-target-change", methods=["POST"])
def notify_target_change():
    """在门户更新目标后，通知参与者新目标。
    Body:
      - phone_number (可选，若提供则优先使用)
      - full_name (可选，仅用于文案称呼)
      - target_min_hr (必填)
      - target_duration_week (必填)
      - template_lang (可选，默认 en_US；可传 zh_CN)
    """
    data = request.get_json() or {}
    phone_number = data.get("phone_number", "")
    full_name = data.get("full_name") or "用户"
    target_min_hr = data.get("target_min_hr")
    target_duration_week = data.get("target_duration_week")
    template_lang = data.get("template_lang", "en_US")

    if target_min_hr is None or target_duration_week is None:
        return jsonify({"error": "缺少目标参数 target_min_hr 或 target_duration_week"}), 400

    clean_number = re.sub(r'\D', '', str(phone_number)) if phone_number else ""
    if clean_number and len(clean_number) == 8:
        clean_number = '65' + clean_number

    try:
        meta_service = MetaWhatsAppService()
        # 模板开窗（节流情况下不会报错）
        if clean_number:
            meta_service.send_template_message(clean_number, 'hello_world', template_lang)

        # 本地化文案
        zh_msg = (
            f"Hi {full_name}! 您的新一周运动目标如下：\n"
            f"- 目标最小心率：{target_min_hr} bpm\n"
            f"- 每周目标时长：{target_duration_week} 分钟\n"
            f"如有不适或疑问，请及时反馈。加油！💪"
        )
        en_msg = (
            f"Hi {full_name}! Your targets for the coming week:\n"
            f"- Target minimum heart rate: {target_min_hr} bpm\n"
            f"- Weekly target duration: {target_duration_week} minutes\n"
            f"Let us know if you have any concerns. You’ve got this! 💪"
        )
        body = en_msg if template_lang == 'en_US' else zh_msg

        if clean_number:
            send_res = meta_service.send_message(clean_number, body)
        else:
            send_res = {"warning": "no_phone_number"}
        return jsonify({
            "status": "success",
            "message_result": send_res
        }), 200
    except Exception as e:
        from routes.webhook import log_to_file
        log_to_file(f"❌ 目标变更通知异常: {str(e)}")
        return jsonify({"error": f"目标变更通知失败: {str(e)}"}), 500
