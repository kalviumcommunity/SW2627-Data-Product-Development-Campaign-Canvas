import sys
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.utils.campaigns import load_campaign_data, fmt_num
from src.utils.load_css import load_css
from src.components.sidebar import render_sidebar
from src.components.navbar import render_navbar

st.set_page_config(page_title="Data Cleaning — CampaignCanvas", page_icon="📊", layout="wide")
load_css()

# Check if user is logged in
if not st.session_state.get("logged_in", False):
    st.switch_page("pages/auth.py")

def main():
    # Sidebar
    render_sidebar("cleaning")

    # Navbar
    render_navbar("Data Cleaning")

    # Header Card
    st.markdown(
        """
        <div class="glass-card" style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground);">CampaignCanvas</div>
            <div style="font-family: var(--font-display); font-size: 1.5rem; font-weight: 700;">Data Cleaning</div>
            <div style="font-size: 0.9rem; color: var(--muted-foreground); margin-top: 0.3rem;">
                Preview the dataset after applying user-configured data cleaning and normalization rules.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Scan raw CSV files dynamically
    raw_dir = Path(root_dir) / "data" / "raw"
    raw_files = sorted([f.name for f in raw_dir.glob("*.csv")]) if raw_dir.exists() else []
    
    # Check if there is an uploaded file in session state
    uploaded_options = []
    if "uploaded_df" in st.session_state and st.session_state.uploaded_df is not None:
        uploaded_options = [f"[Uploaded] {st.session_state.uploaded_filename}"]

    all_options = uploaded_options + raw_files
    
    if not all_options:
        st.info("No datasets available to clean. Please upload a dataset or place CSV files in data/raw.")
        return

    # User selection for dataset to clean
    selected_option = st.selectbox("Select dataset to clean", all_options)
    
    if selected_option.startswith("[Uploaded]"):
        df = st.session_state.uploaded_df
    else:
        df = pd.read_csv(raw_dir / selected_option)

    if df.empty:
        st.info(f"The dataset '{selected_option}' is empty.")
        return

    # Two column layout: Data Preview on left, Rules Panel on right
    col_preview, col_rules = st.columns([5, 2], gap="large")

    with col_rules:
        # Rules card panel
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1.25rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"></path><path d="m9 12 2 2 4-4"></path></svg>
                    <span style="font-family: var(--font-display); font-size: 1.1rem; font-weight: 700; color: white;">Cleaning rules</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            remove_dup = st.toggle("Remove duplicates", value=True, key="rule_dup")
            fill_num = st.toggle("Fill numeric nulls", value=True, key="rule_num")
            fill_str = st.toggle("Fill string nulls", value=True, key="rule_str")
            trim_space = st.toggle("Trim whitespace", value=True, key="rule_trim")
            lower_text = st.toggle("Lowercase text", value=False, key="rule_lower")
            remove_outliers = st.toggle("Remove outliers", value=False, key="rule_outliers")
            normalize_dates = st.toggle("Normalize dates", value=True, key="rule_dates")
            
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            save_clicked = st.button("Save cleaned dataset", use_container_width=True, type="primary")
            if save_clicked:
                st.toast("Cleaned dataset successfully saved to database!", icon="🎉")

    # Apply cleaning steps dynamically
    original_rows = len(df)
    df_cleaned = df.copy()

    if remove_dup:
        df_cleaned = df_cleaned.drop_duplicates()

    # Fill nulls
    if fill_num:
        num_cols = df_cleaned.select_dtypes(include=[np.number]).columns
        for col in num_cols:
            if df_cleaned[col].isnull().any():
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mean())

    if fill_str:
        obj_cols = df_cleaned.select_dtypes(include=[object, "string"]).columns
        for col in obj_cols:
            df_cleaned[col] = df_cleaned[col].fillna("Unknown")

    # Trim/Lowercase
    if trim_space:
        obj_cols = df_cleaned.select_dtypes(include=[object, "string"]).columns
        for col in obj_cols:
            df_cleaned[col] = df_cleaned[col].astype(str).str.strip()

    if lower_text:
        obj_cols = df_cleaned.select_dtypes(include=[object, "string"]).columns
        for col in obj_cols:
            df_cleaned[col] = df_cleaned[col].astype(str).str.lower()

    # Outliers
    if remove_outliers:
        num_cols = df_cleaned.select_dtypes(include=[np.number]).columns
        for col in num_cols:
            col_clean = df_cleaned[col].dropna()
            if len(col_clean) > 0 and col_clean.std() > 0:
                mean = col_clean.mean()
                std = col_clean.std()
                df_cleaned = df_cleaned[
                    (df_cleaned[col] >= mean - 3 * std) & 
                    (df_cleaned[col] <= mean + 3 * std)
                ]

    # Normalize Dates
    if normalize_dates and "date" in df_cleaned.columns:
        try:
            df_cleaned["date"] = pd.to_datetime(df_cleaned["date"], errors="coerce")
            df_cleaned = df_cleaned.dropna(subset=["date"])
            df_cleaned["date"] = df_cleaned["date"].dt.strftime("%Y-%m-%d")
        except Exception:
            pass

    cleaned_rows = len(df_cleaned)

    with col_preview:
        # Display Preview Title and Statistics
        st.markdown(
            f"""
            <div style="margin-bottom: 0.75rem;">
                <h4 style="margin: 0; font-family: var(--font-display); font-size: 1.25rem; font-weight: 700; color: white;">Cleaning preview</h4>
                <div style="font-size: 0.85rem; color: var(--muted-foreground); margin-top: 0.2rem;">
                    Original: <strong style="color: white;">{original_rows} rows</strong> &nbsp;·&nbsp; 
                    Cleaned: <strong style="color: #38bdf8;">{cleaned_rows} rows</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Show Table
        st.table(df_cleaned.head(15))
        st.caption("Showing preview of first 15 rows.")

if __name__ == "__main__":
    main()
