from app.src.services.speech.stt import azure_speech_to_text
from app.src.services.translation.azure import azure_translate_text, azure_transliterate_text
from app.src.services.speech.tts import google_text_to_speech
from llama_index.core.retrievers import VectorIndexRetriever, KeywordTableSimpleRetriever
import json
import os
import uuid
from app.src.services.llm.index_initializer import vector_index
from whatsapp_bot.app.logs.logger import logger

from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class QueryEngine():
    
    def __init__(self, language):
        self.language = language
        self.lang_code = None
        self.lang_code_locale = None
        self.azure_transliteration_code = None
        self.question = None
        self.question_en = None
        self.context = None
        self.prompt = None
        self._get_language_codes()
        
    def _get_language_codes(self):
        with open("app/data/language/lang.json") as f:
            languages = json.load(f)
        for lang, lang_info in languages.items():
            if lang == self.language:
                self.lang_code = lang_info["code"]
                self.lang_code_locale = lang_info["code_locale"]
                self.azure_transliteration_code = lang_info["azure_transliteration_code"]
    
    def text_query_response(self, question, question_prev, answer_prev):
        """
        Gets the requested question answer

        Parameters:
        - language (str): The language for which the answer is requested.
        - question (str): The user question.
        - question_prev (str): The previous user question for context.
        - answer_prev (str): The previous answer for context.

        Returns:
        - answer (str): Received text-based answer.
        """

        if self.azure_transliteration_code != "Latn":
            self.question = question
            # question_native = azure_transliterate_text(self.question, "Latn", self.azure_transliteration_code, self.lang_code)
            self.question_en = azure_translate_text(self.question, self.lang_code, "en")
        else:
            if self.lang_code == "en":
                self.question_en = question
                self.question = question
            else:
                self.question = question
                self.question_en = azure_translate_text(question, self.lang_code, "en")
        print(self.question)
        print(self.question_en)
        self.answer_en = self.llm_response(question_prev, answer_prev)
        
        if self.lang_code == "en":
            self.answer = self.answer_en
        else:
            self.answer = azure_translate_text(self.answer_en, "en", self.lang_code)
        
        return self.answer
    
    def audio_query_response_text(self, audio, question_prev, answer_prev):
        """
        Retrieves an audio-based answer using a voice response API.

        Parameters:
        - language (str): The language for which the answer is requested.
        - audio (str): The path to the audio file containing the user's question.
        - question_prev (str): The previous user question for context.
        - answer_prev (str): The previous answer for context.

        Returns:
        - text_answer (str): The text-based answer received from the voice response API.
        - audio_answer (str): The audio-based answer received from the voice response API.
        """
        
        self.question = azure_speech_to_text(audio, self.lang_code)
        self.answer = self.text_query_response(self.question, question_prev, answer_prev)
        
        return self.answer
    
    def audio_query_response_audio(self, chat_id=None):
        """
        Retrieves an audio-based answer using a voice response API.

        Parameters:
        - language (str): The language for which the answer is requested.
        - audio (str): The path to the audio file containing the user's question.
        - question_prev (str): The previous user question for context.
        - answer_prev (str): The previous answer for context.

        Returns:
        - text_answer (str): The text-based answer received from the voice response API.
        - audio_answer (str): The audio-based answer received from the voice response API.
        """
        if chat_id:
            audio_uuid = chat_id
        else:
            audio_uuid = str(uuid.uuid4())
        audio_answer_path = f"app/data/output/{audio_uuid}.mp3"
        status = google_text_to_speech(self.answer, self.lang_code_locale, audio_answer_path)
        if not status:
            return None, None
        audio_url = f'{os.getenv("APP_URL")}/dl/user/{audio_uuid}.mp3'

        return audio_url, audio_answer_path
    
    def _retrieve_knowledge(self):
        vector_retriever = VectorIndexRetriever(index=vector_index, similarity_top_k=3)
        nodes = vector_retriever.retrieve(self.question_en)
        self.context = ""
        for node in nodes:
            self.context = self.context + "\n" + node.text
            
    def _create_prompt(self):
        self._retrieve_knowledge()
        if self.context:
            self.prompt = f"""
            You are a helpful AI assistant for Climate Resilient Agriculture for small holder farmers in India. 
            Answer from the following context.

            Context
            ==============
            {self.context}
            ==============
            
            - If asked about your origin, creator, developer or any similar context, say you are developed by KissanAI and UNDP.
            - Please answer briefly in simple language.
            - If you don't find answer in context, you can provide answer in context of best practices for climate resilient practices in India.
            - DO NOT MAKE UP ANY FALSE INFORMATION. USE ONLY THE GIVEN CONTEXT. 
            - YOU CAN ALSO ASK USER TO PROVIDE MORE INFORMATION IF NEEDED.
            - If the user question is short or not clear, you can ask for more details.
            - Answre in simple language and in less than 100 words.
            - If context has youtube URLs, please provide most relavent one in the answer for reference.
            - Add follow up questions if needed.
            """
        else:
            self.prompt = """
            You are a helpful AI assistant for Climate Resilient Agriculture for small holder farmers in India. 
            - If asked about your origin, creator, developer or any similar context, say you are developed by KissanAI and UNDP.
            - Please answer briefly in simple language.
            - If you don't find answer in context, you can provide answer in context of best practices for climate resilient practices in India.
            - DO NOT MAKE UP ANY FALSE INFORMATION. USE ONLY THE GIVEN CONTEXT. 
            - YOU CAN ALSO ASK USER TO PROVIDE MORE INFORMATION IF NEEDED.
            - If the user question is short or not clear, you can ask for more details.
            - Answre in simple language and in less than 100 words.
            - If context has youtube URLs, please provide most relavent one in the answer for reference.
            - Add follow up questions if needed.
            """

    def create_llm_message(self, question_prev, answer_prev):
        self._create_prompt()
        
        if question_prev and answer_prev:
            return [
                {
                    "role": "system", 
                    "content": self.prompt
                },
                {
                    "role": "user", 
                    "content": question_prev
                },
                {
                    "role": "assistant", 
                    "content": answer_prev
                },
                {
                    "role": "user", 
                    "content": self.question_en
                }
            ]
        else:
            return [
                {
                    "role": "system", 
                    "content": self.prompt
                },
                            {
                    "role": "user", 
                    "content": self.question_en
                },
                ]
    
    def llm_response(self, question_prev, answer_prev):
        message = self.create_llm_message(question_prev, answer_prev)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=message
        )
        return response.choices[0].message.content