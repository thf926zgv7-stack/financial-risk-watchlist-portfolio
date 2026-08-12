import json
from pathlib import Path
p = Path(__file__).resolve().parents[1] / "data/processed/event_study_data.json"
d = json.loads(p.read_text(encoding="utf-8"))
assert len(d["events"]) == 4
assert set(d["series"]) == {"sp500", "oil", "vix", "treasury10y"}
assert all(len(e["movements"]) == 4 and e["windows"] for e in d["events"])
print("PASS: event-study data structure is valid")
