from __future__ import annotations

import logging
import os
import requests
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

# Configure module logger
logger = logging.getLogger(__name__)

# Load environment variables from .env if present
load_dotenv(override=False)


def is_production_environment() -> bool:
    """Checks whether the application is running in a strict production environment."""
    env = (
        os.getenv("ENVIRONMENT")
        or os.getenv("APP_ENV")
        or os.getenv("STREAMLIT_ENV")
        or "development"
    ).lower()
    return env in ("production", "prod")


def initialize_auth_state(session_state=None):
    """Populate auth state with safe defaults so pages do not rely on None/undefined values."""
    if session_state is None:
        session_state = st.session_state

    if "logged_in" not in session_state:
        session_state["logged_in"] = False
    if "email" not in session_state:
        session_state["email"] = ""
    if "name" not in session_state:
        session_state["name"] = ""
    if "theme" not in session_state:
        session_state["theme"] = "dark"

    return session_state


def require_authentication(redirect_page: str = "pages/auth.py") -> bool:
    """Ensure the user is authenticated before rendering protected pages."""
    initialize_auth_state()
    check_and_restore_session()
    if st.session_state.get("logged_in", False):
        return True

    try:
        st.switch_page(redirect_page)
    except Exception:
        st.rerun()
    return False


def get_clerk_credentials():
    """Resolves Clerk credentials from Streamlit secrets or environment variables."""
    load_dotenv(override=False)
    client_id = None
    client_secret = None
    domain = None
    redirect_uri = None

    # 1. Try Streamlit Secrets first
    try:
        if "clerk" in st.secrets:
            client_id = st.secrets["clerk"].get("client_id")
            client_secret = st.secrets["clerk"].get("client_secret")
            domain = st.secrets["clerk"].get("domain")
            redirect_uri = st.secrets["clerk"].get("redirect_uri")
    except Exception:
        # st.secrets throws StreamlitSecretNotFoundError if secrets.toml is missing
        pass

    # 2. Fallback to Environment Variables
    if not client_id:
        client_id = os.getenv("CLERK_CLIENT_ID") or os.getenv("CLERK_PUBLISHABLE_KEY")
    if not client_secret:
        client_secret = os.getenv("CLERK_CLIENT_SECRET") or os.getenv("CLERK_SECRET_KEY")
    if not domain:
        domain = os.getenv("CLERK_DOMAIN")
    if not redirect_uri:
        redirect_uri = os.getenv("CLERK_REDIRECT_URI")

    # Clean domain if it includes protocol
    if domain:
        domain = domain.replace("https://", "").replace("http://", "").strip("/")

    # Check if running on Render platform where RENDER_EXTERNAL_URL is available
    render_url = os.getenv("RENDER_EXTERNAL_URL")
    if render_url:
        render_redirect = render_url.rstrip("/") + "/"
        if not redirect_uri or "localhost" in redirect_uri:
            redirect_uri = render_redirect

    # Default redirect URI to local dev if not configured
    if not redirect_uri:
        redirect_uri = "http://localhost:8501/"

    return client_id, client_secret, domain, redirect_uri


def initialize_auth() -> bool:
    """Environment-aware authentication initializer.
    
    Guards authentication fallbacks based on environment configuration to prevent
    unauthorized bypasses in production environments.
    """
    initialize_auth_state()
    client_id, client_secret, domain, _ = get_clerk_credentials()
    in_prod = is_production_environment()

    # Verify critical credentials in production
    if not (client_id and client_secret and domain):
        if in_prod:
            st.error(
                "🚨 Critical Authentication Error: Clerk credentials (CLERK_CLIENT_ID, "
                "CLERK_CLIENT_SECRET, CLERK_DOMAIN) are missing in production deployment."
            )
            logger.critical("Production auth initialization failed: Missing Clerk credentials.")
            st.stop()
        else:
            st.warning(
                "⚠️ Clerk credentials not configured. Running in Local Development / Demo Auth Mode."
            )
            return False

    return True


@st.cache_data(ttl=3600, show_spinner=False)
def get_clerk_endpoints(domain: str):
    """Queries Clerk's well-known OpenID configuration endpoint to resolve standard OIDC endpoints.
    
    Results are cached for 1 hour to prevent HTTP roundtrips on every Streamlit rerun.
    """
    default_endpoints = {
        "authorization_endpoint": f"https://{domain}/oauth/authorize",
        "token_endpoint": f"https://{domain}/oauth/token",
        "userinfo_endpoint": f"https://{domain}/oauth/userinfo",
    }

    if not domain:
        return default_endpoints

    config_url = f"https://{domain}/.well-known/openid-configuration"
    try:
        response = requests.get(config_url, timeout=5)
        if response.status_code == 200:
            config = response.json()
            return {
                "authorization_endpoint": config.get(
                    "authorization_endpoint", default_endpoints["authorization_endpoint"]
                ),
                "token_endpoint": config.get(
                    "token_endpoint", default_endpoints["token_endpoint"]
                ),
                "userinfo_endpoint": config.get(
                    "userinfo_endpoint", default_endpoints["userinfo_endpoint"]
                ),
            }
    except Exception as err:
        logger.warning("Could not reach Clerk OpenID configuration endpoint: %s", err)

    return default_endpoints


def safe_switch_page(page_path: str):
    """Safely switches page in Streamlit trying both 'pages/...' and 'src/pages/...' paths."""
    try:
        st.switch_page(page_path)
    except Exception:
        alt_path = (
            f"src/{page_path}"
            if not page_path.startswith("src/")
            else page_path.replace("src/", "", 1)
        )
        try:
            st.switch_page(alt_path)
        except Exception:
            st.rerun()


def handle_clerk_callback():
    """Checks for a Clerk authentication redirect code in query params.
    
    Exchanges it for user info, establishes the session, and redirects to the dashboard.
    """
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]

        client_id, client_secret, domain, redirect_uri = get_clerk_credentials()

        if client_id and client_secret and domain:
            endpoints = get_clerk_endpoints(domain)

            with st.spinner("Completing Clerk Authentication..."):
                try:
                    # Exchange authorization code for token
                    token_url = endpoints["token_endpoint"]
                    token_data = {
                        "code": code,
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "redirect_uri": redirect_uri,
                        "grant_type": "authorization_code",
                    }
                    res = requests.post(token_url, data=token_data, timeout=10)
                    if res.status_code == 200:
                        tokens = res.json()
                        access_token = tokens.get("access_token")

                        # Get user info
                        userinfo_url = endpoints["userinfo_endpoint"]
                        headers = {"Authorization": f"Bearer {access_token}"}
                        userinfo_res = requests.get(userinfo_url, headers=headers, timeout=10)

                        if userinfo_res.status_code == 200:
                            user_data = userinfo_res.json()
                            email = user_data.get("email") or user_data.get("email_address")

                            # Sometimes OIDC payload returns email as first item in list or nested
                            if not email and "emails" in user_data and len(user_data["emails"]) > 0:
                                email = user_data["emails"][0]

                            if email:
                                name = (
                                    user_data.get("name")
                                    or f"{user_data.get('given_name', '')} {user_data.get('family_name', '')}".strip()
                                )
                                if not name:
                                    name = " ".join(
                                        [
                                            word.capitalize()
                                            for word in email.split("@")[0]
                                            .replace(".", " ")
                                            .replace("_", " ")
                                            .split()
                                        ]
                                    )
                                st.session_state.logged_in = True
                                st.session_state.email = email
                                st.session_state.name = name
                                st.session_state.clerk_user = user_data
                                if "explicitly_logged_out" in st.session_state:
                                    del st.session_state["explicitly_logged_out"]

                                try:
                                    st.query_params.clear()
                                except Exception:
                                    pass

                                st.success("Signed in successfully with Clerk!")
                                safe_switch_page("pages/dashboard.py")
                                return
                            else:
                                st.error("No email address returned from your Clerk profile.")
                        else:
                            st.error(f"Failed to fetch Clerk profile details: {userinfo_res.text}")
                    else:
                        st.error(f"Clerk token exchange failed: {res.text}")
                except Exception as e:
                    logger.exception("Error during Clerk OAuth callback")
                    st.error(f"An error occurred during Clerk authentication callback: {e}")
        else:
            if is_production_environment():
                st.error("Authentication failed: Unconfigured Clerk environment in production.")
            else:
                st.warning("Clerk credentials are not configured. Callback code was ignored.")


def check_and_restore_session():
    """Checks for authentication cookies and restores or updates session state/cookies accordingly.
    
    Call this at the beginning of each page rendering to persist authentication.
    """
    # 1. Restore session from cookies if session state logged_in is not True
    if not st.session_state.get("logged_in") and not st.session_state.get("explicitly_logged_out"):
        try:
            cookies = st.context.cookies
            if cookies.get("logged_in") == "true":
                st.session_state.logged_in = True
                email = cookies.get("email", "")
                st.session_state.email = email

                name_cookie = cookies.get("name", "")
                if name_cookie:
                    st.session_state.name = name_cookie
                else:
                    st.session_state.name = " ".join(
                        [
                            w.capitalize()
                            for w in email.split("@")[0]
                            .replace(".", " ")
                            .replace("_", " ")
                            .split()
                        ]
                    )
        except Exception:
            pass

    # 2. If logged in in session state, make sure cookies are set
    if st.session_state.get("logged_in") is True:
        if "cookie_cleared" in st.session_state:
            del st.session_state["cookie_cleared"]
        try:
            cookies = st.context.cookies
            if cookies.get("logged_in") != "true" and not st.session_state.get("cookie_written"):
                email = st.session_state.get("email", "")
                name = st.session_state.get("name", "")
                components.html(
                    f"""
                    <script>
                        parent.document.cookie = "logged_in=true; path=/; max-age=86400; SameSite=Lax";
                        parent.document.cookie = "email={email}; path=/; max-age=86400; SameSite=Lax";
                        parent.document.cookie = "name={name}; path=/; max-age=86400; SameSite=Lax";
                    </script>
                    """,
                    height=0,
                    width=0,
                )
                st.session_state["cookie_written"] = True
        except Exception:
            pass

    # 3. If explicitly logged out, ensure cookies are cleared
    elif st.session_state.get("explicitly_logged_out") is True:
        try:
            cookies = st.context.cookies
            if cookies.get("logged_in") == "true" and not st.session_state.get("cookie_cleared"):
                components.html(
                    """
                    <script>
                        parent.document.cookie = "logged_in=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;";
                        parent.document.cookie = "email=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;";
                        parent.document.cookie = "name=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;";
                    </script>
                    """,
                    height=0,
                    width=0,
                )
                st.session_state["cookie_cleared"] = True
                if "cookie_written" in st.session_state:
                    del st.session_state["cookie_written"]
        except Exception:
            pass