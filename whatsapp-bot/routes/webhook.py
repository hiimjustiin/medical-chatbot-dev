# import requests
# from requests.exceptions import HTTPError
# from flask import Blueprint, request, jsonify, current_app
# from twilio.twiml.messaging_response import MessagingResponse
# import warnings

# webhook_bp = Blueprint('webhook', __name__)

# @webhook_bp.route("/", methods=["POST"])
# def receive_message():
#     if not request.is_json:
#         return jsonify({"error": "Invalid content type"}), 400
    
#     data: dict = request.get_json()    
#     from_number = data.get("From")
#     message_body = data.get("Body")

#     if not from_number or not message_body:
#         return jsonify({"error": "Invalid message format"}), 400

#     payload = {
#         "from": from_number,
#         "body": message_body
#     }
    
#     # Default response, in case forwarding fails
#     # Otherwise, this will be overridden by the success response
#     whatsapp_msg_response = "Sorry! We encountered an error while processing your message."

#     try:
#         res = requests.post(current_app.config["FORWARD_URL"], json=payload)
#         res.raise_for_status()  # Raise an error for bad responses
#     except HTTPError as err:
#         warnings.warn(f"Failed to forward message: {err}")
#     except Exception as e:
#         warnings.warn(f"Error forwarding message: {e}")
#     else:
#         response_data = res.json()
#         if "response" in response_data:
#             whatsapp_msg_response = response_data["response"]
#         else:
#             warnings.warn(f"Unexpected response format: {response_data}")
    
#     whatsapp_response = MessagingResponse()
#     whatsapp_response.message(whatsapp_msg_response)
#     return str(whatsapp_response), 200
    
    
import requests
from requests.exceptions import HTTPError
from flask import Blueprint, request, jsonify, current_app
from twilio.twiml.messaging_response import MessagingResponse
import warnings

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route("/", methods=["POST"])
def receive_message():
    # ✅ 支持 Twilio 默认格式 application/x-www-form-urlencoded
    if request.is_json:
        data: dict = request.get_json()
    else:
        data: dict = request.form.to_dict()

    from_number = data.get("From")
    message_body = data.get("Body")

    if not from_number or not message_body:
        return jsonify({"error": "Invalid message format"}), 400

    payload = {
        "from": from_number,
        "body": message_body
    }

    # 默认回复
    whatsapp_msg_response = "Sorry! We encountered an error while processing your message."

    try:
        res = requests.post(current_app.config["FORWARD_URL"], json=payload)
        res.raise_for_status()
    except HTTPError as err:
        warnings.warn(f"Failed to forward message: {err}")
    except Exception as e:
        warnings.warn(f"Error forwarding message: {e}")
    else:
        response_data = res.json()
        if "response" in response_data:
            whatsapp_msg_response = response_data["response"]
        else:
            warnings.warn(f"Unexpected response format: {response_data}")

    # Twilio 要求返回 TwiML 格式
    whatsapp_response = MessagingResponse()
    whatsapp_response.message(whatsapp_msg_response)
    return str(whatsapp_response), 200
