import sys
from pathlib import Path

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[1])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from datetime import datetime
# pyrefly: ignore [missing-import]
import streamlit as st

from src.utils.clerk_auth import handle_clerk_callback
from src.utils.load_css import load_css

# Configure the Streamlit page
st.set_page_config(page_title="CampaignCanvas", page_icon="📊", layout="wide")
load_css()

current_theme = st.session_state.get("theme", "dark")
next_theme = "light" if current_theme == "dark" else "dark"
theme_icon = """
<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 3a1 1 0 0 1 1 1v1.08a7 7 0 1 1-3.08 12.91 1 1 0 0 1 1.14-1.64A5 5 0 1 0 12 5V4a1 1 0 0 1 1-1Z"/>
    <path d="M12 1.75v2.5M12 19.75v2.5M4.22 4.22l1.77 1.77M17.99 17.99l1.77 1.77M1.75 12h2.5M19.75 12h2.5M4.22 19.78l1.77-1.77M17.99 6.01l1.77-1.77"/>
</svg>
""" if current_theme == "dark" else """
<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 12.8A8.5 8.5 0 1 1 11.2 3a7 7 0 1 0 9.8 9.8Z"/>
</svg>
"""

# Process any Clerk authentication callback parameters
handle_clerk_callback()

# Check if user is logged in
if st.session_state.get("logged_in", False):
    st.switch_page("pages/dashboard.py")

# ---------------------------------------------------------------------------
# IMPORTANT: this page used to be rendered with `components.html(...)`, which
# puts the markup inside a **sandboxed iframe** (`about:srcdoc`). Links with
# target="_top" can't escape that sandbox unless `allow-top-navigation` is
# explicitly granted, which Streamlit's components iframe does not do. That
# is exactly the "Unsafe attempt to initiate navigation..." error you saw in
# devtools, and why Sign in / Get started / Launch workspace / Try the demo
# did nothing.
#
# Fix: render with st.markdown(unsafe_allow_html=True) instead. That injects
# the HTML straight into the real page DOM (no iframe), so plain <a href>
# links navigate normally.
# ---------------------------------------------------------------------------

# Chrome/layout reset so the custom landing page can go full-bleed, same
# pattern used on pages/auth.py
st.markdown(
    """
    <style>
    .stApp,
    .stMain,
    [data-testid="stMain"],
    div.block-container,
    [data-testid="stAppHeader"],
    header[data-testid="stHeader"] {
        padding: 0 !important;
        margin: 0 !important;
        padding-top: 0 !important;
        margin-top: 0 !important;
        top: 0 !important;
    }
    div.block-container {
        max-width: 100% !important;
        width: 100% !important;
    }
    header[data-testid="stHeader"],
    div[data-testid="stAppHeader"] {
        display: none !important;
        height: 0px !important;
    }
    section[data-testid="stSidebar"] { display: none !important; }
    #MainMenu, footer:not(.footer) { visibility: hidden !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Custom HTML and CSS landing page — direct port of the React/Tailwind Landing component
landing_html = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');

* {{ box-sizing: border-box; }}

:root {{
    --landing-background: {'linear-gradient(180deg, #f8fbff 0%, #eef6ff 45%, #eaf1ff 100%)' if current_theme == 'light' else 'radial-gradient(circle at 10% 20%, rgba(56, 189, 248, 0.15) 0%, transparent 40%), radial-gradient(circle at 90% 80%, rgba(99, 102, 241, 0.15) 0%, transparent 40%), #030712'};
    --landing-foreground: {'#0f172a' if current_theme == 'light' else '#f8fafc'};
    --landing-muted: {'#475569' if current_theme == 'light' else '#9ca3af'};
    --landing-surface: {'rgba(255, 255, 255, 0.78)' if current_theme == 'light' else 'rgba(30, 41, 59, 0.4)'};
    --landing-border: {'rgba(148, 163, 184, 0.22)' if current_theme == 'light' else 'rgba(255, 255, 255, 0.1)'};
    --landing-card: {'rgba(255, 255, 255, 0.9)' if current_theme == 'light' else 'rgba(15, 23, 42, 0.4)'};
    --landing-card-border: {'rgba(148, 163, 184, 0.2)' if current_theme == 'light' else 'rgba(255, 255, 255, 0.05)'};
    --landing-footer: {'rgba(255, 255, 255, 0.72)' if current_theme == 'light' else 'rgba(15, 23, 42, 0.3)'};
    --landing-glow: {'rgba(56, 189, 248, 0.18)' if current_theme == 'light' else 'rgba(56, 189, 248, 0.4)'};
}}

.landing-container {{
    display: block;
    background: var(--landing-background);
    color: var(--landing-foreground);
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    min-height: 100vh;
    width: 100%;
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
    box-shadow: 0 0 18px var(--landing-glow);
    color: white;
}}

.logo-icon svg {{ width: 1.25rem; height: 1.25rem; }}

.logo-text {{
    font-size: 1.125rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: var(--landing-foreground);
}}

.header-actions {{ display: flex; align-items: center; gap: 0.5rem; }}

.theme-toggle-link {{
    width: 2.5rem !important;
    height: 2.5rem !important;
    border-radius: 9999px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    border: 1px solid var(--landing-border) !important;
    background: var(--landing-surface) !important;
    color: var(--landing-foreground) !important;
    text-decoration: none !important;
    transition: all 0.2s ease !important;
    margin-right: 0.5rem !important;
}}
.theme-toggle-link svg {{ width: 1rem; height: 1rem; }}
.theme-toggle-link:hover {{ transform: translateY(-1px); box-shadow: 0 10px 30px -18px rgba(15, 23, 42, 0.35); }}

.btn-ghost {{
    background: transparent;
    color: var(--landing-muted);
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    font-weight: 500;
    font-size: 0.875rem;
    text-decoration: none;
    transition: all 0.2s;
    border: 1px solid transparent;
    cursor: pointer;
}}
.btn-ghost:hover {{ color: var(--landing-foreground); background: color-mix(in oklab, var(--landing-foreground) 8%, transparent); }}

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
    border: 1px solid var(--landing-border);
    background: var(--landing-surface);
    backdrop-filter: blur(8px);
    padding: 0.35rem 0.85rem;
    font-size: 0.75rem;
    color: var(--landing-muted);
    margin-bottom: 1.5rem;
}}
.hero-badge svg {{ color: #38bdf8; width: 0.875rem; height: 0.875rem; }}

.hero-title {{
    font-size: clamp(2.5rem, 5vw, 4rem);
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.03em;
    margin: 0 0 1.5rem 0;
    color: var(--landing-foreground);
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
    color: var(--landing-muted);
    line-height: 1.6;
    margin-bottom: 2.25rem;
}}

.hero-actions {{ display: flex; align-items: center; gap: 1rem; justify-content: center; flex-wrap: wrap; }}

.btn-lg {{ padding: 0.75rem 1.75rem; font-size: 1rem; border-radius: 0.75rem; }}

.btn-outline {{
    background: transparent;
    color: var(--landing-foreground);
    border: 1px solid var(--landing-border);
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
    background: color-mix(in oklab, var(--landing-foreground) 7%, transparent);
    border-color: color-mix(in oklab, var(--landing-foreground) 24%, var(--landing-border));
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
    background: var(--landing-card);
    border: 1px solid var(--landing-card-border);
    border-radius: 1rem;
    padding: 1.75rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(12px);
    text-align: left;
}}
.glass-card:hover {{
    transform: translateY(-4px);
    border-color: color-mix(in oklab, var(--landing-foreground) 14%, var(--landing-card-border));
    box-shadow: 0 18px 45px -30px rgba(15, 23, 42, 0.35);
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

.card-title {{ font-weight: 600; font-size: 1.0625rem; color: var(--landing-foreground); margin-bottom: 0.35rem; }}
.card-desc {{ font-size: 0.875rem; color: var(--landing-muted); line-height: 1.5; }}

/* ---------- Footer ---------- */
.footer {{
    border-top: 1px solid var(--landing-border);
    width: 100%;
    background: var(--landing-footer);
    visibility: visible !important;
    display: block !important;
}}

.footer-content {{
    max-width: 80rem;
    margin: 0 auto;
    padding: 1.5rem;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 0.85rem;
    color: #6b7280;
}}

/* --- Streamlit Override Fixes --- */
.landing-container a,
[data-testid="stMarkdownContainer"] .landing-container a {{
    text-decoration: none !important;
}}

[data-testid="stMarkdownContainer"] .landing-container a:hover,
[data-testid="stMarkdownContainer"] .landing-container a:focus {{
    text-decoration: none !important;
}}

[data-testid="stMarkdownContainer"] .landing-container .logo-container {{
    text-decoration: none !important;
}}

[data-testid="stMarkdownContainer"] .landing-container .btn-ghost {{
    color: var(--landing-muted) !important;
    text-decoration: none !important;
}}

[data-testid="stMarkdownContainer"] .landing-container .btn-ghost:hover {{
    color: var(--landing-foreground) !important;
    background: color-mix(in oklab, var(--landing-foreground) 8%, transparent) !important;
}}

[data-testid="stMarkdownContainer"] .landing-container .btn-primary {{
    color: white !important;
    text-decoration: none !important;
}}

[data-testid="stMarkdownContainer"] .landing-container .btn-primary:hover {{
    color: white !important;
}}

[data-testid="stMarkdownContainer"] .landing-container .btn-outline {{
    color: var(--landing-foreground) !important;
    text-decoration: none !important;
}}

[data-testid="stMarkdownContainer"] .landing-container .btn-outline:hover {{
    color: var(--landing-foreground) !important;
    background: color-mix(in oklab, var(--landing-foreground) 7%, transparent) !important;
    border-color: color-mix(in oklab, var(--landing-foreground) 24%, var(--landing-border)) !important;
}}

</style>

<div class="landing-container">
    <!-- Header -->
    <header class="header">
        <a href="/dashboard" class="logo-container">
            <div class="logo-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
            </div>
            <span class="logo-text">CampaignCanvas</span>
        </a>
        <div class="header-actions">
            <a href="?theme={next_theme}" target="_self" class="theme-toggle-link" title="Toggle Theme" aria-label="Toggle theme">{theme_icon}</a>
            <a href="/auth" class="btn-ghost">Sign in</a>
            <a href="/auth" class="btn-primary">Get started</a>
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
            <a href="/auth" class="btn-primary btn-lg">Launch workspace</a>
            <a href="/dashboard" class="btn-outline btn-lg">Try the demo</a>
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
            <span>© {datetime.now().year} CampaignCanvas. All rights reserved.</span>
        </div>
    </footer>
</div>
"""

# Streamlit's markdown parser follows standard Markdown rules, where any
# line indented 4+ spaces is rendered as a literal code block. Our HTML is
# deeply nested (8/12+ spaces per line), which was causing chunks of it to
# show up as raw text instead of being parsed as markup. Stripping leading
# whitespace from each line avoids that while leaving the rendered HTML
# unaffected (HTML doesn't care about indentation).
landing_html_flat = "\n".join(line.lstrip() for line in landing_html.split("\n"))

st.markdown(landing_html_flat, unsafe_allow_html=True)