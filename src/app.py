from datetime import datetime

import streamlit as st


st.set_page_config(page_title="CampaignIQ", page_icon="📊", layout="wide")

FEATURES = [
	{
		"icon": "🗄️",
		"title": "Ingest anything",
		"desc": "CSV, Excel, and JSON with drag & drop validation.",
	},
	{
		"icon": "✨",
		"title": "Clean & profile",
		"desc": "Auto-profile datasets and fix nulls, dupes, and outliers.",
	},
	{
		"icon": "⚡",
		"title": "KPI engine",
		"desc": "CTR, CPA, ROAS, CVR, AOV computed live.",
	},
	{
		"icon": "📈",
		"title": "Insight visuals",
		"desc": "Interactive charts for funnels, cohorts, trends.",
	},
	{
		"icon": "📊",
		"title": "SQL workspace",
		"desc": "Query your datasets with real SQL.",
	},
	{
		"icon": "🛡️",
		"title": "Alerts & reports",
		"desc": "Thresholds, PDF/Excel exports, executive summaries.",
	},
]


st.markdown(
	"""
	<style>
		.stApp {
			background:
				radial-gradient(circle at top left, rgba(34, 197, 94, 0.16), transparent 32%),
				radial-gradient(circle at top right, rgba(14, 165, 233, 0.14), transparent 28%),
				linear-gradient(180deg, #07111f 0%, #0b1726 42%, #f8fafc 42%, #f8fafc 100%);
		}
		.hero-badge {
			display: inline-flex;
			align-items: center;
			gap: 0.5rem;
			border: 1px solid rgba(148, 163, 184, 0.28);
			border-radius: 999px;
			padding: 0.5rem 0.8rem;
			background: rgba(15, 23, 42, 0.55);
			color: #e2e8f0;
			backdrop-filter: blur(12px);
			font-size: 0.9rem;
		}
		.hero-title {
			color: #f8fafc;
			font-size: clamp(2.5rem, 5vw, 4.8rem);
			line-height: 0.98;
			letter-spacing: -0.04em;
			margin: 1rem 0 0.75rem 0;
			font-weight: 800;
		}
		.hero-title span {
			color: #7dd3fc;
		}
		.hero-copy {
			color: #cbd5e1;
			font-size: 1.1rem;
			line-height: 1.7;
			max-width: 42rem;
		}
		.feature-card {
			padding: 1.25rem;
			border-radius: 20px;
			border: 1px solid rgba(148, 163, 184, 0.16);
			background: rgba(15, 23, 42, 0.68);
			box-shadow: 0 16px 40px rgba(2, 6, 23, 0.22);
			min-height: 180px;
		}
		.feature-icon {
			font-size: 1.25rem;
			width: 2.5rem;
			height: 2.5rem;
			display: inline-flex;
			align-items: center;
			justify-content: center;
			border-radius: 14px;
			background: linear-gradient(135deg, #22c55e, #38bdf8);
			margin-bottom: 0.9rem;
		}
		.feature-title {
			color: #f8fafc;
			font-size: 1.06rem;
			font-weight: 700;
			margin-bottom: 0.35rem;
		}
		.feature-desc {
			color: #cbd5e1;
			font-size: 0.96rem;
			line-height: 1.6;
		}
		.footer-note {
			color: #64748b;
			font-size: 0.92rem;
		}
		div[data-testid="stButton"] > button {
			border-radius: 999px;
			padding: 0.8rem 1.25rem;
			border: none;
			font-weight: 700;
		}
		div[data-testid="stButton"] > button:first-child {
			background: linear-gradient(135deg, #22c55e, #0ea5e9);
			color: white;
		}
	</style>
	""",
	unsafe_allow_html=True,
)


top_left, top_right = st.columns([3, 1])
with top_left:
	st.markdown(
		'<div class="hero-badge">✨ Enterprise marketing analytics, self-serve</div>',
		unsafe_allow_html=True,
	)
with top_right:
	auth_col, start_col = st.columns(2)
	with auth_col:
		st.button("Sign in", use_container_width=True)
	with start_col:
		st.button("Get started", type="primary", use_container_width=True)


st.markdown(
	"""
	<div class="hero-title">
		Turn raw campaign data <br /> into <span>decisions</span>.
	</div>
	<div class="hero-copy">
		Upload multi-source marketing data, auto-clean it, run KPIs & funnels, and share
		executive-ready reports - all in one workspace.
	</div>
	""",
	unsafe_allow_html=True,
)


hero_primary, hero_secondary = st.columns([1, 1])
with hero_primary:
	st.button("Launch workspace", type="primary", use_container_width=True)
with hero_secondary:
	st.button("Try the demo", use_container_width=True)


st.write("")
st.write("")

feature_rows = st.columns(3)
for index, feature in enumerate(FEATURES):
	with feature_rows[index % 3]:
		st.markdown(
			f'''
			<div class="feature-card">
				<div class="feature-icon">{feature["icon"]}</div>
				<div class="feature-title">{feature["title"]}</div>
				<div class="feature-desc">{feature["desc"]}</div>
			</div>
			''',
			unsafe_allow_html=True,
		)


st.write("")
st.write("")

footer_left, footer_right = st.columns([1, 1])
with footer_left:
	st.markdown(
		f"<div class='footer-note'>© {datetime.now().year} CampaignIQ</div>",
		unsafe_allow_html=True,
	)
with footer_right:
	st.markdown(
		"<div class='footer-note' style='text-align:right;'>Built with love ✨</div>",
		unsafe_allow_html=True,
	)
