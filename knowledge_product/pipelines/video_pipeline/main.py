from audio_extraction.audio_extract import download_and_save_audio_youtube , video_metadata_audio_file
from transcription.audio_transcriptions import get_transcription_frm_audio_v2
from transcription.lang_detect import language_detection
from translation.translator import translate
from data_extraction.summarizer import get_facts, get_theme, get_keyword
import csv
from openpyxl import Workbook
import os
from preprocessing_text.preprocess import preprocess_text
from utils.error import Incorrect_lang_detect

def process_video_link(video_link):
    try:
        print(f"Processing video link: {video_link}")
        video_info = video_metadata_audio_file(video_link)
        
        video_id, audio_file_name, video_title, channel_name, video_description, video_duration = (
            video_info['video_id'],
            video_info['audio_file_path'],
            video_info['video_title'],
            video_info['channel_name'],
            video_info['video_description'],
            video_info['video_duration']
        )

        transcription_object = get_transcription_frm_audio_v2(audio_file_name, video_id)
        original_lang = transcription_object["language"]
        original_transcription = transcription_object["text"]
        

        translated_version = translate(original_transcription, original_lang, video_id)
        # print(f"Translation completed for video ID: {video_id}")

        lang_detect_result = language_detection(translated_version)
        # print(f"Language Detection completed for video ID: {video_id}")

        lang = list(lang_detect_result.keys())[0]
        if lang == 'na' or float(lang_detect_result[lang]) < 0.8:
            raise Incorrect_lang_detect(lang)

        preprocessed_version = preprocess_text(0.2, translated_version)
        facts = get_facts(preprocessed_version)
        theme = get_theme(facts)
        keywords = get_keyword(facts)
        print(f"Text processing completed for video ID: {video_id}")

        # Return the updated result row with additional fields
        return [video_link, video_id, video_title, channel_name, video_description, video_duration,
                audio_file_name, original_lang, original_transcription.encode('utf-8'), preprocessed_version,
                facts, theme, keywords]
    except Exception as e:
        print(f"Error processing video link: {video_link} - {e}")
        return None
    # finally:
    #     if audio_file_name:
    #         try:
    #             os.remove(f'output_data/audio_files/{audio_file_name}')
    #             print(f"Deleted audio file: {audio_file_name}")
    #         except OSError as e:
    #             print(f"Error deleting audio file {audio_file_name}: {e}")




def main(file_path):
    try:
        output_data_dir = "data/output_data"
        # Create the directory if it doesn't exist
        os.makedirs(output_data_dir, exist_ok=True)
        
        # Prepare the output file path to save in the output_data directory
        base_name = os.path.basename(file_path)  # Extracts the file name from the file_path
        name, extension = os.path.splitext(base_name)
        output_file_name = f"{name}_results.xlsx"
        output_file = os.path.join(output_data_dir, output_file_name)
        
        print("Output file will be generated at:", output_file)

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            workbook = Workbook()
            sheet = workbook.active
            # Update headers to include new fields
            sheet.append(['Video Link', 'Video ID', 'Video Title', 'Channel Name', 'Description', 'Video Duration',
                          'Audio File Name', 'Original Language', 'Original Transcription', 'Translated Version',
                          'Facts', 'Theme', 'Keywords'])

            # Skip the header row in the CSV, if present
            next(csvreader, None)

            processed_rows = 0
            for row in csvreader:
                try:
                    video_link = row[0]
                    result_row = process_video_link(video_link)
                    if result_row is not None:
                        processed_rows += 1
                        sheet.append(result_row)
                        print(f'Processing row {processed_rows} for {video_link} -- completed')
                    else:
                        print(f'Skipping row for {video_link} -- does not meet criteria')

                    if processed_rows % 1 == 0:
                        workbook.save(output_file)
                except Exception as e:
                    print(f'Error processing row for {video_link}: {e} -- proceeding to the next video')

            workbook.save(output_file)
            print("All rows have been processed and saved to", output_file)

    except Exception as e:
        print(f"An error occurred when opening or working with the file: {e}")

if __name__ == "__main__":
    # Replace with the path to your CSV file containing video links
    main("data/input_data/video_links_list.csv")