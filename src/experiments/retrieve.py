# Importing necessary libraries
import json
from typing import Any, Dict, List, Optional

# Importing the custom logger
from src.config.logging import logger

class SearchResult:
    """
    Represents an individual search result.
    """
    def __init__(self, data: Dict[str, Any]):
        self.rank: Optional[int] = data.get('rank')
        self.link: Optional[str] = data.get('link')
        self.knowledge_id: Optional[str] = data.get('knowledge_id')
        self.extractive_answers: List[str] = [ans.replace('Q_A_Answer__c :', '').strip() for ans in data.get('extractive_answers', [])]
        self.extractive_segments: List[str] = data.get('extractive_segments', [])


class QueryResults:
    """
    Represents all search results for a single query, including the summarized answer.
    """
    def __init__(self, query: str, brand: str, summarized_answer: str, results: List[SearchResult]):
        self.query = query
        self.brand = brand
        self.summarized_answer = summarized_answer
        self.results = {result.rank: result for result in results}

    def get_extractive_answer_by_rank(self, rank: int) -> str:
        """Return the first extractive answer for a specific rank."""
        return self.results.get(rank).extractive_answers[0] if rank in self.results and self.results[rank].extractive_answers else ""

    def get_extractive_answers_across_ranks(self) -> str:
        """Concatenate extractive answers across all ranks."""
        return '\n\n'.join([ans for result in self.results.values() for ans in result.extractive_answers])
    
    def get_first_extractive_answer(self) -> str:
        """Return the first extractive answer found across all ranks."""
        for result in self.results.values():
            if result.extractive_answers:
                return result.extractive_answers[0]
        return ""
    
    def get_extractive_segment_by_rank(self, rank: int) -> str:
        """Return the first extractive segment for a specific rank."""
        return self.results.get(rank).extractive_segments[0] if rank in self.results and self.results[rank].extractive_segments else ""

    def get_extractive_segments_across_ranks(self) -> str:
        """Concatenate extractive segments across all ranks."""
        return '\n\n'.join([seg for result in self.results.values() for seg in result.extractive_segments])
    
    def get_first_extractive_segment(self) -> str:
        """Return the first extractive segment found across all ranks."""
        for result in self.results.values():
            if result.extractive_segments:
                return result.extractive_segments[0]
        return ""


def read_jsonl_file(file_path: str) -> List[QueryResults]:
    """
    Reads a JSONL file and returns a list of QueryResults.
    """
    query_results_list = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                data = json.loads(line)
                results = [SearchResult(match) for match in data.get('match_info', [])]
                query_result = QueryResults(data['query'], data['brand'], data.get('summarized_answer', ''), results)
                query_results_list.append(query_result)
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    return query_results_list


if __name__ == "__main__":
    file_path = './data/results/sampled_eval_doc_search.jsonl'  # Replace with your actual file path
    query_results = read_jsonl_file(file_path)
    for query_result in query_results[:5]:  # Displaying data for the first 5 queries
        print()
        print(f"Query: {query_result.query}")
        print('-' * 30)
        print(f"Summarized Answer: {query_result.summarized_answer}")
        print('-' * 30)
        print(f"First Extractive Answer: {query_result.get_first_extractive_answer()}")
        print('-' * 30)
        print(f"Extractive Answers Across Ranks: {query_result.get_extractive_answers_across_ranks()}")
        print('-' * 30)
        print(f"Extractive Answer by Rank: {query_result.get_extractive_answer_by_rank(2)}")
        print('-' * 30)
        print(f"First Extractive Segment: {query_result.get_first_extractive_segment()}")
        print('-' * 30)
        print(f"Extractive Segments Across Ranks: {query_result.get_extractive_segments_across_ranks()}")
        print('-' * 30)
        print(f"Extractive Segment by Rank: {query_result.get_extractive_segment_by_rank(2)}")
        print('-' * 100)
