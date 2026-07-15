from __future__ import annotations

import streamlit as st

# ---------- Icon set (lucide-style, monochrome, currentColor) ----------
_ICONS = {
    "dashboard": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9"></rect><rect x="14" y="3" width="7" height="5"></rect><rect x="14" y="12" width="7" height="9"></rect><rect x="3" y="16" width="7" height="5"></rect></svg>',
    "upload": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>',
    "profiling": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>',
    "cleaning": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275Z"></path></svg>',
    "database": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5V19A9 3 0 0 0 21 19V5"></path><path d="M3 12A9 3 0 0 0 21 12"></path></svg>',
    "analytics": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="m19 9-5 5-4-4-3 3"></path></svg>',
    "funnel": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon></svg>',
    "kpi_engine": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 14 4-4"></path><path d="M3.34 19a10 10 0 1 1 17.32 0"></path></svg>',
    "visualizations": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>',
    "sql_workspace": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>',
    "export_data": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>',
    "alerts": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path></svg>',
}

_SIDEBAR_CSS = """
<style>
section[data-testid="stSidebar"] {
    background: #0b1220;
    border-right: 1px solid rgba(255,255,255,0.06);
}
.nav-section-label {
    padding: 0.75rem 0.75rem 0.5rem;
    font-size: 0.7rem;
    font-weight: 700;
    color: rgba(255,255,255,0.4);
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.nav-link, .nav-link-active {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    padding: 0.55rem 0.75rem;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    font-weight: 500;
    text-decoration: none;
    margin-bottom: 0.15rem;
    border: 1px solid transparent;
    transition: background 0.15s ease;
}
.nav-link {
    color: rgba(255,255,255,0.65);
}
.nav-link:hover {
    background: rgba(255,255,255,0.05);
    color: white;
}
.nav-link-active {
    background: linear-gradient(135deg, rgba(56,189,248,0.2), rgba(99,102,246,0.2));
    border: 1px solid rgba(56,189,248,0.3);
    color: white;
    font-weight: 600;
}
.nav-link svg, .nav-link-active svg {
    flex-shrink: 0;
    opacity: 0.9;
}
</style>
"""


def _render_nav_link(label: str, icon_key: str, href: str, page_key: str, current_page: str) -> None:
    icon_svg = _ICONS.get(icon_key, "")
    css_class = "nav-link-active" if current_page == page_key else "nav-link"
    st.markdown(
        f'<a class="{css_class}" href="{href}">{icon_svg}<span>{label}</span></a>',
        unsafe_allow_html=True,
    )


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
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
                <div style="width: 36px; height: 36px; border-radius: 0.75rem; background: linear-gradient(135deg, #38bdf8, #0ea5e9); display: grid; place-items: center;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                </div>
                <span style="font-family: var(--font-display); font-size: 1.125rem; font-weight: 700; color: white;">CampaignCanvas</span>
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
        _render_nav_link("KPI Engine", "kpi_engine", "/export_data", "kpi_engine", current_page)
        _render_nav_link("Visualizations", "visualizations", "/export_data", "visualizations", current_page)
        _render_nav_link("SQL Workspace", "sql_workspace", "/export_data", "sql_workspace", current_page)

        # Actions Section
        st.markdown('<div class="nav-section-label" style="margin-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 1rem;">Actions</div>', unsafe_allow_html=True)
        _render_nav_link("Reports", "export_data", "/export_data", "export_data", current_page)
        _render_nav_link("Alerts", "alerts", "/export_data", "alerts", current_page)

        st.markdown(
            '<div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.08);"></div>',
            unsafe_allow_html=True,
        )

        # Sign Out Button
        if st.button("Sign out", key="sign_out_btn", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.email = ""
            st.switch_page("app.py")
        st.markdown("</div>", unsafe_allow_html=True)