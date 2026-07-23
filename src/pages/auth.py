import sys
from datetime import datetime
from pathlib import Path

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import streamlit as st

from src.utils.clerk_auth import (
    check_and_restore_session,
    get_clerk_credentials,
    get_clerk_endpoints,
    handle_clerk_callback,
)
from src.utils.load_css import load_css

st.set_page_config(page_title="Sign in — CampaignCanvas", page_icon=":material/bar_chart:", layout="wide")
load_css()

check_and_restore_session()
handle_clerk_callback()

if st.session_state.get("logged_in", False):
    st.switch_page("pages/dashboard.py")

theme = st.session_state.get("theme", "dark")
is_light = theme == "light"
next_theme = "light" if theme == "dark" else "dark"

theme_icon = """
<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 3a1 1 0 0 1 1 1v1.08a7 7 0 1 1-3.08 12.91 1 1 0 0 1 1.14-1.64A5 5 0 1 0 12 5V4a1 1 0 0 1 1-1Z"/>
    <path d="M12 1.75v2.5M12 19.75v2.5M4.22 4.22l1.77 1.77M17.99 17.99l1.77 1.77M1.75 12h2.5M19.75 12h2.5M4.22 19.78l1.77-1.77M17.99 6.01l1.77-1.77"/>
</svg>
""" if theme == "dark" else """
<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 12.8A8.5 8.5 0 1 1 11.2 3a7 7 0 1 0 9.8 9.8Z"/>
</svg>
"""

page_bg = (
    "linear-gradient(180deg, #f8fbff 0%, #eef6ff 45%, #eaf1ff 100%)"
    if is_light
    else "radial-gradient(circle at top, color-mix(in oklab, var(--card) 86%, transparent) 0%, var(--background) 100%)"
)
left_bg = "linear-gradient(180deg, #eff6ff 0%, #dbeafe 100%)" if is_light else "linear-gradient(180deg, #38bdf8 0%, #7dd3fc 100%)"
left_text = "#0f172a" if is_light else "#030712"
left_muted = "rgba(15, 23, 42, 0.72)" if is_light else "rgba(9, 13, 22, 0.8)"
left_soft = "rgba(15, 23, 42, 0.56)" if is_light else "rgba(9, 13, 22, 0.6)"
icon_bg = "rgba(255, 255, 255, 0.72)" if is_light else "rgba(9, 13, 22, 0.08)"
icon_border = "rgba(148, 163, 184, 0.22)" if is_light else "rgba(9, 13, 22, 0.15)"
card_bg = "rgba(255, 255, 255, 0.9)" if is_light else "var(--card)"
card_border = "rgba(148, 163, 184, 0.18)" if is_light else "var(--border)"

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}}

/* Hide overlapping form submit instructions */
[data-testid="InputInstructions"],
div[data-testid="InputInstructions"],
small[data-testid="InputInstructions"],
.stForm [data-testid="InputInstructions"],
form [data-testid="InputInstructions"] {{
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    width: 0 !important;
    opacity: 0 !important;
    pointer-events: none !important;
}}

.theme-toggle-link {{
    width: 2.25rem !important;
    height: 2.25rem !important;
    border-radius: 9999px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    border: 1px solid var(--border) !important;
    background: color-mix(in oklab, var(--foreground) 6%, transparent) !important;
    color: var(--foreground) !important;
    text-decoration: none !important;
    transition: all 0.2s ease !important;
}}
.theme-toggle-link svg {{
    width: 1rem !important;
    height: 1rem !important;
    stroke: var(--foreground) !important;
}}
.theme-toggle-link:hover {{
    transform: translateY(-1px) !important;
    background: color-mix(in oklab, var(--foreground) 12%, transparent) !important;
}}

.stApp,
.stMain,
[data-testid="stMain"],
[data-testid="stAppHeader"],
header[data-testid="stHeader"] {{
    padding: 0 !important;
    margin: 0 !important;
    top: 0 !important;
}}

.stApp {{
    background: {page_bg} !important;
    min-height: 100vh !important;
    overflow: hidden !important;
    padding: 0.65rem !important;
}}

header[data-testid="stHeader"],
div[data-testid="stAppHeader"] {{
    display: none !important;
    height: 0 !important;
}}

section[data-testid="stSidebar"],
#MainMenu,
footer:not(.footer) {{
    display: none !important;
    visibility: hidden !important;
}}

div.block-container {{
    max-width: 100% !important;
    width: 100% !important;
    height: calc(100vh - 1.3rem) !important;
    padding: 0 !important;
}}

div[data-testid="stHorizontalBlock"] {{
    background: {page_bg} !important;
    gap: 0 !important;
    max-width: 100% !important;
    width: 100% !important;
    margin: 0 !important;
    display: flex !important;
    flex-direction: row !important;
    min-height: calc(100vh - 1.3rem) !important;
    height: calc(100vh - 1.3rem) !important;
    box-shadow: none !important;
    border-radius: 1.35rem !important;
    overflow: hidden !important;
}}

div[data-testid="stHorizontalBlock"] > div:first-child,
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child,
.stColumn:first-child {{
    background: {left_bg} !important;
    color: {left_text} !important;
    padding: 4rem 3rem 3rem 2.5rem !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    align-items: flex-start !important;
    min-height: calc(100vh - 1.3rem) !important;
    height: calc(100vh - 1.3rem) !important;
    flex: 0 0 52% !important;
    max-width: 52% !important;
}}

div[data-testid="stHorizontalBlock"] > div:last-child,
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child,
.stColumn:last-child {{
    background: var(--background) !important;
    padding: 4rem 3.5rem 3rem 3.5rem !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: flex-start !important;
    align-items: center !important;
    min-height: calc(100vh - 1.3rem) !important;
    height: calc(100vh - 1.3rem) !important;
    flex: 0 0 48% !important;
    max-width: 48% !important;
}}

.promo-panel {{
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    align-items: flex-start !important;
    height: 100% !important;
    color: {left_text} !important;
}}

.auth-logo {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 3.75rem;
}}

.auth-logo-icon {{
    height: 2.25rem;
    width: 2.25rem;
    border-radius: 0.75rem;
    background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
    display: grid;
    place-items: center;
    box-shadow: 0 0 18px rgba(56, 189, 248, 0.28);
    color: white;
}}

.auth-logo-icon svg {{ width: 1.25rem; height: 1.25rem; }}
.auth-logo-text {{ font-size: 1.125rem; font-weight: 700; letter-spacing: -0.02em; color: {left_text}; }}

div[data-testid="column"]:first-child .auth-logo-icon {{
    background: {icon_bg} !important;
    border: 1px solid {icon_border} !important;
    box-shadow: none !important;
    color: {left_text} !important;
}}

div[data-testid="column"]:first-child .auth-logo-icon svg {{ stroke: {left_text} !important; }}

div[data-testid="column"]:first-child .auth-logo-text {{ color: {left_text} !important; }}

.promo-headline {{
    font-size: clamp(2.15rem, 3.25vw, 3rem) !important;
    font-weight: 800 !important;
    line-height: 1.05 !important;
    letter-spacing: -0.04em !important;
    max-width: 13ch !important;
    margin: 0 0 1rem 0 !important;
    color: {left_text} !important;
}}

.promo-body {{
    max-width: 30rem !important;
    margin-top: 0.9rem !important;
    font-size: 1.05rem !important;
    line-height: 1.65 !important;
    color: {left_muted} !important;
}}

.promo-footer {{
    font-size: 0.85rem !important;
    color: {left_soft} !important;
    font-weight: 500 !important;
}}

.st-key-auth_card {{
    background: {card_bg} !important;
    border: 1px solid {card_border} !important;
    border-radius: 1.35rem !important;
    padding: 2.15rem 2.35rem 1.85rem !important;
    backdrop-filter: blur(20px) !important;
    max-width: 380px !important;
    width: 100% !important;
    margin: 0 auto !important;
    box-shadow: var(--shadow-card) !important;
    margin-top: 0.5rem !important;
}}

.auth-title {{ color: var(--foreground) !important; font-size: 1.8rem !important; font-weight: 700 !important; margin: 0 0 0.35rem 0 !important; letter-spacing: -0.03em !important; }}
.auth-subtitle {{ color: var(--muted-foreground) !important; font-size: 0.95rem !important; margin-bottom: 1.5rem !important; line-height: 1.5 !important; }}

.auth-divider {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 1.35rem 0 1rem 0;
    color: var(--muted-foreground);
    font-size: 0.75rem;
}}

.auth-divider::before,
.auth-divider::after {{
    content: "";
    flex: 1;
    height: 1px;
    background: var(--border);
}}

.back-home {{ text-align: center; margin-top: 1.35rem; font-size: 0.85rem; }}
.back-home a {{ color: var(--muted-foreground) !important; text-decoration: none !important; transition: color 0.2s ease !important; }}
.back-home a:hover {{ color: var(--foreground) !important; }}

.clerk-btn,
div.st-key-clerk_setup_trigger_btn button,
div.st-key-mock_clerk_login_btn button {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0.65rem !important;
    background: linear-gradient(135deg, #6c47ff 0%, #8b5cf6 100%) !important;
    color: white !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    text-decoration: none !important;
    border-radius: 0.9rem !important;
    height: 3rem !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease !important;
    box-shadow: 0 12px 30px rgba(108, 71, 255, 0.26) !important;
}}
.clerk-btn:hover,
div.st-key-clerk_setup_trigger_btn button:hover,
div.st-key-mock_clerk_login_btn button:hover {{
    transform: translateY(-1px) !important;
    filter: brightness(1.03) !important;
    box-shadow: 0 16px 34px rgba(108, 71, 255, 0.34) !important;
}}
.clerk-btn::before,
div.st-key-clerk_setup_trigger_btn button::before,
div.st-key-mock_clerk_login_btn button::before {{
    content: "" !important;
    display: inline-block !important;
    width: 1.1rem !important;
    height: 1.1rem !important;
    background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGZpbGw9Im5vbmUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMi41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0yMSAybC0yIDJtLTcuNjEgNy42MWE1LjUgNS41IDAgMSAxLTcuNzc4IDcuNzc4IDUuNSA1LjUgMCAxIDEgNy43NzctNy43Nzd6bSAwbDE1LjUgNy41bTAgMGwzIDNMMjIgN2wtMy0zbS0zLjUgMy41TDE5IDQiLz48L3N2Zz4=") !important;
    background-size: contain !important;
    background-repeat: no-repeat !important;
    flex: 0 0 auto !important;
}}

div[data-testid="stTextInput"] > div {{
    background: var(--input) !important;
    border: 1px solid var(--border) !important;
    border-radius: 0.85rem !important;
    transition: all 0.2s ease !important;
}}
div[data-testid="stTextInput"] > div:focus-within {{
    border-color: var(--ring) !important;
    box-shadow: 0 0 0 1px var(--ring) !important;
}}
div[data-testid="stTextInput"] > div div,
div[data-testid="stTextInput"] > div div:focus-within,
div[data-baseweb="input"],
div[data-baseweb="input"]:focus-within {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}
div[data-testid="stTextInput"] input,
div[data-baseweb="input"] input,
input {{
    background: transparent !important;
    color: var(--foreground) !important;
    border: none !important;
    box-shadow: none !important;
}}
div[data-testid="stTextInput"] label,
.stTextInput label {{
    color: var(--muted-foreground) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    margin-bottom: 0.35rem !important;
}}
div[data-testid="stTextInput"] button svg,
.stTextInput button svg {{ fill: #6b7280 !important; }}
div[data-testid="stTextInput"] button:hover svg,
.stTextInput button:hover svg {{ fill: var(--foreground) !important; }}

[role="tablist"] {{
    gap: 4px !important;
    background: var(--secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 9999px !important;
    padding: 0.25rem !important;
}}
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
    background: transparent !important;
    display: none !important;
    height: 0 !important;
    width: 0 !important;
    border: none !important;
    content: none !important;
}}
[role="tablist"] > div {{ background: transparent !important; }}
[role="tab"] {{
    color: var(--muted-foreground) !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0.65rem !important;
    flex: 1 !important;
    justify-content: center !important;
    transition: all 0.2s ease !important;
    padding: 0.55rem 1rem !important;
    height: auto !important;
}}
[role="tab"]:hover {{ background: color-mix(in oklab, var(--foreground) 4%, transparent) !important; }}
html body [data-testid="stApp"] [role="tablist"] button[aria-selected="true"],
html body [data-testid="stApp"] [role="tablist"] [role="tab"][aria-selected="true"],
html body [data-testid="stApp"] button[data-baseweb="tab"][aria-selected="true"] {{
    background: color-mix(in oklab, var(--foreground) 10%, transparent) !important;
    box-shadow: 0 0 0 1px var(--ring) !important;
    border-radius: 0.65rem !important;
}}
[role="tablist"] [role="tab"][aria-selected="true"] *,
[role="tab"] [aria-selected="true"] * {{
    color: var(--foreground) !important;
    font-weight: 600 !important;
}}

@media (max-width: 900px) {{
    .stApp {{ height: auto !important; overflow: auto !important; padding: 0 !important; }}
    div.block-container {{ height: auto !important; }}
    div[data-testid="stHorizontalBlock"] {{
        flex-direction: column !important;
        min-height: auto !important;
        height: auto !important;
        border-radius: 0 !important;
    }}
    div[data-testid="stHorizontalBlock"] > div:first-child,
    div[data-testid="stHorizontalBlock"] > div:last-child,
    .stColumn:first-child,
    .stColumn:last-child {{
        width: 100% !important;
        min-height: auto !important;
        height: auto !important;
        padding: 2rem 1.25rem !important;
    }}
    .st-key-auth_card {{ max-width: 100% !important; padding: 2rem 1.25rem 1.75rem !important; }}
}}
</style>
""",
    unsafe_allow_html=True,
)

logo_svg = """<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>"""

col_promo, col_form = st.columns([1.08, 0.92])

with col_promo:
    st.markdown(
        f"""
        <div class="promo-panel">
            <div>
                <div class="auth-logo">
                    <div class="auth-logo-icon">{logo_svg}</div>
                    <span class="auth-logo-text">CampaignCanvas</span>
                </div>
                <div class="promo-headline">Ship marketing insights, not spreadsheets.</div>
                <div class="promo-body">One workspace for ingestion, cleaning, KPIs, funnels, dashboards, alerts, and executive reports.</div>
            </div>
            <div class="promo-footer">© {datetime.now().year} CampaignCanvas</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_form:
    card = st.container(key="auth_card")
    with card:
        clean_theme_icon = theme_icon.strip()
        st.markdown(
            f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.25rem;"><div class="auth-title" style="margin-bottom:0 !important;">Welcome</div><a href="/auth?theme={next_theme}" target="_self" class="theme-toggle-link" title="Switch to {next_theme} mode">{clean_theme_icon}</a></div><p class="auth-subtitle">Sign in to your analytics workspace.</p>',
            unsafe_allow_html=True,
        )

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
                st.markdown(f'<a href="{auth_url}" target="_self" class="clerk-btn">Continue with Clerk</a>', unsafe_allow_html=True)
            else:
                if st.button("Continue with Clerk", use_container_width=True, key="clerk_setup_trigger_btn"):
                    st.session_state["show_clerk_setup"] = True

        if st.session_state.get("show_clerk_setup", False):
            st.markdown(
                """
                <div style="background: color-mix(in oklab, var(--destructive) 12%, transparent); border: 1px solid color-mix(in oklab, var(--destructive) 20%, transparent); border-radius: 0.85rem; padding: 1rem; margin-top: 1rem; margin-bottom: 1rem;">
                    <h4 style="color: var(--destructive); margin-top: 0; margin-bottom: 0.5rem; font-size: 0.95rem; font-weight: 700;">Clerk Auth Setup Required</h4>
                    <p style="color: var(--muted-foreground); font-size: 0.88rem; line-height: 1.5; margin: 0 0 0.75rem 0;">
                        Authentication credentials are not configured. To enable live login, configure your Clerk API keys in environment variables or Streamlit secrets.
                    </p>
                    <code style="background: color-mix(in oklab, var(--foreground) 5%, transparent); padding: 0.7rem 0.8rem; border-radius: 0.55rem; font-size: 0.78rem; color: var(--foreground); display: block; white-space: pre-wrap; border: 1px solid var(--border);">
CLERK_CLIENT_ID=your-client-id
CLERK_CLIENT_SECRET=your-client-secret
CLERK_DOMAIN=your-clerk-domain
CLERK_REDIRECT_URI=http://localhost:8501/
                    </code>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("Proceed with Mock Clerk Login", key="mock_clerk_login_btn", use_container_width=True):
                with st.spinner("Redirecting to Clerk mock login screen..."):
                    import time

                    time.sleep(1.0)
                st.session_state.logged_in = True
                st.session_state.email = "demo.clerk.user@gmail.com"
                st.session_state.name = "Demo Clerk User"
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
                        derived_name = " ".join(
                            [word.capitalize() for word in email.split("@")[0].replace(".", " ").replace("_", " ").split()]
                        )
                        st.session_state.name = derived_name
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
                        st.session_state.name = name
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

        st.markdown('<div class="back-home"><a href="/" target="_top">← Back to home</a></div>', unsafe_allow_html=True)
