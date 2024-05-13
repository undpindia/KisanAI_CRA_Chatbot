"""
Copyright (C) 2023 Titodi Infotech - All Rights Reserved
Author: Pratik Desai
"""
import azure.cognitiveservices.speech as speechsdk
import time
from pydub import AudioSegment
import os


def convert_audio(dir_path, file):
    #get the file name
    file_name = file.split(".")[0]
    file_path = os.path.join(dir_path, file)
    sound = AudioSegment.from_file(file_path)
    sound = sound.set_channels(1)
    sound = sound.set_frame_rate(16000)
    sound.export("wav_audio/"+file_name+".wav", format="wav")


def transcribe_audio(speech_config, audio_filename):
    audio_input = speechsdk.audio.AudioConfig(filename=audio_filename)
    # speech_config.set_property(property_id=speechsdk.PropertyId.SpeechServiceResponse_StablePartialResultThreshold, value=5)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input, language="en-IN")

    done = False

    def stop_cb(evt):
        print('CLOSING on {}'.format(evt))
        speech_recognizer.stop_continuous_recognition()
        nonlocal done
        done = True

    all_results = []
    def handle_final_result(evt):
        all_results.append(evt.result)

    speech_recognizer.recognized.connect(handle_final_result)
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(0)

    return all_results


def transcriptions_to_srt(transcriptions, srt_filename="transcription.srt"):
    srt_format = ""
    for i, transcription in enumerate(transcriptions):
        print(transcription)
        print(transcription.offset)
        print(transcription.duration)
        start_time = time.strftime('%H:%M:%S', time.gmtime(transcription.offset/10000000))
        end_time = time.strftime('%H:%M:%S', time.gmtime((transcription.offset + transcription.duration)/10000000))

        srt_format += f"{i+1}\n"
        srt_format += f"{start_time} --> {end_time}\n"
        srt_format += f"{transcription.text}\n\n"

    with open(srt_filename, "w") as file:
        file.write(srt_format)


def run_on_dir(speech_config, dir_path):
    files = os.listdir(dir_path)
    for file in files:
        file_name = file.split(".")[0]
        convert_audio(dir_path, file)
        transcriptions = transcribe_audio(speech_config, "ouput_data/wav_audio/"+file_name+".wav")
        print(transcriptions)
        # transcriptions_to_srt(transcriptions, "data3/srt/"+file_name+".srt")

speech_key, service_region = "578a475963d64bd28391cf80fa5a7b62", "centralindia"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

run_on_dir(speech_config=speech_config,dir_path="output_data/wav_audio/CsFbTrzZQNo.wav")