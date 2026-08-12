"""Build reproducible event-window metrics from public FRED CSV endpoints."""
from __future__ import annotations
import json
from pathlib import Path
from urllib.request import urlopen
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"; OUT = ROOT / "data" / "processed"
SERIES = {
    "sp500": ("SP500", "S&P 500", "pct"),
    "oil": ("DCOILWTICO", "WTI 原油", "pct"),
    "vix": ("VIXCLS", "VIX 波动率指数", "pct"),
    "treasury10y": ("DGS10", "10年期美债收益率", "bps"),
}
EVENTS = [
    ("pandemic", "世卫组织宣布新冠疫情为全球大流行", "2020-03-11", "公共卫生风险"),
    ("ukraine", "俄乌冲突全面升级", "2022-02-24", "地缘政治风险"),
    ("fed_liftoff", "美联储本轮加息启动", "2022-03-16", "货币政策"),
    ("svb", "硅谷银行被关闭", "2023-03-10", "金融稳定"),
]

def load_series(key, fred_id):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={fred_id}"
    raw = urlopen(url, timeout=30).read()
    (RAW / f"{fred_id}.csv").write_bytes(raw)
    frame = pd.read_csv(RAW / f"{fred_id}.csv")
    frame.columns = ["date", "value"]
    frame["date"] = pd.to_datetime(frame["date"])
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    return frame.dropna().reset_index(drop=True)

def row_for_event(frame, event_date, kind):
    date = pd.Timestamp(event_date)
    idx = frame.index[frame.date <= date][-1]
    before, after = max(0, idx - 5), min(len(frame) - 1, idx + 5)
    start, end = float(frame.loc[idx, "value"]), float(frame.loc[after, "value"])
    change = (end / start - 1) * 100 if kind == "pct" else (end - start) * 100
    window = frame.loc[before:after, ["date", "value"]].copy()
    window["date"] = window.date.dt.strftime("%Y-%m-%d")
    return round(change, 2), window.to_dict("records")

def main():
    RAW.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
    loaded = {key: load_series(key, meta[0]) for key, meta in SERIES.items()}
    events = []
    for event_id, label, date, category in EVENTS:
        movements, windows = {}, {}
        for key, (_, series_label, kind) in SERIES.items():
            change, window = row_for_event(loaded[key], date, kind)
            movements[key] = {"label": series_label, "unit": "%" if kind == "pct" else "bp", "change": change}
            windows[key] = window
        events.append({"id": event_id, "label": label, "date": date, "category": category, "movements": movements, "windows": windows})
    payload = {"title": "Macro Event Shock Map", "window": "事件日后 5 个可得交易日变化；展示前后各 5 个交易日", "series": {k:{"label":v[1],"unit":"%" if v[2]=="pct" else "bp"} for k,v in SERIES.items()}, "events": events}
    (OUT / "event_study_data.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "event_study_data.js").write_text("window.EVENT_STUDY_DATA = " + json.dumps(payload, ensure_ascii=False) + ";", encoding="utf-8")
    print(f"Built {len(events)} events × {len(SERIES)} series.")
if __name__ == "__main__": main()
