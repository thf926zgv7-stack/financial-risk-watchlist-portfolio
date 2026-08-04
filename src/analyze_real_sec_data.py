"""Analyze real SEC filing data without inventing a default/credit-risk label."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "real_sec" / "financial_real_sec.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "real_sec"
DATABASE_PATH = PROJECT_ROOT / "data" / "real_sec" / "sec_financial_health.sqlite"


def scale_higher_is_attention(series: pd.Series, low: float, high: float) -> pd.Series:
    return ((series - low) / (high - low)).clip(0, 1)


def scale_lower_is_attention(series: pd.Series, low: float, high: float) -> pd.Series:
    return (1 - (series - low) / (high - low)).clip(0, 1)


def attention_level(score: float) -> str:
    if score >= 65:
        return "High watch"
    if score >= 40:
        return "Medium watch"
    return "Low watch"


def build_flags(row: pd.Series) -> str:
    flags = []
    if row["debt_ratio"] >= 0.70:
        flags.append("high leverage")
    if row["current_ratio"] < 1.00:
        flags.append("current ratio below 1")
    if row["cashflow_to_liabilities"] < 0.05:
        flags.append("weak operating cash flow coverage")
    if row["revenue_growth"] < 0:
        flags.append("revenue decline")
    if row["roe"] < 0:
        flags.append("negative ROE")
    return "; ".join(flags) if flags else "no rule-based attention flag"


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError("Run src/fetch_sec_real_data.py before this script.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(DATA_PATH)
    frame = frame.sort_values(["ticker", "fiscal_year"]).copy()

    frame["debt_ratio"] = frame["liabilities_usd"] / frame["assets_usd"]
    frame["current_ratio"] = frame["current_assets_usd"] / frame["current_liabilities_usd"]
    frame["cashflow_to_liabilities"] = frame["operating_cashflow_usd"] / frame["liabilities_usd"]
    frame["revenue_growth"] = frame.groupby("ticker")["revenue_usd"].pct_change()
    frame["roe"] = frame["net_income_usd"] / frame["equity_usd"]
    frame["net_profit_margin"] = frame["net_income_usd"] / frame["revenue_usd"]

    # The first available year has no prior-year revenue for a growth comparison.
    # It remains in the raw data but is excluded from score ranking.
    analysis = frame.dropna(subset=["revenue_growth"]).copy()
    components = {
        "leverage": 0.30 * scale_higher_is_attention(analysis["debt_ratio"], 0.35, 0.85),
        "liquidity": 0.20 * scale_lower_is_attention(analysis["current_ratio"], 0.80, 2.20),
        "cashflow": 0.22 * scale_lower_is_attention(analysis["cashflow_to_liabilities"], 0.02, 0.35),
        "growth": 0.13 * scale_lower_is_attention(analysis["revenue_growth"], -0.20, 0.22),
        "profitability": 0.15 * scale_lower_is_attention(analysis["roe"], -0.03, 0.18),
    }
    analysis["financial_watch_score"] = (sum(components.values()) * 100).round(1)
    analysis["attention_level"] = analysis["financial_watch_score"].map(attention_level)
    analysis["attention_flags"] = analysis.apply(build_flags, axis=1)
    analysis["review_priority"] = np.select(
        [analysis["attention_level"] == "High watch", analysis["attention_level"] == "Medium watch"],
        ["Priority 1 - manual context review", "Priority 2 - monitor"],
        default="No priority flag",
    )

    latest_year = int(analysis["fiscal_year"].max())
    latest = analysis[analysis["fiscal_year"] == latest_year].sort_values("financial_watch_score", ascending=False)
    industry_summary = (
        analysis.groupby(["fiscal_year", "industry"], as_index=False)
        .agg(
            observations=("ticker", "size"),
            average_watch_score=("financial_watch_score", "mean"),
            high_watch_share=("attention_level", lambda values: (values == "High watch").mean()),
        )
        .sort_values(["fiscal_year", "average_watch_score"], ascending=[True, False])
    )
    industry_summary[["average_watch_score", "high_watch_share"]] = industry_summary[
        ["average_watch_score", "high_watch_share"]
    ].round(3)

    analysis.to_csv(OUTPUT_DIR / "real_financial_health_results.csv", index=False, encoding="utf-8-sig")
    latest.to_csv(OUTPUT_DIR / f"{latest_year}_watch_list.csv", index=False, encoding="utf-8-sig")
    industry_summary.to_csv(OUTPUT_DIR / "industry_watch_summary.csv", index=False, encoding="utf-8-sig")

    with sqlite3.connect(DATABASE_PATH) as connection:
        frame.to_sql("sec_raw_financials", connection, if_exists="replace", index=False)
        analysis.to_sql("financial_health_results", connection, if_exists="replace", index=False)
        industry_summary.to_sql("industry_watch_summary", connection, if_exists="replace", index=False)

    top_latest = latest[["ticker", "company_name", "industry", "financial_watch_score", "attention_level", "attention_flags"]].head(10)
    table = [
        "| Ticker | Company | Industry | Watch score | Attention level | Rule-based flags |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for _, row in top_latest.iterrows():
        table.append(
            f"| {row['ticker']} | {row['company_name']} | {row['industry']} | {row['financial_watch_score']:.1f} | {row['attention_level']} | {row['attention_flags']} |"
        )

    summary = [
        "# Real-data financial-health watch list",
        "",
        "> This is an educational, rule-based screening exercise built from public SEC XBRL facts as filed. It is not investment advice, a credit decision, an audit conclusion, or a prediction of default.",
        "",
        f"- Source: SEC Company Facts API; the exact API URL for each observation is stored in `financial_real_sec.csv`.",
        f"- Complete company-year observations downloaded: {len(frame)}.",
        f"- Scored observations (years with a prior-year revenue comparison): {len(analysis)}.",
        f"- Latest fiscal year in the current sample: {latest_year}.",
        f"- The score is a transparent blend of leverage, liquidity, operating cash flow coverage, revenue growth and ROE. It deliberately does **not** use a supervised prediction model because this data set has no verified credit-event label.",
        "",
        f"## {latest_year} highest watch-score observations",
        "",
        *table,
        "",
        "## Interpretation boundary",
        "",
        "A high score is only a prompt to read the company filing, debt maturity profile, cash-flow note and business context. It must not be treated as a conclusion about a company’s financial condition.",
    ]
    (OUTPUT_DIR / "real_data_summary.md").write_text("\n".join(summary), encoding="utf-8")
    print(f"Analyzed {len(analysis)} real SEC company-year observations. Results are in {OUTPUT_DIR}.")


if __name__ == "__main__":
    main()
