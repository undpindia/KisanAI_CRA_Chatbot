# WhatsApp Setup Guide

This guide walks you through setting up your WhatsApp API integration with a Facebook Developer account.

## Developer Facebook Account Setup

1. **Create or Access Your App:**
   - Go to the [Facebook Developer Apps](https://developers.facebook.com/apps/) page.
   - If you don't have an app, create one.
   - Click on your app name to access the dashboard.
   ![](images/whatsapp_setup_images/developers_facebook_account_app_view.png)

2. **Configure Webhooks:**
   - Navigate to Webhooks in the left sidebar.
   - Subscribe to the messages API.
   ![](images/whatsapp_setup_images/message_api_subscription.png)
   - Configure your webhook URL and verification token.

3. **WhatsApp API Setup:**
   - Go to WhatsApp -> API Setup.
   - Get your temporary access token (valid for 24 hours).
   ![](images/whatsapp_setup_images/temporary_access_token.png)
   - Copy the token to your `.env` file:
     ```
     WHATSAPP_API_TOKEN = 'your_token'
     ```

4. **Phone Number Configuration:**
   - Find your Phone number ID and copy it to `.env`:
     ```
     WHATSAPP_NUMBER_ID = '262127786975520'
     ```
   ![](images/whatsapp_setup_images/send_and_receiving_messages.png)
   - To add a new phone number:
     1. Go to "Manage phone number list".
     ![](images/whatsapp_setup_images/manage_phone_number_list.png)
     2. Click "Add phone number".
     ![](images/whatsapp_setup_images/add_new_phone_number.png)
     3. Follow the verification process with OTP.
     ![](images/whatsapp_setup_images/verify_phone_number.png)
     4. Once verified, the number will appear in your "To" section.
     ![](images/whatsapp_setup_images/phone_number_verified.png)

5. **Testing Your Setup:**
   - You can send a test message using the interface.
   ![](images/whatsapp_setup_images/test_message.png)
   - You should receive a default template message on your WhatsApp number.
   ![](images/whatsapp_setup_images/received_test_message.png)

6. **Final Configuration:**
   - Go to the Configuration section.
   ![](images/whatsapp_setup_images/configuration.png)
   - Set your backend webhook URL.
   - Enter your verification token (same as WHATSAPP_HOOK_TOKEN in .env):
     ```
     WHATSAPP_HOOK_TOKEN = 'your_verification_token'
     ```
   ![](images/whatsapp_setup_images/webhook_callback_url.png)
   - Click "Verify and Save".

## Important URLs and Settings

- **API Base URL (for whatsapp_wrapper.py):**
  ```python
  self.base_url = "https://graph.facebook.com/v18.0/"
  ```

- **Webhook URL format:**
  ```
  https://[backend-url]/webhook/
  ```

- **Verification Token example:**
  ```
  WHATSAPP_HOOK_TOKEN = 'your_verification_token'
  ```

Once your token is verified, your webhook connection will be established and ready to use.