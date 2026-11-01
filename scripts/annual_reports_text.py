#!/usr/bin/env python3
"""Extract full text of every annual report, page-preserving (form-feed separated)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "data" / "company_docs" / "annual"
TXT_DIR = PDF_DIR / "text"
META = ROOT / "data" / "company_docs" / "manifests" / "annual_reports_text.jsonl"
TXT_DIR.mkdir(parents=True, exist_ok=True)


def pdf_pages(path: Path) -> int:
    out = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, timeout=120)
    m = re.search(r"^Pages:\s+(\d+)", out.stdout, re.M)
    return int(m.group(1)) if m else 0


def main() -> int:
    files = sorted(PDF_DIR.glob("*_AR_*.pdf"))
    print(f"{len(files)} PDFs")
    rows = []
    for i, pdf in enumerate(files, 1):
        ticker, year = re.match(r"([A-Z]+)_AR_(\d{4})", pdf.name).groups()
        txt = TXT_DIR / f"{ticker}_AR_{year}.txt"
        pages = pdf_pages(pdf)
        status = "ok"
        err = ""
        try:
            proc = subprocess.run(
                ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf), str(txt)],
                capture_output=True, text=True, timeout=900,
            )
            if proc.returncode != 0:
                status = "pdftotext_error"
                err = (proc.stderr or "")[:300]
        except Exception as exc:  # noqa: BLE001
            status = "pdftotext_error"
            err = str(exc)[:300]
        text = txt.read_text(encoding="utf-8", errors="replace") if txt.exists() else ""
        page_texts = text.split("\f")
        if page_texts and page_texts[-1].strip() == "":
            page_texts = page_texts[:-1]
        chars = len(text)
        per_page = [len(p) for p in page_texts]
        avg = chars / pages if pages else 0
        minp = min(per_page) if per_page else 0
        low = sum(1 for c in per_page if c < 200)
        if status == "ok" and (pages == 0 or chars == 0):
            status = "no_text"
        elif status == "ok" and avg < 500:
            status = "low_text"
        row = {
            "ticker": ticker, "year": int(year), "file": str(pdf.relative_to(ROOT)),
            "text_file": str(txt.relative_to(ROOT)), "pages": pages,
            "text_chars": chars, "chars_per_page": round(avg, 1),
            "min_page_chars": minp, "pages_under_200_chars": low,
            "extraction_status": status, "notes": err,
        }
        rows.append(row)
        print(f"[{i:2d}/{len(files)}] {ticker} {year}: {pages:4d}p {chars:9d} chars "
              f"{avg:7.1f}/p {status}")
    with META.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    bad = [r for r in rows if r["extraction_status"] != "ok"]
    print(f"written {len(rows)}; non-ok: {len(bad)}")
    for r in bad:
        print("  ", r["ticker"], r["year"], r["extraction_status"], r["chars_per_page"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
