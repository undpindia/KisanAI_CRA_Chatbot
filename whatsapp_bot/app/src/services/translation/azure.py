import requests
import os


def azure_translate_text(input_text, from_language_code, to_language_code):
    """
    Translate text using Azure Translator service.

    Example:
        >>> azure_translate_text("Hello", "en", "hi")
        'नमस्ते'
        >>> azure_translate_text("नमस्ते", "hi", "en")
        'Hello'

    Args:
        input_text (str): The text to be translated
        from_language_code (str): Source language code (e.g., 'en' for English, 'hi' for Hindi, 'mr' for Marathi)
        to_language_code (str): Target language code (e.g., 'en' for English, 'hi' for Hindi, 'mr' for Marathi)

    Returns:
        str: Translated text if successful
        None: If translation fails or encounters an error

    Note:
        Requires the following environment variables to be set:
        - AZURE_TRANSLATOR_ENDPOINT
        - AZURE_TRANSLATOR_KEY
        - AZURE_TRANSLATOR_REGION
    """
    try:
        endpoint = os.getenv("AZURE_TRANSLATOR_ENDPOINT")
        headers = {
            "Ocp-Apim-Subscription-Key": os.getenv("AZURE_TRANSLATOR_KEY"),
            "Ocp-Apim-Subscription-Region": os.getenv("AZURE_TRANSLATOR_REGION"),
            "Content-Type": "application/json"
        }
        params = {
            "api-version": "3.0",
            "from": from_language_code,
            "to": [to_language_code],
        }
        body = [
            {"Text": input_text}
        ]

        response = requests.post(
            endpoint + "/translate", headers=headers, params=params, json=body
        )
        response_json = response.json()

        # Extracting the translated text
        translated_text = response_json[0]["translations"][0]["text"]

        return translated_text

    except Exception as e:
        print(f"Translation error: {str(e)}")  # More descriptive error message
        return None


def azure_transliterate_text(input_text, from_language, to_language, language_code):
    """
    Transliterate text from one script to another using Azure Translator service.
    Converts text between Latin (English) and Devanagari (Hindi/Marathi) scripts.

    Example:
        >>> azure_transliterate_text("namaste", "Latn", "Deva", "hi")
        'नमस्ते'
        >>> azure_transliterate_text("नमस्ते", "Deva", "Latn", "hi")
        'namaste'

    Args:
        input_text (str): The text to be transliterated
        from_language (str): Source script ('Latn' for Latin/English, 'Deva' for Devanagari)
        to_language (str): Target script ('Latn' for Latin/English, 'Deva' for Devanagari)
        language_code (str): Language code ('en' for English, 'hi' for Hindi, 'mr' for Marathi)

    Returns:
        str: Transliterated text if successful
        None: If transliteration fails or encounters an error

    Note:
        Requires the following environment variables to be set:
        - AZURE_TRANSLATOR_ENDPOINT
        - AZURE_TRANSLATOR_KEY
        - AZURE_TRANSLATOR_REGION
    """
    try:
        endpoint = os.getenv("AZURE_TRANSLATOR_ENDPOINT")
        headers = {
            "Ocp-Apim-Subscription-Key": os.getenv("AZURE_TRANSLATOR_KEY"),
            "Ocp-Apim-Subscription-Region": os.getenv("AZURE_TRANSLATOR_REGION"),
            "Content-Type": "application/json"
        }
        params = {
            "api-version": "3.0",
            "language": language_code,
            "fromScript": from_language,
            "toScript": to_language,
        }
        body = [
            {"Text": input_text}
        ]

        response = requests.post(
            endpoint + "/transliterate", headers=headers, params=params, json=body
        )
        response_json = response.json()

        # Extracting the transliterated text
        transliterated_text = response_json[0]["text"]

        return transliterated_text

    except Exception as e:
        print(f"Transliteration error: {str(e)}")  # More descriptive error message
        return None
