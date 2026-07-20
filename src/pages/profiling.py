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

st.set_page_config(page_title="Data Profiling — CampaignCanvas", page_icon="📊", layout="wide")
load_css()

# Check if user is logged in
if not st.session_state.get("logged_in", False):
    st.switch_page("pages/auth.py")

def main():
    # Sidebar
    render_sidebar("profiling")

    # Header Card
    st.markdown(
        """
        <div class="glass-card" style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground);">CampaignCanvas</div>
            <div style="font-family: var(--font-display); font-size: 1.5rem; font-weight: 700;">Data Profiling</div>
            <div style="font-size: 0.9rem; color: var(--muted-foreground); margin-top: 0.3rem;">
                Inspect dataset statistics, check quality scores, and view the profile of individual columns.
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
        st.info("No datasets available to profile. Please upload a dataset or place CSV files in data/raw.")
        return

    # User selection for dataset to profile
    selected_option = st.selectbox("Select dataset to profile", all_options)
    
    if selected_option.startswith("[Uploaded]"):
        df = st.session_state.uploaded_df
    else:
        df = pd.read_csv(raw_dir / selected_option)

    if df.empty:
        st.info(f"The dataset '{selected_option}' is empty.")
        return

    # Calculate Profiling Stats Dynamically
    total_rows = len(df)
    total_cols = len(df.columns)
    missing_cells = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()
    memory_usage_kb = df.memory_usage(deep=True).sum() / 1024

    # Calculate Data Quality Score
    total_elements = df.size
    completeness_ratio = (total_elements - missing_cells) / total_elements if total_elements > 0 else 1.0
    
    # Calculate Outliers Percentage (Numeric columns > 3 stddevs)
    numeric_cols = df.select_dtypes(include='number').columns
    outliers_count = 0
    total_numeric_elements = 0
    for col in numeric_cols:
        col_clean = df[col].dropna()
        if len(col_clean) > 0 and col_clean.std() > 0:
            mean = col_clean.mean()
            std = col_clean.std()
            outliers = col_clean[(col_clean < mean - 3 * std) | (col_clean > mean + 3 * std)]
            outliers_count += len(outliers)
            total_numeric_elements += len(col_clean)

    outlier_ratio = outliers_count / total_numeric_elements if total_numeric_elements > 0 else 0.0
    quality_score = int(max(0.0, min(100.0, (completeness_ratio - outlier_ratio) * 100)))

    # Metrics Display
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rows", fmt_num(total_rows))
    with col2:
        st.metric("Columns", fmt_num(total_cols))
    with col3:
        st.metric("Missing cells", fmt_num(missing_cells))
    with col4:
        st.metric("Duplicates", fmt_num(duplicate_rows))

    col5, col6 = st.columns(2)
    with col5:
        st.metric("Memory", f"{memory_usage_kb:.1f} KB")
    with col6:
        st.metric("Quality Score", f"{quality_score} / 100")

    # Quality Score Progress Bar
    st.markdown("<div style='margin-top: 1.5rem; margin-bottom: 0.5rem; font-weight: 600; color: white;'>Quality score</div>", unsafe_allow_html=True)
    st.progress(quality_score / 100.0)
    st.caption("Completeness ratio minus outlier ratio, scaled from 0 to 100.")

    # Column Profile Section
    st.markdown("<div style='margin-top: 2.5rem; margin-bottom: 0.5rem; font-family: var(--font-display); font-size: 1.15rem; font-weight: 700; color: white;'>Column profile</div>", unsafe_allow_html=True)
    st.caption("Data types, distributions, and sample values.")

    # Generate Profile Dataframe
    profile_rows = []
    for col in df.columns:
        col_series = df[col]
        dtype = str(col_series.dtype)
        
        # Friendly type names
        if "object" in dtype or "string" in dtype:
            type_lbl = "string"
        elif "int" in dtype:
            type_lbl = "integer"
        elif "float" in dtype or "double" in dtype or "decimal" in dtype:
            type_lbl = "float"
        elif "datetime" in dtype:
            type_lbl = "datetime"
        elif "bool" in dtype:
            type_lbl = "boolean"
        else:
            type_lbl = dtype

        missing = col_series.isnull().sum()
        unique = col_series.nunique()
        
        # Calculate stats for numeric columns
        if pd.api.types.is_numeric_dtype(col_series.dtype):
            col_clean = col_series.dropna()
            if not col_clean.empty:
                c_min = f"{col_clean.min():.2f}".rstrip('0').rstrip('.')
                c_max = f"{col_clean.max():.2f}".rstrip('0').rstrip('.')
                c_mean = f"{col_clean.mean():.2f}".rstrip('0').rstrip('.')
                c_std = f"{col_clean.std():.2f}".rstrip('0').rstrip('.')
                
                # Outliers count
                mean = col_clean.mean()
                std = col_clean.std()
                if std > 0:
                    c_outliers = str(len(col_clean[(col_clean < mean - 3 * std) | (col_clean > mean + 3 * std)]))
                else:
                    c_outliers = "0"
            else:
                c_min, c_max, c_mean, c_std, c_outliers = "—", "—", "—", "—", "—"
        else:
            c_min, c_max, c_mean, c_std, c_outliers = "—", "—", "—", "—", "—"

        # Unique samples
        samples = col_series.dropna().unique()[:3]
        samples_str = ", ".join(str(s) for s in samples)

        profile_rows.append({
            "Column": col,
            "Type": type_lbl,
            "Missing": missing,
            "Unique": unique,
            "Min": c_min,
            "Max": c_max,
            "Mean": c_mean,
            "Std": c_std,
            "Outliers": c_outliers,
            "Sample": samples_str
        })

    profile_df = pd.DataFrame(profile_rows)

    st.table(profile_df)

if __name__ == "__main__":
    main()
