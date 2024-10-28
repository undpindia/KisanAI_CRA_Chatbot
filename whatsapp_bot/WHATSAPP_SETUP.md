# WhatsApp Setup Guide

This guide walks you through setting up your WhatsApp API integration with Facebook Developer account.

## Developer Facebook Account Setup

1. Go to the [Facebook Developer Apps](https://developers.facebook.com/apps/) page
   - If you don't have an app, create one

2. Click on your app name to access the dashboard

3. Configure Webhooks:
   - Navigate to Webhooks in the left sidebar
   - Subscribe to the messages API
   - Configure your webhook URL and verification token

4. WhatsApp API Setup:
   - Go to WhatsApp -> API Setup
   - Get your temporary access token (valid for 24 hours)
   - Copy the token to your `.env` file

5. Phone Number Configuration:
   - Find your Phone number ID and copy it to `.env`
   - To add a new phone number:
     1. Go to "Manage phone number list"
     2. Click "Add phone number"
     3. Follow verification process with OTP
     4. Once verified, the number will appear in your "To" section

6. Testing Your Setup:
   - You can send a test message using the interface
   - You should receive a default template message on your WhatsApp number

7. Final Configuration:
   - Go to Configuration section
   - Set your backend webhook URL
   - Enter your verification token (same as WHATSAPP_HOOK_TOKEN in .env)
   - Click "Verify and Save"

## Important URLs and Settings

- API Base URL (for whatsapp_wrapper.py):
```python
self.base_url = "https://graph.facebook.com/v18.0/"
```

- Webhook URL format:
```
https://[backend-url]/webhook/
```

- Verification Token example:
```
WHATSAPP_HOOK_TOKEN = 'your_verification_token'
```

Once your token is verified, your webhook connection will be established and ready to use.

