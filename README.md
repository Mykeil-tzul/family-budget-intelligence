# Family Budget Intelligence

Personal finance pipeline built with Python and Streamlit.

## What it does
- Ingests bank CSV exports (date, description, amount, category)
- Calculates monthly income vs expenses vs savings
- Breaks down spending by category per month
- Tracks spending drift — month over month changes by category
- Estimates savings runway in months

## Tech stack
Python · pandas · Matplotlib · Streamlit

## Live demo
[Launch Dashboard →](YOUR_STREAMLIT_URL)

## Run locally
```bash
git clone https://github.com/Mykeil-tzul/family-budget-intelligence.git
cd family-budget-intelligence
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Built by
[Myke Tzul](https://mykeil-tzul.github.io/myke-portfolio/) · 
Data Scientist | Client Consulting Analyst @ Visa
