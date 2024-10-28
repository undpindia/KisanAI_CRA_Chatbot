import logging
import asyncio
import json
import uuid
import os
import shutil
import tempfile
import time
from app.src.handlers.instances import messenger
from app.src.services.speech.converter import convert_ogg_to_wav
from app.src.services.speech.stt import openai_whisper, azure_speech_to_text
from app.src.services.llm.query_engine import QueryEngine
from app.src.config.database import store_conversation, get_last_conversation, get_conversation_by_chat_id, update_conversation

class ConversationHandler:
    """
    Handles WhatsApp conversations including text, audio, and interactive messages.
    
    This class manages the conversation flow between users and the system, processing
    different types of messages (text, audio, interactive), maintaining conversation
    history, and coordinating responses through various services.

    Attributes:
        data: Raw message data from WhatsApp
        state: User state information including mobile number and language preferences
        message_type: Type of message received (text, audio, or interactive)
        question_prev: Previous question from the conversation history
        answer_prev: Previous answer from the conversation history
        lang_locale: Language locale code for speech-to-text conversion
        query_engine: Instance of QueryEngine for processing queries
    """

    def __init__(self, data, state):
        self.data = data
        self.state = state
        self.message_type = messenger.get_message_type(data)
        
        # Fetch the last conversation
        last_conversation = get_last_conversation(self.state.mobile)
        if last_conversation:
            self.question_prev = last_conversation.get("question", "")
            self.answer_prev = last_conversation.get("answer", "")
        else:
            self.question_prev = ""
            self.answer_prev = ""

        # Load language configuration
        with open('app/data/language/lang.json', 'r') as file:
            lang_config = json.load(file)
        
        # Set lang_locale based on the user's language
        user_language = self.state.language.lower()
        self.lang_locale = lang_config.get(user_language, {}).get('code_locale', 'en-IN')
        
        with open('app/data/default_messages/audio_type_default_messages.json', 'r') as file:
            self.audio_type_default_messages = json.load(file)
        
        self.query_engine = QueryEngine(language=self.state.language)
        

    async def chat(self):
        """
        Routes incoming messages to appropriate handlers based on message type.
        
        Determines the message type and delegates processing to the corresponding
        handler method (text, audio, or interactive).
        """
        if self.message_type == "text":
            await self.handle_text_message()
        elif self.message_type == "audio":
            await self.handle_audio_message()
        elif self.message_type == "interactive":
            await self.handle_audio_interactive_message()
        else:
            pass
        
    async def handle_text_message(self):
        """
        Processes incoming text messages.
        
        Extracts the message content, generates a response using the query engine,
        stores the conversation in the database, and sends the response back to the user.
        """
        message = messenger.get_message(self.data)
        
        if message:
        
            answer = self.query_engine.text_query_response(question=message,
                                                    question_prev=self.question_prev,
                                                    answer_prev=self.answer_prev)
            chat_id = str(uuid.uuid4())
            store_conversation(mobile=self.state.mobile, 
                            chat_id=chat_id, 
                            language=self.state.language, 
                            question_format="text", 
                            question=message, 
                            question_en=self.query_engine.answer_en, 
                            answer=answer, 
                            answer_en=self.query_engine.answer_en, 
                            context=self.query_engine.context,
                            location=self.state.location)
            messenger.send_message(user_phone_number=self.state.mobile,
                                message=answer)
    
    async def handle_audio_message(self):
        """
        Processes incoming audio messages.
        
        Converts audio to text, confirms the transcription with the user,
        generates both text and audio responses, and stores the conversation
        details including audio files in the database.
        
        The process includes:
        1. Converting OGG audio to WAV format
        2. Performing speech-to-text conversion
        3. Sending transcription confirmation to user
        4. Generating and storing responses
        5. Handling audio file storage
        """
        # create tempaudio file
        audio_data = messenger.get_audio_message_file(self.data)
        temp_wav_file_path = None
        try:
            # Convert the OGG audio data to MP3
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
                convert_ogg_to_wav(audio_data, temp_wav_file)
                temp_wav_file_path = temp_wav_file.name
            self.question = azure_speech_to_text(temp_wav_file_path, self.lang_locale)
            if self.question:
                print(f"Question: {self.question}")
                chat_id = str(uuid.uuid4())
                
                # Measure time for sending question confirmation
                start_time = time.time()
                messenger.send_question_confirmation_with_chatid(user_phone_number=self.state.mobile,
                                                                 message=self.question,
                                                                 language=self.state.language,
                                                                 chat_id=chat_id)
                end_time = time.time()
                print(f"Time for sending question confirmation: {end_time - start_time} seconds")
                
                # Store initial conversation with question
                store_conversation(mobile=self.state.mobile, 
                                   chat_id=chat_id, 
                                   language=self.state.language, 
                                   question_format="audio",
                                   answer=None,
                                   question=self.question, 
                                   answer_status=False,
                                   answer_audio_status=False,
                                   context=None,
                                   location=self.state.location)
                
                # Measure time for generating answer from query engine
                start_time = time.time()
                answer = self.query_engine.text_query_response(question=self.question,
                                                               question_prev=self.question_prev,
                                                               answer_prev=self.answer_prev)
                end_time = time.time()
                print(f"Time for generating answer from query engine: {end_time - start_time} seconds")
                
                # Update conversation with text answer
                update_conversation(chat_id=chat_id, 
                                    answer=answer, 
                                    answer_en=self.query_engine.answer_en, 
                                    context=self.query_engine.context,
                                    answer_status=True)
                
                # Measure time for saving input audio file
                start_time = time.time()
                input_folder = 'app/data/input'
                os.makedirs(input_folder, exist_ok=True)
                input_file_path = os.path.join(input_folder, f"{chat_id}.wav")
                shutil.move(temp_wav_file_path, input_file_path)
                end_time = time.time()
                print(f"Time for saving input audio file: {end_time - start_time} seconds")
                                
                # Measure time for generating audio response
                start_time = time.time()
                answer_audio_url, answer_audio_path = self.query_engine.audio_query_response_audio(chat_id=chat_id)
                end_time = time.time()
                print(f"Time for generating audio response: {end_time - start_time} seconds")
                if not answer_audio_url:
                    update_conversation(chat_id=chat_id,
                                        answer_audio_status=None)
                else:
                # Update conversation with audio answer
                    update_conversation(chat_id=chat_id, 
                                        answer_audio_url=answer_audio_url, 
                                        answer_audio_status=True)
                
                return
            else:
                message = self.audio_type_default_messages.get("default_message", {}).get(self.state.language, "Sorry, I could not understand your audio message.")
                messenger.send_message(user_phone_number=self.state.mobile, message=message)
                
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            return
    
    async def handle_audio_interactive_message(self):
        """
        Handles interactive message responses for audio conversations.
        
        Processes user confirmations for transcribed audio messages and manages
        the delivery of corresponding text and audio responses. Implements retry
        logic for fetching conversation data from the database.
        """
        message_response = messenger.get_interactive_response(self.data)
        interactive_type = message_response.get("type")
        button_reply_title = message_response[interactive_type]["title"]
        button_reply_id = message_response[interactive_type]["id"]
        print(f"Button reply title: {button_reply_title}")
        print(f"Button reply id: {button_reply_id}")

        # Extract chat_id and confirmation status
        parts = button_reply_id.split('_')
        chat_id = parts[0]
        confirmation_status = parts[-1]

        if confirmation_status == '1':
            # User confirmed the question, fetch the answer from MongoDB
            conversation = None
            for attempt in range(3):
                conversation = get_conversation_by_chat_id(chat_id)
                if conversation:
                    answer_status = conversation.get("answer_status", False)
                    if answer_status == True:
                        break
                # Wait for incremental delay before retrying
                await asyncio.sleep(attempt + 1)
            
            if conversation and answer_status == True:
                answer = conversation.get("answer", "Sorry, I could not find the answer.")
                messenger.send_message(user_phone_number=self.state.mobile, message=answer)
            else:
                messenger.send_message(user_phone_number=self.state.mobile, message="Something went wrong. Please try again.")

            for attempt in range(3):
                conversation = get_conversation_by_chat_id(chat_id)
                if conversation:
                    answer_audio_status = conversation.get("answer_audio_status", False)
                    if answer_audio_status == True:
                        break
                # Wait for incremental delay before retrying
                await asyncio.sleep(attempt + 1)
            
            if conversation and answer_audio_status == True:
                answer_audio_url = conversation.get("answer_audio_url", None)
                if answer_audio_url:
                    messenger.send_audio(user_phone_number=self.state.mobile, audio=answer_audio_url)
            else:
                messenger.send_message(user_phone_number=self.state.mobile, message="Something went wrong. Please try again.")
        else:
            # User did not confirm the question, do nothing or handle accordingly
            pass
    

