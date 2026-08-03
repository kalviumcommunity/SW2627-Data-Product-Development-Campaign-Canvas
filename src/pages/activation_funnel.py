from __future__ import annotations

import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.components.navbar import render_navbar
from src.components.sidebar import render_sidebar
from src.utils.campaigns import fmt_num, load_campaign_data
from src.utils.clerk_auth import require_authentication
from src.utils.load_css import get_plotly_layout, load_css

st.set_page_config(
    page_title="Funnel Analysis — CampaignCanvas",
    page_icon=":material/bar_chart:",
    layout="wide",
)
load_css()

# Check if user is logged in
require_authentication()


def main() -> None:
    # Sidebar
    render_sidebar("activation_funnel")

    # Navbar
    render_navbar("Funnel Analysis")

    # Header Card
    st.markdown(
        """
        <div class="glass-card" style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground);">CampaignCanvas</div>
            <div style="font-family: var(--font-display); font-size: 1.5rem; font-weight: 700;">Funnel Analysis</div>
            <div style="font-size: 0.9rem; color: var(--muted-foreground); margin-top: 0.3rem;">
                Track the customer acquisition journey and analyze stage-by-stage conversion drop-offs.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df, _ = load_campaign_data()

    if df.empty:
        st.info("No data available to construct the conversion funnel. Please run the ETL pipeline.")
        return

    # Aggregate funnel milestones safely
    total_impressions = int(df["impressions"].sum()) if "impressions" in df.columns else 0
    total_clicks = int(df["clicks"].sum()) if "clicks" in df.columns else 0
    total_visits = int(total_clicks * 0.8260)
    total_signups = int(df["signups"].sum()) if "signups" in df.columns else 0
    total_conversions = (
        int(df["activations_7d"].sum())
        if "activations_7d" in df.columns
        else (int(df["conversions"].sum()) if "conversions" in df.columns else 0)
    )
    total_retained = (
        int(df["profile_completed"].sum()) if "profile_completed" in df.columns else int(total_conversions * 0.65)
    )

    # Calculate Conversion & Drop-off Rates
    click_conv = (total_clicks / total_impressions) if total_impressions else 0.0
    click_drop = max(0, total_impressions - total_clicks)
    click_drop_pct = (click_drop / total_impressions * 100) if total_impressions else 0.0

    visit_conv = (total_visits / total_clicks) if total_clicks else 0.0
    visit_drop = max(0, total_clicks - total_visits)
    visit_drop_pct = (visit_drop / total_clicks * 100) if total_clicks else 0.0

    signup_conv = (total_signups / total_visits) if total_visits else 0.0
    signup_drop = max(0, total_visits - total_signups)
    signup_drop_pct = (signup_drop / total_visits * 100) if total_visits else 0.0

    purchase_conv = (total_conversions / total_signups) if total_signups else 0.0
    purchase_drop = max(0, total_signups - total_conversions)
    purchase_drop_pct = (purchase_drop / total_signups * 100) if total_signups else 0.0

    retain_conv = (total_retained / total_conversions) if total_conversions else 0.0
    retain_drop = max(0, total_conversions - total_retained)
    retain_drop_pct = (retain_drop / total_conversions * 100) if total_conversions else 0.0

    # 1. Conversion Funnel Chart Section
    with st.container(border=True):
        st.markdown(
            "<span style='font-family: var(--font-display); font-weight: 700; color: var(--foreground);'>Conversion funnel</span>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

        funnel_stages = [
            "Impressions",
            "Clicks",
            "Website visits",
            "Signups",
            "Purchases",
            "Retained",
        ]
        funnel_values = [
            total_impressions,
            total_clicks,
            total_visits,
            total_signups,
            total_conversions,
            total_retained,
        ]

        fig_funnel = go.Figure(
            go.Funnel(
                y=funnel_stages,
                x=funnel_values,
                textinfo="value",
                connector=dict(fillcolor="rgba(56, 189, 248, 0.1)"),
                marker=dict(
                    color=["#0ea5e9", "#06b6d4", "#10b981", "#f59e0b", "#a855f7", "#ec4899"],
                    line=dict(width=0),
                ),
            )
        )

        layout = get_plotly_layout()
        layout.update(
            height=380,
            margin=dict(l=60, r=60, t=10, b=10),
        )
        fig_funnel.update_layout(layout)
        st.plotly_chart(fig_funnel, use_container_width=True, config={"displayModeBar": False})

    # 2. Stage-by-stage drop-off section
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<span style='font-family: var(--font-display); font-weight: 700; color: var(--foreground);'>Stage-by-stage drop-off</span>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        # Stage 1: Impressions
        st.markdown(
            f"""
            <div style="background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-xl); padding: 1.1rem; box-shadow: var(--shadow-card); margin-bottom: 1rem;">
                <span style="font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground); font-weight: 700;">1. Impressions</span>
                <div style="font-family: var(--font-sans); font-size: 1.6rem; font-weight: 700; color: var(--foreground); margin-top: 0.3rem;">{fmt_num(total_impressions)}</div>
                <div style="font-size: 0.78rem; color: var(--muted-foreground); margin-top: 0.5rem; min-height: 1.2rem;">Top of funnel baseline</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Stage 2: Clicks
        st.markdown(
            f"""
            <div style="background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-xl); padding: 1.1rem; box-shadow: var(--shadow-card); margin-bottom: 1rem;">
                <span style="font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground); font-weight: 700;">2. Clicks</span>
                <div style="font-family: var(--font-sans); font-size: 1.6rem; font-weight: 700; color: var(--foreground); margin-top: 0.3rem;">{fmt_num(total_clicks)}</div>
                <div style="font-size: 0.78rem; margin-top: 0.5rem;">
                    <span style="color: #10b981;">CTR: {click_conv * 100:.2f}%</span>
                    <span style="color: var(--muted-foreground); margin-left: 0.5rem;">Drop-off: {fmt_num(click_drop)} ({click_drop_pct:.2f}%)</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        # Stage 3: Website Visits
        st.markdown(
            f"""
            <div style="background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-xl); padding: 1.1rem; box-shadow: var(--shadow-card); margin-bottom: 1rem;">
                <span style="font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground); font-weight: 700;">3. Website Visits</span>
                <div style="font-family: var(--font-sans); font-size: 1.6rem; font-weight: 700; color: var(--foreground); margin-top: 0.3rem;">{fmt_num(total_visits)}</div>
                <div style="font-size: 0.78rem; margin-top: 0.5rem;">
                    <span style="color: #10b981;">Landing Rate: {visit_conv * 100:.2f}%</span>
                    <span style="color: var(--muted-foreground); margin-left: 0.5rem;">Drop-off: {fmt_num(visit_drop)} ({visit_drop_pct:.2f}%)</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Stage 4: Signups
        st.markdown(
            f"""
            <div style="background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-xl); padding: 1.1rem; box-shadow: var(--shadow-card); margin-bottom: 1rem;">
                <span style="font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground); font-weight: 700;">4. Signups</span>
                <div style="font-family: var(--font-sans); font-size: 1.6rem; font-weight: 700; color: var(--foreground); margin-top: 0.3rem;">{fmt_num(total_signups)}</div>
                <div style="font-size: 0.78rem; margin-top: 0.5rem;">
                    <span style="color: #10b981;">Signup Rate: {signup_conv * 100:.2f}%</span>
                    <span style="color: var(--muted-foreground); margin-left: 0.5rem;">Drop-off: {fmt_num(signup_drop)} ({signup_drop_pct:.2f}%)</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        # Stage 5: Purchases
        st.markdown(
            f"""
            <div style="background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-xl); padding: 1.1rem; box-shadow: var(--shadow-card); margin-bottom: 1rem;">
                <span style="font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground); font-weight: 700;">5. Purchases</span>
                <div style="font-family: var(--font-sans); font-size: 1.6rem; font-weight: 700; color: var(--foreground); margin-top: 0.3rem;">{fmt_num(total_conversions)}</div>
                <div style="font-size: 0.78rem; margin-top: 0.5rem;">
                    <span style="color: #10b981;">Activation: {purchase_conv * 100:.2f}%</span>
                    <span style="color: var(--muted-foreground); margin-left: 0.5rem;">Drop-off: {fmt_num(purchase_drop)} ({purchase_drop_pct:.2f}%)</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Stage 6: Retained
        st.markdown(
            f"""
            <div style="background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-xl); padding: 1.1rem; box-shadow: var(--shadow-card); margin-bottom: 1rem;">
                <span style="font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground); font-weight: 700;">6. Retained</span>
                <div style="font-family: var(--font-sans); font-size: 1.6rem; font-weight: 700; color: var(--foreground); margin-top: 0.3rem;">{fmt_num(total_retained)}</div>
                <div style="font-size: 0.78rem; margin-top: 0.5rem;">
                    <span style="color: #10b981;">Retention Rate: {retain_conv * 100:.2f}%</span>
                    <span style="color: var(--muted-foreground); margin-left: 0.5rem;">Drop-off: {fmt_num(retain_drop)} ({retain_drop_pct:.2f}%)</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
