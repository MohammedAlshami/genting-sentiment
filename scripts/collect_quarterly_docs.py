#!/usr/bin/env python3
"""Enumerate and download every quarterly-report PDF on the two Genting IR pages.

Outputs (owned by the company-docs collector only):
  data/company_docs/quarterly/<TICKER>_<YEAR>Q<Q>.pdf
  data/company_docs/manifests/quarterly_reports.csv
  data/company_docs/manifests/ir_pages/<company>_quarterly.html

Usage:
  python scripts/collect_quarterly_docs.py enumerate
  python scripts/collect_quarterly_docs.py download
  python scripts/collect_quarterly_docs.py status
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "data" / "company_docs"
QDIR = DOCS / "quarterly"
MAN = DOCS / "manifests"
IRDIR = MAN / "ir_pages"
MANIFEST = MAN / "quarterly_reports.csv"

PAGES = {
    "GENTING": {
        "company": "Genting Berhad",
        "url": "https://www.genting.com/quarterly-reports",
    },
    "GENM": {
        "company": "Genting Malaysia Berhad",
        "url": "https://www.gentingmalaysia.com/quarterly-report",
    },
}

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
HEADERS = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}

FIELDS = [
    "company", "ticker", "year", "quarter", "url", "file",
    "bytes", "sha256", "pages", "text_chars", "status",
]


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def fetch(url: str, tries: int = 4) -> requests.Response:
    last = None
    for attempt in range(1, tries + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=60, allow_redirects=True)
            if r.status_code == 200:
                return r
            last = f"HTTP {r.status_code}"
            if r.status_code in (403, 429, 500, 502, 503, 504):
                time.sleep(3 * attempt)
                continue
            break
        except Exception as exc:  # noqa: BLE001
            last = str(exc)
            time.sleep(3 * attempt)
    raise RuntimeError(f"fetch failed: {url}: {last}")


def parse_year_quarter(title: str) -> tuple[int, int] | None:
    # "2nd Quarterly Report 2026" / "4th Quarterly Financial Report 2025"
    m = re.search(r"(\d)(?:st|nd|rd|th)\s+Quarterly", title, re.I)
    y = re.search(r"\b(20\d{2})\b", title)
    if not m or not y:
        return None
    q = int(m.group(1))
    if not 1 <= q <= 4:
        return None
    return int(y.group(1)), q


def enumerate_reports() -> list[dict]:
    MAN.mkdir(parents=True, exist_ok=True)
    IRDIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for ticker, meta in PAGES.items():
        log(f"fetching IR page for {ticker}: {meta['url']}")
        r = fetch(meta["url"])
        raw_path = IRDIR / f"{ticker}_quarterly.html"
        raw_path.write_bytes(r.content)
        log(f"  saved {raw_path.relative_to(ROOT)} ({len(r.content)} bytes)")
        soup = BeautifulSoup(r.text, "lxml")
        found: dict[tuple[int, int], dict] = {}
        for div in soup.find_all("div", class_="container"):
            h = div.find("h4")
            if not h:
                continue
            title = h.get_text(" ", strip=True)
            if "Quarterly" not in title:
                continue
            yq = parse_year_quarter(title)
            if not yq:
                continue
            a = div.find("a", href=True)
            href = a["href"].strip() if a else ""
            if href in ("", "#", "javascript:void(0)"):
                href = ""
            year, quarter = yq
            cand = {
                "company": meta["company"],
                "ticker": ticker,
                "year": year,
                "quarter": quarter,
                "url": href,
                "title": title,
            }
            # Prefer a real link over the placeholder row.
            if (year, quarter) not in found or (not found[(year, quarter)]["url"] and href):
                found[(year, quarter)] = cand
        log(f"  parsed {len(found)} report slots")
        rows.extend(found.values())

    rows.sort(key=lambda x: (x["ticker"], -x["year"], -x["quarter"]))
    with MANIFEST.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS + ["title"])
        w.writeheader()
        for row in rows:
            out = {k: row.get(k, "") for k in FIELDS}
            out["file"] = f"data/company_docs/quarterly/{row['ticker']}_{row['year']}Q{row['quarter']}.pdf"
            out["status"] = "pending" if row["url"] else "no_url"
            out["title"] = row.get("title", "")
            w.writerow(out)
    log(f"wrote {MANIFEST.relative_to(ROOT)} with {len(rows)} rows")
    missing = [r for r in rows if not r["url"]]
    if missing:
        log(f"  slots without URL: {[(r['ticker'], r['year'], r['quarter']) for r in missing]}")
    return rows


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_pages(path: Path) -> int:
    from pypdf import PdfReader

    try:
        return len(PdfReader(str(path)).pages)
    except Exception:  # noqa: BLE001
        return 0


def read_manifest() -> list[dict]:
    with MANIFEST.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_manifest(rows: list[dict]) -> None:
    tmp = MANIFEST.with_suffix(".csv.tmp")
    with tmp.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS + ["title"])
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in FIELDS + ["title"]})
    tmp.replace(MANIFEST)


def download_all(delay: float = 1.15) -> None:
    QDIR.mkdir(parents=True, exist_ok=True)
    rows = read_manifest()
    total = len(rows)
    last_request = 0.0
    for i, row in enumerate(rows, 1):
        ticker, year, quarter = row["ticker"], int(row["year"]), int(row["quarter"])
        dest = ROOT / row["file"]
        if not row["url"]:
            row["status"] = "no_url"
            continue
        if dest.exists() and dest.stat().st_size > 20_000:
            if row.get("sha256") and row.get("pages"):
                row["status"] = "ok"
                log(f"[{i}/{total}] {dest.name} already present ({row.get('pages')}p) - skip")
                continue
            row["bytes"] = dest.stat().st_size
            row["sha256"] = sha256_file(dest)
            row["pages"] = pdf_pages(dest)
            row["status"] = "ok" if int(row["pages"] or 0) > 0 else "bad_pdf"
            write_manifest(rows)
            log(f"[{i}/{total}] {dest.name} present, hashed ({row['pages']}p)")
            continue

        wait = delay - (time.time() - last_request)
        if wait > 0:
            time.sleep(wait)
        try:
            log(f"[{i}/{total}] GET {row['url']}")
            r = fetch(row["url"])
            last_request = time.time()
            if not r.content.startswith(b"%PDF"):
                row["status"] = "not_pdf"
                log(f"  ERROR not a PDF: first bytes {r.content[:40]!r}")
                write_manifest(rows)
                continue
            tmp = dest.with_suffix(".pdf.part")
            tmp.write_bytes(r.content)
            tmp.replace(dest)
            row["bytes"] = dest.stat().st_size
            row["sha256"] = sha256_file(dest)
            row["pages"] = pdf_pages(dest)
            row["status"] = "ok" if int(row["pages"] or 0) > 0 else "bad_pdf"
            log(f"  saved {dest.name} {row['bytes']/1024:.0f} KB, {row['pages']} pages")
        except Exception as exc:  # noqa: BLE001
            row["status"] = f"error: {exc}"[:180]
            log(f"  ERROR {exc}")
        write_manifest(rows)
    ok = sum(1 for r in rows if r["status"] == "ok")
    log(f"done: {ok}/{total} ok")
    for r in rows:
        if r["status"] != "ok":
            log(f"  {r['ticker']} {r['year']}Q{r['quarter']}: {r['status']}")


def status() -> None:
    rows = read_manifest()
    from collections import Counter

    print(f"rows={len(rows)}")
    print("by ticker:", Counter(r["ticker"] for r in rows))
    print("by status:", Counter(r["status"] for r in rows))
    print("pages total:", sum(int(r["pages"] or 0) for r in rows))
    missing = [r for r in rows if r["status"] != "ok"]
    for r in missing:
        print("  MISSING", r["ticker"], r["year"], r["quarter"], r["status"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["enumerate", "download", "all", "status"])
    ap.add_argument("--delay", type=float, default=1.15)
    args = ap.parse_args()
    if args.stage in ("enumerate", "all"):
        enumerate_reports()
    if args.stage in ("download", "all"):
        download_all(delay=args.delay)
    if args.stage == "status":
        status()


if __name__ == "__main__":
    main()
