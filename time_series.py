import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title = "Google Play Store - Time Series",
    page_icon = "📈",
    layout = "wide"
)

st.markdown(
    """
    <style>
    .main {
    background-color: #0f172a;
    }
    .title {
    font-size : 38px;
    font-weight : bold;
    color: black;
    text-align: center;
    margin-bottom: 5px;
    }
    .subtitle {
    font-size: 17px;
    color: #cbd5e1;
    text-align: center;
    margin-bottom: 30px;
    }
    .metric-box {
    background-color: #1e293b;
    padding: 18px;
    border-radius: 12px;
    text-align: center;
    border: 1px solid #334155;
    }
    .metric-title {
    color: #94a3b8;
    font-size: 14px;
    }
    .metric-value {
    color: white;
    font-size: 26px;
    font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html = True
)

st.markdown(
    '<div class="title">📈 Google Play Store Time Series Analysis</div>',
    unsafe_allow_html = True
)
st.markdown(
    '<div class = "subtitle">Monthly Install Trends and Growth Analysis</div>',
    unsafe_allow_html = True
)

india_time = datetime.now(ZoneInfo("Asia/Kolkata"))
current_hour = india_time.hour
if not (18 <= current_hour < 21):
    st.warning(
        "🔒 Analytics Currently Unavailable\n\n"
        "📊 This graph is available only between "
        "**6:00 PM to 9:00 PM IST**.\n\n"
        "Please check again during the allowed time window."
    )
    st.info(
        f"Current IST time: {india_time.strftime('%I %M %p')}"
    )
    st.stop()

try:
    df = pd.read_csv("googleplaystore.csv")
except FileNotFoundError:
    st.error(
        "❌ googleplaystore.csv was not found.\n\n"
        "Please keep the CSV file in the same folder as time_series.py."
    )
    st.stop()

required_columns = [
    "App",
    "Category",
    "Reviews",
    "Installs",
    "Last Updated"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]
if missing_columns:
    st.error(
        "❌ Missing columns in dataset: "
        + ",".join(missing_columns)
    )
    st.write("Available columns: ")
    st.write(df.columns.tolist())
    st.stop()

df = df.copy()

df["App"] = df["App"].astypeI(str).str.strip()

df["Category"] = (
    df["Category"]
    .astype(str)
    .str.strip()
    .str.upper()
)

df["Reviews"] = (
    df['Reviews']
    .astype(str)
    .str.replace(",", "", regex = False)
    
)

df["Reviews"] = pd.to_numeric(
    df["Reviews"],
    errors = "coerce"
)

df["Installs"] = (
    df["Installs"]
    .astype(str)
    .str.replace(",", "", regex = False)
    .str.replace("+", "", regex = False)
)

df["Installs"] = pd.to_numeric(
    df["Installs"],
    errors = "coerce"
)

df["Last Updated"] = pd.to_datetime(
    df["Last Updated"],
    errors = "coerce"
)

df = df.dropna(
    subset = [
        "App",
        "Category",
        "Reviews",
        "Installs",
        "Last Updated"
    ]
)

filtered_df = df[
    (df["Reviews"] > 500)
    &
    (~df["App"].str.lower().str.startswith(("x", "y", "z")))
    &
    (~df["App"].str.lower().str.contains("s", regex = False))
    &
    (df["Category"].str.startswith(("E", "C", "B")))
].copy()

category_translation = {
    "BEAUTY": "सुंदरता",
    "BUSINESS": "வணிகம்",
    "DATING": "Dating"
}

filtered_df["Category_Display"] = (
    filtered_df["Category"]
    .replace(category_translation)
)

filtered_df["Month"] = (
    filtered_df["Last Updated"]
    .dt.to_period("M")
    .dt.to_timestamp()
)

if filtered_df.empty:
    st.warning(
        "⚠️ No data is avaliable after applying all the required filters."
    )
    st.write("Filters applied:")
    st.write("• Reviews > 500")
    st.write("• App name does not start with X, Y or Z")
    st.write("• App name does not contain letter S")
    st.write("• Category starts with B, C or E")
    st.stop()

monthly_data = (
    filtered_df
    .groupby(
        ["Month", "Category_Display"],
        as_index = False
    )
    .agg(
        Installs = ("Installs", "sum")
    )
)

monthly_data = monthly_data.sort_values(
    by = ["Category_Display", "Month"]
).reset_index(drop=True)

monthly_data["MoM_Growth"] = (
    monthly_data
    .groupby("Category_Display")["Installs"]
    .pct_change()
    *100
)

st.success(
    f"✅ {len(filtered_df):,} apps matched the required filters."
)

total_apps = filtered_df["App"].nunique()

total_installs = filtered_df["Installs"].sum()

categories_count = filtered_df["Category_Display"].nunique()

growth_periods = (
    monthly_data["MoM_Growth"] > 20
).sum()


col1, col2, col3, col4 = st.columns(4)


with col1:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-title">Filtered Apps</div>
            <div class="metric-value">{total_apps:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-title">Total Installs</div>
            <div class="metric-value">{total_installs:,.0f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-title">Categories</div>
            <div class="metric-value">{categories_count}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col4:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-title">Growth > 20%</div>
            <div class="metric-value">{growth_periods}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown("<br>", unsafe_allow_html=True)


fig = go.Figure()

categories = monthly_data[
    "Category_Display"
].dropna().unique()

for category in categories:

    category_df = monthly_data[
        monthly_data["Category_Display"] == category
    ].copy()

    category_df = category_df.sort_values("Month")


    fig.add_trace(
        go.Scatter(
            x=category_df["Month"],
            y=category_df["Installs"],
            mode="lines+markers",
            name=str(category),

            hovertemplate=
            "<b>Category:</b> %{fullData.name}<br>"
            "<b>Month:</b> %{x|%b %Y}<br>"
            "<b>Installs:</b> %{y:,.0f}<br>"
            "<extra></extra>"
        )
    )



    growth_df = category_df[
        category_df["MoM_Growth"] > 20
    ].copy()


    for _, row in growth_df.iterrows():

        month = row["Month"]
        installs = row["Installs"]

        fig.add_vrect(
            x0=month,
            x1=month + pd.DateOffset(months=1),

            fillcolor="green",
            opacity=0.12,

            line_width=0,

            layer="below"
        )


fig.update_layout(

    title={
        "text":
        "📊 Monthly Total Installs by App Category",
        "x": 0.5,
        "xanchor": "center"
    },

    xaxis_title="Month",

    yaxis_title="Total Installs",

    template="plotly_dark",

    height=650,

    hovermode="x unified",

    legend={
        "title": {
            "text": "App Category"
        },
        "orientation": "h",
        "yanchor": "bottom",
        "y": 1.02,
        "xanchor": "center",
        "x": 0.5
    },

    margin={
        "l": 70,
        "r": 40,
        "t": 100,
        "b": 70
    }
)

fig.update_xaxes(
    showgrid=True,
    tickformat="%b %Y",
    tickangle=-45
)


fig.update_yaxes(
    showgrid=True,
    tickformat=","
)


st.plotly_chart(
    fig,
    use_container_width=True
)


st.info(
    "🟢 **Green shaded regions** indicate periods where "
    "monthly installs increased by more than **20% compared "
    "with the previous month**."
)

st.markdown("### 🌐 Category Translation")

st.write(
    "Beauty → सुंदरता"
)

st.write(
    "Business → வணிகம்"
)

st.write(
    "Note: Dating is not included because the required "
    "category filter allows only categories starting with "
    "B, C, or E."
)


with st.expander("🔎 Applied Filters"):

    st.write(
        "✔ Reviews greater than 500"
    )

    st.write(
        "✔ App name does not start with X, Y, or Z"
    )

    st.write(
        "✔ App name does not contain the letter S"
    )

    st.write(
        "✔ Category starts with B, C, or E"
    )

    st.write(
        "✔ Monthly total installs calculated"
    )

    st.write(
        "✔ Periods with MoM growth greater than 20% highlighted"
    )

st.caption(
    f"🕒 Current IST Time: "
    f"{india_time.strftime('%d %B %Y, %I:%M %p')}"
)
