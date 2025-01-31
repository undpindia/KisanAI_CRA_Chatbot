from pydub import AudioSegment
from io import BytesIO
from fastapi import HTTPException
from whatsapp_bot.app.logs.logger import logger

def convert_ogg_to_wav(ogg_content, output_file):
    """
    Converts OGG audio data to WAV format and saves it to the specified output file.

    Parameters:
    - ogg_content (bytes): The binary content of the OGG audio file.
    - output_file (str): The path to save the resulting WAV file.

    Raises:
    - HTTPException: If an error occurs during the conversion process, an internal server error
      is raised with a 500 status code, and the details of the error are provided.
    """

    try:
        sound = AudioSegment.from_file(BytesIO(ogg_content), format="ogg")

        # Export the WAV file
        sound.export(output_file, format="wav")

        logger.info(f"Conversion successful. WAV file saved as: {output_file}")

    except Exception as e:
        logger.error(f"Error processing ogg to wav: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

def convert_ogg_to_mp3(ogg_content, output_file):
    """
    Converts OGG audio data to MP3 format and saves it to the specified output file.

    Parameters:
    - ogg_content (bytes): The binary content of the OGG audio file.
    - output_file (str): The path to save the resulting MP3 file.

    Raises:
    - HTTPException: If an error occurs during the conversion process, an internal server error
      is raised with a 500 status code, and the details of the error are provided.
    """

    try:
        sound = AudioSegment.from_file(BytesIO(ogg_content), format="ogg")

        # Export the MP3 file
        sound.export(output_file, format="mp3")

        logger.info(f"Conversion successful. MP3 file saved as: {output_file}")

    except Exception as e:
        logger.error(f"Error processing ogg to mp3: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")