from src.config.logging import logger
import matplotlib.pyplot as plt
from typing import Tuple
import pandas as pd
import os

def load_excel_data(file_path: str) -> pd.DataFrame:
    """
    Load data from an Excel file.

    Args:
    file_path (str): Path to the Excel file.

    Returns:
    pd.DataFrame: Dataframe containing the loaded data.
    """
    logger.info(f"Loading data from {file_path}")
    return pd.read_excel(file_path)

def prepare_data_for_plotting(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """
    Prepare data for plotting by processing 'pass_fail' and 'label' columns.

    Args:
    df (pd.DataFrame): The dataframe containing the data.

    Returns:
    Tuple[pd.Series, pd.Series]: Two Series objects for plotting.
    """
    # Process 'pass_fail' column
    pass_fail_breakdown = df['pass_fail'].value_counts()
    pass_fail_breakdown_corrected = pass_fail_breakdown.rename(
        index={'PASS': 'Pass', 'FAIL': 'Fail', 'Partial Pass': 'Partial Pass', 
               'Missing Content in Load': 'Fail', 'Pass - No Answer provided answer.': 'Pass'})
    pass_fail_breakdown_corrected = pass_fail_breakdown_corrected.groupby(level=0).sum()

    # Process 'label' column
    label_breakdown = df['label'].value_counts().rename(index={1.0: 'Pass', 0.0: 'Fail', 0.5: 'Partial Pass'})
    label_data = label_breakdown.reindex(['Pass', 'Partial Pass', 'Fail']).fillna(0)

    return pass_fail_breakdown_corrected, label_data

def plot_data(pass_fail_data: pd.Series, label_data: pd.Series, output_file: str):
    """
    Plot and save the data.

    Args:
    pass_fail_data (pd.Series): Data for the 'Pass/Fail' plot.
    label_data (pd.Series): Data for the 'Label' plot.
    output_file (str): Path to save the output plot.
    """
    # Plotting
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(15, 6))
    fig.suptitle('Farmers Insurance Comparative Analysis', fontsize=16)

    # 'Pass/Fail' plot
    pass_fail_data.plot(kind='bar', ax=axes[0], color='skyblue', title='Assessment of Pass/Fail Outcomes (Before)')
    axes[0].set_xlabel('Category')
    axes[0].set_ylabel('Frequency')

    # 'Label' plot
    label_data.plot(kind='bar', ax=axes[1], color='salmon', title='Assessment of Pass/Fail Outcomes (After)')
    axes[1].set_xlabel('Category')
    axes[1].set_ylabel('Frequency')

    # Save the plot
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))
    plt.savefig(output_file, bbox_inches='tight', transparent=True)
    plt.close()
    logger.info(f"Plot saved to {output_file}")

# Main execution
if __name__ == "__main__":
    file_path = './data/results/coalesced.xlsx'
    df = load_excel_data(file_path)
    pass_fail_breakdown_corrected, label_data = prepare_data_for_plotting(df)
    output_file = './data/results/figures/comparison_plots.png'
    plot_data(pass_fail_breakdown_corrected, label_data, output_file)
