# main.py

# from utils.scrape_yad2 import scrape_yad2_pages
# from utils.merge_csv_files import merge_csv_files
# from utils.filter_empty_rows import filter_rows_by_column
# from utils.extract_features_from_tags import extract_features_from_excel
from utils import scrape_yad2_pages, merge_csv_files , filter_rows_by_column, extract_features_from_excel,generate_numeric_ids


def main():
    # 1. Scrape listings from yad2
    # scrape_yad2_pages(
    #     start_page=1,
    #     end_page=2,
    #     output_folder="/Users/margotiamanova/Desktop/DI-FinalProject/results/raw_results",
    #     output_filename="yad2_listings6.csv"
    # )

    # # 2. Merge all raw CSVs
    # merge_csv_files(
    #     folder_path="/Users/margotiamanova/Desktop/DI-FinalProject/results/raw_results",
    #     output_path="/Users/margotiamanova/Desktop/DI-FinalProject/results/merged_results/merged6.csv"
    # )

    # # 3. Filter rows by 'Link' column
    # filter_rows_by_column(
    #     input_file="/Users/margotiamanova/Desktop/DI-FinalProject/results/merged_results/merged6.csv",
    #     output_file="/Users/margotiamanova/Desktop/DI-FinalProject/results/merged_results/merged6_filt.csv",
    #     target_column="Link"
    # )

    # # 4. Extract feature columns from Tags
    # extract_features_from_tags(
    #     input_path="/Users/margotiamanova/Desktop/DI-FinalProject/results/merged_results/merged6_filt.csv",
    #     output_path="/Users/margotiamanova/Desktop/DI-FinalProject/results/merged_results/merged6_filt_features.csv"
    # )
    generate_numeric_ids(
    input_path="/Users/margotiamanova/Desktop/DI-FinalProject/output_with_features2_translated_without_dubl.xlsx",
    output_path="/Users/margotiamanova/Desktop/DI-FinalProject/output_with_features2_translated_without_dubl_ID.xlsx",
    column_name="ID"
    )


    # print("✅ All steps completed successfully.")

if __name__ == "__main__":
    main()
