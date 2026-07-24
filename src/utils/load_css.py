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
          --background: #f8fafc !important;
          --foreground: #0f172a !important;
          --card: #ffffff !important;
          --card-foreground: #0f172a !important;
          --popover: #ffffff !important;
          --popover-foreground: #0f172a !important;
          --primary: #2563eb !important;
          --primary-foreground: #ffffff !important;
          --primary-glow: #38bdf8 !important;
          --secondary: #f1f5f9 !important;
          --secondary-foreground: #334155 !important;
          --muted: #e2e8f0 !important;
          --muted-foreground: #64748b !important;
          --accent: #e2e8f0 !important;
          --accent-foreground: #0f172a !important;
          --destructive: #ef4444 !important;
          --destructive-foreground: #ffffff !important;
          --success: #22c55e !important;
          --success-foreground: #ffffff !important;
          --warning: #eab308 !important;
          --warning-foreground: #0f172a !important;
          --border: #cbd5e1 !important;
          --input: #ffffff !important;
          --ring: #2563eb !important;
          --sidebar: #f1f5f9 !important;
          --sidebar-foreground: #334155 !important;
          --sidebar-accent: #e2e8f0 !important;
          --sidebar-border: #cbd5e1 !important;
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

        /* Streamlit st.container(border=True) & Custom Card Light Mode Styling */
        .stApp [data-testid="stVerticalBlockBorderWrapper"],
        .stApp div[data-testid="stVerticalBlockBorderWrapper"],
        .stApp div[data-testid="stVerticalBlockBorderWrapper"] > div,
        .stApp [data-testid="stContainer"],
        .stApp .glass-card,
        .stApp .dashboard-stat-card,
        .stApp .campaign-card {
            background-color: #ffffff !important;
            background-image: none !important;
            border: 1.5px solid #cbd5e1 !important;
            border-radius: 0.875rem !important;
            box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.08), 0 2px 6px -1px rgba(15, 23, 42, 0.04) !important;
        }
        .stApp [data-testid="stVerticalBlockBorderWrapper"]:hover,
        .stApp div[data-testid="stVerticalBlockBorderWrapper"]:hover,
        .stApp .glass-card:hover,
        .stApp .dashboard-stat-card:hover,
        .stApp .campaign-card:hover {
            border-color: #64748b !important;
            box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.14) !important;
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
        
        /* Toggle outer area */
        div[data-testid="stToggle"] {
            opacity: 1 !important;
            visibility: visible !important;
        }
        
        /* OFF toggle track */
        div[data-testid="stToggle"] [role="switch"] {
            background: #94a3b8 !important;
            background-color: #94a3b8 !important;
            border: 1px solid #64748b !important;
            opacity: 1 !important;
            visibility: visible !important;
        }
        
        /* ON toggle track */
        div[data-testid="stToggle"] [role="switch"][aria-checked="true"] {
            background: #38bdf8 !important;
            background-color: #38bdf8 !important;
            border-color: #0284c7 !important;
            opacity: 1 !important;
        }
        
        /* Toggle knob */
        div[data-testid="stToggle"] [role="switch"] > div {
            background: #ffffff !important;
            background-color: #ffffff !important;
            opacity: 1 !important;
            visibility: visible !important;
        }

        section[data-testid="stSidebar"] {
            background-color: var(--sidebar) !important;
        }
        section[data-testid="stSidebar"] * {
            color: var(--sidebar-foreground) !important;
        }
        div[data-testid="stSidebar"] div[data-testid="stPageLink"] a:hover {
            background: var(--sidebar-accent) !important;
            color: var(--foreground) !important;
        }

        /* Streamlit download and standard button styling in Light Theme */
        .stButton button,
        div[data-testid="stFormSubmitButton"] button,
        div[data-testid="stDownloadButton"] button,
        div[data-testid="stDownloadButton"] a,
        .stDownloadButton button,
        .stDownloadButton a,
        [data-testid="stBaseButton-secondary"],
        [data-testid="stElementContainer"] [data-testid="stDownloadButton"] button,
        [data-testid="stElementContainer"] [data-testid="stDownloadButton"] a {
            background-color: #f1f5f9 !important;
            background-image: none !important;
            color: #334155 !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 0.5rem !important;
        }
        .stButton button *,
        div[data-testid="stFormSubmitButton"] button *,
        div[data-testid="stDownloadButton"] button *,
        div[data-testid="stDownloadButton"] a *,
        .stDownloadButton button *,
        .stDownloadButton a *,
        [data-testid="stBaseButton-secondary"] *,
        [data-testid="stElementContainer"] [data-testid="stDownloadButton"] * {
            color: #334155 !important;
        }

        /* Streamlit Primary Button styling in Light Theme (e.g. Run query, Submit, Upload data) */
        [data-testid="stBaseButton-primary"],
        button[kind="primary"],
        .stButton button[kind="primary"],
        div[data-testid="stFormSubmitButton"] button[kind="primary"],
        .stMain div[data-testid="stPageLink"] a,
        [data-testid="stMain"] div[data-testid="stPageLink"] a {
            background-color: #0284c7 !important;
            background-image: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            border: none !important;
            border-radius: 0.5rem !important;
        }
        [data-testid="stBaseButton-primary"] *,
        button[kind="primary"] *,
        .stButton button[kind="primary"] *,
        div[data-testid="stFormSubmitButton"] button[kind="primary"] *,
        .stMain div[data-testid="stPageLink"] a *,
        .stMain div[data-testid="stPageLink"] a p,
        .stMain div[data-testid="stPageLink"] a span,
        [data-testid="stMain"] div[data-testid="stPageLink"] a *,
        [data-testid="stMain"] div[data-testid="stPageLink"] a p,
        [data-testid="stMain"] div[data-testid="stPageLink"] a span {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }

        /* Plotly background & text color overrides */
        div.js-plotly-plot .main-svg {
            background: transparent !important;
        }
        .stApp .js-plotly-plot text,
        .stApp .js-plotly-plot .xtick text,
        .stApp .js-plotly-plot .ytick text,
        .stApp .js-plotly-plot .legendtext,
        .stApp .js-plotly-plot .gtitle,
        .stApp .js-plotly-plot .xtitle,
        .stApp .js-plotly-plot .ytitle,
        .stApp .js-plotly-plot .annotation-text,
        .stApp .js-plotly-plot .funnel-label,
        .stApp .js-plotly-plot .pielabel-text {
            fill: #0f172a !important;
            color: #0f172a !important;
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

        /* ── Input and Textarea contrast overrides in Light Mode ── */
        .stApp .stTextArea,
        .stApp .stTextArea *,
        .stApp div[data-testid="stTextArea"],
        .stApp div[data-testid="stTextArea"] *,
        .stApp div[data-baseweb="textarea"],
        .stApp div[data-baseweb="textarea"] *,
        .stApp div[data-baseweb="base-input"],
        .stApp div[data-baseweb="base-input"] *,
        .stApp textarea,
        .stApp .stTextInput input,
        .stApp .stTextInput > div,
        .stApp .stTextInput > div > div,
        .stApp div[data-testid="stTextInput"],
        .stApp div[data-testid="stTextInput"] *,
        .stApp div[data-baseweb="input"],
        .stApp div[data-baseweb="input"] * {
            background-color: #ffffff !important;
            background: #ffffff !important;
            color: #0f172a !important;
            -webkit-text-fill-color: #0f172a !important;
            border-color: #cbd5e1 !important;
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

/* Extra accessibility fix for Light Mode selectboxes, textinputs, textareas, metrics, and labels */
.stSelectbox div[data-baseweb="select"] *,
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
div[data-testid="stTextArea"] textarea,
div[data-baseweb="textarea"] textarea,
div[data-testid="stMetricValue"] {
    color: var(--foreground) !important;
    -webkit-text-fill-color: var(--foreground) !important;
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
.stTable,
.custom-data-table,
.performance-table {
    width: 100% !important;
    border-collapse: collapse !important;
    color: var(--foreground) !important;
    background-color: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    overflow: hidden !important;
}
.stTable th,
.stTable td,
.custom-data-table th,
.custom-data-table td,
.performance-table th,
.performance-table td {
    border: 1px solid var(--border) !important;
    padding: 0.75rem 1rem !important;
    color: var(--foreground) !important;
    text-align: left !important;
}
.stTable th,
.custom-data-table th,
.performance-table th {
    background-color: var(--secondary) !important;
    color: var(--foreground) !important;
    font-weight: 600 !important;
}
.stTable td,
.custom-data-table td,
.performance-table td {
    background-color: var(--card) !important;
}
.stTable tr:hover,
.custom-data-table tr:hover,
.performance-table tr:hover {
    background-color: color-mix(in oklab, var(--accent) 18%, transparent) !important;
}
/* Hide index column in Streamlit st.table only if marked blank */
.stTable th.blank,
.stTable td.blank {
    display: none !important;
}

.performance-table-wrapper {
    width: 100% !important;
    overflow-x: auto !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    background: var(--card) !important;
}

.performance-table-wrapper table {
    margin: 0 !important;
    border: none !important;
}

.performance-table-wrapper td,
.performance-table-wrapper th {
    border-color: var(--border) !important;
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
    text_color = "#0f172a" if theme == "light" else "#f8fafc"
    grid_color = "rgba(15, 23, 42, 0.08)" if theme == "light" else "rgba(255,255,255,0.08)"
    
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
