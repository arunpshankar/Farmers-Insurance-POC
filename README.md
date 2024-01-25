# Farmers Insurance POC: Project Setup Guide

This guide provides detailed instructions for setting up and running the project effectively.

## Development Environment

- **Python Version**: Ensure Python 3.8 or higher is installed (3.9 or higher recommended for optimal performance).
- **IDE Recommendation**: Visual Studio Code is suggested, but feel free to use any IDE of your preference.

## Setup Instructions

### 1. Clone the Repository
Execute the following command in your terminal:
```bash
git clone https://github.com/arunpshankar/Farmers-Insurance-POC.git
```

### 2. Project Directory
Change into the cloned directory:
```bash
cd Farmers-Insurance-POC
```

### 3. Virtual Environment (Optional, but Recommended)
Set up and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 5. Update PYTHONPATH
Add the project directory to your PYTHONPATH:
```bash
export PYTHONPATH=$PYTHONPATH:.
```

### 6. Google Cloud Platform (GCP) Credentials
Generate service account credentials for your GCP project, download the JSON key, and place it in the project's `credentials/` folder at the root directory.

## Document Index Setup
Ensure the document index is prepared with necessary data for evaluation as instructed by the PSO team.

- Modify `config/config.yml` to update the datastore ID with the newly created index ID.

## Running Evaluations

### 1. Search Indexed Documents
Navigate to `./data/input` for the evaluation set (`eval.csv` and `sampled_eval.csv`). Start with `sampled_eval.csv` for dry run.

Execute the script:
```bash
Python src/eval/doc_search.py
```
This script initiates a search over the index, capturing results in a JSONL file.

### 2. Review Search Results
Examine the results in `data/results/eval_doc_search.jsonl`.

### 3. Conduct Experiments
Perform various experiments using the search results:

- **Experiment 1**: Direct summarized answers from Vertex AI Search.
- **Experiment 2**: Utilizes extractive answers from cited documents and refines them with LLM.
- **Experiment 3**: Similar to Experiment 2, but uses extractive segments and further refines them with the LLM.

Run these scripts for respective experiments:
```bash
python src/experiments/experiment_1.py
python src/experiments/experiment_2.py
python src/experiments/experiment_3.py
```

### 4. Consolidate and Format Final Answers
Combine and finalize the answers:

- Run `src/experiments/consolidate.py` to merge answers from all experiments.
- Execute `src/experiments/coalesce.py` for a final LLM pass to ensure cohesive, non-duplicative answers.

## Additional Resources
- Explore `/src/insights` for code related to comparative analysis and visualizations.

---