from pathlib import Path
import streamlit as st

# src/utils/load_css.py -> parents[1] = src/  -> assets/styles/style.css
_STYLE_PATH = Path(__file__).resolve().parents[1] / "assets" / "styles" / "style.css"


def load_css(path: Path = _STYLE_PATH) -> None:
    """Inject the shared CampaignCanvas stylesheet into the current page.

    Call this once near the top of every page script (app.py and each
    file in src/pages/), or once inside a shared layout component
    (e.g. navbar.py / sidebar.py) that every page already imports —
    Streamlit re-runs the whole script per page, so CSS injected in
    app.py alone will NOT carry over to src/pages/*.py.
    """
    # Sync theme state from query parameters if provided
    theme_param = st.query_params.get("theme")
    if theme_param in ["light", "dark"]:
        st.session_state["theme"] = theme_param

    # Fallback to cookies if session state is not set
    if "theme" not in st.session_state:
        try:
            cookies = st.context.cookies
            cookie_theme = cookies.get("theme")
            if cookie_theme in ["light", "dark"]:
                st.session_state["theme"] = cookie_theme
        except Exception:
            pass

    # Default to dark mode if not set
    theme = st.session_state.get("theme", "dark")

    try:
        css = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        st.warning(f"Stylesheet not found at {path} — using default Streamlit theme.")
        return

    # In light theme, inject root variable overrides
    theme_variables = ""
    if theme == "light":
        theme_variables = """
        :root, body, .stApp, [data-testid="stAppViewContainer"] {
          --background: oklch(0.98 0.005 240) !important;
          --foreground: oklch(0.12 0.02 240) !important;
          --card: oklch(1 0 0) !important;
          --card-foreground: oklch(0.12 0.02 240) !important;
          --popover: oklch(1 0 0) !important;
          --popover-foreground: oklch(0.12 0.02 240) !important;
          --primary: oklch(0.6 0.18 250) !important;
          --primary-foreground: oklch(0.99 0 0) !important;
          --primary-glow: oklch(0.7 0.14 220) !important;
          --secondary: oklch(0.95 0.01 240) !important;
          --secondary-foreground: oklch(0.25 0.02 240) !important;
          --muted: oklch(0.92 0.01 240) !important;
          --muted-foreground: oklch(0.45 0.02 240) !important;
          --accent: oklch(0.92 0.02 240) !important;
          --accent-foreground: oklch(0.12 0.02 240) !important;
          --destructive: oklch(0.6 0.18 29) !important;
          --destructive-foreground: oklch(0.99 0 0) !important;
          --success: oklch(0.65 0.18 150) !important;
          --success-foreground: oklch(0.99 0 0) !important;
          --warning: oklch(0.75 0.18 70) !important;
          --warning-foreground: oklch(0.12 0.02 240) !important;
          --border: oklch(0.89 0.01 240) !important;
          --input: oklch(1 0 0) !important;
          --ring: oklch(0.6 0.18 250) !important;
          --sidebar: oklch(0.96 0.01 240) !important;
          --sidebar-foreground: oklch(0.25 0.02 240) !important;
          --sidebar-accent: oklch(0.9 0.015 240) !important;
          --sidebar-border: oklch(0.89 0.01 240) !important;
          --shadow-glow: 0 12px 30px -10px rgba(56, 189, 248, 0.2) !important;
          --shadow-card: 0 1px 3px rgba(15, 23, 42, 0.08), 0 4px 12px -4px rgba(2, 6, 23, 0.05) !important;
          
          /* Map to Streamlit native theme properties */
          --background-color: var(--background) !important;
          --text-color: var(--foreground) !important;
          --secondary-background-color: var(--secondary) !important;
          --primary-color: var(--primary) !important;
        }

        /* Force dark text color for common containers in light theme */
        .stApp [data-testid="stMarkdownContainer"] p,
        .stApp [data-testid="stMarkdownContainer"] span,
        .stApp [data-testid="stWidgetLabel"] p,
        .stApp label,
        .stApp .stCaptionContainer,
        .stApp span[data-testid="stHeaderActionElements"] a {
            color: var(--foreground) !important;
        }

        /* Adjustments for custom dashboard HTML components in Light Theme */
        h1, h2, h3, h4, span, p, div {
            color: inherit;
        }
        
        .logo-text {
            color: var(--foreground) !important;
        }
        .hero-title {
            color: var(--foreground) !important;
        }
        .hero-badge {
            background: rgba(148, 163, 184, 0.08) !important;
            border-color: rgba(148, 163, 184, 0.15) !important;
            color: var(--foreground) !important;
        }
        .hero-desc {
            color: var(--muted-foreground) !important;
        }
        .card-title {
            color: var(--foreground) !important;
        }
        .card-desc {
            color: var(--muted-foreground) !important;
        }

        /* Streamlit widget light overrides */
        div[data-testid="stMetricValue"] {
            color: var(--foreground) !important;
        }
        div[data-testid="stMetricLabel"] {
            color: var(--muted-foreground) !important;
        }
        .stTabs button[data-baseweb="tab"] {
            color: var(--muted-foreground) !important;
        }
        .stTabs button[aria-selected="true"] {
            background-color: var(--accent) !important;
            color: var(--accent-foreground) !important;
        }
        section[data-testid="stSidebar"] {
            background-color: var(--sidebar) !important;
        }
        section[data-testid="stSidebar"] * {
            color: var(--sidebar-foreground) !important;
        }
        div[data-testid="stSidebar"] div[data-testid="stPageLink"] a {
            color: var(--sidebar-foreground) !important;
        }
        div[data-testid="stSidebar"] div[data-testid="stPageLink"] a:hover {
            background: var(--sidebar-accent) !important;
            color: var(--foreground) !important;
        }
        /* Plotly background */
        div.js-plotly-plot .main-svg {
            background: transparent !important;
        }

        /* ── File uploader: override dark baseweb styles in Light Mode ── */
        [data-testid="stFileUploader"] section,
        [data-testid="stFileUploaderDropzone"] {
            background-color: #f8fafc !important;
            border: 1.5px dashed #94a3b8 !important;
            color: #1e293b !important;
        }
        [data-testid="stFileUploader"] button,
        [data-testid="stFileUploader"] [role="button"],
        [data-testid="stFileUploader"] button[kind="secondary"],
        [data-testid="stFileUploader"] [data-baseweb="button"] {
            background-color: #e2e8f0 !important;
            color: #1e293b !important;
            border: 1px solid #cbd5e1 !important;
        }
        [data-testid="stFileUploader"] button:hover,
        [data-testid="stFileUploader"] [data-baseweb="button"]:hover {
            background-color: #cbd5e1 !important;
        }
        [data-testid="stFileUploader"] span,
        [data-testid="stFileUploader"] p,
        [data-testid="stFileUploader"] small {
            color: #64748b !important;
        }
        """

    # Global CSS overrides (no style tags)
    extra_overrides = """
/* Override all hardcoded white/light text colors in inline styles to use dynamic foreground variable */
[style*="color: white"],
[style*="color:white"],
[style*="color: rgba(255, 255, 255"],
[style*="color:rgba(255,255,255"],
[style*="color: rgb(255, 255, 255"],
[style*="color:rgb(255,255,255"],
[style*="color:#fff"],
[style*="color: #fff"],
[style*="color:#ffffff"],
[style*="color: #ffffff"],
[style*="color: #f5f8fb"],
[style*="color:#f5f8fb"],
[style*="color: rgb(245, 248, 251"],
[style*="color:rgb(245,248,251"],
[style*="color: rgb(245, 248, 253"],
[style*="color:rgb(245,248,253"],
[style*="color: rgba(245, 248, 251"],
[style*="color:rgba(245,248,251"],
[style*="color: #e2e8f0"],
[style*="color:#e2e8f0"],
[style*="color: rgb(226, 232, 240"],
[style*="color:rgb(226,232,240"] {
    color: var(--foreground) !important;
}

/* Extra accessibility fix for Light Mode selectboxes, textinputs, metrics, and labels */
.stSelectbox div[data-baseweb="select"] *,
.stTextInput input,
.stNumberInput input,
div[data-testid="stMetricValue"] {
    color: var(--foreground) !important;
}

/* Streamlit widget labels styling */
label[data-testid="stWidgetLabel"],
.stWidgetLabel *,
div[data-testid="stWidgetLabel"] {
    color: var(--foreground) !important;
}

/* Streamlit captions and muted text in Light Theme */
div[data-testid="stCaptionContainer"],
.stCaptionContainer,
div[data-testid="stCaptionContainer"] *,
span[data-testid="stCaptionContainer"],
.stMarkdown div[data-testid="stMarkdownContainer"] p {
    color: var(--foreground) !important;
}

/* Disabled input fields text accessibility fix in Light Mode */
div[data-testid="stTextInput"] input:disabled,
div[data-baseweb="input"] input:disabled,
.stTextInput input:disabled,
input:disabled,
[disabled] {
    color: var(--muted-foreground) !important;
    -webkit-text-fill-color: var(--muted-foreground) !important;
    opacity: 0.85 !important;
}

/* HTML Table overrides for beautiful dynamic theme support in st.table */
.stTable {
    width: 100% !important;
    border-collapse: collapse !important;
    color: var(--foreground) !important;
    background-color: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
}
.stTable th {
    background-color: var(--secondary) !important;
    color: var(--foreground) !important;
    font-weight: 600 !important;
    text-align: left !important;
    padding: 0.75rem 1rem !important;
    border-bottom: 2px solid var(--border) !important;
}
.stTable td {
    padding: 0.75rem 1rem !important;
    border-bottom: 1px solid var(--border) !important;
    color: var(--foreground) !important;
}
.stTable tr:hover {
    background-color: var(--accent) !important;
}
/* Hide index column in Streamlit st.table */
.stTable tbody tr th:first-child,
.stTable thead tr th:first-child {
    display: none !important;
}

/* Custom data tables (used in Upload history etc.) — do NOT hide any columns */
.custom-data-table {
    width: 100% !important;
    border-collapse: collapse !important;
    color: var(--foreground) !important;
    background-color: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
}
.custom-data-table th {
    background-color: var(--secondary) !important;
    color: var(--foreground) !important;
    font-weight: 600 !important;
    text-align: left !important;
    padding: 0.75rem 1rem !important;
    border-bottom: 2px solid var(--border) !important;
}
.custom-data-table td {
    padding: 0.75rem 1rem !important;
    border-bottom: 1px solid var(--border) !important;
    color: var(--foreground) !important;
}
.custom-data-table tr:hover {
    background-color: var(--accent) !important;
}
"""

    import textwrap
    theme_variables = textwrap.dedent(theme_variables).strip()
    extra_overrides = textwrap.dedent(extra_overrides).strip()

    # Combine everything inside a single style block to avoid markdown rendering bugs
    combined_css = f"{theme_variables}\n{css}\n{extra_overrides}"
    st.markdown(f"<style>{combined_css}</style>", unsafe_allow_html=True)
    
# Initialize and restore authentication state via cookies
    from src.utils.clerk_auth import check_and_restore_session
    check_and_restore_session()

    # Make sure browser theme cookie is set correctly to prevent theme reset on page redirects
    try:
        cookies = st.context.cookies
        if cookies.get("theme") != theme:
            import streamlit.components.v1 as components
            components.html(
                f"""
                <script>
                    parent.document.cookie = "theme={theme}; path=/; max-age=31536000; SameSite=Lax";
                </script>
                """,
                height=0,
                width=0,
            )
    except Exception:
        pass


def get_plotly_layout() -> dict:
    """Get the plotly layout dict styled dynamically for the active theme."""
    theme = st.session_state.get("theme", "dark")
    text_color = "#1e293b" if theme == "light" else "#e2e8f0"
    grid_color = "rgba(15, 23, 42, 0.06)" if theme == "light" else "rgba(255,255,255,0.06)"
    
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, sans-serif", "color": text_color, "size": 11},
        "margin": {"t": 40, "b": 40, "l": 40, "r": 40},
        "xaxis": {
            "gridcolor": grid_color,
            "zeroline": False,
            "showline": False,
            "tickfont": {"color": text_color},
            "title": {"font": {"color": text_color}},
        },
        "yaxis": {
            "gridcolor": grid_color,
            "zeroline": False,
            "showline": False,
            "tickfont": {"color": text_color},
            "title": {"font": {"color": text_color}},
        },
        "legend": {
            "font": {"color": text_color}
        }
    }
