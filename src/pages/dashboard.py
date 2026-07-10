from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.utils.campaigns import aggregate_by, compute_kpis, fmt_currency, fmt_num, fmt_pct, load_campaign_data
from src.utils.load_css import load_css


st.set_page_config(page_title="Dashboard — CampaignIQ", page_icon="📊", layout="wide")
load_css()


def _trend_revenue_delta(frame: pd.DataFrame) -> float:
    if frame.empty:
        return 0.0

    ordered = frame.sort_values("date")
    midpoint = len(ordered) // 2
    first_half = float(ordered.iloc[:midpoint]["revenue"].sum())
    second_half = float(ordered.iloc[midpoint:]["revenue"].sum())
    return ((second_half - first_half) / first_half) * 100 if first_half else 0.0


def _format_banner(is_demo: bool) -> str:
    if is_demo:
        return "Demo dataset loaded. Add a processed or raw CSV to replace it."
    return "Live dataset loaded from your workspace data directory."


def _build_date_series(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=["date", "spend", "revenue", "conversions"])

    dated = frame.copy()
    dated["date"] = pd.to_datetime(dated["date"], errors="coerce")
    dated = dated.dropna(subset=["date"])
    dated["date"] = dated["date"].dt.strftime("%Y-%m-%d")

    return (
        dated.groupby("date", as_index=False)
        .agg(spend=("spend", "sum"), revenue=("revenue", "sum"), conversions=("conversions", "sum"))
        .sort_values("date")
        .reset_index(drop=True)
    )


def _render_campaign_card(title: str, campaign: pd.Series | None, positive: bool) -> None:
    if campaign is None or campaign.empty:
        return

    icon = "▲" if positive else "▼"
    accent = "#16a34a" if positive else "#dc2626"
    st.markdown(
        f"""
        <div class="glass-card" style="padding: 1rem 1.1rem; margin-bottom: 0.75rem;">
            <div style="font-size: 0.75rem; font-weight: 700; color: {accent};">{icon} {title}</div>
            <div style="font-weight: 600; margin-top: 0.25rem;">{campaign['name']}</div>
            <div style="font-size: 0.85rem; color: var(--muted-foreground); margin-top: 0.25rem;">
                Revenue: {fmt_currency(float(campaign['totalRevenue']))} · ROAS {float(campaign['roas']):.2f}x
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    frame, is_demo = load_campaign_data()
    by_date = _build_date_series(frame)
    by_campaign = aggregate_by(frame, "campaign")
    kpis = compute_kpis(frame)
    growth = _trend_revenue_delta(by_date)

    best = by_campaign.iloc[0] if not by_campaign.empty else None
    worst = by_campaign.iloc[-1] if len(by_campaign) > 1 else None

    st.markdown(
        f"""
        <div class="glass-card" style="display:flex;align-items:center;justify-content:space-between;gap:1rem;margin-bottom:1rem;">
            <div>
                <div style="font-size:0.75rem;letter-spacing:0.08em;text-transform:uppercase;color:var(--muted-foreground);">CampaignIQ dashboard</div>
                <div style="font-family:var(--font-display);font-size:1.1rem;font-weight:700;">Daily campaign performance and activation signals</div>
                <div style="font-size:0.9rem;color:var(--muted-foreground);margin-top:0.3rem;">{_format_banner(is_demo)}</div>
            </div>
            <div style="text-align:right;font-size:0.8rem;color:var(--muted-foreground);">Updated {datetime.now().strftime('%b %d, %Y')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if is_demo:
        st.info("Demo data is being used because no campaign dataset was found in data/raw or data/processed.")

    metric_rows = [
        [("Total campaigns", fmt_num(kpis["totalCampaigns"]), None), ("Total spend", fmt_currency(kpis["totalSpend"]), None), ("Revenue", fmt_currency(kpis["totalRevenue"]), f"{growth:+.1f}% vs. prior period"), ("Conversions", fmt_num(kpis["totalConversions"]), None)],
        [("CTR", fmt_pct(kpis["ctr"]), None), ("CPA", fmt_currency(kpis["cpa"]), None), ("ROAS", f"{kpis['roas']:.2f}x", None), ("Conversion rate", fmt_pct(kpis["cvr"]), None)],
    ]

    for row in metric_rows:
        cols = st.columns(4)
        for column, (label, value, delta) in zip(cols, row):
            with column:
                st.metric(label=label, value=value, delta=delta)

    left, right = st.columns([2, 1], gap="large")

    with left:
        st.markdown('<div class="glass-card" style="padding:1.25rem;">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:var(--font-display);font-weight:700;margin-bottom:0.25rem;">Revenue vs. Spend</div>', unsafe_allow_html=True)
        st.caption("Daily trend")

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
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(showgrid=False, title=None),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", title=None),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass-card" style="padding:1.25rem;">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:var(--font-display);font-weight:700;margin-bottom:0.25rem;">Top / Worst Campaign</div>', unsafe_allow_html=True)
        st.caption("By total revenue")
        _render_campaign_card("Best", best, True)
        if worst is not None and (best is None or worst["name"] != best["name"]):
            _render_campaign_card("Worst", worst, False)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card" style="padding:1.25rem; margin-top: 1rem;">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:var(--font-display);font-weight:700;margin-bottom:0.25rem;">Campaign performance</div>', unsafe_allow_html=True)
    st.caption("Top 10 campaigns by revenue")

    top_campaigns = by_campaign.head(10)
    if top_campaigns.empty:
        st.info("No campaign data to display.")
    else:
        bar = go.Figure()
        bar.add_trace(go.Bar(x=top_campaigns["name"], y=top_campaigns["totalRevenue"], name="Revenue", marker_color="#38bdf8"))
        bar.add_trace(go.Bar(x=top_campaigns["name"], y=top_campaigns["totalSpend"], name="Spend", marker_color="#f59e0b"))
        bar.update_layout(
            height=360,
            barmode="group",
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(tickangle=-15, title=None),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", title=None),
        )
        st.plotly_chart(bar, use_container_width=True, config={"displayModeBar": False})

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card" style="padding:1.25rem; margin-top: 1rem;">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:var(--font-display);font-weight:700;margin-bottom:0.25rem;">Campaign data</div>', unsafe_allow_html=True)
    st.caption("Aggregated by campaign")

    table = by_campaign.loc[:, ["name", "totalRevenue", "totalSpend", "totalConversions", "roas", "ctr", "cvr"]].copy()
    table["totalRevenue"] = table["totalRevenue"].map(fmt_currency)
    table["totalSpend"] = table["totalSpend"].map(fmt_currency)
    table["totalConversions"] = table["totalConversions"].map(fmt_num)
    table["roas"] = table["roas"].map(lambda value: f"{value:.2f}x")
    table["ctr"] = table["ctr"].map(fmt_pct)
    table["cvr"] = table["cvr"].map(fmt_pct)
    st.dataframe(table, use_container_width=True, hide_index=True)

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()