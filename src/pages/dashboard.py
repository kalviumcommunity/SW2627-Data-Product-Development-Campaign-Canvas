from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.utils.campaigns import aggregate_by, compute_kpis, fmt_currency, fmt_num, fmt_pct, load_campaign_data
from src.utils.load_css import load_css

st.set_page_config(page_title="Dashboard — CampaignIQ", page_icon="📊", layout="wide")
load_css()

def _format_banner(is_demo: bool) -> str:
    if is_demo:
        return "Demo dataset loaded. Run the ETL pipeline with your raw datasets to update."
    return "Live dataset loaded from your workspace processed data directory."

def main() -> None:
    frame, is_demo = load_campaign_data()
    
    # Page Header
    st.markdown(
        f"""
        <div class="glass-card" style="display:flex;align-items:center;justify-content:space-between;gap:1rem;margin-bottom:1.5rem;">
            <div>
                <div style="font-size:0.75rem;letter-spacing:0.08em;text-transform:uppercase;color:var(--muted-foreground);">CampaignIQ Dashboard</div>
                <div style="font-family:var(--font-display);font-size:1.4rem;font-weight:700;">Campaign-to-Activation Analytics Canvas</div>
                <div style="font-size:0.9rem;color:var(--muted-foreground);margin-top:0.3rem;">{_format_banner(is_demo)}</div>
            </div>
            <div style="text-align:right;font-size:0.8rem;color:var(--muted-foreground);">Last Ingested: {datetime.now().strftime('%b %d, %H:%M UTC')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if frame.empty:
        st.info("No data available. Please place CSVs under data/raw/ and run the ETL pipeline.")
        return

    # Filters Section
    st.markdown('<div class="glass-card" style="padding: 1.25rem; margin-bottom: 1.5rem;">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:var(--font-display);font-size:0.9rem;font-weight:700;margin-bottom:0.75rem;">Global Filters</div>', unsafe_allow_html=True)
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        platforms = ["All Platforms"] + list(frame["ad_platform"].unique())
        selected_platform = st.selectbox("Ad Platform", platforms)
    with col_f2:
        dates = pd.to_datetime(frame["date"])
        min_date, max_date = dates.min(), dates.max()
        selected_date_range = st.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
    with col_f3:
        campaign_search = st.text_input("Campaign Search", "")
    st.markdown('</div>', unsafe_allow_html=True)

    # Filter implementation
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

    # Compute KPIs
    kpis = compute_kpis(filtered_df)

    # Display KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="TOTAL AD SPEND", value=fmt_currency(kpis["totalSpend"]))
    with col2:
        st.metric(label="SIGNUPS", value=fmt_num(kpis["totalSignups"]))
    with col3:
        activation_rate_str = fmt_pct(kpis["activationRate"])
        st.metric(label="ACTIVATIONS (7D)", value=fmt_num(kpis["totalActivations"]), delta=f"{activation_rate_str} Activation Rate", delta_color="normal")
    with col4:
        # Highlighting Wasted Spend in red/inverse delta if it exists
        wasted_delta = f"CPAU: {fmt_currency(kpis['cpau'])}" if kpis['totalActivations'] > 0 else None
        st.metric(label="EST. WASTED SPEND", value=fmt_currency(kpis["wastedSpend"]), delta=wasted_delta, delta_color="inverse")

    # Middle Section: Funnel Chart and Performance Summary
    left, right = st.columns([2, 1], gap="large")

    with left:
        st.markdown('<div class="glass-card" style="padding:1.25rem; height: 100%;">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:var(--font-display);font-weight:700;margin-bottom:0.25rem;">Conversion Funnel</div>', unsafe_allow_html=True)
        st.caption("Impressions to Downstream Activation Conversion")

        total_imp = filtered_df["impressions"].sum()
        total_clicks = filtered_df["clicks"].sum()
        total_signups = filtered_df["signups"].sum()
        total_acts = filtered_df["activations_7d"].sum()

        if total_imp == 0:
            st.info("No impressions recorded in this time range.")
        else:
            fig = go.Figure(go.Funnel(
                y=["Impressions", "Clicks", "Signups", "Activations (7D)"],
                x=[total_imp, total_clicks, total_signups, total_acts],
                textinfo="value+percent initial",
                connector=dict(fillcolor="rgba(99, 102, 241, 0.2)"),
                marker=dict(color=["#6366f1", "#818cf8", "#0284c7", "#10b981"])
            ))
            fig.update_layout(
                height=260,
                margin=dict(l=20, r=20, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f3f4f6", family="Inter")
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass-card" style="padding:1.25rem; height: 100%;">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:var(--font-display);font-weight:700;margin-bottom:0.25rem;">Campaign Performance Summary</div>', unsafe_allow_html=True)
        st.caption("Top platforms by conversion volume")

        by_platform = aggregate_by(filtered_df, "ad_platform")
        if by_platform.empty:
            st.info("No data available.")
        else:
            for _, row in by_platform.iterrows():
                p_name = str(row["name"]).replace("_", " ").title()
                p_spend = fmt_currency(row["spend_usd"])
                p_acts = int(row["activations_7d"])
                p_rate = fmt_pct(row["activation_rate"])
                
                st.markdown(
                    f"""
                    <div style="padding: 0.6rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
                        <div style="display:flex; justify-content:space-between; font-weight:600; font-size:0.875rem;">
                            <span>{p_name}</span>
                            <span>{p_acts} Activations</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:var(--muted-foreground); margin-top:0.2rem;">
                            <span>Spend: {p_spend}</span>
                            <span>Activation Rate: {p_rate}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        st.markdown("</div>", unsafe_allow_html=True)

    # Bottom Section: Audit Table
    st.markdown('<div class="glass-card" style="padding:1.25rem; margin-top:1.5rem;">', unsafe_allow_html=True)
    st.markdown('<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.25rem;">'
                '<div style="font-family:var(--font-display);font-weight:700;">Campaign Performance Audit Table</div>'
                '</div>', unsafe_allow_html=True)
    st.caption("All active marketing campaigns and their activation rates")

    by_campaign = aggregate_by(filtered_df, "campaign_id")
    if by_campaign.empty:
        st.info("No campaign data matching filters.")
    else:
        table_df = by_campaign.copy()
        
        # Flags poor performing campaigns (<10% activation rate)
        table_df["Status"] = table_df["activation_rate"].apply(lambda rate: "⚠️ Low Yield" if rate < 0.10 else "🟢 Active")
        table_df["spend_usd"] = table_df["spend_usd"].map(fmt_currency)
        table_df["signups"] = table_df["signups"].map(fmt_num)
        table_df["activations_7d"] = table_df["activations_7d"].map(fmt_num)
        table_df["activation_rate"] = table_df["activation_rate"].map(fmt_pct)
        table_df["cpau"] = table_df["cpau"].map(fmt_currency)
        table_df["ad_platform"] = table_df["ad_platform"].str.replace("_", " ").str.title()

        table_display = table_df.rename(columns={
            "display_name": "Campaign Name",
            "ad_platform": "Platform",
            "spend_usd": "Spend ($)",
            "signups": "Signups",
            "activations_7d": "Activations",
            "activation_rate": "Activation Rate",
            "cpau": "CPAU ($/Act)"
        })
        
        cols_to_show = ["Campaign Name", "Platform", "Spend ($)", "Signups", "Activations", "Activation Rate", "CPAU ($/Act)", "Status"]
        st.dataframe(table_display[cols_to_show], use_container_width=True, hide_index=True)
        
        # CSV download button
        csv_data = by_campaign.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Audit Table to CSV",
            data=csv_data,
            file_name="campaign_performance_audit.csv",
            mime="text/csv"
        )

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()