from google.cloud import translate_v2 as translate

def detect_text(text):
    """
    Detect the language of a given text.

    Args:
        text (str): The text for which to detect the language.

    Returns:
        str: The ISO 639-1 language code of the detected language.
    """

    # Initialize the translation client with your service account credentials
    client = translate.Client.from_service_account_json('app/data/service_account/key.json')

    # Language Detect
    language_detected = client.detect_language(text)
    language_detected_code = language_detected['language']

    return language_detected_code

def translate_text(text,source_language,target_language):
    """
    Translate a given text from a source language to a target language.

    Args:
        text (str): The text to translate.
        source_language (str): The ISO 639-1 code of the source language.
        target_language (str): The ISO 639-1 code of the target language.

    Returns:
        str: The tr
    """

    # Initialize the translation client with your service account credentials
    client = translate.Client.from_service_account_json('app/data/service_account/key.json')

    # Translate the text
    result = client.translate(values=text,source_language=source_language,target_language=target_language)
    translated_text = result['translatedText']

    return translated_text