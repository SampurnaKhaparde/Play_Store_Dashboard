import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title = "Global App Install Analytics",
    layout = "wide",
    initial_sidebar_state = "expanded"
)

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(
            circle at top left,
            #e0e7ff 0%,
            #f8fafc 35%,
            #eef2ff 70%,
            #f8fafc 100%
        );
}


.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.hero {
    background:
        linear-gradient(
            135deg,
            #172554,
            #312e81,
            #4f46e5,
            #6366f1
        );

    padding: 32px;

    border-radius: 25px;

    color: white;

    margin-bottom: 25px;

    box-shadow:
        0 15px 40px rgba(49,46,129,0.25);
}

.hero h1 {
    font-size: 42px;
    font-weight: 800;
    margin: 0;
}

.hero p {
    font-size: 17px;
    margin-top: 8px;
    opacity: 0.9;
}

div[data-testid="stMetric"] {

    background: rgba(255,255,255,0.95);

    border-radius: 20px;

    padding: 20px;

    border: 1px solid #e2e8f0;

    box-shadow:
        0 8px 25px rgba(15,23,42,0.08);

    transition: all 0.25s ease;
}

div[data-testid="stMetric"]:hover {

    transform: translateY(-5px);

    box-shadow:
        0 15px 30px rgba(15,23,42,0.13);
}

div[data-testid="stMetricLabel"] {

    color: #64748b !important;

    font-weight: 600;
}

div[data-testid="stMetricValue"] {

    color: #312e81 !important;

    font-weight: 800;
}

.section-title {

    font-size: 25px;

    font-weight: 800;

    color: #1e293b;

    margin-top: 20px;

    margin-bottom: 15px;
}

.info-card {

    background: rgba(255,255,255,0.95);

    padding: 18px;

    border-radius: 18px;

    border: 1px solid #e2e8f0;

    box-shadow:
        0 6px 20px rgba(15,23,42,0.07);

    text-align: center;
}

.info-title {

    font-size: 13px;

    color: #64748b;

    font-weight: 600;
}

.info-value {

    font-size: 21px;

    color: #312e81;

    font-weight: 800;

    margin-top: 5px;
}

section[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            #eef2ff,
            #f8fafc
        );
}

.highlight {

    background:
        linear-gradient(
            135deg,
            #fff7ed,
            #ffedd5
        );

    border-left: 6px solid #f97316;

    padding: 17px;

    border-radius: 14px;

    margin: 15px 0;
}

.footer {

    text-align: center;

    color: #64748b;

    font-size: 13px;

    padding: 20px;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">

<h1>🌍 Global App Install Analytics</h1>

<p>
Interactive Choropleth Visualization • Top 5 Categories •
Install Threshold Analysis
</p>

</div>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("googleplaystore.csv")
    df = df.drop_duplicates()
    df.columns = df.columns.str.strip()

    df["Installs_Clean"] = (
        df["Installs"]
        .astype(str)
        .str.replace(",","", regex = False)
        .str.replace("+","", regex = False)
        .str.strip()
    )

    df["Installs_Clean"] = pd.to_numeric(
        df["Installs_Clean"],
        errors = "coerce"
    )

    df = df.dropna(
        subset = ["Category", "Installs_Clean"]
    )
    return df
df = load_data()

filtered_df = df[
    ~df["Category"]
    .astype(str)
    .str.upper()
    .str.startswith(
        ("A", "C", "G", "S")
    )
].copy()

category_data = (
    filtered_df
    .groupby(
        "Category",
        as_index = False
    )
    .agg(
        Total_Installs = (
            "Installs_Clean",
            "sum"
        ),
        Total_Apps = (
            "App",
            "count"
        )
    )
    .sort_values("Total_Installs", ascending = False)
)

top_5 = category_data.head(5).copy()

top_5["Threshold"] = top_5[
    "Total_Installs"
].apply(
    lambda x:
    "Above 1 Million"
    if x > 1_000_000
    else "Below 1 Million"
)

st.sidebar.markdown(
    "# 🎛️ Dashboard Controls"
)

selected_category = st.sidebar.selectbox(
    "📂 Select Category",
    top_5["Category"].tolist()
)

map_style= st.sidebar.selectbox(
    "🌍 Map Style",
    ["Natural Earth", "Mercator"]
)
chart_type = st.sidebar.selectbox(
    "📊 Comparison Chart",
    ["Bar Chart", "Donut Chart", "Treemap"]
)

show_table = st.sidebar.toggle(
    "📋 Show Data Table",
    value = True
)
st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📌 Filters Applied
🏆 Top 5 Categories
🚫 A / C / G / S removed
🔥 Install threshold: 1M+
🌍 Global visualization
🕕 Available: 6PM to 8PM IST """)

selected_row = top_5[
    top_5["Category"]== selected_category
].iloc[0]
selected_installs = selected_row["Total_Installs"]
selected_apps = selected_row["Total_Apps"]

st.markdown('<div class = "selection-title">📊 Key Performance Indicators</div>', unsafe_allow_html = True)
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("🏆 Top Categories", "5")
with c2:
    st.metric("📂 Selected Category", selected_category)
with c3:
    st.metric("⬇️ Total Installs", f"{selected_installs:,.0f}")
with c4:
    st.metric("📱 Total Apps", f"{selected_apps:,}")

ist = ZoneInfo("Asia/Kolkata")
now = datetime.now(ist)
current_time = now.time()
start_time = time(18, 0)
end_time = time (20, 0)

st.markdown('<div class= "section-title">⏰ Dashboard Availability</div>', unsafe_allow_html = True)

t1, t2, t3 = st.columns(3)
with t1:
    st.markdown(
        f"""
        <div class = "info-card">
        <div class = "info-title">
        Current IST Time
        </div>
        <div class = "info-value">
        {now.strftime('%I:%M:%S %p')}
        </div>
        </div>
        """,
        unsafe_allow_html = True
    )
with t2:
    st.markdown(
        """
        <div class = "info-card">
        <div class = "info-title">
        Available Time
        </div>
        <div class= = "info-value">
        6:00 PM - 8:00 PM
        </div>
        </div>
        """,
        unsafe_allow_html = True
    )
with t3:
    if start_time <= current_time < end_time:
        st.success(
            "🟢 Charts Active"
        )
    else:
        st.warning(
            "🔒 Charts Locked"
        )

if selected_installs > 1_000_000:
    st.markdown(
        f"""
        <div class = "highlight">
        <b>{selected_category}</b> exceeds the <b>1 Million Install</b> threshold.
        <br><br>
        Total Installs:
        <b>{selected_installs:,.0f}</b>
        </div>""",
        unsafe_allow_html = True
    )
else:
    st.info(
        f"ℹ️ {selected_category} has"
        f"{selected_installs:,.0f} installs"
    )

st.markdown('<div class = "selection-title"> 🌍 Global Category Map</div>', unsafe_allow_html = True)
st.caption("Interactive global visulization of the selected"
           "category. Hover over countries for details.")
world = pd.DataFrame({
    "Country": [
        "India",
        "United States",
        "United Kingdom",
        "Canada",
        "Australia",
        "Germany",
        "France",
        "Japan",
        "Brazil",
        "South Africa",
        "Italy",
        "Spain",
        "Mexico",
        "Singapore",
        "China",
        "Russia",
        "South Korea",
        "Indonesia",
        "Netherlands",
        "Switzerland"
    ],
    "IS03": [
        "IND",
        "USA",
        "GBR",
        "CAN",
        "AUS",
        "DEU",
        "FRA",
        "JPN",
        "BRA",
        "ZAF",
        "ITA",
        "ESP",
        "MEX",
        "SGP",
        "CHN",
        "RUS",
        "KOR",
        "IDN",
        "NLD",
        "CHE"
    ]
})

world["Category_Installs"] = selected_installs
world["Category"] = selected_category

projection = ("natural earth"
              if map_style == "Natural Earth"
              else "mercator")

fig_map = px.choropleth(
    world,
    locations = "IS03",
    locationmode = "ISO-3",
    color = "Category_Installs",
    hover_name = "Country",
    hover_data = {
        "IS03" : False,
        "Category" : True,
        "Category_Installs": ":,.0f"
    },
    color_continuous_scale = "Viridis",
    projection = projection,
    title = (
        f"🌍 Global Visualization -- "
        f"{selected_category}"
    )
)

fig_map.update_geos(
    showframe = False,
    showcoastlines = True,
    showcountries = True,
    coastlinecolor = "#64748b",
    countrycolor = "#cbd5e1",
    landcolor = "#e2e8f0",
    projection_type = projection

)

fig_map.update_layout(
    height = 620,
    margin = dict(
        l = 0,
        r = 0,
        t = 65,
        b = 0
    ),
    paper_bgcolor = "rgba(0,0 0,0)",
    plot_bgcolor = "rgba(0,0,0,0)",
    coloraxis_colorbar = dict(
        title = "Installs"
    )
)

st.plotly_chart(
    fig_map,
    use_container_width = True
)
left, right = st.columns(2)

with left:
    st.markdown(
        '<div class = "section-title">🏆 Top 5 Categories</div>',
        unsafe_allow_html = True
    )
    if chart_type == "Bar Chart":
        fig = px.bar(
            top_5,
            x = "Category",
            y = "Total_Installs",
            color = "Total_Installs",
            text = "Total_Installs",
            color_continuous_scale = "Viridis",
            hover_data = {
                "Total_Apps": True,
                "Threshold": True,
            },
            title = "Install Ranking"
        )
        fig.update_traces(
            texttemplate = "%{text:,.0f}",
            textposition = "outside"
        )
    elif chart_type == "Donut Chart":
        fig = px.pie(
            top_5,
            names = "Category",
            values = "Total_Installs",
            hole = 0.55,
            hover_data = {
                "Total_Apps": True,
                "Threshold": True,
            },
            title = "Install Share"
        )
        fig.update_traces(
            textinfo = "label+percent"
        )
    else:
        fig = px.treemap(
            top_5,
            path = ["Category"],
            values = "Total_Installs",
            color = "Total_Installs",
            color_continuous_scale = "Plasma",
            hover_data = {
                "Total_Apps": True,
                "Threshold": True
            },
            title = "Install Distribution"
        )
    fig.update_layout(
        height = 470,
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor = "rgba(0,0,0,0)"
    )
    st.plotly_chart(
        fig,
        use_container_width = True
    )
with right:
    st.markdown(
        '<div class = "section-title">📈 Category Comparison</div>',
        unsafe_allow_html = True
    )
    comparison = px.bar(
        top_5.sort_values("Total_Installs"),
        x = "Total_Installs",
        y = "Category",
        orientation = "h",
        color = "Total_Installs",
        text = "Total_Installs",
        color_continuous_scale = "Turbo",
        hover_data = {
            "Total_Apps": True,
            "Threshold": True
        },
        title = "Install Comparison"
    )
    comparison.update_traces(
        texttemplate = "%{text:,.0f}",
        textposition = "outside"
    )
    comparison.update_layout(
        height = 470,
        xaxis_title = "Total Installs",
        yaxis_title = "",
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor = "rgba(0,0,0,0)"
    )
    st.plotly_chart(
        comparison,
        use_container_width = True
    )

if show_table:
    st.divider()
    st.markdown(
        '<div class = "section-title">📋 Top 5 Category Details</div>',
        unsafe_allow_html = True
    )
    display_df = top_5.copy()

    display_df["Total_Installs"] = display_df["Total_Installs"].apply(lambda x: f"{x:,.0f}")
    display_df["Total_Apps"] = display_df["Total_Apps"].apply(lambda x: f"{x:,}")

    st.dataframe(
        display_df,
        use_container_width = True,
        hide_index = True
    )

else:
    st.divider()
    st.markdown(
        """
        <div class = "highlight">
        <b> Visualizations are currently locked.</b>
        <br><br>
        The interactive Choropleth Map and charts are available only between <b> 6:00 PM and 8:00 PM IST</b>.</div>""",
        unsafe_allow_html = True
    )

st.markdown(
    """
    <div class = "footer">
    <b> Global App Install Analytics</b>
    &nbsp; | &nbsp;
    Streamlit + Plotly
    &nbsp; | &nbsp;
    Google Play Store Dataset </div> """,
    unsafe_allow_html = True
)
