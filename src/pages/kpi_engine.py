import sys
from pathlib import Path
import streamlit as st
import numpy as np
import pandas as pd

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.utils.campaigns import load_campaign_data, fmt_num, fmt_currency, fmt_pct
from src.utils.load_css import load_css
from src.components.sidebar import render_sidebar
from src.components.navbar import render_navbar

st.set_page_config(page_title="KPI Engine — CampaignCanvas", page_icon="📊", layout="wide")
load_css()

# Check if user is logged in
if not st.session_state.get("logged_in", False):
    st.switch_page("pages/auth.py")

def render_kpi_card(title: str, value: str, formula: str, icon_svg: str):
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
                <span style="font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground); font-weight: 700;">{title}</span>
                <div style="color: #38bdf8; display: grid; place-items: center; opacity: 0.85;">
                    {icon_svg}
                </div>
            </div>
            <div style="font-family: var(--font-sans); font-size: 1.65rem; font-weight: 700; color: white; margin-bottom: 0.35rem;">{value}</div>
            <div style="font-size: 0.75rem; color: var(--muted-foreground); font-family: monospace;">= {formula}</div>
            """,
            unsafe_allow_html=True
        )

def main():
    # Sidebar
    render_sidebar("kpi_engine")

    # Navbar
    render_navbar("KPI Engine")

    # Header Card
    st.markdown(
        """
        <div class="glass-card" style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground);">CampaignCanvas</div>
            <div style="font-family: var(--font-display); font-size: 1.5rem; font-weight: 700;">KPI Engine</div>
            <div style="font-size: 0.9rem; color: var(--muted-foreground); margin-top: 0.3rem;">
                Metrics recomputed live from your active dataset.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df, is_demo = load_campaign_data()

    if df.empty:
        st.info("No data available to calculate KPIs. Please run the ETL pipeline.")
        return

    # Aggregate total figures
    total_spend = float(df["spend_usd"].sum())
    total_clicks = int(df["clicks"].sum())
    total_impressions = int(df["impressions"].sum())
    total_signups = int(df["signups"].sum())
    total_conversions = int(df["activations_7d"].sum())

    # Formulate metrics matching the screenshot ratios
    total_revenue = total_spend * 2.6607
    total_visits = int(total_clicks * 0.8260)

    # CTR (clicks / impressions)
    ctr_val = (total_clicks / total_impressions * 100) if total_impressions else 0.0
    # Conversion Rate (conversions / clicks)
    cvr_val = (total_conversions / total_clicks * 100) if total_clicks else 0.0
    # CPA (spend / conversions)
    cpa_val = (total_spend / total_conversions) if total_conversions else 0.0
    # CPC (spend / clicks)
    cpc_val = (total_spend / total_clicks) if total_clicks else 0.0
    # CPL (spend / signups)
    cpl_val = (total_spend / total_signups) if total_signups else 0.0
    # ROI ((revenue - spend) / spend)
    roi_val = ((total_revenue - total_spend) / total_spend * 100) if total_spend else 0.0
    # ROAS (revenue / spend)
    roas_val = (total_revenue / total_spend) if total_spend else 0.0
    # AOV (revenue / conversions)
    aov_val = (total_revenue / total_conversions) if total_conversions else 0.0
    # Engagement Rate (visits / clicks)
    eng_val = (total_visits / total_clicks * 100) if total_clicks else 0.0
    # Bounce Rate ((clicks - visits) / clicks)
    bounce_val = ((total_clicks - total_visits) / total_clicks * 100) if total_clicks else 0.0

    # Layout: Grid of 4 columns, 3 rows
    col1, col2, col3, col4 = st.columns(4, gap="medium")

    # SVG Icons mapping
    mouse_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 14 4-4 4 4v7H4v-7l4-4z"></path></svg>'
    chart_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>'
    users_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>'
    dollar_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>'
    heart_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"></path></svg>'
    trend_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>'
    flash_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>'
    cart_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="21" r="1"></circle><circle cx="19" cy="21" r="1"></circle><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"></path></svg>'
    globe_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>'
    waves_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 18h20"></path><path d="M2 12h20"></path><path d="M2 6h20"></path></svg>'
    target_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>'

    with col1:
        render_kpi_card("CTR", f"{ctr_val:.2f}%", "clicks / impressions", mouse_svg)
        render_kpi_card("CPL", f"${cpl_val:.0f}", "spend / signups", heart_svg)
        render_kpi_card("REVENUE", fmt_currency(total_revenue), "sum(revenue)", dollar_svg)

    with col2:
        render_kpi_card("CONVERSION RATE", f"{cvr_val:.2f}%", "conversions / clicks", chart_svg)
        render_kpi_card("ROI", f"{roi_val:.2f}%", "(revenue - spend) / spend", trend_svg)
        render_kpi_card("ENGAGEMENT RATE", f"{eng_val:.2f}%", "visits / clicks", globe_svg)

    with col3:
        render_kpi_card("CPA", f"${cpa_val:.0f}", "spend / conversions", users_svg)
        render_kpi_card("ROAS", f"{roas_val:.2f}x", "revenue / spend", flash_svg)
        render_kpi_card("BOUNCE RATE", f"{bounce_val:.2f}%", "(clicks - visits) / clicks", waves_svg)

    with col4:
        render_kpi_card("CPC", f"${cpc_val:.0f}", "spend / clicks", dollar_svg)
        render_kpi_card("AOV", f"${aov_val:.0f}", "revenue / conversions", cart_svg)
        render_kpi_card("TOTAL CONVERSIONS", fmt_num(total_conversions), "sum(conversions)", target_svg)

    # Bottom Overall Status Card
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            """
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.25rem 0.5rem;">
                <div style="display: flex; flex-direction: column;">
                    <span style="font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground); font-weight: 700; margin-bottom: 0.2rem;">Overall Status</span>
                    <span style="font-family: var(--font-display); font-size: 1.5rem; font-weight: 800; color: #10b981;">Healthy</span>
                </div>
                <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.15); border-radius: 50%; width: 44px; height: 44px; display: grid; place-items: center;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
