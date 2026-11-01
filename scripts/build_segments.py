#!/usr/bin/env python3
"""Build data/raw/company_segments.csv from the quarterly results press releases.

Segment revenue in RM million for the individual quarter (first numeric column of
the summary table). Segment names follow the company's own labels.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_quarterly import pairs, txt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw"
MANIFEST = json.loads((ROOT / "data" / "company_docs" / "pdf_manifest.json").read_text())

SEGMENTS = {
    "GENTING": ["Malaysia", "Singapore", "UK and Egypt", "US and Bahamas",
                "Oil Palm Plantation", "Downstream Manufacturing", "Power", "Property",
                "Oil & Gas", "Investments & Others"],
    "GENM": ["Malaysia", "United Kingdom and Egypt",
             "United States of America and Bahamas", "Property", "Investments & others"],
}

DISPLAY = {
    ("GENTING", "Malaysia"): "Leisure & Hospitality - Malaysia",
    ("GENTING", "Singapore"): "Leisure & Hospitality - Singapore",
    ("GENTING", "UK and Egypt"): "Leisure & Hospitality - UK and Egypt",
    ("GENTING", "US and Bahamas"): "Leisure & Hospitality - US and Bahamas",
    ("GENTING", "Oil Palm Plantation"): "Plantation - Oil Palm Plantation",
    ("GENTING", "Downstream Manufacturing"): "Plantation - Downstream Manufacturing",
    ("GENM", "Malaysia"): "Leisure & Hospitality - Malaysia",
    ("GENM", "United Kingdom and Egypt"): "Leisure & Hospitality - UK and Egypt",
    ("GENM", "United States of America and Bahamas"): "Leisure & Hospitality - US and Bahamas",
    ("GENM", "Property"): "Properties",
    ("GENM", "Investments & others"): "Investments & Others",
}

NUM = r"\(?-?[\d,]+(?:\.\d+)?\)?"


def first_number(line: str) -> float | None:
    m = re.search(NUM, line)
    if not m:
        return None
    s = m.group(0).replace(",", "")
    neg = s.startswith("(") and s.endswith(")")
    v = float(s.strip("()"))
    return -v if neg else v


def period_from_title(title: str) -> tuple[str, str]:
    m = re.search(r"ended\s+(\d{2})/(\d{2})/(\d{4})", title)
    day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return f"{(month - 1) // 3 + 1}Q{str(year)[-2:]}", f"{year:04d}-{month:02d}-{day:02d}"


def segment_block(text: str) -> list[str]:
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if re.match(r"^\s*Revenue\s*$", l)), None)
    end = next((i for i, l in enumerate(lines) if "Adjusted EBITDA" in l and i > (start or 0)), None)
    if start is None or end is None:
        return []
    return lines[start:end]


def main() -> int:
    rows = []
    for ticker in ("GENTING", "GENM"):
        for key, report, press in pairs(ticker):
            title = next(v["title"] for v in MANIFEST.values()
                         if v["local"].endswith(press.stem + ".pdf"))
            period, period_end = period_from_title(title)
            if period_end < "2024-11-02":
                continue
            block = segment_block(txt(press))
            for line in block:
                clean = re.sub(r"^\s*-\s*", "", line).strip()
                for seg in SEGMENTS[ticker]:
                    if clean.lower().startswith(seg.lower() + " ") or clean.lower() == seg.lower():
                        rest = clean[len(seg):].strip()
                        # skip total rows masquerading as a segment (value must look numeric)
                        val = first_number(rest)
                        if val is not None:
                            rows.append({
                                "company": ticker,
                                "period": period,
                                "period_end": period_end,
                                "segment": DISPLAY.get((ticker, seg), seg),
                                "revenue": round(val, 1),
                                "source_url": next(v["url"] for v in MANIFEST.values()
                                                   if v["local"].endswith(press.stem + ".pdf")),
                            })
                        break
    # de-duplicate (segment may appear twice in a section)
    seen = set()
    unique = []
    for r in rows:
        k = (r["company"], r["period"], r["segment"])
        if k in seen:
            continue
        seen.add(k)
        unique.append(r)
    unique.sort(key=lambda r: (r["company"], r["period_end"], r["segment"]))
    path = OUT / "company_segments.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["company", "period", "period_end", "segment",
                                           "revenue", "source_url"])
        w.writeheader()
        w.writerows(unique)
    print(f"wrote {len(unique)} segment rows")
    for r in unique:
        print(f"{r['company']:8} {r['period']:5} {r['segment']:38} {r['revenue']:9.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
