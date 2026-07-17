import sys
from pathlib import Path
import time
import streamlit as st

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.utils.load_css import load_css
from src.components.sidebar import render_sidebar

st.set_page_config(page_title="Reports — CampaignCanvas", page_icon="📊", layout="wide")
load_css()

# Check if user is logged in
if not st.session_state.get("logged_in", False):
    st.switch_page("pages/auth.py")

def render_report_card(title: str, desc: str, key_id: str):
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display: flex; align-items: flex-start; gap: 0.75rem; margin-bottom: 0.75rem;">
                <div style="width: 40px; height: 40px; border-radius: 0.5rem; background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.12); display: grid; place-items: center;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><line x1="10" y1="9" x2="8" y2="9"></line></svg>
                </div>
                <div style="display: flex; flex-direction: column;">
                    <span style="font-family: var(--font-display); font-size: 1.1rem; font-weight: 700; color: white;">{title}</span>
                    <span style="font-size: 0.85rem; color: var(--muted-foreground); margin-top: 0.2rem; min-height: 2.2rem;">{desc}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Action button
        st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
        generate_clicked = st.button("Generate", key=f"gen_{key_id}", use_container_width=True)
        if generate_clicked:
            with st.spinner(f"Compiling {title}..."):
                time.sleep(1.2)
            st.toast(f"{title} successfully generated!", icon="🎉")

def main():
    # Sidebar
    render_sidebar("reports")

    # Header Card
    st.markdown(
        """
        <div class="glass-card" style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground);">CampaignCanvas</div>
            <div style="font-family: var(--font-display); font-size: 1.5rem; font-weight: 700;">Reports</div>
            <div style="font-size: 0.9rem; color: var(--muted-foreground); margin-top: 0.3rem;">
                Generate and download executive summaries, KPI breakdowns, or raw spreadsheets.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3x2 Grid layout
    row1_col1, row1_col2, row1_col3 = st.columns(3, gap="medium")
    
    with row1_col1:
        render_report_card("Executive PDF", "One-page summary of headline KPIs.", "exec_pdf")
    with row1_col2:
        render_report_card("Summary PDF", "KPIs + top campaigns breakdown.", "sum_pdf")
    with row1_col3:
        render_report_card("Detailed PDF", "Full campaign table + KPIs.", "detail_pdf")

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    row2_col1, row2_col2, row2_col3 = st.columns(3, gap="medium")
    
    with row2_col1:
        render_report_card("CSV export", "Raw dataset for spreadsheets.", "csv_export")
    with row2_col2:
        render_report_card("Excel workbook", "Data + aggregated views.", "excel_wb")
    with row2_col3:
        # Keep empty to match the 3-column spacing layout of row 1
        pass

if __name__ == "__main__":
    main()
