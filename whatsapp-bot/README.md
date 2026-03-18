# Whatsapp Bot Frontend for Medical Chatbot

This folder contains the WhatsApp bot frontend implementation for the Medical Chatbot application.

## Supported API Providers

- ✅ **Meta WhatsApp Business API** (Recommended)
- ✅ **Twilio WhatsApp API** (Alternative)

## Prerequisites

### Meta WhatsApp Business API (Recommended)
1. Visit [Meta for Developers](https://developers.facebook.com/)
2. Create a WhatsApp Business App
3. Obtain the necessary tokens and IDs

For detailed setup, please refer to: [META_SETUP.md](./META_SETUP.md)

### Twilio API (Alternative)
1. Visit [Twilio](https://www.twilio.com/en-us) to get an account
2. Obtain your Account SID and Auth Token

## Setup

### 1. Install Dependencies

Run the following command **in this directory** to install the required packages. Using a Python virtual environment is recommended:

```shell
pip install -r requirements.txt
```

### 2. Environment Variable Configuration

Create `.env` file and configure the necessary environment variables:

#### Meta WhatsApp Business API (Recommended)
```bash
# Meta API Configuration
META_ACCESS_TOKEN=your_meta_access_token_here
META_VERIFY_TOKEN=your_custom_verify_token_here
META_PHONE_NUMBER_ID=your_phone_number_id_here
META_BUSINESS_ACCOUNT_ID=your_business_account_id_here

# General Configuration
FORWARD_URL=http://localhost:3005/api/data/chat/message

# Use Meta API
USE_META_API=true
```

#### Twilio API (Alternative)
```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890

# General Configuration
FORWARD_URL=http://localhost:3005/api/data/chat/message

# Use Twilio API
USE_META_API=false
```

### 3. Webhook Setup

#### Meta API
1. Set the webhook URL in the Meta Developer Console: `{ROOT_URL}/webhook`
2. Set the Verify Token to match the `META_VERIFY_TOKEN` in your `.env` file
3. Subscribe to the necessary fields: `messages`, `message_deliveries`, `message_reads`

#### Twilio API
1. Set the webhook URL in the Twilio Console: `{ROOT_URL}/webhook`
2. Ensure the webhook can receive POST requests

## Test Configuration

Run the test script to verify your configuration:

```bash
python test_meta_api.py
```

## Start the WhatsApp Bot

Run the following command:

```shell
python main.py
```

## Features

- 🔄 Automatic switching between Meta/Twilio APIs
- 📨 Send and receive WhatsApp messages
- 🔐 Webhook validation and signature verification
- 📊 Detailed operational logs
- 🚀 Forwarding messages to the Backend API
- 📱 Support for Template Messages

## File Structure

```
whatsapp-bot/
├── config.py                 # Configuration file
├── main.py                   # Main application file
├── meta_whatsapp_service.py  # Meta WhatsApp service logic
├── routes/                   # Routing files
│   ├── webhook.py            # Webhook handling
│   ├── send.py               # Message sending logic
│   └── __init__.py           # Route registration
├── requirements.txt          # Python dependencies
├── META_SETUP.md             # Meta API setup guide
├── test_meta_api.py          # Configuration test script
└── README.md                 # This file
```

## Troubleshooting

### Common Issues

1. **Webhook Verification Failed**
   - Check if the Verify Token is correct
   - Ensure the webhook URL is publicly accessible (e.g., using ngrok for local dev)

2. **Message Sending Failed**
   - Verify that the API token is still valid
   - Check the phone number format (must include country code)

3. **Configuration Errors**
   - Run `python test_meta_api.py` to check settings
   - Review the log file: `whatsapp_debug.log`

## Support

If you need help:
1. Check the log files
2. Run the test scripts
3. Refer to the setup guides
4. Confirm your environment variable configurations
