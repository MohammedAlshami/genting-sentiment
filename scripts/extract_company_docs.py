#!/usr/bin/env python3
"""Extract text from company PDFs (annual + quarterly reports).

Writes alongside each PDF:
  <stem>.txt        full text, page-delimited with "=== PAGE n ===" markers
  <stem>.pages.json {"pages": n, "chars": n, "starts": [char offset per page]}
  <stem>.index.json page numbers for key statement headings (annual reports)
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "data" / "company_docs"

HEADINGS = {
    "income_statement": [
        r"CONSOLIDATED STATEMENTS? OF PROFIT OR LOSS",
        r"CONSOLIDATED INCOME STATEMENTS?",
    ],
    "financial_position": [
        r"CONSOLIDATED STATEMENTS? OF FINANCIAL POSITION",
        r"CONSOLIDATED BALANCE SHEETS?",
    ],
    "cash_flow": [r"CONSOLIDATED STATEMENTS? OF CASH FLOWS?"],
    "changes_in_equity": [r"CONSOLIDATED STATEMENTS? OF CHANGES IN EQUITY"],
    "segment": [r"SEGMENT (INFORMATION|REPORTING)", r"OPERATING SEGMENTS"],
    "borrowings": [r"BORROWINGS", r"MATURITY PROFILE", r"DEBT MATURITY"],
    "dividends": [r"DIVIDENDS?", r"DISTRIBUTION TO SHAREHOLDERS"],
    "major_shareholders": [
        r"SUBSTANTIAL SHAREHOLDERS",
        r"ANALYSIS OF SHAREHOLDINGS",
        r"THIRTY LARGEST",
    ],
    "directors": [r"BOARD OF DIRECTORS", r"DIRECTORS' PROFILE", r"PROFILE OF DIRECTORS"],
    "related_party": [r"RELATED PARTY", r"RELATED-PARTY"],
    "five_year": [r"FIVE[- ]YEAR", r"FINANCIAL HIGHLIGHTS", r"GROUP FINANCIAL HIGHLIGHTS"],
}


def extract(pdf: Path, force: bool = False) -> dict:
    txt_path = pdf.with_suffix(".txt")
    meta_path = pdf.with_suffix(".pages.json")
    if txt_path.exists() and meta_path.exists() and not force:
        return json.loads(meta_path.read_text())

    reader = PdfReader(str(pdf))
    parts = []
    starts = []
    pos = 0
    hits: dict[str, list[int]] = {k: [] for k in HEADINGS}
    for i, page in enumerate(reader.pages, 1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:  # noqa: BLE001
            text = f"[EXTRACTION ERROR: {exc}]"
        text = text.replace("\x00", "")
        block = f"\n\n=== PAGE {i} ===\n\n{text}"
        starts.append(pos)
        parts.append(block)
        pos += len(block)
        up = re.sub(r"\s+", " ", text.upper())
        for key, pats in HEADINGS.items():
            if any(re.search(p, up) for p in pats):
                hits[key].append(i)

    full = "".join(parts).lstrip("\n")
    txt_path.write_text(full, encoding="utf-8")
    meta = {"pdf": pdf.name, "pages": len(reader.pages), "chars": len(full), "starts": starts}
    meta_path.write_text(json.dumps(meta, indent=1))
    pdf.with_suffix(".index.json").write_text(json.dumps(hits, indent=1))
    print(f"  {pdf.name}: {len(reader.pages)} pages, {len(full):,} chars -> {txt_path.name}")
    return meta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    paths = args.paths or sorted(DOCS.glob("*.pdf"))
    for p in paths:
        if not p.exists():
            print(f"missing {p}")
            continue
        extract(p, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
