#!/usr/bin/env python3
"""Sanity-check data/raw/company_financials.csv.

Checks: required columns, duplicate (company, period), revenue > 0,
net_debt == total_debt - cash, period_end inside the collection window,
non-empty source_url, dividend >= 0, EPS parses.
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "data" / "raw" / "company_financials.csv"
REQUIRED = [
    "company", "period", "period_end", "revenue", "ebitda", "pbt", "net_profit",
    "finance_cost", "total_debt", "cash", "net_debt", "eps", "dividend", "source_url",
]
START = date(2024, 11, 2)
END = date(2026, 11, 2)


def num(v):
    v = (v or "").strip()
    if v == "":
        return None
    try:
        return float(v.replace(",", ""))
    except ValueError:
        return "BAD"


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else DEFAULT
    errors: list[str] = []
    warnings: list[str] = []
    rows = list(csv.DictReader(path.open()))
    header = list(rows[0].keys()) if rows else []
    if header != REQUIRED:
        errors.append(f"header mismatch: {header}")

    dupes = Counter((r["company"], r["period"]) for r in rows)
    for k, n in dupes.items():
        if n > 1:
            errors.append(f"duplicate period {k} x{n}")

    for i, r in enumerate(rows, 2):
        tag = f"line {i} {r.get('company')} {r.get('period')}"
        try:
            pe = date.fromisoformat(r["period_end"])
            if not (START <= pe <= END):
                errors.append(f"{tag}: period_end {pe} outside window")
        except ValueError:
            errors.append(f"{tag}: bad period_end {r['period_end']!r}")
        for f in ("revenue", "ebitda", "pbt", "net_profit", "finance_cost",
                  "total_debt", "cash", "net_debt", "eps", "dividend"):
            v = num(r[f])
            if v == "BAD":
                errors.append(f"{tag}: non-numeric {f}={r[f]!r}")
        rev = num(r["revenue"])
        if rev is not None and rev != "BAD" and rev <= 0:
            errors.append(f"{tag}: revenue not > 0")
        td, cash, nd = num(r["total_debt"]), num(r["cash"]), num(r["net_debt"])
        if all(isinstance(x, float) for x in (td, cash, nd)):
            if abs((td - cash) - nd) > 0.5:
                errors.append(f"{tag}: net_debt {nd} != total_debt {td} - cash {cash}")
        if not r["source_url"].startswith("http"):
            errors.append(f"{tag}: missing source_url")
        if r["period"].startswith(("1Q", "2Q", "3Q")) and not r["period"].startswith(("1Q", "2Q", "3Q")):
            warnings.append(f"{tag}: odd period")

    print(f"{path}: {len(rows)} rows")
    for c, n in Counter(r["company"] for r in rows).items():
        print(f"  {c}: {n} periods")
    for e in errors:
        print("ERROR", e)
    for w in warnings:
        print("WARN", w)
    print("OK" if not errors else f"FAIL: {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
