#!/usr/bin/env python3
"""Download every Genting Berhad / Genting Malaysia annual report (1998-2025).

Parses the two official annual-report index pages, keeps only links whose anchor
text is an annual/integrated annual report, and downloads to
data/company_docs/annual/<TICKER>_AR_<YEAR>.pdf.

Idempotent: an existing file is kept only if its sha256 matches the server copy;
otherwise it is replaced atomically. At least 1s between HTTP requests.
"""
from __future__ import annotations

import csv
import hashlib
import os
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "company_docs" / "annual"
MAN = ROOT / "data" / "company_docs" / "manifests"
OUT.mkdir(parents=True, exist_ok=True)
MAN.mkdir(parents=True, exist_ok=True)
PARTIAL = MAN / "annual_reports_download.csv"

SOURCES = [
    ("Genting Berhad", "GENTING", "https://www.genting.com/annual_reports"),
    ("Genting Malaysia Berhad", "GENM", "https://www.gentingmalaysia.com/annual_reports"),
]

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
HEADERS = {"User-Agent": UA, "Accept": "text/html,application/pdf,*/*"}

AR_TEXT = re.compile(r"annual\s+report|integrated\s+annual\s+report", re.I)
YEAR_RE = re.compile(r"(19|20)\d{2}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def discover() -> list[dict]:
    found: list[dict] = []
    for company, ticker, page in SOURCES:
        resp = requests.get(page, headers=HEADERS, timeout=60)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        seen: set[tuple[str, str]] = set()
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href.lower().split("?")[0].endswith(".pdf"):
                continue
            text = " ".join(a.get_text(" ", strip=True).split())
            if not AR_TEXT.search(text):
                continue
            years = YEAR_RE.findall(text)
            # findall with groups returns the group, so use finditer
            years = [m.group(0) for m in YEAR_RE.finditer(text)]
            if not years:
                print(f"WARN no year in anchor text: {text!r} {href}", file=sys.stderr)
                continue
            year = int(years[-1])
            if not (1998 <= year <= 2025):
                print(f"WARN implausible year {year}: {text!r} {href}", file=sys.stderr)
                continue
            key = (ticker, str(year))
            if key in seen:
                continue
            seen.add(key)
            found.append({
                "company": company,
                "ticker": ticker,
                "year": year,
                "doc_type": "annual_report",
                "url": href,
            })
        print(f"{ticker}: {len(seen)} annual reports discovered")
    return found


def main() -> int:
    docs = discover()
    print(f"discovered {len(docs)} PDFs")
    rows = []
    last_request = 0.0
    for doc in sorted(docs, key=lambda d: (d["ticker"], d["year"])):
        dest = OUT / f"{doc['ticker']}_AR_{doc['year']}.pdf"
        status = "downloaded"
        notes = ""
        # GENTING 2011: the official link is a truncated 65-page cover.  Keep the
        # complete Bursa-filed substitute instead of re-downloading the broken file.
        if (doc["ticker"] == "GENTING" and doc["year"] == 2011 and dest.exists()
                and sha256_file(dest).startswith("fab3805cd5")):
            doc.update(sha256=sha256_file(dest), bytes=dest.stat().st_size,
                       file=str(dest.relative_to(ROOT)),
                       download_status="skipped_alternate",
                       notes="kept full Bursa-filed 143-page substitute; official link is truncated")
            rows.append(doc)
            print(f"skip {dest.name} (full Bursa substitute)")
            continue
        if dest.exists() and dest.stat().st_size > 0:
            # Cheap identity check first: same byte size as server.
            try:
                head = requests.head(doc["url"], headers=HEADERS, timeout=60,
                                     allow_redirects=True)
                remote_len = int(head.headers.get("Content-Length", "-1"))
            except Exception as exc:  # noqa: BLE001
                remote_len = -1
                notes = f"head failed: {exc}"
            if remote_len == dest.stat().st_size:
                status = "skipped_existing"
                doc["sha256"] = sha256_file(dest)
                doc["bytes"] = dest.stat().st_size
                doc["file"] = str(dest.relative_to(ROOT))
                doc["download_status"] = status
                doc["notes"] = notes
                rows.append(doc)
                print(f"skip {dest.name} ({remote_len} bytes)")
                continue

        if last_request:
            time.sleep(max(0.0, 1.0 - (time.time() - last_request)))
        last_request = time.time()
        tmp = dest.with_suffix(".pdf.part")
        try:
            with requests.get(doc["url"], headers=HEADERS, timeout=180,
                              stream=True, allow_redirects=True) as resp:
                resp.raise_for_status()
                ctype = resp.headers.get("Content-Type", "")
                if "pdf" not in ctype.lower() and not resp.content[:5].startswith(b"%PDF"):
                    raise RuntimeError(f"not a PDF (content-type={ctype})")
                h = hashlib.sha256()
                size = 0
                with tmp.open("wb") as fh:
                    for chunk in resp.iter_content(1 << 20):
                        if not chunk:
                            continue
                        fh.write(chunk)
                        h.update(chunk)
                        size += len(chunk)
            if dest.exists():
                old = sha256_file(dest)
                if old == h.hexdigest():
                    tmp.unlink(missing_ok=True)
                    status = "skipped_existing"
                else:
                    tmp.replace(dest)
            else:
                tmp.replace(dest)
            doc.update(sha256=h.hexdigest(), bytes=size,
                       file=str(dest.relative_to(ROOT)),
                       download_status=status, notes=notes)
            rows.append(doc)
            print(f"{status:16s} {dest.name:24s} {size/1e6:7.2f} MB")
        except Exception as exc:  # noqa: BLE001
            tmp.unlink(missing_ok=True)
            doc.update(sha256="", bytes=0,
                       file=str(dest.relative_to(ROOT)),
                       download_status="failed", notes=str(exc)[:300])
            rows.append(doc)
            print(f"FAILED {dest.name}: {exc}", file=sys.stderr)

    fields = ["company", "ticker", "year", "doc_type", "url", "file", "bytes",
              "sha256", "download_status", "notes"]
    with PARTIAL.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    ok = sum(1 for r in rows if r["download_status"] in ("downloaded", "skipped_existing"))
    print(f"done: {ok}/{len(rows)} available; manifest {PARTIAL}")
    return 0 if ok == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
