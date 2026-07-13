import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.utils.campaigns import load_campaign_data, fmt_currency, fmt_num, fmt_pct, aggregate_by
from src.utils.load_css import load_css
from src.components.sidebar import render_sidebar

st.set_page_config(page_title="Campaign Performance Analysis — CampaignIQ", page_icon="📊", layout="wide")
load_css()

# Check if user is logged in
if not st.session_state.get("logged_in", False):
    st.switch_page("pages/auth.py")

def main():
    # Sidebar
    render_sidebar("campaign_analysis")
    st.markdown(
        """
        <div class="glass-card" style="margin-bottom: 1rem;">
            <div style="font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground);">CampaignIQ</div>
            <div style="font-family: var(--font-display); font-size: 1.5rem; font-weight: 700;">Campaign Performance & Wasted Spend Audit</div>
            <div style="font-size: 0.9rem; color: var(--muted-foreground); margin-top: 0.3rem;">
                Audit ad campaigns, track CPAU (Cost per Activated User), and flag low-yield budget items.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    frame, is_demo = load_campaign_data()
    if frame.empty:
        st.info("No data available to render campaign analysis. Please run the ETL pipeline.")
        return

    # Filter columns
    col1, col2 = st.columns(2)
    with col1:
        platforms = ["All Platforms"] + list(frame["ad_platform"].unique())
        selected_platform = st.selectbox("Platform filter", platforms)
    with col2:
        campaign_search = st.text_input("Campaign name search", "")

    # Filter logic
    filtered_df = frame.copy()
    if selected_platform != "All Platforms":
        filtered_df = filtered_df[filtered_df["ad_platform"] == selected_platform]
    if campaign_search:
        filtered_df = filtered_df[
            filtered_df["campaign_name"].str.contains(campaign_search, case=False) |
            filtered_df["campaign_id"].str.contains(campaign_search, case=False)
        ]

    # Aggregate by campaign
    campaign_data = aggregate_by(filtered_df, "campaign_id")
    if campaign_data.empty:
        st.info("No campaign records match your search filters.")
        return

    # Calculate audit metrics
    # Flag campaigns where activation rate is < 10%
    campaign_data["is_underperforming"] = campaign_data["activation_rate"] < 0.10
    
    total_spend = campaign_data["spend_usd"].sum()
    wasted_campaigns = campaign_data[campaign_data["is_underperforming"]]
    total_wasted_spend = wasted_campaigns["spend_usd"].sum()
    wasted_pct = (total_wasted_spend / total_spend * 100) if total_spend else 0.0

    # Display audit cards
    stat_col1, stat_col2, stat_col3 = st.columns(3)
    with stat_col1:
        st.metric(
            label="Total Audited Spend",
            value=fmt_currency(total_spend)
        )
    with stat_col2:
        st.metric(
            label="Wasted Ad Spend (<10% Activation)",
            value=fmt_currency(total_wasted_spend),
            delta=f"{wasted_pct:.1f}% of total spend",
            delta_color="inverse"
        )
    with stat_col3:
        st.metric(
            label="Flagged Campaigns",
            value=f"{len(wasted_campaigns)} / {len(campaign_data)}",
            delta="Requiring immediate pause/reduction",
            delta_color="off"
        )

    # Underperforming Alert
    if not wasted_campaigns.empty:
        st.error(
            f"⚠️ Found **{len(wasted_campaigns)} campaigns** with downstream activation rates **under 10%**. "
            f"Pausing or reallocating budget away from these campaigns could save up to **{fmt_currency(total_wasted_spend)}**."
        )

    # Detailed Table
    st.markdown('<div class="glass-card" style="padding: 1.5rem; margin-top: 1rem;">', unsafe_allow_html=True)
    st.markdown('<div style="font-family: var(--font-display); font-weight: 700; margin-bottom: 0.5rem;">Performance Audit Table</div>', unsafe_allow_html=True)
    st.caption("Campaigns sorted by total spend. High CPAU and low activation rate campaigns are flagged below.")

    # Format dataframe for display
    display_table = campaign_data.copy()
    
    def flag_activation_rate(row):
        pct_str = f"{row['activation_rate']*100:.1f}%"
        if row["is_underperforming"]:
            return f"⚠️ {pct_str} (Low)"
        return pct_str

    def flag_cpau(row):
        cpau_str = fmt_currency(row["cpau"])
        if row["is_underperforming"]:
            return f"🚨 {cpau_str}"
        return cpau_str

    display_table["Activation Rate"] = display_table.apply(flag_activation_rate, axis=1)
    display_table["CPAU ($/Act)"] = display_table.apply(flag_cpau, axis=1)
    display_table["Spend ($)"] = display_table["spend_usd"].map(fmt_currency)
    display_table["Signups"] = display_table["signups"].map(fmt_num)
    display_table["Activations"] = display_table["activations_7d"].map(fmt_num)
    display_table["Platform"] = display_table["ad_platform"].str.replace("_", " ").str.title()
    
    display_cols = ["display_name", "Platform", "Spend ($)", "Signups", "Activations", "Activation Rate", "CPAU ($/Act)"]
    rename_dict = {
        "display_name": "Campaign Name",
    }
    
    display_table_final = display_table[display_cols].rename(columns=rename_dict)
    
    st.dataframe(display_table_final, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Platform Breakdown charts
    st.markdown('<div class="glass-card" style="padding: 1.5rem; margin-top: 1rem;">', unsafe_allow_html=True)
    st.markdown('<div style="font-family: var(--font-display); font-weight: 700; margin-bottom: 1rem;">Platform-Level Performance</div>', unsafe_allow_html=True)
    
    platform_data = aggregate_by(filtered_df, "ad_platform")
    if not platform_data.empty:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            # Spend vs Activations by platform
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(x=platform_data["name"].str.replace("_", " ").str.title(), y=platform_data["spend_usd"], name="Spend ($)", marker_color="#0ea5e9"))
            fig_bar.add_trace(go.Bar(x=platform_data["name"].str.replace("_", " ").str.title(), y=platform_data["activations_7d"] * 10, name="Activations x10", marker_color="#10b981"))
            fig_bar.update_layout(
                height=300,
                barmode="group",
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(title=None),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", title=None),
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
            
        with col_c2:
            # CPAU Comparison by platform
            fig_line = go.Figure()
            fig_line.add_trace(go.Bar(
                x=platform_data["name"].str.replace("_", " ").str.title(), 
                y=platform_data["cpau"], 
                text=[fmt_currency(val) for val in platform_data["cpau"]],
                textposition='auto',
                marker_color="#f59e0b"
            ))
            fig_line.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(title=None),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", title="CPAU ($)")
            )
            st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})
            
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
