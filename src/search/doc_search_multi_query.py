from src.query.expander import expand_query_and_get_variants
from src.search.doc_search import search
from src.config.logging import logger
from src.config.setup import *


def multi_query_search(query: str, brand: str) -> dict:
    """
    Expands a given query, performs a search for each variant with the specified brand, 
    and returns the search results in a dictionary mapping each query variant to its results.

    Args:
    query (str): The query to be expanded and searched.
    brand (str): The brand to be included in the search.

    Returns:
    dict: A dictionary mapping each query variant to a list of search results.

    Raises:
    Exception: If an error occurs during the query expansion or search process.
    """
    try:
        variants = expand_query_and_get_variants(query)
        search_results = {}
        result = search(query, brand)
        search_results[query] = result
        for variant in variants:
            result = search(variant, brand)
            search_results[variant] = result
        return search_results
    except Exception as e:
        logger.error(f"Error in perform_brand_search with query '{query}' and brand '{brand}': {e}")
        raise

if __name__ == '__main__':
    query = "How do I stop a refund check?"
    brand = "Farmers"
    results = multi_query_search(query, brand)
    for variant, result in results.items():
        print(f"Query: {variant}")
        print(result)
        print('-' * 100)
