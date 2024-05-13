# def preprocess_text(temperature,translated_content):
#     from openai import OpenAI
#     import os

#     client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
    
#     response = client.chat.completions.create(
#         model="gpt-4",
#         temperature=temperature,
#         messages=[
#             {
#                 "role": "system",
#                 "content": '''You are a helpful assistant for the company KissanAI. 
#                 Your task is to correct any spelling discrepancies in the transcribed text. 
#                 Remove all type of special characters. 
#                 Only add necessary punctuation such as periods, commas, and capitalization, and use only the context provided.
#                 Don't add any new context out of the provided context
#                 '''
#             },
#             {
#                 "role": "user",
#                 "content": translated_content
#             }
#         ]
#     )
#     return response.choices[0].message.content


import os
from openai import OpenAI
import tiktoken

def preprocess_text(temperature, translated_content):
    # Initialize the OpenAI client
    import os
    from openai import AzureOpenAI
        
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
        api_version =os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )
    # Get the encoding for the GPT model
    encoding = tiktoken.encoding_for_model("gpt-4")
    
    # Define the function to count tokens
    def num_tokens(text):
        return len(encoding.encode(text))
    
    # Define the function to process text in batches
    def process_batch(batch):
        response = client.chat.completions.create(
            model="gpt-4-116-preview",
            temperature=temperature,
            messages=[
                {
                    "role": "system",
                    "content": '''You are a helpful assistant for the company KissanAI. 
                    Your task is to correct any spelling discrepancies in the transcribed text. 
                    Remove all type of special characters. 
                    Only add necessary punctuation such as periods, commas, and capitalization, and use only the context provided.
                    Don't add any new context out of the provided context
                    '''
                },
                {
                    "role": "user",
                    "content": batch
                }
            ]
        )
        return response.choices[0].message.content
        
    # Initialize variables
    max_tokens = 3500
    processed_content = []
    current_batch = []
    current_count = 0
    
    # Tokenize the translated_content
    tokens = encoding.encode(translated_content)
    
    # Break down content into batches and process each batch
    for token in tokens:
        current_batch.append(token)
        current_count += 1
        if current_count >= max_tokens:
            batch_text = encoding.decode(current_batch)
            processed_content.append(process_batch(batch_text))
            current_batch = []
            current_count = 0
    
    # Process the last batch if any tokens are left
    if current_batch:
        batch_text = encoding.decode(current_batch)
        processed_content.append(process_batch(batch_text))
    
    # Combine all the processed content
    return ''.join(processed_content)
