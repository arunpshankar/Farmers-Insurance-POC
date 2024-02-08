from src.search.multi_query_retriever import read_jsonl_file
from src.utils.io import save_to_excel
from src.config.logging import logger
from src.utils.io import save_to_csv
from src.generate.llm import LLM
from google.cloud import storage
from PyPDF2 import PdfReader
from typing import Optional
from typing import List
from typing import Dict 
import pandas as pd
import io


llm = LLM()

def extract_text_from_gcs_pdf(gcs_url: str) -> Optional[str]:
    """
    Extracts text from a PDF file stored in Google Cloud Storage (GCS).

    Parameters:
    - gcs_url (str): The URL of the PDF file in GCS. Format: 'gs://bucket-name/path/to/file.pdf'

    Returns:
    - Optional[str]: The extracted text from the PDF, or None if extraction fails.
    """
    try:
        if not gcs_url.startswith("gs://"):
            raise ValueError("URL must start with 'gs://'")

        parts = gcs_url[5:].split('/', 1)
        if len(parts) < 2:
            raise ValueError("Invalid GCS URL format")

        bucket_name, blob_name = parts

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        pdf_bytes = io.BytesIO()
        blob.download_to_file(pdf_bytes)
        pdf_bytes.seek(0)

        reader = PdfReader(pdf_bytes)
        text = ''.join(page.extract_text() for page in reader.pages if page.extract_text())

        return text
    except Exception as e:
        logger.error(f"Failed to extract text from PDF in GCS: {e}", exc_info=True)
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

def query_document(query: str, match_id: str) -> Optional[str]:
    """
    Queries a document in GCS with a given match ID for a specific query and extracts the relevant answer.

    Parameters:
    - query (str): The question to find an answer to within the document.
    - match_id (str): The match ID of the document in GCS.

    Returns:
    - Optional[str]: The extracted answer if found, otherwise None.
    """
    gcs_url = construct_gcs_url(match_id)
    text = extract_text_from_gcs_pdf(gcs_url)
    if text is not None:
        ans = llm.find_answer(query, text) 
        return ans
    else:
        logger.info(f"No text extracted for match_id: {match_id}")
        return None

# Example usage
query = 'What is the mid-term cancellation fee in CA?'
matched_id = [('kaD4T0000004dL3UAI', 1.0)]

answer = query_document(query, matched_id[0][0])
logger.info(answer)