from flask import Blueprint, request, jsonify, current_app
from twilio.rest import Client
import warnings

send_bp = Blueprint('send', __name__)

@send_bp.route("/", methods=["POST"])
def send_message():
    data: dict = request.get_json()
    to_number = data.get("to")
    body = data.get("body")

    if not to_number or not body:
        warnings.warn("Bot endpoint '/send' called without 'to' or 'body'")
        return jsonify({"error": "Missing 'to' or 'body'"}), 400

    try:
        client = Client(current_app.config["TWILIO_ACCOUNT_SID"], current_app.config["TWILIO_AUTH_TOKEN"])
        message = client.messages.create(
            body=body,
            from_=current_app.config["TWILIO_WHATSAPP_NUMBER"],
            to=f"whatsapp:{to_number}"
        )
        return jsonify({"sid": message.sid, "status": message.status}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
