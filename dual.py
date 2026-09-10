import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title = "Google PlayStore Analytics",
    layout = "wide"
)

st.markdown(
    """
    <style>
        .main {
            background-color: #f5f7fb;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .big-title {
        font-size: 38px;
        font-weight: bold;
        }
        .subtitle {
        font-size: 17px;
        color: #6b7280;
        margin-bottom: 25px;
        }
    </style>
    """,
    unsafe_allow_html = True
)

st.sidebar.title("⚙️ Dashboard Settings")

test_mode = st.sidebar.checkbox(
    "Test Mode",
    value = True
)
st.sidebar.info(
    "Test Mode ON -> chart is visible anytime.\n\n"
    "Test Mode OFF -> chart is visible only"
    "between 1:00 PM to 2:00 PM IST."
)

try:
    df = pd.read_csv("googleplaystore.csv")
except FileNotFoundError:
    st.error(
        "❌ googleplaystore.csv was not found."
        "Put the CSV file in the same folder as"
        "dual.py."
    )
    st.stop()

df.columns = df.columns.str.strip()
required_columns = [
    "App",
    "Category",
    "Installs",
    "Price",
    "Type",
    "Android Ver",
    "Size",
    "Content Rating"
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
    st.stop()

df["Installs_Num"] = (
    df["Installs"]
    .astype(str)
    .str.replace(",", "", regex = False)
    .str.replace("+", "", regex = False)
    .str.strip()
)

df["Installs_Num"] = pd.to_numeric(
    df["Installs_Num"],
    errors = "coerce"
)

df["Price_Num"] = (
    df["Price"]
    .astype(str)
    .str.replace("$", "", regex = False)
    .str.strip()
)

df["Price_Num"] = pd.to_numeric(
    df["Price_Num"],
    errors = "coerce"
).fillna(0)

df["Revenue"] = (
    df["Installs_Num"]*
    df["Price_Num"]
)

df["App_Name_Length"] = (
    df["App"]
    .astype(str)
    .str.len()
)

df["Android_Version_Num"] = (
    df["Android Ver"]
    .astype(str)
    .str.extract(r"(\d+(?:\.\d+)?)",
                 expand = False)
)

df["Android_Version_Num"] = pd.to_numeric(
    df["Android_Version_Num"],
    errors = "coerce"
)

def convert_size(value):
    value = str(value).strip()

    try:
        if value.endswith("M"):
            return float(
                value.replace("M", "")
            )
        elif value.endswith("k"):
            return float(
                value.replace("k", "")
            )/1024
        else:
            return None
    except:
        return None

df["Size_MB"] = df["Size"].apply(convert_size)

df = df.drop_duplicates(
    subset = ["App"]
)

filtered_df = df[
    (df["Installs_Num"] >= 10000)
    &
    (df["Revenue"] >= 10000)
    &
    (df["Android_Version_Num"] > 4.0)
    &
    (df["Size_MB"] > 15)
    &
    (df["Content Rating"] == "Everyone")
    &
    (df["App_Name_Length"] <= 30)
].copy()

top_3_categories = (
    filtered_df
    .groupby("Category")["Installs_Num"]
    .sum()
    .nlargest(3)
    .index
    .tolist()
)

filtered_df = filtered_df[
    filtered_df["Category"].isin(top_3_categories)
]

india_time = datetime.now(
    ZoneInfo("Asia/Kolkata")
)
current_minutes = (
    india_time.hour*60 + india_time.minute
)
start_minutes = 13*60
end_minutes = 14*60

is_allowed_time = (
    start_minutes <= current_minutes < end_minutes
)
st.markdown(
    '<div class = "big-title">'
    'Google Play Store Analytics'
    '</div>',
    unsafe_allow_html = True
)
st.markdown(
    '<div class = "subtitle">'
    'Dual-Axis Analysis of Average Installs'
    'and Revenue for Free vs Paid Apps'
    '</div',
    unsafe_allow_html = True
)

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Current IST Time",
        india_time.strftime('%I:%M:%S %p')
    )
with col2:
    if test_mode:
        st.metric(
            "Chart Status",
            "Test Mode"
        )
    elif is_allowed_time:
        st.metric(
            "Char Status",
            "AVAILABLE"
        )
    else:
        st.metric(
            "Chart Status",
            "LOCKED"
        )

show_chart = (
    test_mode or is_allowed_time
)

if show_chart:
    st.success("Dual-axis chart is available.")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Filtered Apps",
            f"{len(filtered_df):,}"
        )
    with col2:
        st.metric(
            "Top Categories",
            len(top_3_categories)
        )
    with col3:
        total_installs = (
            filtered_df["Installs_Num"]
            .sum()
        )
        st.metric(
            "TOtal Installs",
            f"{total_installs:,.0f}"
        )
    with col4:
        total_revenue = (
            filtered_df["Revenue"]
            .sum()
        )
        st.metric(
            "Total Revenue",
            f"${total_revenue:,.0f}"
        )
    st.divider()

    st.subheader("🏆 Top 3 Categories")
    if top_3_categories:
        category_text = " + ".join(
            top_3_categories
        )
        st.info(category_text)
    else:
        st.warning(
            "No categories satisfy all filters."
        )

    chart_data = (
        filtered_df
        .groupby(
            ["Category", "Type"]
        )
        .agg(
            Average_Installs = (
                "Installs_Num",
                "mean"
            ),
            Average_Revenue = (
                "Revenue",
                "mean"
            )
        )
        .reset_index()
    )
    fig = go.Figure()

    for app_type in ["Free", "Paid"]:
        data = chart_data[
            chart_data["Type"] == app_type
        ]
        if not data.empty:
            fig.add_trace(
                go.Bar(
                    x = data["Category"],
                    y = data["Average_Installs"],
                    name = (
                        f"{app_type} - "
                        f"Average Installs"
                    ),
                    text = [
                        f"{value:,.0f}"
                        for value in
                        data["Average_Installs"]
                    ],
                    textposition = "auto",
                    hovertemplate = (
                        "<b>%{x}</b><br>"
                        "Type: "
                        + app_type
                        + "<br>"
                        "Average Installs: "
                        "%{y:,.0f}"
                        "<extra></extra>"
                    )
                )
            )

    for app_type in ["Free", "Paid"]:
        data = chart_data[
            chart_data["Type"] == app_type
        ]
        if not data.empty:
            fig.add_trace(
                go.Scatter(
                    x = data["Category"],
                    y = data["Average_Revenue"],
                    name = (
                        f"{app_type} - "
                        f"Average Revenue"
                    ),
                    mode = "lines+markers",
                    yaxis = "y2",
                    line = dict(
                        width = 3
                    ),
                    marker = dict(
                        size = 9
                    ),
                    hovertemplate = (
                        "<b>%{x}</b><br>"
                        "Type: "
                        + app_type
                        + "<br>"
                        "Average Revenue: $"
                        "%{y:,.0f}"
                        "<extra></extra>"
                    )
                )
            )
    fig.update_layout(
        title = dict(
            text = (
                "Average Installs & Revenue"
                "-- Free vs Paid Apps"
            ),
            font = dict(
                size = 24
            ),
            x = 0.02
        ),
        xaxis = dict(
            title = "Top 3 App Categories",
            showgrid = False
        ),
        yaxis = dict(
            title = "Average Installs",
            showgrid = True
        ),
        yaxis2 = dict(
            title = "Average Revenue ($)",
            overlaying = "y",
            side = "right",
            showgrid = False
        ),
        barmode = "group",
        height = 600,
        hovermode = "x unified",

        legend = dict(
            orientation = "h",
            yanchor = "bottom",
            y = 1.02,
            xanchor = "right",
            x = 1
        ),
        margin = dict(
            l = 70,
            r = 70,
            t = 110,
            b = 70
        ),
        paper_bgcolor = "white",
        plot_bgcolor = "white"
    )

    st.plotly_chart(
        fig,
        use_container_width = True
    )

    st.divider()
    st.subheader("Applied Filters")
    col1, col2 = st.columns(2)

    with col1:
        st.write("✅ Installs >= 10,000")
        st.write("✅ Revenue >= $10,000")
        st.write("✅ Android Version > 4.0")
        st.write("✅ Size > 15 MB")

    with col2:
        st.write(
            "✅ Content Rating = Everyone"
        )
        st.write(
            "✅ App Name <= 30 characters"
        )
        st.write(
            "✅ Top 3 Categories"
        )
        st.write(
            "✅ Free vs Paid"
        )

else:
    st.divider()
    st.subheader(
        "🔒 Chart Currently Unavailable"
    )
    st.warning(
        "The Dual-axis chart is available"
        "only between 1:00 PM to 2:00 PM IST."
    )
    st.write(
        "🕐 Current IST Time: "
        f"**{india_time.strftime('%I:%M:%S %p')}**"
    )
    st.info(
        "⏰ Please return between "
        "**1:00 PM to 2:00 PM IST** "
        "to view the chart."
    )
    st.divider()
