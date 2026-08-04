"""Fetch a small, reproducible real-data sample from the SEC Company Facts API.

The SEC API contains facts as filed by registrants.  This script deliberately
keeps the sample small, makes one request per company, and records the exact
source URL and download time in the output file.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data" / "real_sec" / "financial_real_sec.csv"
YEARS = (2021, 2022, 2023, 2024)

# Non-financial operating companies are selected because their balance-sheet
# ratios are more comparable than those of banks and insurers.
COMPANIES = [
    ("0000320193", "AAPL", "Apple Inc.", "Technology"),
    ("0000789019", "MSFT", "Microsoft Corporation", "Technology"),
    ("0001018724", "AMZN", "Amazon.com, Inc.", "Consumer & Technology"),
    ("0001652044", "GOOGL", "Alphabet Inc.", "Technology"),
    ("0001326801", "META", "Meta Platforms, Inc.", "Technology"),
    ("0001045810", "NVDA", "NVIDIA Corporation", "Technology"),
    ("0000104169", "WMT", "Walmart Inc.", "Consumer"),
    ("0000021344", "KO", "The Coca-Cola Company", "Consumer"),
    ("0000080424", "PG", "The Procter & Gamble Company", "Consumer"),
    ("0000077476", "PEP", "PepsiCo, Inc.", "Consumer"),
    ("0000320187", "NKE", "NIKE, Inc.", "Consumer"),
    ("0000063908", "MCD", "McDonald's Corporation", "Consumer"),
    ("0000018230", "CAT", "Caterpillar Inc.", "Industrial"),
    ("0000354950", "HD", "The Home Depot, Inc.", "Consumer"),
    ("0000909832", "COST", "Costco Wholesale Corporation", "Consumer"),
]

TAG_CANDIDATES = {
    "assets_usd": ("Assets",),
    "liabilities_usd": ("Liabilities",),
    "current_assets_usd": ("AssetsCurrent",),
    "current_liabilities_usd": ("LiabilitiesCurrent",),
    "operating_cashflow_usd": ("NetCashProvidedByUsedInOperatingActivities",),
    "revenue_usd": ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet"),
    "net_income_usd": ("NetIncomeLoss", "ProfitLoss"),
    "equity_usd": ("StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"),
}


def fetch_json(url: str) -> dict:
    request = Request(
        url,
        headers={
            "User-Agent": "FinancialDataLearningProject/1.0",
        },
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def annual_usd_value(company_facts: dict, tags: tuple[str, ...], fiscal_year: int) -> float | None:
    """Return the latest annual 10-K fact for one standard US-GAAP concept."""
    gaap_facts = company_facts.get("facts", {}).get("us-gaap", {})
    for tag in tags:
        units = gaap_facts.get(tag, {}).get("units", {})
        observations = units.get("USD", [])
        candidates = [
            item
            for item in observations
            if item.get("form") == "10-K"
            and item.get("fp") == "FY"
            and str(item.get("fy")) == str(fiscal_year)
            and item.get("val") is not None
        ]
        if candidates:
            chosen = max(candidates, key=lambda item: (item.get("filed", ""), item.get("end", "")))
            return float(chosen["val"])
    return None


def main() -> None:
    rows: list[dict] = []
    downloaded_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    failures: list[str] = []

    for cik, ticker, expected_name, industry in COMPANIES:
        source_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        try:
            company_facts = fetch_json(source_url)
        except Exception as error:  # Records a transparent failure rather than silently inventing data.
            failures.append(f"{ticker}: {error}")
            continue

        company_name = company_facts.get("entityName", expected_name)
        for fiscal_year in YEARS:
            row = {
                "ticker": ticker,
                "company_name": company_name,
                "industry": industry,
                "fiscal_year": fiscal_year,
                "cik": cik,
                "source_url": source_url,
                "downloaded_at_utc": downloaded_at,
            }
            for column, tags in TAG_CANDIDATES.items():
                row[column] = annual_usd_value(company_facts, tags, fiscal_year)
            if all(pd.notna(value) for column, value in row.items() if column in TAG_CANDIDATES):
                rows.append(row)
            else:
                failures.append(f"{ticker} FY{fiscal_year}: incomplete standard US-GAAP facts")
        time.sleep(0.12)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    log_path = OUTPUT_PATH.parent / "download_log.txt"
    log_lines = [
        "Source: SEC Company Facts API (official public EDGAR XBRL data)",
        f"Downloaded at UTC: {downloaded_at}",
        f"Requested companies: {len(COMPANIES)}",
        f"Complete annual observations written: {len(rows)}",
        "",
        "Skipped/incomplete observations:",
        *failures,
    ]
    log_path.write_text("\n".join(log_lines), encoding="utf-8")

    if not rows:
        print("No complete records were downloaded. The diagnostic log follows:")
        print("\n".join(failures[:10]))
        raise RuntimeError("No SEC records were downloaded. Check download_log.txt for details.")

    frame = pd.DataFrame(rows).sort_values(["ticker", "fiscal_year"])
    numeric_columns = list(TAG_CANDIDATES)
    frame[numeric_columns] = frame[numeric_columns].astype(float)
    frame.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"Wrote {len(frame)} real SEC company-year observations to {OUTPUT_PATH}.")
    print(f"See {log_path} for any incomplete observations.")


if __name__ == "__main__":
    main()
