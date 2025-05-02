# filter_empty_rows.py

import csv

def filter_rows_by_column(input_file: str, output_file: str, column_name: str) -> None:
    """
    Filters out rows where the specified column is empty or whitespace-only,
    and writes the cleaned data to a new CSV file (can be the same as input).

    :param input_file: Path to the input CSV file
    :param output_file: Path to save the filtered CSV file
    :param column_name: Name of the column to check for non-empty values
    """
    # Read the input file
    with open(input_file, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = [row for row in reader if row.get(column_name, '').strip() != '']

    if not rows:
        print("No valid rows found. Output file will not be created.")
        return

    # Write filtered rows to output file
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done! Filtered file saved as {output_file}")




