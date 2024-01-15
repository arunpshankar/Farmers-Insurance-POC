from src.experiments.retrieve import read_jsonl_file
from src.utils.io import save_to_excel
from src.config.logging import logger
from src.utils.io import save_to_csv
from src.generate.llm import LLM
from typing import List, Dict
import pandas as pd

llm = LLM()

def extract_and_process_data(file_path: str) -> List[Dict]:
    """ Extracts and processes data from a JSONL file. """
    data = []
    try:
        query_results = read_jsonl_file(file_path)
        for query_result in query_results:
            summarized_answer = query_result.summarized_answer
            citations = query_result.extract_citations(summarized_answer)
            context = '\n\n'.join([query_result.get_extractive_segment_by_rank(rank) for rank in citations])
            query = query_result.query
            ans = llm.find_answer(query, context)
            data.append({
                'brand': query_result.brand,
                'ans_exp_3': llm.format_answer(ans)
            })
    except Exception as e:
        logger.error(f"Error in extracting and processing JSONL data: {e}")
    return data

def read_and_drop_csv(file_path: str, columns_to_drop: List[str]) -> pd.DataFrame:
    """ Reads a CSV file and drops specified columns. """
    try:
        df = pd.read_csv(file_path)
        return df.drop(columns=columns_to_drop)
    except Exception as e:
        logger.error(f"Error reading or processing CSV file: {e}")
        return pd.DataFrame()

def combine_dataframes(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """ Combines two DataFrames. """
    try:
        return pd.concat([df1, df2], axis=1)
    except Exception as e:
        logger.error(f"Error combining dataframes: {e}")
        return pd.DataFrame()


def main():
    """ Main function to execute the script tasks. """
    # File paths
    jsonl_file_path = './data/results/eval_doc_search.jsonl'
    csv_file_path = './data/input/eval.csv'
    concat_csv_path = './data/results/exp_3.csv'
    excel_output_path = './data/results/exp_3.xlsx'

    jsonl_data = extract_and_process_data(jsonl_file_path)
    df_jsonl = pd.DataFrame(jsonl_data)

    df_csv_dropped = read_and_drop_csv(csv_file_path, ['article_id', 'filter', 'matched_articles'])
    if df_csv_dropped.empty:
        return

    df_combined = combine_dataframes(df_csv_dropped, df_jsonl)
    if df_combined.empty:
        return

    save_to_csv(df_combined, concat_csv_path)
    save_to_excel(df_combined, excel_output_path)

if __name__ == "__main__":
    main()
