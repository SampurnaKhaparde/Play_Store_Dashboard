import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="Google Play Store Bubble Chart",
    page_icon = "📱",
    layout = "wide"
)
india_time = datetime.now(ZoneInfo("Asia/Kolkata"))
current_time = india_time.time()

start_time = datetime.strptime("22:00", "%H:%M").time()
end_time = datetime.strptime("23:00", "%H:%M").time()

if not (start_time <= current_time <= end_time):
    st.warning(
        f"⏰ Bubble chart is available only 5:00 PM to 7:00 PM IST.\n\n"
        f"Current IST time: {india_time.strftime('%I:%M %p')}"
    )
    st.stop()

st.title("📱 Google Play Store Analytics")
st.subheader("🎈 Interactive App Size vs Rating Bubble Chart")

try:
    df = pd.read_csv("googleplaystore.csv")
except FileNotFoundError:
    st.error("❌ googleplaystore.csv not found.")
    st.info("Put googleplaystore.csv in the same folder as bubble.py")
    st.stop()

required_columns = [
    "App",
    "Category",
    "Rating",
    "Reviews",
    "Size",
    "Installs"
]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    st.error(f"❌ Missing columns: {missing}")
    st.write("Available columns:")
    st.write(df.columns.tolist())
    st.stop()

df["Rating"] = pd.to_numeric(
    df["Rating"],
    errors="coerce"
)

df["Reviews"] = pd.to_numeric(
    df["Reviews"],
    errors="coerce"
)

df["Installs"] = (
    df["Installs"]
    .astype(str)
    .str.replace(",", "", regex = False)
    .str.replace("+", "", regex = False)
)

df["Installs"] = pd.to_numeric(
    df["Installs"],
    errors="coerce"
)

def convert_size(value):
    if pd.isna(value):
        return None
    value = str(value).strip()
    if value == "Varies with device":
        return None

    try:
        if value.endswith("M"):
            return float(value[:-1])
        elif value.endswith("k"):
            return float(value[:-1])/1024
        elif value.endswith("K"):
            return float(value[:-1])/1024
        elif value.endswith("G"):
            return float(value[:-1])*1024
        else:
            return float(value)

    except:
        return None

df["Size_MB"] = df["Size"].apply(convert_size)
df["Category"] = df["Category"].replace(
    "EVENTS",
    "Events"
)

df = df.dropna(
    subset=[
        "Rating",
        "Reviews",
        "Installs",
        "Size_MB"
    ]
)

bubble_df = df[
    (df["Rating"] > 3.5)&
    (df["Reviews"] > 500)&
    (df["Installs"] > 50000)&
    (~df["App"].astype(str).str.contains("S", case= False, na= False))
]

categories = [
    "GAME",
    "BEAUTY",
    "BUSINESS",
    "COMICS",
    "COMMUNICATION",
    "DATING",
    "ENTERTAINMENT",
    "SOCIAL",
    "EVENTS"
]

bubble_df = bubble_df[
    bubble_df["Category"].isin(categories)
]

if bubble_df.empty:
    st.warning(
        "⚠️ No apps match all the required filters."
    )
    st.write("Nimber of rows after filtering:", len(bubble_df))
    st.info(
        "Try reducing the filters or check your dataset."
    )
    st.stop()

translation = {
    "BEAUTY": "सौंदर्य",
    "BUSINESS": "வணிகம்",
    "DATING": "Partnersuche",
    "GAME": "Game",
    "COMICS": "Comics",
    "COMMUNICATION": "Communication",
    "ENTERTAINMENT": "Entertainment",
    "SOCIAL": "Social",
    "EVENTS": "Events"
}

bubble_df["Category_Display"] = (
    bubble_df["Category"]
    .map(translation)
    .fillna(bubble_df["Category"])
)

st.sidebar.header("🎛️ Filters")
selected_categories = st.sidebar.multiselect(
    "Select Categories",
    options= categories,
    default= categories
)

min_rating = st.sidebar.slider(
    "Minimum Rating",
    3.5,
    5.0,
    3.5,
    0.1
)

min_reviews = st.sidebar.number_input(
    "Minimum Reviews",
    min_value= 0,
    value= 500
)

min_installs = st.sidebar.number_input(
    "Minimum Installs",
    min_value= 0,
    value= 50000
)

bubble_df = bubble_df[
    bubble_df["Category"].isin(selected_categories)
]
bubble_df = bubble_df[
    bubble_df["Rating"] >= min_rating
]
bubble_df = bubble_df[
    bubble_df["Reviews"] >= min_reviews
]
bubble_df = bubble_df[
    bubble_df["Installs"] >= min_installs
]

if bubble_df.empty:
    st.warning(
        "⚠️ No data available for the selected filters."
    )
    st.stop()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "📱 Apps",
    len(bubble_df)
)
col2.metric(
    "⭐ Avg Rating",
    round(bubble_df["Rating"].mean(), 2)
)
col3.metric(
    "📥 Total Installs",
    f"{bubble_df["Installs"].sum():,.0f}"
)
col4.metric(
    "💬 Reviews",
    f"{bubble_df['Reviews'].sum():,.0f}"
)

fig = px.scatter(
    bubble_df,
    x = "Size_MB",
    y = "Rating",
    size = "Installs",
    color = "Category_Display",
    hover_name= "App",
    hover_data={
        "Size_MB": ":.2f",
        "Rating": ":.2f",
        "Reviews": ":,",
        "Installs": ":,",
        "Category_Display": True
    },
    size_max = 60,
    title="🎈 App Size vs Rating - Bubble Size = Installs"
)

for trace in fig.data:
    if trace.name == "Game":
        trace.marker.color = "#4260f5"
        trace.marker.line.color = "white"
        trace.marker.line.width = 2

fig.update_layout(
    template = "plotly_dark",
    height = 650,
    title = {
        "x": 0.5,
        "font": {
            "size": 24
        }
    },
    xaxis_title = "📦 App Size (MB)",
    yaxis_title = "⭐ Average Rating",
    legend_title = "📂 Category",
    hovermode = "closest"
)
fig.update_xaxes(
    showgrid = True
)
fig.update_yaxes(
    range = [3.4, 5.1],
    showgrid = True
)

st.plotly_chart(
    fig,
    use_container_width= True
)

with st.expander("📊 View Filtered Data"):
    st.dataframe(
        bubble_df[
            [
                "App",
                "Category_Display",
                "Rating",
                "Reviews",
                "Installs",
                "Size_MB"
            ]
        ],
        use_container_width = True
    )

st.markdown("---")

st.caption(
    f"🕒 Current IST Time: {india_time.strftime('%I:%M:%S %p')} | "
    "Chart available from 5:00 PM to 7:00 PM IST"
)
