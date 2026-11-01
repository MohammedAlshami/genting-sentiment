#!/usr/bin/env python3
"""Cross-check data/raw/company_financials.csv against the Bursa summary tables
embedded in the announcement bodies of data/raw/company_filings.jsonl.

The Bursa "Summary of Key Financial Information" is in RM'000 for all 16 results
announcements, so values are divided by 1,000 before comparison with the CSV.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "raw" / "company_financials.csv"
FILINGS = ROOT / "data" / "raw" / "company_filings.jsonl"

LABELS = {
    "revenue": "Revenue",
    "pbt": "Profit/(loss) before tax",
    "net_profit": "Profit/(loss) for the period",
    "eps": "Basic earnings/(loss) per share (Subunit)",
    "dividend": "Proposed/Declared dividend per share (Subunit)",
}


def first_num(body: str, label: str):
    i = body.find(label)
    if i < 0:
        return None
    m = re.search(r"-?[\d,]+(?:\.\d+)?", body[i + len(label):])
    if not m:
        return None
    return float(m.group(0).replace(",", ""))


def period_from_title(title: str):
    m = re.search(r"ended\s+(\d{2})/(\d{2})/(\d{4})", title)
    if not m:
        return None
    month, year = int(m.group(2)), int(m.group(3))
    return f"{(month - 1) // 3 + 1}Q{str(year)[-2:]}"


def main() -> int:
    rows = {(r["company"], r["period"]): r for r in csv.DictReader(CSV.open())}
    errors = checked = 0
    for line in FILINGS.open():
        rec = json.loads(line)
        if (rec["raw"].get("category") or "") != "Financial Results":
            continue
        period = period_from_title(rec["title"])
        key = (rec["channel"], period)
        if key not in rows:
            continue
        row = rows[key]
        checked += 1
        for field, label in LABELS.items():
            raw = first_num(rec["body"], label)
            if raw is None:
                print(f"MISSING {key} {field}")
                errors += 1
                continue
            expected = raw / 1000 if field in ("revenue", "pbt", "net_profit") else raw
            got = float(row[field])
            tol = 0.05 if field in ("revenue", "pbt", "net_profit") else 0.005
            if abs(expected - got) > tol:
                print(f"MISMATCH {key} {field}: bursa={expected} csv={got}")
                errors += 1
    print(f"checked {checked} result announcements; mismatches={errors}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
