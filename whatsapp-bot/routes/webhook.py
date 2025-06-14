import requests
from requests.exceptions import HTTPError
from flask import Blueprint, request, jsonify, current_app, make_response
from twilio.twiml.messaging_response import MessagingResponse
import warnings
import datetime

# ✅ 写入调试日志到文件
def log_to_file(msg):
    with open("/tmp/whatsapp_debug.log", "a") as f:
        timestamp = datetime.datetime.now().isoformat()
        f.write(f"[{timestamp}] {msg}\n")

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route("/", methods=["POST"])
def receive_message():
    if request.is_json:
        data: dict = request.get_json()
    else:
        data: dict = request.form.to_dict()

    from_number = data.get("From")
    message_body = data.get("Body")

    log_to_file(f"✅ Received message - From: {from_number}, Body: {message_body}")

    if not from_number or not message_body:
        log_to_file("❌ Invalid message format.")
        return jsonify({"error": "Invalid message format"}), 400

    payload = {
        "From": from_number,
        "Body": message_body
    }

    log_to_file(f"🔄 Forwarding payload to {current_app.config['FORWARD_URL']}: {payload}")

    whatsapp_msg_response = "Sorry! We encountered an error while processing your message."

    try:
        res = requests.post(current_app.config["FORWARD_URL"], json=payload)
        res.raise_for_status()

        content_type = res.headers.get("Content-Type", "")
        log_to_file(f"✅ Backend response status: {res.status_code}")
        log_to_file(f"🧾 Headers: {res.headers}")
        log_to_file(f"📦 Body: {res.text}")

        if "application/json" in content_type:
            response_data = res.json()
            whatsapp_msg_response = response_data.get("response", whatsapp_msg_response)
        else:
            whatsapp_msg_response = res.text.strip()

    except HTTPError as err:
        log_to_file(f"❌ HTTPError when forwarding: {err}")
        warnings.warn(f"Failed to forward message: {err}")
    except Exception as e:
        log_to_file(f"❌ Exception during forwarding: {e}")
        warnings.warn(f"Error forwarding message: {e}")

    # ✅ 判断是否是原生 TwiML，避免双重嵌套
    if whatsapp_msg_response.strip().startswith("<Response>"):
        xml_str = whatsapp_msg_response.strip()
        log_to_file("📤 TwiML response is already formatted. Passing through.")
    else:
        twilio_response = MessagingResponse()
        twilio_response.message(whatsapp_msg_response)
        xml_str = str(twilio_response)
        log_to_file("📤 TwiML response generated via MessagingResponse.")

    log_to_file(f"📤 Final XML returned to Twilio:\n{xml_str}")

    response = make_response(xml_str)
    response.headers['Content-Type'] = 'text/xml'
    return response
