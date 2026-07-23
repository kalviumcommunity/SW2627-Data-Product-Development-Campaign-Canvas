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
from src.utils.load_css import load_css, get_plotly_layout
from src.components.sidebar import render_sidebar
from src.components.navbar import render_navbar

st.set_page_config(page_title="CampaignCanvas", page_icon=":material/bar_chart:", layout="wide")
load_css()

# Check if user is logged in
if not st.session_state.get("logged_in", False):
    st.switch_page("pages/auth.py")


def _build_date_series(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["date", "spend", "revenue", "conversions", "signups", "activations_7d"])

    dated = frame.copy()
    dated["date"] = pd.to_datetime(dated["date"], errors="coerce")
    dated = dated.dropna(subset=["date"])
    dated["date"] = dated["date"].dt.strftime("%Y-%m-%d")

    spend_col = "spend_usd" if "spend_usd" in dated.columns else "spend"
    activation_col = "activations_7d" if "activations_7d" in dated.columns else "conversions"

    grouped = (
        dated.groupby("date", as_index=False)
        .agg(
            spend=(spend_col, "sum"),
            conversions=(activation_col, "sum"),
            signups=("signups", "sum"),
            activations_7d=(activation_col, "sum"),
            revenue=("revenue", "sum")
        )
        .sort_values("date")
        .reset_index(drop=True)
    )
    return grouped


def _build_funnel_totals(frame: pd.DataFrame) -> list[int]:
    if frame.empty:
        return [0, 0, 0, 0, 0]

    return [
        int(frame["impressions"].sum()),
        int(frame["clicks"].sum()),
        int(frame["signups"].sum()) if "signups" in frame.columns else 0,
        int(frame["profile_completed"].sum()) if "profile_completed" in frame.columns else 0,
        int(frame["activations_7d"].sum()) if "activations_7d" in frame.columns else 0,
    ]


def _trend_revenue_delta(frame: pd.DataFrame) -> float:
    if frame.empty:
        return 0.0

    ordered = frame.sort_values("date")
    midpoint = len(ordered) // 2
    first_half = float(ordered.iloc[:midpoint]["revenue"].sum())
    second_half = float(ordered.iloc[midpoint:]["revenue"].sum())
    return ((second_half - first_half) / first_half) * 100 if first_half else 0.0


def _campaign_name(campaign: pd.Series) -> str:
    return str(campaign["display_name"] if "display_name" in campaign else campaign["name"])


def _render_card_shell(label: str, value: str, icon_svg: str, accent_class: str, delta_html: str = "") -> None:
    st.markdown(
        f"""
        <div class="dashboard-stat-card {accent_class}">
            <div class="dashboard-stat-card__header">
                <div class="dashboard-stat-card__label">{label}</div>
                <div class="dashboard-stat-card__icon">{icon_svg}</div>
            </div>
            <div class="dashboard-stat-card__value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_campaign_card(title: str, campaign: pd.Series | None, positive: bool) -> None:
    if campaign is None or campaign.empty:
        return

    icon = "▲" if positive else "▼"
    accent = "#10b981" if positive else "#ef4444"
    st.markdown(
        f"""
        <div class="campaign-card" style="background: var(--secondary); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1rem 1.05rem; margin-bottom: 0.8rem;">
            <div class="campaign-card__label" style="color: {accent}; display: flex; align-items: center; gap: 0.35rem; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; margin-bottom: 0.35rem;">
                <span>{icon}</span>
                <span>{title}</span>
            </div>
            <div class="campaign-card__name" style="font-weight: 700; font-size: 1rem; color: var(--foreground);">{_campaign_name(campaign)}</div>
            <div class="campaign-card__meta" style="font-size: 0.82rem; color: var(--muted-foreground); margin-top: 0.35rem;">
                Revenue: {fmt_currency(campaign['totalRevenue'])} · ROAS {campaign['roas']:.2f}x
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    # Sidebar
    render_sidebar("dashboard")
    
    # Navbar
    render_navbar("Dashboard")

    frame, is_demo = load_campaign_data()
    by_date = _build_date_series(frame)
    kpis = compute_kpis(frame)
    growth = _trend_revenue_delta(by_date)

    campaign_col = "campaign_id" if "campaign_id" in frame.columns else "campaign"
    by_campaign = aggregate_by(frame, campaign_col)
    best = by_campaign.iloc[0] if not by_campaign.empty else None
    worst = by_campaign.iloc[-1] if len(by_campaign) > 1 else None

    # Get dynamic theme colors for Plotly charts
    plotly_style = get_plotly_layout()
    text_color = plotly_style["font"]["color"]
    grid_color = plotly_style["xaxis"]["gridcolor"]

    # Banner Card
    with st.container(border=True):
        col_text, col_btn = st.columns([5, 1], vertical_alignment="center")
        with col_text:
            st.markdown('<div style="font-size: 0.9rem; color: var(--muted-foreground);">Demo dataset loaded. Upload your own to unlock the pipeline.</div>', unsafe_allow_html=True)
        with col_btn:
            st.page_link("pages/upload.py", label="Upload data", icon=":material/upload:")

    st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)

    # First row of metric cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        _render_card_shell(
            "Total campaigns",
            f"{int(kpis['totalCampaigns'])}",
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>',
            "accent-violet",
        )

    with col2:
        total_spend = kpis['totalSpend']
        _render_card_shell(
            "Total spend",
            fmt_currency(total_spend),
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="1" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
            "accent-amber",
        )

    with col3:
        total_revenue = float(frame["revenue"].sum()) if not frame.empty else 0.0
        delta_color = "#10b981" if growth >= 0 else "#ef4444"
        delta_icon = "▲" if growth >= 0 else "▼"
        _render_card_shell(
            "Revenue",
            fmt_currency(total_revenue),
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
            "accent-emerald",
        )

    with col4:
        total_conversions = int(kpis.get('totalActivations', kpis.get('totalSignups', 0)))
        _render_card_shell(
            "Conversions",
            f"{total_conversions:,}",
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
            "accent-sky",
        )

    st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)

    # Second row of metric cards
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        _render_card_shell(
            "CTR",
            f"{kpis['ctr']*100:.2f}%",
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></polygon>',
            "accent-violet",
        )

    with col6:
        _render_card_shell(
            "CPA",
            fmt_currency(kpis['cpa']),
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><polyline points="17 11 19 13 23 9"/></polyline>',
            "accent-rose",
        )

    with col7:
        roas = total_revenue / total_spend if total_spend else 0.0
        _render_card_shell(
            "ROAS",
            f"{roas:.2f}x",
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
            "accent-emerald",
        )

    with col8:
        _render_card_shell(
            "Conversion rate",
            f"{kpis['cvr']*100:.2f}%",
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="1" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></path>',
            "accent-cyan",
        )

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    # Middle Section: Revenue vs. Spend + Top/Worst Campaign
    col_chart, col_side = st.columns([7, 3], gap="medium")
    with col_chart:
        with st.container(border=True):
            st.markdown('<div style="font-family: var(--font-display); font-size: 1.1rem; font-weight: 700; color: var(--foreground); margin-bottom: 0.2rem;">Revenue vs. Spend</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 0.8rem; color: var(--muted-foreground); margin-bottom: 1rem;">Daily trend</div>', unsafe_allow_html=True)

            if by_date.empty:
                st.info("No trend data is available yet.")
            else:
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=by_date["date"],
                        y=by_date["revenue"],
                        name="Revenue",
                        mode="lines+markers",
                        line=dict(color="#1d8cff", width=2.5),
                        fill="tozeroy",
                        fillcolor="rgba(29, 140, 255, 0.12)",
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=by_date["date"],
                        y=by_date["spend"],
                        name="Spend",
                        mode="lines+markers",
                        line=dict(color="#f59e0b", width=2.5),
                        fill="tozeroy",
                        fillcolor="rgba(245, 158, 11, 0.10)",
                    )
                )
                fig.update_layout(
                    height=320,
                    margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=text_color, size=11)),
                    xaxis=dict(showgrid=False, title=None, tickfont=dict(color=text_color, size=10)),
                    yaxis=dict(showgrid=True, gridcolor=grid_color, title=None, tickfont=dict(color=text_color, size=10)),
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_side:
        with st.container(border=True):
            st.markdown('<div style="font-family: var(--font-display); font-size: 1.1rem; font-weight: 700; color: var(--foreground); margin-bottom: 0.2rem;">Top / Worst Campaign</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 0.8rem; color: var(--muted-foreground); margin-bottom: 1rem;">By total revenue</div>', unsafe_allow_html=True)
            _render_campaign_card("Best", best, True)
            if worst is not None and (best is None or _campaign_name(worst) != _campaign_name(best)):
                _render_campaign_card("Worst", worst, False)

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    # Campaign Performance Section (Bar Chart)
    with st.container(border=True):
        st.markdown('<div style="font-family: var(--font-display); font-size: 1.1rem; font-weight: 700; color: var(--foreground); margin-bottom: 0.2rem;">Campaign performance</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 0.8rem; color: var(--muted-foreground); margin-bottom: 1rem;">Revenue and spend by campaign</div>', unsafe_allow_html=True)

        if by_campaign.empty:
            st.info("No campaign performance data is available yet.")
        else:
            campaign_perf = by_campaign.copy().head(10)
            spend_col = "spend_usd" if "spend_usd" in campaign_perf.columns else "spend"
            label_col = "display_name" if "display_name" in campaign_perf.columns else "name"
            fig_perf = go.Figure()
            fig_perf.add_trace(
                go.Bar(
                    x=campaign_perf[label_col],
                    y=campaign_perf["revenue"],
                    name="Revenue",
                    marker_color="#1d8cff",
                    width=0.36,
                )
            )
            fig_perf.add_trace(
                go.Bar(
                    x=campaign_perf[label_col],
                    y=campaign_perf[spend_col],
                    name="Spend",
                    marker_color="#f59e0b",
                    width=0.36,
                )
            )
            fig_perf.update_layout(
                height=340,
                barmode="group",
                bargap=0.28,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5, font=dict(color=text_color, size=11)),
                xaxis=dict(showgrid=False, title=None, tickangle=-15, tickfont=dict(color=text_color, size=10)),
                yaxis=dict(showgrid=True, gridcolor=grid_color, title=None, tickfont=dict(color=text_color, size=10)),
            )
            st.plotly_chart(fig_perf, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    # Acquisition Funnel & Signups vs. Activations Section
    col_funnel, col_prog = st.columns([1, 1], gap="medium")
    with col_funnel:
        with st.container(border=True):
            st.markdown('<div style="font-family: var(--font-display); font-size: 1.1rem; font-weight: 700; color: var(--foreground); margin-bottom: 0.2rem;">Acquisition funnel</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 0.8rem; color: var(--muted-foreground); margin-bottom: 1rem;">Joined from ad, signup, and activation tables</div>', unsafe_allow_html=True)

            funnel_values = _build_funnel_totals(frame)
            fig_funnel = go.Figure(
                go.Funnel(
                    y=["Impressions", "Clicks", "Signups", "Profile completed", "Activations"],
                    x=funnel_values,
                    textinfo="value+percent previous",
                    connector=dict(fillcolor="rgba(56, 189, 248, 0.12)"),
                    marker=dict(
                        color=["#0ea5e9", "#06b6d4", "#10b981", "#f59e0b", "#a855f7"],
                        line=dict(width=0),
                    ),
                )
            )
            fig_funnel.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=text_color, family="Inter, sans-serif"),
            )
            st.plotly_chart(fig_funnel, use_container_width=True, config={"displayModeBar": False})

    with col_prog:
        with st.container(border=True):
            st.markdown('<div style="font-family: var(--font-display); font-size: 1.1rem; font-weight: 700; color: var(--foreground); margin-bottom: 0.2rem;">Signups vs. activations</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 0.8rem; color: var(--muted-foreground); margin-bottom: 1rem;">Daily progression from HubSpot into product usage</div>', unsafe_allow_html=True)

            if by_date.empty:
                st.info("No trend data is available yet.")
            else:
                fig_stage_trend = go.Figure()
                fig_stage_trend.add_trace(
                    go.Scatter(
                        x=by_date["date"],
                        y=by_date["signups"],
                        name="Signups",
                        mode="lines+markers",
                        line=dict(color="#38bdf8", width=2.5),
                        marker=dict(size=5),
                    )
                )
                fig_stage_trend.add_trace(
                    go.Scatter(
                        x=by_date["date"],
                        y=by_date["activations_7d"],
                        name="Activations",
                        mode="lines+markers",
                        line=dict(color="#10b981", width=2.5),
                        marker=dict(size=5),
                    )
                )
                fig_stage_trend.update_layout(
                    height=320,
                    margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=text_color, size=10)),
                    xaxis=dict(showgrid=False, title=None, tickfont=dict(color=text_color, size=10)),
                    yaxis=dict(showgrid=True, gridcolor=grid_color, title=None, tickfont=dict(color=text_color, size=10)),
                )
                st.plotly_chart(fig_stage_trend, use_container_width=True, config={"displayModeBar": False})


if __name__ == "__main__":
    main()
