#!/usr/bin/env python3
"""Assemble the annual-report manifest from download, text and table artefacts."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANN = ROOT / "data" / "company_docs" / "annual"
MAN = ROOT / "data" / "company_docs" / "manifests"
DL = MAN / "annual_reports_download.csv"
TXT = MAN / "annual_reports_text.jsonl"
OUT = MAN / "annual_reports.csv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_pages(path: Path) -> int:
    out = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, timeout=60)
    for line in out.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    return 0


def main() -> int:
    dl = {r["ticker"] + "_" + r["year"]: r for r in csv.DictReader(DL.open())}
    tx = {}
    if TXT.exists():
        for line in TXT.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                tx[r["ticker"] + "_" + str(r["year"])] = r
    rows = []
    for key, d in sorted(dl.items(), key=lambda kv: (kv[1]["ticker"], int(kv[1]["year"]))):
        ticker, year = d["ticker"], int(d["year"])
        pdf = ANN / f"{ticker}_AR_{year}.pdf"
        t = tx.get(key, {})
        tabjson = ANN / "tables" / f"{ticker}_AR_{year}.json"
        tab = {}
        if tabjson.exists():
            try:
                tab = json.loads(tabjson.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                tab = {}
        pages = pdf_pages(pdf) if pdf.exists() else 0
        size = pdf.stat().st_size if pdf.exists() else 0
        digest = sha256(pdf) if pdf.exists() else ""
        notes = d.get("notes", "")
        status = d.get("download_status", "")
        if ticker == "GENTING" and year == 2011:
            status = "downloaded_alternate"
            notes = ("official genting.com link returns a truncated 65-page file ending mid-"
                     "directors' report; replaced with the full 170-page report assembled from the two "
                     "Bursa Malaysia attachments filed 23 May 2012 (announcement 1265884, "
                     "attachments 157583+157584, sha256 fab380...ed5167); original kept in "
                     "annual/alternates/")
        if pages and pages <= 20:
            notes = (notes + " | " if notes else "") + "page count <=20"
        if t.get("extraction_status") not in (None, "ok"):
            notes = (notes + " | " if notes else "") + f"text: {t.get('extraction_status')}"
        rows.append({
            "company": d["company"], "ticker": ticker, "year": year,
            "doc_type": "annual_report", "url": d["url"],
            "file": str(pdf.relative_to(ROOT)), "bytes": size, "sha256": digest,
            "pages": pages, "text_chars": t.get("text_chars", ""),
            "download_status": status,
            "text_extraction_status": t.get("extraction_status", ""),
            "chars_per_page": t.get("chars_per_page", ""),
            "table_count": tab.get("n_tables", ""),
            "table_rows": tab.get("n_rows", ""),
            "table_cells": tab.get("n_cells", ""),
            "notes": notes,
        })
    fields = ["company", "ticker", "year", "doc_type", "url", "file", "bytes",
              "sha256", "pages", "text_chars", "download_status",
              "text_extraction_status", "chars_per_page", "table_count",
              "table_rows", "table_cells", "notes"]
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {len(rows)} rows to {OUT}")
    print("missing sha:", sum(1 for r in rows if not r["sha256"]))
    print("missing pages:", sum(1 for r in rows if not r["pages"]))
    print("pages<=20:", sum(1 for r in rows if r["pages"] and r["pages"] <= 20))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
