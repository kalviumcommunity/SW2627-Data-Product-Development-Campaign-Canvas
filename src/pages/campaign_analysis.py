from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.components.sidebar import render_sidebar
from src.utils.campaigns import aggregate_by, fmt_currency, load_campaign_data
from src.utils.load_css import load_css

st.set_page_config(page_title="Analytics — CampaignCanvas", page_icon="📊", layout="wide")
load_css()

if not st.session_state.get("logged_in", False):
    st.switch_page("pages/auth.py")

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

PLOTLY_THEME_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Inter, sans-serif", "color": "#94a3b8", "size": 11},
    "margin": {"t": 40, "b": 40, "l": 40, "r": 40},
    "xaxis": {"gridcolor": "rgba(255,255,255,0.06)", "zeroline": False, "showline": False},
    "yaxis": {"gridcolor": "rgba(255,255,255,0.06)", "zeroline": False, "showline": False},
}


def _prepare_frame() -> tuple[pd.DataFrame, bool]:
    frame, is_demo = load_campaign_data()
    if frame.empty:
        return frame, is_demo

    frame = frame.copy()
    frame["campaign"] = frame["campaign_name"]
    frame["platform"] = frame["ad_platform"].astype(str).str.replace("_", " ").str.title()

    def map_channel(row):
        camp = str(row["campaign_id"]).lower()
        if "email" in camp or "mailchimp" in camp or "klaviyo" in camp:
            return "Email"
        if "youtube" in camp or "video" in camp:
            return "Video"
        if "display" in camp or "remarketing" in camp:
            return "Display"
        if "brand" in camp or "search" in camp:
            return "Search"
        return "Social"

    def map_region(row):
        camp = str(row["campaign_id"]).lower()
        if "brand" in camp:
            return "US"
        if "nonbrand" in camp or "retarget" in camp:
            return "EU"
        if "prospect" in camp or "leadgen" in camp:
            return "LATAM"
        return "APAC"

    def map_device(row):
        camp = str(row["campaign_id"]).lower()
        return "Mobile" if "brand" in camp or "prospect" in camp else "Desktop"

    frame["channel"] = frame.apply(map_channel, axis=1)
    frame["region"] = frame.apply(map_region, axis=1)
    frame["device"] = frame.apply(map_device, axis=1)
    frame["conversions"] = frame["activations_7d"]
    frame["spend"] = frame["spend_usd"]
    frame["revenue"] = frame["conversions"] * 133.72
    return frame, is_demo


def _format_pct(value: float) -> str:
    return f"{value:.2f}%"


def main() -> None:
    render_sidebar("campaign_analysis")

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
    dimension_map = {label: label.lower() for label in tab_labels}
    selected_tab = st.radio("Group Performance By", tab_labels, horizontal=True, label_visibility="collapsed")
    dimension_col = dimension_map[selected_tab]

    grouped = aggregate_by(df, dimension_col)
    if grouped.empty:
        st.info("No grouped data available for analysis.")
        return

    grouped = grouped.copy()
    grouped["CTR"] = (grouped["clicks"] / grouped["impressions"] * 100).fillna(0.0)
    grouped["CVR"] = (grouped["signups"] / grouped["clicks"] * 100).fillna(0.0)
    grouped["ROAS"] = (grouped.get("revenue", grouped["spend_usd"] * 1.5) / grouped["spend_usd"]).fillna(0.0)

    col_donut, col_bar = st.columns(2, gap="large")
    with col_donut:
        with st.container(border=True):
            st.markdown(
                f"<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Revenue by {dimension_col}</span>",
                unsafe_allow_html=True,
            )
            fig_donut = go.Figure(
                data=[
                    go.Pie(
                        labels=grouped["name"],
                        values=grouped.get("totalRevenue", grouped.get("revenue", grouped["spend_usd"])),
                        hole=0.4,
                        marker=dict(colors=COLOR_PALETTE),
                    )
                ]
            )
            fig_donut.update_layout(PLOTLY_THEME_LAYOUT)
            fig_donut.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    with col_bar:
        with st.container(border=True):
            st.markdown(
                f"<span style='font-family: var(--font-display); font-weight: 700; color: white;'>ROAS by {dimension_col}</span>",
                unsafe_allow_html=True,
            )
            fig_bar = px.bar(grouped, x="name", y="roas", color_discrete_sequence=["#38bdf8"])
            fig_bar.update_layout(PLOTLY_THEME_LAYOUT)
            fig_bar.update_traces(marker_color="#38bdf8", opacity=0.9)
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            "<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Performance breakdown</span>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

        display_df = grouped[["name", "impressions", "clicks", "CTR", "signups", "CVR", "spend_usd", "totalRevenue", "roas"]].copy()
        display_df = display_df.rename(
            columns={
                "name": dimension_col,
                "impressions": "Impressions",
                "clicks": "Clicks",
                "signups": "Conv.",
                "spend_usd": "Spend",
                "totalRevenue": "Revenue",
                "roas": "ROAS",
            }
        )
        display_df["Spend"] = display_df["Spend"].map(fmt_currency)
        display_df["Revenue"] = display_df["Revenue"].map(fmt_currency)
        display_df["ROAS"] = display_df["ROAS"].map(lambda value: f"{value:.2f}x")
        display_df["CTR"] = display_df["CTR"].map(_format_pct)
        display_df["CVR"] = display_df["CVR"].map(_format_pct)
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    col_time, col_scatter = st.columns(2, gap="large")

    with col_time:
        with st.container(border=True):
            st.markdown(
                "<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Time-series — Conversions</span>",
                unsafe_allow_html=True,
            )
            daily_df = df.groupby("date", as_index=False)["conversions"].sum().sort_values("date")
            fig_line = px.line(daily_df, x="date", y="conversions", color_discrete_sequence=["#10b981"])
            fig_line.update_layout(PLOTLY_THEME_LAYOUT)
            fig_line.update_traces(line=dict(color="#10b981", width=2))
            st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})

    with col_scatter:
        with st.container(border=True):
            st.markdown(
                "<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Spend vs. Revenue correlation</span>",
                unsafe_allow_html=True,
            )
            scatter_df = df.groupby(["date", dimension_col], as_index=False).agg({"spend": "sum", "revenue": "sum"})
            fig_scatter = px.scatter(scatter_df, x="spend", y="revenue", color_discrete_sequence=["#38bdf8"])
            fig_scatter.update_layout(PLOTLY_THEME_LAYOUT)
            fig_scatter.update_traces(marker=dict(size=8, opacity=0.75, line=dict(width=1, color="rgba(255,255,255,0.2)")))
            st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})


if __name__ == "__main__":
    main()
