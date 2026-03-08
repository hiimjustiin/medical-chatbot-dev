import os

class Config:
    # Meta WhatsApp Business API 配置
    META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN")
    META_VERIFY_TOKEN = os.environ.get("META_VERIFY_TOKEN")
    META_PHONE_NUMBER_ID = os.environ.get("META_PHONE_NUMBER_ID")
    META_BUSINESS_ACCOUNT_ID = os.environ.get("META_BUSINESS_ACCOUNT_ID")
    META_APP_SECRET = os.environ.get("META_APP_SECRET")  # 用于校验 X-Hub-Signature-256
    
    # 模板回退配置（24h 会话外）
    # 默认使用官方示例模板 hello_world/en_US，确保开箱即用
    FALLBACK_TEMPLATE_NAME = os.environ.get("FALLBACK_TEMPLATE_NAME", "hello_world")
    FALLBACK_TEMPLATE_LANG = os.environ.get("FALLBACK_TEMPLATE_LANG", "en_US")
    
    # Twilio 配置 (作为备选)
    TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
    TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER")
    
    # 通用配置 - 指向NestJS GPT服务
    FORWARD_URL = os.environ.get("FORWARD_URL", "http://localhost:3005/chat/message")
    
    # 选择使用哪个API提供商
    USE_META_API = os.environ.get("USE_META_API", "true").lower() == "true"
