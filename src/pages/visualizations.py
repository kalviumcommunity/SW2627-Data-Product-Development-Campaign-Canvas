import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.components.navbar import render_navbar
from src.components.sidebar import render_sidebar
from src.utils.campaigns import (
    add_marketing_dimensions,
    calculate_revenue,
    load_campaign_data,
)
from src.utils.clerk_auth import require_authentication
from src.utils.load_css import get_plotly_layout, load_css

st.set_page_config(
    page_title="Visualizations — CampaignCanvas",
    page_icon=":material/bar_chart:",
    layout="wide",
)
load_css()

# Check if user is logged in
require_authentication()

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
    "#06b6d4",  # Cyan
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

    # Add standardized dimensions and calculation attributes
    df = add_marketing_dimensions(df)
    df["revenue"] = calculate_revenue(df)

    # Standardize schema column names if needed
    spend_col = "spend_usd" if "spend_usd" in df.columns else "spend"
    activation_col = (
        "activations_7d"
        if "activations_7d" in df.columns
        else "activations"
        if "activations" in df.columns
        else "conversions"
    )

    # Convert date column to datetime for proper temporal sorting
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Layout Grid: 2 columns, 2 rows
    col_row1_left, col_row1_right = st.columns(2, gap="large")
    col_row2_left, col_row2_right = st.columns(2, gap="large")

    # 1. Bar Chart — Revenue by Channel
    with col_row1_left:
        with st.container(border=True):
            st.markdown(
                "<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Bar — Revenue by Channel</span>",
                unsafe_allow_html=True,
            )

            bar_df = df.groupby("channel", as_index=False)[["revenue"]].sum()
            order_map = {"Email": 0, "Search": 1, "Social": 2, "Video": 3, "Display": 4}
            bar_df["order"] = bar_df["channel"].map(order_map).fillna(5)
            bar_df = bar_df.sort_values(by="order")

            fig_bar = px.bar(
                bar_df,
                x="channel",
                y="revenue",
                labels={"channel": "Channel", "revenue": "Revenue ($)"},
                color_discrete_sequence=["#38bdf8"],
            )

            fig_bar.update_layout(get_plotly_layout())
            fig_bar.update_traces(
                marker_color="#38bdf8",
                marker_line_color="#38bdf8",
                marker_line_width=1,
                opacity=0.9,
            )
            st.plotly_chart(
                fig_bar, use_container_width=True, config={"displayModeBar": False}
            )

    # 2. Pie Chart — Spend distribution
    with col_row1_right:
        with st.container(border=True):
            st.markdown(
                "<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Pie — Spend distribution</span>",
                unsafe_allow_html=True,
            )

            spend_df = df.groupby("platform_grouped", as_index=False)[[spend_col]].sum()

            fig_pie = px.pie(
                spend_df,
                names="platform_grouped",
                values=spend_col,
                color_discrete_sequence=COLOR_PALETTE,
            )

            fig_pie.update_layout(get_plotly_layout())
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(
                fig_pie, use_container_width=True, config={"displayModeBar": False}
            )

    # 3. Donut Chart — Conversions by Region
    with col_row2_left:
        with st.container(border=True):
            st.markdown(
                "<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Donut — Conversions by Region</span>",
                unsafe_allow_html=True,
            )

            region_df = df.groupby("region", as_index=False)[[activation_col]].sum()

            fig_donut = go.Figure(
                data=[
                    go.Pie(
                        labels=region_df["region"],
                        values=region_df[activation_col],
                        hole=0.4,
                        marker=dict(colors=COLOR_PALETTE),
                    )
                ]
            )

            fig_donut.update_layout(get_plotly_layout())
            fig_donut.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(
                fig_donut, use_container_width=True, config={"displayModeBar": False}
            )

    # 4. Line Chart — Daily conversions
    with col_row2_right:
        with st.container(border=True):
            st.markdown(
                "<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Line — Daily conversions</span>",
                unsafe_allow_html=True,
            )

            if "date" in df.columns:
                daily_df = (
                    df.groupby("date", as_index=False)[[activation_col]]
                    .sum()
                    .sort_values(by="date")
                )
            else:
                daily_df = pd.DataFrame(columns=["date", activation_col])

            fig_line = px.line(
                daily_df,
                x="date",
                y=activation_col,
                labels={"date": "Date", activation_col: "Conversions"},
                color_discrete_sequence=["#10b981"],
            )

            fig_line.update_layout(get_plotly_layout())
            fig_line.update_traces(line=dict(color="#10b981", width=2.5))
            st.plotly_chart(
                fig_line, use_container_width=True, config={"displayModeBar": False}
            )


if __name__ == "__main__":
    main()