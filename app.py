import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from budget_analysis import (
    load_transactions, monthly_summary,
    category_breakdown, savings_runway, spending_drift
)

st.set_page_config(
    page_title="Family Budget Intelligence",
    page_icon="💰",
    layout="wide"
)

st.title("Family Budget Intelligence")
st.markdown("*Personal finance pipeline — bank CSV → insights → decisions*")
st.divider()

uploaded = st.file_uploader(
    "Upload your bank CSV (date, description, amount, category)",
    type="csv"
)

if uploaded:
    df = load_transactions(uploaded)
else:
    st.info("No file uploaded — showing sample data")
    df = load_transactions("data/sample_transactions.csv")

months = sorted(df['month'].unique())
selected_month = st.selectbox("Select month to analyze", months, index=len(months)-1)

summary = monthly_summary(df)
net, runway = savings_runway(df, summary['Expenses'].mean())

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Income", f"${summary['Income'].sum():,.0f}")
col2.metric("Total Expenses", f"${summary['Expenses'].sum():,.0f}")
col3.metric("Net Savings", f"${net:,.0f}")
col4.metric("Savings Runway", f"{runway} months")

st.divider()
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Monthly Overview")
    fig, ax = plt.subplots(figsize=(7, 4))
    x = range(len(summary))
    width = 0.3
    ax.bar([i - width for i in x], summary['Income'],
           width=width, label='Income', color='#2ecc71')
    ax.bar(x, summary['Expenses'],
           width=width, label='Expenses', color='#e74c3c')
    ax.bar([i + width for i in x], summary['Savings'],
           width=width, label='Savings', color='#3498db')
    ax.set_xticks(list(x))
    ax.set_xticklabels(summary.index, rotation=45, ha='right')
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
    ax.legend()
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#f8f9fa')
    st.pyplot(fig)

with col_right:
    st.subheader(f"Spending by Category — {selected_month}")
    breakdown = category_breakdown(df, selected_month)
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    colors = plt.cm.Set2.colors[:len(breakdown)]
    ax2.pie(
        breakdown.values,
        labels=breakdown.index,
        autopct='%1.1f%%',
        colors=colors,
        startangle=140
    )
    ax2.set_facecolor('#f8f9fa')
    fig2.patch.set_facecolor('#f8f9fa')
    st.pyplot(fig2)

st.divider()
st.subheader("Spending Drift — Month over Month Change")
drift = spending_drift(df)
st.dataframe(
    drift.style.format("${:,.2f}").background_gradient(
        cmap='RdYlGn', axis=None
    ),
    use_container_width=True
)

st.divider()
st.subheader("Full Transaction Log")
display_df = df[df['month'] == selected_month][
    ['date', 'description', 'amount', 'category']
].sort_values('date')
st.dataframe(display_df, use_container_width=True)

st.caption("Built by Myke Tzul · mykeil-tzul.github.io/myke-portfolio")