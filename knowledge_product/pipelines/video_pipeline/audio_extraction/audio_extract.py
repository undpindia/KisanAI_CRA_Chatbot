from pydub import AudioSegment
from pytube import YouTube
import os
import youtube_dl


def get_video_id(url):
    yt = YouTube(url)
    video_id = yt.video_id
    return video_id


# def download_and_save_audio_youtube(url):
#     # Download YouTube video with only audio stream
#     yt = YouTube(url,
#         use_oauth=True,
#         allow_oauth_cache=True)
#     video_id = yt.video_id
#     audio_stream = yt.streams.filter(only_audio=True).first()
    
#     # Create destination path for audio files
#     destination_path = f"output_data/audio_files/"
#     os.makedirs(destination_path, exist_ok=True)

#     # Download audio and save in temporary location
#     temp_path = "temp_audio"
#     audio_file_path = audio_stream.download(output_path=temp_path)

  
#     audio = AudioSegment.from_file(audio_file_path)
#     # wav_file_path = os.path.join(destination_path, f"{video_id}.wav")
#     # audio.export(wav_file_path, format='wav')

#     # Convert to MP3 using pydub
#     mp3_file_path = os.path.join(destination_path, f"{video_id}.mp3")
#     audio.export(mp3_file_path, format='mp3')

#     # Optional: Remove the original downloaded file
#     os.remove(audio_file_path)

#     # Print and return the name of the saved file
#     print(f"Audio file saved as: {video_id}.mp3")
#     info_dict={'vedio_id':video_id ,'filename':f"{video_id}.mp3"}
#     return f"{video_id}.mp3"

import yt_dlp

def download_and_save_audio_youtube(youtube_url, destination_path="output_data/audio_files/"):
    # Ensure the destination directory exists
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        # The outtmpl option is updated to save the file in the given destination_path with the video_id as the name
        'outtmpl': destination_path + '%(id)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extract information about the video to use the video ID in the filename
        info_dict = ydl.extract_info(youtube_url, download=False)
        video_id = info_dict.get('id', None)
        
        # If video_id is extracted, proceed to download
        if video_id:
            ydl.download([youtube_url])
            # Return the full path to the downloaded audio file
            return os.path.join(f"{video_id}.mp3")
        else:
            raise Exception("Could not extract video ID from the URL.")


def delete_audio_file(audio_file_name, destination_path="output_data/audio_files/"):
    # Construct the full path to the audio file
    file_path = os.path.join(destination_path, audio_file_name)

    # Check if the file exists
    if os.path.exists(file_path):
        # Delete the file
        os.remove(file_path)
        print(f"Deleted audio file: {file_path}")
    else:
        # If the file does not exist, raise an error
        print(f"Audio file not found: {file_path}")

def video_metadata_audio_file(youtube_url, destination_path="output_data/audio_files/"):
    # Ensure the destination directory exists
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': destination_path + '%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,  # Suppresses most output
        'no_warnings': True,  # Suppresses warnings
    }

    # Initialize an empty dictionary to hold the video information
    video_info = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extract information about the video without downloading
        info_dict = ydl.extract_info(youtube_url, download=False)
        video_id = info_dict.get('id', None)
        video_title = info_dict.get('title', None)
        channel_name = info_dict.get('uploader', None)
        video_description = info_dict.get('description', None)
        video_duration = info_dict.get('duration', None)  # Extracting video duration
        audio_file_path = os.path.join(destination_path, f"{video_id}.mp3")

        # Check if the audio file already exists
        if not os.path.isfile(audio_file_path):
            # If the audio file does not exist, download it
            ydl.download([youtube_url])

        # Populate the video information dictionary
        video_info = {
            'video_id': video_id,
            'video_title': video_title,
            'channel_name': channel_name,
            'video_description': video_description,
            'video_duration': video_duration,  # Including video duration in the dictionary
            'audio_file_path': audio_file_path
        }
    
    return video_info



# def video_metadata_audio_file(youtube_url, destination_path="output_data/audio_files/"):
    # Ensure the destination directory exists
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': destination_path + '%(id)s.%(ext)s',
        'noplaylist': True
    }

    # Initialize an empty dictionary to hold the video information
    video_info = {}
    # filename=f"{video_id}.mp3"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extract information about the video without downloading
        info_dict = ydl.extract_info(youtube_url, download=False)
        video_id = info_dict.get('id', None)
        video_title = info_dict.get('title', None)
        channel_name = info_dict.get('uploader', None)
        video_description = info_dict.get('description', None)
        video_duration = info_dict.get('duration', None)  # Extracting video duration
        audio_file_path = os.path.join(destination_path, f"{video_id}.mp3")

        # Check if the audio file already exists
        if not os.path.isfile(audio_file_path):
            # If the audio file does not exist, download it
            ydl.download([youtube_url])

        # Populate the video information dictionary
        video_info = {
            'video_id': video_id,
            'video_title': video_title,
            'channel_name': channel_name,
            'video_description': video_description,
            'video_duration': video_duration,  # Including video duration in the dictionary
            'audio_file_path': audio_file_path
        }
    
    return video_info
# Call the function with the YouTube URL
# print(download_and_save_audio_youtube("https://www.youtube.com/watch?v=DDYT6BPY4oM"))