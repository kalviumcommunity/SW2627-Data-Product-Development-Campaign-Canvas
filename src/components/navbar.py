import streamlit as st


def render_navbar(page_title: str):
    """Render top navbar with title on the far left, and email + theme badge on the far right edge with working hover tooltip."""
    user_email = st.session_state.get("email", "Signed in")
    theme = st.session_state.get("theme", "dark")
    target_theme = "dark" if theme == "light" else "light"
    icon = ":material/dark_mode:" if theme == "light" else ":material/light_mode:"

    st.markdown(
        f"""
        <style>
        /* 1. Navbar Container */
        .st-key-navbar_row {{
            margin-bottom: 1.25rem !important;
            padding: 0.2rem 0 !important;
            width: 100% !important;
        }}

        /* 2. Main Horizontal Layout */
        .st-key-navbar_row [data-testid="stHorizontalBlock"] {{
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            justify-content: space-between !important;
            width: 100% !important;
        }}

        /* 3. Left Column (Title) */
        .st-key-navbar_row [data-testid="column"]:first-child {{
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            flex: 0 0 auto !important;
            width: auto !important;
        }}

        /* 4. Right Column (Email + Button) - Pushed to far right edge */
        .st-key-navbar_row [data-testid="column"]:last-child {{
            display: flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
            flex: 1 1 auto !important;
            width: auto !important;
        }}

        /* 5. Inject Email directly next to Theme Toggle Button */
        div.st-key-theme_toggle_btn {{
            display: inline-flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
            gap: 0.85rem !important;
            margin-left: auto !important;
        }}

        div.st-key-theme_toggle_btn::before {{
            content: "{user_email}";
            color: var(--muted-foreground, #666666);
            font-size: 0.875rem;
            font-weight: 500;
            line-height: 1;
            white-space: nowrap;
            user-select: none;
        }}

        /* 6. Circular Badge Button Styling */
        div.st-key-theme_toggle_btn button {{
            background-color: var(--card, #ffffff) !important;
            border: 1px solid var(--border, rgba(0, 0, 0, 0.08)) !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
            margin: 0 !important;
            padding: 0 !important;
            height: 2.2rem !important;
            width: 2.2rem !important;
            min-height: 2.2rem !important;
            min-width: 2.2rem !important;
            border-radius: 50% !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }}

        div.st-key-theme_toggle_btn button:hover {{
            border-color: var(--primary) !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1) !important;
            transform: translateY(-1px);
        }}

        div.st-key-theme_toggle_btn button span[data-testid="stIconMaterial"] {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            line-height: 1 !important;
            font-size: 1.15rem !important;
            color: var(--foreground) !important;
            -webkit-text-fill-color: var(--foreground) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="navbar_row"):
        col_left, col_right = st.columns([1, 1], vertical_alignment="center")

        # LEFT SIDE: Icon + Title
        with col_left:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; gap: 0.65rem; height: 2.2rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--foreground); opacity: 0.85; flex-shrink: 0;">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                        <line x1="3" y1="9" x2="21" y2="9"/>
                        <line x1="9" y1="21" x2="9" y2="9"/>
                    </svg>
                    <span style="
                        font-family: var(--font-display);
                        font-size: 1.15rem;
                        font-weight: 700;
                        color: var(--foreground);
                        line-height: 1;
                        letter-spacing: -0.01em;
                        white-space: nowrap;
                    ">
                        {page_title}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # RIGHT SIDE: Email + Moon Icon with working hover tooltip
        with col_right:
            if st.button(
                icon,
                key="theme_toggle_btn",
                help=f"Switch to {target_theme} theme",
                use_container_width=False,
            ):
                st.session_state["theme"] = target_theme
                import streamlit.components.v1 as components

                components.html(
                    f"""
                    <script>
                        parent.document.cookie = "theme={target_theme}; path=/; max-age=31536000; SameSite=Lax";
                    </script>
                    """,
                    height=0,
                    width=0,
                )
                st.rerun()