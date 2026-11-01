#!/usr/bin/env python3
"""Rebuild data/raw/quarterly_numbers.csv from the per-report table CSVs.

One row per numeric cell.  row_label is the table row's label (including
multi-line labels), col_label is the column header inferred from pdfplumber
word positions, context is the surrounding text on the same table row/page.
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QDIR = ROOT / "data" / "company_docs" / "quarterly"
OUT = ROOT / "data" / "raw" / "quarterly_numbers.csv"
COMPANY = {"GENTING": "Genting Berhad", "GENM": "Genting Malaysia Berhad"}


def page_heading(stem: str, page: int) -> str:
    path = QDIR / "text" / f"{stem}.txt"
    if not path.exists():
        return ""
    raw = path.read_text(encoding="utf-8", errors="replace")
    parts = re.split(r"\n===== PAGE (\d+) =====\n", raw)
    d = {int(parts[i]): parts[i + 1] for i in range(1, len(parts) - 1, 2)}
    lines = [x.strip() for x in d.get(page, "").splitlines() if x.strip()]
    return " | ".join(lines[:2])[:200]


def main():
    fields = ["company", "ticker", "year", "quarter", "page", "table_index",
              "row", "col", "value_text", "value_number", "row_label", "col_label",
              "context", "strategy"]
    n = 0
    tmp = OUT.with_suffix(".csv.tmp")
    with tmp.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for path in sorted((QDIR / "tables").glob("*.csv")):
            stem = path.stem
            ticker = stem.split("_")[0]
            year = int(stem.split("_")[1][:4])
            quarter = int(stem.split("Q")[1])
            by_row = defaultdict(list)
            for r in csv.DictReader(path.open(newline="", encoding="utf-8")):
                by_row[(int(r["page"]), int(r["table_index"]), int(r["row"]))].append(r)
            for (page, ti, rno), cells in sorted(by_row.items()):
                cells.sort(key=lambda c: int(c["col"]))
                nums = [c for c in cells if c["value_number"] != ""]
                if not nums:
                    continue
                label = (nums[0].get("row_label") or "").strip()
                if not label:
                    label = " ".join(c["value_text"] for c in cells if c["value_number"] == "").strip()
                text_ctx = " ".join(c["value_text"] for c in cells if c["value_number"] == "").strip()
                ctx = " | ".join(x for x in (page_heading(stem, page), text_ctx) if x)[:500]
                for c in nums:
                    w.writerow({
                        "company": COMPANY[ticker], "ticker": ticker,
                        "year": year, "quarter": quarter,
                        "page": page, "table_index": ti, "row": rno, "col": c["col"],
                        "value_text": c["value_text"], "value_number": c["value_number"],
                        "row_label": label[:250], "col_label": c["col_label"],
                        "context": ctx, "strategy": c["strategy"],
                    })
                    n += 1
    tmp.replace(OUT)
    print(f"wrote {OUT} ({n} numeric cells)")


if __name__ == "__main__":
    main()
