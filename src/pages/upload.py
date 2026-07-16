import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.utils.load_css import load_css
from src.components.sidebar import render_sidebar

st.set_page_config(page_title="Upload Dataset — CampaignCanvas", page_icon="📊", layout="wide")
load_css()

# Check if user is logged in
if not st.session_state.get("logged_in", False):
    st.switch_page("pages/auth.py")

# Initialize session state for upload history
if "upload_history" not in st.session_state:
    st.session_state.upload_history = [
        {
            "filename": "ad_campaign_metrics.csv",
            "size": "42.5 KB",
            "type": "CSV",
            "status": "Processed",
            "timestamp": "2026-07-16 10:14"
        },
        {
            "filename": "hubspot_signups.csv",
            "size": "112.8 KB",
            "type": "CSV",
            "status": "Processed",
            "timestamp": "2026-07-16 10:14"
        },
        {
            "filename": "product_activations.csv",
            "size": "84.1 KB",
            "type": "CSV",
            "status": "Processed",
            "timestamp": "2026-07-16 10:14"
        }
    ]

def format_size(bytes_size):
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.1f} MB"

def main():
    # Sidebar
    render_sidebar("upload")

    # Header Card
    st.markdown(
        """
        <div class="glass-card" style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground);">CampaignCanvas</div>
            <div style="font-family: var(--font-display); font-size: 1.5rem; font-weight: 700;">Upload Dataset</div>
            <div style="font-size: 0.9rem; color: var(--muted-foreground); margin-top: 0.3rem;">
                Ingest new campaign performance and activation data files into the workspace.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Main Grid (Upload Card and History Panel)
    col_upload, col_space = st.columns([2, 1])

    with col_upload:
        # Dropzone File Uploader
        with st.container(border=True):
            st.markdown(
                """
                <div style="text-align: center; padding: 1.5rem 0 0.5rem 0; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                    <div style="width: 56px; height: 56px; border-radius: 50%; background: rgba(56, 189, 248, 0.08); display: flex; align-items: center; justify-content: center; margin-bottom: 0.75rem;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
                    </div>
                    <h4 style="margin: 0; font-size: 1.15rem; font-weight: 600; color: white;">Drop your dataset here</h4>
                    <p style="margin: 0.4rem 0 1.2rem 0; font-size: 0.85rem; color: var(--muted-foreground);">CSV, Excel (.xlsx/.xls), or JSON — up to a few MBs</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            uploaded_file = st.file_uploader("Upload dataset", type=["csv", "xlsx", "xls", "json"], label_visibility="collapsed")
            
            if uploaded_file is not None:
                # Add to history if not already added
                exists = any(item["filename"] == uploaded_file.name for item in st.session_state.upload_history)
                if not exists:
                    try:
                        if uploaded_file.name.endswith(".csv"):
                            df_uploaded = pd.read_csv(uploaded_file)
                        elif uploaded_file.name.endswith((".xls", ".xlsx")):
                            df_uploaded = pd.read_excel(uploaded_file)
                        else:
                            df_uploaded = pd.read_json(uploaded_file)
                        st.session_state.uploaded_df = df_uploaded
                        st.session_state.uploaded_filename = uploaded_file.name
                        status = "Processed"
                    except Exception as e:
                        st.error(f"Error parsing file: {e}")
                        status = "Failed"

                    file_ext = uploaded_file.name.split(".")[-1].upper()
                    st.session_state.upload_history.insert(0, {
                        "filename": uploaded_file.name,
                        "size": format_size(uploaded_file.size),
                        "type": file_ext,
                        "status": status,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    if status == "Processed":
                        st.toast(f"File {uploaded_file.name} successfully uploaded and parsed!", icon="✅")
                    else:
                        st.toast(f"File {uploaded_file.name} failed to parse.", icon="❌")

        # History Table Panel
        st.markdown("<div style='margin-top: 2rem; margin-bottom: 0.5rem; font-family: var(--font-display); font-size: 1.15rem; font-weight: 700; color: white;'>Upload history</div>", unsafe_allow_html=True)
        
        if not st.session_state.upload_history:
            st.markdown(
                """
                <div class="glass-card" style="padding: 2.5rem; text-align: center; color: var(--muted-foreground);">
                    No uploads yet.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            history_df = pd.DataFrame(st.session_state.upload_history)
            history_df.columns = ["File Name", "Size", "Type", "Status", "Date"]
            
            # Format and render dataframe with custom config
            st.dataframe(
                history_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        help="Current status of the upload file",
                        options=["Processed", "Ready", "Failed"]
                    )
                }
            )

if __name__ == "__main__":
    main()
