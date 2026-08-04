from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd


def build_revenue_spend_chart(by_date: pd.DataFrame, base_layout: dict, text_color: str, grid_color: str) -> go.Figure:
    """Build the revenue-vs-spend trend chart for the dashboard."""
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
    layout = base_layout.copy()
    layout.update(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=text_color, size=11),
        ),
        xaxis=dict(showgrid=False, title=None, tickfont=dict(color=text_color, size=10)),
        yaxis=dict(showgrid=True, gridcolor=grid_color, title=None, tickfont=dict(color=text_color, size=10)),
    )
    fig.update_layout(layout)
    return fig


def build_campaign_performance_chart(by_campaign: pd.DataFrame, base_layout: dict, text_color: str, grid_color: str) -> go.Figure:
    """Build the campaign performance grouped bar chart."""
    campaign_perf = by_campaign.copy().head(10)
    spend_col = "spend_usd" if "spend_usd" in campaign_perf.columns else ("totalSpend" if "totalSpend" in campaign_perf.columns else "spend")
    revenue_col = "totalRevenue" if "totalRevenue" in campaign_perf.columns else "revenue"
    label_col = "display_name" if "display_name" in campaign_perf.columns else ("name" if "name" in campaign_perf.columns else "campaign_id")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=campaign_perf[label_col], y=campaign_perf[revenue_col], name="Revenue", marker_color="#1d8cff", width=0.36))
    fig.add_trace(go.Bar(x=campaign_perf[label_col], y=campaign_perf[spend_col], name="Spend", marker_color="#f59e0b", width=0.36))

    layout = base_layout.copy()
    layout.update(
        height=340,
        barmode="group",
        bargap=0.28,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5, font=dict(color=text_color, size=11)),
        xaxis=dict(showgrid=False, title=None, tickangle=-15, tickfont=dict(color=text_color, size=10)),
        yaxis=dict(showgrid=True, gridcolor=grid_color, title=None, tickfont=dict(color=text_color, size=10)),
    )
    fig.update_layout(layout)
    return fig


def build_signup_activation_chart(by_date: pd.DataFrame, base_layout: dict, text_color: str, grid_color: str) -> go.Figure:
    """Build the signups vs activations trend chart."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=by_date["date"], y=by_date["signups"], name="Signups", mode="lines+markers", line=dict(color="#38bdf8", width=2.5), marker=dict(size=5)))
    fig.add_trace(go.Scatter(x=by_date["date"], y=by_date["activations_7d"], name="Activations", mode="lines+markers", line=dict(color="#10b981", width=2.5), marker=dict(size=5)))

    layout = base_layout.copy()
    layout.update(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=text_color, size=10)),
        xaxis=dict(showgrid=False, title=None, tickfont=dict(color=text_color, size=10)),
        yaxis=dict(showgrid=True, gridcolor=grid_color, title=None, tickfont=dict(color=text_color, size=10)),
    )
    fig.update_layout(layout)
    return fig
