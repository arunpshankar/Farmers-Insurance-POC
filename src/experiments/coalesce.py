from src.utils.io import save_to_excel
from src.utils.io import save_to_csv
from src.generate.llm import LLM
import pandas as pd 


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
