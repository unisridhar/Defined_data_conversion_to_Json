import pandas as pd
import os
import glob
import json
import regex as re
def clean_text(text):
    # Remove placeholders like [n_s/], [uni/], [filler/]
    clean_text = re.sub(r'\[.*?/\]', '', text)
    return clean_text.strip()
# Define the base directory for reading Excel files
language_path = 'Rechecked-Summarization/Arabic/Defined-ai'

# Define the base directory for saving JSON files
output_base_dir = 'Processed-Summarization/Arabic/Defined-ai'

# Walk through the directory
if os.path.isdir(language_path):
    for domain_folder in os.listdir(language_path):
        domain_path = os.path.join(language_path, domain_folder)
        if os.path.isdir(domain_path):
            # Get all Excel files in the domain folder
            excel_files = glob.glob(os.path.join(domain_path, '*.xlsx'))
            for file_path in excel_files:
                # Read the Excel file into a DataFrame
                df = pd.read_excel(file_path)
                transcription_col = next((col for col in df.columns if col.lower() == 'transcription'), None)

                if transcription_col:
                    print("")
                else :
                    print(f"Not found {file_path}")

                # Define the columns of interest
                columns_of_interest = [col for col in df.columns if any(q in col for q in ["Q1", "Q2", "Q3", "Q4"])]

                # Check if all required columns are present
                if len(columns_of_interest) == 4:
                    # Create a new DataFrame with the selected columns
                    df_selected = df[columns_of_interest]

                    # Extract the answers from the first row
                    answers = df_selected.iloc[0].to_dict()
                    transcription_data = [{"speaker": "Agent" if i % 2 == 0 else "Customer", "text": clean_text(text)}
                                          for i, text in enumerate(df[transcription_col].tolist())]
                    answers['Transcription'] = transcription_data

                    # Define the output file path with the same structure but in a different base directory and with .json extension
                    relative_path = os.path.relpath(file_path, language_path)
                    json_output_path = os.path.join(output_base_dir, relative_path.replace('.xlsx', '.json'))

                    # Ensure the output directory exists
                    os.makedirs(os.path.dirname(json_output_path), exist_ok=True)

                    # Save the answers in JSON format
                    with open(json_output_path, 'w', encoding='utf-8') as json_file:
                        json.dump(answers, json_file, ensure_ascii=False, indent=4)

                    # print(f"Answers extracted and saved to {json_output_path}")
                else:
                    missing_cols = set(["Q1", "Q2", "Q3", "Q4", "Transcription"]) - set([col.split()[0] for col in columns_of_interest])
                    print(f"File {file_path} is missing columns: {missing_cols}")

print("Processing completed.")
