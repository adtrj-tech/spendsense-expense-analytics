# SpendSense — Personal Expense Analytics Dashboard

SpendSense is a Python-based expense analytics web application built with Streamlit. It helps users explore their spending patterns, understand category-wise expenses, and identify unusually large transactions using a statistical outlier detection method.

## Features

- **Expense dashboard:** View key spending metrics at a glance.
- **CSV data input:** Explore sample expense data or upload your own transaction CSV.
- **Interactive filters:** Filter transactions by category and date range.
- **Category-wise analysis:** Visualize spending across different categories.
- **Daily spending trends:** Explore how expenses change over time.
- **Transaction explorer:** Review filtered transactions in a table.
- **CSV export:** Download the filtered transaction data.
- **Unusual-spending detection:** Flag potentially unusual high-value transactions using an Interquartile Range (IQR)-based method.

## Tech Stack

- **Language:** Python
- **Web application:** Streamlit
- **Data processing:** Pandas
- **Interactive visualizations:** Plotly
- **Anomaly detection:** Statistical IQR method
- **Testing:** Pytest

## Project Structure

```text
SpendSense/
├── app.py
├── anomaly_detection.py
├── styles.css
├── requirements.txt
├── data/
│   ├── sample_expenses.csv
│   └── test_anomaly.csv
└── tests/
    └── test_anomaly_detection.py
```

## Getting Started

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd spendsense-expense-analytics
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your repository's actual HTTPS URL.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Install dependencies

On Windows, use:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Run the application

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Streamlit will provide a local URL to open the dashboard in your browser.

## Unusual-Spending Detection

SpendSense uses the Interquartile Range (IQR), a statistical method for identifying values that lie unusually far from the rest of a distribution.

The method calculates:

- **Q1:** The 25th percentile.
- **Q3:** The 75th percentile.
- **IQR:** Q3 − Q1.
- **Upper threshold:** Q3 + 1.5 × IQR.

Transactions above the applicable upper threshold are flagged as potentially unusual. Depending on the number of transactions in a category, the application uses either a category-specific threshold or a global threshold.

**Important:** An unusual transaction is not necessarily fraudulent. The result is a statistical flag for further review, not a financial judgment.

## Testing

Run the automated tests with:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

The current test suite contains eight tests covering the anomaly-detection functionality.

## Sample Data and Privacy

The repository includes sample CSV data for demonstrating the dashboard and testing anomaly detection. When using your own financial data, review the file contents before uploading or sharing them. Do not commit private financial information, passwords, API keys, or other secrets to GitHub.

## Future Improvements

- Monthly budget tracking and budget alerts.
- Spending forecasts and trend analysis.
- More detailed financial insights.
- Improved data validation and reporting.

## Author

**Adith Raj**

B.Tech Information Technology | AI & Data Science Learner

---

*SpendSense is a learning and portfolio project focused on Python, data analysis, statistical anomaly detection, and interactive dashboards.*