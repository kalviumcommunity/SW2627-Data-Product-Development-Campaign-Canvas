
from __future__ import annotations

import streamlit as st


def _render_nav_link(label: str, icon: str, page_path: str, page_key: str, current_page: str) -> None:
    if current_page == page_key:
        st.markdown(
            f"""
            <div style="padding: 0.5rem 0.75rem; border-radius: 0.5rem; display: flex; align-items: center; gap: 0.5rem; background: linear-gradient(135deg, rgba(56,189,248,0.2), rgba(99,102,246,0.2)); border: 1px solid rgba(56,189,248,0.3); color: white; font-size: 0.875rem; font-weight: 600;">
                <span style="font-size: 1rem; line-height: 1;">{icon}</span>
                {label}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.page_link(page_path, label=label, icon=icon, use_container_width=True)


def render_sidebar(current_page: str):
    """
    Render the CampaignIQ sidebar.

    Args:
        current_page: The name of the current active page to highlight
    """
    with st.sidebar:
        # Logo at top
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
                <div style="width: 36px; height: 36px; border-radius: 0.75rem; background: linear-gradient(135deg, #38bdf8, #0ea5e9); display: grid; place-items: center;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                </div>
                <span style="font-family: var(--font-display); font-size: 1.125rem; font-weight: 700; color: white;">CampaignIQ</span>
            </div>
        """, unsafe_allow_html=True)

        _render_nav_link("Dashboard", "📊", "pages/dashboard.py", "dashboard", current_page)
        _render_nav_link("Analytics", "📈", "pages/campaign_analysis.py", "campaign_analysis", current_page)
        _render_nav_link("Funnel", "📊", "pages/activation_funnel.py", "activation_funnel", current_page)
        _render_nav_link("Reports", "📄", "pages/export_data.py", "export_data", current_page)

        st.markdown(
            """
            <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.08); display: flex; flex-direction: column; gap: 0.25rem;">
            """,
            unsafe_allow_html=True,
        )

        # Sign Out Button
        if st.button("Sign out", key="sign_out_btn", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.email = ""
            st.switch_page("app.py")

        st.markdown("</div>", unsafe_allow_html=True)
