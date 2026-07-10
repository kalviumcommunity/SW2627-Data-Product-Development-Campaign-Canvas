from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


DATA_ROOT = Path(__file__).resolve().parents[2] / "data"
_COLUMN_ALIASES = {
    "date": ("date", "sync_date", "day", "timestamp"),
    "campaign": ("campaign", "campaign_name", "utm_campaign", "name", "campaign_id"),
    "spend": ("spend", "spend_usd", "cost", "total_spend"),
    "revenue": ("revenue", "total_revenue", "sales"),
    "conversions": ("conversions", "activated_users", "signups", "leads"),
    "clicks": ("clicks",),
    "impressions": ("impressions",),
}


def _build_demo_data() -> pd.DataFrame:
    rng = np.random.default_rng(7)
    dates = pd.date_range("2026-06-01", periods=14, freq="D")
    campaigns = [
        "Search - Brand",
        "Search - Nonbrand",
        "Paid Social - Prospecting",
        "Paid Social - Retargeting",
        "YouTube - Awareness",
        "Display - Remarketing",
        "Email - Nurture",
        "Affiliate - Partners",
    ]

    rows: list[dict[str, object]] = []
    for date in dates:
        for index, campaign in enumerate(campaigns):
            spend = float(rng.uniform(120, 900) * (1 + index * 0.08))
            clicks = int(rng.uniform(120, 1_900) * (1 + index * 0.05))
            impressions = int(clicks * rng.uniform(9.0, 20.0))
            conversions = int(max(1, clicks * rng.uniform(0.02, 0.12)))
            revenue = float(spend * rng.uniform(1.1, 4.8))

            rows.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "campaign": campaign,
                    "spend": round(spend, 2),
                    "revenue": round(revenue, 2),
                    "conversions": conversions,
                    "clicks": clicks,
                    "impressions": impressions,
                }
            )

    return pd.DataFrame(rows)


def _normalize_frame(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    rename_map: dict[str, str] = {}

    for target, aliases in _COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in normalized.columns:
                rename_map[alias] = target
                break

    normalized = normalized.rename(columns=rename_map)

    for required in ("date", "campaign", "spend", "revenue", "conversions", "clicks", "impressions"):
        if required not in normalized.columns:
            normalized[required] = 0

    normalized = normalized.loc[:, ["date", "campaign", "spend", "revenue", "conversions", "clicks", "impressions"]]
    normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    normalized["campaign"] = normalized["campaign"].astype(str).fillna("Unknown campaign")

    for numeric in ("spend", "revenue", "conversions", "clicks", "impressions"):
        normalized[numeric] = pd.to_numeric(normalized[numeric], errors="coerce").fillna(0)

    normalized = normalized.dropna(subset=["date"])
    normalized["conversions"] = normalized["conversions"].astype(int)
    normalized["clicks"] = normalized["clicks"].astype(int)
    normalized["impressions"] = normalized["impressions"].astype(int)
    return normalized.reset_index(drop=True)


def load_campaign_data() -> tuple[pd.DataFrame, bool]:
    candidate_dirs = [DATA_ROOT / "processed", DATA_ROOT / "raw"]
    for directory in candidate_dirs:
        if not directory.exists():
            continue

        for path in sorted(directory.glob("*")):
            if path.suffix.lower() not in {".csv", ".parquet", ".xlsx", ".xls"}:
                continue

            try:
                if path.suffix.lower() == ".csv":
                    frame = pd.read_csv(path)
                elif path.suffix.lower() == ".parquet":
                    frame = pd.read_parquet(path)
                else:
                    frame = pd.read_excel(path)
            except Exception:
                continue

            if not frame.empty:
                return _normalize_frame(frame), False

    return _build_demo_data(), True


def compute_kpis(frame: pd.DataFrame) -> dict[str, float]:
    total_spend = float(frame["spend"].sum())
    total_revenue = float(frame["revenue"].sum())
    total_clicks = float(frame["clicks"].sum())
    total_impressions = float(frame["impressions"].sum())
    total_conversions = float(frame["conversions"].sum())

    return {
        "totalCampaigns": float(frame["campaign"].nunique()),
        "totalSpend": total_spend,
        "totalRevenue": total_revenue,
        "totalConversions": total_conversions,
        "ctr": total_clicks / total_impressions if total_impressions else 0.0,
        "cpa": total_spend / total_conversions if total_conversions else 0.0,
        "roas": total_revenue / total_spend if total_spend else 0.0,
        "cvr": total_conversions / total_clicks if total_clicks else 0.0,
    }


def aggregate_by(frame: pd.DataFrame, key: str) -> pd.DataFrame:
    grouped = (
        frame.groupby(key, dropna=False, as_index=False)
        .agg(
            totalSpend=("spend", "sum"),
            totalRevenue=("revenue", "sum"),
            totalConversions=("conversions", "sum"),
            clicks=("clicks", "sum"),
            impressions=("impressions", "sum"),
        )
        .rename(columns={key: "name"})
    )

    grouped["ctr"] = grouped.apply(lambda row: row["clicks"] / row["impressions"] if row["impressions"] else 0.0, axis=1)
    grouped["cpa"] = grouped.apply(lambda row: row["totalSpend"] / row["totalConversions"] if row["totalConversions"] else 0.0, axis=1)
    grouped["roas"] = grouped.apply(lambda row: row["totalRevenue"] / row["totalSpend"] if row["totalSpend"] else 0.0, axis=1)
    grouped["cvr"] = grouped.apply(lambda row: row["totalConversions"] / row["clicks"] if row["clicks"] else 0.0, axis=1)

    return grouped.sort_values(["totalRevenue", "totalSpend", "name"], ascending=[False, False, True]).reset_index(drop=True)


def fmt_currency(value: float) -> str:
    return f"${value:,.0f}" if abs(value) >= 1_000 else f"${value:,.2f}"


def fmt_num(value: float) -> str:
    return f"{value:,.0f}"


def fmt_pct(value: float) -> str:
    return f"{value * 100:.1f}%"