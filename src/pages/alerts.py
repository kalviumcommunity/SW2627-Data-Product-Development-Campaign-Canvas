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

st.set_page_config(page_title="Alerts — CampaignCanvas", page_icon="📊", layout="wide")
load_css()

# Check if user is logged in
if not st.session_state.get("logged_in", False):
    st.switch_page("pages/auth.py")

# Initialize active alerts list in session state
if "active_alerts" not in st.session_state:
    st.session_state.active_alerts = []


def main():
    # Sidebar
    render_sidebar("alerts")
    
    # Navbar
    render_navbar("Alerts")

    # Layout: Left column for Active Alerts, Right column for Create Alert form
    col_active, col_create = st.columns([5, 3], gap="large")

    with col_create:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1.25rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
                    <span style="font-family: var(--font-display); font-size: 1.1rem; font-weight: 700; color: white;">Create alert</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            with st.form("create_alert_form", border=False):
                alert_name = st.text_input("Name", value="High CPA warning", placeholder="Enter alert name")
                metric = st.selectbox(
                    "Metric",
                    ["CPA ($)", "Spend ($)", "Conversions", "CTR (%)", "Clicks", "Impressions"]
                )
                
                col_op, col_val = st.columns(2)
                with col_op:
                    operator = st.selectbox("Operator", ["Above (>)", "Below (<)", "Equals (=)"])
                with col_val:
                    threshold = st.number_input("Threshold", value=50.0, step=1.0)
                
                st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                create_submitted = st.form_submit_button("+ Create", use_container_width=True, type="primary")
                
                if create_submitted:
                    if not alert_name.strip():
                        st.error("Please enter a name for the alert.")
                    else:
                        st.session_state.active_alerts.append({
                            "name": alert_name,
                            "metric": metric,
                            "operator": operator,
                            "threshold": threshold
                        })
                        st.toast(f"Alert '{alert_name}' successfully created!", icon="🔔")
                        st.rerun()

    with col_active:
        # Active alerts container
        if not st.session_state.active_alerts:
            st.markdown(
                """
                <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.1); border-radius: var(--radius-xl); padding: 3rem; text-align: center; color: var(--muted-foreground); font-size: 0.9rem;">
                    No alerts yet — create one on the right to monitor a KPI threshold.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            # Display active alerts as beautiful custom panels
            for idx, alert in enumerate(st.session_state.active_alerts):
                # Map operator string to icon representation
                op_icon = ">" if ">" in alert["operator"] else "<" if "<" in alert["operator"] else "="
                
                # Check metric formats for display
                fmt_val = f"${alert['threshold']:.2f}" if "$" in alert["metric"] or alert["metric"] == "CPA ($)" else f"{alert['threshold']:.2f}%" if "%" in alert["metric"] else f"{int(alert['threshold'])}"

                with st.container(border=True):
                    col_info, col_action = st.columns([6, 1])
                    with col_info:
                        st.markdown(
                            f"""
                            <div style="display: flex; flex-direction: column;">
                                <span style="font-family: var(--font-display); font-weight: 700; color: white; font-size: 1.05rem;">{alert['name']}</span>
                                <span style="font-size: 0.85rem; color: var(--muted-foreground); margin-top: 0.25rem;">
                                    Monitors: <strong style="color: #38bdf8;">{alert['metric']}</strong> {op_icon} <strong style="color: #38bdf8;">{fmt_val}</strong>
                                </span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    with col_action:
                        # Add some margin spacing
                        st.markdown("<div style='margin-top: 0.25rem;'></div>", unsafe_allow_html=True)
                        if st.button("🗑️", key=f"del_alert_{idx}", help="Delete alert"):
                            st.session_state.active_alerts.pop(idx)
                            st.toast(f"Alert '{alert['name']}' deleted.", icon="🗑️")
                            st.rerun()


if __name__ == "__main__":
    main()

