from src.experiments.retrieve import read_jsonl_file
from src.generate.llm import LLM
import pandas as pd

llm = LLM()

# File paths
jsonl_file_path = './data/results/sampled_eval_doc_search.jsonl'  # Adjusted file path for the assistant's file system
csv_file_path = './data/input/sampled_eval.csv'
output_csv_path = './data/results/exp_1.csv'
joined_csv_path = './data/results/exp_1_joined.csv'
excel_output_path = './data/results/exp_1_joined.xlsx'

# Reading JSONL file and extracting required information
data = []

query_results = read_jsonl_file(jsonl_file_path)
for query_result in query_results:
    data.append({
            'question': query_result.query,
            'ans_exp_1': llm.format_answer(query_result.summarized_answer)
        })

# Creating a DataFrame from the JSONL data and saving it as a CSV file
df_jsonl = pd.DataFrame(data)
df_jsonl.to_csv(output_csv_path, index=False)

# Reading the original CSV file
df_csv = pd.read_csv(csv_file_path)

# Dropping the specified columns: 'article_id', 'filter', 'matched_article'
df_csv_dropped = df_csv.drop(columns=['article_id', 'filter', 'matched_articles'])

# Combining the two DataFrames based on the 'question' column
df_joined = df_csv_dropped.merge(df_jsonl, on='question', how='outer')

# Saving the combined DataFrame as a new CSV file 
df_joined.to_csv(joined_csv_path, index=False)

# Saving as an Excel file with wrapped text
with pd.ExcelWriter(excel_output_path, engine='xlsxwriter') as writer:
    df_joined.to_excel(writer, index=False, sheet_name='Results')
    worksheet = writer.sheets['Results']
    for idx, col in enumerate(df_joined):
        worksheet.set_column(idx, idx, 20)  # Set column width
        cell_format = writer.book.add_format({'text_wrap': True})
        worksheet.set_column(idx, idx, cell_format=cell_format)

