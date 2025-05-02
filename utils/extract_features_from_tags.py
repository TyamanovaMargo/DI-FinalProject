# extract_features_from_tags.py

import pandas as pd

def extract_features_from_excel(input_path: str, output_path: str) -> None:
    """
    Loads an Excel file, extracts binary features from Tags1–Tags3 columns,
    and saves the result to a CSV file.

    :param input_path: Path to the input .xls or .xlsx file
    :param output_path: Path to the output .csv file
    """
    # List of features to extract
    features = [
        "3 bathrooms", "Security room", "2 balconies", "Unique", "After urban renewal",
        "Renovated building", "3 balconies", "Large kitchen", "Parking", "3 air directions",
        "4 bathrooms", "Close to park", "Close to the sea", "Open city view", "4 air directions",
        "Open sea view", "4 balconies", "Flexible price", "New property", "Master suite",
        "First line to the sea", "Open park view", "Received urban renewal permit",
        "Worth seeing / Don’t miss out", "Rear-facing property", "New from the contractor",
        "Architecturally renovated", "Bargain opportunity / Special opportunity", "recommended"
    ]

    # Load the Excel file
    df = pd.read_excel(input_path)

    # Combine tag columns into one string column
    df["all_tags"] = df[["Tags1", "Tags2", "Tags3"]].astype(str).agg(" | ".join, axis=1)

    # Create binary columns for each feature
    for feature in features:
        df[feature] = df["all_tags"].apply(lambda x: 1 if feature in x else 0)

    # Remove the helper column
    df.drop(columns=["all_tags"], inplace=True)

    # Save the final dataframe to CSV
    df.to_csv(output_path, index=False, encoding='utf-8-sig')


