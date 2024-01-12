import pandas as pd 
from src.generate.llm import LLM

llm = LLM()


df = pd.read_csv('./data/results/consolidated.csv')

merged_answers = []
for _, row in df.iterrows():
    merged_ans = []
    _, _, _, _, _, ans_exp_1, ans_exp_2, ans_exp_3 = row 
    merged_ans.append('Answer 1')
    merged_ans.append(ans_exp_1)
    merged_ans.append('\n\n')
    merged_ans.append('Answer 2')
    merged_ans.append(ans_exp_2)
    merged_ans.append('\n\n')
    merged_ans.append('Answer 3')
    merged_ans.append(ans_exp_3)
    merged_answers.append('\n'.join(merged_ans))

coalesced_answers = []
for ans in merged_answers:
    coalesced_answer = llm.coalesce_answer(ans)
    coalesced_answers.append(coalesced_answer)


df['final_answer'] = coalesced_answers

# Saving the combined DataFrame as a new CSV file 
df.to_csv('./data/results/coalesced.csv', index=False)

# Saving as an Excel file with wrapped text
with pd.ExcelWriter('./data/results/coalesced.xlsx', engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Results')
    worksheet = writer.sheets['Results']
    for idx, col in enumerate(df):
        worksheet.set_column(idx, idx, 20)  # Set column width
        cell_format = writer.book.add_format({'text_wrap': True})
        worksheet.set_column(idx, idx, cell_format=cell_format)




