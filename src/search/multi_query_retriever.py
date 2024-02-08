from typing import Any, Dict, List, Tuple
from src.config.logging import logger
from collections import Counter
import json
import re 


class QueryResult:
    """Represents a search query result with its associated metadata."""

    def __init__(self, query: str, brand: str, match_ids: list, cited_ids: list) -> None:
        """
        Initializes a new instance of the QueryResult class.

        Parameters:
        - query (str): The search query.
        - brand (str): The brand related to the query.
        - match_ids (list): List of IDs of most relevant docs.
        - cited_ids (list)
        """
        self.query = query
        self.brand = brand
        self.match_ids = match_ids
        self.cited_ids = cited_ids


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


def find_most_weighted_ids(data: List[Tuple[int, str]], top_k: int = 1) -> List[Tuple[str, float]]:
    """
    Finds the document IDs most weighted by occurrence and rank in a given list of tuples, returning the top k IDs.

    Parameters:
    - data (List[Tuple[int, str]]): A list of tuples, where each tuple consists of a rank (int) and a document ID (str).
    - top_k (int): The number of top weighted IDs to return.

    Returns:
    - List[Tuple[str, float]]: A list of tuples, each containing an ID with a high aggregated score and the score itself, up to top k items.

    Raises:
    - ValueError: If the input list is empty, if any tuple does not follow the expected format, or if top_k is less than 1.
    """
    if not data:
        return []
    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    scores = {}
    for rank, doc_id in data:
        if not isinstance(rank, int) or not isinstance(doc_id, str):
            raise ValueError("Tuple elements must be an int and a str, respectively.")

        score = 1 / rank  # Inverse scoring system based on rank
        scores[doc_id] = scores.get(doc_id, 0) + score

    # Sort items based on score in descending order and select the top k
    top_weighted_ids = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_k]
    return top_weighted_ids


def extract_ids_from_tuples(input_tuples: List[Tuple[str, float]]) -> List[str]:
    """
    Extracts and returns the first element of each tuple in a list of tuples.

    Parameters:
    - input_tuples (List[Tuple[str, float]]): A list of tuples, where each tuple consists of an ID (str) and a value (float).

    Returns:
    - List[str]: A list of IDs extracted from the input list of tuples.
    """
    return [tup[0] for tup in input_tuples]


def extract_citations(text: str) -> list:
        """
        Extracts and returns a list of citations from the given text, sorted by frequency.

        Parameters:
        text (str): The text from which citations are to be extracted.

        Returns:
        list: A list of integers representing the citations, sorted by their frequency.
        """
        try:
            citations = re.findall(r'\[\d+\]', text)
            citation_counts = Counter(int(citation.strip('[]')) for citation in citations)
            return sorted(citation_counts, key=citation_counts.get, reverse=True)
        except Exception as e:
            raise RuntimeError(f"An error occurred: {e}")
        

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
                matched_ids = []
                cited_ids = []
               
                for variant, info in data.items():
                    if variant not in ['query', 'brand'] and info:
                        match_info = info['match_info']
                        for match in match_info:
                            rank = match['rank']
                            knowledge_id = match['knowledge_id']
                            matched_ids.append((rank, knowledge_id))
                most_weighted_ids = find_most_weighted_ids(matched_ids, top_k=5)
                #ids = extract_ids_from_tuples(most_weighted_ids)

                for variant, info in data.items():
                    if variant not in ['query', 'brand'] and info:
                        summary = info['summarized_answer']
                        citations = extract_citations(summary)
                        match_info = info['match_info']
                        for match in match_info:
                            rank = match['rank']
                            knowledge_id = match['knowledge_id']
                            if rank in citations:
                                cited_ids.append((rank, knowledge_id))

                most_weighted_cited_ids = find_most_weighted_ids(cited_ids, top_k=5)
                #ids_by_citation = extract_ids_from_tuples(most_weighted_cited_ids)
                query_results_list.append(QueryResult(query, brand, most_weighted_ids, most_weighted_cited_ids))
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
            logger.info(f'Query: {query_result.query}, Brand: {query_result.brand}, Cited IDs: {query_result.cited_ids}, Match IDs: {query_result.match_ids}')
    except Exception as e:
        logger.error(f"Failed to process file: {e}")