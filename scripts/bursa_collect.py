#!/usr/bin/env python3
"""Bonus collector: Bursa Malaysia company announcements for GENTING (3182) and GENM (4715)."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup
from curl_cffi import requests as cffi_requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from news_lib import DATA, clean_text, http_get  # noqa: E402

API = "https://www.bursamalaysia.com/api/v1/announcements/search"
VIEW = "https://disclosure.bursamalaysia.com/FileAccess/viewHtml?e={ann_id}"
DETAIL = (
    "https://www.bursamalaysia.com/market_information/announcements/"
    "company_announcement/announcement_details?ann_id={ann_id}"
)
DATE_RE = re.compile(r"(\d{1,2})\s+(\w{3})\s+(\d{4})")
COMPANIES = [(3182, "GENTING", "Genting Berhad"), (4715, "GENM", "Genting Malaysia Berhad")]
MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1
)}


def announcement_text(ann_id: str) -> str:
    r = http_get(VIEW.format(ann_id=ann_id), timeout=40, tries=2)
    if r is None or r.status_code != 200:
        return ""
    soup = BeautifulSoup(r.text, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return clean_text(soup.get_text("\n"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DATA / "bursa_announcements.jsonl")
    args = ap.parse_args()
    session = cffi_requests.Session()
    out: list[dict] = []
    seen: set[str] = set()
    existing: dict[str, dict] = {}
    if args.out.exists():
        for line in args.out.read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                existing[str(rec.get("native_id"))] = rec
    for code, ticker, name in COMPANIES:
        page = 1
        total = None
        company_count = 0
        while True:
            params = {
                "company": str(code),
                "ann_type": "company",
                "dt_ht": "02/11/2025",
                "dt_lt": "03/11/2026",
                "per_page": "20",
                "page": str(page),
            }
            try:
                r = session.get(
                    API,
                    params=params,
                    impersonate="chrome",
                    timeout=40,
                    headers={
                        "Accept": "application/json",
                        "X-Requested-With": "XMLHttpRequest",
                        "Referer": "https://www.bursamalaysia.com/",
                    },
                )
                j = r.json()
            except Exception as exc:
                print(f"{ticker} page {page}: ERR {exc}")
                break
            if total is None:
                total = j.get("recordsTotal", 0)
                print(f"{ticker}: {total} announcements in window")
            rows = j.get("data") or []
            if not rows:
                break
            for row in rows:
                date_html, company_html, title_html = row[1], row[2], row[3]
                m = DATE_RE.search(re.sub(r"<[^>]+>", " ", date_html))
                if not m:
                    continue
                dt = datetime(
                    int(m.group(3)), MONTHS[m.group(2)[:3]], int(m.group(1)), 12, 0, tzinfo=timezone.utc
                )
                link_m = re.search(r"ann_id=(\d+)", title_html)
                if not link_m:
                    continue
                ann_id = link_m.group(1)
                if ann_id in seen:
                    continue
                seen.add(ann_id)
                company_count += 1
                if ann_id in existing:
                    out.append(existing[ann_id])
                    continue
                soup = BeautifulSoup(title_html, "lxml")
                title = clean_text(soup.get_text(" "))
                company = clean_text(BeautifulSoup(company_html, "lxml").get_text(" "))
                body = announcement_text(ann_id)
                out.append(
                    {
                        "record_type": "announcement",
                        "source": "bursa",
                        "channel": name,
                        "native_id": ann_id,
                        "ticker": ticker,
                        "stock_code": str(code),
                        "company": company or name,
                        "title": title,
                        "published_utc": int(dt.timestamp()),
                        "url": DETAIL.format(ann_id=ann_id),
                        "body": body or None,
                        "raw": {
                            "bursa_announcement_id": ann_id,
                            "time_precision": "date_only_noon_myt",
                            "text_source": "disclosure_bursamalaysia_viewHtml",
                        },
                    }
                )
                time.sleep(1.1)
            if company_count >= total or len(rows) < 20:
                break
            page += 1
            time.sleep(1.1)
    out.sort(key=lambda x: x["published_utc"], reverse=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        for rec in out:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"wrote {len(out)} announcements -> {args.out}")
    print(f"with body: {sum(1 for r in out if r['body'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
