from src.experiments.retrieve import read_jsonl_file
from src.utils.io import save_to_excel
from src.config.logging import logger
from src.utils.io import save_to_csv
from src.generate.llm import LLM
from typing import List, Dict
import pandas as pd

# Initialize the Language Model
llm = LLM()

def read_and_process_jsonl(file_path: str) -> List[Dict]:
    """ Reads and processes data from a JSONL file. """
    out_data = []
    try:
        query_results = read_jsonl_file(file_path)
        for query_result in query_results:
            matched_articles_new = []
            matches = query_result.results
            citations = query_result.extract_citations(query_result.summarized_answer)
            for rank, match in matches.items():
                if rank in citations:
                    matched_articles_new.append(match.knowledge_id)
            out_data.append({'brand': query_result.brand, 'ans_exp_1': llm.format_answer(query_result.summarized_answer), 'matched_articles_new': '\n'.join(matched_articles_new)})
        return out_data
    except Exception as e:
        logger.error(f"Error reading or processing JSONL file: {e}")
        return []

def read_csv(file_path: str) -> pd.DataFrame:
    """ Reads data from a CSV file. """
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return pd.DataFrame()

def combine_dataframes(df_csv: pd.DataFrame, df_jsonl: pd.DataFrame) -> pd.DataFrame:
    """ Combines two DataFrames. """
    try:
        df_csv_dropped = df_csv.drop(columns=['filter'])
        return pd.concat([df_csv_dropped, df_jsonl], axis=1)
    except Exception as e:
        logger.error(f"Error combining dataframes: {e}")
        return pd.DataFrame()


def main():
    """ Main function to execute the script tasks. """
    # File paths
    jsonl_file_path = './data/results/sampled_eval_doc_search.jsonl'
    csv_file_path = './data/input/sampled_eval.csv'
    concat_csv_path = './data/results/exp_1.csv'
    excel_output_path = './data/results/exp_1.xlsx'

    logger.info("Reading and processing JSONL file.")
    jsonl_data = read_and_process_jsonl(jsonl_file_path)
    df_jsonl = pd.DataFrame(jsonl_data)
    print(df_jsonl)

    df_csv = read_csv(csv_file_path)
    if df_csv.empty:
        return

    df_combined = combine_dataframes(df_csv, df_jsonl)
    if df_combined.empty:
        return

    save_to_csv(df_combined, concat_csv_path)
    save_to_excel(df_combined, excel_output_path)

if __name__ == "__main__":
    main()
