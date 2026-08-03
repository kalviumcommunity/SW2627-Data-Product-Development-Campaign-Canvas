import sqlite3
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.components.navbar import render_navbar
from src.components.sidebar import render_sidebar
from src.database.queries import SQL_WORKSPACE_DEFAULT_QUERY
from src.utils.campaigns import (
    add_marketing_dimensions,
    calculate_revenue,
    load_campaign_data,
)
from src.utils.clerk_auth import require_authentication
from src.utils.load_css import load_css
from src.utils.sql_safety import validate_sql_query

st.set_page_config(
    page_title="SQL Workspace — CampaignCanvas",
    page_icon=":material/bar_chart:",
    layout="wide",
)
load_css()

# Check if user is logged in
require_authentication()

# Initialize saved queries in session state
if "saved_queries" not in st.session_state:
    st.session_state.saved_queries = []

if "sql_editor_content" not in st.session_state:
    st.session_state.sql_editor_content = SQL_WORKSPACE_DEFAULT_QUERY


def main():
    # Sidebar
    render_sidebar("sql_workspace")

    # Navbar
    render_navbar("SQL Workspace")

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

    # Add standardized dimensions and metrics
    df = add_marketing_dimensions(df)

    # Standardize column mappings for SQL engine alignment
    df["campaign"] = df["campaign_name"] if "campaign_name" in df.columns else df.get("campaign_id", "")
    df["platform"] = df["ad_platform"] if "ad_platform" in df.columns else df.get("platform_grouped", "")
    df["conversions"] = (
        df["activations_7d"] if "activations_7d" in df.columns else df.get("activations", df.get("conversions", 0))
    )
    df["spend"] = df["spend_usd"] if "spend_usd" in df.columns else df.get("spend", 0)
    df["revenue"] = calculate_revenue(df)

    if "visits" not in df.columns:
        clicks_val = df["clicks"] if "clicks" in df.columns else 0
        df["visits"] = (clicks_val * 0.826).astype(int)

    # Keep schema columns expected by SQL interface
    final_cols = [
        "date",
        "campaign",
        "channel",
        "platform",
        "region",
        "device",
        "impressions",
        "clicks",
        "visits",
        "signups",
        "conversions",
        "spend",
        "revenue",
    ]

    # Filter available columns dynamically to prevent key errors
    available_cols = [c for c in final_cols if c in df.columns]
    df_db = df[available_cols].copy()

    # Load database in-memory SQLite connection
    conn_mem = sqlite3.connect(":memory:")
    df_db.to_sql("campaigns", conn_mem, index=False)

    # Layout: left column for querying, right column for saved queries
    col_query, col_saved = st.columns([5, 2], gap="large")

    with col_query:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-family: var(--font-display); font-size: 1.15rem; font-weight: 700; color: var(--foreground); margin-bottom: 0.5rem;">SQL Workspace</div>
                <div style="font-size: 0.85rem; color: var(--muted-foreground); margin-bottom: 1.25rem; line-height: 1.5;">
                    Table available: <span style="background: rgba(148, 163, 184, 0.15); color: var(--foreground); padding: 0.15rem 0.45rem; border-radius: 0.35rem; font-family: monospace; font-size: 0.82rem; font-weight: 600;">campaigns</span> — columns: date, campaign, channel, platform, region, device, impressions, clicks, visits, signups, conversions, spend, revenue
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Code editor text area
            query_input = st.text_area(
                "SQL Query",
                value=st.session_state.sql_editor_content,
                height=180,
                label_visibility="collapsed",
                key="query_text_area",
            )

            # Action controls row
            st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
            col_run_btn, col_save_name, col_save_btn = st.columns([1, 2, 1])

            with col_run_btn:
                run_clicked = st.button(
                    "Run",
                    icon=":material/play_arrow:",
                    key="run_query_btn",
                    use_container_width=True,
                    type="primary",
                )
            with col_save_name:
                save_name = st.text_input(
                    "Query Name",
                    placeholder="Name to save",
                    label_visibility="collapsed",
                    key="save_query_name",
                )
            with col_save_btn:
                save_clicked = st.button(
                    "Save",
                    icon=":material/bookmark:",
                    key="save_query_btn",
                    use_container_width=True,
                )

            if save_clicked:
                if not save_name.strip():
                    st.error("Please enter a name for the query.")
                else:
                    try:
                        validate_sql_query(query_input)
                    except ValueError as exc:
                        st.error(str(exc))
                    else:
                        st.session_state.saved_queries.append({"name": save_name, "query": query_input})
                        st.toast(
                            f"Query '{save_name}' successfully saved!",
                            icon=":material/download:",
                        )
                        st.rerun()

    with col_saved:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>
                    <span style="font-family: var(--font-display); font-size: 1.05rem; font-weight: 700; color: var(--foreground);">Saved queries</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if not st.session_state.saved_queries:
                st.markdown(
                    "<div style='font-size: 0.85rem; color: var(--muted-foreground); text-align: center; padding: 2rem 0;'>No saved queries yet.</div>",
                    unsafe_allow_html=True,
                )
            else:
                for idx, sq in enumerate(st.session_state.saved_queries):
                    col_sq_name, col_sq_del = st.columns([5, 1])
                    with col_sq_name:
                        if st.button(sq["name"], key=f"load_sq_{idx}", use_container_width=True):
                            st.session_state.sql_editor_content = sq["query"]
                            st.toast(
                                f"Loaded '{sq['name']}' into query editor.",
                                icon=":material/check:",
                            )
                            st.rerun()
                    with col_sq_del:
                        if st.button(
                            "",
                            icon=":material/delete:",
                            key=f"del_sq_{idx}",
                            help="Delete query",
                        ):
                            st.session_state.saved_queries.pop(idx)
                            st.toast("Query deleted.", icon=":material/delete:")
                            st.rerun()

    # Results Panel
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            """
            <div style="margin-bottom: 0.75rem;">
                <h4 style="margin: 0; font-family: var(--font-display); font-size: 1.15rem; font-weight: 700; color: var(--foreground);">Results</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if run_clicked or st.session_state.get("query_has_run", False):
            st.session_state.query_has_run = True

            try:
                safe_query = validate_sql_query(query_input)
                # Run query against in-memory DB
                res_df = pd.read_sql_query(safe_query, conn_mem)

                if res_df.empty:
                    st.info("Query executed successfully but returned 0 rows.")
                else:
                    st.dataframe(res_df, use_container_width=True, hide_index=True)
                    st.caption(f"Query returned {len(res_df)} rows.")
            except Exception as e:
                st.error(f"SQL Execution Error: {e}")
        else:
            st.markdown(
                "<div style='font-size: 0.85rem; color: var(--muted-foreground); padding: 1rem 0;'>Run a query to see results.</div>",
                unsafe_allow_html=True,
            )

    conn_mem.close()


if __name__ == "__main__":
    main()
