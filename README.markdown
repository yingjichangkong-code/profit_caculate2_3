# Urban Renewal Decision Software

A Python-based decision support tool for urban renewal planning, solving:

- **Problem 2**: Sort compounds by marginal cost-effectiveness.
- **Problem 3**: Find the cost-effectiveness inflection point using NSGA-II.

## Installation

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd urban_renewal
   ```
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:

   ```bash
   streamlit run main.py
   ```

## Usage

- **Input**: Upload `compounds.csv` and `config.json` or edit via UI.
- **Run**: Click "Run Problem 2" or "Run Problem 3" to compute results.
- **Output**: View tables, text, and plots; export results as ZIP.

## File Structure

- `main.py`: Streamlit UI.
- `data_handler.py`: Data loading.
- `problem_two.py`: Problem 2 computation.
- `problem_three.py`: Problem 3 computation.
- `utils.py`: Union-find and visualizations.
- `templates/`: Default data files.

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies.