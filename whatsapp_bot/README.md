## Prerequisites
* Python 3.8
* WhatsApp API, API token and number ID
* FFmpeg (required for audio processing)

## System Dependencies

1. Install FFmpeg for audio processing:
```bash
$ sudo apt update
$ sudo apt install ffmpeg
```

## Create a .env file in your root

Set the necessary environment variables in `.env` file:
```
# WhatsApp Configuration
WHATSAPP_ACCESS_TOKEN = 'Your WhatsApp API token'
WHATSAPP_NUMBER_ID = 'Your WhatsApp number ID'
WHATSAPP_HOOK_TOKEN = 'Your Verification Token'

# MongoDB Configuration
MONGO_DB_NAME = 'Your Database Name'
MONGO_DB_USER_COLLECTION = 'user_details'
MONGO_DB_CONVERSATION_COLLECTION = 'user_conversations'
DATABASE_URL = 'mongodb://localhost:27017/'

# OpenAI Configuration
OPENAI_API_KEY = 'Your OpenAI API Key'

# Azure Services Configuration
AZURE_SPEECH_SUBSCRIPTION_KEY = "Your Azure Speech Key"
AZURE_SPEECH_REGION = "Your Azure Region"
AZURE_TRANSLATOR_KEY = "Your Azure Translator Key"
AZURE_TRANSLATOR_REGION = "Your Azure Region"
AZURE_TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com"

# Application Configuration
APP_URL = 'Your Domain URL'  # e.g., https://whatsapp.yourdomain.com
SENTRY_DSN = "Your Sentry DSN"  # Optional: for error tracking
```

Set URL for `WhatsApp API` in whatsapp_wrapper.py:
```python
self.base_url = "https://graph.facebook.com/v18.0/"
```

## Development Environment Setup

1. Install virtualenv
```bash
$ sudo pip3 install virtualenv
```

2. Create virtual environment
```bash
$ virtualenv venv --python=python3.8
```

3. Activate virtual environment
```bash
$ source venv/bin/activate
```

4. Install the required libraries:
```bash
(venv)$ pip install -r requirements.txt
```

5. Run the server:
```bash
(venv)$ python asgi.py
```

## Domain Setup

### Development
For development, you can use ngrok to create a temporary domain:
```bash
ngrok http 8000
```
Use the generated URL (e.g., https://xyz.ngrok.io/webhook/) in your WhatsApp webhook settings.

### Production
For production, set up a domain with Nginx as reverse proxy to forward requests to your application. Configure SSL using Let's Encrypt for secure HTTPS connections.

Your webhook URL should be accessible at:
```
https://your-domain.com/webhook/
```

For detailed WhatsApp setup instructions, please refer to [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md)
