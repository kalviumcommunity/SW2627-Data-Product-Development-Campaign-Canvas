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

st.set_page_config(page_title="Activation Funnel — CampaignIQ", page_icon="📊", layout="wide")
load_css()

def main():
    st.markdown(
        """
        <div class="glass-card" style="margin-bottom: 1rem;">
            <div style="font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground);">CampaignIQ</div>
            <div style="font-family: var(--font-display); font-size: 1.5rem; font-weight: 700;">Conversion Funnel Analysis</div>
            <div style="font-size: 0.9rem; color: var(--muted-foreground); margin-top: 0.3rem;">
                Track the user journey from impressions to downstream activation milestones.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    frame, is_demo = load_campaign_data()
    if frame.empty:
        st.info("No data available to render the funnel. Please run the ETL pipeline.")
        return

    # Sidebar / Top filters
    col1, col2, col3 = st.columns(3)
    with col1:
        platforms = ["All Platforms"] + list(frame["ad_platform"].unique())
        selected_platform = st.selectbox("Filter by Ad Platform", platforms)
    with col2:
        dates = pd.to_datetime(frame["date"])
        min_date, max_date = dates.min(), dates.max()
        selected_date_range = st.date_input("Filter by Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
    with col3:
        campaign_search = st.text_input("Search Campaigns", "")

    # Apply filters
    filtered_df = frame.copy()
    if selected_platform != "All Platforms":
        filtered_df = filtered_df[filtered_df["ad_platform"] == selected_platform]
    
    if len(selected_date_range) == 2:
        start_date, end_date = selected_date_range
        filtered_df = filtered_df[
            (pd.to_datetime(filtered_df["date"]) >= pd.to_datetime(start_date)) & 
            (pd.to_datetime(filtered_df["date"]) <= pd.to_datetime(end_date))
        ]
        
    if campaign_search:
        filtered_df = filtered_df[
            filtered_df["campaign_name"].str.contains(campaign_search, case=False) |
            filtered_df["campaign_id"].str.contains(campaign_search, case=False)
        ]

    # Calculate Funnel Steps
    total_impressions = int(filtered_df["impressions"].sum())
    total_clicks = int(filtered_df["clicks"].sum())
    total_signups = int(filtered_df["signups"].sum())
    total_profile_completed = int(filtered_df["profile_completed"].sum())
    total_activations = int(filtered_df["activations_7d"].sum())

    # Rates
    ctr = total_clicks / total_impressions if total_impressions else 0
    click_to_signup = total_signups / total_clicks if total_clicks else 0
    signup_to_profile = total_profile_completed / total_signups if total_signups else 0
    profile_to_activation = total_activations / total_profile_completed if total_profile_completed else 0
    signup_to_activation = total_activations / total_signups if total_signups else 0

    # Layout for Funnel
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown('<div class="glass-card" style="padding: 1.5rem;">', unsafe_allow_html=True)
        st.markdown('<div style="font-family: var(--font-display); font-weight: 700; margin-bottom: 1rem;">User Journey Funnel</div>', unsafe_allow_html=True)

        # Plotly Funnel Chart
        funnel_stages = [
            "Impressions", 
            "Clicks", 
            "Signups", 
            "Profile Completed", 
            "Activations (7D)"
        ]
        funnel_values = [
            total_impressions, 
            total_clicks, 
            total_signups, 
            total_profile_completed, 
            total_activations
        ]

        fig = go.Figure(go.Funnel(
            y=funnel_stages,
            x=funnel_values,
            textinfo="value+percent initial",
            connector=dict(fillcolor="rgba(56, 189, 248, 0.2)"),
            marker=dict(
                color=["#0ea5e9", "#0284c7", "#6366f1", "#818cf8", "#10b981"],
                line=dict(width=0)
            )
        ))

        fig.update_layout(
            height=400,
            margin=dict(l=40, r=40, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f3f4f6", family="Inter")
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass-card" style="padding: 1.5rem; height: 100%;">', unsafe_allow_html=True)
        st.markdown('<div style="font-family: var(--font-display); font-weight: 700; margin-bottom: 1rem;">Conversion Milestones</div>', unsafe_allow_html=True)

        milestones = [
            ("Click-Through Rate (CTR)", fmt_pct(ctr), f"{fmt_num(total_clicks)} clicks from {fmt_num(total_impressions)} impressions"),
            ("Click-to-Signup Rate", fmt_pct(click_to_signup), f"{fmt_num(total_signups)} signups from {fmt_num(total_clicks)} clicks"),
            ("Signup-to-Profile Rate", fmt_pct(signup_to_profile), f"{fmt_num(total_profile_completed)} profiles setup from {fmt_num(total_signups)} signups"),
            ("Profile-to-Activation Rate", fmt_pct(profile_to_activation), f"{fmt_num(total_activations)} activated users out of {fmt_num(total_profile_completed)} completed profiles"),
            ("Overall Signup-to-Activation Rate", fmt_pct(signup_to_activation), f"Total active conversion rate of marketing campaigns")
        ]

        for title, val, desc in milestones:
            st.markdown(
                f"""
                <div style="padding: 0.75rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.85rem; color: var(--muted-foreground); font-weight: 500;">{title}</span>
                        <span style="font-family: var(--font-display); font-weight: 700; color: #38bdf8;">{val}</span>
                    </div>
                    <div style="font-size: 0.75rem; color: var(--muted-foreground); margin-top: 0.15rem;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
