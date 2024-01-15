# Farmers Insurance POC

## 🚀 Getting Started

Welcome to the Farmers Insurance POC repository. This guide will walk you through setting up and running the project.

### 🛠️ Development Environment 

- **Python Version**: 3.8+ (3.9+ recommended for optimal performance)
- **Recommended IDE**: Visual Studio Code or any other IDE you prefer

### Setup Instructions

#### 1. Clone the Repository:
   ```bash
   git clone https://github.com/arunpshankar/Farmers-Insurance-POC.git
   ```

#### 2. Navigate to the Project Directory:
   ```bash
   cd Farmers-Insurance-POC
   ```

#### 3. Set Up Virtual Environment (Optional but recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

#### 4. Install Dependencies:
   ```bash
   pip install -r requirements.txt
   ```

#### 5. Update Your PYTHONPATH:
   ```bash
   export PYTHONPATH=$PYTHONPATH:.
   ```

## Document Index Setup
Before running valuations, ensure to set up the document index with data provided by Farmers Insurance.

- Once the document index is created, modify `config/config.yml` to update the index ID (datastore ID).

## Instructions to Run Evaluation

1. **Perform Search Over Indexed Documents Using Vertex AI Search**:
   Navigate to `./data/input` which contains the evaluation set (`eval.csv` and `sampled_eval.csv`). Start with `sampled_eval.csv` for initial testing.

   Run the script:
   ```bash
   ./eval/doc_search.py
   ```
   This initiates a search over the index and captures results in a JSONL file.

2. **Review Search Results**:
   Check `data/results/eval_doc_search.jsonl` for the search results.

3. **Conduct Experiments**:
   Leverage the search results and summarized answers with citations to perform various experiments:
   - **Experiment 1**: Uses only the summarized answer from Vertex AI search.
   - **Experiment 2**: Utilizes extractive answers from cited documents.
   - **Experiment 3**: Similar to Experiment 2, but uses extractive segments from matched documents, then passes these to the LLM alongside the query for an answer.

   Run any of these experiments to derive answers in various styles. The answers tend to get more detailed from Experiment 1 to 3 due to growing context.

4. **Consolidate and Format Final Answers**:
   The generated answers are then consolidated and coalesced into a formatted final version.

## Additional Resources
- `/src/insights`: Contains code for comparative analysis and visualization.

---