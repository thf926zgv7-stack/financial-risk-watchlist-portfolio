# Corporate Financial Health Watchlist

> A portfolio project that turns public SEC XBRL filing data into a transparent, rule-based financial-health watchlist.  
> 作品集项目：基于公开 SEC 财务报表数据，对企业财务健康度进行可解释的初筛与排序。

## Why this project

The initial question was practical: **if an analyst has limited review capacity, which public-company filings should be examined first?**

I built a small Python workflow that collects standard annual financial facts from the SEC Company Facts API, constructs interpretable indicators, produces a financial-health watch score, and exports both a review list and a lightweight HTML dashboard.

## What it does

- Retrieves public EDGAR XBRL facts for a selected group of U.S. non-financial companies.
- Builds leverage, liquidity, operating cash-flow coverage, revenue-growth, and ROE indicators.
- Produces a transparent 0-100 **financial watch score** and rule-based attention flags.
- Writes raw facts and results to CSV and SQLite, then generates a review dashboard.
- Retains the source URL for every observation so results can be traced back to the original public filing data.

## Design choices

This is deliberately a **screening tool**, not a default-prediction model. Public filings in this project do not contain verified default, credit-event, or audit-exception labels. Training a supervised model on invented labels would be misleading, so the project uses an explicit rule-based score instead.

The score only identifies observations that merit further review. It is **not** investment advice, a credit decision, an audit conclusion, or a judgement about any company.

## Data and snapshot

- Source: [SEC Company Facts API](https://www.sec.gov/edgar/sec-api-documentation) / EDGAR XBRL public filings.
- Coverage in the included run: 2022-2024 financial years; 40 complete company-year observations; 10 latest-year companies.
- The included outputs are a reproducible portfolio snapshot, not a live market-data service.

## Run locally

```powershell
python -m pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File .\run_real_data.ps1
```

Open `outputs/real_sec/real_sec_dashboard.html` after the run. The pipeline refreshes public data, recalculates scores, writes a local SQLite database, and regenerates the dashboard.

## Repository structure

```text
src/                         # Download, analysis, and dashboard scripts
data/real_sec/               # Included public-data snapshot
outputs/real_sec/            # Watchlist, sector summary, and HTML dashboard
run_real_data.ps1            # One-command pipeline runner
```

## Skills demonstrated

Python, Pandas, NumPy, SQLite, public API ingestion, data-quality filtering, interpretable risk scoring, CSV/HTML reporting, and reproducible project organization.

## Limitations and next steps

- The current sample is intentionally small and limited to non-financial U.S. listed companies.
- Missing or non-standard XBRL facts are excluded rather than imputed blindly.
- A next version could add a documented peer-selection policy, multi-year trend review, and a Streamlit interface.

