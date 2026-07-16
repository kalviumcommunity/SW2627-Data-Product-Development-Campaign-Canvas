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
    try:
        css = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        st.warning(f"Stylesheet not found at {path} — using default Streamlit theme.")
        return
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)