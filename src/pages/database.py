from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
	sys.path.insert(0, root_dir)

from src.database.db_client import get_connection, init_db
from src.utils.campaigns import load_campaign_data
from src.utils.load_css import load_css
from src.components.sidebar import render_sidebar

st.set_page_config(page_title="Database — CampaignCanvas", page_icon="📊", layout="wide")
load_css()

# Check if user is logged in
if not st.session_state.get("logged_in", False):
	st.switch_page("pages/auth.py")


SCHEMA_TABLES = [
	{
		"name": "ad_campaign_metrics",
		"scope": "Auto-generated",
		"columns": ["campaign_id (PK)", "ad_platform", "spend_usd", "clicks", "impressions", "sync_date"],
	},
	{
		"name": "hubspot_signups",
		"scope": "Auto-generated",
		"columns": ["email (PK)", "utm_campaign (FK)", "signup_timestamp"],
	},
	{
		"name": "product_activations",
		"scope": "Auto-generated",
		"columns": ["user_id (PK)", "email (FK)", "signup_timestamp", "activation_timestamp", "profile_completed", "campaign_run"],
	},
]


def _table_row_count(connection, table_name: str) -> int:
	try:
		cursor = connection.execute(f"SELECT COUNT(*) FROM {table_name}")
		result = cursor.fetchone()
		return int(result[0]) if result else 0
	except Exception:
		return 0


def _table_column_count(connection, table_name: str) -> int:
	try:
		cursor = connection.execute(f"PRAGMA table_info({table_name})")
		return len(cursor.fetchall())
	except Exception:
		return 0


def _build_dataset_summary(connection) -> pd.DataFrame:
	frame, is_demo = load_campaign_data()

	raw_tables = []
	for table_name in ["ad_campaign_metrics", "hubspot_signups", "product_activations"]:
		raw_tables.append(
			{
				"Name": table_name,
				"Source": "SQLite" if not is_demo else "Demo fallback",
				"Rows": _table_row_count(connection, table_name),
				"Columns": _table_column_count(connection, table_name),
				"Cleaned": "✓" if table_name == "product_activations" else "—",
			}
		)

	raw_tables.append(
		{
			"Name": "unified_campaign_view",
			"Source": "In-app join",
			"Rows": int(len(frame)),
			"Columns": int(frame.shape[1]),
			"Cleaned": "✓",
		}
	)

	return pd.DataFrame(raw_tables)


def main() -> None:
	render_sidebar("database")

	init_db()

	conn = get_connection()
	try:
		st.markdown(
			"""
			<div class="glass-card" style="margin-bottom: 1.5rem;">
				<div style="font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted-foreground);">CampaignCanvas</div>
				<div style="font-family: var(--font-display); font-size: 1.5rem; font-weight: 700;">Database</div>
				<div style="font-size: 0.9rem; color: var(--muted-foreground); margin-top: 0.3rem; line-height: 1.5;">
					Your campaign data is stored in a managed SQLite database that mirrors the PRD schema.
					The unified campaign view is derived from those tables and used across the app for analysis.
				</div>
			</div>
			""",
			unsafe_allow_html=True,
		)

		st.caption(f"Database file: {Path(__file__).resolve().parents[2] / 'data' / 'processed' / 'marketing.db'}")

		schema_cols = st.columns(len(SCHEMA_TABLES))
		for col, table in zip(schema_cols, SCHEMA_TABLES):
			row_count = _table_row_count(conn, table["name"])
			with col:
				st.markdown(
					f"""
					<div class="glass-card" style="padding: 1.25rem; height: 100%;">
						<div style="display: flex; align-items: center; justify-content: space-between; gap: 0.75rem;">
							<div style="font-family: var(--font-display); font-weight: 700;">public.{table['name']}</div>
							<span style="font-size: 0.72rem; padding: 0.25rem 0.5rem; border-radius: 9999px; background: rgba(255,255,255,0.06); color: var(--muted-foreground);">{table['scope']}</span>
						</div>
						<div style="margin-top: 0.75rem; font-size: 0.85rem; color: var(--muted-foreground);">Rows: {row_count:,}</div>
						<ul style="margin: 0.9rem 0 0 1rem; padding: 0; color: var(--muted-foreground); font-size: 0.8rem; line-height: 1.5;">
							{''.join(f'<li>{column}</li>' for column in table['columns'])}
						</ul>
					</div>
					""",
					unsafe_allow_html=True,
				)

		st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

		st.markdown(
			"""
			<div class="glass-card" style="padding: 1.25rem; margin-bottom: 1rem;">
				<div style="font-family: var(--font-display); font-size: 1.15rem; font-weight: 700;">Your datasets</div>
				<div style="font-size: 0.9rem; color: var(--muted-foreground); margin-top: 0.35rem;">
					Source tables plus the unified campaign dataset used by the app.
				</div>
			</div>
			""",
			unsafe_allow_html=True,
		)

		summary = _build_dataset_summary(conn)
		st.table(summary)
	finally:
		conn.close()


if __name__ == "__main__":
	main()
