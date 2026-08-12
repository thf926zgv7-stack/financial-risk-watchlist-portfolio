# Cross-Border Operations Lab

> A portfolio-ready, browser-based decision tool that connects real public retail transaction data with a transparent four-factor cross-border operating scenario simulator.

中文版：面向跨境电商、商业分析、数据运营与金融科技岗位的公开数据作品。它用匿名公开零售交易数据展示经营看板，并用四个可调参数演示汇率、物流、定价和采购成本如何影响贡献利润。

## What problem does it solve?

Operating teams often need two different views at the same time:

1. **What happened?** Explore historical monthly sales, market concentration, customer segments, and repeat-purchase signals using public data.
2. **What could happen next?** Stress-test a simple operating plan when foreign exchange, logistics, local price, or product cost changes.

This project deliberately keeps the two views separate. The dashboard is based on a real, anonymous public dataset; the scenario calculator uses visible illustrative assumptions and is **not** presented as any company's forecast.

## Live features

- Public-data dashboard: cleaned transaction count, date range, monthly revenue trend, top markets, and RFM-style customer segments.
- Country selector: inspect a selected market's recorded revenue, order count, customers, and share of tracked revenue.
- Four-parameter simulator: adjust FX, logistics cost, price, and product cost; immediately see revenue, contribution profit, margin, and pressure level.
- Scenario CSV download: exports the exact inputs and results used in the browser.
- No login, API key, user upload, or personal information required.

## Data and integrity boundary

### Historical dashboard data

- Source: [UCI Machine Learning Repository - Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail).
- The source records anonymous transactions from a UK-based non-store retailer. This repository stores only derived aggregates for the demo site, not the original transaction file.
- The processing script excludes cancellation invoices, missing customer IDs, and non-positive quantities or prices. Every rule is visible in `scripts/build_data.py`.

### Scenario data

- Market unit price, baseline order volume, logistics cost, platform fee, and price elasticity are illustrative user-editable assumptions.
- FX, logistics, price, and product-cost controls are scenario inputs, not reported data from an employer, client, or listed company.
- Outputs are for education and portfolio demonstration; they are not investment advice, financial projections, audit conclusions, or operating recommendations for a real company.

## How to run locally

No package installation is needed to view the included dashboard and simulator.

```powershell
Set-Location '15_跨境经营冲击推演器_GitHub'
python -m http.server 8000
```

Open `http://localhost:8000` in a browser.

To refresh the public-data aggregates from UCI (requires Python with `pandas` and `openpyxl`):

```powershell
python scripts/build_data.py
python scripts/test_data.py
```

## Repository structure

```text
index.html                         # static interactive dashboard + simulator
scripts/build_data.py              # download, clean, aggregate public retail data
scripts/test_data.py               # reproducibility checks for generated data
data/processed/operations_summary.json
data/processed/operations_summary.js
src/calculator.py                  # original transparent Python simulator logic
tests/test_calculator.py           # unit tests for simulator logic
```

## Portfolio talking points

> Built a browser-based cross-border operations lab using anonymized public retail data. Implemented a reproducible Python pipeline for transaction cleaning, monthly/country KPIs and RFM-style segmentation, then paired it with a transparent four-factor scenario simulator for FX, logistics, pricing and COGS sensitivity analysis. Clearly separated historical public-data findings from illustrative operating assumptions.

## Suggested next iteration

- Add a user-supplied CSV schema validator that runs only in the browser, without uploading data.
- Add scenario version comparison in local browser storage.
- Add a documented metric dictionary and experiment-design template for real operations teams.

## License and attribution

Code in this repository is released under the MIT License. Source data remains subject to its original UCI terms and attribution requirements.
