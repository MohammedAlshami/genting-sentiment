#!/usr/bin/env python3
"""Build the long annual-report numbers CSV directly from table JSONs.

Every numeric token in every table cell becomes one row. `cell_text` preserves
the original cell verbatim, including units, percentages and footnotes.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "data" / "company_docs" / "annual" / "tables"
OUT = ROOT / "data" / "raw" / "annual_report_numbers.csv"
OUT.parent.mkdir(parents=True, exist_ok=True)

COMPANY = {"GENTING": "Genting Berhad", "GENM": "Genting Malaysia Berhad"}
TOKEN = re.compile(r"\(?-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\)?%?")
DATE = re.compile(r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b")


def tokens(text: str):
    s = DATE.sub(" ", text)
    for m in TOKEN.finditer(s):
        tok = m.group(0)
        raw = tok.replace(",", "").replace("%", "")
        neg = raw.startswith("(") and raw.endswith(")")
        raw = raw.strip("()")
        try:
            v = float(raw)
        except ValueError:
            continue
        if neg:
            v = -v
        yield tok, v


def has_number(text: str) -> bool:
    return any(True for _ in tokens(text))


def main() -> int:
    files = sorted(TABLES.glob("*_AR_*.json"))
    n = 0
    per_ticker = {}
    with OUT.open("w", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        w.writerow(["company", "ticker", "year", "page", "table_index", "method",
                    "row_index", "col_index", "value_text", "value_number",
                    "cell_text", "row_label", "col_label", "caption"])
        for f in files:
            m = re.match(r"([A-Z]+)_AR_(\d{4})", f.name)
            if not m:
                continue
            ticker, year = m.group(1), int(m.group(2))
            d = json.loads(f.read_text(encoding="utf-8"))
            for tb in d.get("tables", []):
                rows = tb.get("rows", [])
                # Header rows are those before the first row containing a number.
                header_end = 0
                for ri, row in enumerate(rows[:8]):
                    if any(has_number(c) for c in row):
                        header_end = ri
                        break
                else:
                    header_end = min(2, len(rows))
                col_labels = []
                for j in range(tb.get("n_cols", 0)):
                    lab = ""
                    for ri in range(header_end - 1, -1, -1):
                        if j < len(rows[ri]):
                            c = rows[ri][j]
                            if c and not has_number(c):
                                lab = c
                                break
                    col_labels.append(lab)
                last_label = ""
                for ri, row in enumerate(rows):
                    # label = leading text cells before the first number
                    labs = []
                    for c in row:
                        if has_number(c):
                            break
                        if c:
                            labs.append(c)
                    if labs:
                        last_label = " ".join(labs)
                    row_label = last_label
                    for j, cell in enumerate(row):
                        if not cell:
                            continue
                        for tok, val in tokens(cell):
                            w.writerow([
                                COMPANY.get(ticker, ticker), ticker, year,
                                tb["page"], tb["table_index"], tb["method"],
                                ri, j, tok, val, cell,
                                row_label[:250],
                                col_labels[j][:120] if j < len(col_labels) else "",
                                tb.get("caption", "")[:300],
                            ])
                            n += 1
            per_ticker[ticker] = per_ticker.get(ticker, 0) + 1
    print(f"wrote {n:,} numeric tokens to {OUT}")
    for k, v in sorted(per_ticker.items()):
        print(f"  {k}: {v} report files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
