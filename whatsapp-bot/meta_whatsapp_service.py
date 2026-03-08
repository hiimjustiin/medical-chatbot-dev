import requests
import json
import hmac
import hashlib
from typing import Dict, Optional
from datetime import datetime, timedelta
import os
from config import Config

class MetaWhatsAppService:
    def __init__(self):
        self.access_token = Config.META_ACCESS_TOKEN
        self.phone_number_id = Config.META_PHONE_NUMBER_ID
        self.verify_token = Config.META_VERIFY_TOKEN
        self.base_url = "https://graph.facebook.com/v18.0"
        self.app_secret = Config.META_APP_SECRET  # used for X-Hub-Signature-256 verification
        # 简单的进程内模板发送节流（同一号码24小时内只发一次模板）
        self._template_last_sent_at: Dict[str, datetime] = {}
        self._throttle_templates = os.environ.get("THROTTLE_TEMPLATES", "true").lower() in ("1", "true", "yes")
        
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verify Meta webhook (GET)"""
        if mode == "subscribe" and token == self.verify_token:
            return challenge
        return None
    
    def verify_signature(self, body: str, signature: str) -> bool:
        """Verify webhook signature (POST) using App Secret.
        If app secret is not configured, allow (useful for local testing)."""
        if not signature:
            return False
        if not self.app_secret:
            # No secret configured: do not block local/tests
            return True
            
        # signature header format: "sha256=HEX"
        try:
            scheme, expected_signature = signature.split('=', 1)
        except ValueError:
            return False
        if scheme.lower() != 'sha256':
            return False
        
        calculated_signature = hmac.new(
            self.app_secret.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(calculated_signature, expected_signature)
    
    def send_message(self, to_number: str, message: str) -> Dict:
        """Send WhatsApp text message"""
        if not self.access_token or not self.phone_number_id:
            return {"error": "Meta API configuration incomplete"}
            
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": message}
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            if response.ok:
                return response.json()
            # 尽量返回服务端的错误结构，便于上层判断 24h 窗口等
            try:
                return {"error": "http_error", "status": response.status_code, "response": response.json()}
            except Exception:
                return {"error": "http_error", "status": response.status_code, "response_text": response.text}
        except requests.exceptions.RequestException as e:
            return {"error": "request_exception", "detail": f"Failed to send message: {str(e)}"}
    
    def send_template_message(self, to_number: str, template_name: str, language_code: str = "en_US", components: list = None) -> Dict:
        """Send template message
        注意：模板消息可以随时发送，不受24小时窗口限制
        """
        if not self.access_token or not self.phone_number_id:
            return {"error": "Meta API configuration incomplete"}

        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        if components:
            payload["template"]["components"] = components
            
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            if response.ok:
                return response.json()
            
            # 处理错误响应
            try:
                error_data = response.json()
                return {"error": "http_error", "status": response.status_code, "response": error_data}
            except Exception:
                return {"error": "http_error", "status": response.status_code, "response_text": response.text}
        except requests.exceptions.RequestException as e:
            return {"error": "request_exception", "detail": f"Failed to send template message: {str(e)}"}
    
    def get_template_info(self, template_name: str) -> Dict:
        """查询模板详情（包括支持的语言代码和结构）"""
        if not self.access_token:
            return {"error": "Meta API configuration incomplete"}
        
        # 需要 Business Account ID 来查询模板
        business_account_id = Config.META_BUSINESS_ACCOUNT_ID
        if not business_account_id:
            return {"error": "META_BUSINESS_ACCOUNT_ID not configured"}
        
        url = f"{self.base_url}/{business_account_id}/message_templates"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        params = {
            "name": template_name,
            "limit": 100
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=20)
            if response.ok:
                data = response.json()
                # 查找匹配的模板
                templates = data.get("data", [])
                matching = [t for t in templates if t.get("name") == template_name]
                if matching:
                    return {"success": True, "templates": matching}
                else:
                    return {"error": f"Template '{template_name}' not found", "available": [t.get("name") for t in templates]}
            try:
                return {"error": "http_error", "status": response.status_code, "response": response.json()}
            except Exception:
                return {"error": "http_error", "status": response.status_code, "response_text": response.text}
        except requests.exceptions.RequestException as e:
            return {"error": "request_exception", "detail": f"Failed to get template info: {str(e)}"}
    
    def get_phone_number_info(self) -> Dict:
        """Get phone number info"""
        if not self.access_token or not self.phone_number_id:
            return {"error": "Meta API configuration incomplete"}
            
        url = f"{self.base_url}/{self.phone_number_id}"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get phone number info: {str(e)}"}

