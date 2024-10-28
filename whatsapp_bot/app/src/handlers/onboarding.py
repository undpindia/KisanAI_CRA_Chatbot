import logging
import asyncio
import json
import uuid
import os
import re
from app.src.handlers.instances import messenger
from app.src.services.speech.stt import openai_whisper
from app.src.config.config import settings  # Add this import at the top

class OnboardingProcess:
    """
    Manages the user onboarding workflow for the WhatsApp CRA assistant.
    
    This class handles the complete onboarding process including language selection,
    consent management, and user details collection (name, location, gender).
    The process is interactive and supports multiple input types including text,
    audio, and interactive messages.

    Attributes:
        data: Raw message data from WhatsApp
        state: User state object tracking onboarding progress
        message_type: Type of message received (text, audio, or interactive)
        language_audio_mapping: JSON mapping of language-specific audio files
        consent_mapping: JSON mapping of consent-related messages and media
    """

    def __init__(self, data, state):
        self.data = data
        self.state = state
        self.message_type = messenger.get_message_type(data)
        
        with open("app/data/language/language_audio_mapping.json", "r") as json_file:
            self.language_audio_mapping = json.load(json_file)
            
        with open("app/data/language/consent_mapping.json", "r") as json_file:
            self.consent_mapping = json.load(json_file)

    async def start(self):
        """
        Orchestrates the onboarding workflow based on user state.
        
        Manages the sequential flow of onboarding steps:
        1. Language selection and confirmation
        2. Consent process
        3. User details collection (name, location, gender)
        
        Each step includes validation and confirmation before proceeding.
        """
        try:


            if self.state.language_confirmed is False:
                
                if self.state.onboarding_video_sent is False:
                    messenger.send_message(user_phone_number=self.state.mobile, message="Welcome to the KissanAI CRA assistant.")
                    intro_message_video_url = f'{settings.APP_URL}/dl/static/intro_to_cra.mp4'
                    print(settings.APP_URL)
                    print(settings.WHATSAPP_ACCESS_TOKEN)
                    print(settings.WHATSAPP_NUMBER_ID)
                    print(intro_message_video_url)
                    send_video_status = messenger.send_video(user_phone_number=self.state.mobile, video=intro_message_video_url, caption="Introduction to CRA assistant.")
                    self.state.onboarding_video_sent = send_video_status
                    self.state.save()
                    await asyncio.sleep(2)

                if self.state.onboarding_audio_sent is False:
                    intro_message_audio_url = f'{settings.APP_URL}/dl/static/intro_to_cra.mp3'
                    send_audio_status = messenger.send_audio(user_phone_number=self.state.mobile, audio=intro_message_audio_url)
                    self.state.onboarding_audio_sent = send_audio_status
                    self.state.save()
                    await asyncio.sleep(3)

                if self.state.onboarding_audio_sent and self.state.language_selection_sent is False:
                    await self.send_language_selection()
                    await asyncio.sleep(1.5)
                    return

                if self.state.language_selection_sent and self.state.language_selection_received is False:
                    await self.process_language_selection_response()
                    return
                
                elif self.state.language_confirmation_sent is False and self.state.language_confirmation_received is False:
                    language_confirmation_sent_status = messenger.send_language_confirmation(user_phone_number=self.state.mobile, language=self.state.language)
                    # Update state
                    self.state.language_confirmation_sent = language_confirmation_sent_status
                    self.state.save()
                    return
                
                elif self.state.language_confirmation_sent and self.state.language_confirmation_received is False:
                    print("Language confirmation sent, but not received.")
                    await self.process_language_confirmation_response()
                    return
                
                else:
                    print("Language confirmation sent, but not received.")
                    with open("app/data/default_messages/language_validation_default_messages.json", "r") as json_file:
                        language_validation_mapping = json.load(json_file)
                    messenger.send_message(user_phone_number=self.state.mobile, message=language_validation_mapping['default_messages'][self.state.language])
                    return
            
            elif self.state.consent is False:
                if self.state.consent_rejected:
                    await self.send_rejected_consent_followup()
                    return
                elif self.state.consent_sent is False and self.state.consent_received is False:
                    await self.send_consent()
                    return
                elif self.state.consent_sent and self.state.consent_received is False:
                    await self.process_consent_response()
                else:
                    await self.process_consent_rejection()
                    return
            
            elif self.state.name_confirmed is False:
                if self.state.name_confirmation_sent is False and self.state.name_confirmation_received is False:
                    await self.process_name_response()
                    return
                elif self.state.name_confirmation_sent and self.state.name_confirmation_received is False:
                    await self.process_name_confirmation_response()
                    return
            
            elif self.state.location_confirmed is False:
                if self.state.location_confirmation_sent is False and self.state.location_confirmation_received is False:
                    await self.process_location_response()
                    return
                elif self.state.location_confirmation_sent and self.state.location_confirmation_received is False:
                    await self.process_location_confirmation_response()
                    return
            
            elif self.state.gender_confirmed is False:
                if self.state.gender_selection_sent is False:
                    await self.send_gender_selection()
                    return
                elif self.state.gender_selection_sent and self.state.gender_selection_received is False:
                    await self.process_gender_selection_response()
                    return
                elif self.state.gender_selection_received and self.state.gender_confirmation_sent is False:
                    await self.send_gender_confirmation()
                    return
                elif self.state.gender_confirmation_sent and self.state.gender_confirmation_received is False:
                    await self.process_gender_confirmation_response()
                    return
            
            else:
                pass
        except Exception as e:
            logging.error(f"Error in onboarding process: {str(e)}")
            return 
    
    async def send_language_selection(self):
        """
        Initiates the language selection process.
        
        Sends interactive buttons for language selection and updates the user state
        to track that language selection has been initiated.
        """
        language_selection_message = messenger.send_language_selection_button(user_phone_number=self.state.mobile)
        self.state.language_selection_sent = language_selection_message
        self.state.save()
        return

    async def process_language_selection_response(self):
        """
        Handles user response to language selection.
        
        Processes different types of responses (interactive, text, audio) and
        validates the selected language. Updates user state and sends confirmation
        on valid selection.
        """
        message_type = self.message_type

        if message_type == "interactive":
            message_response = messenger.get_interactive_response(self.data)
            interactive_type = message_response.get("type")
            button_reply_title = message_response[interactive_type]["title"]
            button_reply_id = message_response[interactive_type]["id"]

            if button_reply_id in ["ENGLISH_LANGUAGE_BUTTON_ID_1", 
                                    "HINDI_LANGUAGE_BUTTON_ID_2", 
                                    "MARATHI_LANGUAGE_BUTTON_ID_3"]:
                self.state.language = button_reply_id.split('_')[0].lower()
                self.state.language_selection_sent = True
                self.state.language_selection_received = True
                self.state.save()

                audio_url = self.language_audio_mapping['language_audio_mapping']['language_selection_button'][self.state.language]
                # Send audio confirmation
                messenger.send_audio(user_phone_number=self.state.mobile, audio=audio_url)
                await asyncio.sleep(0.5)
                # Send language confirmation button
                await self.send_language_confirmation()
            else:
                messenger.send_message(user_phone_number=self.state.mobile, message="Please select your preferred language from language selection buttons to continue.")
        elif message_type == "text":
            message = messenger.get_message(self.data)
            if message.lower() in ["english", "hindi", "marathi", "हिंदी", "मराठी"]:
                self.state.language = message.lower()
                self.state.language_selection_sent = True
                self.state.language_selection_received = True
                self.state.save()

                audio_url = self.language_audio_mapping['language_audio_mapping']['language_selection_button'][self.state.language]
                # Send audio confirmation
                messenger.send_audio(user_phone_number=self.state.mobile, audio=audio_url)
                await asyncio.sleep(0.5)
                # Send language confirmation button
                await self.send_language_confirmation()
            else:
                messenger.send_message(user_phone_number=self.state.mobile, message="Please select your preferred language from language selection buttons to continue.")
        elif message_type == "audio":
            audio_file = messenger.get_audio_message_file(self.data)
            audio_transcription = openai_whisper(audio_file, translate=True)
            
            detected_language = next((lang for lang in ["english", "hindi", "marathi"] if lang in audio_transcription.lower()), None)
            if detected_language:
                self.state.language = audio_transcription.lower()
                self.state.language_selection_sent = True
                self.state.language_selection_received = True
                self.state.save()

                audio_url = self.language_audio_mapping['language_audio_mapping']['language_selection_button'][self.state.language]
                # Send audio confirmation
                messenger.send_audio(user_phone_number=self.state.mobile, audio=audio_url)
                await asyncio.sleep(0.5)
                # Send language confirmation button
                await self.send_language_confirmation()
            else:
                messenger.send_message(user_phone_number=self.state.mobile, message="Please select your preferred language from language selection buttons to continue.")
        else:
            messenger.send_message(user_phone_number=self.state.mobile, message="Please select your preferred language from language selection buttons to continue.")                
        return
    
    async def send_language_confirmation(self):
        """
        Sends the language confirmation section to the user.
        """
        language_confirmation_message = messenger.send_language_confirmation(user_phone_number=self.state.mobile, language=self.state.language)
        self.state.language_confirmation_sent = language_confirmation_message
        self.state.save()
        return

    async def process_language_confirmation_response(self):
        """
        Processes the language confirmation received from the user.
        """
        message_type = messenger.get_message_type(self.data)

        if message_type == "interactive":
            message_response = messenger.get_interactive_response(self.data)
            interactive_type = message_response.get("type")
            button_reply_title = message_response[interactive_type]["title"]
            button_reply_id = message_response[interactive_type]["id"]

            if "CONFIRM_LANGUAGE_BUTTON_ID_1" in button_reply_id:
                self.state.language_confirmation_received = True
                self.state.language_confirmed = True
                self.state.language = button_reply_id.split('_')[0].lower()
                self.state.save()
                await self.send_consent()
                return
            elif "CONFIRM_LANGUAGE_BUTTON_ID_2" in button_reply_id:
                self.state.language_confirmation_received = False
                self.state.language_confirmed = False
                self.state.language = None
                await self.send_language_selection()
                self.state.language_selection_received = False
                self.state.save()
                return
            
        elif message_type == "text":
            message = messenger.get_message(self.data)
            if message.lower() == "yes" or message.lower() == "confirm":
                self.state.language_confirmation_received = True
                self.state.language_confirmed = True
                self.state.save()
                await self.send_consent()
                return
            elif message.lower() == "no" or message.lower() == "change":
                self.state.language_confirmation_received = False
                self.state.language_confirmed = False
                self.state.language = None
                await self.send_language_selection()
                self.state.language_selection_received = False
                self.state.save()
                return
        elif message_type == "audio":
            audio_file = messenger.get_audio_message_file(self.data)
            audio_transcription = openai_whisper(audio_file, translate=True)
            if "yes" in audio_transcription.lower() or "confirm" in audio_transcription.lower():
                self.state.language_confirmation_received = True
                self.state.language_confirmed = True
                self.state.save()
                await self.send_consent()
                return
            elif "no" in audio_transcription.lower() or "change" in audio_transcription.lower():
                self.state.language_confirmation_received = False
                self.state.language_confirmed = False
                self.state.language = None
                await self.send_language_selection()
                self.state.language_selection_received = False
                self.state.save()
                return
        else:
            messenger.send_message(user_phone_number=self.state.mobile, message="Please confirm your selected language to continue.")
        return
    
    async def send_consent(self):
        """
        Initiates the consent collection process.
        
        Sends consent-related video, audio, and interactive messages in the user's
        selected language. Updates state to track consent process initiation.
        """
        with open("app/data/language/consent_mapping.json", "r") as json_file:
            consent_mapping = json.load(json_file)
			
        video_url = consent_mapping['consent_video'][self.state.language]
        # Replace example.com with APP_URL from config
        video_url = video_url.replace("https://example.com", settings.APP_URL)
        video_caption = consent_mapping['consent_video_title_text'][self.state.language]
        messenger.send_video(user_phone_number=self.state.mobile,video=video_url,caption=video_caption)
        await asyncio.sleep(2)
			
        # Get the audio file for the language
        audio_url = consent_mapping['consent_audio'][self.state.language]
        audio_url = audio_url.replace("https://example.com", settings.APP_URL)
        messenger.send_audio(user_phone_number=self.state.mobile, audio=audio_url)
        await asyncio.sleep(2)
        
        consent_message = messenger.send_consent_request(user_phone_number=self.state.mobile, language=self.state.language)
        self.state.consent_sent = consent_message
        self.state.save()
        return
    
    async def process_consent_response(self):
        """
        Processes user's consent response.
        
        Handles different types of consent responses (interactive, text, audio)
        and manages the workflow based on whether consent is granted or denied.
        """
        message_type = messenger.get_message_type(self.data)
        
        def confirm_consent_rejection():
            with open("app/data/language/consent_mapping.json", "r") as json_file:
                consent_mapping = json.load(json_file)
            consent_rejection_confirmation_text = consent_mapping['consent_rejection_confirmation_text'][self.state.language]
            messenger.send_message(user_phone_number=self.state.mobile, message=consent_rejection_confirmation_text)
            consent_message = messenger.send_consent_rejection_confirmation(user_phone_number=self.state.mobile, language=self.state.language)

        if message_type == "interactive":
            message_response = messenger.get_interactive_response(self.data)
            interactive_type = message_response.get("type")
            button_reply_title = message_response[interactive_type]["title"]
            button_reply_id = message_response[interactive_type]["id"]

            if "CONSENT_BUTTON_ID_1" in button_reply_id:
                self.state.consent_received = True
                self.state.consent = True
                self.state.save()
                await self.send_name_request()
                return
            elif "CONSENT_BUTTON_ID_2" in button_reply_id:
                self.state.consent_received = True
                self.state.consent = False
                self.state.save()
                confirm_consent_rejection()
                return
            
        elif message_type == "text":
            message = messenger.get_message(self.data)
            if message.lower() == "yes" or message.lower() == "confirm":
                self.state.consent_received = True
                self.state.consent = True
                self.state.save()
                await self.send_name_request()
                return
            elif message.lower() == "no" or message.lower() == "change":
                self.state.consent_received = False
                self.state.consent = False
                self.state.save()
                confirm_consent_rejection()
                return
            
        elif message_type == "audio":
            audio_file = messenger.get_audio_message_file(self.data)
            audio_transcription = openai_whisper(audio_file, translate=True)
            if "yes" in audio_transcription.lower() or "confirm" in audio_transcription.lower():
                self.state.consent_received = True
                self.state.consent = True
                self.state.save()
                await self.send_name_request()
                return
            elif "no" in audio_transcription.lower() or "change" in audio_transcription.lower():
                self.state.consent_received = False
                self.state.consent = False
                self.state.save()
                confirm_consent_rejection()
                return
        else:
            messenger.send_message(user_phone_number=self.state.mobile, message="Please provide your consent to continue.")
    
    async def send_rejected_consent_followup(self):
        
        with open("app/data/language/consent_mapping.json", "r") as json_file:
            consent_mapping = json.load(json_file)
        consent_rejection_followup_text = consent_mapping['consent_rejection_followup_text'][self.state.language]
        messenger.send_message(user_phone_number=self.state.mobile, message=consent_rejection_followup_text)
        
        return
    
    async def process_consent_rejection(self):
        """
        Processes explicit consent rejection.
        
        Handles the workflow when a user explicitly rejects consent, including
        sending follow-up messages and updating user state accordingly.
        """
        message_type = messenger.get_message_type(self.data)
        
        if message_type == "interactive":
            message_response = messenger.get_interactive_response(self.data)
            interactive_type = message_response.get("type")
            button_reply_title = message_response[interactive_type]["title"]
            button_reply_id = message_response[interactive_type]["id"]

            if "CONSENT_REJECTION_BUTTON_ID_1" in button_reply_id:
                self.state.consent_received = True
                self.state.consent = True
                self.state.save()
                await self.send_name_request()
                return
            
            elif "CONSENT_REJECTION_BUTTON_ID_2" in button_reply_id:
                self.state.consent_received = True
                self.state.consent = False
                self.state.consent_rejected = True
                self.state.save()
                await self.send_rejected_consent_followup()
                return
            
        elif message_type == "text":
            
            message = messenger.get_message(self.data)
            if message.lower() == "yes" or message.lower() == "confirm":
                self.state.consent_received = True
                self.state.consent = True
                self.state.save()
                await self.send_name_request()
                return
            
            elif message.lower() == "no" or message.lower() == "change":
                self.state.consent_received = True
                self.state.consent = False
                self.state.consent_rejected = True
                self.state.save()
                await self.send_rejected_consent_followup()
                return
            
        elif message_type == "audio":
            audio_file = messenger.get_audio_message_file(self.data)
            audio_transcription = openai_whisper(audio_file, translate=True)
            
            if "yes" in audio_transcription.lower() or "confirm" in audio_transcription.lower():
                self.state.consent_received = True
                self.state.consent = True
                self.state.save()
                await self.send_name_request()
                return
            
            elif "no" in audio_transcription.lower() or "change" in audio_transcription.lower():
                self.state.consent_received = True
                self.state.consent = False
                self.state.consent_rejected = True
                self.state.save()
                await self.send_rejected_consent_followup()
                return
            
        else:
            messenger.send_message(user_phone_number=self.state.mobile, message="Please provide your consent to continue.")
            return
    
    async def send_name_request(self):
        """
        Initiates the name collection process.
        
        Sends name request messages and audio prompts in the user's selected language.
        """
        with open("app/data/language/user_details_messages_mapping.json", "r") as json_file:
            user_details_messages_mapping = json.load(json_file)
        
        audio_selection_message= self.language_audio_mapping['language_audio_mapping']['language_name_button'][self.state.language]
        audio_url = audio_selection_message.replace("https://example.com", settings.APP_URL)
        messenger.send_audio(user_phone_number=self.state.mobile, audio=audio_url)
        await asyncio.sleep(2)
        
        user_name_message_request = user_details_messages_mapping['ask_name_text'][self.state.language]
        messenger.send_message(user_phone_number=self.state.mobile, message=user_name_message_request)
        return
    
    async def send_name_request_to_continue(self):
        """
        Sends a follow-up name request.
        
        Used when initial name collection needs to be repeated, includes
        appropriate prompts and instructions in the user's language.
        """
        with open("app/data/language/user_details_messages_mapping.json", "r") as json_file:
            user_details_messages_mapping = json.load(json_file)
        
        audio_selection_message= self.language_audio_mapping['language_audio_mapping']['language_name_button'][self.state.language]
        audio_url = audio_selection_message.replace("https://example.com", settings.APP_URL)
        messenger.send_audio(user_phone_number=self.state.mobile, audio=audio_url)
        await asyncio.sleep(2)
        
        user_name_message_request = user_details_messages_mapping['ask_name_to_continue'][self.state.language]
        messenger.send_message(user_phone_number=self.state.mobile, message=user_name_message_request)
        return
    
    async def process_name_response(self):
        """
        Processes user's name response.
        
        Handles different input types for name collection and initiates name
        confirmation process upon valid input.
        """
        message_type = messenger.get_message_type(self.data)
        
        if message_type == "text":
            message = messenger.get_message(self.data)
            if message:
                self.state.name = message
                self.state.save()
                await self.send_name_confirmation()
                self.state.name_confirmation_sent = True
                self.state.save()
                return
        elif message_type == "audio":
            audio_file = messenger.get_audio_message_file(self.data)
            audio_transcription = openai_whisper(audio_file, translate=True)
            if audio_transcription:
                self.state.name = audio_transcription
                self.state.save()
                await self.send_name_confirmation()
                self.state.name_confirmation_sent = True
                self.state.save()
                return
        else:
            await self.send_name_request()
            return        
        
    async def send_name_confirmation(self):
        """
        Sends the name confirmation section to the user.
        """
        user_confirmation_json_file_path = 'app/data/confirmation/multilingual_user_confirmation_response.json'
        # Load the JSON data from the file
        with open(user_confirmation_json_file_path, 'r') as json_file:
            user_confirmation_json = json.load(json_file)
        user_confirmation_response = user_confirmation_json["interaction_responses"][self.state.language]
        response_message_template = user_confirmation_response['name']
        response_message = response_message_template.format(user_name=self.state.name)
        name_confirmation_message = messenger.send_name_confirmation(user_phone_number=self.state.mobile, 
                                                                     message=response_message, 
                                                                     language=self.state.language)
        self.state.name_confirmation_sent = name_confirmation_message
        self.state.save()
        return
    
    async def process_name_confirmation_response(self):
        """
        Processes the name confirmation received from the user.
        """
        message_type = messenger.get_message_type(self.data)
        
        if message_type == "interactive":
            message_response = messenger.get_interactive_response(self.data)
            interactive_type = message_response.get("type")
            button_reply_title = message_response[interactive_type]["title"]
            button_reply_id = message_response[interactive_type]["id"]

            if "NAME_BUTTON_ID_1" in button_reply_id:
                self.state.name_confirmation_received = True
                self.state.name_confirmed = True
                self.state.save()
                await self.send_location_request()
                return
            elif "NAME_BUTTON_ID_2" in button_reply_id:
                self.state.name_confirmation_sent = False
                self.state.name_confirmation_received = False
                self.state.name_confirmed = False
                self.state.name = None
                self.state.save()
                await self.send_name_request_to_continue()
                return
            else:
                messenger.send_message(user_phone_number=self.state.mobile, message="Please confirm your name to continue.")
                return
            
        elif message_type == "text":
            message = messenger.get_message(self.data)
            if message.lower() == "yes" or message.lower() == "confirm":
                self.state.name_confirmation_received = True
                self.state.name_confirmed = True
                self.state.save()
                await self.send_location_request()
                return
            elif message.lower() == "no" or message.lower() == "change":
                self.state.name_confirmation_sent = False
                self.state.name_confirmation_received = False
                self.state.name_confirmed = False
                self.state.name = None
                self.state.save()
                await self.send_name_request_to_continue()
                return
            else:
                messenger.send_message(user_phone_number=self.state.mobile, message="Please confirm your name to continue.")
                return
            
        elif message_type == "audio":
            audio_file = messenger.get_audio_message_file(self.data)
            audio_transcription = openai_whisper(audio_file, translate=True)
            if "yes" in audio_transcription.lower() or "confirm" in audio_transcription.lower():
                self.state.name_confirmation_received = True
                self.state.name_confirmed = True
                self.state.save()
                await self.send_location_request()
                return
            elif "no" in audio_transcription.lower() or "change" in audio_transcription.lower():
                self.state.name_confirmation_sent = False
                self.state.name_confirmation_received = False
                self.state.name_confirmed = False
                self.state.name = None
                self.state.save()
                await self.send_name_request_to_continue()
                return
            else:
                messenger.send_message(user_phone_number=self.state.mobile, message="Please confirm your name to continue.")
                return
            
        else:
            messenger.send_message(user_phone_number=self.state.mobile, message="Please confirm your name to continue.")
            return
    
    async def send_location_request(self):
        """
        Initiates the location collection process.
        
        Sends location request messages and audio prompts in the user's selected language.
        """
        with open("app/data/language/user_details_messages_mapping.json", "r") as json_file:
            user_details_messages_mapping = json.load(json_file)
        
        audio_selection_message= self.language_audio_mapping['language_audio_mapping']['language_location_button'][self.state.language]
        audio_url = audio_selection_message.replace("https://example.com", settings.APP_URL)
        messenger.send_audio(user_phone_number=self.state.mobile, audio=audio_url)
        await asyncio.sleep(2)
        
        user_name_message_request = user_details_messages_mapping['ask_location_text'][self.state.language]
        messenger.send_message(user_phone_number=self.state.mobile, message=user_name_message_request)
        return
    
    async def send_location_request_to_continue(self):
        """
        Sends a follow-up location request.
        
        Used when initial location collection needs to be repeated, includes
        appropriate prompts and instructions in the user's language.
        """
        with open("app/data/language/user_details_messages_mapping.json", "r") as json_file:
            user_details_messages_mapping = json.load(json_file)
        
        audio_selection_message= self.language_audio_mapping['language_audio_mapping']['language_location_button'][self.state.language]
        audio_url = audio_selection_message.replace("https://example.com", settings.APP_URL)
        messenger.send_audio(user_phone_number=self.state.mobile, audio=audio_url)
        await asyncio.sleep(2)
        
        user_name_message_request = user_details_messages_mapping['ask_location_to_continue'][self.state.language]
        messenger.send_message(user_phone_number=self.state.mobile, message=user_name_message_request)
        return
    
    async def process_location_response(self):
        """
        Processes user's location response.
        
        Handles different input types for location collection and initiates location
        confirmation process upon valid input.
        """
        message_type = messenger.get_message_type(self.data)
        
        if message_type == "text":
            message = messenger.get_message(self.data)
            if message:
                self.state.location = message
                self.state.save()
                await self.send_location_confirmation()
                self.state.location_confirmation_sent = True
                self.state.save()
                return
        elif message_type == "audio":
            audio_file = messenger.get_audio_message_file(self.data)
            audio_transcription = openai_whisper(audio_file, translate=True)
            if audio_transcription:
                self.state.location = audio_transcription
                self.state.save()
                await self.send_location_confirmation()
                self.state.location_confirmation_sent = True
                self.state.save()
                return
        else:
            await self.send_location_request()
            return

    async def process_location_confirmation_response(self):
        """
        Processes the location confirmation received from the user.
        """
        message_type = messenger.get_message_type(self.data)
        
        if message_type == "interactive":
            message_response = messenger.get_interactive_response(self.data)
            interactive_type = message_response.get("type")
            button_reply_title = message_response[interactive_type]["title"]
            button_reply_id = message_response[interactive_type]["id"]

            if "LOCATION_BUTTON_ID_1" in button_reply_id:
                self.state.location_confirmation_received = True
                self.state.location_confirmed = True
                self.state.save()
                await self.send_gender_selection()
                return
            elif "LOCATION_BUTTON_ID_2" in button_reply_id:
                self.state.location_confirmation_sent = False
                self.state.location_confirmation_received = False
                self.state.location_confirmed = False
                self.state.location = None
                self.state.save()
                await self.send_location_request_to_continue()
                return
            else:
                messenger.send_message(user_phone_number=self.state.mobile, message="Please confirm your location to continue.")
                return
            
        elif message_type == "text":
            message = messenger.get_message(self.data)
            if message.lower() == "yes" or message.lower() == "confirm":
                self.state.location_confirmation_received = True
                self.state.location_confirmed = True
                self.state.save()
                await self.send_gender_selection()
                return
            elif message.lower() == "no" or message.lower() == "change":
                self.state.location_confirmation_sent = False
                self.state.location_confirmation_received = False
                self.state.location_confirmed = False
                self.state.location = None
                self.state.save()
                await self.send_location_request_to_continue()
                return
            else:
                messenger.send_message(user_phone_number=self.state.mobile, message="Please confirm your location to continue.")
                return
            
        elif message_type == "audio":
            audio_file = messenger.get_audio_message_file(self.data)
            audio_transcription = openai_whisper(audio_file, translate=True)
            if "yes" in audio_transcription.lower() or "confirm" in audio_transcription.lower():
                self.state.location_confirmation_received = True
                self.state.location_confirmed = True
                self.state.save()
                await self.send_gender_selection()
                return
            elif "no" in audio_transcription.lower() or "change" in audio_transcription.lower():
                self.state.location_confirmation_sent = False
                self.state.location_confirmation_received = False
                self.state.location_confirmed = False
                self.state.location = None
                self.state.save()
                await self.send_location_request_to_continue()
                return
            else:
                messenger.send_message(user_phone_number=self.state.mobile, message="Please confirm your location to continue.")
                return
            
        else:
            messenger.send_message(user_phone_number=self.state.mobile, message="Please confirm your location to continue.")
            return

    async def send_location_confirmation(self):
        """
        Sends the location confirmation section to the user.
        """
        user_confirmation_json_file_path = 'app/data/confirmation/multilingual_user_confirmation_response.json'
        # Load the JSON data from the file
        with open(user_confirmation_json_file_path, 'r') as json_file:
            user_confirmation_json = json.load(json_file)
        user_confirmation_response = user_confirmation_json["interaction_responses"][self.state.language]
        response_message_template = user_confirmation_response['location']
        response_message = response_message_template.format(user_location=self.state.location)
        location_confirmation_message = messenger.send_location_confirmation(user_phone_number=self.state.mobile, 
                                                                             message=response_message, 
                                                                             language=self.state.language)
        self.state.location_confirmation_sent = location_confirmation_message
        self.state.save()
        return
    
    async def send_gender_selection(self):
        """
        Initiates the gender selection process.
        
        Sends interactive buttons for gender selection along with audio prompts
        in the user's selected language.
        """
        with open("app/data/language/user_details_messages_mapping.json", "r") as json_file:
            user_details_messages_mapping = json.load(json_file)
        
        audio_selection_message= self.language_audio_mapping['language_audio_mapping']['language_gender_button'][self.state.language]
        audio_url = audio_selection_message.replace("https://example.com", settings.APP_URL)
        messenger.send_audio(user_phone_number=self.state.mobile, audio=audio_url)
        await asyncio.sleep(2)

        user_gender_message_request = user_details_messages_mapping['ask_gender_text'][self.state.language]
        messenger.send_message(user_phone_number=self.state.mobile, message=user_gender_message_request)
        gender_selection_message = messenger.send_gender_selection_button(user_phone_number=self.state.mobile, 
                                                                          language=self.state.language)
        self.state.gender_selection_sent = gender_selection_message
        self.state.save()
        return
    
    async def send_gender_selection_to_continue(self):
        """
        Sends a follow-up gender selection request.
        
        Used when initial gender selection needs to be repeated, includes
        appropriate prompts and interactive options in the user's language.
        """
        with open("app/data/language/user_details_messages_mapping.json", "r") as json_file:
            user_details_messages_mapping = json.load(json_file)
        
        audio_selection_message= self.language_audio_mapping['language_audio_mapping']['language_gender_button'][self.state.language]
        audio_url = audio_selection_message.replace("https://example.com", settings.APP_URL)
        messenger.send_audio(user_phone_number=self.state.mobile, audio=audio_url)
        await asyncio.sleep(2)
        
        user_gender_message_request = user_details_messages_mapping['ask_gender_to_continue'][self.state.language]
        messenger.send_message(user_phone_number=self.state.mobile, message=user_gender_message_request)
        gender_selection_message = messenger.send_gender_selection_button(user_phone_number=self.state.mobile, 
                                                                          language=self.state.language)
        self.state.gender_selection_sent = gender_selection_message
        self.state.save()
        return
    
    async def process_gender_selection_response(self):
        """
        Processes user's gender selection response.
        
        Handles different types of gender selection inputs and initiates
        confirmation process upon valid selection.
        """
        message_type = self.message_type

        if message_type == "interactive":
            message_response = messenger.get_interactive_response(self.data)
            interactive_type = message_response.get("type")
            button_reply_title = message_response[interactive_type]["title"]
            button_reply_id = message_response[interactive_type]["id"]

            if button_reply_id in ["ENGLISH_GENDER_BUTTON_ID_1", 
                                   "HINDI_GENDER_BUTTON_ID_1", 
                                   "MARATHI_GENDER_BUTTON_ID_1",
                                   "ENGLISH_GENDER_BUTTON_ID_2", 
                                   "HINDI_GENDER_BUTTON_ID_2", 
                                   "MARATHI_GENDER_BUTTON_ID_2",
                                   "ENGLISH_GENDER_BUTTON_ID_3", 
                                   "HINDI_GENDER_BUTTON_ID_3", 
                                   "MARATHI_GENDER_BUTTON_ID_3"]:
                self.state.gender = button_reply_title.split()[-1]
                self.state.gender_selection_sent = True
                self.state.gender_selection_received = True
                self.state.save()
                # Proceed to the next step in the onboarding process
                await self.send_gender_confirmation()
            else:
                messenger.send_message(user_phone_number=self.state.mobile, message="Please select your gender from the buttons to continue.")
        elif message_type == "text":
            message = messenger.get_message(self.data)
            if message.lower() in ["male", "female", "other"]:
                self.state.gender = message.lower()
                self.state.gender_selection_sent = True
                self.state.gender_selection_received = True
                self.state.save()
                # Proceed to the next step in the onboarding process
                await self.send_gender_confirmation()
            else:
                messenger.send_message(user_phone_number=self.state.mobile, message="Please select your gender from the buttons to continue.")
        elif message_type == "audio":
            audio_file = messenger.get_audio_message_file(self.data)
            audio_transcription = openai_whisper(audio_file, translate=True)
            if audio_transcription.lower() in ["male", "female", "other"]:
                self.state.gender = audio_transcription.lower()
                self.state.gender_selection_sent = True
                self.state.gender_selection_received = True
                self.state.save()
                # Proceed to the next step in the onboarding process
                await self.send_gender_confirmation()
            else:
                messenger.send_message(user_phone_number=self.state.mobile, message="Please select your gender from the buttons to continue.")
        else:
            messenger.send_message(user_phone_number=self.state.mobile, message="Please select your gender from the buttons to continue.")

    async def send_gender_confirmation(self):
        """
        Sends the gender confirmation section to the user.
        """
        user_confirmation_json_file_path = 'app/data/confirmation/multilingual_user_confirmation_response.json'
        # Load the JSON data from the file
        with open(user_confirmation_json_file_path, 'r') as json_file:
            user_confirmation_json = json.load(json_file)
        user_confirmation_response = user_confirmation_json["interaction_responses"][self.state.language]
        response_message_template = user_confirmation_response['gender']
        response_message = response_message_template.format(user_gender=self.state.gender)
        gender_confirmation_message = messenger.send_gender_confirmation(user_phone_number=self.state.mobile, 
                                                                         message=response_message, 
                                                                         language=self.state.language)
        self.state.gender_confirmation_sent = gender_confirmation_message
        self.state.save()
        return

    async def process_gender_confirmation_response(self):
        """
        Processes the gender confirmation received from the user.
        """
        message_type = messenger.get_message_type(self.data)
        
        if message_type == "interactive":
            message_response = messenger.get_interactive_response(self.data)
            interactive_type = message_response.get("type")
            button_reply_title = message_response[interactive_type]["title"]
            button_reply_id = message_response[interactive_type]["id"]

            if "GENDER_CONFIRMATION_BUTTON_ID_1" in button_reply_id:
                self.state.gender_confirmation_received = True
                self.state.gender_confirmed = True
                self.state.save()
                # Proceed to the next step in the onboarding process
                await self.onboarding_complete()
                return
                return
            elif "GENDER_CONFIRMATION_BUTTON_ID_2" in button_reply_id:
                self.state.gender_selection_received = False
                self.state.gender_confirmation_sent = False
                self.state.gender_confirmation_received = False
                self.state.gender_confirmed = False
                self.state.gender = None
                self.state.save()
                await self.send_gender_selection_to_continue()
                return
            else:
                messenger.send_message(user_phone_number=self.state.mobile, message="Please confirm your gender to continue.")
                return
            
        elif message_type == "text":
            message = messenger.get_message(self.data)
            if message.lower() == "yes" or message.lower() == "confirm":
                self.state.gender_confirmation_received = True
                self.state.gender_confirmed = True
                self.state.save()
                # Proceed to the next step in the onboarding process
                await self.onboarding_complete()
                return
            elif message.lower() == "no" or message.lower() == "change":
                self.state.gender_selection_received = False
                self.state.gender_confirmation_sent = False
                self.state.gender_confirmation_received = False
                self.state.gender_confirmed = False
                self.state.gender = None
                self.state.save()
                await self.send_gender_selection_to_continue()
                return
            else:
                messenger.send_message(user_phone_number=self.state.mobile, message="Please confirm your gender to continue.")
                return
            
        elif message_type == "audio":
            audio_file = messenger.get_audio_message_file(self.data)
            audio_transcription = openai_whisper(audio_file, translate=True)
            if "yes" in audio_transcription.lower() or "confirm" in audio_transcription.lower():
                self.state.gender_confirmation_received = True
                self.state.gender_confirmed = True
                self.state.save()
                # Proceed to the next step in the onboarding process
                await self.onboarding_complete()
                return
            elif "no" in audio_transcription.lower() or "change" in audio_transcription.lower():
                self.state.gender_selection_received = False
                self.state.gender_confirmation_sent = False
                self.state.gender_confirmation_received = False
                self.state.gender_confirmed = False
                self.state.gender = None
                self.state.save()
                await self.send_gender_selection_to_continue()
                return
            else:
                messenger.send_message(user_phone_number=self.state.mobile, message="Please confirm your gender to continue.")
                return
            
        else:
            messenger.send_message(user_phone_number=self.state.mobile, message="Please confirm your gender to continue.")
            return
    
    async def onboarding_complete(self):
        """
        Finalizes the onboarding process.
        
        Updates user state to mark onboarding as complete and sends confirmation
        messages to the user. Prepares the system for normal operation mode.
        """
        self.state.onboarded = True
        self.state.save()
        with open("app/data/language/user_details_messages_mapping.json", "r") as json_file:
            user_details_messages_mapping = json.load(json_file)
        user_onboarded_message = user_details_messages_mapping['onboarding_completed'][self.state.language]        
        messenger.send_message(user_phone_number=self.state.mobile, message=user_onboarded_message)
        
        onboarding_audio_message = self.language_audio_mapping['language_audio_mapping']['language_question_button'][self.state.language]
        audio_url = onboarding_audio_message.replace("https://example.com", settings.APP_URL)
        messenger.send_audio(user_phone_number=self.state.mobile, audio=audio_url)
        

