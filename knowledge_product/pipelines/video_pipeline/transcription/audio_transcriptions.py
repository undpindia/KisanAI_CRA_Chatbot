# from keys.keys import *
import time 
import os
# import TimeSpan
import azure.cognitiveservices.speech as azure_speech
import time
from pydub import AudioSegment
from dotenv import load_dotenv
import openai
import os
import json

# Load environment variables from .env file
load_dotenv()



# from openai import OpenAI
# client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
# print(os.getenv("OPENAI_KEY"))

import os
from openai import AzureOpenAI
    
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version =os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

# # speech_key, service_region = azure_speech_service_key, "centralindia"

def get_transcription_frm_audio(path):
    audio_file= open(path, "rb")
    transcript = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file,
    response_format="text"
    )
    return transcript

def get_translation_frm_audio(path):
    audio_file= open(path, "rb")
    transcript = client.audio.translations.create(
    model="whisper-1", 
    file=audio_file,
    response_format="text"
    )
    return transcript


# def get_transcription_frm_audio_v2(path, video_id):
#     print(f"transcribing transcript from --- {path}")
#     transcriptions_dir = "output_data/transcriptions"
#     os.makedirs(transcriptions_dir, exist_ok=True)
    
#     transcript_file_path = os.path.join(transcriptions_dir, f"{video_id}_transcript.txt")
    
#     if os.path.exists(transcript_file_path):
#         with open(transcript_file_path, 'r', encoding='utf-8') as transcript_file:
#             transcript = transcript_file.read()
#         transcript_dict = json.loads(transcript)
#     else:
#         with open(path, "rb") as audio_file:
#             transcription_obj = client.audio.transcriptions.create(
#                 model="whisper-1", 
#                 file=audio_file,
#                 response_format="verbose_json"
#             )
        
#         text = transcription_obj.text
#         language = transcription_obj.language
#         transcript_dict = {
#             "text": text,
#             "language": language
#         }
#         # print(transcript_dict)
#         with open(transcript_file_path, 'w', encoding='utf-8') as transcript_file:
#             json.dump(transcript_dict, transcript_file, ensure_ascii=False, indent=4)
    
#     return transcript_dict


def get_transcription_frm_audio_v2(path, video_id):
    print(f"transcribing transcript from --- {path}")
    transcriptions_dir = "output_data/transcriptions"
    os.makedirs(transcriptions_dir, exist_ok=True)
    
    transcript_file_path = os.path.join(transcriptions_dir, f"{video_id}_transcript.txt")
    
    if os.path.exists(transcript_file_path):
        with open(transcript_file_path, 'r', encoding='utf-8') as transcript_file:
            transcript = transcript_file.read()
        transcript_dict = json.loads(transcript)
    else:
        song = AudioSegment.from_file(path)
        ten_minutes = 10 * 60 * 1000  # PyDub handles time in milliseconds
        parts = len(song) // ten_minutes + (1 if len(song) % ten_minutes else 0)
        full_transcript_text = ""
        full_transcript_language = None
        
        for part in range(parts):
            start = part * ten_minutes
            end = start + ten_minutes if (start + ten_minutes) < len(song) else len(song)
            audio_part = song[start:end]
            
            audio_part_file_path = os.path.join(transcriptions_dir, f"{video_id}_part{part}.mp3")
            audio_part.export(audio_part_file_path, format="mp3")
            
            with open(audio_part_file_path, "rb") as audio_file:
                transcription_obj = client.audio.transcriptions.create(
                    model="whisper", 
                    file=audio_file,
                    response_format="verbose_json"
                )
            os.remove(audio_part_file_path)  # Clean up the temporary audio file
            
            full_transcript_text += transcription_obj.text
            if full_transcript_language is None:
                full_transcript_language = transcription_obj.language
        
        transcript_dict = {
            "text": full_transcript_text,
            "language": full_transcript_language
        }
        
        with open(transcript_file_path, 'w', encoding='utf-8') as transcript_file:
            json.dump(transcript_dict, transcript_file, ensure_ascii=False, indent=4)
    
    return transcript_dict
####################################################################

# Similar process as above but parallel 


import os
import json
from pydub import AudioSegment
from multiprocessing import Pool, Manager
ten_minutes = 10 * 60 * 1000  # PyDub handles time in milliseconds


def transcribe_part(args):
    path, part_num, video_id, transcriptions_dir, song = args
    start = part_num * ten_minutes
    end = start + ten_minutes if (start + ten_minutes) < len(song) else len(song)
    audio_part = song[start:end]
    audio_part_file_path = os.path.join(transcriptions_dir, f"{video_id}_part{part_num}.mp3")
    audio_part.export(audio_part_file_path, format="mp3")

    with open(audio_part_file_path, "rb") as audio_file:
        transcription_obj = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json"
        )

    os.remove(audio_part_file_path)  # Clean up the temporary audio file
    return transcription_obj

def get_transcription_frm_audio_parallel(path, video_id):
    # Print a statement indicating the start of transcription process
    print(f"transcribing transcript from --- {path}")

    # Directory where transcriptions will be stored
    transcriptions_dir = "output_data/transcriptions"
    # Ensure the directory exists, create if not
    os.makedirs(transcriptions_dir, exist_ok=True)

    # Define the path for the transcript file based on the video ID
    transcript_file_path = os.path.join(transcriptions_dir, f"{video_id}_transcript.txt")

    # Check if a transcript file already exists for the current video ID
    if os.path.exists(transcript_file_path):
        # Open the existing transcript file and load its content
        with open(transcript_file_path, 'r', encoding='utf-8') as transcript_file:
            transcript = transcript_file.read()
            transcript_dict = json.loads(transcript)
    else:
        # Load the audio file from the specified path
        song = AudioSegment.from_file(path)
        # Time segment size for splitting the audio, 10 minutes in milliseconds
        ten_minutes = 10 * 60 * 1000

        # Calculate the number of parts to divide the audio into
        parts = len(song) // ten_minutes + (1 if len(song) % ten_minutes else 0)

        # Use a multiprocessing manager to handle results from parallel processes
        with Manager() as manager:
            results = manager.list()  # A managed list to store results
            pool = Pool()  # Pool of worker processes

            # Prepare arguments for each part to be processed
            args = [(path, part, video_id, transcriptions_dir) for part in range(parts)]
            # Map each part to the transcription function in parallel
            transcription_objs = pool.map(transcribe_part, args)
            pool.close()  # Close the pool to prevent more tasks from being submitted
            pool.join()  # Wait for all worker processes to finish

            # Initialize variables for assembling the full transcript
            full_transcript_text = ""
            full_transcript_language = None

            # Aggregate results from all transcribed parts
            for transcription_obj in transcription_objs:
                full_transcript_text += transcription_obj.text
                if full_transcript_language is None:
                    full_transcript_language = transcription_obj.language

            # Create a dictionary to store the combined transcript and language
            transcript_dict = {
                "text": full_transcript_text,
                "language": full_transcript_language
            }

            # Save the full transcript to a file
            with open(transcript_file_path, 'w', encoding='utf-8') as transcript_file:
                json.dump(transcript_dict, transcript_file, ensure_ascii=False, indent=4)

    # Return the dictionary containing the transcript and language
    return transcript_dict




#transcribe only upto 5 minutes of audio

def get_transcription_frm_audio_5_minutes(path, video_id):
    # Print a statement indicating the path of the file being transcribed
    print(f"transcribing transcript from --- {path}")
    
    # Directory where transcriptions will be saved
    transcriptions_dir = "output_data/transcriptions"
    
    # Ensure the transcription directory exists; create if it doesn't
    os.makedirs(transcriptions_dir, exist_ok=True)

    # Define the path for the transcript file based on the video ID
    transcript_file_path = os.path.join(transcriptions_dir, f"{video_id}_transcript.txt")

    # Check if a transcript already exists for this video ID
    if os.path.exists(transcript_file_path):
        # If it exists, open and read the transcript file
        with open(transcript_file_path, 'r', encoding='utf-8') as transcript_file:
            transcript = transcript_file.read()
        # Load the transcript as a dictionary
        transcript_dict = json.loads(transcript)
    else:
        # Load the audio file from the specified path
        song = AudioSegment.from_file(path)
        # Set the time limit to five minutes, expressed in milliseconds
        five_minutes = 5 * 60 * 1000  
        
        # If the audio is longer than five minutes, trim it to five minutes
        if len(song) > five_minutes:
            song = song[:five_minutes]  

        # Path where the part of the audio to be transcribed is temporarily saved
        audio_part_file_path = os.path.join(transcriptions_dir, f"{video_id}_part0.mp3")
        # Export the first five minutes of audio to an MP3 file
        song.export(audio_part_file_path, format="mp3")
        
        # Initialize variables for storing the full transcript and language
        full_transcript_text = ""
        full_transcript_language = None
        
        # Open the exported audio file for reading
        with open(audio_part_file_path, "rb") as audio_file:
            # Create a transcription of the audio file using the 'whisper' model
            transcription_obj = client.audio.transcriptions.create(
                model="whisper", 
                file=audio_file,
                response_format="verbose_json"
            )
        # Remove the temporary audio file after transcription
        os.remove(audio_part_file_path)  
        
        # Append the text from the transcription object to the full transcript
        full_transcript_text += transcription_obj.text
        # Set the language from the transcription object
        full_transcript_language = transcription_obj.language
    
        # Create a dictionary to store the transcript and its language
        transcript_dict = {
            "text": full_transcript_text,
            "language": full_transcript_language
        }
        
        # Write the full transcript dictionary to the transcript file
        with open(transcript_file_path, 'w', encoding='utf-8') as transcript_file:
            json.dump(transcript_dict, transcript_file, ensure_ascii=False, indent=4)

    # Return the transcript dictionary
    return transcript_dict






















def get_transcription_frm_audio_v3(path,lang):
    audio_file= open(path, "rb")
    language=""
    transcript = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file,
    response_format="text",
    language=lang
    )
    return transcript


def convert_audio(dir_path, file):
    #get the file name
    file_name = file.split(".")[0]
    file_path = os.path.join(dir_path, file)
    sound = AudioSegment.from_file(file_path)
    sound = sound.set_channels(1)
    sound = sound.set_frame_rate(16000)
    sound.export("output_data/audio_files_wav/"+file_name+".wav", format="wav")


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
            return True, result.text
        elif result.reason == azure_speech.ResultReason.NoMatch:
            return (result.no_match_details)
        elif result.reason == azure_speech.ResultReason.Canceled:
            return False, "Speech recognition was canceled."
        else:
            return False, "An unknown error occurred."

    except Exception as e:
        return False, e




# convert_audio("/home/ubuntu/Desktop/Kissan_AI/youtube_kb_pipeline/youtube-kb-pipeline/output_data/audio_files","T9EMbm38NOg.mp3")
# print(azure_speech_to_text("output_data/audio_files_wav/T9EMbm38NOg.wav", "hi-IN"))

# print(get_transcription_frm_audio_v3("audio_files/sJ99Hb03UgY/sJ99Hb03UgY.mp3",'te'))
    

# # object=get_transcription_frm_audio_v2("audio_files/8-Ymdc6EdKw/8-Ymdc6EdKw.mp3")
# # transcription_object = object
# # # print(parse_whisper_transcription(output))
# # print(f"Text: {transcription_object.text}")
# # print(f"Language: {transcription_object.language}")
# # print(f"Duration: {transcription_object.duration} seconds")
# # for segment in transcription_object.segments:
# #     print(f"Segment ID: {segment['id']}")
# #     print(f"Start Time: {segment['start']} seconds")
# #     print(f"End Time: {segment['end']} seconds")
# #     print(f"Segment Text: {segment['text']}")












##MICROSOFT MODULES 


# speech_key, service_region = os.getenv("AZURE_SPEECH_SUBSCRIPTION_KEY"), os.getenv("AZURE_SPEECH_REGION")



# def recognize_from_file(audio_file_path):
#     speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
#     speech_config.speech_recognition_language="en-US"

#     audio_input = speechsdk.AudioConfig(filename=audio_file_path)
#     speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)
#     result = speech_recognizer.start_continuous_recognition_async()
#     speech_recognizer.stop_continuous_recognition_async()
    
#     if result.reason == speechsdk.ResultReason.RecognizedSpeech:
#         print("Recognized: {}".format(result.text))
#     elif result.reason == speechsdk.ResultReason.NoMatch:
#         print("No speech could be recognized: {}".format(result.no_match_details))
#     elif result.reason == speechsdk.ResultReason.Canceled:
#         cancellation_details = result.cancellation_details
#         print("Speech Recognition canceled: {}".format(cancellation_details.reason))
#         if cancellation_details.reason == speechsdk.CancellationReason.Error:
#             print("Error details: {}".format(cancellation_details.error_details))



# def recognize_from_microphone():
#     # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
#     speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    
#     speech_config.speech_recognition_language="en-US"

#     audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
#     speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

#     print("Speak into your microphone.")
#     speech_recognition_result = speech_recognizer.recognize_once_async().get()

#     if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
#         print("Recognized: {}".format(speech_recognition_result.text))
#     elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
#         print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
#     elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
#         cancellation_details = speech_recognition_result.cancellation_details
#         print("Speech Recognition canceled: {}".format(cancellation_details.reason))
#         if cancellation_details.reason == speechsdk.CancellationReason.Error:
#             print("Error details: {}".format(cancellation_details.error_details))
#             print("Did you set the speech resource key and region values?")

# recognize_from_microphone()
# recognize_from_file(audio_file_path='wav_audio/CsFbTrzZQNo.wav')
# downloaded_file = download_and_save_audio_youtube('https://www.youtube.com/watch?v=8-Ymdc6EdKw&t=4s')

# object=get_transcription_frm_audio_v2("audio_files/8-Ymdc6EdKw/8-Ymdc6EdKw.mp3")
# transcription_object = object
# # print(parse_whisper_transcription(output))
# print(f"Text: {transcription_object.text}")
# print(f"Language: {transcription_object.language}")
# print(f"Duration: {transcription_object.duration} seconds")
# for segment in transcription_object.segments:
#     print(f"Segment ID: {segment['id']}")
#     print(f"Start Time: {segment['start']} seconds")
#     print(f"End Time: {segment['end']} seconds")
#     print(f"Segment Text: {segment['text']}")
