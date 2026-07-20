import sys
from pathlib import Path
import streamlit as st

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.utils.load_css import load_css
from src.components.sidebar import render_sidebar
from src.components.navbar import render_navbar

st.set_page_config(page_title="Settings — CampaignCanvas", page_icon=":material/bar_chart:", layout="wide")
load_css()

# Check if user is logged in
if not st.session_state.get("logged_in", False):
    st.switch_page("pages/auth.py")


def main():
    # Sidebar
    render_sidebar("settings")
    
    # Navbar
    render_navbar("Settings")

    # 2x2 Grid Layout
    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        # 1. Profile Settings
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1.25rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                    <span style="font-family: var(--font-display); font-size: 1.05rem; font-weight: 700; color: white;">Profile</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            default_name = st.session_state.get("name", "")
            fullname = st.text_input("Full name", value=default_name, key="settings_fullname")
            
            # Default email value from session state
            default_email = st.session_state.get("email", "")
            email = st.text_input("Email", value=default_email, key="settings_email", disabled=True)
            
            st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
            save_clicked = st.button("Save", key="save_profile_btn")
            if save_clicked:
                st.session_state.name = fullname
                import streamlit.components.v1 as components
                components.html(
                    f"""
                    <script>
                        parent.document.cookie = "name={fullname}; path=/; max-age=86400; SameSite=Lax";
                    </script>
                    """,
                    height=0,
                    width=0,
                )
                st.toast("Profile settings saved successfully!", icon=":material/check_circle:")
        
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

        # 3. Notifications Settings
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1.25rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
                    <span style="font-family: var(--font-display); font-size: 1.05rem; font-weight: 700; color: white;">Notifications</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.toggle("Email me when alerts trigger", value=True, key="settings_email_alerts")
            st.caption("Requires connecting an email provider.")

    with col_right:
        # 2. Appearance Settings
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1.25rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/><path d="M2 12h20"/></svg>
                    <span style="font-family: var(--font-display); font-size: 1.05rem; font-weight: 700; color: white;">Appearance</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            current_theme = st.session_state.get("theme", "dark")
            is_dark = (current_theme == "dark")
            
            def on_theme_toggle_change():
                new_theme = "dark" if st.session_state["settings_dark_mode"] else "light"
                st.session_state["theme"] = new_theme
                st.query_params["theme"] = new_theme

            st.toggle(
                "Dark mode",
                value=is_dark,
                key="settings_dark_mode",
                on_change=on_theme_toggle_change
            )
            st.caption("Switch between light and dark themes.")
        
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

        # 4. Data Settings
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1.25rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
                    <span style="font-family: var(--font-display); font-size: 1.05rem; font-weight: 700; color: white;">Data</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.write("Download a full workbook of every dataset in your workspace.")
            
            st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
            download_btn = st.button("Download backup (.xlsx)", key="download_backup_btn")
            if download_btn:
                st.toast("Backup archive generated and downloading...", icon=":material/download:")


if __name__ == "__main__":
    main()

