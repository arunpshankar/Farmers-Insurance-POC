from typing import List
import logging
from src.config.logging import logger
from src.config.setup import config
from src.generate.llm import LLM

def expand_query_and_get_variants(query: str, num_variants: int = 4) -> List[str]:
    """
    Expand a given query using a language model and return a list of query variants.

    Args:
    query (str): The query to be expanded.
    num_variants (int): The number of query variants to generate.

    Returns:
    List[str]: A list of expanded query variants.
    
    Raises:
    Exception: If an error occurs in the query expansion process.
    """
    try:
        llm = LLM()  # Initialize the language model
        expanded_query = llm.expand_query(query, num_variants)
        variants = expanded_query.split('|')
        cleaned_variants = [variant.strip() for variant in variants]
        return cleaned_variants
    except Exception as e:
        logger.error(f"Error expanding query '{query}': {e}")
        raise

if __name__ == '__main__':
    query = 'When would I recycle a diary comment in PSP?'
    query_variants = expand_query_and_get_variants(query)
    print(query_variants)

