import pandas as pd 
from src.generate.llm import LLM

def merge_answers(df: pd.DataFrame) -> list:
    """ Merges answers from different columns of a DataFrame into a single list. """
    merged_answers = []
    for _, row in df.iterrows():
        ans_exp_1, ans_exp_2, ans_exp_3 = row['ans_exp_1'], row['ans_exp_2'], row['ans_exp_3']
        merged_ans = ['Answer 1', ans_exp_1, '\n\n', 'Answer 2', ans_exp_2, '\n\n', 'Answer 3', ans_exp_3]
        merged_answers.append('\n'.join(merged_ans))
    return merged_answers

def coalesce_answers(merged_answers: list, llm: LLM) -> list:
    """ Coalesces merged answers using the provided language model. """
    return [llm.coalesce_answer(ans) for ans in merged_answers]

def save_to_csv(df: pd.DataFrame, file_path: str):
    """ Saves DataFrame to a CSV file. """
    df.to_csv(file_path, index=False)
    print(f"DataFrame saved as CSV at {file_path}")

def save_to_excel(df: pd.DataFrame, file_path: str):
    """ Saves DataFrame to an Excel file with wrapped text. """
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Results')
        worksheet = writer.sheets['Results']
        for idx, _ in enumerate(df):
            worksheet.set_column(idx, idx, 20, writer.book.add_format({'text_wrap': True}))
    print(f"DataFrame saved as Excel file at {file_path}")

def main():
    llm = LLM()
    df = pd.read_csv('./data/results/consolidated.csv')

    merged_answers = merge_answers(df)
    coalesced_answers = coalesce_answers(merged_answers, llm)
    df['final_answer'] = coalesced_answers

    # Save the combined DataFrame as new CSV and Excel files
    csv_output_path = './data/results/coalesced.csv'
    excel_output_path = './data/results/coalesced.xlsx'

    save_to_csv(df, csv_output_path)
    save_to_excel(df, excel_output_path)

if __name__ == "__main__":
    main()
