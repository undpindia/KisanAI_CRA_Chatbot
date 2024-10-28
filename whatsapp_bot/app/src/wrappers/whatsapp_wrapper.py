# import necessary libraries
import json
import os
from time import time
import requests
from typing import Dict, Any, Union
import logging

# Setup logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

class WhatsApp():
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WhatsApp, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        from app.src.config.config import get_settings  # Move import here
        self._settings = get_settings()  # Use getter instead of direct import
        self.base_url = "https://graph.facebook.com/v18.0"
        self._initialized = True

    @property
    def phone_number_id(self):
        return self._settings.WHATSAPP_NUMBER_ID

    @property
    def url(self):
        return f"{self.base_url}/{self.phone_number_id}"

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self._settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

    def send_message(self,user_phone_number,message):
        """
        Sends a text message to a WhatsApp user

        Parameters:
        - message (str): The text message to be sent to the user.
        - user_phone_number (str): Phone number of the user with country code without '+'.
    
        Returns:
        - dict: If the message is successfully sent, returns the body message.
        """
        data = {
            "messaging_product": "whatsapp",
            "to": user_phone_number,
            "type": "text",
            "text": {"body": message},
        }

        response = requests.request("POST", f"{self.url}/messages", headers=self.headers, json=data)
        if response.status_code == 200:
            logging.info(f"Message sent to {user_phone_number}")
            logging.info(f"Response: {response.json()}")
            return message
        else:
            logging.info(f"Message not sent to {user_phone_number}")
            logging.info(f"Response: {response.json()}")

    def preprocess(self, data: Dict[Any, Any]) -> Dict[Any, Any]:
        """
        Preprocesses the data received from the webhook.

        Parameters:
        - data (dict): The data received from the webhook.

        Returns:
        - dict: The preprocessed data extracted from the webhook.
        """

        return data["entry"][0]["changes"][0]["value"]

    def get_name(self, data: Dict[Any, Any]) -> Union[str, None]:
        """
        Extracts the name of the sender from the data received from the webhook.

        Parameters:
        - data (dict): The data received from the webhook

        Returns:
        - str: The name of the sender
        """

        contact = self.preprocess(data)
        if contact:
            return contact["contacts"][0]["profile"]["name"]

    def get_mobile(self, data: Dict[Any, Any]) -> Union[str, None]:
        """
        Extracts the mobile number of the sender from the data received from the webhook.

        Parameters:
        - data (dict): The data received from the webhook.

        Returns:
        - str: The mobile number of the sender
        """

        data = self.preprocess(data)
        if "contacts" in data:
            return data["contacts"][0]["wa_id"]
        
    def get_display_mobile(self, data: Dict[Any, Any]) -> Union[str, None]:
        """
        Extracts the display mobile number of the sender from the data received from the webhook.

        Parameters:
        - data (dict): The data received from the webhook.

        Returns:
        - str: The display mobile number of the sender
        """

        data = self.preprocess(data)
        if "metadata" in data and "display_phone_number" in data["metadata"]:
            print(data["metadata"]["display_phone_number"])
            return data["metadata"]["display_phone_number"]
        return None
    
    # def get_sender_timestamp(self, data: Dict[Any, Any]) -> Union[str, None]:
    #     """
    #     Extracts the timestamp of the first message from the data received from the webhook.

    #     Parameters:
    #     - data (dict): The data received from the webhook.

    #     Returns:
    #     - int: The timestamp of the first message, or None if not found.
    #     """

    #     data = self.preprocess(data)
    #     if "messages" in data:
    #         return data["messages"][0]["timestamp"]

    def changed_field(self, data: Dict[Any, Any]) -> str:
        """
        Helper function to check if the field changed in the data received from the webhook.

        Parameters:
        - data (dict): The data received from the webhook

        Returns:
        - str: The field changed in the data received from the webhook
        """
        
        return data["entry"][0]["changes"][0]["field"]
    
    def is_message(self, data: Dict[Any, Any]) -> bool:
        """is_message checks if the data received from the webhook is a message.

        Parameters:
        - data (dict): The data received from the webhook

        Returns:
        - bool: True if the data is a message, False otherwise
        """
        data = self.preprocess(data)
        if "messages" in data:
            return True
        else:
            return False

    def get_message_type(self, data: Dict[Any, Any]) -> Union[str, None]:
        """
        Gets the type of the message sent by the sender from the data received from the webhook.

        Parameters:
        - data (dict): The data received from the webhook

        Returns:
        - str: The type of the message sent by the sender
        """
        data = self.preprocess(data)
        if "messages" in data:
            return data["messages"][0]["type"]

    def get_message(self, data: Dict[Any, Any]) -> Union[str, None]:
        """
        Extracts the text message of the sender from the data received from the webhook.

        Parameters:
        - data (dict): The data received from the webhook
        
        Returns:
        - str: The text message received from the sender
        """
        data = self.preprocess(data)
        if "messages" in data:
            return data["messages"][0]["text"]["body"]

    def get_interactive_response(self, data: Dict[Any, Any]) -> Union[Dict, None]:
        """
        Extracts the response of the interactive message from the data received from the webhook.

        Parameters:
        - data (dict): The data received from the webhook

        Returns:
        - dict: The response of the interactive message
        """
        data = self.preprocess(data)
        if "messages" in data:
            if "interactive" in data["messages"][0]:
                return data["messages"][0]["interactive"]

    def send_audio(self, audio, user_phone_number, link=True):
        """
        Sends an audio message to a WhatsApp user
        Audio messages can either be sent by passing the audio id or by passing the audio link.

        Parameters:
        - audio (str): Audio id or link of the audio.
        - user_phone_number (str): Phone number of the user with country code without '+'.
        - link (bool): Whether to send an audio id or an audio link. 
            True means that the audio is an id, False means that the audio is a link. Default is True.
        """
        if link:
            data = {
                "messaging_product": "whatsapp",
                "to": user_phone_number,
                "type": "audio",
                "audio": {"link": audio},
            }
        else:
            data = {
                "messaging_product": "whatsapp",
                "to": user_phone_number,
                "type": "audio",
                "audio": {"id": audio},
            }

        response = requests.request("POST", f"{self.url}/messages", headers=self.headers, json=data)
        if response.status_code == 200:
            logging.info(f"Audio sent to {user_phone_number}")
            return True
        else:
            logging.info(f"Audio not sent to {user_phone_number}")
            return False

    def send_video(self, video, user_phone_number, caption, link=True):
        """
        Sends a video message to a WhatsApp user
        Video messages can either be sent by passing the video id or by passing the video link.

        Parameters:
        - video (str): Video id or link of the video.
        - user_phone_number (str): Phone number of the user with country code without '+'.
        - caption (str): Caption of the video.
        - link (bool, optional): Whether to send a video id or a video link. 
            True means that the video is an id, False means that the video is a link. Default is True.
        """
        if link:
            data = {
                "messaging_product": "whatsapp",
                "to": user_phone_number,
                "type": "video",
                "video": {"link": video, "caption": caption},
            }
        else:
            data = {
                "messaging_product": "whatsapp",
                "to": user_phone_number,
                "type": "video",
                "video": {"id": video, "caption": caption},
            }
        
        response = requests.request("POST", f"{self.url}/messages", headers=self.headers, json=data)
        if response.status_code == 200:
            logging.info(f"{caption} Video sent to {user_phone_number}")
            return True
        else:
            logging.info(f"{caption} Video not sent to {user_phone_number}")
            return False
        
    def get_audio_message_file(self, data: Dict[Any, Any]) -> Union[Dict, None]:
        """
        Retrieves the audio file associated with the first message in the provided data.
    
        Parameters:
        - data (Dict[Any, Any]): A dictionary containing the necessary information for retrieving the audio file.

        Returns:
        - Union[Dict, None]: The binary content of the audio file if successful, otherwise None.

        Note:
        - The input data is expected to be preprocessed using the `preprocess` method before calling this function.
        - The function assumes that the data structure contains a "messages" key, and the first message has an "audio" key.
        - The audio file is fetched using the provided base URL and the audio ID obtained from the first message.
        - The function makes two HTTP GET requests to obtain the audio file: one to retrieve the audio file's URL and another to fetch the actual audio content.
        - If the retrieval is successful, the binary content of the audio file is returned. Otherwise, None is returned.
        """
        data = self.preprocess(data)
        
        # Extract audio ID from the first message
        if "messages" in data:
            if "audio" in data["messages"][0]:
                audio_id =  data["messages"][0]["audio"]["id"]

        # Request to get audio file URL
        audio = requests.request("GET", f"{self.base_url}/{audio_id}", headers=self.headers)
        audio_json_response = audio.json()

        # Extract the url from the audio json response
        audio_url = audio_json_response['url']

        # Use the URL to retrieve audio message content
        response = requests.request("GET",f"{audio_url}", headers=self.headers).content

        return response

    def send_language_selection_button(self,user_phone_number):
        """
        Endpoint for sending language selection buttons.

        Parameters:
        - user_phone_number (str): The WhatsApp number of the user to whom the message will be sent.
        """
        # Specify the path to the JSON file
        json_file_path = "app/data/language/language_selection_button.json"

        # Load JSON data from the input file
        with open(json_file_path, 'r') as json_file:
            language_selection_button_json = json.load(json_file)

        # Pass the user's phone number to JSON
        language_selection_button_json["to"] = user_phone_number

        # Extract Body Text
        body_text = language_selection_button_json["interactive"]["body"]["text"]

        response = requests.request("POST", f"{self.url}/messages", headers=self.headers, json=language_selection_button_json)
        if response.status_code == 200:
            logging.info(f"language selection button sent to {user_phone_number}")
            return True
        else:
            logging.info(f"language selection button not sent to {user_phone_number}")
            return False
        
    def send_gender_selection_button(self, user_phone_number, language):
        """
        Endpoint for sending gender selection buttons based on the user's language.

        Parameters:
        - user_phone_number (str): The WhatsApp number of the user to whom the message will be sent.
        - language (str): The language for which the gender selection buttons will be sent (English, Hindi, Marathi).
        """
        # Specify the path to the JSON file
        json_file_path = "app/data/confirmation/multilingual_gender_selection_buttons.json"

        # Load JSON data from the input file
        with open(json_file_path, 'r') as json_file:
            gender_selection_button_json = json.load(json_file)

        # Pass the language
        specific_language_gender_selection_json = gender_selection_button_json[language]

        # Pass the user's phone number to JSON
        specific_language_gender_selection_json["to"] = user_phone_number

        response = requests.request("POST", f"{self.url}/messages", headers=self.headers, json=specific_language_gender_selection_json)
        if response.status_code == 200:
            logging.info(f"Gender selection button sent to {user_phone_number} in {language}")
            return True
        else:
            logging.info(f"Gender selection button not sent to {user_phone_number} in {language}")
            return False
        

    def send_language_confirmation(self, user_phone_number, language):
        """
        Endpoint for sending language confirmation buttons in the specified language
    
        Parameters:
        - user_phone_number (str): The WhatsApp number of the user to whom the message will be sent.
        - language (str): The language for which the confirmation buttons will be sent (English, Hindi, Marathi).
        """

        # Specify the path to your JSON file
        json_file_path = "app/data/confirmation/multilingual_language_confirmation_buttons.json"

        # Load JSON data from the input file
        with open(json_file_path, 'r') as json_file:
            language_confirmation_json = json.load(json_file)
        
        # Pass the language
        specific_language_confirmation_json = language_confirmation_json[language]

        # Pass the user's phone number to JSON
        specific_language_confirmation_json["to"] = user_phone_number

        response = requests.request("POST", f"{self.url}/messages", headers=self.headers, json=specific_language_confirmation_json)
        if response.status_code == 200:
            logging.info(f"{language} language confirmation button sent to {user_phone_number}")
            return True
        else:
            logging.info(f"{language} language confirmation button not sent to {user_phone_number}")
            return False
    
    def send_consent_request(self, user_phone_number, language):
        """
        Endpoint for sending consent confirmation buttons in the specified language

        Parameters:
        - user_phone_number (str): The WhatsApp number of the user to whom the message will be sent.
        - language (str): The language for which the consent confirmation buttons will be sent (English, Hindi, Marathi).
        """
        
        # Specify the path to your JSON file
        json_file_path = "app/data/confirmation/multilingual_consent_confirmation_buttons.json"

        # Load JSON data from the input file
        with open(json_file_path, 'r') as json_file:
            consent_confirmation_json = json.load(json_file)

        # Pass the language
        language_specific_consent_confirmation_json = consent_confirmation_json[language]

        # Pass the user's phone number to JSON
        language_specific_consent_confirmation_json["to"] = user_phone_number

        response = requests.request("POST", f"{self.url}/messages", headers=self.headers, json=language_specific_consent_confirmation_json)
        if response.status_code == 200:
            logging.info(f"{language} language consent confirmation button sent to {user_phone_number}")
            return True
        else:
            logging.info(f"{language} language consent confirmation button not sent to {user_phone_number}")
            return False
    
    def send_consent_rejection_confirmation(self, user_phone_number, language):
        """
        Endpoint for sending consent confirmation buttons in the specified language

        Parameters:
        - user_phone_number (str): The WhatsApp number of the user to whom the message will be sent.
        - language (str): The language for which the consent confirmation buttons will be sent (English, Hindi, Marathi).
        """
        
        # Specify the path to your JSON file
        json_file_path = "app/data/confirmation/multilingual_consent_rejection_buttons.json"

        # Load JSON data from the input file
        with open(json_file_path, 'r') as json_file:
            consent_rejection_confirmation_json = json.load(json_file)

        # Pass the language
        language_specific_consent_confirmation_json = consent_rejection_confirmation_json[language]

        # Pass the user's phone number to JSON
        language_specific_consent_confirmation_json["to"] = user_phone_number

        response = requests.request("POST", f"{self.url}/messages", headers=self.headers, json=language_specific_consent_confirmation_json)
        if response.status_code == 200:
            return True
        else:
            return False

    def send_name_confirmation(self, user_phone_number, message, language):
        """
        Endpoint for sending name confirmation buttons in the specified language

        Parameters:
        - user_phone_number (str): The WhatsApp number of the user to whom the message will be sent.
        - message (str): The message to be sent along with name confirmation buttons.
        - language (str): The language for which the name confirmation buttons will be sent (English, Hindi, Marathi).
        """

        # Specify the path to your JSON file
        json_file_path = "app/data/confirmation/multilingual_name_confirmation_buttons.json"

        # Load JSON data from the input file
        with open(json_file_path, 'r') as json_file:
            name_confirmation_json = json.load(json_file)

        # Pass the language
        language_specific_name_confirmation_json = name_confirmation_json[language]

        # Pass the user's phone number and message to JSON
        language_specific_name_confirmation_json["to"] = user_phone_number
        language_specific_name_confirmation_json["interactive"]["body"]["text"] = message

        response = requests.request("POST", f"{self.url}/messages", headers=self.headers, json=language_specific_name_confirmation_json)
        if response.status_code == 200:
            logging.info(f"{language} language name confirmation button sent to {user_phone_number}")
            return True
        else:
            logging.info(f"{language} language name confirmation button not sent to {user_phone_number}")
            return False
    
    def send_location_confirmation(self, user_phone_number, message, language):
        """
        Endpoint for sending location confirmation buttons in the specified language

        Parameters:
        - user_phone_number (str): The WhatsApp number of the user to whom the message will be sent.
        - message (str): The message to be sent along with location confirmation buttons.
        - language (str): The language for which the location confirmation buttons will be sent (English, Hindi, Marathi).
        """
    
        # Specify the path to your JSON file
        json_file_path = "app/data/confirmation/multilingual_location_confirmation_buttons.json"

        # Load JSON data from the input file
        with open(json_file_path, 'r') as json_file:
            location_confirmation_json = json.load(json_file)

        # Pass the language
        language_specific_location_confirmation_json = location_confirmation_json[language]

        # Pass the user's phone number and message to JSON
        language_specific_location_confirmation_json["to"] = user_phone_number
        language_specific_location_confirmation_json["interactive"]["body"]["text"] = message

        response = requests.request("POST", f"{self.url}/messages", headers=self.headers, json=language_specific_location_confirmation_json)
        if response.status_code == 200:
            logging.info(f"{language} language location confirmation button sent to {user_phone_number}")
            return True
        else:
            logging.info(f"{language} language location confirmation button not sent to {user_phone_number}")
            return False

    def send_gender_confirmation(self, user_phone_number, message, language):
        """
        Endpoint for sending gender confirmation buttons in the specified language

        Parameters:
        - user_phone_number (str): The WhatsApp number of the user to whom the message will be sent.
        - message (str): The message to be sent along with gender confirmation buttons.
        - language (str): The language for which the gender confirmation buttons will be sent (English, Hindi, Marathi).
        """

        # Specify the path to your JSON file
        json_file_path = "app/data/confirmation/multilingual_gender_confirmation_buttons.json"

        # Load JSON data from the input file
        with open(json_file_path, 'r') as json_file:
            gender_confirmation_json = json.load(json_file)

        # Pass the language
        language_specific_gender_confirmation_json = gender_confirmation_json[language]

        # Pass the user's phone number and message to JSON
        language_specific_gender_confirmation_json["to"] = user_phone_number
        language_specific_gender_confirmation_json["interactive"]["body"]["text"] = message

        response = requests.request("POST", f"{self.url}/messages", headers=self.headers, json=language_specific_gender_confirmation_json)
        if response.status_code == 200:
            logging.info(f"{language} language gender confirmation button sent to {user_phone_number}")
            return True
        else:
            logging.info(f"{language} language gender confirmation button not sent to {user_phone_number}")
            return False

    def send_question_confirmation(self, user_phone_number, message, language):
        """
        Endpoint for sending question confirmation buttons in the specified language

        Parameters:
        - user_phone_number (str): The WhatsApp number of the user to whom the message will be sent.
        - message (str): The message to be sent along with question confirmation buttons.
        - language (str): The language for which the question confirmation buttons will be sent (English, Hindi, Marathi).
        """

        # Specify the path to your JSON file
        json_file_path = "app/data/confirmation/multilingual_question_confirmation_buttons.json"

        # Load JSON data from the input file
        with open(json_file_path, 'r') as json_file:
            question_confirmation_json = json.load(json_file)

        # Pass the language
        language_specific_question_confirmation_json = question_confirmation_json[language]

        # Pass the user's phone number and message to JSON
        language_specific_question_confirmation_json["to"] = user_phone_number
        language_specific_question_confirmation_json["interactive"]["body"]["text"] = message

        response = requests.request("POST", f"{self.url}/messages", headers=self.headers, json=language_specific_question_confirmation_json)
        if response.status_code == 200:
            logging.info(f"{language} language question confirmation button sent to {user_phone_number}")
            return True
        else:
            logging.info(f"{language} language question confirmation button not sent to {user_phone_number}")
            return False
    
    def send_question_confirmation_with_chatid(self, user_phone_number, message, language, chat_id):
        # Load the JSON template
        with open('app/data/confirmation/multilingual_question_confirmation_with_chatid_buttons.json', 'r') as file:
            templates = json.load(file)
        
        # Get the template for the specified language
        template = templates[language]
        
        # Format the button IDs with chat_id
        for button in template['interactive']['action']['buttons']:
            button['reply']['id'] = button['reply']['id'].format(chatid=chat_id)
        
        # Set the message text
        template['to'] = user_phone_number
        template['interactive']['body']['text'] = message
        
        # Send the message (assuming a send_message method exists)
        response = requests.request("POST", f"{self.url}/messages", headers=self.headers, json=template)
        if response.status_code == 200:
            logging.info(f"{language} language question confirmation button sent to {user_phone_number}")
            return True
        else:
            logging.info(f"{language} language question confirmation button not sent to {user_phone_number}")
            return False
    
    def get_delivery(self, data: Dict[Any, Any]) -> Union[Dict, None]:
        """
        Extracts the delivery status of the message from the data received from the webhook.
        Args:
            data [dict]: The data received from the webhook

        Returns:
            dict: The delivery status of the message and message id of the message
        """

        # Traverse the nested structure using if conditions
        if 'entry' in data:
            entry = data['entry'][0] if data['entry'] else None
            if entry and 'changes' in entry:
                changes = entry['changes'][0] if entry['changes'] else None
                if changes and 'value' in changes:
                    value = changes['value']
                    if value and 'statuses' in value:
                        statuses = value['statuses']
                        if statuses and len(statuses) > 0:
                            # Extract status from the first element in the statuses array
                            status = statuses[0]['status']
                            return status

    @classmethod
    def refresh_instance(cls):
        cls._instance = None



