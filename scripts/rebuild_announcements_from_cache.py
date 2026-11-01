#!/usr/bin/env python3
"""Merge announcement records reconstructed from cached KLSE Screener pages.

This is a recovery path for the paginated GENM crawl: every detail page that was
already fetched is parsed offline, so no additional network requests are needed.
Existing records (and their attachment metadata) are preserved.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect_announcements import (  # noqa: E402
    parse_ks_list, parse_ks_detail, parse_dt, START, END, TICKERS, PAGEDIR,
)

ROOT = Path(__file__).resolve().parent.parent
JSONL = ROOT / "data" / "raw" / "company_announcements.jsonl"


def main():
    existing = []
    if JSONL.exists():
        existing = [json.loads(x) for x in JSONL.read_text(encoding="utf-8").splitlines() if x.strip()]
    by_native = {r.get("native_id"): r for r in existing}
    by_ks = {r.get("raw", {}).get("ks_id"): r for r in existing}
    added = 0
    scanned = 0
    for page in range(9, 25):
        f = PAGEDIR / f"ks_list_GENM_p{page}.html"
        if not f.exists():
            continue
        for it in parse_ks_list(f.read_text(encoding="utf-8", errors="replace"), "GENM", page):
            scanned += 1
            detail_path = PAGEDIR / f"ks_detail_{it['source_id']}.html"
            if not detail_path.exists():
                continue
            d = parse_ks_detail(detail_path.read_text(encoding="utf-8", errors="replace"))
            dt = parse_dt(d.get("date_text"), it.get("time"))
            if not dt or dt < START or dt > END:
                continue
            native = f"bursa:{d.get('ann_id')}" if d.get("ann_id") else f"ks:{it['source_id']}"
            if native in by_native or it["source_id"] in by_ks:
                continue
            rec = {
                "source": "bursa_filing", "record_type": "announcement",
                "ticker": "GENM", "company": TICKERS["4715"][1],
                "native_id": native,
                "created_utc": int(dt.timestamp()), "created_myt": dt.isoformat(),
                "date": dt.strftime("%Y-%m-%d"), "time": it.get("time"),
                "category": d.get("category") or it.get("category"),
                "title": re.sub(r"^(GENTING|GENM)\s*-\s*", "", d.get("title") or it.get("title") or ""),
                "body": d.get("body") or it.get("snippet") or "",
                "url": d.get("bursa_url") or it["url"], "ks_url": it["url"],
                "reference": d.get("reference"), "ann_id": d.get("ann_id"),
                "attachments": [],
                "raw": {"category": d.get("category") or it.get("category"),
                        "attachment_url": None, "ks_id": it["source_id"],
                        "ks_page": page, "snippet": it.get("snippet"),
                        "body_source": "ks_detail_offline"},
            }
            existing.append(rec)
            by_native[native] = rec
            by_ks[it["source_id"]] = rec
            added += 1
    existing.sort(key=lambda r: (r["ticker"], r["created_utc"]))
    JSONL.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in existing) + "\n", encoding="utf-8")
    print(f"scanned {scanned} cached list items; added {added}; total {len(existing)}")
    print(Counter(r["ticker"] for r in existing))
    print("date range", min(r["date"] for r in existing), max(r["date"] for r in existing))


if __name__ == "__main__":
    main()
