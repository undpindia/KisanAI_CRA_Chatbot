import requests, uuid, json,os




endpoint = "https://api.cognitive.microsofttranslator.com"


code_dict={}

def translate(text,lang,video_id):
    if (lang != "english" ):
            path = '/translate'
            constructed_url = endpoint + path

            params = {
                'api-version': '3.0',
                'to': 'en'
            }

            headers = {
                'Ocp-Apim-Subscription-Key': os.getenv("AZURE_TRANSLATOR_SUBSCRIPTION_KEY"),
                # location required if you're using a multi-service or regional (not global) resource.
                'Ocp-Apim-Subscription-Region':os.getenv("AZURE_TRASLATOR_REGION"),
                'Content-type': 'application/json',
                'X-ClientTraceId': str(uuid.uuid4())
            }

            # You can pass more than one object in body.
            body = [{
                'text': text
            }]

            request = requests.post(constructed_url, params=params, headers=headers, json=body)
            response = request.json()

            # output=json.dumps(response, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))
            output = response[0]['translations'][0]['text']
            
            return output
         
    else:
        return text
    
def translate_text(text):
    
    headers = {
        'accept': 'application/json',
        'X-API-Key': '0Lvk4ebM1Koppt5NbCHzWZ2tT9M0qnoa',  # Replace with your actual API key
        'Content-Type': 'application/json',
    }
    json_data = {
        'data': {
            'text': text,
            'language': 'hindi',
            
        },
    }
    response = requests.post('https://qa.sarvam.ai/api/runtime/conversation', headers=headers, json=json_data,timeout=60)
    if response.status_code == 200:
        result = response.json()
        return  result['data']['text'] # You'll need to adjust this based on the actual response structure
    else:
        return "Error: " + str(response.status_code)


# def translate(text, lang, video_id):
#     # Define the path where translations will be saved
#     output_dir = "output_data/translations"
#     # Create the directory if it does not exist
#     os.makedirs(output_dir, exist_ok=True)

#     # Define the output file path
#     file_path = os.path.join(output_dir, f"{video_id}_translated.txt")

#     # Check if the translation already exists
#     if os.path.isfile(file_path):
#         with open(file_path, 'r', encoding='utf-8') as file:
#             translated_text = file.read()
#     else:
#         if lang != "english":
#             path = '/translate'
#             constructed_url = endpoint + path

#             params = {
#                 'api-version': '3.0',
#                 'to': 'en'
#             }

#             headers = {
#                 'Ocp-Apim-Subscription-Key': os.getenv("AZURE_TRANSLATOR_SUBSCRIPTION_KEY"),
#                 # location required if you're using a multi-service or regional (not global) resource.
#                 'Ocp-Apim-Subscription-Region':os.getenv("AZURE_TRASLATOR_REGION"),
#                 'Content-type': 'application/json',
#                 'X-ClientTraceId': str(uuid.uuid4())
#             }

#             # You can pass more than one object in body.
#             body = [{
#                 'text': text
#             }]

#             request = requests.post(constructed_url, params=params, headers=headers, json=body)
#             response = request.json()

#             output = response[0]['translations'][0]['text']
            
            
#             # Save the translated text to a file
#             with open(file_path, 'w', encoding='utf-8') as file:
#                 file.write(output)
#             return output
#         else:
#             # If the language is English, no translation is needed, just save the text
#             translated_text = text
#             with open(file_path, 'w', encoding='utf-8') as file:
#                 file.write(translated_text)

#     return translated_text



# obj=translate_text(''' It’s time to rebuild, with hands unified,
# Where ancient echoes in modern hearts reside.
# It’s time for stones to chant once more,
# The sacred names, the sages adore.

# It’s time for spires to reach for skies,
# Where faith’s pure flame eternally lies.
# It’s time for resurgence of Hindutva’s core,
# Where Dharmic values we re-explore.

# It’s time for culture to reclaim its space,
# In every carved figure, every etched grace.
# It’s time for history’s page to turn,
# Where Ram’s ideals in every heart burn.

# It’s time for Ayodhya to rise anew,
# A beacon of peace, for the many, not few.
# It’s time for resurgence, a new age’s start,
# Where Ram temple stands, a work of art.''') 

# print(obj)
