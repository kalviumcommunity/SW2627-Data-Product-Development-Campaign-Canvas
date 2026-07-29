from __future__ import annotations

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
    aggregate_by,
    fmt_currency,
    load_campaign_data,
)
from src.utils.load_css import get_plotly_layout, load_css
from src.utils.clerk_auth import require_authentication

st.set_page_config(
    page_title="Analytics — CampaignCanvas",
    page_icon=":material/bar_chart:",
    layout="wide",
)
load_css()

require_authentication()

COLOR_PALETTE = [
    "#38bdf8",
    "#6366f1",
    "#818cf8",
    "#ec4899",
    "#f43f5e",
    "#10b981",
    "#f59e0b",
    "#a855f7",
    "#06b6d4",
]


def _prepare_frame() -> tuple[pd.DataFrame, bool]:
    """Loads dataset and verifies standardized column mappings."""
    frame, is_demo = load_campaign_data()
    if frame.empty:
        return frame, is_demo

    frame = add_marketing_dimensions(frame)

    if "spend" not in frame.columns and "spend_usd" in frame.columns:
        frame["spend"] = frame["spend_usd"]
    if "conversions" not in frame.columns and "activations_7d" in frame.columns:
        frame["conversions"] = frame["activations_7d"]
    if "campaign" not in frame.columns:
        frame["campaign"] = frame.get("campaign_name", frame.get("campaign_id", ""))

    return frame, is_demo


def _format_pct(value: float) -> str:
    """Formats float value as a clean percentage string."""
    return f"{value:.2f}%"


def main() -> None:
    render_sidebar("campaign_analysis")

    # Navbar
    render_navbar("Analytics")

    st.markdown(
        """
        <div class="glass-card" style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground);">CampaignCanvas</div>
            <div style="font-family: var(--font-display); font-size: 1.5rem; font-weight: 700;">Analytics</div>
            <div style="font-size: 0.9rem; color: var(--muted-foreground); margin-top: 0.3rem; line-height: 1.5;">
                Drill into channel, platform, region, device, and campaign performance to inspect spend, revenue, and conversion efficiency.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df, _ = _prepare_frame()
    if df.empty:
        st.info("No data available for analysis. Please run the ETL pipeline.")
        return

    tab_labels = ["Channel", "Platform", "Region", "Device", "Campaign"]
    dimension_map = {
        "Channel": "channel",
        "Platform": "platform",
        "Region": "region",
        "Device": "device",
        "Campaign": "campaign_id" if "campaign_id" in df.columns else "campaign",
    }
    selected_tab = st.radio(
        "Group Performance By",
        tab_labels,
        horizontal=True,
        label_visibility="collapsed",
    )
    dimension_col = dimension_map[selected_tab]

    grouped = aggregate_by(df, dimension_col)
    if grouped.empty:
        st.info("No grouped data available for analysis.")
        return

    grouped = grouped.copy()

    # Derived Rate Calculations (Defensive math checks)
    grouped["CTR"] = (
        (grouped["clicks"] / grouped["impressions"] * 100)
        if "impressions" in grouped.columns and "clicks" in grouped.columns
        else 0.0
    ).fillna(0.0)

    grouped["CVR"] = (
        (grouped["signups"] / grouped["clicks"] * 100)
        if "clicks" in grouped.columns and "signups" in grouped.columns
        else 0.0
    ).fillna(0.0)

    spend_col = (
        "spend_usd"
        if "spend_usd" in grouped.columns
        else ("spend" if "spend" in grouped.columns else "totalSpend")
    )
    revenue_col = (
        "totalRevenue"
        if "totalRevenue" in grouped.columns
        else ("revenue" if "revenue" in grouped.columns else spend_col)
    )

    grouped["ROAS"] = (grouped[revenue_col] / grouped[spend_col].replace(0, pd.NA)).fillna(0.0)

    grouped["Activation rate"] = (
        (grouped["activations_7d"] / grouped["signups"].replace(0, pd.NA) * 100)
        if "signups" in grouped.columns and "activations_7d" in grouped.columns
        else 0.0
    ).fillna(0.0)

    # Theme Layout Setup
    base_layout = get_plotly_layout()
    text_color = base_layout["font"]["color"]
    grid_color = base_layout["xaxis"]["gridcolor"]

    # First Row: Donut Chart + Bar Chart
    col_donut, col_bar = st.columns(2, gap="large")
    with col_donut:
        with st.container(border=True):
            st.markdown(
                f"<span style='font-family: var(--font-display); font-weight: 700; color: var(--foreground);'>Signups by {selected_tab}</span>",
                unsafe_allow_html=True,
            )
            fig_donut = go.Figure(
                data=[
                    go.Pie(
                        labels=grouped["name"],
                        values=grouped["signups"] if "signups" in grouped.columns else [0] * len(grouped),
                        hole=0.4,
                        marker=dict(colors=COLOR_PALETTE),
                    )
                ]
            )
            layout_donut = base_layout.copy()
            layout_donut.update(height=300, margin=dict(l=10, r=10, t=10, b=10))
            fig_donut.update_layout(layout_donut)
            fig_donut.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(
                fig_donut,
                use_container_width=True,
                config={"displayModeBar": False},
            )

    with col_bar:
        with st.container(border=True):
            st.markdown(
                f"<span style='font-family: var(--font-display); font-weight: 700; color: var(--foreground);'>Activation rate by {selected_tab}</span>",
                unsafe_allow_html=True,
            )
            fig_bar = px.bar(
                grouped,
                x="name",
                y="Activation rate",
                color_discrete_sequence=["#38bdf8"],
            )
            layout_bar = base_layout.copy()
            layout_bar.update(
                height=300,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=False, title=None, tickfont=dict(color=text_color, size=10)),
                yaxis=dict(showgrid=True, gridcolor=grid_color, title=None, tickfont=dict(color=text_color, size=10)),
            )
            fig_bar.update_layout(layout_bar)
            fig_bar.update_traces(marker_color="#38bdf8", opacity=0.9)
            st.plotly_chart(
                fig_bar,
                use_container_width=True,
                config={"displayModeBar": False},
            )

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # Breakdown Table
    with st.container(border=True):
        st.markdown(
            "<span style='font-family: var(--font-display); font-weight: 700; color: var(--foreground);'>Performance breakdown</span>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

        display_cols = [
            "name",
            "impressions",
            "clicks",
            "CTR",
            "signups",
            "CVR",
            "activations_7d",
            "Activation rate",
            spend_col,
            revenue_col,
            "ROAS",
        ]
        existing_cols = [c for c in display_cols if c in grouped.columns]

        display_df = grouped[existing_cols].copy()
        rename_dict = {
            "name": selected_tab,
            "impressions": "Impressions",
            "clicks": "Clicks",
            "signups": "Conv.",
            "activations_7d": "Activations",
            "Activation rate": "Activation rate (%)",
            spend_col: "Spend",
            revenue_col: "Revenue",
            "ROAS": "ROAS",
        }
        display_df = display_df.rename(columns=rename_dict)

        if "Spend" in display_df.columns:
            display_df["Spend"] = display_df["Spend"].map(fmt_currency)
        if "Revenue" in display_df.columns:
            display_df["Revenue"] = display_df["Revenue"].map(fmt_currency)
        if "ROAS" in display_df.columns:
            display_df["ROAS"] = display_df["ROAS"].map(lambda val: f"{val:.2f}x")
        if "CTR" in display_df.columns:
            display_df["CTR"] = display_df["CTR"].map(_format_pct)
        if "CVR" in display_df.columns:
            display_df["CVR"] = display_df["CVR"].map(_format_pct)
        if "Activation rate (%)" in display_df.columns:
            display_df["Activation rate (%)"] = display_df["Activation rate (%)"].map(_format_pct)

        table_html = display_df.to_html(index=False, classes="performance-table", border=0)

        st.markdown(
            f"""
            <div class="performance-table-wrapper">
            {table_html}
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    # Second Row: Time-Series Line + Spend Scatter
    col_time, col_scatter = st.columns(2, gap="large")

    with col_time:
        with st.container(border=True):
            st.markdown(
                "<span style='font-family: var(--font-display); font-weight: 700; color: var(--foreground);'>Time-series — Signups and activations</span>",
                unsafe_allow_html=True,
            )
            if "date" in df.columns:
                daily_df = (
                    df.groupby("date", as_index=False)
                    .agg({"signups": "sum", "activations_7d": "sum"})
                    .sort_values("date")
                )
            else:
                daily_df = pd.DataFrame(columns=["date", "signups", "activations_7d"])

            if daily_df.empty or daily_df["date"].nunique() < 3:
                campaign_df = (
                    grouped[["name", "signups", "activations_7d"]]
                    .head(8)
                    .sort_values("signups", ascending=False)
                )
                fig_line = go.Figure()
                fig_line.add_trace(
                    go.Bar(
                        x=campaign_df["name"],
                        y=campaign_df["signups"],
                        name="Signups",
                        marker_color="#38bdf8",
                    )
                )
                fig_line.add_trace(
                    go.Bar(
                        x=campaign_df["name"],
                        y=campaign_df["activations_7d"],
                        name="Activations",
                        marker_color="#10b981",
                    )
                )
                layout_line = base_layout.copy()
                layout_line.update(
                    barmode="group",
                    height=300,
                    margin=dict(l=10, r=10, t=10, b=10),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=text_color, size=10)),
                    xaxis=dict(showgrid=False, title=None, tickfont=dict(color=text_color, size=10)),
                    yaxis=dict(showgrid=True, gridcolor=grid_color, title=None, tickfont=dict(color=text_color, size=10)),
                )
                fig_line.update_layout(layout_line)
            else:
                fig_line = go.Figure()
                fig_line.add_trace(
                    go.Scatter(
                        x=daily_df["date"],
                        y=daily_df["signups"],
                        name="Signups",
                        mode="lines+markers",
                        line=dict(color="#38bdf8", width=2.5),
                    )
                )
                fig_line.add_trace(
                    go.Scatter(
                        x=daily_df["date"],
                        y=daily_df["activations_7d"],
                        name="Activations",
                        mode="lines+markers",
                        line=dict(color="#10b981", width=2.5),
                    )
                )
                layout_line = base_layout.copy()
                layout_line.update(
                    height=300,
                    margin=dict(l=10, r=10, t=10, b=10),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=text_color, size=10)),
                    xaxis=dict(showgrid=False, title=None, tickfont=dict(color=text_color, size=10)),
                    yaxis=dict(showgrid=True, gridcolor=grid_color, title=None, tickfont=dict(color=text_color, size=10)),
                )
                fig_line.update_layout(layout_line)

            st.plotly_chart(
                fig_line,
                use_container_width=True,
                config={"displayModeBar": False},
            )

    with col_scatter:
        with st.container(border=True):
            st.markdown(
                "<span style='font-family: var(--font-display); font-weight: 700; color: var(--foreground);'>Spend vs. activations correlation</span>",
                unsafe_allow_html=True,
            )
            scatter_dim = dimension_col if dimension_col in df.columns else "channel"
            spend_df_col = "spend" if "spend" in df.columns else "spend_usd"

            if "date" in df.columns and scatter_dim in df.columns:
                scatter_df = df.groupby(["date", scatter_dim], as_index=False).agg(
                    {spend_df_col: "sum", "activations_7d": "sum"}
                )
            else:
                scatter_df = pd.DataFrame(columns=[spend_df_col, "activations_7d"])

            fig_scatter = px.scatter(
                scatter_df,
                x=spend_df_col,
                y="activations_7d",
                color_discrete_sequence=["#38bdf8"],
            )
            layout_scatter = base_layout.copy()
            layout_scatter.update(
                height=300,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=True, gridcolor=grid_color, title="Spend ($)", tickfont=dict(color=text_color, size=10)),
                yaxis=dict(showgrid=True, gridcolor=grid_color, title="Activations", tickfont=dict(color=text_color, size=10)),
            )
            fig_scatter.update_layout(layout_scatter)
            fig_scatter.update_traces(
                marker=dict(
                    size=8,
                    opacity=0.75,
                    line=dict(width=1, color="rgba(255,255,255,0.2)"),
                )
            )
            st.plotly_chart(
                fig_scatter,
                use_container_width=True,
                config={"displayModeBar": False},
            )


if __name__ == "__main__":
    main()