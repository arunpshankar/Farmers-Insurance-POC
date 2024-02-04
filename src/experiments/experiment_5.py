from src.search.multi_query_retriever import read_jsonl_file
from src.utils.io import save_to_excel
from src.config.logging import logger
from src.utils.io import save_to_csv
from src.generate.llm import LLM
from google.cloud import storage
from typing import Optional
from typing import List
from typing import Dict 
import pandas as pd
import PyPDF2
import io


llm = LLM()

def extract_text_from_gcs_pdf(gcs_url: str) -> Optional[str]:
    """
    Extracts text from a PDF file stored in Google Cloud Storage.

    Args:
    gcs_url (str): The URL of the PDF file in Google Cloud Storage. 
                   Format: 'gs://bucket-name/path/to/pdf/file.pdf'

    Returns:
    Optional[str]: Extracted text from the PDF or None if extraction fails.
    """
    try:
        # Extract bucket name and blob name from the URL
        if not gcs_url.startswith("gs://"):
            raise ValueError("URL must start with 'gs://'")

        parts = gcs_url[5:].split('/', 1)
        if len(parts) < 2:
            raise ValueError("Invalid GCS URL format")

        bucket_name, blob_name = parts

        # Initialize Google Cloud Storage client
        storage_client = storage.Client()

        # Access the bucket and blob
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Download the blob to a BytesIO object
        pdf_bytes = io.BytesIO()
        blob.download_to_file(pdf_bytes)
        pdf_bytes.seek(0)

        # Read PDF and extract text
        reader = PyPDF2.PdfReader(pdf_bytes)
        text = ''
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

        return text

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None
    

def construct_gcs_url(match_id: str) -> str:
    """
    Generates a Google Cloud Storage (GCS) URL for a PDF document based on its match ID.

    Parameters:
    - match_id (str): Unique identifier of the document.

    Returns:
    - str: GCS URL for the document.
    """
    base_url = 'gs://farmers-poc-as/documents-for-vertex-search-v1/pdfs_v3/{match_id}.pdf'
    return base_url.format(match_id=match_id)


def extract_and_process_data(file_path: str) -> List[Dict]:
    """ Extracts and processes data from a JSONL file. """
    out_data = []
    try:
        query_results = read_jsonl_file(file_path)
        for query_result in query_results:
            match_id = query_result.match_id
            query = query_result.query
            gcs_url = construct_gcs_url(match_id)
            context = extract_text_from_gcs_pdf(gcs_url)
            ans = llm.find_answer(query, context)
            out_data.append({
                'brand': query_result.brand,
                'ans_exp_5': llm.format_answer(ans),
                'matched_article_new': match_id
            })
    except Exception as e:
        logger.error(f"Error in extracting and processing JSONL data: {e}")
    return out_data


def read_and_drop_csv(file_path: str, columns_to_drop: List[str]) -> pd.DataFrame:
    """ Reads a CSV file and drops specified columns. """
    try:
        df = pd.read_csv(file_path)
        return df.drop(columns=columns_to_drop)
    except Exception as e:
        logger.error(f"Error reading or processing CSV file: {e}")
        return pd.DataFrame()


def combine_dataframes(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """ Combines two DataFrames. """
    try:
        return pd.concat([df1, df2], axis=1)
    except Exception as e:
        logger.error(f"Error combining dataframes: {e}")
        return pd.DataFrame()


def main():
    """ Main function to execute the script tasks. """
    # File paths
    jsonl_file_path = './data/results/eval_2_mq_doc_search.jsonl'
    csv_file_path = './data/input/eval_2.csv'
    concat_csv_path = './data/results/exp_5.csv'
    excel_output_path = './data/results/exp_5.xlsx'

    jsonl_data = extract_and_process_data(jsonl_file_path)
    df_jsonl = pd.DataFrame(jsonl_data)

    df_csv_dropped = read_and_drop_csv(csv_file_path, ['filter'])
    if df_csv_dropped.empty:
        return

    df_combined = combine_dataframes(df_csv_dropped, df_jsonl)
    if df_combined.empty:
        return

    save_to_csv(df_combined, concat_csv_path)
    save_to_excel(df_combined, excel_output_path)


if __name__ == "__main__":
    main()

