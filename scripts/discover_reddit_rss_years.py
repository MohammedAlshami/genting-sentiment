#!/usr/bin/env python3
"""Year-sliced Reddit Atom search for 2016-2022 (fills the Arctic gap).

Reddit's Atom search caps a single query at roughly 250 newest results.  For
r/malaysia ``genting`` the unsliced feed only reaches mid-2023, so each
Nov-Oct year is queried separately with the ``timestamp:`` operator.

Output: /tmp/opencode/reddit_rss_years_2016_2024.json
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

OUT = Path("/tmp/opencode/reddit_rss_years_2016_2024.json")
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
MIN_INTERVAL = 65.0
START = int(datetime(2016, 11, 1, 16, 0, 0, tzinfo=timezone.utc).timestamp())
END = int(datetime(2024, 11, 1, 16, 0, 0, tzinfo=timezone.utc).timestamp())

_last = 0.0


def get(url: str, retries: int = 5) -> str | None:
    global _last
    for attempt in range(retries):
        wait = MIN_INTERVAL - (time.monotonic() - _last)
        if wait > 0:
            time.sleep(wait)
        try:
            r = requests.get(
                url,
                headers={"User-Agent": UA, "Accept": "application/atom+xml, application/xml;q=0.9"},
                timeout=60,
            )
            _last = time.monotonic()
        except requests.RequestException as exc:
            print(f"    retry {attempt + 1}/{retries}: {exc}", flush=True)
            time.sleep(30)
            continue
        if r.status_code == 429:
            delay = 120 + 60 * attempt
            print(f"    HTTP 429; sleeping {delay}s", flush=True)
            time.sleep(delay)
            _last = time.monotonic()
            continue
        if r.status_code != 200:
            print(f"    HTTP {r.status_code}", flush=True)
            return None
        return r.text
    return None


def parse(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "xml")
    out = []
    for e in soup.find_all("entry"):
        id_el, up_el, ti_el = e.find("id"), e.find("updated"), e.find("title")
        if not id_el or not up_el:
            continue
        native = id_el.get_text(strip=True)
        if not native.startswith("t3_"):
            continue
        try:
            dt = datetime.fromisoformat(up_el.get_text(strip=True).replace("Z", "+00:00"))
        except ValueError:
            continue
        content = e.find("content")
        link = e.find("link")
        out.append(
            {
                "id": native[3:],
                "fullname": native,
                "title": ti_el.get_text(" ", strip=True) if ti_el else "",
                "created_utc": int(dt.timestamp()),
                "permalink": link.get("href") if link else None,
                "selftext": BeautifulSoup(content.get_text(), "lxml").get_text(" ", strip=True)
                if content
                else None,
                "discovery": "reddit_rss_year",
            }
        )
    return out


def year_bounds(year: int) -> tuple[int, int]:
    a = max(START, int(datetime(year, 11, 1, 16, tzinfo=timezone.utc).timestamp()))
    b = min(END, int(datetime(year + 1, 11, 1, 16, tzinfo=timezone.utc).timestamp()))
    return a, b


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--subreddit", default="malaysia")
    ap.add_argument("--query", default="genting")
    ap.add_argument("--start-year", type=int, default=2016)
    ap.add_argument("--end-year", type=int, default=2022)
    args = ap.parse_args()

    posts: dict[str, dict] = {}
    log = {}
    for year in range(args.start_year, args.end_year + 1):
        a, b = year_bounds(year)
        base = (
            f"https://www.reddit.com/r/{args.subreddit}/search.rss?"
            f"q={requests.utils.quote(args.query)}+timestamp%3A{a}..{b}"
            f"&restrict_sr=1&sort=new&limit=100"
        )
        print(f"== {year} {datetime.fromtimestamp(a, timezone.utc):%Y-%m-%d}.."
              f"{datetime.fromtimestamp(b, timezone.utc):%Y-%m-%d} ==", flush=True)
        after = None
        pages = 0
        rows_all: dict[str, dict] = {}
        while pages < 5:
            url = base + (f"&after={after}" if after else "")
            html = get(url)
            pages += 1
            if not html:
                break
            rows = parse(html)
            if not rows:
                break
            for p in rows:
                rows_all[p["id"]] = p
            print(f"  page {pages}: {len(rows)} rows, {len(rows_all)} unique", flush=True)
            if len(rows) < 100:
                break
            after = rows[-1]["fullname"]
        for p in rows_all.values():
            if a <= p["created_utc"] < b:
                posts[p["id"]] = p
        log[str(year)] = {"pages": pages, "rows": len(rows_all)}

    result = {
        "window": {"start_utc": START, "end_utc": END},
        "query": f"r/{args.subreddit}:{args.query}",
        "years": log,
        "posts": sorted(posts.values(), key=lambda p: p["created_utc"]),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {len(posts)} posts to {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
