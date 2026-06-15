import sys
import base64
import subprocess
from pathlib import Path

import streamlit as st
import plotly.express as px

from src.process_data import (
    load_observations,
    calculate_summary,
    satellite_reliability,
    station_reliability,
    add_health_score,
)

from src.anomaly import (
    rule_based_anomalies,
    isolation_forest_anomalies,
)


st.set_page_config(
    page_title="Satellite Monitor",
    page_icon="🛰️",
    layout="wide",
)


def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    return encoded


bg_image_path = Path("assets/satellite_bg.jpg")

if bg_image_path.exists():
    bg_image = get_base64_image(bg_image_path)
else:
    bg_image = None


if bg_image:
    background_css = f"""
    .stApp {{
        background-image:
            linear-gradient(rgba(2, 6, 23, 0.82), rgba(2, 6, 23, 0.92)),
            url("data:image/jpg;base64,{bg_image}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    """
else:
    background_css = """
    .stApp {
        background-color: #0b1020;
    }
    """


st.markdown(
    f"""
    <style>
    {background_css}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }}

    h1, h2, h3 {{
        color: #f8fafc;
    }}

    p, div, span {{
        color: #dbeafe;
    }}

    .hero-card {{
        background: linear-gradient(
        135deg,
        rgba(17, 24, 39, 0.92) 0%,
        rgba(30, 58, 138, 0.88) 55%,
        rgba(15, 23, 42, 0.92) 100%
      );
        padding: 28px;
        border-radius: 22px;
        border: 1px solid rgba(147, 197, 253, 0.25);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.35);
        margin-bottom: 26px;
        backdrop-filter: blur(8px);
    }}

    .hero-title {{
        font-size: 46px;
        font-weight: 800;
        color: white;
        margin-bottom: 6px;
    }}

    .hero-subtitle {{
        font-size: 18px;
        color: #bfdbfe;
        max-width: 900px;
        line-height: 1.6;
    }}

    .section-card {{
        background-color: rgba(17, 24, 39, 0.88);
        padding: 22px;
        border-radius: 18px;
        border: 1px solid rgba(148, 163, 184, 0.2);
        margin-top: 18px;
        margin-bottom: 18px;
        backdrop-filter: blur(8px);
    }}

    .metric-card {{
        background-color: rgba(17, 24, 39, 0.9);
        padding: 20px;
        border-radius: 18px;
        border: 1px solid rgba(96, 165, 250, 0.25);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(8px);
    }}

    .metric-label {{
        font-size: 14px;
        color: #93c5fd;
        margin-bottom: 8px;
    }}

    .metric-value {{
        font-size: 34px;
        font-weight: 800;
        color: #ffffff;
    }}

    .small-note {{
        color: #94a3b8;
        font-size: 14px;
        line-height: 1.5;
    }}

    .badge-good {{
        display: inline-block;
        padding: 6px 12px;
        background-color: rgba(34, 197, 94, 0.16);
        color: #86efac;
        border: 1px solid rgba(34, 197, 94, 0.35);
        border-radius: 999px;
        font-weight: 700;
    }}

    .badge-warning {{
        display: inline-block;
        padding: 6px 12px;
        background-color: rgba(245, 158, 11, 0.16);
        color: #fcd34d;
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-radius: 999px;
        font-weight: 700;
    }}

    .badge-danger {{
        display: inline-block;
        padding: 6px 12px;
        background-color: rgba(239, 68, 68, 0.16);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-radius: 999px;
        font-weight: 700;
    }}

    [data-testid="stMetricValue"] {{
        color: #ffffff;
    }}

    [data-testid="stMetricLabel"] {{
        color: #93c5fd;
    }}

    [data-testid="stSidebar"] {{
        background-color: rgba(2, 6, 23, 0.95);
    }}

    div[data-testid="stDataFrame"] {{
        border-radius: 16px;
        overflow: hidden;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">🛰️ Satellite Monitor</div>
        <div class="hero-subtitle">
            Satellite observation reliability and anomaly monitoring dashboard.
            Satellite Monitor analyzes open SatNOGS ground-station data to track communication
            reliability, ground-station performance, and unusual observation patterns.
        </div>
        <br>
        <span class="badge-good">Open Satellite Data</span>
        &nbsp;
        <span class="badge-warning">Reliability Monitoring</span>
        &nbsp;
        <span class="badge-good">Python + Streamlit</span>
    </div>
    """,
    unsafe_allow_html=True,
)


st.sidebar.title("🛰️ Satellite Monitor Controls")

st.sidebar.markdown(
    """
    Use these controls to filter the dashboard and focus on stronger data signals.
    """
)

min_observations = st.sidebar.slider(
    "Minimum observations",
    min_value=1,
    max_value=20,
    value=1,
)

show_raw_data = st.sidebar.checkbox("Show raw observation data", value=False)

st.sidebar.markdown("---")

if st.sidebar.button("Refresh SatNOGS Data"):
    with st.spinner("Fetching latest observations from SatNOGS..."):
        result = subprocess.run(
            [sys.executable, "src/fetch_data.py"],
            capture_output=True,
            text=True,
        )

    if result.returncode == 0:
        st.sidebar.success("Data refreshed. Refresh the page to see updates.")
    else:
        st.sidebar.error("Data refresh failed.")
        st.sidebar.text(result.stderr)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Data Source:**
    SatNOGS open ground-station observations
    """
)


try:
    df = load_observations()
except FileNotFoundError:
    st.error(
        "No data found. Please run `python src/fetch_data.py` first to collect observations."
    )
    st.stop()


summary = calculate_summary(df)

satellite_df = satellite_reliability(df)
satellite_df = add_health_score(satellite_df)

station_df = station_reliability(df)

satellite_df = satellite_df[satellite_df["observations"] >= min_observations].copy()
station_df = station_df[station_df["observations"] >= min_observations].copy()

satellite_with_ml = isolation_forest_anomalies(satellite_df)
rule_anomalies = rule_based_anomalies(satellite_df)


st.markdown("## Mission Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Total Observations</div>
            <div class="metric-value">{summary["total_observations"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Overall Success Rate</div>
            <div class="metric-value">{summary["success_rate"]}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Unique Satellites</div>
            <div class="metric-value">{summary["unique_satellites"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Unique Ground Stations</div>
            <div class="metric-value">{summary["unique_stations"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown("## Daily Observation Activity")

daily = (
    df.groupby("date")
    .agg(
        observations=("id", "count"),
        success_rate=("is_success", "mean"),
    )
    .reset_index()
)

daily["success_rate"] = daily["success_rate"] * 100

fig_daily = px.line(
    daily,
    x="date",
    y="observations",
    title="Observations Over Time",
    markers=True,
)

fig_daily.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#dbeafe"),
)

st.plotly_chart(fig_daily, use_container_width=True)


st.markdown("## Satellite Reliability")

top_satellites = satellite_df.head(20)

fig_sat = px.bar(
    top_satellites,
    x="satellite",
    y="success_rate",
    hover_data=["observations", "avg_duration", "health_score"],
    title="Top Satellites by Observation Count: Success Rate",
)

fig_sat.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#dbeafe"),
)

st.plotly_chart(fig_sat, use_container_width=True)

st.dataframe(top_satellites, use_container_width=True)


st.markdown("## Satellite Health Score")

st.markdown(
    """
    <div class="section-card">
        <p class="small-note">
        The health score combines observation success rate, number of observations,
        and average observation duration. It is not a real satellite health diagnosis;
        it is a software-generated reliability indicator based on open observation data.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

top_health = satellite_df.sort_values("health_score", ascending=False).head(20)

fig_health = px.bar(
    top_health,
    x="satellite",
    y="health_score",
    hover_data=["observations", "success_rate", "avg_duration"],
    title="Top Satellites by Health Score",
)

fig_health.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#dbeafe"),
)

st.plotly_chart(fig_health, use_container_width=True)


st.markdown("## Ground Station Reliability")

top_stations = station_df.head(20)

fig_station = px.bar(
    top_stations,
    x="station",
    y="success_rate",
    hover_data=["observations", "avg_duration"],
    title="Top Ground Stations by Observation Count: Success Rate",
)

fig_station.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#dbeafe"),
)

st.plotly_chart(fig_station, use_container_width=True)

st.dataframe(top_stations, use_container_width=True)


st.markdown("## Anomaly Alerts")

if rule_anomalies.empty:
    st.markdown(
        """
        <span class="badge-good">No rule-based anomalies found</span>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"""
        <span class="badge-danger">{len(rule_anomalies)} rule-based anomalies found</span>
        """,
        unsafe_allow_html=True,
    )
    st.dataframe(rule_anomalies, use_container_width=True)


st.markdown("## Machine Learning Anomaly View")

if "is_ml_anomaly" not in satellite_with_ml.columns:
    st.info("ML anomaly column was not created. Check src/anomaly.py.")
else:
    ml_anomalies = satellite_with_ml[satellite_with_ml["is_ml_anomaly"] == 1]

    if ml_anomalies.empty:
        st.markdown(
            """
            <span class="badge-good">No ML anomalies found</span>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <span class="badge-warning">{len(ml_anomalies)} ML anomalies found</span>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(ml_anomalies, use_container_width=True)


if show_raw_data:
    st.markdown("## Raw Observation Data")
    st.dataframe(df, use_container_width=True)


st.markdown("## Why This Matters")

st.markdown(
    """
    <div class="section-card">
        <p>
        Satellite connectivity depends on more than satellites in orbit. It also depends on
        reliable ground operations, consistent observation quality, and fast detection of unusual
        communication behavior.
        </p>
        <p>
        Satellite Monitor demonstrates how Python, open satellite data, data analysis, and anomaly detection
        can support satellite operations workflows by turning raw observation records into reliability
        insights.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
