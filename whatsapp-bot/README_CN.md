# Whatsapp Bot Frontend for Medical Chatbot

这个文件夹包含了医疗聊天机器人应用的WhatsApp机器人前端实现。

## 支持的API提供商

- ✅ **Meta WhatsApp Business API** (推荐)
- ✅ **Twilio WhatsApp API** (备选)

## 先决条件

### Meta WhatsApp Business API (推荐)
1. 访问 [Meta for Developers](https://developers.facebook.com/)
2. 创建WhatsApp Business应用
3. 获取必要的token和ID

详细设置请参考: [META_SETUP.md](./META_SETUP.md)

### Twilio API (备选)
1. 访问 [Twilio](https://www.twilio.com/en-us) 获取账户
2. 获取Account SID和Auth Token

## 设置

### 1. 安装依赖

**在此目录中**运行以下命令安装所需包。建议使用Python虚拟环境：

```shell
pip install -r requirements.txt
```

### 2. 环境变量配置

创建`.env`文件并配置必要的环境变量：

#### Meta WhatsApp Business API (推荐)
```bash
# Meta API配置
META_ACCESS_TOKEN=your_meta_access_token_here
META_VERIFY_TOKEN=your_custom_verify_token_here
META_PHONE_NUMBER_ID=your_phone_number_id_here
META_BUSINESS_ACCOUNT_ID=your_business_account_id_here

# 通用配置
FORWARD_URL=http://localhost:3005/api/data/chat/message

# 使用Meta API
USE_META_API=true
```

#### Twilio API (备选)
```bash
# Twilio配置
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890

# 通用配置
FORWARD_URL=http://localhost:3005/api/data/chat/message

# 使用Twilio API
USE_META_API=false
```

### 3. Webhook设置

#### Meta API
1. 在Meta开发者控制台设置webhook URL: `{ROOT_URL}/webhook`
2. 设置验证令牌与`.env`文件中的`META_VERIFY_TOKEN`一致
3. 订阅必要的字段: `messages`, `message_deliveries`, `message_reads`

#### Twilio API
1. 在Twilio控制台设置webhook URL: `{ROOT_URL}/webhook`
2. 确保webhook可以接收POST请求

## 测试配置

运行测试脚本验证配置：

```bash
python test_meta_api.py
```

## 启动WhatsApp机器人

运行以下命令：

```shell
python main.py
```

## 功能特性

- 🔄 自动切换Meta/Twilio API
- 📨 接收和发送WhatsApp消息
- 🔐 Webhook验证和签名验证
- 📊 详细的操作日志
- 🚀 消息转发到后端API
- 📱 支持模板消息

## 文件结构

```
whatsapp-bot/
├── config.py                 # 配置文件
├── main.py                   # 主应用文件
├── meta_whatsapp_service.py  # Meta WhatsApp服务
├── routes/                   # 路由文件
│   ├── webhook.py           # Webhook处理
│   ├── send.py              # 消息发送
│   └── __init__.py          # 路由注册
├── requirements.txt          # Python依赖
├── META_SETUP.md            # Meta API设置指南
├── test_meta_api.py         # 配置测试脚本
└── README.md                # 本文件
```

## 故障排除

### 常见问题

1. **Webhook验证失败**
   - 检查验证令牌是否正确
   - 确保webhook URL可公开访问

2. **消息发送失败**
   - 验证API token是否有效
   - 检查电话号码格式

3. **配置错误**
   - 运行`python test_meta_api.py`检查配置
   - 查看日志文件`whatsapp_debug.log`

## 支持

如需帮助，请：
1. 检查日志文件
2. 运行测试脚本
3. 参考设置指南
4. 确认环境变量配置
