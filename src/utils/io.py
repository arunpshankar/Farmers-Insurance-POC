
from src.config.logging import logger
import pandas as pd 


def save_to_excel(df: pd.DataFrame, file_path: str):
    """ Saves DataFrame to an Excel file with wrapped text. """
    try:
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Results')
            worksheet = writer.sheets['Results']
            for idx, _ in enumerate(df):
                worksheet.set_column(idx, idx, 20, writer.book.add_format({'text_wrap': True}))
        logger.info(f"DataFrame saved as Excel file at {file_path}")
    except Exception as e:
        logger.error(f"Error saving Excel file: {e}")


def save_to_csv(df: pd.DataFrame, file_path: str):
    """ Saves DataFrame to a CSV file. """
    try:
        df.to_csv(file_path, index=False)
        logger.info(f"DataFrame saved as CSV at {file_path}")
    except Exception as e:
        logger.error(f"Error saving CSV file: {e}")