from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.components.sidebar import render_sidebar
from src.utils.campaigns import aggregate_by, fmt_currency, load_campaign_data
from src.utils.load_css import load_css, get_plotly_layout

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
    campaign_text = frame["campaign_id"].astype(str).str.lower() if "campaign_id" in frame.columns else pd.Series("", index=frame.index)
    platform_text = frame["ad_platform"].astype(str).str.lower() if "ad_platform" in frame.columns else pd.Series("", index=frame.index)

    def _pick_channel(campaign_id: str, campaign_name: str) -> str:
        if any(token in campaign_id or token in campaign_name for token in ["email", "mailchimp", "klaviyo"]):
            return "Email"
        if any(token in campaign_id or token in campaign_name for token in ["youtube", "video"]):
            return "Video"
        if any(token in campaign_id or token in campaign_name for token in ["display", "remarketing"]):
            return "Display"
        if any(token in campaign_id or token in campaign_name for token in ["brand", "search"]):
            return "Search"
        return "Social"

    def _pick_region(campaign_id: str) -> str:
        if "brand" in campaign_id:
            return "US"
        if "nonbrand" in campaign_id or "retarget" in campaign_id:
            return "EU"
        if "prospect" in campaign_id or "leadgen" in campaign_id:
            return "LATAM"
        return "APAC"

    def _pick_device(campaign_id: str) -> str:
        return "Mobile" if any(token in campaign_id for token in ["brand", "prospect", "instagram", "tiktok"]) else "Desktop"

    def _pick_platform(platform: str, campaign_id: str) -> str:
        if "google" in platform or "google" in campaign_id:
            return "Google"
        if "youtube" in campaign_id:
            return "YouTube"
        if "display" in campaign_id:
            return "Programmatic"
        if "meta" in platform or "meta" in campaign_id or "instagram" in campaign_id:
            return "Meta"
        if "linkedin" in campaign_id:
            return "LinkedIn"
        if "tiktok" in campaign_id:
            return "TikTok"
        if "pinterest" in campaign_id:
            return "Pinterest"
        return "Other"

    campaign_name_text = frame["campaign_name"].astype(str).str.lower() if "campaign_name" in frame.columns else campaign_text
    frame["channel"] = [_pick_channel(campaign_id, campaign_name) for campaign_id, campaign_name in zip(campaign_text, campaign_name_text)]
    frame["platform_grouped"] = [_pick_platform(platform, campaign_id) for platform, campaign_id in zip(platform_text, campaign_text)]
    frame["region"] = [_pick_region(campaign_id) for campaign_id in campaign_text]
    frame["device"] = [_pick_device(campaign_id) for campaign_id in campaign_text]
    frame["campaign"] = frame["campaign_name"] if "campaign_name" in frame.columns else frame["campaign_id"]
    frame["platform"] = frame["ad_platform"].astype(str).str.replace("_", " ").str.title()
    frame["conversions"] = frame["activations_7d"]
    frame["spend"] = frame["spend_usd"]
    frame["revenue"] = frame["revenue"] if "revenue" in frame.columns else frame["conversions"] * 133.72
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
    grouped["Activation rate"] = (grouped["activations_7d"] / grouped["signups"] * 100).fillna(0.0)

    col_donut, col_bar = st.columns(2, gap="large")
    with col_donut:
        with st.container(border=True):
            st.markdown(
                f"<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Signups by {dimension_col}</span>",
                unsafe_allow_html=True,
            )
            fig_donut = go.Figure(
                data=[
                    go.Pie(
                        labels=grouped["name"],
                        values=grouped["signups"],
                        hole=0.4,
                        marker=dict(colors=COLOR_PALETTE),
                    )
                ]
            )
            fig_donut.update_layout(get_plotly_layout())
            fig_donut.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    with col_bar:
        with st.container(border=True):
            st.markdown(
                f"<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Activation rate by {dimension_col}</span>",
                unsafe_allow_html=True,
            )
            fig_bar = px.bar(grouped, x="name", y="Activation rate", color_discrete_sequence=["#38bdf8"])
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

        display_df = grouped[["name", "impressions", "clicks", "CTR", "signups", "CVR", "activations_7d", "Activation rate", "spend_usd", "totalRevenue", "roas"]].copy()
        display_df = display_df.rename(
            columns={
                "name": dimension_col,
                "impressions": "Impressions",
                "clicks": "Clicks",
                "signups": "Conv.",
                "activations_7d": "Activations",
                "Activation rate": "Activation rate (%)",
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
        display_df["Activation rate (%)"] = display_df["Activation rate (%)"].map(_format_pct)
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    col_time, col_scatter = st.columns(2, gap="large")

    with col_time:
        with st.container(border=True):
            st.markdown(
                "<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Time-series — Signups and activations</span>",
                unsafe_allow_html=True,
            )
            daily_df = df.groupby("date", as_index=False).agg({"signups": "sum", "activations_7d": "sum"}).sort_values("date")
            if daily_df["date"].nunique() < 3:
                campaign_df = grouped[["name", "signups", "activations_7d"]].head(8).sort_values("signups", ascending=False)
                fig_line = go.Figure()
                fig_line.add_trace(go.Bar(x=campaign_df["name"], y=campaign_df["signups"], name="Signups", marker_color="#38bdf8"))
                fig_line.add_trace(go.Bar(x=campaign_df["name"], y=campaign_df["activations_7d"], name="Activations", marker_color="#10b981"))
                fig_line.update_layout(PLOTLY_THEME_LAYOUT, barmode="group")
            else:
                fig_line = go.Figure()
                fig_line.add_trace(go.Scatter(x=daily_df["date"], y=daily_df["signups"], name="Signups", mode="lines+markers", line=dict(color="#38bdf8", width=2.5)))
                fig_line.add_trace(go.Scatter(x=daily_df["date"], y=daily_df["activations_7d"], name="Activations", mode="lines+markers", line=dict(color="#10b981", width=2.5)))
                fig_line.update_layout(PLOTLY_THEME_LAYOUT)
            st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})

    with col_scatter:
        with st.container(border=True):
            st.markdown(
                "<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Spend vs. activations correlation</span>",
                unsafe_allow_html=True,
            )
            scatter_df = df.groupby(["date", dimension_col], as_index=False).agg({"spend": "sum", "activations_7d": "sum"})
            fig_scatter = px.scatter(scatter_df, x="spend", y="activations_7d", color_discrete_sequence=["#38bdf8"])
            fig_scatter.update_layout(PLOTLY_THEME_LAYOUT)
            fig_scatter.update_traces(marker=dict(size=8, opacity=0.75, line=dict(width=1, color="rgba(255,255,255,0.2)")))
            st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})


if __name__ == "__main__":
    main()
