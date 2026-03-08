from flask import Blueprint, request, jsonify, current_app
from twilio.rest import Client
import warnings

# 导入Meta WhatsApp服务
from meta_whatsapp_service import MetaWhatsAppService

send_bp = Blueprint('send', __name__)

@send_bp.route("/", methods=["POST"])
def send_message():
    data: dict = request.get_json()
    to_number = data.get("to")
    body = data.get("body")

    if not to_number or not body:
        warnings.warn("Bot endpoint '/send' called without 'to' or 'body'")
        return jsonify({"error": "缺少 'to' 或 'body' 参数"}), 400

    # 根据配置选择API提供商
    if current_app.config.get('USE_META_API', True):
        return send_via_meta(to_number, body)
    else:
        return send_via_twilio(to_number, body)

def send_via_meta(to_number: str, body: str):
    """通过Meta API发送消息"""
    try:
        meta_service = MetaWhatsAppService()
        result = meta_service.send_message(to_number, body)
        
        if "error" in result:
            return jsonify({"error": result["error"]}), 500
        
        return jsonify({
            "message_id": result.get("messages", [{}])[0].get("id"),
            "status": "sent",
            "provider": "meta"
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Meta API发送失败: {str(e)}"}), 500

def send_via_twilio(to_number: str, body: str):
    """通过Twilio API发送消息"""
    try:
        client = Client(current_app.config["TWILIO_ACCOUNT_SID"], current_app.config["TWILIO_AUTH_TOKEN"])
        message = client.messages.create(
            body=body,
            from_=current_app.config["TWILIO_WHATSAPP_NUMBER"],
            to=f"whatsapp:{to_number}"
        )
        return jsonify({
            "sid": message.sid, 
            "status": message.status,
            "provider": "twilio"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Twilio API发送失败: {str(e)}"}), 500
