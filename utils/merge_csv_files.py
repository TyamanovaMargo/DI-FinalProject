# merge_csv_files.py

import pandas as pd
import glob
import os

def merge_csv_files(input_folder: str, output_file: str) -> None:
    """
    Merges all CSV files in the specified folder into one DataFrame,
    removes duplicates, and saves the result to a CSV file.

    :param input_folder: Path to the folder containing CSV files
    :param output_file: Path to save the merged CSV file
    """
    # Find all CSV files in the folder
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))

    # Read all CSV files into a list of DataFrames
    df_list = [pd.read_csv(file) for file in csv_files]

    # Concatenate into one DataFrame
    merged_df = pd.concat(df_list, ignore_index=True)

    # Drop duplicates across all columns
    merged_df.drop_duplicates(inplace=True)

    # Save the merged result
    merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"Merged {len(csv_files)} files. Final row count: {len(merged_df)}.")

