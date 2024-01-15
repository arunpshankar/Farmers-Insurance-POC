from src.utils.io import save_to_excel
from src.config.logging import logger
from src.utils.io import save_to_csv
import pandas as pd

def load_csv(file_path: str) -> pd.DataFrame:
    """ Loads a CSV file into a DataFrame. """
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        logger.info(f"Error loading CSV file {file_path}: {e}")
        return pd.DataFrame()

def combine_dataframes_columnwise(dfs: list) -> pd.DataFrame:
    """ Combines a list of DataFrames column-wise. """
    combined_df = pd.concat(dfs, axis=1)
    # Removing duplicate columns
    return combined_df.loc[:, ~combined_df.columns.duplicated()]


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
