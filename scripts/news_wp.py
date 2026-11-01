#!/usr/bin/env python3
"""Stage 3b: pull full-text Genting posts from WordPress REST APIs."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests as cffi_requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from news_lib import CACHE, clean_text, strip_tags  # noqa: E402

SITES = {
    "businesstoday.com.my": "https://www.businesstoday.com.my",
    "ggrasia.com": "https://ggrasia.com",
    "therakyatpost.com": "https://www.therakyatpost.com",
    "thesun.my": "https://thesun.my",
    "themalaysianreserve.com": "https://www.themalaysianreserve.com",
}

OUT = CACHE / "wp_posts.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    session = cffi_requests.Session()
    records: list[dict] = []
    for name, base in SITES.items():
        page = 1
        site_count = 0
        while page <= 12:
            url = (
                f"{base}/wp-json/wp/v2/posts?search=genting&per_page=100&page={page}"
                "&after=2025-11-01T00:00:00&before=2026-11-03T00:00:00"
                "&_fields=id,date,date_gmt,link,title,content,author,excerpt"
            )
            try:
                r = session.get(url, impersonate="chrome", timeout=45)
            except Exception as exc:
                print(f"{name} page {page}: ERR {exc}")
                break
            if r.status_code == 400:
                break
            if r.status_code != 200:
                print(f"{name} page {page}: HTTP {r.status_code}")
                break
            try:
                posts = r.json()
            except Exception:
                print(f"{name} page {page}: bad JSON")
                break
            if not posts:
                break
            for p in posts:
                title = strip_tags((p.get("title") or {}).get("rendered", ""))
                body = strip_tags((p.get("content") or {}).get("rendered", ""))
                if not title or not body:
                    continue
                dt = None
                if p.get("date_gmt"):
                    dt = datetime.fromisoformat(p["date_gmt"]).replace(tzinfo=timezone.utc)
                elif p.get("date"):
                    dt = datetime.fromisoformat(p["date"]).astimezone(timezone.utc)
                if dt is None:
                    continue
                records.append(
                    {
                        "url": p.get("link"),
                        "title": clean_text(title),
                        "author": None,
                        "published_utc": int(dt.timestamp()),
                        "body": body,
                        "publisher": name,
                        "wp_id": p.get("id"),
                        "published_source": "wp_api",
                    }
                )
                site_count += 1
            if len(posts) < 100:
                break
            page += 1
            time.sleep(1.1)
        print(f"{name}: {site_count} posts")
    # de-dup by url
    by = {r["url"]: r for r in records if r.get("url")}
    records = list(by.values())
    args.out.write_text(json.dumps(records, ensure_ascii=False))
    print(f"wrote {len(records)} -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
