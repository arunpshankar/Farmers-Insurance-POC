from typing import Any, Dict, List, Tuple
from src.config.logging import logger
import json


class QueryResult:
    """Represents a search query result with its associated metadata."""

    def __init__(self, query: str, brand: str, match_id: str) -> None:
        """
        Initializes a new instance of the QueryResult class.

        Parameters:
        - query (str): The search query.
        - brand (str): The brand related to the query.
        - match_id (str): The ID of the most relevant document.
        """
        self.query = query
        self.brand = brand
        self.match_id = match_id


def find_most_weighted_id(data: List[Tuple[int, str]]) -> Tuple[str, float]:
    """
    Finds the document ID most weighted by occurrence and rank in a given list of tuples.

    Parameters:
    - data (List[Tuple[int, str]]): A list of tuples, where each tuple consists of a rank (int) and a document ID (str).

    Returns:
    - Tuple[str, float]: A tuple containing the ID with the highest aggregated score and the score itself.

    Raises:
    - ValueError: If the input list is empty or if any tuple does not follow the expected format.
    """
    if not data:
        logger.error("Input list is empty.")
        raise ValueError("The input data list cannot be empty.")

    scores = {}
    for rank, doc_id in data:
        if not isinstance(rank, int) or not isinstance(doc_id, str):
            logger.error("Invalid data format in the input list.")
            raise ValueError("Tuple elements must be an int and a str, respectively.")

        score = 1 / rank  # Inverse scoring system based on rank
        scores[doc_id] = scores.get(doc_id, 0) + score

    most_weighted_id, most_weighted_score = max(scores.items(), key=lambda item: item[1])
    return most_weighted_id, most_weighted_score

def read_jsonl_file(file_path: str) -> List[QueryResult]:
    """
    Reads a JSONL file and returns a list of QueryResult objects.

    Parameters:
    - file_path (str): The path to the JSONL file.

    Returns:
    - List[QueryResult]: A list of QueryResult objects extracted from the file.

    Raises:
    - FileNotFoundError: If the specified file does not exist.
    - json.JSONDecodeError: If the file is not valid JSONL.
    - Exception: For any other errors encountered during processing.
    """
    query_results_list = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                data = json.loads(line)
                query = data['query']
                brand = data['brand']
                matched_ids = [(match['rank'], match['knowledge_id']) for variant, info in data.items() if variant not in ['query', 'brand'] for match in info['match_info']]
                if matched_ids:
                    match_id, score = find_most_weighted_id(matched_ids)
                    query_results_list.append(QueryResult(query, brand, match_id))
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise
    return query_results_list


if __name__ == "__main__":
    try:
        file_path = './data/results/eval_2_mq_doc_search.jsonl'  # Replace with your actual file path
        query_results = read_jsonl_file(file_path)
        for query_result in query_results[:5]:  # Display data for the first 5 queries for brevity
            logger.info(f'Query: {query_result.query}, Brand: {query_result.brand}, Match ID: {query_result.match_id}')
    except Exception as e:
        logger.error(f"Failed to process file: {e}")