"""Build aggregate, portfolio-safe data files from the UCI Online Retail data.

The original transaction file is downloaded to data/raw/ (gitignored). Only
derived aggregates used by the static demo site are written to data/processed/.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
SOURCE_URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"


def download_source() -> pd.DataFrame:
    """Download the official UCI ZIP and return its Excel table."""
    request = Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0 (portfolio educational project)"})
    with urlopen(request, timeout=60) as response:
        blob = response.read()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    archive_path = RAW_DIR / "online_retail.zip"
    archive_path.write_bytes(blob)
    with ZipFile(BytesIO(blob)) as archive:
        xlsx_names = [name for name in archive.namelist() if name.lower().endswith(".xlsx")]
        if not xlsx_names:
            raise RuntimeError("UCI archive did not include an Excel file.")
        excel_bytes = archive.read(xlsx_names[0])
    raw_path = RAW_DIR / "online_retail.xlsx"
    raw_path.write_bytes(excel_bytes)
    return pd.read_excel(BytesIO(excel_bytes), engine="openpyxl")


def rfm_segments(frame: pd.DataFrame) -> list[dict[str, int | str | float]]:
    reference = frame["InvoiceDate"].max().normalize() + pd.Timedelta(days=1)
    rfm = frame.groupby("CustomerID", as_index=False).agg(
        last_purchase=("InvoiceDate", "max"),
        frequency=("InvoiceNo", "nunique"),
        monetary=("revenue", "sum"),
    )
    rfm["recency_days"] = (reference - rfm["last_purchase"].dt.normalize()).dt.days
    rfm["recency_rank"] = pd.qcut(rfm["recency_days"].rank(method="first"), 4, labels=False) + 1
    rfm["frequency_rank"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=False) + 1
    rfm["monetary_rank"] = pd.qcut(rfm["monetary"].rank(method="first"), 4, labels=False) + 1

    def label(row: pd.Series) -> str:
        if row["recency_rank"] <= 2 and row["frequency_rank"] >= 3 and row["monetary_rank"] >= 3:
            return "High-value active"
        if row["recency_rank"] == 4:
            return "At-risk"
        if row["frequency_rank"] >= 3:
            return "Repeat purchaser"
        return "Developing"

    rfm["segment"] = rfm.apply(label, axis=1)
    summary = rfm.groupby("segment", as_index=False).agg(customers=("CustomerID", "size"), revenue=("monetary", "sum"))
    return [
        {"segment": row.segment, "customers": int(row.customers), "revenue": round(float(row.revenue), 2)}
        for row in summary.sort_values("revenue", ascending=False).itertuples(index=False)
    ]


def main() -> None:
    raw = download_source()
    required = {"InvoiceNo", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"}
    if missing := required.difference(raw.columns):
        raise ValueError(f"Missing required UCI columns: {sorted(missing)}")

    frame = raw.copy()
    frame["InvoiceNo"] = frame["InvoiceNo"].astype(str).str.strip()
    frame["InvoiceDate"] = pd.to_datetime(frame["InvoiceDate"], errors="coerce")
    frame["Quantity"] = pd.to_numeric(frame["Quantity"], errors="coerce")
    frame["UnitPrice"] = pd.to_numeric(frame["UnitPrice"], errors="coerce")
    frame["CustomerID"] = pd.to_numeric(frame["CustomerID"], errors="coerce")
    invalid = (
        frame["InvoiceNo"].str.startswith("C", na=False)
        | frame["InvoiceDate"].isna()
        | frame["Quantity"].isna()
        | frame["UnitPrice"].isna()
        | frame["CustomerID"].isna()
        | (frame["Quantity"] <= 0)
        | (frame["UnitPrice"] <= 0)
    )
    clean = frame.loc[~invalid].copy()
    clean["revenue"] = clean["Quantity"] * clean["UnitPrice"]
    clean["month"] = clean["InvoiceDate"].dt.to_period("M").astype(str)

    monthly = clean.groupby("month", as_index=False).agg(
        revenue=("revenue", "sum"), orders=("InvoiceNo", "nunique"), customers=("CustomerID", "nunique")
    )
    monthly["average_order_value"] = monthly["revenue"] / monthly["orders"]
    countries = clean.groupby("Country", as_index=False).agg(
        revenue=("revenue", "sum"), orders=("InvoiceNo", "nunique"), customers=("CustomerID", "nunique")
    ).sort_values("revenue", ascending=False).head(12)
    total_revenue = float(clean["revenue"].sum())
    countries["share_of_revenue"] = countries["revenue"] / total_revenue

    data = {
        "metadata": {
            "source_name": "UCI Online Retail",
            "source_url": "https://archive.ics.uci.edu/dataset/352/online+retail",
            "downloaded_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "currency_note": "Recorded values are source-dataset monetary units and are not converted to CNY.",
            "cleaning_rules": "Excluded cancellation invoices, missing CustomerID, invalid dates and non-positive quantity or price.",
        },
        "overview": {
            "raw_rows": int(len(raw)),
            "clean_rows": int(len(clean)),
            "excluded_rows": int(invalid.sum()),
            "date_start": clean["InvoiceDate"].min().date().isoformat(),
            "date_end": clean["InvoiceDate"].max().date().isoformat(),
            "customers": int(clean["CustomerID"].nunique()),
            "orders": int(clean["InvoiceNo"].nunique()),
            "revenue": round(total_revenue, 2),
        },
        "monthly": [
            {
                "month": row.month,
                "revenue": round(float(row.revenue), 2),
                "orders": int(row.orders),
                "customers": int(row.customers),
                "average_order_value": round(float(row.average_order_value), 2),
            }
            for row in monthly.itertuples(index=False)
        ],
        "countries": [
            {
                "country": row.Country,
                "revenue": round(float(row.revenue), 2),
                "orders": int(row.orders),
                "customers": int(row.customers),
                "share_of_revenue": round(float(row.share_of_revenue), 6),
            }
            for row in countries.itertuples(index=False)
        ],
        "segments": rfm_segments(clean),
    }
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    json_path = PROCESSED_DIR / "operations_summary.json"
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (PROCESSED_DIR / "operations_summary.js").write_text(
        "window.OPERATIONS_DATA = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8"
    )
    print(f"Built dashboard aggregates from {len(clean):,} clean transactions.")
    print(f"Wrote {json_path}")


if __name__ == "__main__":
    main()
