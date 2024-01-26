
from src.query.expander import expand_query_and_get_variants
from src.search.doc_search import search
from src.config.logging import logger
from src.config.setup import config





query = "How do I stop pay a refund check?"
brand = "Farmers"

variants = expand_query_and_get_variants(query)
search_results = []

for variant in variants:
    result = search(query, brand)
    search_results.append(result)
    print(result)
    print('-' * 100)
#print(search_results)