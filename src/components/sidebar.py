from __future__ import annotations

import streamlit as st

# ---------- Icon set (Material Symbols) ----------
_MATERIAL_ICONS = {
    "dashboard": ":material/dashboard:",
    "upload": ":material/upload:",
    "profiling": ":material/search:",
    "cleaning": ":material/brush:",
    "database": ":material/database:",
    "analytics": ":material/trending_up:",
    "funnel": ":material/filter_alt:",
    "kpi_engine": ":material/speed:",
    "visualizations": ":material/bar_chart:",
    "sql_workspace": ":material/terminal:",
    "export_data": ":material/description:",
    "alerts": ":material/notifications:",
    "settings": ":material/settings:",
}

# ---------- Page Paths ----------
_PAGE_PATHS = {
    "dashboard": "pages/dashboard.py",
    "upload": "pages/upload.py",
    "profiling": "pages/profiling.py",
    "cleaning": "pages/cleaning.py",
    "database": "pages/database.py",
    "campaign_analysis": "pages/campaign_analysis.py",
    "activation_funnel": "pages/activation_funnel.py",
    "kpi_engine": "pages/kpi_engine.py",
    "visualizations": "pages/visualizations.py",
    "sql_workspace": "pages/sql_workspace.py",
    "reports": "pages/reports.py",
    "alerts": "pages/alerts.py",
    "settings": "pages/settings.py",
}

_SIDEBAR_CSS = """
<style>
section[data-testid="stSidebar"] {
    background: var(--sidebar) !important;
    border-right: 1px solid var(--sidebar-border);
}
.nav-section-label {
    padding: 0.8rem 0.75rem 0.45rem;
    font-size: 0.68rem;
    font-weight: 700;
    color: var(--muted-foreground);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* Remove default Streamlit background, border, and style from st.page_link in sidebar */
div[data-testid="stSidebar"] div[data-testid="stPageLink"] {
    background-color: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
}

div[data-testid="stSidebar"] div[data-testid="stPageLink"] a {
    display: flex !important;
    align-items: center !important;
    gap: 0.65rem !important;
    padding: 0.64rem 0.75rem !important;
    border-radius: 0.75rem !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    text-decoration: none !important;
    margin-bottom: 0.2rem !important;
    border: 1px solid transparent !important;
    background-color: transparent !important;
    background: transparent !important;
    color: var(--sidebar-foreground) !important;
    transition: background 0.15s ease, transform 0.15s ease, border-color 0.15s ease !important;
    width: 100% !important;
}

div[data-testid="stSidebar"] div[data-testid="stPageLink"] a:hover {
    background: var(--sidebar-accent) !important;
    color: var(--foreground) !important;
    transform: translateX(2px) !important;
}

/* Specific styling for the Active nav link */
div[class*="nav-link-active-container"] div[data-testid="stPageLink"] a {
    background: linear-gradient(135deg, rgba(56,189,248,0.18), rgba(129,140,248,0.12)) !important;
    border: 1px solid rgba(56,189,248,0.24) !important;
    color: var(--foreground) !important;
    font-weight: 600 !important;
}

/* Ensure no extra padding/margins on container wrapper elements */
div[class*="nav-link-container"], div[class*="nav-link-active-container"] {
    padding: 0 !important;
    margin: 0 !important;
}

/* Ensure text and icons inherit colors properly */
div[data-testid="stSidebar"] div[data-testid="stPageLink"] a * {
    color: inherit !important;
}

/* Align and style the material symbols icon inside the page link */
div[data-testid="stSidebar"] div[data-testid="stPageLink"] a span[data-testid="stIconMaterial"] {
    color: inherit !important;
    font-size: 1.1rem !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    opacity: 0.9 !important;
}
</style>
"""


def _render_nav_link(label: str, icon_key: str, href: str, page_key: str, current_page: str) -> None:
    page_path = _PAGE_PATHS.get(page_key)
    if not page_path:
        return

    icon = _MATERIAL_ICONS.get(icon_key, ":material/link:")

    # Wrap in active or inactive container class
    is_active = (current_page == page_key)
    container_class = "nav-link-active-container" if is_active else "nav-link-container"

    with st.container(key=f"{container_class}_{page_key}"):
        st.page_link(page_path, label=label, icon=icon)


def render_sidebar(current_page: str):
    """
    Render the CampaignCanvas sidebar.

    Args:
        current_page: The name of the current active page to highlight
    """
    with st.sidebar:
        st.markdown(_SIDEBAR_CSS, unsafe_allow_html=True)

        # Logo at top
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem; padding: 0.15rem 0;">
                <div style="width: 36px; height: 36px; border-radius: 0.9rem; background: linear-gradient(135deg, #38bdf8, #0f172a); border: 1px solid var(--sidebar-border); display: grid; place-items: center; box-shadow: 0 16px 30px -20px rgba(56,189,248,0.6);">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                </div>
                <span style="font-family: var(--font-display); font-size: 1.125rem; font-weight: 700; color: var(--sidebar-foreground); letter-spacing: -0.02em;">CampaignCanvas</span>
            </div>
        """, unsafe_allow_html=True)

        # Overview Section
        st.markdown('<div class="nav-section-label">Overview</div>', unsafe_allow_html=True)
        _render_nav_link("Dashboard", "dashboard", "/dashboard", "dashboard", current_page)

        # Data Section
        st.markdown('<div class="nav-section-label">Data</div>', unsafe_allow_html=True)
        _render_nav_link("Upload", "upload", "/export_data", "upload", current_page)
        _render_nav_link("Profiling", "profiling", "/export_data", "profiling", current_page)
        _render_nav_link("Cleaning", "cleaning", "/export_data", "cleaning", current_page)
        _render_nav_link("Database", "database", "/export_data", "database", current_page)

        # Insights Section
        st.markdown('<div class="nav-section-label">Insights</div>', unsafe_allow_html=True)
        _render_nav_link("Analytics", "analytics", "/campaign_analysis", "campaign_analysis", current_page)
        _render_nav_link("Funnel", "funnel", "/activation_funnel", "activation_funnel", current_page)
        _render_nav_link("KPI Engine", "kpi_engine", "/kpi_engine", "kpi_engine", current_page)
        _render_nav_link("Visualizations", "visualizations", "/visualizations", "visualizations", current_page)
        _render_nav_link("SQL Workspace", "sql_workspace", "/sql_workspace", "sql_workspace", current_page)

        # Actions Section
        st.markdown('<div class="nav-section-label" style="margin-top: 0.5rem; border-top: 1px solid var(--sidebar-border); padding-top: 1rem;">Actions</div>', unsafe_allow_html=True)
        _render_nav_link("Reports", "export_data", "/reports", "reports", current_page)
        _render_nav_link("Alerts", "alerts", "/alerts", "alerts", current_page)
        _render_nav_link("Settings", "settings", "/settings", "settings", current_page)

        st.markdown(
            '<div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--sidebar-border);"></div>',
            unsafe_allow_html=True,
        )

        # Sign Out Button
        if st.button("Sign out", key="sign_out_btn", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.email = ""
            st.switch_page("app.py")
        st.markdown("</div>", unsafe_allow_html=True)