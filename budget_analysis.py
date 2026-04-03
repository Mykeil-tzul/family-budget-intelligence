import pandas as pd

def load_transactions(filepath):
    df = pd.read_csv(filepath, parse_dates=['date'])
    df['month'] = df['date'].dt.to_period('M').astype(str)
    df['type'] = df['amount'].apply(
        lambda x: 'Income' if x > 0 else 'Expense'
    )
    return df

def monthly_summary(df):
    income = df[df['type'] == 'Income'].groupby('month')['amount'].sum()
    expenses = df[df['type'] == 'Expense'].groupby('month')['amount'].sum().abs()
    savings = income - expenses
    summary = pd.DataFrame({
        'Income': income,
        'Expenses': expenses,
        'Savings': savings
    }).fillna(0)
    return summary

def category_breakdown(df, month=None):
    expenses = df[df['type'] == 'Expense'].copy()
    if month:
        expenses = expenses[expenses['month'] == month]
    breakdown = expenses.groupby('category')['amount'].sum().abs()
    return breakdown.sort_values(ascending=False)

def savings_runway(df, monthly_expenses_avg):
    income = df[df['type'] == 'Income']['amount'].sum()
    expenses = df[df['type'] == 'Expense']['amount'].sum().abs()
    net_savings = income - expenses
    if monthly_expenses_avg > 0:
        runway_months = net_savings / monthly_expenses_avg
    else:
        runway_months = 0
    return round(net_savings, 2), round(runway_months, 1)

def spending_drift(df):
    monthly = df[df['type'] == 'Expense'].groupby(
        ['month', 'category']
    )['amount'].sum().abs().unstack(fill_value=0)
    drift = monthly.diff().iloc[1:]
    return drift