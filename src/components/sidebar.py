
from __future__ import annotations

import streamlit as st


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

        # Overview section
        st.markdown("""
            <div style="margin-bottom: 0.25rem; padding: 0 0.25rem; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #64748b;">
                Overview
            </div>
        """, unsafe_allow_html=True)

        # Dashboard link
        if current_page == "dashboard":
            st.markdown("""
                <div style="padding: 0.5rem 0.75rem; border-radius: 0.5rem; display: flex; align-items: center; gap: 0.5rem; background: linear-gradient(135deg, rgba(56,189,248,0.2), rgba(99,102,246,0.2)); border: 1px solid rgba(56,189,248,0.3); color: white; font-size: 0.875rem; font-weight: 600;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"></rect><rect width="7" height="5" x="14" y="3" rx="1"></rect><rect width="7" height="9" x="14" y="12" rx="1"></rect><rect width="7" height="5" x="3" y="16" rx="1"></rect></svg>
                    Dashboard
                </div>
            """, unsafe_allow_html=True)
        else:
            st.page_link("pages/dashboard.py", label="Dashboard", icon="📊", use_container_width=True)

        # Data section
        st.markdown("""
            <div style="margin-top: 1.5rem; margin-bottom: 0.5rem; padding: 0 0.25rem; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #64748b;">
                Data
            </div>
        """, unsafe_allow_html=True)

        # Upload (placeholder)
        st.markdown("""
            <div style="padding: 0.5rem 0.75rem; border-radius: 0.5rem; display: flex; align-items: center; gap: 0.5rem; color: #94a3b8; font-size: 0.875rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" x2="12" y1="3" y2="15"></line></svg>
                Upload
            </div>
        """, unsafe_allow_html=True)

        # Profiling (placeholder)
        st.markdown("""
            <div style="padding: 0.5rem 0.75rem; border-radius: 0.5rem; display: flex; align-items: center; gap: 0.5rem; color: #94a3b8; font-size: 0.875rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4Z"></path></svg>
                Profiling
            </div>
        """, unsafe_allow_html=True)

        # Cleaning (placeholder)
        st.markdown("""
            <div style="padding: 0.5rem 0.75rem; border-radius: 0.5rem; display: flex; align-items: center; gap: 0.5rem; color: #94a3b8; font-size: 0.875rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3h18v18H3z"></path><path d="M18 12l-6 6-6-6"></path></svg>
                Cleaning
            </div>
        """, unsafe_allow_html=True)

        # Database (placeholder)
        st.markdown("""
            <div style="padding: 0.5rem 0.75rem; border-radius: 0.5rem; display: flex; align-items: center; gap: 0.5rem; color: #94a3b8; font-size: 0.875rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5V19A9 3 0 0 0 21 19V5"></path><path d="M3 12A9 3 0 0 0 21 12"></path></svg>
                Database
            </div>
        """, unsafe_allow_html=True)

        # Insights section
        st.markdown("""
            <div style="margin-top: 1.5rem; margin-bottom: 0.5rem; padding: 0 0.25rem; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #64748b;">
                Insights
            </div>
        """, unsafe_allow_html=True)

        # Analytics link
        if current_page == "campaign_analysis":
            st.markdown("""
                <div style="padding: 0.5rem 0.75rem; border-radius: 0.5rem; display: flex; align-items: center; gap: 0.5rem; background: linear-gradient(135deg, rgba(56,189,248,0.2), rgba(99,102,246,0.2)); border: 1px solid rgba(56,189,248,0.3); color: white; font-size: 0.875rem; font-weight: 600;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                    Analytics
                </div>
            """, unsafe_allow_html=True)
        else:
            st.page_link("pages/campaign_analysis.py", label="Analytics", icon="📈", use_container_width=True)

        # Funnel link
        if current_page == "activation_funnel":
            st.markdown("""
                <div style="padding: 0.5rem 0.75rem; border-radius: 0.5rem; display: flex; align-items: center; gap: 0.5rem; background: linear-gradient(135deg, rgba(56,189,248,0.2), rgba(99,102,246,0.2)); border: 1px solid rgba(56,189,248,0.3); color: white; font-size: 0.875rem; font-weight: 600;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                    Funnel
                </div>
            """, unsafe_allow_html=True)
        else:
            st.page_link("pages/activation_funnel.py", label="Funnel", icon="📊", use_container_width=True)

        # KPI Engine (placeholder)
        st.markdown("""
            <div style="padding: 0.5rem 0.75rem; border-radius: 0.5rem; display: flex; align-items: center; gap: 0.5rem; color: #94a3b8; font-size: 0.875rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                KPI Engine
            </div>
        """, unsafe_allow_html=True)

        # Visualizations (placeholder)
        st.markdown("""
            <div style="padding: 0.5rem 0.75rem; border-radius: 0.5rem; display: flex; align-items: center; gap: 0.5rem; color: #94a3b8; font-size: 0.875rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5"></path><path d="M5 12l7-7 7 7"></path></svg>
                Visualizations
            </div>
        """, unsafe_allow_html=True)

        # SQL Workspace (placeholder)
        st.markdown("""
            <div style="padding: 0.5rem 0.75rem; border-radius: 0.5rem; display: flex; align-items: center; gap: 0.5rem; color: #94a3b8; font-size: 0.875rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><polyline points="17 5 21 9 13 9"></polyline></svg>
                SQL Workspace
            </div>
        """, unsafe_allow_html=True)

        # Actions section
        st.markdown("""
            <div style="margin-top: 1.5rem; margin-bottom: 0.5rem; padding: 0 0.25rem; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #64748b;">
                Actions
            </div>
        """, unsafe_allow_html=True)

        # Reports link
        if current_page == "export_data":
            st.markdown("""
                <div style="padding: 0.5rem 0.75rem; border-radius: 0.5rem; display: flex; align-items: center; gap: 0.5rem; background: linear-gradient(135deg, rgba(56,189,248,0.2), rgba(99,102,246,0.2)); border: 1px solid rgba(56,189,248,0.3); color: white; font-size: 0.875rem; font-weight: 600;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" x2="8" y1="13" y2="13"></line><line x1="16" x2="8" y1="17" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                    Reports
                </div>
            """, unsafe_allow_html=True)
        else:
            st.page_link("pages/export_data.py", label="Reports", icon="📄", use_container_width=True)

        # Alerts (placeholder)
        st.markdown("""
            <div style="padding: 0.5rem 0.75rem; border-radius: 0.5rem; display: flex; align-items: center; gap: 0.5rem; color: #94a3b8; font-size: 0.875rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                Alerts
            </div>
        """, unsafe_allow_html=True)

        # Spacer
        st.markdown("""
            <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.08); display: flex; flex-direction: column; gap: 0.25rem;">
        """, unsafe_allow_html=True)

        # Sign Out Button
        if st.button("Sign out", key="sign_out_btn", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.email = ""
            st.switch_page("app.py")

        st.markdown("</div>", unsafe_allow_html=True)
