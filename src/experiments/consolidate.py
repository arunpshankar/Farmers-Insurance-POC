import pandas as pd

# Load the CSV files
exp_1 = pd.read_csv('./data/results/exp_1_joined.csv')
exp_2 = pd.read_csv('./data/results/exp_2_joined.csv')
exp_3 = pd.read_csv('./data/results/exp_3_joined.csv')

# To combine the DataFrames column-wise, we use 'concat' with axis=1
consolidated_columnwise = pd.concat([exp_1, exp_2, exp_3], axis=1)

# Removing duplicate columns
consolidated_columnwise = consolidated_columnwise.loc[:,~consolidated_columnwise.columns.duplicated()]

# Saving the consolidated DataFrame to a new CSV file
consolidated_columnwise_file = './data/results/consolidated.csv'
consolidated_columnwise.to_csv(consolidated_columnwise_file, index=False)


# Saving as an Excel file with wrapped text
excel_output_path = './data/results/consolidated.xlsx'
with pd.ExcelWriter(excel_output_path, engine='xlsxwriter') as writer:
    consolidated_columnwise.to_excel(writer, index=False, sheet_name='Results')
    worksheet = writer.sheets['Results']
    for idx, col in enumerate(consolidated_columnwise):
        worksheet.set_column(idx, idx, 20)  # Set column width
        cell_format = writer.book.add_format({'text_wrap': True})
        worksheet.set_column(idx, idx, cell_format=cell_format)
