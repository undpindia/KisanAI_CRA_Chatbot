import os
import json
import logging
import tempfile
from azure.cognitiveservices import speech as azure_speech
from app.src.services.speech.converter import convert_ogg_to_mp3
from google.cloud import speech
from openai import OpenAI


def google_speech_recognize(config: speech.RecognitionConfig, audio: speech.RecognitionAudio) -> speech.RecognizeResponse:
    """
    Translates speech to text using the Google Cloud Platform (GCP) Speech-to-Text API.

    Parameters:
    - config (speech.RecognitionConfig): The configuration for speech recognition, including language, audio format, etc.
    - audio (speech.RecognitionAudio): The audio data to be recognized.

    Returns:
    - speech.RecognizeResponse: The response containing the recognized text and additional information.
    """

    # Generate connection
    client = speech.SpeechClient.from_service_account_file('app/data/service_account/key.json')
    # Synchronous speech recognition request
    response = client.recognize(config=config, audio=audio)
    # Return results
    return response.results


def azure_speech_to_text(audio_file_path, lang_locale):
    try:
        subscription_key = os.getenv("AZURE_SPEECH_SUBSCRIPTION_KEY")
        region = os.getenv("AZURE_SPEECH_REGION")
        speech_config = azure_speech.SpeechConfig(subscription=subscription_key, region=region)
        audio_config = azure_speech.audio.AudioConfig(filename=audio_file_path)
        speech_recognizer = azure_speech.SpeechRecognizer(speech_config=speech_config,
                                                          language=lang_locale,
                                                          audio_config=audio_config)
        result = speech_recognizer.recognize_once()
        if result.reason == azure_speech.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == azure_speech.ResultReason.NoMatch:
            logging.error("Azure STT: No speech could be recognized.")
            return None
        elif result.reason == azure_speech.ResultReason.Canceled:
            logging.error(f"Azure STT: Speech recognition was canceled. Error: {result.error_details}")
            return None
        else:
            logging.error("Azure STT: An unknown error occurred.")
            return None

    except Exception as e:
        logging.error(f"Azure STT: Error in azure_speech_to_text: {e}")
        return None

def openai_whisper(audio_data, translate):
    temp_mp3_file_path = None
    try:
        # Convert the OGG audio data to MP3
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_mp3_file:
            convert_ogg_to_mp3(audio_data, temp_mp3_file)
            temp_mp3_file_path = temp_mp3_file.name

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        if translate:
            translation = client.audio.translations.create(
                model="whisper-1",
                file=open(temp_mp3_file_path, "rb")
            )
            return translation.text
        else:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=open(temp_mp3_file_path, "rb")
            )
            return transcription.text
    except Exception as e:
        logging.error(f"Error in openai_whisper: {e}")
        return None
    finally:
        # Clean up the temporary file
        if temp_mp3_file_path and os.path.exists(temp_mp3_file_path):
            os.remove(temp_mp3_file_path)