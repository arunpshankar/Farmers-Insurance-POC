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
    

