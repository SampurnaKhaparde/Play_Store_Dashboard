import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import glob
import re


st.set_page_config(
    page_title="Cumulative App Installs",
    page_icon="📊",
    layout="wide"
)


india_time = datetime.now(
    ZoneInfo("Asia/Kolkata")
)

current_hour = india_time.hour


if not (16 <= current_hour < 18):

    st.title("⏰ Cumulative App Installs")

    st.markdown("---")

    st.warning(
        "🔒 This visualization is currently unavailable."
    )

    st.info(
        "📅 Available Time: **4:00 PM – 6:00 PM IST**"
    )

    st.write(
        f"🕒 Current IST Time: "
        f"**{india_time.strftime('%I:%M:%S %p')}**"
    )

    st.markdown("---")

    st.subheader(
        "📊 Dashboard Access Restricted"
    )

    st.write(
        "This visualization can only be viewed "
        "between **4:00 PM and 6:00 PM IST**."
    )

    st.write(
        "Please come back during the specified "
        "time window to access the stacked area chart."
    )

    st.stop()

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(
            135deg,
            #f8fafc,
            #eef2ff,
            #f8fafc
        );
    }

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 900;
        color: #312e81;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 17px;
        margin-bottom: 25px;
    }

    .card {
        background: white;
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        min-height: 95px;
    }

    .label {
        font-size: 13px;
        color: #64748b;
        font-weight: 700;
    }

    .value {
        font-size: 27px;
        color: #1e293b;
        font-weight: 900;
        margin-top: 5px;
    }

    .section {
        font-size: 24px;
        font-weight: 800;
        color: #1e293b;
        margin-top: 25px;
        margin-bottom: 10px;
    }

    .footer {
        text-align: center;
        color: #64748b;
        margin-top: 30px;
        padding: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-title">'
    '📊 Cumulative App Installs Over Time'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Interactive Stacked Area Analysis of '
    'Filtered Google Play Store Apps'
    '</div>',
    unsafe_allow_html=True
)


@st.cache_data
def load_data():

    project_folder = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    possible_files = [
        "googleplaystore.csv",
        "Google_Play_Store.csv",
        "Google_Play_Store_Cleaned.csv",
        "google_play_store.csv",
        "GooglePlayStore.csv"
    ]

    file_path = None

    for filename in possible_files:

        path = os.path.join(
            project_folder,
            filename
        )

        if os.path.exists(path):

            file_path = path
            break

    if file_path is None:

        csv_files = glob.glob(
            os.path.join(
                project_folder,
                "*.csv"
            )
        )

        if csv_files:

            file_path = csv_files[0]

    if file_path is None:

        raise FileNotFoundError(
            "Google Play Store CSV file was not found."
        )

    return pd.read_csv(
        file_path,
        on_bad_lines="skip"
    )

try:

    df = load_data()

except Exception as e:

    st.error(
        f"❌ Error loading CSV: {e}"
    )

    st.info(
        "Make sure googleplaystore.csv is located "
        "in the main Googleplay_Dashboard folder."
    )

    st.stop()

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
)
required_columns = [
    "App",
    "Category",
    "Rating",
    "Reviews",
    "Size",
    "Installs",
    "Last Updated"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    st.error(
        f"❌ Missing columns: {missing_columns}"
    )

    st.write(
        "Available columns:",
        list(df.columns)
    )

    st.stop()

df["App"] = (
    df["App"]
    .astype(str)
    .str.strip()
)

df["Category"] = (
    df["Category"]
    .astype(str)
    .str.strip()
)
df["Rating"] = pd.to_numeric(
    df["Rating"],
    errors="coerce"
)
df["Reviews"] = (
    df["Reviews"]
    .astype(str)
    .str.replace(
        ",",
        "",
        regex=False
    )
)

df["Reviews"] = pd.to_numeric(
    df["Reviews"],
    errors="coerce"
)
df["Installs"] = (
    df["Installs"]
    .astype(str)
    .str.replace(
        ",",
        "",
        regex=False
    )
    .str.replace(
        "+",
        "",
        regex=False
    )
)

df["Installs"] = pd.to_numeric(
    df["Installs"],
    errors="coerce"
)
def convert_size(value):

    if pd.isna(value):

        return None

    value = str(value).upper().strip()

    if value == "VARIES WITH DEVICE":

        return None

    numbers = re.findall(
        r"[\d.]+",
        value
    )

    if not numbers:

        return None

    number = float(
        numbers[0]
    )

    if "KB" in value:

        return number / 1024

    return number


df["Size_MB"] = df["Size"].apply(
    convert_size
)
df = df[
    df["Rating"] >= 4.2
]
df = df[
    ~df["App"].str.contains(
        r"\d",
        na=False
    )
]
df = df[
    df["Category"].str.startswith(
        ("T", "P"),
        na=False
    )
]
df = df[
    df["Reviews"] > 1000
]

df = df[
    (df["Size_MB"] >= 20)
    &
    (df["Size_MB"] <= 80)
]

df["Last Updated"] = pd.to_datetime(
    df["Last Updated"],
    errors="coerce"
)

df = df.dropna(
    subset=[
        "Last Updated",
        "Installs"
    ]
)
if df.empty:

    st.warning(
        "⚠️ No applications match all the required filters."
    )

    st.stop()

df["Month"] = (
    df["Last Updated"]
    .dt.to_period("M")
    .dt.to_timestamp()
)
translation = {

    "TRAVEL & LOCAL":
        "Voyage et Local",

    "PRODUCTIVITY":
        "Productividad",

    "PHOTOGRAPHY":
        "写真"
}

df["Display_Category"] = (
    df["Category"]
    .map(translation)
    .fillna(
        df["Category"]
    )
)

monthly = (
    df.groupby(
        [
            "Month",
            "Display_Category"
        ],
        as_index=False
    )["Installs"]
    .sum()
)

monthly = monthly.sort_values(
    [
        "Display_Category",
        "Month"
    ]
)

monthly["Previous"] = (
    monthly
    .groupby(
        "Display_Category"
    )["Installs"]
    .shift(1)
)
monthly["MoM_Growth"] = (
    (
        monthly["Installs"]
        -
        monthly["Previous"]
    )
    /
    monthly["Previous"]
) * 100

monthly["High_Growth"] = (
    monthly["MoM_Growth"] > 25
)

monthly["Cumulative"] = (
    monthly
    .groupby(
        "Display_Category"
    )["Installs"]
    .cumsum()
)

categories = sorted(
    monthly[
        "Display_Category"
    ].unique()
)

with st.sidebar:

    st.header(
        "🎛️ Dashboard Controls"
    )

    selected = st.multiselect(
        "📂 Select Categories",
        categories,
        default=categories
    )

    st.markdown("---")

    st.subheader(
        "🔎 Applied Filters"
    )

    st.write(
        "⭐ Rating ≥ 4.2"
    )

    st.write(
        "🔤 App name contains no numbers"
    )

    st.write(
        "📂 Category starts with T / P"
    )

    st.write(
        "💬 Reviews > 1,000"
    )

    st.write(
        "📦 Size: 20–80 MB"
    )

    st.markdown("---")

    st.success(
        "🟢 Available: 4:00 PM – 6:00 PM IST"
    )

    st.write(
        "🕒 Current IST:",
        india_time.strftime(
            "%I:%M:%S %p"
        )
    )

chart_data = monthly[
    monthly[
        "Display_Category"
    ].isin(selected)
].copy()

if chart_data.empty:

    st.warning(
        "⚠️ Please select at least one category."
    )

    st.stop()

total_apps = df[
    "App"
].nunique()

total_installs = df[
    "Installs"
].sum()

total_categories = df[
    "Display_Category"
].nunique()

growth_count = monthly[
    monthly["High_Growth"]
].shape[0]

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.markdown(
        f"""
        <div class="card">

            <div class="label">
                📱 FILTERED APPS
            </div>

            <div class="value">
                {total_apps:,}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

with c2:

    st.markdown(
        f"""
        <div class="card">

            <div class="label">
                📥 TOTAL INSTALLS
            </div>

            <div class="value">
                {total_installs:,.0f}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

with c3:

    st.markdown(
        f"""
        <div class="card">

            <div class="label">
                📂 CATEGORIES
            </div>

            <div class="value">
                {total_categories}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

with c4:

    st.markdown(
        f"""
        <div class="card">

            <div class="label">
                🚀 >25% GROWTH
            </div>

            <div class="value">
                {growth_count}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )
st.markdown(
    '<div class="section">'
    '📈 Cumulative Installs by Category'
    '</div>',
    unsafe_allow_html=True
)

st.caption(
    "🟡 Highlighted periods indicate more than "
    "25% month-over-month growth."
)
colors = [
    "#6366F1",
    "#06B6D4",
    "#10B981",
    "#F59E0B",
    "#EC4899",
    "#8B5CF6",
    "#EF4444",
    "#3B82F6"
]

category_colors = {
    category:
        colors[index % len(colors)]
    for index, category
    in enumerate(categories)
}
fig = go.Figure()
for category in selected:

    temp = chart_data[
        chart_data[
            "Display_Category"
        ] == category
    ].sort_values(
        "Month"
    )

    fig.add_trace(
        go.Scatter(

            x=temp["Month"],

            y=temp["Cumulative"],

            mode="lines",

            name=category,

            stackgroup="one",

            line=dict(
                color=category_colors[
                    category
                ],
                width=2.5
            ),

            fillcolor=category_colors[
                category
            ],

            opacity=0.75,

            customdata=temp[
                [
                    "Installs",
                    "MoM_Growth"
                ]
            ].fillna(0).values,

            hovertemplate=(
                "<b>%{fullData.name}</b>"
                "<br>📅 %{x|%B %Y}"
                "<br>📥 Monthly Installs: "
                "%{customdata[0]:,.0f}"
                "<br>📈 MoM Growth: "
                "%{customdata[1]:.2f}%"
                "<br>📊 Cumulative: "
                "%{y:,.0f}"
                "<extra></extra>"
            )
        )
    )

high_growth = chart_data[
    chart_data["High_Growth"]
]
for month in high_growth[
    "Month"
].drop_duplicates():

    fig.add_vrect(

        x0=(
            month
            -
            pd.Timedelta(
                days=12
            )
        ),

        x1=(
            month
            +
            pd.Timedelta(
                days=12
            )
        ),

        fillcolor="#F59E0B",

        opacity=0.15,

        layer="below",

        line_width=0
    )
if not high_growth.empty:

    fig.add_trace(
        go.Scatter(

            x=high_growth[
                "Month"
            ],

            y=high_growth[
                "Cumulative"
            ],

            mode="markers",

            showlegend=False,

            marker=dict(
                size=11,
                color="#F59E0B",
                line=dict(
                    width=2,
                    color="#92400E"
                )
            ),

            customdata=high_growth[
                [
                    "Display_Category",
                    "MoM_Growth"
                ]
            ].values,

            hovertemplate=(
                "<b>🚀 HIGH GROWTH</b>"
                "<br>📂 %{customdata[0]}"
                "<br>📅 %{x|%B %Y}"
                "<br>📈 Growth: "
                "%{customdata[1]:.2f}%"
                "<extra></extra>"
            )
        )
    )

fig.update_layout(

    height=620,

    template="plotly_white",

    paper_bgcolor="rgba(0,0,0,0)",

    plot_bgcolor=(
        "rgba(255,255,255,0.8)"
    ),

    hovermode="x unified",

    margin=dict(
        l=70,
        r=210,
        t=40,
        b=80
    ),

    xaxis=dict(

        title="📅 Month",

        showgrid=True,

        gridcolor=(
            "rgba(148,163,184,.2)"
        ),

        rangeslider=dict(
            visible=True,
            thickness=0.06
        )
    ),

    yaxis=dict(

        title="📈 Cumulative Installs",

        tickformat=",",

        showgrid=True,

        gridcolor=(
            "rgba(148,163,184,.2)"
        )
    ),

    legend=dict(

        title="<b>📂 Categories</b>",

        orientation="v",

        x=1.02,

        y=1,

        xanchor="left",

        yanchor="top",

        bgcolor=(
            "rgba(255,255,255,.95)"
        ),

        bordercolor="#E2E8F0",

        borderwidth=1,

        font=dict(
            size=13
        )
    )
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": True,
        "displaylogo": False,
        "scrollZoom": True,
        "responsive": True
    }
)

st.markdown(
    '<div class="section">'
    '🚀 High Growth Months'
    '</div>',
    unsafe_allow_html=True
)

if high_growth.empty:

    st.info(
        "No category recorded more than "
        "25% month-over-month growth."
    )

else:

    table = high_growth[
        [
            "Month",
            "Display_Category",
            "Installs",
            "MoM_Growth"
        ]
    ].copy()

    table["Month"] = (
        table["Month"]
        .dt.strftime("%B %Y")
    )

    table["Installs"] = (
        table["Installs"]
        .map(
            lambda x:
            f"{x:,.0f}"
        )
    )

    table["MoM_Growth"] = (
        table["MoM_Growth"]
        .map(
            lambda x:
            f"{x:.2f}%"
        )
    )

    table.columns = [
        "📅 Month",
        "📂 Category",
        "📥 Installs",
        "📈 MoM Growth"
    ]

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True
    )
st.markdown(
    f"""
    <div class="footer">

        📊 Google Play Store Analytics
        &nbsp; • &nbsp;

        🕒 Available 4:00 PM – 6:00 PM IST
        &nbsp; • &nbsp;

        Current IST:
        <b>
        {india_time.strftime("%I:%M:%S %p")}
        </b>

    </div>
    """,
    unsafe_allow_html=True
)
