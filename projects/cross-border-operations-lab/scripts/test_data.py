"""Lightweight reproducibility checks for the generated dashboard aggregates."""

from __future__ import annotations

import json
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "operations_summary.json"


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    overview = data["overview"]
    assert overview["raw_rows"] > overview["clean_rows"] > 0
    assert overview["orders"] > 0 and overview["customers"] > 0 and overview["revenue"] > 0
    assert len(data["monthly"]) >= 6
    assert len(data["countries"]) >= 3
    assert len(data["segments"]) >= 3
    assert sum(row["revenue"] for row in data["countries"]) <= overview["revenue"] + 0.1
    print("PASS: operations_summary.json has valid, non-empty aggregate outputs.")


if __name__ == "__main__":
    main()
