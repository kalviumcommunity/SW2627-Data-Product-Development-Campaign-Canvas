import sys
from pathlib import Path

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from datetime import datetime
import streamlit as st
from src.utils.clerk_auth import handle_clerk_callback, get_clerk_credentials, get_clerk_endpoints

st.set_page_config(page_title="Sign in — CampaignIQ", page_icon="📊", layout="wide")

# Process any Clerk authentication callback parameters
handle_clerk_callback()

# ---------- Styling: reskin default Streamlit widgets to match the dark CampaignIQ theme ----------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}}

.stApp {{
    background: radial-gradient(circle at 10% 20%, rgba(56, 189, 248, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(99, 102, 241, 0.15) 0%, transparent 40%),
                #030712 !important;
}}

header[data-testid="stHeader"] {{ background: transparent !important; }}
section[data-testid="stSidebar"] {{ display: none !important; }}
#MainMenu, footer {{ visibility: hidden; }}

div.block-container {{
    max-width: 1100px;
    padding-top: 4rem;
    padding-bottom: 4rem;
}}

/* Card wrapper — targets a stable, version-proof key instead of Streamlit's
   internal testid (which changes between versions and also matches st.form's
   own default border, causing a nested/mismatched box). */
.st-key-auth_card {{
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 1.25rem;
    padding: 2.5rem 2.5rem 2rem;
    backdrop-filter: blur(12px);
    max-width: 460px;
    margin: 0 auto;
}}

.auth-logo {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1.75rem;
}}
.auth-logo-icon {{
    height: 2.25rem;
    width: 2.25rem;
    border-radius: 0.75rem;
    background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
    display: grid;
    place-items: center;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
    color: white;
}}
.auth-logo-icon svg {{ width: 1.25rem; height: 1.25rem; }}
.auth-logo-text {{ font-size: 1.125rem; font-weight: 600; letter-spacing: -0.02em; color: white; }}

.auth-title {{ color: white; font-size: 1.6rem; font-weight: 700; margin: 0 0 0.25rem 0; }}
.auth-subtitle {{ color: #9ca3af; font-size: 0.9rem; margin-bottom: 0; }}

.auth-divider {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 1.5rem 0 1rem 0;
    color: #6b7280;
    font-size: 0.75rem;
}}
.auth-divider::before, .auth-divider::after {{
    content: "";
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.1);
}}

.back-home {{
    text-align: center;
    margin-top: 1.5rem;
    font-size: 0.8rem;
}}
.back-home a {{ color: #9ca3af; text-decoration: none; }}
.back-home a:hover {{ color: white; }}

/* Left promo panel */
.promo-panel {{
    background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
    border-radius: 1.25rem;
    padding: 2.5rem;
    height: 100%;
    min-height: 480px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    color: white;
    position: relative;
    overflow: hidden;
}}
.promo-panel::after {{
    content: "";
    position: absolute;
    bottom: -6rem;
    right: -6rem;
    height: 20rem;
    width: 20rem;
    border-radius: 50%;
    background: rgba(255,255,255,0.12);
    filter: blur(10px);
}}
.promo-headline {{ font-size: 1.9rem; font-weight: 800; line-height: 1.2; margin-top: 1.5rem; }}
.promo-body {{ margin-top: 1rem; font-size: 0.95rem; color: rgba(255,255,255,0.85); max-width: 22rem; }}
.promo-footer {{ font-size: 0.8rem; color: rgba(255,255,255,0.7); }}

/* Clerk button — purple themed login button with a key icon */
.st-key-clerk_btn button {{
    background: #6c47ff !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    position: relative;
    padding-left: 2.25rem !important;
    box-shadow: 0 0 15px rgba(108, 71, 255, 0.4) !important;
}}
.st-key-clerk_btn button:hover {{
    background: #5b3ae0 !important;
    color: white !important;
    box-shadow: 0 0 20px rgba(108, 71, 255, 0.6) !important;
}}
.st-key-clerk_btn button:focus:not(:active) {{
    border-color: transparent !important;
    color: white !important;
    box-shadow: 0 0 15px rgba(108, 71, 255, 0.4) !important;
}}
.st-key-clerk_btn button::before {{
    content: "";
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    width: 1.1rem;
    height: 1.1rem;
    background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGZpbGw9Im5vbmUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMi41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0yMSAybC0yIDJtLTcuNjEgNy42MWE1LjUgNS41IDAgMSAxLTcuNzc4IDcuNzc4IDUuNSA1LjUgMCAxIDEgNy43NzctNy43Nzd6bSAwbDE1LjUgNy41bTAgMGwzIDNMMjIgN2wtMy0zbS0zLjUgMy41TDE5IDQiLz48L3N2Zz4=");
    background-size: contain;
    background-repeat: no-repeat;
}}

/* Inputs */
.stTextInput input {{
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: white !important;
    border-radius: 0.6rem !important;
}}
.stTextInput input:focus {{
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 1px #38bdf8 !important;
}}
.stTextInput label {{ color: #d1d5db !important; font-size: 0.85rem !important; }}
/* Password "show/hide" eye icon defaults to the theme's primaryColor on hover/focus */
.stTextInput button svg {{ fill: #9ca3af !important; }}
.stTextInput button:hover svg {{ fill: white !important; }}

/* Tabs — hardcode every BaseWeb tab part (pill container, active highlight bar,
   bottom border, focus ring) so none of them can fall back to Streamlit's
   default theme primaryColor (red). */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0;
    background: rgba(255,255,255,0.04);
    border-radius: 0.6rem;
    padding: 0.2rem;
}}
.stTabs [data-baseweb="tab-highlight"] {{
    background-color: transparent !important;
}}
.stTabs [data-baseweb="tab-border"] {{
    background-color: transparent !important;
}}
.stTabs button[data-baseweb="tab"] {{
    color: #9ca3af !important;
    background-color: transparent !important;
    border: none !important;
    border-radius: 0.5rem !important;
    flex: 1;
    justify-content: center;
    transition: background-color 0.15s ease, color 0.15s ease;
}}
.stTabs button[data-baseweb="tab"] p {{
    color: inherit !important;
}}
.stTabs button[data-baseweb="tab"]:hover {{
    color: white !important;
    background-color: rgba(255,255,255,0.04) !important;
}}
.stTabs button[data-baseweb="tab"]:focus {{
    outline: none !important;
    box-shadow: none !important;
}}
.stTabs button[aria-selected="true"] {{
    background-color: rgba(255,255,255,0.08) !important;
    color: white !important;
}}
.stTabs button[aria-selected="true"]:hover {{
    background-color: rgba(255,255,255,0.08) !important;
}}

/* Primary submit button */
div[data-testid="stFormSubmitButton"] button {{
    background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%) !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 0.6rem !important;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
}}
div[data-testid="stFormSubmitButton"] button:hover {{
    filter: brightness(1.08);
}}
div[data-testid="stFormSubmitButton"] button:focus:not(:active) {{
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.3) !important;
    color: white !important;
    border-color: transparent !important;
}}
</style>
""", unsafe_allow_html=True)

logo_svg = """<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>"""

col_promo, col_form = st.columns([1, 1], gap="large")

with col_promo:
    st.markdown(f"""
    <div class="promo-panel">
        <div class="auth-logo">
            <div class="auth-logo-icon" style="background:rgba(255,255,255,0.2); box-shadow:none;">{logo_svg}</div>
            <span class="auth-logo-text">CampaignIQ</span>
        </div>
        <div>
            <div class="promo-headline">Ship marketing insights, not spreadsheets.</div>
            <div class="promo-body">One workspace for ingestion, cleaning, KPIs, funnels, dashboards, alerts, and executive reports.</div>
        </div>
        <div class="promo-footer">© {datetime.now().year} CampaignIQ</div>
    </div>
    """, unsafe_allow_html=True)

with col_form:
    card = st.container(key="auth_card")
    with card:
        st.markdown(f"""
        <div class="auth-logo">
            <div class="auth-logo-icon">{logo_svg}</div>
            <span class="auth-logo-text">CampaignIQ</span>
        </div>
        <div class="auth-title">Welcome</div>
        <p class="auth-subtitle">Sign in to your analytics workspace.</p>
        """, unsafe_allow_html=True)

        clerk_wrap = st.container(key="clerk_btn")
        with clerk_wrap:
            if st.button("Continue with Clerk", use_container_width=True):
                client_id, client_secret, domain, redirect_uri = get_clerk_credentials()
                if client_id and client_secret and domain:
                    st.session_state["clerk_redirect_uri"] = redirect_uri
                    endpoints = get_clerk_endpoints(domain)
                    
                    import uuid
                    state = str(uuid.uuid4())
                    st.session_state["clerk_oauth_state"] = state
                    
                    auth_url = (
                        f"{endpoints['authorization_endpoint']}"
                        f"?client_id={client_id}"
                        f"&redirect_uri={redirect_uri}"
                        "&response_type=code"
                        "&scope=openid%20profile%20email"
                        f"&state={state}"
                    )
                    redirect_js = f"<script>window.top.location.href = '{auth_url}';</script>"
                    st.components.v1.html(redirect_js, height=0)
                else:
                    st.session_state["show_clerk_setup"] = True

        if st.session_state.get("show_clerk_setup", False):
            st.markdown("""
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 0.75rem; padding: 1rem; margin-top: 1rem; margin-bottom: 1rem;">
                <h4 style="color: #f87171; margin-top: 0; margin-bottom: 0.5rem; font-size: 0.95rem; font-weight: 600;">Clerk Setup Required</h4>
                <p style="color: #d1d5db; font-size: 0.85rem; line-height: 1.4; margin: 0 0 0.75rem 0;">
                    Clerk credentials are not configured. To enable live login, please configure your Clerk API keys in your environment variables or Streamlit secrets:
                </p>
                <code style="background: rgba(0,0,0,0.3); padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; color: #38bdf8; display: block; margin-bottom: 0.5rem; white-space: pre-wrap;">
CLERK_CLIENT_ID=your-client-id
CLERK_CLIENT_SECRET=your-client-secret
CLERK_DOMAIN=your-clerk-domain
CLERK_REDIRECT_URI=http://localhost:8501/
                </code>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Proceed with Mock Clerk Login", key="mock_clerk_login_btn", use_container_width=True):
                with st.spinner("Redirecting to Clerk mock login screen..."):
                    import time
                    time.sleep(1.0)
                st.session_state.logged_in = True
                st.session_state.email = "demo.clerk.user@gmail.com"
                st.success("Welcome back! Redirecting to dashboard...")
                st.switch_page("pages/dashboard.py")

        st.markdown('<div class="auth-divider">or</div>', unsafe_allow_html=True)

        tab_signin, tab_signup, tab_reset = st.tabs(["Sign in", "Sign up", "Reset"])

        with tab_signin:
            with st.form("signin_form", border=False):
                email = st.text_input("Email", key="signin_email")
                password = st.text_input("Password", type="password", key="signin_password")
                submitted = st.form_submit_button("Sign in", use_container_width=True)
                if submitted:
                    if not email or not password:
                        st.error("Please enter both email and password.")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.email = email
                        st.success("Welcome back! Redirecting to dashboard...")
                        st.switch_page("pages/dashboard.py")

        with tab_signup:
            with st.form("signup_form", border=False):
                name = st.text_input("Full name", key="signup_name")
                email_up = st.text_input("Email", key="signup_email")
                password_up = st.text_input("Password", type="password", key="signup_password")
                submitted_up = st.form_submit_button("Create account", use_container_width=True)
                if submitted_up:
                    if not name or not email_up or len(password_up) < 6:
                        st.error("Fill in all fields — password needs at least 6 characters.")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.email = email_up
                        st.success("Account created! Redirecting to dashboard...")
                        st.switch_page("pages/dashboard.py")

        with tab_reset:
            with st.form("reset_form", border=False):
                email_reset = st.text_input("Email", key="reset_email")
                submitted_reset = st.form_submit_button("Send reset link", use_container_width=True)
                if submitted_reset:
                    if not email_reset:
                        st.error("Enter your email first.")
                    else:
                        st.success("Reset link sent — hook this up to your auth backend to actually send it.")

        st.markdown(
            '<div class="back-home"><a href="/" target="_top">← Back to home</a></div>',
            unsafe_allow_html=True,
        )