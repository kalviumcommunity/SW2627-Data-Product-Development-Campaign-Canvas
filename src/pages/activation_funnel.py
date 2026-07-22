import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.utils.campaigns import load_campaign_data, fmt_num, fmt_pct
from src.utils.load_css import load_css
from src.components.sidebar import render_sidebar
from src.components.navbar import render_navbar

st.set_page_config(page_title="Funnel Analysis — CampaignCanvas", page_icon="📊", layout="wide")
load_css()

# Check if user is logged in
if not st.session_state.get("logged_in", False):
    st.switch_page("pages/auth.py")

def main():
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

    df, is_demo = load_campaign_data()

    if df.empty:
        st.info("No data available to construct the conversion funnel. Please run the ETL pipeline.")
        return

    # Aggregate funnel milestones
    total_impressions = int(df["impressions"].sum())
    total_clicks = int(df["clicks"].sum())
    total_visits = int(total_clicks * 0.8260)
    total_signups = int(df["signups"].sum())
    total_conversions = int(df["activations_7d"].sum())  # Purchases
    total_retained = int(df["profile_completed"].sum())    # Retained

    # Rates
    click_conv = (total_clicks / total_impressions) if total_impressions else 0.0
    click_drop = total_impressions - total_clicks
    click_drop_pct = (click_drop / total_impressions * 100) if total_impressions else 0.0

    visit_conv = (total_visits / total_clicks) if total_clicks else 0.0
    visit_drop = total_clicks - total_visits
    visit_drop_pct = (visit_drop / total_clicks * 100) if total_clicks else 0.0

    signup_conv = (total_signups / total_visits) if total_visits else 0.0
    signup_drop = total_visits - total_signups
    signup_drop_pct = (signup_drop / total_visits * 100) if total_visits else 0.0

    purchase_conv = (total_conversions / total_signups) if total_signups else 0.0
    purchase_drop = total_signups - total_conversions
    purchase_drop_pct = (purchase_drop / total_signups * 100) if total_signups else 0.0

    retain_conv = (total_retained / total_conversions) if total_conversions else 0.0
    retain_drop = total_conversions - total_retained
    retain_drop_pct = (retain_drop / total_conversions * 100) if total_conversions else 0.0

    # 1. Conversion Funnel Chart Section
    with st.container(border=True):
        st.markdown("<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Conversion funnel</span>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

        funnel_stages = [
            "Impressions",
            "Clicks",
            "Website visits",
            "Signups",
            "Purchases",
            "Retained"
        ]
        funnel_values = [
            total_impressions,
            total_clicks,
            total_visits,
            total_signups,
            total_conversions,
            total_retained
        ]

        fig_funnel = go.Figure(go.Funnel(
            y=funnel_stages,
            x=funnel_values,
            textinfo="value",
            connector=dict(fillcolor="rgba(56, 189, 248, 0.1)"),
            marker=dict(
                color=["#0ea5e9", "#06b6d4", "#10b981", "#f59e0b", "#a855f7", "#ec4899"],
                line=dict(width=0)
            )
        ))

        theme = st.session_state.get("theme", "dark")
        text_color = "#1e293b" if theme == "light" else "#e2e8f0"

        fig_funnel.update_layout(
            height=380,
            margin=dict(l=60, r=60, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=text_color, family="Inter, sans-serif")
        )
        st.plotly_chart(fig_funnel, use_container_width=True, config={"displayModeBar": False})

    # 2. Stage-by-stage drop-off section
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("<span style='font-family: var(--font-display); font-weight: 700; color: white;'>Stage-by-stage drop-off</span>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        # Impressions Card
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="padding: 0.15rem 0;">
                    <span style="font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground); font-weight: 700;">Impressions</span>
                    <div style="font-family: var(--font-sans); font-size: 1.6rem; font-weight: 700; color: white; margin-top: 0.3rem;">{fmt_num(total_impressions)}</div>
                    <div style="font-size: 0.78rem; color: var(--muted-foreground); margin-top: 0.5rem; visibility: hidden;">placeholder to align layout height</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        # Signups Card
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="padding: 0.15rem 0;">
                    <span style="font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground); font-weight: 700;">Signups</span>
                    <div style="font-family: var(--font-sans); font-size: 1.6rem; font-weight: 700; color: white; margin-top: 0.3rem;">{fmt_num(total_signups)}</div>
                    <div style="font-size: 0.78rem; margin-top: 0.5rem;">
                        <span style="color: #10b981;">Conversion: {signup_conv*100:.2f}%</span>
                        <span style="color: var(--muted-foreground); margin-left: 0.5rem;">Drop-off: {fmt_num(signup_drop)} ({signup_drop_pct:.2f}%)</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with col2:
        # Clicks Card
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="padding: 0.15rem 0;">
                    <span style="font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground); font-weight: 700;">Clicks</span>
                    <div style="font-family: var(--font-sans); font-size: 1.6rem; font-weight: 700; color: white; margin-top: 0.3rem;">{fmt_num(total_clicks)}</div>
                    <div style="font-size: 0.78rem; margin-top: 0.5rem;">
                        <span style="color: #10b981;">Conversion: {click_conv*100:.2f}%</span>
                        <span style="color: var(--muted-foreground); margin-left: 0.5rem;">Drop-off: {fmt_num(click_drop)} ({click_drop_pct:.2f}%)</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        # Purchases Card
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="padding: 0.15rem 0;">
                    <span style="font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground); font-weight: 700;">Purchases</span>
                    <div style="font-family: var(--font-sans); font-size: 1.6rem; font-weight: 700; color: white; margin-top: 0.3rem;">{fmt_num(total_conversions)}</div>
                    <div style="font-size: 0.78rem; margin-top: 0.5rem;">
                        <span style="color: #10b981;">Conversion: {purchase_conv*100:.2f}%</span>
                        <span style="color: var(--muted-foreground); margin-left: 0.5rem;">Drop-off: {fmt_num(purchase_drop)} ({purchase_drop_pct:.2f}%)</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with col3:
        # Website Visits Card
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="padding: 0.15rem 0;">
                    <span style="font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground); font-weight: 700;">Website Visits</span>
                    <div style="font-family: var(--font-sans); font-size: 1.6rem; font-weight: 700; color: white; margin-top: 0.3rem;">{fmt_num(total_visits)}</div>
                    <div style="font-size: 0.78rem; margin-top: 0.5rem;">
                        <span style="color: #10b981;">Conversion: {visit_conv*100:.2f}%</span>
                        <span style="color: var(--muted-foreground); margin-left: 0.5rem;">Drop-off: {fmt_num(visit_drop)} ({visit_drop_pct:.2f}%)</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        # Retained Card
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="padding: 0.15rem 0;">
                    <span style="font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground); font-weight: 700;">Retained</span>
                    <div style="font-family: var(--font-sans); font-size: 1.6rem; font-weight: 700; color: white; margin-top: 0.3rem;">{fmt_num(total_retained)}</div>
                    <div style="font-size: 0.78rem; margin-top: 0.5rem;">
                        <span style="color: #10b981;">Conversion: {retain_conv*100:.2f}%</span>
                        <span style="color: var(--muted-foreground); margin-left: 0.5rem;">Drop-off: {fmt_num(retain_drop)} ({retain_drop_pct:.2f}%)</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

if __name__ == "__main__":
    main()
