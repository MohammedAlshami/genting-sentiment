#!/usr/bin/env python3
"""Stage 1b: deep discovery using month-sized Google News windows.

A single year-long `after:` query is capped at roughly 50-100 ranked items, so
each query is walked month by month (and split further if a slice hits the cap).
"""

from __future__ import annotations

import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from news_discover import GN_QUERIES, strip_publisher  # noqa: E402
from news_lib import CACHE, WINDOW_END, WINDOW_START, cache_path, http_get, parse_pubdate, sha1  # noqa: E402

CAP = 90


def rss_url(query: str, start: datetime, end: datetime) -> str:
    q = f"{query} after:{start:%Y-%m-%d} before:{end:%Y-%m-%d}"
    return (
        "https://news.google.com/rss/search?q="
        + re.sub(r"\s+", "+", q)
        + "&hl=en-MY&gl=MY&ceid=MY:en"
    )


def fetch_window(query: str, start: datetime, end: datetime, out: dict, depth: int = 0) -> None:
    url = rss_url(query, start, end)
    cp = cache_path("gn_deep", url, ".xml")
    if cp.exists():
        xml_text = cp.read_text(encoding="utf-8", errors="replace")
    else:
        r = http_get(url, timeout=45)
        if r is None or r.status_code != 200:
            print(f"    FAIL {start:%Y-%m-%d}..{end:%Y-%m-%d} {query}")
            return
        xml_text = r.text
        cp.write_text(xml_text, encoding="utf-8")
        time.sleep(1.0)
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return
    raw_items = root.findall(".//item")
    span_days = (end - start).days
    if len(raw_items) >= CAP and span_days > 2 and depth < 4:
        mid = start + (end - start) / 2
        fetch_window(query, start, mid, out, depth + 1)
        fetch_window(query, mid, end, out, depth + 1)
        return
    added = 0
    for it in raw_items:
        link = (it.findtext("link") or "").strip()
        if not link:
            continue
        src_el = it.find("source")
        source = (src_el.text or "").strip() if src_el is not None else None
        pub = parse_pubdate(it.findtext("pubDate"))
        if pub is None or not (WINDOW_START <= pub < WINDOW_END):
            continue
        title = (it.findtext("title") or "").strip()
        rec = {
            "google_url": link,
            "google_id": (it.findtext("guid") or "").strip(),
            "title": strip_publisher(title, source),
            "title_raw": title,
            "source": source,
            "published_utc": int(pub.timestamp()),
            "pub_text": it.findtext("pubDate"),
            "query": query,
            "discovered_via": "google_news_deep",
        }
        if link not in out:
            out[link] = rec
            added += 1


def main() -> int:
    start = datetime(2025, 11, 1, tzinfo=timezone.utc)
    end = datetime(2026, 11, 3, tzinfo=timezone.utc)
    out: dict[str, dict] = {}
    old_path = CACHE / "discovery.json"
    if old_path.exists():
        for it in json.loads(old_path.read_text()):
            out[it["google_url"]] = it
    before = len(out)
    windows = []
    cur = start
    while cur < end:
        nxt = (cur.replace(day=1) + timedelta(days=32)).replace(day=1)
        windows.append((cur, min(nxt, end)))
        cur = nxt
    print(f"{len(GN_QUERIES)} queries x {len(windows)} months; starting with {before} items")
    for qi, q in enumerate(GN_QUERIES, 1):
        for wi, (a, b) in enumerate(windows, 1):
            fetch_window(q, a, b, out)
        print(f"[{qi}/{len(GN_QUERIES)}] {q}: total {len(out)} (+{len(out)-before})", flush=True)
        before = len(out)
    items = sorted(out.values(), key=lambda x: x["published_utc"], reverse=True)
    old_path.write_text(json.dumps(items, ensure_ascii=False, indent=1))
    print(f"\nwrote {len(items)} discovery items -> {old_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
