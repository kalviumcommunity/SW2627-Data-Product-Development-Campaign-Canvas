import streamlit as st


def render_navbar(page_title: str):
    """
    Render the top navbar showing page title and user info.
    
    Args:
        page_title: Title of the current page to display
    """
    user_email = st.session_state.get("email", "Signed in")
    theme = st.session_state.get("theme", "dark")
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 0.75rem; min-height: 2.2rem; height: 100%;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--foreground); opacity: 0.85;">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                    <line x1="3" y1="9" x2="21" y2="9"/>
                    <line x1="9" y1="21" x2="9" y2="9"/>
                </svg>
                <span style="
                    font-family: var(--font-display);
                    font-size: 1.15rem;
                    font-weight: 700;
                    color: var(--foreground);
                ">
                    {page_title}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_right:
        sub_email, sub_theme = st.columns([5, 1])

        with sub_email:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: flex-end; align-items: center; min-height: 2.2rem; height: 100%; text-align: right; width: 100%;">
                    <span style="
                        color: var(--muted-foreground);
                        font-size: 0.875rem;
                        font-weight: 500;
                    ">
                        {user_email}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with sub_theme:
            icon = ":material/dark_mode:" if theme == "light" else ":material/light_mode:"
            target_theme = "Dark" if theme == "light" else "Light"
            if st.button(
                icon,
                key="theme_toggle_btn",
                help=f"Switch to {target_theme} theme",
                use_container_width=False,
            ):
                new_theme = "dark" if theme == "light" else "light"
                st.session_state["theme"] = new_theme

                import streamlit.components.v1 as components

                components.html(
                    f"""
                    <script>
                        parent.document.cookie = "theme={new_theme}; path=/; max-age=31536000; SameSite=Lax";
                    </script>
                    """,
                    height=0,
                    width=0,
                )
                st.rerun()
