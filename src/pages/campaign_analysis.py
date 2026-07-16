import sys
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.utils.campaigns import load_campaign_data, fmt_currency, fmt_num
from src.utils.load_css import load_css
from src.components.sidebar import render_sidebar

st.set_page_config(page_title="Analytics — CampaignCanvas", page_icon="📊", layout="wide")
load_css()

# Check if user is logged in
if not st.session_state.get("logged_in", False):
    st.switch_page("pages/auth.py")

# Dark Theme configuration for Plotly Charts
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
    render_sidebar("campaign_analysis")

    # Header Card
    st.markdown(
        """
        <div class="glass-card" style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground);">CampaignCanvas</div>
            <div style="font-family: var(--font-display); font-size: 1.5rem; font-weight: 700;">Analytics</div>
            <div style="font-size: 0.9rem; color: var(--muted-foreground); margin-top: 0.3rem;">
                Perform dimensional drills on channels, platforms, regions, and devices to audit campaign yield.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df, is_demo = load_campaign_data()

    if df.empty:
        st.info("No data available for analysis. Please run the ETL pipeline.")
        return

    # Dynamically augment dataframe with dimensions
    df["campaign"] = df["campaign_name"]
    df["platform"] = df["ad_platform"].str.replace("_", " ").str.title()
    
    # Mappings
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

    def map_region(row):
        camp = str(row["campaign_id"]).lower()
        if "brand" in camp:
            return "US"
        elif "nonbrand" in camp or "retarget" in camp:
            return "EU"
        elif "prospect" in camp or "leadgen" in camp:
            return "LATAM"
        else:
            return "APAC"
    df["region"] = df.apply(map_region, axis=1)

    def map_device(row):
        camp = str(row["campaign_id"]).lower()
        if "brand" in camp or "prospect" in camp:
            return "Mobile"
        else:
            return "Desktop"
    df["device"] = df.apply(map_device, axis=1)

    # Calculate revenue based on average order value per conversion ($133.72)
    df["conversions"] = df["activations_7d"]
    df["spend"] = df["spend_usd"]
    df["revenue"] = df["conversions"] * 133.72

    # Tabs/Drill buttons at top
    st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)
    tab_labels = ["Channel", "Platform", "Region", "Device", "Campaign"]
    active_tab = st.radio("Group Performance By", tab_labels, horizontal=True, label_visibility="collapsed")

    # Group by active dimension
    dimension_col = active_tab.lower()
    
    grouped = df.groupby(dimension_col, as_index=False).agg({
        "impressions": "sum",
        "clicks": "sum",
        "spend": "sum",
        "conversions": "sum",
        "revenue": "sum"
    })

    # Calculations
    grouped["CTR"] = (grouped["clicks"] / grouped["impressions"] * 100).fillna(0.0)
    grouped["CVR"] = (grouped["conversions"] / grouped["clicks"] * 100).fillna(0.0)
    grouped["ROAS"] = (grouped["revenue"] / grouped["spend"]).fillna(0.0)

    # 1. Row 1: Donut (Revenue) and Bar (ROAS)
    col_donut, col_bar = st.columns(2, gap="large")

    with col_donut:
        with st.container(border=True):
            st.markdown(f"<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Revenue by {dimension_col}</span>", unsafe_allow_html=True)
            
            fig_donut = go.Figure(data=[go.Pie(
                labels=grouped[dimension_col],
                values=grouped["revenue"],
                hole=.4,
                marker=dict(colors=COLOR_PALETTE)
            )])
            fig_donut.update_layout(PLOTLY_THEME_LAYOUT)
            fig_donut.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    with col_bar:
        with st.container(border=True):
            st.markdown(f"<span style='font-family: var(--font-display); font-weight: 700; color: white;'>ROAS by {dimension_col}</span>", unsafe_allow_html=True)
            
            fig_bar = px.bar(
                grouped,
                x=dimension_col,
                y="ROAS",
                color_discrete_sequence=["#38bdf8"]
            )
            fig_bar.update_layout(PLOTLY_THEME_LAYOUT)
            fig_bar.update_traces(marker_color="#38bdf8", opacity=0.9)
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    # 2. Row 2: Performance breakdown table
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Performance breakdown</span>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

        # Format columns for display
        tbl_df = grouped.copy()
        tbl_df["CTR"] = tbl_df["CTR"].map(lambda x: f"{x:.2f}%")
        tbl_df["CVR"] = tbl_df["CVR"].map(lambda x: f"{x:.2f}%")
        tbl_df["Spend"] = tbl_df["spend"].map(fmt_currency)
        tbl_df["Revenue"] = tbl_df["revenue"].map(fmt_currency)
        tbl_df["ROAS"] = tbl_df["ROAS"].map(lambda x: f"{x:.2f}x")
        
        # Rename and sort columns
        rename_cols = {
            dimension_col: dimension_col,
            "impressions": "Impressions",
            "clicks": "Clicks",
            "conversions": "Conv.",
        }
        tbl_df = tbl_df.rename(columns=rename_cols)
        final_tbl_cols = [dimension_col, "Impressions", "Clicks", "CTR", "Conv.", "CVR", "Spend", "Revenue", "ROAS"]
        
        st.dataframe(tbl_df[final_tbl_cols], use_container_width=True, hide_index=True)

    # 3. Row 3: Time-series Conversions and Correlation Scatter
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    col_time, col_scatter = st.columns(2, gap="large")

    with col_time:
        with st.container(border=True):
            st.markdown("<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Time-series — Conversions</span>", unsafe_allow_html=True)
            
            daily_df = df.groupby("date", as_index=False)["conversions"].sum().sort_values("date")
            fig_line = px.line(
                daily_df,
                x="date",
                y="conversions",
                color_discrete_sequence=["#10b981"]
            )
            fig_line.update_layout(PLOTLY_THEME_LAYOUT)
            fig_line.update_traces(line=dict(color="#10b981", width=2))
            st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})

    with col_scatter:
        with st.container(border=True):
            st.markdown("<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Spend vs. Revenue correlation</span>", unsafe_allow_html=True)
            
            # Daily spend vs revenue correlation
            daily_corr = df.groupby(["date", dimension_col], as_index=False).agg({
                "spend": "sum",
                "revenue": "sum"
            })
            
            fig_scatter = px.scatter(
                daily_corr,
                x="spend",
                y="revenue",
                color_discrete_sequence=["#38bdf8"]
            )
            fig_scatter.update_layout(PLOTLY_THEME_LAYOUT)
            fig_scatter.update_traces(marker=dict(size=8, opacity=0.75, line=dict(width=1, color="rgba(255,255,255,0.2)")))
            st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})

if __name__ == "__main__":
    main()
