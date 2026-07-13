import sys
from pathlib import Path

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[1])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from datetime import datetime
# pyrefly: ignore [missing-import]
import streamlit as st
import streamlit.components.v1 as components

from src.utils.load_css import load_css

# Configure the Streamlit page
st.set_page_config(page_title="CampaignCanvas", page_icon="📊", layout="wide")
load_css()

# Check if user is logged in
if st.session_state.get("logged_in", False):
    st.switch_page("pages/dashboard.py")

# Custom HTML and CSS landing page — direct port of the React/Tailwind Landing component
landing_html = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');

* {{ box-sizing: border-box; }}

html, body {{
    margin: 0;
    padding: 0;
    background: radial-gradient(circle at 10% 20%, rgba(56, 189, 248, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(99, 102, 241, 0.15) 0%, transparent 40%),
                #030712;
    color: #f3f4f6;
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}}

.landing-container {{
    display: block;
}}

/* ---------- Header ---------- */
.header {{
    max-width: 80rem;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.25rem 1.5rem;
    width: 100%;
}}

.logo-container {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    text-decoration: none;
    color: inherit;
}}

.logo-icon {{
    height: 2.25rem;
    width: 2.25rem;
    border-radius: 0.75rem;
    background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
    display: grid;
    place-items: center;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
    color: white;
}}

.logo-icon svg {{ width: 1.25rem; height: 1.25rem; }}

.logo-text {{
    font-size: 1.125rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: white;
}}

.header-actions {{ display: flex; align-items: center; gap: 0.5rem; }}

.btn-ghost {{
    background: transparent;
    color: #9ca3af;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    font-weight: 500;
    font-size: 0.875rem;
    text-decoration: none;
    transition: all 0.2s;
    border: 1px solid transparent;
    cursor: pointer;
}}
.btn-ghost:hover {{ color: white; background: rgba(255, 255, 255, 0.05); }}

.btn-primary {{
    background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
    color: white;
    padding: 0.5rem 1.25rem;
    border-radius: 0.5rem;
    font-weight: 600;
    font-size: 0.875rem;
    text-decoration: none;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
    transition: all 0.2s;
    border: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}}
.btn-primary:hover {{ transform: translateY(-1px); box-shadow: 0 0 20px rgba(56, 189, 248, 0.5); }}

/* ---------- Hero ---------- */
.hero-section {{
    max-width: 80rem;
    margin: 0 auto;
    padding: 5rem 1.5rem 6rem;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
}}

.hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    border-radius: 9999px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(8px);
    padding: 0.35rem 0.85rem;
    font-size: 0.75rem;
    color: #cbd5e1;
    margin-bottom: 1.5rem;
}}
.hero-badge svg {{ color: #38bdf8; width: 0.875rem; height: 0.875rem; }}

.hero-title {{
    font-size: clamp(2.5rem, 5vw, 4rem);
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.03em;
    margin: 0 0 1.5rem 0;
    color: white;
}}

.gradient-text {{
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.hero-desc {{
    max-width: 42rem;
    font-size: 1.125rem;
    color: #9ca3af;
    line-height: 1.6;
    margin-bottom: 2.25rem;
}}

.hero-actions {{ display: flex; align-items: center; gap: 1rem; justify-content: center; flex-wrap: wrap; }}

.btn-lg {{ padding: 0.75rem 1.75rem; font-size: 1rem; border-radius: 0.75rem; }}

.btn-outline {{
    background: transparent;
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 0.75rem 1.75rem;
    font-size: 1rem;
    border-radius: 0.75rem;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.2s;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}}
.btn-outline:hover {{
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.4);
    transform: translateY(-1px);
}}

/* ---------- Features ---------- */
.features-section {{
    max-width: 80rem;
    margin: 0 auto;
    padding: 0 1.5rem 6rem 1.5rem;
    width: 100%;
}}

.features-grid {{
    display: grid;
    grid-template-columns: repeat(1, minmax(0, 1fr));
    gap: 1.5rem;
}}
@media (min-width: 768px) {{
    .features-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
}}

.glass-card {{
    background: rgba(15, 23, 42, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 1rem;
    padding: 1.75rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(12px);
    text-align: left;
}}
.glass-card:hover {{
    transform: translateY(-4px);
    border-color: rgba(56, 189, 248, 0.2);
    box-shadow: 0 0 30px rgba(56, 189, 248, 0.15);
}}

.card-icon-container {{
    height: 2.5rem;
    width: 2.5rem;
    border-radius: 0.5rem;
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.1) 0%, rgba(2, 132, 199, 0.1) 100%);
    display: grid;
    place-items: center;
    margin-bottom: 1.25rem;
    color: #38bdf8;
    border: 1px solid rgba(56, 189, 248, 0.2);
}}
.card-icon-container svg {{ width: 1.25rem; height: 1.25rem; }}

.card-title {{ font-weight: 600; font-size: 1.0625rem; color: white; margin-bottom: 0.35rem; }}
.card-desc {{ font-size: 0.875rem; color: #9ca3af; line-height: 1.5; }}

/* ---------- Footer ---------- */
.footer {{ border-top: 1px solid rgba(255, 255, 255, 0.05); width: 100%; }}
.footer-content {{
    max-width: 80rem;
    margin: 0 auto;
    padding: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.875rem;
    color: #6b7280;
}}
</style>

<div class="landing-container">
    <!-- Header -->
    <header class="header">
        <a href="/dashboard" target="_self" class="logo-container">
            <div class="logo-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
            </div>
            <span class="logo-text">CampaignCanvas</span>
        </a>
        <div class="header-actions">
            <a href="/auth" target="_self" class="btn-ghost">Sign in</a>
            <a href="/auth" target="_self" class="btn-primary">Get started</a>
        </div>
    </header>

    <!-- Hero -->
    <section class="hero-section">
        <div class="hero-badge">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275Z"></path><path d="m5 3 1 2.5L8.5 6 6 7 5 9.5 4 7 1.5 6 4 5Z"></path><path d="m19 17 1 2.5 2.5.5-2.5 1-1 2.5-1-2.5-2.5-1 2.5-1Z"></path></svg>
            Enterprise marketing analytics, self-serve
        </div>
        <h1 class="hero-title">
            Turn raw campaign data <br> into <span class="gradient-text">decisions</span>.
        </h1>
        <p class="hero-desc">
            Upload multi-source marketing data, auto-clean it, run KPIs & funnels, and share
            executive-ready reports — all in one workspace.
        </p>
        <div class="hero-actions">
            <a href="/auth" target="_self" class="btn-primary btn-lg">Launch workspace</a>
            <a href="/dashboard" target="_self" class="btn-outline btn-lg">Try the demo</a>
        </div>
    </section>

    <!-- Features -->
    <section class="features-section">
        <div class="features-grid">
            <div class="glass-card">
                <div class="card-icon-container">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5V19A9 3 0 0 0 21 19V5"></path><path d="M3 12A9 3 0 0 0 21 12"></path></svg>
                </div>
                <div class="card-title">Ingest anything</div>
                <p class="card-desc">CSV, Excel, and JSON with drag & drop validation.</p>
            </div>
            <div class="glass-card">
                <div class="card-icon-container">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275Z"></path><path d="m5 3 1 2.5L8.5 6 6 7 5 9.5 4 7 1.5 6 4 5Z"></path><path d="m19 17 1 2.5 2.5.5-2.5 1-1 2.5-1-2.5-2.5-1 2.5-1Z"></path></svg>
                </div>
                <div class="card-title">Clean & profile</div>
                <p class="card-desc">Auto-profile datasets and fix nulls, dupes, and outliers.</p>
            </div>
            <div class="glass-card">
                <div class="card-icon-container">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 14 4-4"></path><path d="M3.34 19a10 10 0 1 1 17.32 0"></path></svg>
                </div>
                <div class="card-title">KPI engine</div>
                <p class="card-desc">CTR, CPA, ROAS, CVR, AOV computed live.</p>
            </div>
            <div class="glass-card">
                <div class="card-icon-container">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="m19 9-5 5-4-4-3 3"></path></svg>
                </div>
                <div class="card-title">Insight visuals</div>
                <p class="card-desc">Interactive charts for funnels, cohorts, trends.</p>
            </div>
            <div class="glass-card">
                <div class="card-icon-container">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                </div>
                <div class="card-title">SQL workspace</div>
                <p class="card-desc">Query your datasets with real SQL.</p>
            </div>
            <div class="glass-card">
                <div class="card-icon-container">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 9.7a1 1 0 0 1-.68 0C7.5 20.5 4 18 4 13V6a1 1 0 0 1 .76-.97l8-2a1 1 0 0 1 .48 0l8 2A1 1 0 0 1 20 6Z"></path></svg>
                </div>
                <div class="card-title">Alerts & reports</div>
                <p class="card-desc">Thresholds, PDF/Excel exports, executive summaries.</p>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
        <div class="footer-content">
            <span>© {datetime.now().year} CampaignIQ</span>
            <span>Built with love ✨</span>
        </div>
    </footer>
</div>
"""

components.html(landing_html, height=1350, scrolling=True)