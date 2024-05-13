import os
import json
import pandas as pd
import numpy as np  # Ensure numpy is imported
import openai

# Set your OpenAI API key here
openai.api_key = "<YOUR_API_KEY>"

def generate_meaningful_information(text):
    # Feel free to customize the prompt based on your requirements
    prompt = "Generate a simple but brief summary and insight for farmers related to climate resilient agriculture from District climate data:"
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo", # Using the GPT-4-turbo model
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

def main():
    
    # Base directory containing climate data folders
    base_dir = 'dicra_data'

    # Output directory for text files
    output_dir = 'dicra_insights'
    # Prepare to collect data
    data_list = []

    # Walk through each directory in the base directory
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.geojson') and 'VECTOR/DISTRICT' in root:
                # Extract climate condition from the path
                climate_condition = root.split(os.sep)[1]
                
                # Full path to the GeoJSON file
                file_path = os.path.join(root, file)
                
                # Load GeoJSON file
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Extract features
                features = data['features']
                
                # Extract data from each feature
                for feature in features:
                    properties = feature['properties']
                    district_name = properties.get('district_name', 'Unknown')
                    # Exclude 'area', 'uid', 'centroid', 'geometry details', 'District Name', and 'Climate Condition'
                    record = {key: val for key, val in properties.items() if key not in ['_geojson', 'area', 'uid', 'centroid', 'district_name', 'Climate Condition']}
                    record['Climate Condition'] = climate_condition
                    record['District Name'] = district_name
                    data_list.append(record)

    # Create DataFrame
    df = pd.DataFrame(data_list)

    # Group by 'District Name' and create a file for each district
    for district, group_df in df.groupby('District Name'):
        print(f"Generating insights for {district}")
        content = "District: {district}\nState: Jharkhand\n\n"
        for index, row in group_df.iterrows():
            filtered_data = {key: val for key, val in row.items() if key not in ['District Name', 'Climate Condition'] and pd.notna(val)}
            climate_data = ', '.join([f"{key}: {val}" for key, val in filtered_data.items() if not pd.isna(val)])
            if climate_data:
                content += f"{row['Climate Condition']}: {climate_data}\n"
        generated_content = generate_meaningful_information(content)
        
        # Save the generated content to a new text file
        insight_filename = f"{district}.txt"
        generated_file_path = os.path.join(output_dir, insight_filename)
        with open(generated_file_path, 'w') as new_file:
            new_file.write(generated_content)
        
if __name__ == "__main__":
    main()