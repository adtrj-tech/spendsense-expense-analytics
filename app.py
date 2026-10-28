from anomaly_detection import flag_unusual_transactions
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------- Configuration ----------

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_FILE = BASE_DIR / "data" / "sample_expenses.csv"
CSS_FILE = BASE_DIR / "styles.css"

REQUIRED_COLUMNS = [
    "date",
    "description",
    "category",
    "amount",
    "payment_method",
]

st.set_page_config(
    page_title="SpendSense | Expense Intelligence",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Load external CSS ----------

if CSS_FILE.exists():
    st.markdown(
        f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )
else:
    st.warning("styles.css was not found. Using default styling.")

# ---------- Helpers ----------

def load_csv(file):
    """Read a CSV and normalize its column names."""
    df = pd.read_csv(file)
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
    )
    return df


def validate_expenses(df):
    """Return a cleaned DataFrame and validation errors."""
    missing = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing:
        return None, [
            "Missing columns: " + ", ".join(missing)
        ]

    if df.empty:
        return None, ["The CSV contains no transactions."]

    df = df.copy()

    df["date"] = pd.to_datetime(
        df["date"], errors="coerce"
    )
    df["amount"] = pd.to_numeric(
        df["amount"], errors="coerce"
    )

    text_columns = [
        "description",
        "category",
        "payment_method",
    ]

    for col in text_columns:
        df[col] = df[col].astype("string").str.strip()
        df[col] = df[col].replace("", pd.NA)

    invalid = (
        df["date"].isna()
        | df["amount"].isna()
        | (df["amount"] <= 0)
        | df[text_columns].isna().any(axis=1)
    )

    if invalid.any():
        return df.loc[invalid], [
            f"{int(invalid.sum())} invalid transaction(s) found."
        ]

    return df.sort_values("date").copy(), []


def money(value):
    """Format an amount in Indian rupees."""
    return f"₹{value:,.2f}"


# ---------- Sidebar ----------

with st.sidebar:
    st.markdown(
        '<div class="brand">'
        '<span class="brand-mark">₹</span>'
        '<span>SpendSense</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.caption("PERSONAL FINANCE INTELLIGENCE")
    st.divider()

    st.markdown("### Your data")

    source = st.radio(
        "Data source",
        ["Sample expenses", "Upload a CSV"],
    )

    uploaded_file = None

    if source == "Upload a CSV":
        uploaded_file = st.file_uploader(
            "Choose your expense file",
            type=["csv"],
            help=(
                "Required columns: date, description, "
                "category, amount, payment_method."
            ),
        )

    st.divider()

    st.caption("ABOUT SPENDSENSE")
    st.caption(
        "A personal finance analytics project that "
        "turns transaction data into useful insights."
    )
    st.caption(
        "Use fictional or anonymized data during development."
    )

# ---------- Page header ----------

st.markdown(
    """
    <div style="
        color: #5B3FD6;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 2px;
        line-height: 1.8;
        opacity: 1;
        margin-bottom: 10px;
    ">
        YOUR MONEY, MADE CLEARER
    </div>
    """,
    unsafe_allow_html=True,
)
st.title("Expense overview")
st.markdown(
    '<div class="page-subtitle">'
    "Understand your spending, discover patterns, "
    "and make informed decisions."
    "</div>",
    unsafe_allow_html=True,
)

# ---------- Read data ----------

df = None

try:
    if source == "Sample expenses":
        if not SAMPLE_FILE.exists():
            st.error(
                "Sample data not found. Check "
                "data/sample_expenses.csv."
            )
            st.stop()

        raw_df = load_csv(SAMPLE_FILE)

    elif uploaded_file is not None:
        raw_df = load_csv(uploaded_file)

    else:
        st.info(
            "Choose Sample expenses or upload a CSV "
            "from the sidebar to get started."
        )
        st.stop()

except (
    pd.errors.ParserError,
    UnicodeDecodeError,
    ValueError,
) as exc:
    st.error(f"Could not read the CSV file: {exc}")
    st.stop()

# ---------- Validate data ----------

validated_df, errors = validate_expenses(raw_df)

if errors:
    st.error("Your data needs attention before analysis.")
    st.write(errors[0])

    if validated_df is not None:
        st.dataframe(
            validated_df,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption(
            "Check the required columns and file format."
        )

    st.stop()

df = validated_df

st.success(
    f"Data validated successfully · {len(df):,} transactions"
)

# ---------- Filters ----------

st.markdown("### Spending overview")

filter_col1, filter_col2 = st.columns([1, 1])

with filter_col1:
    categories = sorted(df["category"].unique().tolist())

    selected_categories = st.multiselect(
        "Filter categories",
        options=categories,
        default=categories,
    )

with filter_col2:
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    date_range = st.date_input(
        "Transaction date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

filtered = df[df["category"].isin(selected_categories)].copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        filtered["date"].dt.date.between(start_date, end_date)
    ]

if filtered.empty:
    st.warning("No transactions match the selected filters.")
    st.stop()

# ---------- Summary cards ----------

total = filtered["amount"].sum()
count = len(filtered)
average = filtered["amount"].mean()

category_totals = (
    filtered.groupby("category")["amount"]
    .sum()
    .sort_values(ascending=False)
)

top_category = category_totals.index[0]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total expenses", money(total))

with col2:
    st.metric("Transactions", f"{count:,}")

with col3:
    st.metric("Average transaction", money(average))

with col4:
    st.metric("Top category", top_category)

# ---------- Charts ----------

st.markdown("### Understand your spending")

left, right = st.columns(2, gap="large")

with left:
    st.markdown(
        '<div class="section-heading">Spending by category</div>'
        '<div class="section-caption">'
        "Which categories account for the most spending?"
        "</div>",
        unsafe_allow_html=True,
    )

    chart_data = (
        category_totals.rename("amount")
        .reset_index()
        .sort_values("amount", ascending=True)
    )

    fig_category = px.bar(
        chart_data,
        x="amount",
        y="category",
        orientation="h",
        text="amount",
        labels={"amount": "Amount (₹)", "category": ""},
        color_discrete_sequence=["#7057E8"],
    )

    fig_category.update_traces(
        texttemplate="₹%{text:,.0f}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{y}<br>₹%{x:,.2f}<extra></extra>",
    )

    fig_category.update_layout(
    height=360,
    autosize=True,
    margin=dict(l=10, r=35, t=15, b=35),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(family="Arial", color="#19213A"),
    showlegend=False,
    xaxis=dict(
        showgrid=True,
        gridcolor="#E9ECF4",
        zeroline=False,
    ),
    yaxis=dict(showgrid=False),
    )

    st.plotly_chart(
    fig_category,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "responsive": True,
    },
    key="category_chart",
    )

with right:
    st.markdown(
        '<div class="section-heading">Daily spending trend</div>'
        '<div class="section-caption">'
        "See how your expenses change over time."
        "</div>",
        unsafe_allow_html=True,
    )

    daily = (
        filtered.groupby("date", as_index=False)["amount"]
        .sum()
        .sort_values("date")
    )

    fig_trend = px.line(
        daily,
        x="date",
        y="amount",
        markers=True,
        labels={"date": "Date", "amount": "Amount (₹)"},
    )

    fig_trend.update_traces(
        line_color="#7057E8",
        line_width=3,
        marker_size=7,
        hovertemplate="%{x|%d %b %Y}<br>₹%{y:,.2f}<extra></extra>",
    )

    fig_trend.update_layout(
    height=360,
    autosize=True,
    margin=dict(l=15, r=15, t=15, b=35),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(family="Arial", color="#19213A"),
    showlegend=False,
    xaxis=dict(
        showgrid=False,
        range=[
            daily["date"].min(),
            daily["date"].max(),
        ],
        tickformat="%b %d",
        automargin=True,
    ),
    yaxis=dict(
        title="Amount (₹)",
        showgrid=True,
        gridcolor="#E9ECF4",
        zeroline=False,
        automargin=True,
    ),
    )

    st.plotly_chart(
    fig_trend,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "responsive": True,
    },
    key="daily_trend_chart",
    )

# ---------- Unusual spending detection ----------

st.markdown("### Unusual spending detection")

st.caption(
    "Statistical screening identifies unusually high amounts "
    "for review. A flag does not mean fraud or an error."
)

try:
    anomaly_df = flag_unusual_transactions(filtered)

    flagged = anomaly_df[anomaly_df["is_unusual"]].copy()

    if flagged.empty:
        st.success(
            "No unusually high transactions were detected "
            "using the current IQR threshold."
        )
    else:
        st.warning(
            f"{len(flagged)} transaction(s) flagged for review."
        )

        st.dataframe(
            flagged[
                    [
                        "date",
                        "description",
                        "category",
                        "anomaly_scope",
                        "amount",
                        "anomaly_threshold",
                        "anomaly_reason",
                    ]
            ].sort_values("amount", ascending=False),
            use_container_width=True,
            hide_index=True,
        )

    with st.expander("How does this detection work?"):
        st.write(
            "SpendSense calculates the 25th percentile (Q1) "
            "and 75th percentile (Q3) of the selected transaction "
            "amounts. It flags amounts above Q3 + 1.5 × IQR, "
            "where IQR = Q3 − Q1."
        )
        st.write(
            "This is a statistical baseline. It does not establish "
            "fraud, financial risk, or whether a purchase was "
            "unexpected for the user."
        )

except ValueError as exc:
    st.info(str(exc))

# ---------- Transactions ----------

st.markdown("### Recent transactions")
st.caption(
    "Review your filtered transactions and export the records."
)

display_df = filtered.sort_values(
    "date", ascending=False
).copy()

display_df["date"] = display_df["date"].dt.strftime("%d %b %Y")
display_df["amount"] = display_df["amount"].map(money)

st.dataframe(
    display_df[
        [
            "date",
            "description",
            "category",
            "amount",
            "payment_method",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    "Download filtered transactions",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="spendsense_transactions.csv",
    mime="text/csv",
)

# ---------- Footer ----------

st.markdown(
    '<div class="app-footer">'
    "SpendSense · Personal finance analytics · "
    "Results reflect the transactions provided."
    "</div>",
    unsafe_allow_html=True,
)
