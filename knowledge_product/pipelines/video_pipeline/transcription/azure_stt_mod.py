# """
# Copyright (C) 2023 Titodi Infotech - All Rights Reserved
# Author: Pratik Desai
# """
import azure.cognitiveservices.speech as speechsdk
import time

from pydub import AudioSegment
import os
import time ,collections
import json

# speech_key, service_region = azure_speech_service_key, "centralindia"
# def convert_audio(dir_path, file):
#     #get the file name
#     file_name = file.split(".")[0]
#     file_path = os.path.join(dir_path, file)
#     sound = AudioSegment.from_file(file_path)
#     sound = sound.set_channels(1)
#     sound = sound.set_frame_rate(16000)
#     sound.export(file_name+".wav", format="wav")


# def transcribe_audio(speech_config, audio_filename):
#     audio_input = speechsdk.audio.AudioConfig(filename=audio_filename)
#     # speech_config.set_property(property_id=speechsdk.PropertyId.SpeechServiceResponse_StablePartialResultThreshold, value=5)
#     speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input, language="en-US")

#     done = False

#     def stop_cb(evt):
#         print('CLOSING on {}'.format(evt))
#         speech_recognizer.stop_continuous_recognition()
#         nonlocal done
#         done = True

#     all_results = []
#     def handle_final_result(evt):
#         all_results.append(evt.result)

#     speech_recognizer.recognized.connect(handle_final_result)
#     speech_recognizer.session_stopped.connect(stop_cb)
#     speech_recognizer.canceled.connect(stop_cb)

#     speech_recognizer.start_continuous_recognition()
#     while not done:
#         time.sleep(0)

#     return all_results


# speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)


# print(transcribe_audio(speech_config,"CsFbTrzZQNo.wav"))





# def transcriptions_to_srt(transcriptions, srt_filename="transcription.srt"):
#     srt_format = ""
#     for i, transcription in enumerate(transcriptions):
#         print(transcription)
#         print(transcription.offset)
#         print(transcription.duration)
#         start_time = time.strftime('%H:%M:%S', time.gmtime(transcription.offset/10000000))
#         end_time = time.strftime('%H:%M:%S', time.gmtime((transcription.offset + transcription.duration)/10000000))

#         srt_format += f"{i+1}\n"
#         srt_format += f"{start_time} --> {end_time}\n"
#         srt_format += f"{transcription.text}\n\n"

#     with open(srt_filename, "w") as file:
#         file.write(srt_format)


# def run_on_dir(speech_config, dir_path):
#     files = os.listdir(dir_path)
#     for file in files:
#         file_name = file.split(".")[0]
#         convert_audio(dir_path, file)
#         transcriptions = transcribe_audio(speech_config, file_name+".wav")
#         print(transcriptions)
#         transcriptions_to_srt(transcriptions,file_name+".srt")




# def speech_recognize_once_from_file():
#     """performs one-shot speech recognition with input from an audio file"""
#     # <SpeechRecognitionWithFile>
#     speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
#     audio_config = speechsdk.audio.AudioConfig(filename="wav_audio/CsFbTrzZQNo.wav")
#     # Creates a speech recognizer using a file as audio input, also specify the speech language
#     speech_recognizer = speechsdk.SpeechRecognizer(
#         speech_config=speech_config, language="en-US", audio_config=audio_config)

#     # Starts speech recognition, and returns after a single utterance is recognized. The end of a
#     # single utterance is determined by listening for silence at the end or until a maximum of 15
#     # seconds of audio is processed. It returns the recognition text as result.
#     # Note: Since recognize_once() returns only a single utterance, it is suitable only for single
#     # shot recognition like command or query.
#     # For long-running multi-utterance recognition, use start_continuous_recognition() instead.
#     result = speech_recognizer.recognize_once()

#     # Check the result
#     if result.reason == speechsdk.ResultReason.RecognizedSpeech:
#         print("Recognized: {}".format(result.text))
#     elif result.reason == speechsdk.ResultReason.NoMatch:
#         print("No speech could be recognized: {}".format(result.no_match_details))
#     elif result.reason == speechsdk.ResultReason.Canceled:
#         cancellation_details = result.cancellation_details
#         print("Speech Recognition canceled: {}".format(cancellation_details.reason))
#         if cancellation_details.reason == speechsdk.CancellationReason.Error:
#             print("Error details: {}".format(cancellation_details.error_details))


# def speech_language_detection_once_from_file():
#     """performs one-shot speech language detection with input from an audio file"""
#     # <SpeechLanguageDetectionWithFile>
#     # Creates an AutoDetectSourceLanguageConfig, which defines a number of possible spoken languages
#     auto_detect_source_language_config = \
#         speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-US","hi-IN","bn-IN","mr-IN"])

#     # Creates a SpeechConfig from your speech key and region
#     speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

#     # Creates an AudioConfig from a given WAV file
#     audio_config = speechsdk.audio.AudioConfig(filename="wav_audio/CsFbTrzZQNo.wav")

#     # Creates a source language recognizer using a file as audio input, also specify the speech language
#     source_language_recognizer = speechsdk.SourceLanguageRecognizer(
#         speech_config=speech_config,
#         auto_detect_source_language_config=auto_detect_source_language_config,
#         audio_config=audio_config)

#     # Starts speech language detection, and returns after a single utterance is recognized. The end of a
#     # single utterance is determined by listening for silence at the end or until a maximum of 15
#     # seconds of audio is processed. It returns the detection text as result.
#     # Note: Since recognize_once() returns only a single utterance, it is suitable only for single
#     # shot detection like command or query.
#     # For long-running multi-utterance detection, use start_continuous_recognition() instead.
#     result = source_language_recognizer.recognize_once()

#     # Check the result
#     if result.reason == speechsdk.ResultReason.RecognizedSpeech:
#         detected_src_lang = result.properties[
#             speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult]
#         print("Detected Language: {}".format(detected_src_lang))
#     elif result.reason == speechsdk.ResultReason.NoMatch:
#         print("No speech could be recognized: {}".format(result.no_match_details))
#     elif result.reason == speechsdk.ResultReason.Canceled:
#         cancellation_details = result.cancellation_details
#         print("Speech Language Detection canceled: {}".format(cancellation_details.reason))
#         if cancellation_details.reason == speechsdk.CancellationReason.Error:
#             print("Error details: {}".format(cancellation_details.error_details))
#     # </SpeechLanguageDetectionWithFile>
            
# def speech_language_detection_once_from_continuous():
#     """performs continuous speech language detection with input from an audio file"""
#     # <SpeechContinuousLanguageDetectionWithFile>
#     # Creates an AutoDetectSourceLanguageConfig, which defines a number of possible spoken languages
#     auto_detect_source_language_config = \
#         speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-US","hi-IN","te-IN","bn-IN"])

#     # Creates a SpeechConfig from your speech key and region
#     speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

#     # Set continuous language detection (override the default of "AtStart")
#     speech_config.set_property(
#         property_id=speechsdk.PropertyId.SpeechServiceConnection_LanguageIdMode, value='Continuous')

#     audio_config = speechsdk.audio.AudioConfig(filename="wav_audio/CsFbTrzZQNo.wav")

#     source_language_recognizer = speechsdk.SourceLanguageRecognizer(
#         speech_config=speech_config,
#         auto_detect_source_language_config=auto_detect_source_language_config,
#         audio_config=audio_config)

#     done = False

#     def stop_cb(evt: speechsdk.SessionEventArgs):
#         """callback that signals to stop continuous recognition upon receiving an event `evt`"""
#         print('CLOSING on {}'.format(evt))
#         nonlocal done
#         done = True

#     def audio_recognized(evt: speechsdk.SpeechRecognitionEventArgs):
#         """
#         callback that catches the recognized result of audio from an event 'evt'.
#         :param evt: event listened to catch recognition result.
#         :return:
#         """
#         if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
#             if evt.result.properties.get(
#                     speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult) is None:
#                 print("Unable to detect any language")
#             else:
#                 detected_src_lang = evt.result.properties[
#                     speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult]
#                 json_result = evt.result.properties[speechsdk.PropertyId.SpeechServiceResponse_JsonResult]
#                 detail_result = json.loads(json_result)
#                 start_offset = detail_result['Offset']
#                 duration = detail_result['Duration']
#                 if duration >= 0:
#                     end_offset = duration + start_offset
#                 else:
#                     end_offset = 0
#                 print("Detected language = " + detected_src_lang)
#                 print(f"Start offset = {start_offset}, End offset = {end_offset}, "
#                       f"Duration = {duration} (in units of hundreds of nanoseconds (HNS))")
#                 global language_detected
#                 language_detected = True

#     # Connect callbacks to the events fired by the speech recognizer
#     source_language_recognizer.recognized.connect(audio_recognized)
#     source_language_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
#     source_language_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
#     source_language_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
#     # stop continuous recognition on either session stopped or canceled events
#     source_language_recognizer.session_stopped.connect(stop_cb)
#     source_language_recognizer.canceled.connect(stop_cb)

#     # Start continuous speech recognition
#     source_language_recognizer.start_continuous_recognition()
#     while not done:
#         time.sleep(.5)

#     source_language_recognizer.stop_continuous_recognition()

# def speech_language_detection_first_60_seconds():
#     """performs speech language detection for the first 60 seconds of the file"""

#     # Creates an AutoDetectSourceLanguageConfig, which defines a number of possible spoken languages
#     auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
#         languages=["en-US", "hi-IN", "te-IN", "bn-IN"])

#     # Creates a SpeechConfig from your speech key and region
#     speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

#     # Set continuous language detection (override the default of "AtStart")
#     speech_config.set_property(
#         property_id=speechsdk.PropertyId.SpeechServiceConnection_LanguageIdMode, value='Continuous')

#     audio_config = speechsdk.audio.AudioConfig(filename="wav_audio/CsFbTrzZQNo.wav")

#     source_language_recognizer = speechsdk.SourceLanguageRecognizer(
#         speech_config=speech_config,
#         auto_detect_source_language_config=auto_detect_source_language_config,
#         audio_config=audio_config)

#     done = False
#     detected_languages = []

#     def stop_cb(evt: speechsdk.SessionEventArgs):
#         """callback that signals to stop continuous recognition upon receiving an event `evt`"""
#         print('CLOSING on {}'.format(evt))
#         nonlocal done
#         done = True

#     def audio_recognized(evt: speechsdk.SpeechRecognitionEventArgs):
#         """
#         callback that catches the recognized result of audio from an event 'evt'.
#         :param evt: event listened to catch recognition result.
#         :return:
#         """
#         if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
#             if evt.result.properties.get(
#                     speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult) is None:
#                 print("Unable to detect any language")
#             else:
#                 detected_src_lang = evt.result.properties[
#                     speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult]
#                 json_result = evt.result.properties[speechsdk.PropertyId.SpeechServiceResponse_JsonResult]
#                 detail_result = json.loads(json_result)
#                 start_offset = detail_result['Offset']
#                 duration = detail_result['Duration']

#                 # Store detected language only within the first 60 seconds
#                 if start_offset <= 60 * 1e7:  # 60 seconds in units of hundreds of nanoseconds (HNS)
#                     detected_languages.append(detected_src_lang)

#                 if duration >= 0:
#                     end_offset = duration + start_offset
#                 else:
#                     end_offset = 0
#                 print("Detected language = " + detected_src_lang)
#                 print(f"Start offset = {start_offset}, End offset = {end_offset}, "
#                       f"Duration = {duration} (in units of hundreds of nanoseconds (HNS))")

#     # Connect callbacks to the events fired by the speech recognizer
#     source_language_recognizer.recognized.connect(audio_recognized)
#     source_language_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
#     source_language_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
#     source_language_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
#     # stop continuous recognition on either session stopped or canceled events
#     source_language_recognizer.session_stopped.connect(stop_cb)
#     source_language_recognizer.canceled.connect(stop_cb)

#     # Start continuous speech recognition
#     source_language_recognizer.start_continuous_recognition()
#     while not done:
#         time.sleep(.5)

#     source_language_recognizer.stop_continuous_recognition()

#     return detected_languages




import time



# def speech_language_detection_once_from_continuous_60_seconds():
#     """performs continuous speech language detection for 60 seconds"""
#     auto_detect_source_language_config = \
#         speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["mr-IN","hi-IN","te-IN","bn-IN"])

#     # Creates a SpeechConfig from your speech key and region
#     speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

#     # Set continuous language detection (override the default of "AtStart")
#     speech_config.set_property(
#         property_id=speechsdk.PropertyId.SpeechServiceConnection_LanguageIdMode, value='Continuous')

#     audio_config = speechsdk.audio.AudioConfig(filename="wav_audio/CsFbTrzZQNo.wav")

#     source_language_recognizer = speechsdk.SourceLanguageRecognizer(
#         speech_config=speech_config,
#         auto_detect_source_language_config=auto_detect_source_language_config,
#         audio_config=audio_config)

#     done = False

#     def stop_cb(evt: speechsdk.SessionEventArgs):
#         """callback that signals to stop continuous recognition upon receiving an event `evt`"""
#         # print('CLOSING on {}'.format(evt))
#         nonlocal done
#         done = True
#     detected_languages = []
#     # existing code to set up config and recognizer
    
#     start_time = time.time()
    
#     def audio_recognized(evt):
#         """callback to handle recognition events"""
#         if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
#             detected_lang = evt.result.properties[speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult]
#             detected_languages.append(detected_lang)
            
#     # Connect callbacks
#     source_language_recognizer.recognized.connect(audio_recognized)
#     source_language_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
#     source_language_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
#     source_language_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
#     # Start continuous recognition
#     source_language_recognizer.start_continuous_recognition()
    
#     while time.time() - start_time < 60: 
#         time.sleep(.5)
        
#     source_language_recognizer.stop_continuous_recognition()
#     language_counts = collections.Counter(detected_languages)
#     total_detections = len(detected_languages)
#     language_percentages = {lang: count / total_detections * 100 for lang, count in language_counts.items()}

#     dominant_language = language_counts.most_common(1)[0][0]

#     return dominant_language, language_percentages



# speech_language_detection_once_from_file()
# speech_language_detection_once_from_continuous()
print(speech_language_detection_once_from_continuous_60_seconds())
# languages=["en-US","hi-IN","mr-IN","ta-IN","te-IN","gu-IN","kn-IN","bn-IN","ml-IN"]