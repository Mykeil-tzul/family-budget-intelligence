from pathlib import Path
from datetime import timedelta
import warnings

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Family Budget Intelligence Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# STYLING
# =========================
st.markdown(
    """
    <style>
    .title-main {
        color: #1f4788;
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 8px;
    }
    .subtitle {
        color: #666;
        font-size: 16px;
        margin-bottom: 24px;
    }
    .section-note {
        color: #666;
        font-size: 14px;
        margin-top: -6px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# DATA HELPERS
# =========================
@st.cache_data
def generate_sample_data() -> pd.DataFrame:
    """Generate demo transaction data if no CSV is available."""
    np.random.seed(42)

    dates = pd.date_range(start="2024-04-01", end="2025-03-31", freq="D")

    categories = {
        "Groceries": {"weight": 0.20, "variation": 0.30},
        "Utilities": {"weight": 0.10, "variation": 0.15},
        "Entertainment": {"weight": 0.12, "variation": 0.50},
        "Dining Out": {"weight": 0.15, "variation": 0.40},
        "Transportation": {"weight": 0.13, "variation": 0.25},
        "Shopping": {"weight": 0.12, "variation": 0.60},
        "Healthcare": {"weight": 0.08, "variation": 0.70},
        "Other": {"weight": 0.10, "variation": 0.40},
    }

    transactions = []
    daily_budget = 50

    for date in dates:
        if np.random.random() < 0.7:
            num_transactions = np.random.randint(1, 4)

            for _ in range(num_transactions):
                category = np.random.choice(list(categories.keys()))
                cat_data = categories[category]

                base_amount = daily_budget * cat_data["weight"] * np.random.uniform(0.5, 1.5)
                amount = base_amount * np.random.uniform(
                    1 - cat_data["variation"],
                    1 + cat_data["variation"],
                )

                transactions.append(
                    {
                        "date": date,
                        "category": category,
                        "amount": round(float(amount), 2),
                        "description": f"{category} purchase",
                    }
                )

    return pd.DataFrame(transactions)


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names and validate required fields."""
    df = df.copy()
    df.columns = [str(col).strip().lower() for col in df.columns]

    required = {"date", "category", "amount", "description"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing))}. "
            "CSV must include date, category, amount, description."
        )

    return df


def preprocess_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Clean transaction data for analysis."""
    df = standardize_columns(df)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["category"] = df["category"].astype(str).str.strip()
    df["description"] = df["description"].astype(str).str.strip()

    df = df.dropna(subset=["date", "amount", "category", "description"]).copy()
    df["amount"] = df["amount"].abs()
    df["year_month"] = df["date"].dt.to_period("M").astype(str)
    df["day_name"] = df["date"].dt.day_name()
    df["week"] = df["date"].dt.isocalendar().week.astype(int)

    return df.sort_values("date").reset_index(drop=True)


@st.cache_data
def load_sample_data() -> pd.DataFrame:
    """Load local sample CSV or fall back to generated data."""
    base_dir = Path(__file__).resolve().parent
    sample_path = base_dir / "data" / "data" / "sample_transactions_famintel.csv"

    try:
        df = pd.read_csv(sample_path)
        return preprocess_transactions(df)
    except Exception:
        return preprocess_transactions(generate_sample_data())


def load_uploaded_data(uploaded_file) -> pd.DataFrame:
    """Load uploaded CSV file."""
    df = pd.read_csv(uploaded_file)
    return preprocess_transactions(df)


# =========================
# ANALYTICS
# =========================
def apply_filters(
    df: pd.DataFrame,
    start_date,
    end_date,
    selected_category: str,
) -> pd.DataFrame:
    filtered = df.copy()

    start_ts = pd.to_datetime(start_date)
    end_ts = pd.to_datetime(end_date)

    mask = (filtered["date"] >= start_ts) & (filtered["date"] <= end_ts)
    filtered = filtered.loc[mask].copy()

    if selected_category != "All":
        filtered = filtered[filtered["category"] == selected_category].copy()

    return filtered


def calculate_metrics(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "total_spent": 0.0,
            "avg_daily": 0.0,
            "avg_transaction": 0.0,
            "num_transactions": 0,
            "monthly_avg": 0.0,
            "top_category": "N/A",
            "top_category_amount": 0.0,
        }

    total_spent = float(df["amount"].sum())
    active_days = max(df["date"].nunique(), 1)
    active_months = max(df["year_month"].nunique(), 1)

    category_totals = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    top_category = category_totals.index[0]
    top_category_amount = float(category_totals.iloc[0])

    return {
        "total_spent": total_spent,
        "avg_daily": total_spent / active_days,
        "avg_transaction": float(df["amount"].mean()),
        "num_transactions": int(len(df)),
        "monthly_avg": total_spent / active_months,
        "top_category": top_category,
        "top_category_amount": top_category_amount,
    }


def spending_change_pct(df: pd.DataFrame) -> float:
    if df.empty or df["year_month"].nunique() < 2:
        return 0.0

    monthly = df.groupby("year_month")["amount"].sum()
    first_half = monthly.iloc[: max(len(monthly) // 2, 1)].sum()
    second_half = monthly.iloc[max(len(monthly) // 2, 1) :].sum()

    if first_half == 0:
        return 0.0
    return float(((second_half - first_half) / first_half) * 100)


def create_monthly_trend(df: pd.DataFrame):
    monthly = df.groupby("year_month", as_index=False)["amount"].sum()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=monthly["year_month"],
            y=monthly["amount"],
            mode="lines+markers",
            name="Actual Spending",
        )
    )

    if len(monthly) >= 3:
        x = np.arange(len(monthly))
        z = np.polyfit(x, monthly["amount"], 2)
        trend = np.poly1d(z)(x)

        fig.add_trace(
            go.Scatter(
                x=monthly["year_month"],
                y=trend,
                mode="lines",
                name="Trend",
                line=dict(dash="dash"),
            )
        )

    fig.update_layout(
        title="Monthly Spending Trend",
        xaxis_title="Month",
        yaxis_title="Total Spending ($)",
        hovermode="x unified",
        height=420,
    )
    return fig


def create_category_comparison(df: pd.DataFrame):
    category_stats = (
        df.groupby("category")["amount"]
        .agg(["sum", "count"])
        .sort_values("sum", ascending=True)
        .reset_index()
    )

    fig = px.bar(
        category_stats,
        x="sum",
        y="category",
        orientation="h",
        title="Total Spending by Category",
        labels={"sum": "Total Amount ($)", "category": "Category"},
        color="sum",
        color_continuous_scale="Viridis",
    )
    fig.update_layout(height=420, showlegend=False)
    return fig


def create_spending_by_category(df: pd.DataFrame):
    category_spending = (
        df.groupby("category")["amount"]
        .agg(["sum", "count", "mean"])
        .round(2)
        .sort_values("sum", ascending=False)
    )

    fig = px.pie(
        category_spending.reset_index(),
        values="sum",
        names="category",
        title="Spending Distribution by Category",
        hole=0.35,
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return fig, category_spending


def create_daily_heatmap(df: pd.DataFrame):
    heatmap_data = df.groupby(["week", "day_name"], as_index=False)["amount"].sum()
    heatmap_pivot = heatmap_data.pivot_table(
        index="day_name",
        columns="week",
        values="amount",
        fill_value=0,
    )

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    existing_days = [day for day in day_order if day in heatmap_pivot.index]
    heatmap_pivot = heatmap_pivot.reindex(existing_days)

    fig = px.imshow(
        heatmap_pivot,
        labels=dict(x="Week Number", y="Day of Week", color="Amount ($)"),
        title="Spending Heatmap: Day & Week Patterns",
        color_continuous_scale="RdYlGn_r",
        aspect="auto",
    )
    fig.update_layout(height=320)
    return fig


def create_category_trends(df: pd.DataFrame):
    top_categories = df.groupby("category")["amount"].sum().nlargest(5).index
    filtered_df = df[df["category"].isin(top_categories)].copy()

    trend_df = (
        filtered_df.groupby(["year_month", "category"], as_index=False)["amount"].sum()
    )

    fig = px.line(
        trend_df,
        x="year_month",
        y="amount",
        color="category",
        title="Top 5 Categories - Monthly Trend",
        markers=True,
        height=420,
    )
    fig.update_xaxes(tickangle=-45)
    return fig


def forecast_spending(df: pd.DataFrame, months_ahead: int = 3):
    monthly = df.groupby("year_month")["amount"].sum()
    if monthly.empty:
        return []

    alpha = 0.3
    forecast = []
    last_value = float(monthly.iloc[-1])
    baseline = float(monthly.mean())

    for _ in range(months_ahead):
        next_value = alpha * last_value + (1 - alpha) * baseline
        forecast.append(float(next_value))
        last_value = next_value

    return forecast


def build_insights(df: pd.DataFrame) -> list[str]:
    insights = []
    if df.empty:
        return ["No data available for the selected filters."]

    total = df["amount"].sum()
    category_totals = df.groupby("category")["amount"].sum().sort_values(ascending=False)

    top_category = category_totals.index[0]
    top_pct = (category_totals.iloc[0] / total) * 100 if total else 0
    insights.append(f"Top spend category is **{top_category}**, making up **{top_pct:.1f}%** of total spend.")

    if "Dining Out" in category_totals.index:
        dining_pct = (category_totals["Dining Out"] / total) * 100 if total else 0
        insights.append(f"**Dining Out** accounts for **{dining_pct:.1f}%** of total spending.")

    if "Groceries" in category_totals.index and "Dining Out" in category_totals.index:
        if category_totals["Dining Out"] > category_totals["Groceries"] * 0.5:
            insights.append("Dining spend is relatively high versus groceries. Meal planning could reduce leakage.")

    monthly = df.groupby("year_month")["amount"].sum()
    if len(monthly) >= 2:
        latest = monthly.iloc[-1]
        prior = monthly.iloc[-2]
        if prior > 0:
            change = ((latest - prior) / prior) * 100
            direction = "up" if change > 0 else "down"
            insights.append(f"Latest month is **{direction} {abs(change):.1f}%** versus the prior month.")

    return insights


# =========================
# APP HEADER
# =========================
st.markdown('<p class="title-main">💰 Family Budget Intelligence</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Personal finance pipeline — bank CSV → insights → decisions</p>',
    unsafe_allow_html=True,
)

# =========================
# LOAD DATA
# =========================
uploaded_file = st.file_uploader(
    "Upload your bank CSV (date, description, amount, category)",
    type=["csv"],
)

if uploaded_file is not None:
    try:
        df = load_uploaded_data(uploaded_file)
        st.success("Uploaded file loaded successfully.")
    except Exception as e:
        st.error(f"Could not read uploaded file: {e}")
        st.info("Falling back to sample data.")
        df = load_sample_data()
else:
    st.info("No file uploaded — showing sample data")
    df = load_sample_data()

if df.empty:
    st.warning("No records available.")
    st.stop()

# =========================
# SIDEBAR FILTERS
# =========================
with st.sidebar:
    st.header("🎛️ Controls & Filters")

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    date_range = st.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    categories = ["All"] + sorted(df["category"].dropna().unique().tolist())
    selected_category = st.selectbox("Filter by Category", categories)

filtered_df = apply_filters(df, start_date, end_date, selected_category)
metrics = calculate_metrics(filtered_df)

# =========================
# KPI ROW
# =========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Spent", f"${metrics['total_spent']:,.2f}")

with col2:
    st.metric("Monthly Average", f"${metrics['monthly_avg']:,.2f}")

with col3:
    st.metric("Average Transaction", f"${metrics['avg_transaction']:,.2f}")

with col4:
    change_pct = spending_change_pct(filtered_df)
    st.metric(
        "Trend Change",
        f"{abs(change_pct):.1f}%",
        delta=f"{'↑' if change_pct > 0 else '↓'}",
    )

st.divider()

# =========================
# QUICK STATS
# =========================
with st.sidebar:
    st.subheader("📊 Quick Stats")
    st.metric("Total Transactions", f"{metrics['num_transactions']:,}")
    st.metric("Average Daily Spend", f"${metrics['avg_daily']:.2f}")
    st.metric("Top Category", metrics["top_category"])

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Overview", "🏷️ Category Analysis", "📅 Trends & Patterns", "🔮 Forecast", "💡 Insights"]
)

with tab1:
    left, right = st.columns([1.5, 1])

    with left:
        st.plotly_chart(create_monthly_trend(filtered_df), use_container_width=True)

    with right:
        st.plotly_chart(create_category_comparison(filtered_df), use_container_width=True)

with tab2:
    left, right = st.columns(2)

    with left:
        pie_fig, category_data = create_spending_by_category(filtered_df)
        st.plotly_chart(pie_fig, use_container_width=True)

    with right:
        st.subheader("Category Breakdown")
        table_df = category_data.copy()
        table_df["% of Total"] = (table_df["sum"] / table_df["sum"].sum() * 100).round(1)
        st.dataframe(
            table_df[["sum", "count", "mean", "% of Total"]].rename(
                columns={
                    "sum": "Total ($)",
                    "count": "Transactions",
                    "mean": "Avg ($)",
                }
            ),
            use_container_width=True,
        )

with tab3:
    st.plotly_chart(create_category_trends(filtered_df), use_container_width=True)
    st.plotly_chart(create_daily_heatmap(filtered_df), use_container_width=True)

with tab4:
    left, right = st.columns([2, 1])

    with left:
        forecast_months = st.slider("Forecast Months Ahead", 1, 12, 3)
        forecast_values = forecast_spending(filtered_df, forecast_months)

        monthly_hist = filtered_df.groupby("year_month")["amount"].sum()
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=monthly_hist.index,
                y=monthly_hist.values,
                mode="lines+markers",
                name="Historical",
            )
        )

        if forecast_values:
            last_date = filtered_df["date"].max()
            future_labels = [
                str((pd.Timestamp(last_date) + pd.DateOffset(months=i)).to_period("M"))
                for i in range(1, forecast_months + 1)
            ]

            fig.add_trace(
                go.Scatter(
                    x=future_labels,
                    y=forecast_values,
                    mode="lines+markers",
                    name="Forecast",
                    line=dict(dash="dash"),
                )
            )

        fig.update_layout(
            title="Spending Forecast",
            xaxis_title="Month",
            yaxis_title="Spending ($)",
            hovermode="x unified",
            height=450,
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Forecast Summary")
        for i, value in enumerate(forecast_values, start=1):
            st.metric(f"Month +{i}", f"${value:,.0f}")

with tab5:
    left, right = st.columns(2)

    with left:
        st.subheader("🎯 Key Insights")
        for insight in build_insights(filtered_df):
            st.info(insight)

        if not filtered_df.empty:
            category_std = filtered_df.groupby("category")["amount"].std().dropna()
            if not category_std.empty:
                most_variable = category_std.idxmax()
                st.warning(f"Most variable category is **{most_variable}**.")

    with right:
        st.subheader("💡 Recommendations")

        total = filtered_df["amount"].sum()
        category_totals = filtered_df.groupby("category")["amount"].sum()

        if total > 0 and "Dining Out" in category_totals.index:
            dining_pct = (category_totals["Dining Out"] / total) * 100
            if dining_pct > 15:
                st.success("Cutting Dining Out modestly could unlock meaningful savings.")

        if "Shopping" in category_totals.index:
            st.success("Review Shopping purchases for one-time vs recurring spend.")

        if "Healthcare" in category_totals.index:
            st.success("Review Healthcare expenses for FSA/HSA reimbursement opportunities.")

        recent_cutoff = filtered_df["date"].max() - timedelta(days=90)
        first_cutoff = filtered_df["date"].min() + timedelta(days=90)

        first_period = filtered_df[filtered_df["date"] <= first_cutoff]["amount"].mean()
        recent_period = filtered_df[filtered_df["date"] >= recent_cutoff]["amount"].mean()

        if pd.notna(first_period) and pd.notna(recent_period):
            if recent_period > first_period * 1.1:
                st.warning("Recent spending is trending upward. Review budget allocations.")
            else:
                st.info("Spending appears relatively stable over the selected period.")

st.divider()

# =========================
# EXPORTS
# =========================
with st.expander("📥 Export Data"):
    col1, col2 = st.columns(2)

    with col1:
        csv_full = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Filtered Dataset (CSV)",
            data=csv_full,
            file_name="budget_analysis.csv",
            mime="text/csv",
        )

    with col2:
        summary = pd.DataFrame(
            {
                "Metric": [
                    "Total Spent",
                    "Monthly Average",
                    "Transactions",
                    "Categories",
                ],
                "Value": [
                    f"${metrics['total_spent']:.2f}",
                    f"${metrics['monthly_avg']:.2f}",
                    metrics["num_transactions"],
                    filtered_df["category"].nunique(),
                ],
            }
        )

        csv_summary = summary.to_csv(index=False)
        st.download_button(
            label="Download Summary Report (CSV)",
            data=csv_summary,
            file_name="budget_summary.csv",
            mime="text/csv",
        )

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #999; font-size: 12px;'>
        <p>Family Budget Intelligence Dashboard | Built with Streamlit & Plotly</p>
        <p>Data-driven insights for smarter financial decisions</p>
    </div>
    """,
    unsafe_allow_html=True,
)