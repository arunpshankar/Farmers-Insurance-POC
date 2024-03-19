from src.config.logging import logger
from collections import defaultdict
from google.cloud import storage
from src.generate.llm import LLM
from PyPDF2 import PdfReader
from typing import Optional
from typing import Tuple
from typing import List
from typing import Dict 
import pandas as pd
import time 
import io


llm = LLM()


def extract_text_from_gcs_pdf(gcs_url: str) -> Optional[str]:
    """
    Extracts text from a PDF file stored in Google Cloud Storage.

    Args:
        gcs_url (str): The URL of the PDF file in Google Cloud Storage.

    Returns:
        Optional[str]: Extracted text from the PDF or None if extraction fails.
    """
    attempt = 0
    max_attempts = 3
    backoff_factor = 2  # Time to wait multiplies by this factor with each attempt
    base_wait_time = 1  # Initial wait time in seconds

    while attempt < max_attempts:
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
            attempt += 1
            wait_time = base_wait_time * (backoff_factor ** attempt)
            logger.error(f"Attempt {attempt}/{max_attempts} failed with error: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    logger.error("Maximum retry attempts reached. Failing operation.")
    return None

def construct_gcs_url(match_id: str) -> str:
    """
    Generates a Google Cloud Storage (GCS) URL for a PDF document based on its match ID.

    Args:
        match_id (str): Unique identifier of the document.

    Returns:
        str: GCS URL for the document.
    """
    base_url = 'gs://farmers-poc-as/documents-for-vertex-search-v1/pdfs_v3/{match_id}.pdf'
    return base_url.format(match_id=match_id)

def normalize_scores_in_list(score_list: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
    """
    Normalizes the scores in a list of tuples to be between 0 and 1.

    Args:
        score_list (List[Tuple[str, float]]): Each tuple contains an identifier and a score.

    Returns:
        List[Tuple[str, float]]: A new list with the scores normalized.
    """
    if not score_list:
        return []

    scores = [score for _, score in score_list]
    min_score, max_score = min(scores), max(scores)

    if min_score == max_score:
        return [(id, 1.0) for id, _ in score_list] if max_score != 0 else [(id, 0.0) for id, _ in score_list]

    return [(id, (score - min_score) / (max_score - min_score)) for id, score in score_list]

def filter_candidates_by_threshold(candidates: List[Tuple[str, float]], threshold: float) -> List[Tuple[str, float]]:
    """
    Filters a list of candidates based on a threshold.

    Args:
        candidates (List[Tuple[str, float]]): Candidates to filter.
        threshold (float): Threshold for filtering.

    Returns:
        List[Tuple[str, float]]: Filtered candidates.
    """
    return [candidate for candidate in candidates if candidate[1] >= threshold]

def combine_and_sort(x: List[Tuple[str, float]], y: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
    """
    Combines two lists of tuples, sums scores for duplicate keys, and sorts the combined list.

    Args:
        x (List[Tuple[str, float]]): First list of tuples.
        y (List[Tuple[str, float]]): Second list of tuples.

    Returns:
        List[Tuple[str, float]]: Combined and sorted list with normalized scores.
    """
    combined_list = x + y
    score_dict = defaultdict(float)
    for key, value in combined_list:
        score_dict[key] += value
    sorted_combined_list = sorted(score_dict.items(), key=lambda item: item[1], reverse=True)
    return normalize_scores_in_list(sorted_combined_list)

def adjust_scores(tuples_list: List[Tuple[str, float]], factor: float) -> List[Tuple[str, float]]:
    """
    Adjusts the scores in a list of tuples by a given factor.

    Args:
        tuples_list (List[Tuple[str, float]]): The list of tuples to adjust.
        factor (float): The factor by which to adjust scores.

    Returns:
        List[Tuple[str, float]]: The adjusted list of tuples.
    """
    return [(item[0], item[1] * factor) for item in tuples_list]

def process_dataframe(df_path: str, output_path: str) -> None:
    """
    Processes a DataFrame to adjust scores, extract text from PDFs, and find answers to questions.

    Args:
        df_path (str): Path to the input CSV file.
        output_path (str): Path to save the output CSV file.
    """
    df = pd.read_csv(df_path)
    count = 0
    in_top3 = 0
    dist = defaultdict(int)
    out = []

    for _, row in df.iterrows():
        q, ea, pa, article_id, ma, pf, rea, brand, old_ans, cited_, matched_ = row
        cited = eval(cited_)
        matched = eval(matched_)

        cited = normalize_scores_in_list(cited)
        matched = normalize_scores_in_list(matched)
        
        z = combine_and_sort(cited, matched)
        combo = filter_candidates_by_threshold(z[:3], 0.2)
        
        if article_id == combo[0][0]:
            count += 1
        
        ids_only = [item[0] for item in combo]
        dist[len(ids_only)] += 1
        if article_id in ids_only:
            in_top3 += 1
        
        gcs_url = construct_gcs_url(combo[0][0])
        text = extract_text_from_gcs_pdf(gcs_url)
        
        llm = LLM()  # Assuming LLM is initialized here
        ans = llm.find_answer(q, text)
        
        out.append((q, ea, article_id, pf, rea, brand, old_ans, combo[0][0], ans))
    
    logger.info(f"Exact matches: {count}, In top 3: {in_top3}, Distribution: {dict(dist)}")
    
    odf = pd.DataFrame(out, columns=['question', 'expected_ans', 'expected_id', 'old_outcome', 'old_reason', 'brand', 'old_ans', 'matched_article_id', 'new_ans'])
    odf.to_csv(output_path, index=False)

if __name__ == "__main__":
    # Example usage
    input_csv_path = './data/results/exp_5_new.csv'
    output_csv_path = './data/results/exp_5_1_new.csv'
    process_dataframe(input_csv_path, output_csv_path)