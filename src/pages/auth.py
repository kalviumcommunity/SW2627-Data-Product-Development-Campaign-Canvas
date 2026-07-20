import sys
from pathlib import Path

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from datetime import datetime
import streamlit as st
from src.utils.clerk_auth import (
    handle_clerk_callback,
    get_clerk_credentials,
    get_clerk_endpoints,
    check_and_restore_session,
)

st.set_page_config(page_title="Sign in — CampaignCanvas", page_icon="📊", layout="wide")

# Restore session from cookies
check_and_restore_session()

# Process any Clerk authentication callback parameters
handle_clerk_callback()

# Check if user is logged in
if st.session_state.get("logged_in", False):
    st.switch_page("pages/dashboard.py")


# ---------- Styling: reskin default Streamlit widgets to match the dark CampaignCanvas theme ----------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}}

.stApp,
.stMain,
[data-testid="stMain"],
div.block-container,
[data-testid="stAppHeader"],
header[data-testid="stHeader"] {{
    padding: 0 !important;
    margin: 0 !important;
    padding-top: 0 !important;
    margin-top: 0 !important;
    top: 0 !important;
}}

.stApp {{
    background: #030712 !important;
    height: 100vh !important;
    overflow: hidden !important;
}}

header[data-testid="stHeader"],
div[data-testid="stAppHeader"] {{
    display: none !important;
    height: 0px !important;
}}

section[data-testid="stSidebar"] {{ display: none !important; }}
#MainMenu, footer {{ visibility: hidden; }}

/* Force Streamlit block container to fill 100% viewport width and height (no gap) */
div.block-container {{
    max-width: 100% !important;
    width: 100% !important;
    height: 100vh !important;
}}

/* Horizontal columns layout - unify to single card split down the middle */
div[data-testid="stHorizontalBlock"] {{
    background: #090d16 !important;
    border: none !important;
    border-radius: 0px !important;
    overflow: hidden !important;
    gap: 0px !important;
    max-width: 100% !important;
    width: 100% !important;
    margin: 0 !important;
    display: flex !important;
    flex-direction: row !important;
    min-height: 100vh !important;
    height: 100vh !important;
    box-shadow: none !important;
}}

/* Left panel column wrapper */
div[data-testid="stHorizontalBlock"] > div:first-child,
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child,
.stColumn:first-child {{
    background: linear-gradient(180deg, #38bdf8 0%, #7dd3fc 100%) !important;
    background-color: linear-gradient(180deg, #38bdf8 0%, #7dd3fc 100%) !important;
    color: #030712 !important;
    padding: 4rem 3.5rem !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    align-items: flex-start !important;
    min-height: 100vh !important;
    height: 100vh !important;
    border-radius: 1rem 0 0 1rem !important;
}}



/* Hide standard Streamlit gap/margin/padding inside the columns */
div[data-testid="column"] > div {{
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
}}

/* Promo panel content styling */
.promo-panel {{
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    align-items: flex-start !important;
    height: 100% !important;
    color: #090d16 !important;
    text-align: left !important;
}}
.promo-headline {{
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    line-height: 1.2 !important;
    margin-top: 0 !important;
    margin-bottom: 1rem !important;
    color: #090d16 !important;
    letter-spacing: -0.03em !important;
    text-align: left !important;
}}
.promo-body {{
    margin-top: 1rem !important;
    font-size: 1.1rem !important;
    color: rgba(9, 13, 22, 0.8) !important;
    line-height: 1.6 !important;
    max-width: 28rem !important;
    text-align: left !important;
}}
.promo-footer {{
    font-size: 0.85rem !important;
    color: rgba(9, 13, 22, 0.6) !important;
    font-weight: 500 !important;
    margin-top: 0 !important;
    text-align: left !important;
}}

/* Right panel column wrapper */
div[data-testid="stHorizontalBlock"] > div:last-child,
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child,
.stColumn:last-child {{
    background: radial-gradient(circle at top, rgba(15, 23, 42, 0.8) 0%, #030712 100%) !important;
    padding: 3rem 3.5rem !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    min-height: 100vh !important;
    height: 100vh !important;
}}

/* Card wrapper - Auth Form Card */
.st-key-auth_card {{
    background: rgba(15, 23, 42, 0.8) !important;
    border: 1px solid rgba(148, 163, 184, 0.1) !important;
    border-radius: 1.25rem !important;
    padding: 2.5rem 2.75rem 2rem !important;
    backdrop-filter: blur(20px) !important;
    max-width: 450px !important;
    width: 100% !important;
    margin: 0 auto !important;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5) !important;
}}

.auth-logo {{
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 0.75rem;
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

/* Darken the logo icon on the left promo panel */
div[data-testid="column"]:first-child .auth-logo-icon {{
    background: rgba(9, 13, 22, 0.08) !important;
    border: 1px solid rgba(9, 13, 22, 0.15) !important;
    box-shadow: none !important;
    color: #090d16 !important;
}}
div[data-testid="column"]:first-child .auth-logo-icon svg {{
    stroke: #090d16 !important;
}}
div[data-testid="column"]:first-child .auth-logo-text {{
    color: #090d16 !important;
    font-weight: 700 !important;
}}

.auth-title {{ color: white; font-size: 1.75rem; font-weight: 700; margin: 0 0 0.35rem 0; }}
.auth-subtitle {{ color: #9ca3af; font-size: 0.9rem; margin-bottom: 3; }}

.auth-divider {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 1.5rem 0 1rem 0;
    color: #4b5563;
    font-size: 0.75rem;
}}
.auth-divider::before, .auth-divider::after {{
    content: "";
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.08);
}}

.back-home {{
    text-align: center;
    margin-top: 1.5rem;
    font-size: 0.85rem;
}}
.back-home a {{ color: #9ca3af; text-decoration: none; transition: color 0.2s ease; }}
.back-home a:hover {{ color: white; }}

/* Clerk Login Button - links and styled buttons */
.clerk-btn,
div.st-key-clerk_setup_trigger_btn button,
div.st-key-mock_clerk_login_btn button {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: #6c47ff !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    text-decoration: none !important;
    border-radius: 0.6rem !important;
    height: 2.75rem !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 15px rgba(108, 71, 255, 0.4) !important;
}}
.clerk-btn:hover,
div.st-key-clerk_setup_trigger_btn button:hover,
div.st-key-mock_clerk_login_btn button:hover {{
    background: #5b3ae0 !important;
    color: white !important;
    box-shadow: 0 0 20px rgba(108, 71, 255, 0.6) !important;
    text-decoration: none !important;
}}

/* Insert Clerk logo dynamically on Streamlit button triggers */
.clerk-btn::before,
div.st-key-clerk_setup_trigger_btn button::before,
div.st-key-mock_clerk_login_btn button::before {{
    content: "" !important;
    display: inline-block !important;
    width: 1.1rem !important;
    height: 1.1rem !important;
    margin-right: 0.65rem !important;
    background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGZpbGw9Im5vbmUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMi41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0yMSAybC0yIDJtLTcuNjEgNy42MWE1LjUgNS41IDAgMSAxLTcuNzc4IDcuNzc4IDUuNSA1LjUgMCAxIDEgNy43NzctNy43Nzd6bSAwbDE1LjUgNy41bTAgMGwzIDNMMjIgN2wtMy0zbS0zLjUgMy41TDE5IDQiLz48L3N2Zz4=");
    background-size: contain !important;
    background-repeat: no-repeat !important;
}}

/* BaseWeb Input styling (Email, Password, Name) */
div[data-testid="stTextInput"] > div {{
    background-color: rgba(15, 23, 42, 0.65) !important;
    background: rgba(15, 23, 42, 0.65) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 0.6rem !important;
    transition: all 0.2s ease !important;
}}

/* BaseWeb Input Focus styling */
div[data-testid="stTextInput"] > div:focus-within {{
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 1px #38bdf8 !important;
}}

/* Clear borders, backgrounds, and shadows on inner container wrappers to resolve the double border issue */
div[data-testid="stTextInput"] > div div,
div[data-testid="stTextInput"] > div div:focus-within,
div[data-baseweb="input"],
div[data-baseweb="input"]:focus-within {{
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
    border-bottom: none !important;
    box-shadow: none !important;
}}

div[data-testid="stTextInput"] input,
div[data-baseweb="input"] input,
input {{
    background-color: transparent !important;
    background: transparent !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: none !important;
}}

/* Input Labels */
div[data-testid="stTextInput"] label,
.stTextInput label {{
    color: #cbd5e1 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    margin-bottom: 0.35rem !important;
}}

/* Password eye icons */
div[data-testid="stTextInput"] button svg,
.stTextInput button svg {{
    fill: #6b7280 !important;
}}
div[data-testid="stTextInput"] button:hover svg,
.stTextInput button:hover svg {{
    fill: #ffffff !important;
}}

/* Tabs override to dark themed pill container */
[role="tablist"] {{
    gap: 4px !important;
    background: rgba(15, 23, 42, 0.7) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 9999px !important;
    padding: 0.25rem !important;
}}

/* Hide highlight indicators/presentations inside tablist */
[role="tablist"] > *:not([role="tab"]),
[role="tablist"] [role="presentation"],
[data-baseweb="tab-highlight"],
[data-baseweb="tab-border"],
[role="tab"] > div:nth-child(2),
[role="tab"] div:nth-child(2),
[role="tab"]::after,
[role="tab"]::before,
[role="tab"][aria-selected="true"]::after,
[role="tab"][aria-selected="true"]::before {{
    background-color: transparent !important;
    background: transparent !important;
    display: none !important;
    height: 0px !important;
    width: 0px !important;
    border: none !important;
    content: none !important;
}}

[role="tablist"] > div {{
    background-color: transparent !important;
    background: transparent !important;
}}

/* Individual tabs styling */
[role="tab"] {{
    color: #9ca3af !important;
    background-color: transparent !important;
    border: none !important;
    border-bottom: none !important;
    border-radius: 0.45rem !important;
    flex: 1 !important;
    justify-content: center !important;
    transition: all 0.2s ease !important;
    padding: 0.5rem 1rem !important;
    height: auto !important;
}}

/* Brute force remove borders and red accents from tab headers with high specificity */
html body [data-testid="stApp"] [role="tablist"],
html body [data-testid="stApp"] [role="tablist"] *,
html body [data-testid="stApp"] [role="tab"],
html body [data-testid="stApp"] [role="tab"] * {{
    border: none !important;
    border-bottom: none !important;
    box-shadow: none !important;
    outline: none !important;
}}

/* Set default background of all tablist direct child div elements to transparent to hide indicators */
html body [data-testid="stApp"] [role="tablist"] > div,
html body [data-testid="stApp"] [role="tablist"] > div * {{
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
    border-bottom: none !important;
    box-shadow: none !important;
    outline: none !important;
}}

html body [data-testid="stApp"] div[data-testid="stTabs"] [role="tablist"] [role="tab"] *,
html body [data-testid="stApp"] div[data-testid="stTabs"] [role="tablist"] [role="tab"] p,
html body [data-testid="stApp"] div[data-testid="stTabs"] [role="tablist"] [role="tab"] span,
[role="tablist"] [role="tab"] *,
[role="tab"] * {{
    color: #9ca3af !important;
    font-weight: 500 !important;
}}

/* Hover state */
[role="tab"]:hover {{
    background-color: rgba(255, 255, 255, 0.03) !important;
}}
div[data-testid="stTabs"] [role="tablist"] [role="tab"]:hover *,
[role="tablist"] [role="tab"]:hover *,
[role="tab"]:hover * {{
    color: white !important;
}}

/* Selected active tab state */
html body [data-testid="stApp"] [role="tablist"] button[aria-selected="true"],
html body [data-testid="stApp"] [role="tablist"] [role="tab"][aria-selected="true"],
html body [data-testid="stApp"] button[data-baseweb="tab"][aria-selected="true"] {{
    background-color: #1e293b !important;
    box-shadow: 0 0 0 0.5px #38bdf8 !important;
    border-radius: 0.7rem !important;
}}
div[data-testid="stTabs"] [role="tablist"] [role="tab"][aria-selected="true"] *,
div[data-testid="stTabs"] [role="tablist"] [role="tab"][aria-selected="true"] p,
div[data-testid="stTabs"] [role="tablist"] [role="tab"][aria-selected="true"] span,
[role="tablist"] [role="tab"][aria-selected="true"] *,
[role="tab"][aria-selected="true"] * {{
    color: white !important;
    font-weight: 600 !important;
}}

[role="tab"]:focus {{
    outline: none !important;
    box-shadow: none !important;
}}

/* Submit Form Button styling */
div[data-testid="stFormSubmitButton"] button,
.stButton button {{
    background: linear-gradient(135deg, #38bdf8 0%, #7dd3fc 100%) !important;
    color: #030712 !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 0.875rem !important;
    box-shadow: 0 10px 30px rgba(56, 189, 248, 0.25) !important;
    width: 100% !important;
    min-height: 3rem !important;
    transition: all 0.2s ease !important;
}}
div[data-testid="stFormSubmitButton"] button:hover,
.stButton button:hover {{
    background: linear-gradient(135deg, #4ab3ff 0%, #8de4ff 100%) !important;
    color: #030712 !important;
    box-shadow: 0 15px 35px rgba(56, 189, 248, 0.35) !important;
    transform: translateY(-1px) !important;
}}
div[data-testid="stFormSubmitButton"] button:focus:not(:active),
.stButton button:focus:not(:active) {{
    color: #030712 !important;
    border-color: transparent !important;
}}

/* --- Streamlit Override Fixes --- */
[data-testid="stMarkdownContainer"] .clerk-btn {{
    color: white !important;
    text-decoration: none !important;
}}
[data-testid="stMarkdownContainer"] .clerk-btn:hover {{
    color: white !important;
    text-decoration: none !important;
}}
[data-testid="stMarkdownContainer"] .back-home a {{
    color: #9ca3af !important;
    text-decoration: none !important;
}}
[data-testid="stMarkdownContainer"] .back-home a:hover {{
    color: white !important;
    text-decoration: none !important;
}}
</style>
""", unsafe_allow_html=True)

logo_svg = """<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>"""

col_promo, col_form = st.columns([1, 1])

with col_promo:
    st.markdown(f"""
    <div class="promo-panel">
        <div class="auth-logo">
            <div class="auth-logo-icon">{logo_svg}</div>
            <span class="auth-logo-text">CampaignCanvas</span>
        </div>
        <div>
            <div class="promo-headline">Ship marketing insights, not spreadsheets.</div>
            <div class="promo-body">One workspace for ingestion, cleaning, KPIs, funnels, dashboards, alerts, and executive reports.</div>
        </div>
        <div class="promo-footer">© {datetime.now().year} CampaignCanvas</div>
    </div>
    """, unsafe_allow_html=True)

with col_form:
    card = st.container(key="auth_card")
    with card:
        st.markdown(f"""
        <div class="auth-title">Welcome</div>
        <p class="auth-subtitle">Sign in to your analytics workspace.</p>
        """, unsafe_allow_html=True)

        client_id, client_secret, domain, redirect_uri = get_clerk_credentials()
        clerk_wrap = st.container(key="clerk_btn")
        with clerk_wrap:
            if client_id and client_secret and domain:
                st.session_state["clerk_redirect_uri"] = redirect_uri
                endpoints = get_clerk_endpoints(domain)
                
                import uuid
                state = st.session_state.get("clerk_oauth_state")
                if not state:
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
                clerk_button_html = f'''
                <a href="{auth_url}" target="_self" class="clerk-btn">
                    Continue with Clerk
                </a>
                '''
                st.markdown(clerk_button_html, unsafe_allow_html=True)
            else:
                if st.button("Continue with Clerk", use_container_width=True, key="clerk_setup_trigger_btn"):
                    st.session_state["show_clerk_setup"] = True

        if st.session_state.get("show_clerk_setup", False):
            st.markdown("""
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 0.75rem; padding: 1rem; margin-top: 1rem; margin-bottom: 1rem;">
                <h4 style="color: #f87171; margin-top: 0; margin-bottom: 0.5rem; font-size: 0.95rem; font-weight: 600;">Clerk Auth Setup Required</h4>
                <p style="color: #d1d5db; font-size: 0.85rem; line-height: 1.4; margin: 0 0 0.75rem 0;">
                    Authentication credentials are not configured. To enable live login, please configure your Clerk API keys in your environment variables or Streamlit secrets:
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