# Cross-Border Operations Lab | 跨境经营冲击推演器

> A browser-based decision tool connecting public retail transaction data with a transparent four-factor cross-border operating scenario simulator.

面向跨境电商、商业分析、数据运营与金融科技岗位的公开数据作品：用匿名零售交易数据展示经营看板，并用四个可调参数演示汇率、物流、定价和采购成本如何影响贡献利润。

## What problem does it solve?

Operating teams need two distinct views at once: what happened historically, and what could happen under a defined shock. This project keeps these views rigorously separate:

1. **Historical view**: monthly sales, market concentration and RFM-style customer segments using public data.
2. **Scenario view**: a simplified operating plan stressed by FX, logistics, local price and product-cost changes.

## Live features

- Public-data dashboard: cleaned transaction count, date range, monthly revenue trend, top markets and customer segments.
- Country selector: recorded revenue, orders, customers and revenue share for a selected market.
- Four-parameter simulator: immediate revenue, contribution-profit, margin and pressure changes.
- CSV download: exports the exact scenario inputs and outputs shown in the browser.
- No login, API key, upload or personal information is required.

## Data and integrity boundary

### Historical dashboard data

- Source: [UCI Machine Learning Repository — Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail).
- The source contains anonymous transactions from a UK-based non-store retailer. This project publishes only derived aggregates, never the original transaction file.
- `scripts/build_data.py` visibly removes cancellations, missing customer IDs and non-positive quantities/prices.

### Scenario data

- Unit price, order volume, logistics cost, platform fee and price elasticity are illustrative, editable assumptions.
- FX, logistics, price and COGS controls are scenario inputs, not data from an employer, client or listed company.
- Results are for education and portfolio demonstration, not investment advice, audit conclusions or real-company forecasts.

## Run locally

```powershell
Set-Location '15_跨境经营冲击推演器_GitHub'
python -m http.server 8000
```

Open `http://localhost:8000`. To refresh the public-data aggregates (requires `pandas` and `openpyxl`):

```powershell
python scripts/build_data.py
python scripts/test_data.py
python -m unittest discover -s tests -p 'test_*.py'
```

## Repository structure

```text
index.html                          # Static interactive dashboard and simulator
scripts/build_data.py               # Download, clean and aggregate public retail data
data/processed/operations_summary.* # Reproducible aggregate snapshot for the app
src/calculator.py                   # Transparent scenario-calculation logic
tests/test_calculator.py            # Unit checks for the calculation logic
```

## Portfolio talking point

> Built a browser-based cross-border operations lab using anonymized public retail data. Implemented a reproducible Python pipeline for transaction cleaning, monthly/country KPIs and RFM-style segmentation, then paired it with a transparent four-factor scenario simulator for FX, logistics, pricing and COGS sensitivity analysis. Clearly separated historical public-data findings from illustrative operating assumptions.

## License and attribution

Code is released under the MIT License. Source data remains subject to its original UCI terms and attribution requirements.
