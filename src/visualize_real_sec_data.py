"""Build a dependency-free HTML dashboard for the real SEC-data version."""

from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "real_sec"


def bar(value: float, maximum: float = 100) -> str:
    width = max(0, min(100, value / maximum * 100))
    color = "#B42318" if value >= 65 else "#B54708" if value >= 40 else "#1570EF"
    return f'<div class="bar-track"><div class="bar" style="width:{width:.1f}%;background:{color}"></div></div>'


def main() -> None:
    results_path = OUTPUT_DIR / "real_financial_health_results.csv"
    if not results_path.exists():
        raise FileNotFoundError("Run src/analyze_real_sec_data.py before this script.")

    results = pd.read_csv(results_path)
    latest_year = int(results["fiscal_year"].max())
    latest = results[results["fiscal_year"] == latest_year].sort_values(
        "financial_watch_score", ascending=False
    )

    rows = []
    for _, row in latest.iterrows():
        rows.append(
            "<tr>"
            f"<td>{escape(row['ticker'])}</td><td>{escape(row['company_name'])}</td><td>{escape(row['industry'])}</td>"
            f"<td>{row['financial_watch_score']:.1f}{bar(float(row['financial_watch_score']))}</td>"
            f"<td>{escape(row['attention_level'])}</td><td>{escape(row['attention_flags'])}</td>"
            "</tr>"
        )

    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>SEC real-data financial-health dashboard</title>
<style>body{{font-family:Arial,sans-serif;background:#F8FAFC;color:#182230;margin:0;padding:36px;line-height:1.45}}main{{max-width:1180px;margin:auto}}h1{{margin-bottom:4px}}.note{{background:#FFF7ED;border-left:4px solid #F79009;padding:14px 16px;border-radius:4px}}.cards{{display:flex;gap:16px;margin:20px 0}}.card{{background:white;border:1px solid #E4E7EC;border-radius:8px;padding:16px;min-width:170px}}.num{{font-size:26px;font-weight:700;color:#175CD3}}table{{border-collapse:collapse;background:white;width:100%;font-size:13px}}th,td{{padding:10px;border:1px solid #EAECF0;vertical-align:top;text-align:left}}th{{background:#F2F4F7}}.bar-track{{height:7px;border-radius:5px;background:#EAECF0;margin-top:5px;min-width:120px}}.bar{{height:7px;border-radius:5px}}</style></head><body><main>
<h1>Real-data financial-health watch list</h1><p>Latest fiscal year: {latest_year} | Source: SEC Company Facts API</p>
<div class="note"><strong>Interpretation boundary:</strong> These are real public filing facts, but this dashboard is an educational rule-based screen only. It is not investment advice, a credit decision, an audit conclusion or a default prediction.</div>
<div class="cards"><div class="card"><div>Latest-year companies</div><div class="num">{len(latest)}</div></div><div class="card"><div>High-watch observations</div><div class="num">{(latest['attention_level'] == 'High watch').sum()}</div></div><div class="card"><div>Data range</div><div class="num">{results['fiscal_year'].min()}-{latest_year}</div></div></div>
<h2>Latest-year watch list</h2><table><thead><tr><th>Ticker</th><th>Company</th><th>Industry</th><th>Watch score</th><th>Attention level</th><th>Rule-based flags</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<p>For source URLs, raw reported values and calculations, open <code>financial_real_sec.csv</code> and <code>real_financial_health_results.csv</code>.</p>
</main></body></html>'''
    (OUTPUT_DIR / "real_sec_dashboard.html").write_text(html, encoding="utf-8")
    print(f"Dashboard written to {OUTPUT_DIR / 'real_sec_dashboard.html'}.")


if __name__ == "__main__":
    main()
