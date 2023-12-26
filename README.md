## Prerequisites

- Anaconda installed
- Python 3.x
- Required Python packages (install with `pip install -r requirements.txt`):
  - `pandas`
  - `numpy`
  - `scikit-learn`
  -

## Installation

1. Navigate to the project repository:

   ```bash
   cd recommender-system
   ```

2. Run the cmd below to create and install requirements packages:

   ```bash
   conda env create --name streamlit_sia --file conda.yml
   conda activate streamlit_sia
   ```

3. Usage

   Run the training pipeline as follows:

   ```bash
    streamlit run app.py
   ```
