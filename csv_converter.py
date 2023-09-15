import os
import pandas as pd
import datetime
import json

# Get today's date in the desired format
today_date = datetime.datetime.now().strftime("%d-%m-%Y")

# Create a folder for CSV files with today's date
output_folder = "13-09-2023" + "_Csv"

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# List all files in the folder with today's date
input_folder =  "13-09-2023"

if not os.path.exists(input_folder):
    print("Folder not found.")
    exit()

json_files = [f for f in os.listdir(input_folder) if f.endswith('.json')]

# Initialize a list to store DataFrames
dfs = []

# Process each JSON file and read it into a DataFrame
for json_file in json_files:
    with open(os.path.join(input_folder, json_file), 'r') as json_file:
        data = json.load(json_file)

    # Convert JSON to DataFrame and append to the list
    df = pd.json_normalize(data, sep='_')
    dfs.append(df)

# Concatenate all DataFrames into one
merged_df = pd.concat(dfs, ignore_index=True)

# Define the CSV file path
csv_file_path = os.path.join(output_folder, 'merged_data.csv')

# Write the DataFrame to a CSV file
merged_df.to_csv(csv_file_path, index=False)

print(f"Converted {len(json_files)} JSON file(s) to CSV format in file '{csv_file_path}'.")
