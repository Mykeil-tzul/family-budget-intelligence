# 💰 Family Budget Intelligence Dashboard

An interactive personal finance analytics app built with Python, pandas, Streamlit, and Plotly. The app transforms raw bank CSV exports into spending trends, category breakdowns, forecasts, and actionable budget insights.

## Live Demo

[Launch Family Budget Intelligence](https://family-budget-intelligence-m.streamlit.app/)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.34-red)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

## What it does

- Loads bank-style CSV exports or generates demo transactions
- Surfaces monthly spending trends, category breakdowns, and comparisons
- Surfaces pattern views (category trends, day/week heatmaps)
- Simple forward spending forecast and an insights / recommendations tab
- Download full data or a short summary as CSV

## Dashboard Preview
![Overview](images/family-budget-overview.png)
![Forecast](images/family-budget-forecast.png)

## 🎯 Features

### 📊 Comprehensive Analytics

- **Monthly Spending Trends**: Track spending over time with trend lines
- **Category Analysis**: Breakdown by category with pie charts and statistics
- **Pattern Recognition**: Heatmaps for day-and-week spending patterns
- **Top Categories**: See highest-spend areas quickly

### 📈 Advanced Insights

- **Spending Forecasts**: Projections a few months ahead (exponential smoothing)
- **Category Trends**: Top categories over time
- **Transaction Metrics**: Totals, averages, and transaction counts for the selected range

### 🎛️ Interactive Controls

- **Date Range Filtering**: Focus analysis on a period
- **Category Filters**: Filter the dataset by category
- **Export**: Download the full dataset or a summary CSV

### 💡 Smart Recommendations

- Highlights top spend, frequency, and variability
- Rule-based tips in the Insights tab

## 📱 Dashboard Tabs

1. **📈 Overview** — Monthly trends and category comparison  
2. **🏷️ Category Analysis** — Spending breakdown with a statistics table  
3. **📅 Trends & Patterns** — Category trends and spending heatmap  
4. **🔮 Forecast** — Historical series plus projected months (slider 1–12)  
5. **💡 Insights** — Key findings and recommendations  

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher  
- pip  

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/Mykeil-tzul/family-budget-intelligence.git
cd family-budget-intelligence
```

2. **Create a virtual environment** (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Run the application**

```bash
streamlit run app.py
```

5. **Open in the browser** — usually `http://localhost:8501`

## Live demo

[Launch Dashboard →](YOUR_STREAMLIT_URL)

## 📂 Project Structure

```
family-budget-intelligence/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── sample_transactions.csv   # Optional; app falls back to generated sample data
├── README.md
└── .gitignore
```

## 📊 Data Format

The app reads a CSV with at least:

```csv
date,category,amount,description
2024-04-01,Groceries,45.50,Grocery shopping
2024-04-01,Dining Out,32.00,Restaurant dinner
2024-04-02,Utilities,120.00,Electric bill
```

**Columns**

- `date` — Transaction date (parseable by pandas, e.g. YYYY-MM-DD)  
- `category` — Spending category  
- `amount` — Numeric amount  
- `description` — Optional text  

Place the file as `sample_transactions.csv` in the project root, or rely on the built-in sample generator in `app.py`.

## 🎨 Key Technologies

- **Streamlit** — UI and layout  
- **Pandas** — Data handling  
- **NumPy** — Numeric helpers (trends, samples)  
- **Plotly** — Interactive charts  
- **Python 3**

## Skills Demonstrated

- Data Cleaning
- Exploratory Data Analysis
- KPI Development
- Time Series Trend Analysis
- Forecasting Logic
- Interactive Dashboard Design
- Business Insight Communication

## 🔧 Configuration

- **Categories (demo data)** — Adjust the `categories` dict inside `generate_sample_data()` in `app.py`.  
- **Forecast horizon** — Use the slider on the Forecast tab (1–12 months).  
- **Date range** — Use the sidebar date picker.  

## 🔐 Privacy & Security

- Processing is local unless you deploy the app yourself.  
- No built-in third-party analytics in the app code.  

## 🤝 Contributing

Contributions are welcome via Pull Request.

## Why This Project Matters

This project demonstrates the kind of applied analytics and product thinking used in real data science and analytics roles:

- ingesting and validating raw transaction data
- cleaning and standardizing records for analysis
- computing KPI-level business metrics
- identifying category-level spending behavior
- forecasting future spending patterns
- translating data into recommendations and decisions

## 📝 License

This project is licensed under the MIT License — see the LICENSE file if present.

## 📚 Resources

- [Streamlit Documentation](https://docs.streamlit.io/)  
- [Plotly Python](https://plotly.com/python/)  
- [Pandas Documentation](https://pandas.pydata.org/docs/)  

## 🔄 Version History

### v1.0.0 (2026-04-03)

- Initial dashboard release with tabs, filters, forecast, and export  

---

## Built by

[Myke Tzul](https://mykeil-tzul.github.io/myke-portfolio/) · Data Scientist | Client Consulting Analyst @ Visa  

**Made with care for clearer financial decisions**
