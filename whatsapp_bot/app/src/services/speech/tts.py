import logging
from google.cloud import texttospeech as gcp_tts


def google_text_to_speech(text, lang_locale, output_file_path):
    """
    Converts the given text into speech using Google Text-to-Speech API, and saves the audio output
    to the specified file in MP3 format.

    Args:
    text (str): The text to be converted into speech.
    lang_locale (str): The language code for the desired language of the speech output.
    output_file_path (str): The path to the file where the audio output will be saved to.

    Returns:
    bool: True if the audio content is written to the output_file successfully, otherwise False.
    Exception: The exception that occurred during the API call, if any. None if the API call was successful.

    Example:
    >>> google_text_to_speech("Hello world!", "en-US", "output.mp3")
    True
    """

    try:
        client = gcp_tts.TextToSpeechClient.from_service_account_json("app/data/service_account/key.json")
        synthesis_input = gcp_tts.SynthesisInput(text=text)
        voice = gcp_tts.VoiceSelectionParams(
            language_code="{}".format(lang_locale), ssml_gender=gcp_tts.SsmlVoiceGender.NEUTRAL
        )
        audio_config = gcp_tts.AudioConfig(
            audio_encoding=gcp_tts.AudioEncoding.MP3
        )
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        with open(output_file_path, "wb") as out:
            out.write(response.audio_content)

        return True

    except Exception as e:
        logging.error(f"Google TTS: Error in google_text_to_speech: {e}")
        return False
