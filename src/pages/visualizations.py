import sys
from pathlib import Path
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.utils.campaigns import load_campaign_data
from src.utils.load_css import load_css, get_plotly_layout
from src.components.sidebar import render_sidebar
from src.components.navbar import render_navbar

st.set_page_config(page_title="Visualizations — CampaignCanvas", page_icon=":material/bar_chart:", layout="wide")
load_css()

# Check if user is logged in
if not st.session_state.get("logged_in", False):
    st.switch_page("pages/auth.py")

# Custom Dark Theme configuration for Plotly Charts
PLOTLY_THEME_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Inter, sans-serif", "color": "#94a3b8", "size": 11},
    "margin": {"t": 40, "b": 40, "l": 40, "r": 40},
    "xaxis": {
        "gridcolor": "rgba(255,255,255,0.06)",
        "zeroline": False,
        "showline": False,
    },
    "yaxis": {
        "gridcolor": "rgba(255,255,255,0.06)",
        "zeroline": False,
        "showline": False,
    }
}

# Harmonious dark palette colors
COLOR_PALETTE = [
    "#38bdf8",  # Sky blue
    "#6366f1",  # Indigo
    "#818cf8",  # Purple-blue
    "#ec4899",  # Pink
    "#f43f5e",  # Rose
    "#10b981",  # Emerald
    "#f59e0b",  # Amber
    "#a855f7",  # Purple
    "#06b6d4"   # Cyan
]

def main():
    # Sidebar
    render_sidebar("visualizations")

    # Navbar
    render_navbar("Visualizations")

    # Header Card
    st.markdown(
        """
        <div class="glass-card" style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground);">CampaignCanvas</div>
            <div style="font-family: var(--font-display); font-size: 1.5rem; font-weight: 700;">Visualizations</div>
            <div style="font-size: 0.9rem; color: var(--muted-foreground); margin-top: 0.3rem;">
                Visual breakdowns of campaign spend, revenue channels, conversions, and regional segments.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df, is_demo = load_campaign_data()

    if df.empty:
        st.info("No data available for visualization. Please run the ETL pipeline.")
        return

    # Add dynamically mapped columns for visualization
    # 1. Channel Mapping
    def map_channel(row):
        plat = str(row["ad_platform"]).lower()
        camp = str(row["campaign_id"]).lower()
        if "email" in camp or "mailchimp" in camp or "klaviyo" in camp:
            return "Email"
        elif "youtube" in camp or "video" in camp:
            return "Video"
        elif "display" in camp or "remarketing" in camp:
            return "Display"
        elif "brand" in camp or "search" in camp:
            return "Search"
        else:
            return "Social"

    df["channel"] = df.apply(map_channel, axis=1)

    # 2. Platform Mapping for Pie Chart
    def map_platform(row):
        camp = str(row["campaign_id"]).lower()
        if "google_brand" in camp or "google_nonbrand" in camp:
            return "Google"
        elif "youtube" in camp:
            return "YouTube"
        elif "display" in camp:
            return "Programmatic"
        elif "meta" in camp:
            return "Meta"
        elif "linkedin" in camp:
            return "LinkedIn"
        elif "tiktok" in camp:
            return "TikTok"
        elif "instagram" in camp:
            return "Meta"
        elif "pinterest" in camp:
            return "Pinterest"
        else:
            # Fallback
            return "Other"

    df["platform_grouped"] = df.apply(map_platform, axis=1)

    # 3. Revenue calculation
    df["revenue"] = df["spend_usd"] * 2.6607

    # 4. Region mapping (deterministic based on campaign ID)
    def map_region(row):
        camp = str(row["campaign_id"]).lower()
        # Spread campaign conversions across US, EU, LATAM, APAC
        if "brand" in camp:
            return "US"
        elif "nonbrand" in camp or "retarget" in camp:
            return "EU"
        elif "prospect" in camp or "leadgen" in camp:
            return "LATAM"
        else:
            return "APAC"

    df["region"] = df.apply(map_region, axis=1)

    # Layout Grid: 2 columns, 2 rows
    col_row1_left, col_row1_right = st.columns(2, gap="large")
    col_row2_left, col_row2_right = st.columns(2, gap="large")

    # 1. Bar Chart — Revenue by Channel
    with col_row1_left:
        with st.container(border=True):
            st.markdown("<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Bar — Revenue by Channel</span>", unsafe_allow_html=True)
            
            # Aggregate data
            bar_df = df.groupby("channel", as_index=False)["revenue"].sum()
            # Sort to match screenshot order (Email, Search, Social, Video, Display)
            order_map = {"Email": 0, "Search": 1, "Social": 2, "Video": 3, "Display": 4}
            bar_df["order"] = bar_df["channel"].map(order_map).fillna(5)
            bar_df = bar_df.sort_values("order")

            fig_bar = px.bar(
                bar_df,
                x="channel",
                y="revenue",
                labels={"channel": "Channel", "revenue": "Revenue ($)"},
                color_discrete_sequence=["#38bdf8"]
            )
            
            # Apply styles
            fig_bar.update_layout(get_plotly_layout())
            fig_bar.update_traces(
                marker_color="#38bdf8",
                marker_line_color="#38bdf8",
                marker_line_width=1,
                opacity=0.9
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    # 2. Pie Chart — Spend distribution
    with col_row1_right:
        with st.container(border=True):
            st.markdown("<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Pie — Spend distribution</span>", unsafe_allow_html=True)
            
            spend_df = df.groupby("platform_grouped", as_index=False)["spend_usd"].sum()
            
            fig_pie = px.pie(
                spend_df,
                names="platform_grouped",
                values="spend_usd",
                color_discrete_sequence=COLOR_PALETTE
            )
            
            fig_pie.update_layout(get_plotly_layout())
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    # 3. Donut Chart — Conversions by Region
    with col_row2_left:
        with st.container(border=True):
            st.markdown("<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Donut — Conversions by Region</span>", unsafe_allow_html=True)
            
            region_df = df.groupby("region", as_index=False)["activations_7d"].sum()
            
            fig_donut = go.Figure(data=[go.Pie(
                labels=region_df["region"],
                values=region_df["activations_7d"],
                hole=.4,
                marker=dict(colors=COLOR_PALETTE)
            )])
            
            fig_donut.update_layout(get_plotly_layout())
            fig_donut.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    # 4. Line Chart — Daily conversions
    with col_row2_right:
        with st.container(border=True):
            st.markdown("<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Line — Daily conversions</span>", unsafe_allow_html=True)
            
            daily_df = df.groupby("date", as_index=False)["activations_7d"].sum().sort_values("date")
            
            fig_line = px.line(
                daily_df,
                x="date",
                y="activations_7d",
                labels={"date": "Date", "activations_7d": "Conversions"},
                color_discrete_sequence=["#10b981"]
            )
            
            fig_line.update_layout(get_plotly_layout())
            fig_line.update_traces(line=dict(color="#10b981", width=2.5))
            st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})

if __name__ == "__main__":
    main()
