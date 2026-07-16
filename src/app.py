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
    #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Custom HTML and CSS landing page — direct port of the React/Tailwind Landing component
landing_html = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');

* {{ box-sizing: border-box; }}

.landing-container {{
    display: block;
    background: radial-gradient(circle at 10% 20%, rgba(56, 189, 248, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(99, 102, 241, 0.15) 0%, transparent 40%),
                #030712;
    color: #f3f4f6;
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
.footer {{
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    width: 100%;
    background: rgba(15, 23, 42, 0.3);
}}

.footer-content {{
    max-width: 80rem;
    margin: 0 auto;
    padding: 3rem 1.5rem 2rem;
}}

.footer-top {{
    display: grid;
    grid-template-columns: 2fr repeat(3, 1fr);
    gap: 2rem;
    padding-bottom: 2.5rem;
}}
@media (max-width: 768px) {{
    .footer-top {{ grid-template-columns: 1fr; gap: 2rem; }}
}}

.footer-brand-desc {{
    font-size: 0.875rem;
    color: #6b7280;
    line-height: 1.6;
    margin-top: 0.75rem;
    max-width: 20rem;
}}

.footer-col-title {{
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #9ca3af;
    margin-bottom: 0.9rem;
}}

.footer-links {{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.6rem; }}

.footer-link {{
    font-size: 0.875rem;
    color: #6b7280;
    text-decoration: none;
    transition: color 0.2s;
}}
.footer-link:hover {{ color: #f3f4f6; }}

.footer-social {{ display: flex; align-items: center; gap: 0.6rem; margin-top: 1.25rem; }}

.footer-social-icon {{
    height: 2.25rem;
    width: 2.25rem;
    border-radius: 0.5rem;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(255, 255, 255, 0.03);
    display: grid;
    place-items: center;
    color: #9ca3af;
    text-decoration: none;
    transition: all 0.2s;
}}
.footer-social-icon:hover {{
    color: #38bdf8;
    border-color: rgba(56, 189, 248, 0.3);
    background: rgba(56, 189, 248, 0.08);
}}
.footer-social-icon svg {{ width: 1rem; height: 1rem; }}

.footer-bottom {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.75rem;
    padding-top: 1.75rem;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    font-size: 0.8125rem;
    color: #6b7280;
}}

.footer-bottom-links {{ display: flex; gap: 1.25rem; }}
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
            <div class="footer-top">
                <div>
                    <a href="/dashboard" class="logo-container">
                        <div class="logo-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                        </div>
                        <span class="logo-text">CampaignCanvas</span>
                    </a>
                    <p class="footer-brand-desc">
                        Enterprise marketing analytics for teams who need clean data,
                        live KPIs, and reports they can ship to leadership.
                    </p>
                    <div class="footer-social">
                        <a href="#" class="footer-social-icon" aria-label="Twitter / X">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M18.9 2H22l-7.6 8.7L23.3 22H16.6l-5.2-6.8L5.4 22H2.3l8.1-9.3L1.4 2h6.9l4.7 6.2L18.9 2Zm-1.2 18h1.7L7.4 4h-1.8l12.1 16Z"></path></svg>
                        </a>
                        <a href="#" class="footer-social-icon" aria-label="LinkedIn">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5ZM3 9h4v12H3V9Zm7 0h3.8v1.7h.05c.53-1 1.83-2.05 3.77-2.05 4.03 0 4.78 2.65 4.78 6.1V21h-4v-5.6c0-1.34-.02-3.06-1.87-3.06-1.87 0-2.16 1.46-2.16 2.96V21h-4V9Z"></path></svg>
                        </a>
                        <a href="#" class="footer-social-icon" aria-label="GitHub">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.58 2 12.25c0 4.53 2.87 8.37 6.84 9.73.5.1.68-.22.68-.49 0-.24-.01-1.04-.01-1.89-2.78.62-3.37-1.21-3.37-1.21-.46-1.19-1.11-1.51-1.11-1.51-.91-.64.07-.62.07-.62 1 .07 1.53 1.05 1.53 1.05.89 1.57 2.34 1.11 2.91.85.09-.67.35-1.12.63-1.38-2.22-.26-4.56-1.14-4.56-5.07 0-1.12.39-2.03 1.03-2.75-.1-.26-.45-1.31.1-2.72 0 0 .84-.28 2.75 1.05a9.24 9.24 0 0 1 5 0c1.91-1.33 2.75-1.05 2.75-1.05.55 1.41.2 2.46.1 2.72.64.72 1.03 1.63 1.03 2.75 0 3.94-2.34 4.81-4.57 5.06.36.32.68.94.68 1.9 0 1.37-.01 2.47-.01 2.81 0 .27.18.6.69.49A10.26 10.26 0 0 0 22 12.25C22 6.58 17.52 2 12 2Z"></path></svg>
                        </a>
                    </div>
                </div>
                <div>
                    <div class="footer-col-title">Product</div>
                    <ul class="footer-links">
                        <li><a href="/dashboard" class="footer-link">Dashboard</a></li>
                        <li><a href="#" class="footer-link">Features</a></li>
                        <li><a href="#" class="footer-link">Pricing</a></li>
                        <li><a href="#" class="footer-link">Changelog</a></li>
                    </ul>
                </div>
                <div>
                    <div class="footer-col-title">Resources</div>
                    <ul class="footer-links">
                        <li><a href="#" class="footer-link">Documentation</a></li>
                        <li><a href="#" class="footer-link">API reference</a></li>
                        <li><a href="#" class="footer-link">Support</a></li>
                        <li><a href="#" class="footer-link">Status</a></li>
                    </ul>
                </div>
                <div>
                    <div class="footer-col-title">Company</div>
                    <ul class="footer-links">
                        <li><a href="#" class="footer-link">About</a></li>
                        <li><a href="#" class="footer-link">Blog</a></li>
                        <li><a href="#" class="footer-link">Careers</a></li>
                        <li><a href="#" class="footer-link">Contact</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <span>© {datetime.now().year} CampaignCanvas. All rights reserved.</span>
                <div class="footer-bottom-links">
                    <a href="#" class="footer-link">Privacy</a>
                    <a href="#" class="footer-link">Terms</a>
                    <span>Built with love ✨</span>
                </div>
            </div>
        </div>
    </footer>
</div>
<script>
(function() {{
    function setupInterceptors() {{
        document.querySelectorAll('a').forEach(function(anchor) {{
            if (anchor.textContent.includes('hidden_auth') || anchor.textContent.includes('hidden_dash')) {{
                return;
            }}
            let href = anchor.getAttribute('href');
            if (href === '/auth' || href === '/dashboard' || href === 'pages/auth.py' || href === 'pages/dashboard.py') {{
                if (!anchor.dataset.intercepted) {{
                    anchor.dataset.intercepted = "true";
                    anchor.addEventListener('click', function(e) {{
                        e.preventDefault();
                        let targetKey = href.includes('auth') ? 'auth' : 'dashboard';
                        let streamlitLink = document.querySelector('div[data-testid="stPageLink"] a[href*="' + targetKey + '"]');
                        if (streamlitLink) {{
                            streamlitLink.click();
                        }} else {{
                            window.location.href = href;
                        }}
                    }});
                }}
            }}
        }});
    }}
    setupInterceptors();
    setInterval(setupInterceptors, 200);
}})();
</script>
"""

# Streamlit's markdown parser follows standard Markdown rules, where any
# line indented 4+ spaces is rendered as a literal code block. Our HTML is
# deeply nested (8/12+ spaces per line), which was causing chunks of it to
# show up as raw text instead of being parsed as markup. Stripping leading
# whitespace from each line avoids that while leaving the rendered HTML
# unaffected (HTML doesn't care about indentation).
landing_html_flat = "\n".join(line.lstrip() for line in landing_html.split("\n"))

st.markdown(landing_html_flat, unsafe_allow_html=True)

# Hidden page links to allow client-side single page app navigation
st.markdown("<div style='display:none;'>", unsafe_allow_html=True)
st.page_link("pages/auth.py", label="hidden_auth")
st.page_link("pages/dashboard.py", label="hidden_dash")
st.markdown("</div>", unsafe_allow_html=True)