#!/usr/bin/env python3
"""Download PDF attachments for selected Bursa announcements.

Reads data/raw/company_filings.jsonl, picks financial-results announcements (and
optionally keyword-matched corporate-action announcements), downloads each PDF
attachment from disclosure.bursamalaysia.com, and writes a manifest.

Usage:
  python scripts/download_filing_pdfs.py --filter financial
  python scripts/download_filing_pdfs.py --filter corporate
"""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests

ROOT = Path(__file__).resolve().parents[1]
FILINGS = ROOT / "data" / "raw" / "company_filings.jsonl"
DOCS = ROOT / "data" / "company_docs"
QDIR = DOCS / "quarterly"
ADIR = DOCS / "announcements"
MANIFEST = DOCS / "pdf_manifest.json"

CORPORATE_KEYWORDS = [
    "RIGHTS ISSUE", "TAKE-OVER", "TAKEOVER", "TENDER OFFER", "MEDIUM TERM NOTES",
    "MTN", "SUBORDINATED", "DIVIDEND", "SHARE BUY-BACK", "BUY-BACK", "CIRCULAR",
    "ANNUAL REPORT", "PRIVATISATION", "ACQUISITION", "DISPOSAL",
]


def safe(name: str) -> str:
    name = re.sub(r"\.pdf$", "", name, flags=re.I)
    name = re.sub(r"[^A-Za-z0-9._ -]+", "", name).strip().replace(" ", "_")
    return re.sub(r"_{2,}", "_", name)[:90] or "attachment"


def load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text())
    return {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--filter", choices=["financial", "corporate", "all"], default="financial")
    ap.add_argument("--max", type=int, default=0)
    args = ap.parse_args()

    QDIR.mkdir(parents=True, exist_ok=True)
    ADIR.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()
    s = requests.Session(impersonate="chrome")
    last = 0.0
    downloaded = skipped = failed = 0

    records = [json.loads(line) for line in FILINGS.open() if line.strip()]
    todo = []
    for rec in records:
        raw = rec.get("raw") or {}
        cat = (raw.get("category") or "").lower()
        title = (rec.get("title") or "").upper()
        atts = raw.get("attachments") or []
        if not atts:
            continue
        is_fin = "financial results" in cat or "quarterly rpt" in title.lower()
        blob = " ".join([
            title,
            (raw.get("subject") or "").upper(),
            (raw.get("description") or "").upper()[:2000],
        ])
        is_corp = any(k in blob for k in CORPORATE_KEYWORDS)
        if args.filter == "financial" and not is_fin:
            continue
        if args.filter == "corporate" and not (is_corp and not is_fin):
            continue
        todo.append(rec)

    print(f"{len(todo)} announcements with attachments selected")
    for n, rec in enumerate(todo, 1):
        raw = rec["raw"]
        date = (raw.get("date_announced") or "")[:11]
        try:
            d = datetime.strptime(date, "%d %b %Y").strftime("%Y-%m-%d")
        except ValueError:
            d = datetime.fromtimestamp(rec["created_utc"], timezone.utc).strftime("%Y-%m-%d")
        outdir = QDIR / rec["channel"] if "financial results" in (raw.get("category") or "").lower() else ADIR
        outdir.mkdir(parents=True, exist_ok=True)
        for i, att in enumerate(raw["attachments"], 1):
            key = f"{rec['native_id']}:{i}"
            if key in manifest and Path(manifest[key]["path"]).exists():
                skipped += 1
                continue
            fname = f"{d}_{rec['native_id'].split(':')[-1]}_{i}_{safe(att['name'])}.pdf"
            path = outdir / fname
            for attempt in range(5):
                wait = 1.05 - (time.time() - last)
                if wait > 0:
                    time.sleep(wait)
                last = time.time()
                try:
                    r = s.get(att["url"], timeout=180)
                except Exception as exc:  # noqa: BLE001
                    print(f"  ! {exc} {att['url']}")
                    time.sleep(5)
                    continue
                if r.status_code == 200 and r.content[:4] == b"%PDF":
                    path.write_bytes(r.content)
                    manifest[key] = {
                        "native_id": rec["native_id"],
                        "ticker": rec["channel"],
                        "title": rec["title"],
                        "date": d,
                        "name": att["name"],
                        "url": att["url"],
                        "local": str(path.relative_to(ROOT)),
                        "bytes": len(r.content),
                    }
                    downloaded += 1
                    print(f"  [{n}/{len(todo)}] {path.name} ({len(r.content)//1024} KB)", flush=True)
                    break
                if r.status_code in (429, 500, 502, 503, 504):
                    time.sleep(10 * (attempt + 1))
                    continue
                print(f"  ! HTTP {r.status_code} {att['url']}")
                failed += 1
                break
            if args.max and downloaded >= args.max:
                break
        MANIFEST.write_text(json.dumps(manifest, indent=1))
        if args.max and downloaded >= args.max:
            break

    MANIFEST.write_text(json.dumps(manifest, indent=1))
    print(f"downloaded={downloaded} cached={skipped} failed={failed} manifest={MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
