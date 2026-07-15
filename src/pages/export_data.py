import sys
from pathlib import Path
import pandas as pd
import streamlit as st

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.utils.campaigns import load_campaign_data, fmt_num
from src.utils.load_css import load_css
from src.components.sidebar import render_sidebar

st.set_page_config(page_title="Export Data — CampaignCanvas", page_icon="📊", layout="wide")
load_css()

# Check if user is logged in
if not st.session_state.get("logged_in", False):
    st.switch_page("pages/auth.py")

def main():
    # Sidebar
    render_sidebar("export_data")

    st.markdown(
        """
        <div class="glass-card" style="margin-bottom: 1rem;">
            <div style="font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground);">CampaignCanvas</div>
            <div style="font-family: var(--font-display); font-size: 1.5rem; font-weight: 700;">Data Export Workspace</div>
            <div style="font-size: 0.9rem; color: var(--muted-foreground); margin-top: 0.3rem;">
                Review, filter, and export the unified campaign performance and activation datasets for auditing.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    frame, is_demo = load_campaign_data()
    if frame.empty:
        st.info("No data available to export. Please run the ETL pipeline.")
        return

    # Export configuration filters
    st.markdown('<div class="glass-card" style="padding: 1.5rem; margin-bottom: 1rem;">', unsafe_allow_html=True)
    st.markdown('<div style="font-family: var(--font-display); font-weight: 700; margin-bottom: 1rem;">Export Configuration</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        platforms = ["All Platforms"] + list(frame["ad_platform"].unique())
        selected_platform = st.selectbox("Ad Platform Filter", platforms)
    with col2:
        dates = pd.to_datetime(frame["date"])
        min_date, max_date = dates.min(), dates.max()
        selected_date_range = st.date_input("Date Period Filter", [min_date, max_date], min_value=min_date, max_value=max_date)
    with col3:
        file_format = st.selectbox("Export File Format", ["CSV (.csv)", "JSON (.json)"])

    # Filter logic
    filtered_df = frame.copy()
    if selected_platform != "All Platforms":
        filtered_df = filtered_df[filtered_df["ad_platform"] == selected_platform]
    
    if len(selected_date_range) == 2:
        start_date, end_date = selected_date_range
        filtered_df = filtered_df[
            (pd.to_datetime(filtered_df["date"]) >= pd.to_datetime(start_date)) & 
            (pd.to_datetime(filtered_df["date"]) <= pd.to_datetime(end_date))
        ]
        
    st.markdown("</div>", unsafe_allow_html=True)

    # Show dataset stats
    stat_col1, stat_col2, stat_col3 = st.columns(3)
    with stat_col1:
        st.metric("Total Records Found", fmt_num(len(filtered_df)))
    with stat_col2:
        memory_usage_kb = filtered_df.memory_usage(deep=True).sum() / 1024
        st.metric("Export Memory Footprint", f"{memory_usage_kb:.2f} KB")
    with stat_col3:
        campaign_count = filtered_df["campaign_id"].nunique()
        st.metric("Unique Campaigns Included", fmt_num(campaign_count))

    # Dataset Preview & Download Action
    st.markdown('<div class="glass-card" style="padding: 1.5rem; margin-top: 1rem;">', unsafe_allow_html=True)
    st.markdown('<div style="font-family: var(--font-display); font-weight: 700; margin-bottom: 0.5rem;">Dataset Preview</div>', unsafe_allow_html=True)
    st.caption("First 15 records of the filtered cohort.")
    st.dataframe(filtered_df.head(15), use_container_width=True, hide_index=True)
    
    # Download Button Trigger
    st.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
    if "CSV" in file_format:
        data_to_download = filtered_df.to_csv(index=False).encode('utf-8')
        mime_type = 'text/csv'
        filename = f"campaign_activation_export_{selected_platform.lower().replace(' ', '_')}.csv"
    else:
        data_to_download = filtered_df.to_json(orient="records", indent=2).encode('utf-8')
        mime_type = 'application/json'
        filename = f"campaign_activation_export_{selected_platform.lower().replace(' ', '_')}.json"

    st.download_button(
        label=f"📥 Download Filtered Dataset ({file_format.split(' ')[0]})",
        data=data_to_download,
        file_name=filename,
        mime=mime_type,
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
