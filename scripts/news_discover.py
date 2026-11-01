#!/usr/bin/env python3
"""Stage 1: discover Genting articles via Google News RSS and publisher searches."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from news_lib import (  # noqa: E402
    CACHE,
    DATA,
    WINDOW_END,
    WINDOW_START,
    cache_path,
    http_get,
    parse_pubdate,
    sha1,
)

GN_QUERIES = [
    '"Genting" Malaysia',
    '"Genting Berhad"',
    '"Genting Malaysia"',
    "GENM",
    '"Genting rights issue"',
    '"Genting 3182"',
    '"Genting debt"',
    '"Resorts World Genting"',
    '"Genting New York"',
    '"Genting Bhd"',
    '"Genting group"',
    "Genting Bursa Malaysia",
    "Genting shares",
    "Genting earnings",
    "Genting dividend",
    "Genting Fitch",
    "Genting Moody's",
    "Genting sukuk",
    "Genting bond",
    "Genting casino Malaysia",
    "Genting layoffs",
    "Genting tax",
    "Genting share price",
    "Genting results",
    "Genting quarterly profit",
    "Genting annual report",
    "site:theedgemalaysia.com Genting",
    "site:thestar.com.my Genting",
    "site:nst.com.my Genting",
    "site:themalaysianreserve.com Genting",
    "site:focusmalaysia.my Genting",
    "site:bernama.com Genting",
    "site:thesun.my Genting",
    "site:malaymail.com Genting",
    "site:freemalaysiatoday.com Genting",
    "site:klsescreener.com Genting",
    "site:themalaysianinsight.com Genting",
    "site:malaysiakini.com Genting",
    "site:therakyatpost.com Genting",
    "site:thevibes.com Genting",
    "site:edgeprop.my Genting",
    "site:thestar.com.my \"Genting Malaysia\"",
    "site:theedgemalaysia.com \"Genting Malaysia\"",
]

GN_RSS = "https://news.google.com/rss/search?q={q}&hl=en-MY&gl=MY&ceid=MY:en"


def strip_publisher(title: str, source: str | None) -> str:
    if source:
        for sep in (" - ", " | "):
            suffix = f"{sep}{source}"
            if title.endswith(suffix):
                return title[: -len(suffix)].strip()
    # Google usually appends " - Publisher"; remove a trailing dash segment that
    # matches a known publisher-ish single token.
    return title.strip()


def discover_google() -> list[dict]:
    items: list[dict] = []
    seen_links: set[str] = set()
    for i, q in enumerate(GN_QUERIES, 1):
        url = GN_RSS.format(q=q.replace(" ", "+"))
        # add explicit date range
        url += "&q="  # no-op keeps URL assembly readable
        url = (
            "https://news.google.com/rss/search?q="
            + re.sub(r"\s+", "+", f"{q} after:2025-11-01 before:2026-11-03")
            + "&hl=en-MY&gl=MY&ceid=MY:en"
        )
        cp = cache_path("gn", url, ".xml")
        if cp.exists():
            xml_text = cp.read_text(encoding="utf-8", errors="replace")
        else:
            r = http_get(url, timeout=40)
            if r is None or r.status_code != 200:
                print(f"[{i}/{len(GN_QUERIES)}] FAIL {q}")
                continue
            xml_text = r.text
            cp.write_text(xml_text, encoding="utf-8")
            time.sleep(1.2)
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as exc:
            print(f"[{i}/{len(GN_QUERIES)}] parse error {q}: {exc}")
            continue
        n_new = 0
        for it in root.findall(".//item"):
            link = (it.findtext("link") or "").strip()
            if not link or link in seen_links:
                continue
            seen_links.add(link)
            src_el = it.find("source")
            source = (src_el.text or "").strip() if src_el is not None else None
            title = (it.findtext("title") or "").strip()
            pub = parse_pubdate(it.findtext("pubDate"))
            if pub is None or not (WINDOW_START <= pub < WINDOW_END):
                continue
            items.append(
                {
                    "google_url": link,
                    "google_id": (it.findtext("guid") or "").strip(),
                    "title": strip_publisher(title, source),
                    "title_raw": title,
                    "source": source,
                    "published_utc": int(pub.timestamp()),
                    "pub_text": it.findtext("pubDate"),
                    "query": q,
                    "discovered_via": "google_news",
                }
            )
            n_new += 1
        print(f"[{i}/{len(GN_QUERIES)}] {q}: {n_new} new (total {len(items)})")
    return items


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=CACHE / "discovery.json")
    args = ap.parse_args()
    items = discover_google()
    # merge with previous run if present, keyed by google_url
    if args.out.exists():
        old = json.loads(args.out.read_text())
        by = {x["google_url"]: x for x in old}
        for it in items:
            by[it["google_url"]] = it
        items = list(by.values())
    items.sort(key=lambda x: x["published_utc"], reverse=True)
    args.out.write_text(json.dumps(items, ensure_ascii=False, indent=1))
    print(f"\nwrote {len(items)} discovery items -> {args.out}")
    src: dict[str, int] = {}
    for it in items:
        src[it.get("source") or "?"] = src.get(it.get("source") or "?", 0) + 1
    for k, v in sorted(src.items(), key=lambda kv: -kv[1]):
        print(f"  {v:4d}  {k}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
