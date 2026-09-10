import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time
from zoneinfo import ZoneInfo

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Google Play Store",
    page_icon="📱",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown("""
<style>
div[data-testid="stMetric"] {
    background: white;
    border-radius: 20px;
    padding: 20px;
    border: 1px solid #E0E7FF;
    box-shadow: 0px 8px 25px rgba(49, 46, 129, 0.12);
}

div[data-testid="stMetricLabel"] {
    color: #475569 !important;
}

div[data-testid="stMetricValue"] {
    color: #312E81 !important;
    font-weight: 800 !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("googleplaystore.csv")


df = load_data()

# --------------------------------------------------
# DATA CLEANING
# --------------------------------------------------
df = df.drop_duplicates()

df.columns = df.columns.str.strip()

df["Rating"] = pd.to_numeric(
    df["Rating"],
    errors="coerce"
)

df["Reviews"] = pd.to_numeric(
    df["Reviews"],
    errors="coerce"
)

# Clean installs
df["Installs_Clean"] = (
    df["Installs"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace("+", "", regex=False)
    .str.strip()
)

df["Installs_Clean"] = pd.to_numeric(
    df["Installs_Clean"],
    errors="coerce"
)

# --------------------------------------------------
# CONVERT SIZE TO MB
# --------------------------------------------------
def convert_size(size):
    size = str(size).strip()

    if size == "Varies with device":
        return None

    try:
        if size.endswith("M"):
            return float(size[:-1])

        elif size.endswith("k"):
            return float(size[:-1]) / 1024

        else:
            return None

    except:
        return None


df["Size_MB"] = df["Size"].apply(convert_size)

# --------------------------------------------------
# DATE CONVERSION
# --------------------------------------------------
df["Last Updated"] = pd.to_datetime(
    df["Last Updated"],
    errors="coerce"
)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.title("🔍 Dashboard Filters")

st.sidebar.info(
    "The assignment filters are automatically applied."
)

st.sidebar.write("⭐ Minimum Rating: **4.0**")
st.sidebar.write("💾 Minimum Size: **10 MB**")
st.sidebar.write("📅 Update Month: **January**")
st.sidebar.write("🏆 Categories: **Top 10 by Installs**")

# --------------------------------------------------
# TITLE
# --------------------------------------------------
st.title("📱 Google Play Store Dashboard")

st.markdown(
    "## Top App Categories Analysis Based on Installs, Ratings and Reviews"
)

st.divider()

# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------
filtered_df = df[
    (df["Rating"] >= 4.0)
    & (df["Size_MB"] >= 10)
    & (df["Last Updated"].dt.month == 1)
].copy()

filtered_df = filtered_df.dropna(
    subset=["Installs_Clean"]
)

# --------------------------------------------------
# CATEGORY ANALYSIS
# --------------------------------------------------
category_data = (
    filtered_df
    .groupby("Category")
    .agg(
        Total_Installs=("Installs_Clean", "sum"),
        Average_Rating=("Rating", "mean"),
        Total_Reviews=("Reviews", "sum"),
        Total_Apps=("App", "count")
    )
    .reset_index()
)

# --------------------------------------------------
# TOP 10 CATEGORIES
# --------------------------------------------------
top_10 = (
    category_data
    .sort_values(
        "Total_Installs",
        ascending=False
    )
    .head(10)
)

# --------------------------------------------------
# DASHBOARD METRICS
# --------------------------------------------------
st.subheader("📊 Dashboard Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "📱 Total Apps",
    f"{len(df):,}"
)

col2.metric(
    "✅ Filtered Apps",
    f"{len(filtered_df):,}"
)

col3.metric(
    "📂 Categories",
    f"{len(category_data):,}"
)

col4.metric(
    "⬇️ Total Installs",
    f"{filtered_df['Installs_Clean'].sum():,.0f}"
)

st.divider()

# --------------------------------------------------
# IST TIME
# --------------------------------------------------
ist = ZoneInfo("Asia/Kolkata")

current_datetime = datetime.now(ist)
current_time = current_datetime.time()

start_time = time(15, 0)
end_time = time(17, 0)

# --------------------------------------------------
# CHART SECTION
# --------------------------------------------------
st.subheader("📈 Category Performance Analysis")

time_col1, time_col2 = st.columns(2)

time_col1.info(
    "🕒 Current IST Time: "
    + current_datetime.strftime("%I:%M:%S %p")
)

time_col2.info(
    "⏰ Chart Availability: 3:00 PM – 5:00 PM IST"
)

# --------------------------------------------------
# CHECK TIME
# --------------------------------------------------
if start_time <= current_time <= end_time:

    st.success(
        "🟢 Chart is currently available"
    )

    # --------------------------------------------------
    # CREATE FIGURE
    # --------------------------------------------------
    fig = go.Figure()

    # Average Rating Bar
    fig.add_trace(
        go.Bar(
            x=top_10["Category"],
            y=top_10["Average_Rating"],
            name="Average Rating",
            yaxis="y"
        )
    )

    # Total Reviews Bar
    fig.add_trace(
        go.Bar(
            x=top_10["Category"],
            y=top_10["Total_Reviews"],
            name="Total Reviews",
            yaxis="y2"
        )
    )

    # --------------------------------------------------
    # CHART LAYOUT
    # --------------------------------------------------
    fig.update_layout(
        title="Average Rating vs Total Review Count",

        barmode="group",

        xaxis=dict(
            title="App Category",
            tickangle=-30
        ),

        yaxis=dict(
            title="Average Rating",
            range=[0, 5.5]
        ),

        yaxis2=dict(
            title="Total Reviews",
            overlaying="y",
            side="right",
            showgrid=False
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),

        height=600,

        margin=dict(
            l=60,
            r=60,
            t=100,
            b=100
        )
    )

    # --------------------------------------------------
    # DISPLAY CHART
    # --------------------------------------------------
    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # TOP 10 TABLE
    # --------------------------------------------------
    st.subheader(
        "📋 Top 10 Categories Details"
    )

    display_data = top_10.copy()

    display_data["Total_Installs"] = (
        display_data["Total_Installs"]
        .apply(lambda x: f"{x:,.0f}")
    )

    display_data["Average_Rating"] = (
        display_data["Average_Rating"]
        .round(2)
    )

    display_data["Total_Reviews"] = (
        display_data["Total_Reviews"]
        .apply(lambda x: f"{x:,.0f}")
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------
# CHART NOT AVAILABLE
# --------------------------------------------------
else:

    st.warning(
        "🔒 Category Performance Chart is Currently Unavailable."
    )

    st.error(
        "This graph can only be viewed between "
        "3:00 PM and 5:00 PM IST."
    )

    st.caption(
        "Please visit the dashboard during the allowed time."
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()

st.caption(
    "Google Play Store Analytics Dashboard | Internship Project"
)
