from src.search.doc_search import search
from src.config.logging import logger
import jsonlines 
import csv


def process_csv_and_write_jsonl(csv_file_path, jsonl_file_path):
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        with jsonlines.open(jsonl_file_path, mode='w') as writer:
            for row in reader:
                query = row['question']
                brand = row['filter']
                logger.info(f'Performing doc search for query={query}')
                search_result = search(query, brand)
                # Include the query and brand in the result
                search_result.update({"query": query, "brand": brand})
                writer.write(search_result)

# Define file paths
csv_file_path = './data/input/eval_2.csv'
jsonl_file_path = './data/results/eval_doc_search_2.jsonl'

# Process the CSV file and write to a JSONL file
process_csv_and_write_jsonl(csv_file_path, jsonl_file_path)