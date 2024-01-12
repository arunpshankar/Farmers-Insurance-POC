import pandas as pd

def load_csv(file_path: str) -> pd.DataFrame:
    """ Loads a CSV file into a DataFrame. """
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading CSV file {file_path}: {e}")
        return pd.DataFrame()

def combine_dataframes_columnwise(dfs: list) -> pd.DataFrame:
    """ Combines a list of DataFrames column-wise. """
    combined_df = pd.concat(dfs, axis=1)
    # Removing duplicate columns
    return combined_df.loc[:, ~combined_df.columns.duplicated()]

def save_to_csv(df: pd.DataFrame, file_path: str):
    """ Saves DataFrame to a CSV file. """
    try:
        df.to_csv(file_path, index=False)
        print(f"DataFrame saved as CSV at {file_path}")
    except Exception as e:
        print(f"Error saving CSV file: {e}")

def save_to_excel(df: pd.DataFrame, file_path: str):
    """ Saves DataFrame to an Excel file with wrapped text. """
    try:
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Results')
            worksheet = writer.sheets['Results']
            for idx, _ in enumerate(df):
                worksheet.set_column(idx, idx, 20, writer.book.add_format({'text_wrap': True}))
        print(f"DataFrame saved as Excel file at {file_path}")
    except Exception as e:
        print(f"Error saving Excel file: {e}")

def main():
    """ Main function to execute the script tasks. """
    # Load the CSV files
    exp_1 = load_csv('./data/results/exp_1.csv')
    exp_2 = load_csv('./data/results/exp_2.csv')
    exp_3 = load_csv('./data/results/exp_3.csv')

    # Combine the DataFrames column-wise
    consolidated_columnwise = combine_dataframes_columnwise([exp_1, exp_2, exp_3])

    # Save the consolidated DataFrame to new CSV and Excel files
    consolidated_columnwise_file = './data/results/consolidated.csv'
    excel_output_path = './data/results/consolidated.xlsx'

    save_to_csv(consolidated_columnwise, consolidated_columnwise_file)
    save_to_excel(consolidated_columnwise, excel_output_path)

if __name__ == "__main__":
    main()
