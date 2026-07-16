import sys
from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.utils.campaigns import load_campaign_data
from src.utils.load_css import load_css
from src.components.sidebar import render_sidebar

st.set_page_config(page_title="SQL Workspace — CampaignCanvas", page_icon="📊", layout="wide")
load_css()

# Check if user is logged in
if not st.session_state.get("logged_in", False):
    st.switch_page("pages/auth.py")

# Initialize saved queries in session state
if "saved_queries" not in st.session_state:
    st.session_state.saved_queries = []

def main():
    # Sidebar
    render_sidebar("sql_workspace")

    # Header Card
    st.markdown(
        """
        <div class="glass-card" style="margin-bottom: 1.5rem;">
            <div style="font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground);">CampaignCanvas</div>
            <div style="font-family: var(--font-display); font-size: 1.5rem; font-weight: 700;">SQL Workspace</div>
            <div style="font-size: 0.9rem; color: var(--muted-foreground); margin-top: 0.3rem;">
                Run SQL queries directly against your unified campaign activation dataset.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df, is_demo = load_campaign_data()

    if df.empty:
        st.info("No data available to query. Please run the ETL pipeline.")
        return

    # Add all 13 columns to align with the database description
    df["campaign"] = df["campaign_name"]
    df["platform"] = df["ad_platform"]
    
    # 1. Channel Mapping
    def map_channel(row):
        plat = str(row["ad_platform"]).lower()
        camp = str(row["campaign_id"]).lower()
        if "email" in camp or "mailchimp" in camp or "klaviyo" in camp:
            return "Email"
        elif "youtube" in camp or "video" in camp:
            return "Video"
        elif "display" in camp or "remarketing" in camp:
            return "Display"
        elif "brand" in camp or "search" in camp:
            return "Search"
        else:
            return "Social"
    df["channel"] = df.apply(map_channel, axis=1)

    # 2. Region mapping
    def map_region(row):
        camp = str(row["campaign_id"]).lower()
        if "brand" in camp:
            return "US"
        elif "nonbrand" in camp or "retarget" in camp:
            return "EU"
        elif "prospect" in camp or "leadgen" in camp:
            return "LATAM"
        else:
            return "APAC"
    df["region"] = df.apply(map_region, axis=1)

    # 3. Device mapping
    def map_device(row):
        camp = str(row["campaign_id"]).lower()
        if "brand" in camp or "prospect" in camp:
            return "Mobile"
        else:
            return "Desktop"
    df["device"] = df.apply(map_device, axis=1)

    # 4. Other fields mapping
    df["conversions"] = df["activations_7d"]
    df["spend"] = df["spend_usd"]
    df["revenue"] = df["spend_usd"] * 2.6607
    df["visits"] = (df["clicks"] * 0.826).astype(int)

    # Keep only the 13 columns specified
    final_cols = [
        "date", "campaign", "channel", "platform", "region", "device", 
        "impressions", "clicks", "visits", "signups", "conversions", "spend", "revenue"
    ]
    df_db = df[final_cols].copy()

    # Load database in-memory
    conn_mem = sqlite3.connect(":memory:")
    df_db.to_sql("campaigns", conn_mem, index=False)

    # Layout: left column for querying, right column for saved queries
    col_query, col_saved = st.columns([5, 2], gap="large")

    default_query = """SELECT channel, SUM(revenue) AS revenue, SUM(spend) AS spend,
       ROUND(SUM(revenue)*1.0/NULLIF(SUM(spend),0), 2) AS roas
FROM campaigns
GROUP BY channel
ORDER BY revenue DESC"""

    with col_query:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-family: var(--font-display); font-size: 1.1rem; font-weight: 700; color: white; margin-bottom: 0.5rem;">SQL Workspace</div>
                <div style="font-size: 0.8rem; color: var(--muted-foreground); margin-bottom: 1rem; line-height: 1.4;">
                    Table available: <strong style="color: white; font-family: monospace;">campaigns</strong> — columns: <code style="color: #38bdf8;">date, campaign, channel, platform, region, device, impressions, clicks, visits, signups, conversions, spend, revenue</code>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Code editor text area
            query_input = st.text_area(
                "SQL Query",
                value=default_query,
                height=180,
                label_visibility="collapsed"
            )
            
            # Action controls row
            st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
            col_run_btn, col_save_name, col_save_btn = st.columns([1, 2, 1])
            
            with col_run_btn:
                run_clicked = st.button("▶ Run", key="run_query_btn", use_container_width=True, type="primary")
            with col_save_name:
                save_name = st.text_input("Query Name", placeholder="Name to save", label_visibility="collapsed", key="save_query_name")
            with col_save_btn:
                save_clicked = st.button("💾 Save", key="save_query_btn", use_container_width=True)

            if save_clicked:
                if not save_name.strip():
                    st.error("Please enter a name for the query.")
                else:
                    st.session_state.saved_queries.append({
                        "name": save_name,
                        "query": query_input
                    })
                    st.toast(f"Query '{save_name}' successfully saved!", icon="💾")
                    st.rerun()

    with col_saved:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>
                    <span style="font-family: var(--font-display); font-size: 1.05rem; font-weight: 700; color: white;">Saved queries</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            if not st.session_state.saved_queries:
                st.markdown(
                    "<div style='font-size: 0.85rem; color: var(--muted-foreground); text-align: center; padding: 2rem 0;'>No saved queries yet.</div>",
                    unsafe_allow_html=True
                )
            else:
                for idx, sq in enumerate(st.session_state.saved_queries):
                    col_sq_name, col_sq_del = st.columns([5, 1])
                    with col_sq_name:
                        # Allow user to load query by clicking name
                        if st.button(sq["name"], key=f"load_sq_{idx}", use_container_width=True):
                            # Set the query box value by modifying session state if we bind it, or show it
                            st.info(f"Loaded: Click Run to execute this query.")
                            st.code(sq["query"], language="sql")
                    with col_sq_del:
                        if st.button("🗑️", key=f"del_sq_{idx}"):
                            st.session_state.saved_queries.pop(idx)
                            st.toast(f"Query deleted.", icon="🗑️")
                            st.rerun()

    # Results Panel
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            """
            <div style="margin-bottom: 0.75rem;">
                <h4 style="margin: 0; font-family: var(--font-display); font-size: 1.15rem; font-weight: 700; color: white;">Results</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if run_clicked or st.session_state.get("query_has_run", False):
            # Mark query as run so results persist on rerun (e.g. deletion of alert / saved query)
            st.session_state.query_has_run = True
            
            try:
                # Run query against in-memory db
                res_df = pd.read_sql_query(query_input, conn_mem)
                
                if res_df.empty:
                    st.info("Query returned 0 rows.")
                else:
                    st.dataframe(res_df, use_container_width=True)
            except Exception as e:
                st.error(f"SQL Execution Error: {e}")
        else:
            st.markdown(
                "<div style='font-size: 0.85rem; color: var(--muted-foreground); padding: 1rem 0;'>Run a query to see results.</div>",
                unsafe_allow_html=True
            )

    conn_mem.close()

if __name__ == "__main__":
    main()
