from __future__ import annotations

import html


def escape_html(value: object) -> str:
    """Escape text for safe insertion into HTML snippets rendered by Streamlit."""
    return html.escape(str(value), quote=True)
