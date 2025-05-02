import pandas as pd
import hashlib

def generate_numeric_ids(input_path, output_path, column_name='ID'):
    """
    Converts string values in the specified column to unique numeric identifiers
    and saves the result to a new file.
    
    :param input_path: Path to the input Excel or CSV file
    :param output_path: Path to the output Excel file
    :param column_name: Name of the column containing string IDs
    """
    # Load the file (supports .xlsx and .csv)
    if input_path.endswith('.csv'):
        df = pd.read_csv(input_path)
    else:
        df = pd.read_excel(input_path)

    # Hash function to convert string to a numeric ID
    def string_to_int_hash(value):
        return int(hashlib.md5(str(value).encode()).hexdigest()[:8], 16)

    # Apply hashing to the specified column
    df[f'{column_name}_numeric'] = df[column_name].apply(string_to_int_hash)

    # Save the result
    df.to_excel(output_path, index=False)
    print(f"File saved: {output_path}")
