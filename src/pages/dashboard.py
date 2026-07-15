
from __future__ import annotations

import sys
from pathlib import Path

root_dir = str(Path(__file__).resolve().parents[2])
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.utils.campaigns import aggregate_by, compute_kpis, fmt_currency, fmt_num, fmt_pct, load_campaign_data
from src.utils.load_css import load_css
from src.components.sidebar import render_sidebar

st.set_page_config(page_title="CampaignCanvas", page_icon="📊", layout="wide")
load_css()

# Check if user is logged in
if not st.session_state.get("logged_in", False):
    st.switch_page("pages/auth.py")

def _format_banner(is_demo: bool) -> str:
    if is_demo:
        return "Demo dataset loaded. Upload your own to unlock the pipeline."
    return "Live dataset loaded from your workspace data directory."

def _build_date_series(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["date", "spend", "revenue", "conversions"])

    dated = frame.copy()
    dated["date"] = pd.to_datetime(dated["date"], errors="coerce")
    dated = dated.dropna(subset=["date"])
    dated["date"] = dated["date"].dt.strftime("%Y-%m-%d")

    spend_col = "spend_usd" if "spend_usd" in dated.columns else "spend"
    activation_col = "activations_7d" if "activations_7d" in dated.columns else "conversions"

    grouped = (
        dated.groupby("date", as_index=False)
        .agg(spend=(spend_col, "sum"), conversions=(activation_col, "sum"))
        .sort_values("date")
        .reset_index(drop=True)
    )
    grouped["revenue"] = grouped["spend"] * 1.5  # Demo revenue calculation
    return grouped

def _trend_revenue_delta(frame: pd.DataFrame) -> float:
    if frame.empty:
        return 0.0

    ordered = frame.sort_values("date")
    midpoint = len(ordered) // 2
    first_half = float(ordered.iloc[:midpoint]["revenue"].sum())
    second_half = float(ordered.iloc[midpoint:]["revenue"].sum())
    return ((second_half - first_half) / first_half) * 100 if first_half else 0.0

def _render_campaign_card(title: str, campaign: pd.Series | None, positive: bool) -> None:
    if campaign is None or campaign.empty:
        return

    icon = "▲" if positive else "▼"
    accent = "#10b981" if positive else "#ef4444"
    st.markdown(
        f"""
        <div style="padding: 1rem 1.1rem; border-radius: 0.75rem; border: 1px solid rgba(255,255,255,0.08); background: rgba(15,23,42,0.5); margin-bottom: 0.75rem;">
            <div style="display: flex; align-items: center; gap: 0.25rem; font-size: 0.75rem; font-weight: 700; color: {accent}; margin-bottom: 0.25rem;">
                <span>{icon}</span>
                <span>{title}</span>
            </div>
            <div style="font-weight: 600; color: white;">{campaign['display_name'] if 'display_name' in campaign else campaign['name']}</div>
            <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.25rem;">
                Revenue: {fmt_currency(campaign['totalRevenue'])} · ROAS {campaign['roas']:.2f}x
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def main() -> None:
    # Sidebar
    render_sidebar("dashboard")

    frame, is_demo = load_campaign_data()
    by_date = _build_date_series(frame)
    kpis = compute_kpis(frame)
    growth = _trend_revenue_delta(by_date)

    campaign_col = "campaign_id" if "campaign_id" in frame.columns else "campaign"
    by_campaign = aggregate_by(frame, campaign_col)
    best = by_campaign.iloc[0] if not by_campaign.empty else None
    worst = by_campaign.iloc[-1] if len(by_campaign) > 1 else None

    # Header Section
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="display: none;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"></rect><rect width="7" height="5" x="14" y="3" rx="1"></rect><rect width="7" height="9" x="14" y="12" rx="1"></rect><rect width="7" height="5" x="3" y="16" rx="1"></rect></svg>
                </div>
                <div style="font-size: 0.875rem; font-weight: 500; color: white;">Dashboard</div>
            </div>
            <div style="display: flex; align-items: center; gap: 1rem;">
    """, unsafe_allow_html=True)
    
    # User Email
    st.markdown(f"""
                <div style="font-size: 0.875rem; color: #cbd5e1;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:inline; margin-right: 0.25rem; vertical-align: middle;"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                    {st.session_state.email}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Banner with Upload Button
    st.markdown(f"""
        <div style="background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.75rem; padding: 1rem; display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <div style="color: #cbd5e1; font-size: 0.875rem;">{_format_banner(is_demo)}</div>
            <button style="background: linear-gradient(135deg, #38bdf8, #0ea5e9); color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; font-size: 0.875rem; font-weight: 600; cursor: pointer;">
                Upload data
            </button>
        </div>
    """, unsafe_allow_html=True)

    if is_demo:
        pass
        # st.info("Demo data is being used because no campaign dataset was found in data/raw or data/processed.")

    # Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div style="background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.75rem; padding: 1rem 1.25rem; position: relative; overflow: hidden;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                    <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 500; text-transform: uppercase;">Total Campaigns</div>
                    <div style="width: 32px; height: 32px; border-radius: 9999px; background: rgba(139,92,246,0.15); display: grid; place-items: center;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"></rect><rect width="7" height="5" x="14" y="3" rx="1"></rect><rect width="7" height="9" x="14" y="12" rx="1"></rect><rect width="7" height="5" x="3" y="16" rx="1"></rect></svg>
                    </div>
                </div>
                <div style="font-family: var(--font-display); font-size: 1.875rem; font-weight: 800; color: white;">{int(kpis['totalCampaigns'])}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        total_spend = kpis['totalSpend']
        st.markdown(f"""
            <div style="background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.75rem; padding: 1rem 1.25rem; position: relative; overflow: hidden;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                    <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 500; text-transform: uppercase;">Total Spend</div>
                    <div style="width: 32px; height: 32px; border-radius: 9999px; background: rgba(245,158,11,0.15); display: grid; place-items: center;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="1" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                    </div>
                </div>
                <div style="font-family: var(--font-display); font-size: 1.875rem; font-weight: 800; color: white;">{fmt_currency(total_spend)}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        total_revenue = kpis['totalSpend'] * 1.5
        delta_color = "#10b981" if growth >= 0 else "#ef4444"
        delta_icon = "▲" if growth >=0 else "▼"
        st.markdown(f"""
            <div style="background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.75rem; padding: 1rem 1.25rem; position: relative; overflow: hidden;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                    <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 500; text-transform: uppercase;">Revenue</div>
                    <div style="width: 32px; height: 32px; border-radius: 9999px; background: rgba(16,185,129,0.15); display: grid; place-items: center;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
                    </div>
                </div>
                <div style="font-family: var(--font-display); font-size: 1.875rem; font-weight: 800; color: white;">{fmt_currency(total_revenue)}</div>
                <div style="display: flex; align-items: center; gap: 0.25rem; color: {delta_color}; font-size: 0.75rem; font-weight: 500; margin-top: 0.25rem;">
                    <span>{delta_icon}</span>
                    <span>{abs(growth):.1f}% vs. prior period</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        total_conversions = int(kpis.get('totalActivations', kpis.get('totalSignups', 0)))
        st.markdown(f"""
            <div style="background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.75rem; padding: 1rem 1.25rem; position: relative; overflow: hidden;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                    <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 500; text-transform: uppercase;">Conversions</div>
                    <div style="width: 32px; height: 32px; border-radius: 9999px; background: rgba(56,189,248,0.15); display: grid; place-items: center;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>
                    </div>
                </div>
                <div style="font-family: var(--font-display); font-size: 1.875rem; font-weight: 800; color: white;">{total_conversions:,}</div>
            </div>
        """, unsafe_allow_html=True)

    # Second Row of Metric Cards
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.markdown(f"""
            <div style="background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.75rem; padding: 1rem 1.25rem; position: relative; overflow: hidden;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                    <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 500; text-transform: uppercase;">CTR</div>
                    <div style="width: 32px; height: 32px; border-radius: 9999px; background: rgba(139,92,246,0.15); display: grid; place-items: center;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                    </div>
                </div>
                <div style="font-family: var(--font-display); font-size: 1.875rem; font-weight: 800; color: white;">{kpis['ctr']*100:.2f}%</div>
            </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(f"""
            <div style="background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.75rem; padding: 1rem 1.25rem; position: relative; overflow: hidden;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                    <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 500; text-transform: uppercase;">CPA</div>
                    <div style="width: 32px; height: 32px; border-radius: 9999px; background: rgba(236,72,153,0.15); display: grid; place-items: center;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ec4899" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><polyline points="17 11 19 13 23 9"></polyline></svg>
                    </div>
                </div>
                <div style="font-family: var(--font-display); font-size: 1.875rem; font-weight: 800; color: white;">{fmt_currency(kpis['cpa'])}</div>
            </div>
        """, unsafe_allow_html=True)

    with col7:
        roas = 1.5
        st.markdown(f"""
            <div style="background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.75rem; padding: 1rem 1.25rem; position: relative; overflow: hidden;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                    <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 500; text-transform: uppercase;">ROAS</div>
                    <div style="width: 32px; height: 32px; border-radius: 9999px; background: rgba(34,197,94,0.15); display: grid; place-items: center;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
                    </div>
                </div>
                <div style="font-family: var(--font-display); font-size: 1.875rem; font-weight: 800; color: white;">{roas:.2f}x</div>
            </div>
        """, unsafe_allow_html=True)

    with col8:
        st.markdown(f"""
            <div style="background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.75rem; padding: 1rem 1.25rem; position: relative; overflow: hidden;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                    <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 500; text-transform: uppercase;">Conversion Rate</div>
                    <div style="width: 32px; height: 32px; border-radius: 9999px; background: rgba(6,182,212,0.15); display: grid; place-items: center;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#06b6d4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="1" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                    </div>
                </div>
                <div style="font-family: var(--font-display); font-size: 1.875rem; font-weight: 800; color: white;">{kpis['cvr']*100:.2f}%</div>
            </div>
        """, unsafe_allow_html=True)

    left, right = st.columns([2, 1], gap="large")
    with left:
        st.markdown("""
            <div style="background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.75rem; padding: 1.25rem;">
                <div style="font-family: var(--font-display); font-weight: 700; color: white; margin-bottom: 0.25rem;">Revenue vs. Spend</div>
                <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 1rem;">Daily trend</div>
        """, unsafe_allow_html=True)

        if by_date.empty:
            st.info("No trend data is available yet.")
        else:
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=by_date["date"],
                    y=by_date["revenue"],
                    name="Revenue",
                    mode="lines",
                    line=dict(color="#38bdf8", width=3),
                    fill="tozeroy",
                    fillcolor="rgba(56, 189, 248, 0.16)",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=by_date["date"],
                    y=by_date["spend"],
                    name="Spend",
                    mode="lines",
                    line=dict(color="#f59e0b", width=3),
                    fill="tozeroy",
                    fillcolor="rgba(245, 158, 11, 0.14)",
                )
            )
            fig.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="white", size=10)),
                xaxis=dict(showgrid=False, title=None, tickfont=dict(color="#94a3b8", size=10)),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", title=None, tickfont=dict(color="#94a3b8", size=10)),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("""
            <div style="background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.75rem; padding: 1.25rem;">
                <div style="font-family: var(--font-display); font-weight: 700; color: white; margin-bottom: 0.25rem;">Top / Worst Campaign</div>
                <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 1rem;">By total revenue</div>
        """, unsafe_allow_html=True)
        _render_campaign_card("Best", best, True)
        if worst is not None and (best is None or (worst['display_name'] if 'display_name' in worst else worst['name']) != (best['display_name'] if 'display_name' in best else best['name'])):
            _render_campaign_card("Worst", worst, False)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
        <div style="background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.08); border-radius: 0.75rem; padding: 1.25rem; margin-top: 1.25rem;">
            <div style="font-family: var(--font-display); font-weight: 700; color: white; margin-bottom: 0.25rem;">Campaign performance</div>
            <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 1rem;">Revenue and spend by campaign</div>
    """, unsafe_allow_html=True)

    if by_campaign.empty:
        st.info("No campaign performance data is available yet.")
    else:
        campaign_perf = by_campaign.copy().head(10)
        spend_col = "spend_usd" if "spend_usd" in campaign_perf.columns else "spend"
        label_col = "display_name" if "display_name" in campaign_perf.columns else "name"
        campaign_perf["revenue"] = campaign_perf[spend_col] * 1.5
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=campaign_perf[label_col],
                y=campaign_perf["revenue"],
                name="Revenue",
                marker_color="#1d8cff",
                width=0.36,
            )
        )
        fig.add_trace(
            go.Bar(
                x=campaign_perf[label_col],
                y=campaign_perf[spend_col],
                name="Spend",
                marker_color="#f59e0b",
                width=0.36,
            )
        )
        fig.update_layout(
            height=340,
            barmode="group",
            bargap=0.28,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5, font=dict(color="white", size=12)),
            xaxis=dict(showgrid=False, title=None, tickangle=-20, tickfont=dict(color="#94a3b8", size=10)),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", title=None, tickfont=dict(color="#94a3b8", size=10)),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

