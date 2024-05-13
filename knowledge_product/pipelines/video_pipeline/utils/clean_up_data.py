import os
import shutil
import pandas as pd

# Data Cleanup Script
# This Python script is designed to perform two main tasks: (1) Delete all files and directories within specified paths, 
# and (2) Clean data from specified Excel files. It is intended for use in environments where periodic cleanup of directories 
# and resetting of data files is necessary, such as in development or testing environments.

# IMPORTS:
# os: Used for interacting with the operating system to perform tasks like listing and deleting files and directories.
# shutil: Used for file and directory operations, specifically for deleting directories.
# pandas: A powerful data manipulation library used here to read from and write to Excel files.

# VARIABLES:
# paths_to_clean: A list containing string paths to directories that the user wants to clean. New paths can be added to this list as needed.
# excel_files_to_clean: A list containing string paths to Excel files that the user wants to clean by removing all their content.

# FUNCTIONS:
# delete_files_and_folders(paths): Takes a list of paths and iterates through each path. For each path, it checks every item within the directory.
# If the item is a file, it deletes it using os.unlink(). If the item is a directory, it recursively deletes it using shutil.rmtree().
# This function ensures that all files and subdirectories within the specified paths are completely removed.

# clean_excel_files(files): Takes a list of Excel file paths. For each file, it opens the file using pandas, clears all data by reducing the DataFrame
# to zero rows, and then saves the empty DataFrame back to the Excel file. This function effectively "resets" the Excel files by removing all content
# while keeping the file itself and its structure intact.

# SCRIPT EXECUTION:
# The script calls delete_files_and_folders with the paths_to_clean to clear out the specified directories.
# It then calls clean_excel_files with the excel_files_to_clean to reset the data in the specified Excel files.
# Finally, it prints "Data cleanup completed." to indicate that the operations have finished.

# USAGE:
# To use this script, modify the paths_to_clean and excel_files_to_clean lists to reflect the actual directories and files you need to clean.
# Ensure that you have proper backups and permissions before running this script, as the operations performed are destructive and irreversible.

import os
import shutil
import pandas as pd

# List of directory paths to clean
paths_to_clean = [
    'data/output_data/audio_files',
    'data/output_data/audio_files_wav',
    'data/output_data/transcriptions',
    'data/output_data/translations'
    # Add more paths as needed
]

# List of Excel files to clean
excel_files_to_clean = [
    'data/output_data/video_links_list_results.xlsx'
    # Add more Excel file paths as needed
]

# List of CSV files to clean
csv_files_to_clean = [
    'data/input_data/video_links_list.csv'
    # Add more CSV file paths as needed
]

# Function to delete all files and folders within the specified paths
def delete_files_and_folders(paths):
    for path in paths:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

# Function to clean data from multiple Excel files
def clean_excel_files(files):
    for file_path in files:
        df = pd.read_excel(file_path)
        df = df.iloc[0:0]
        df.to_excel(file_path, index=False)

# Function to clean data from multiple CSV files
def clean_csv_files(files):
    for file_path in files:
        df = pd.read_csv(file_path)
        df = df.iloc[0:0]
        df.to_csv(file_path, index=False)

# Call the functions to delete files and clean the Excel and CSV files
delete_files_and_folders(paths_to_clean)
clean_excel_files(excel_files_to_clean)
clean_csv_files(csv_files_to_clean)

print("Data cleanup completed.")
