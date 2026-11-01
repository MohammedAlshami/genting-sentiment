#!/usr/bin/env python3
"""Discover Reddit posts via the public Atom search feed (full-text fallback).

Arctic Shift's title search misses posts whose title does not contain
"Genting"/"GENM" but whose body does (e.g. "Takeover offer extended").  Reddit's
Atom search feed is full-text, so it is used as a complementary discovery
source.  The feed is rate-limited to roughly one request per minute from this
machine; the script therefore sleeps between requests and retries 429s.

Output: /tmp/opencode/reddit_rss_2016_2024_candidates.json
"""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

OUT = Path("/tmp/opencode/reddit_rss_2016_2024_candidates.json")
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
MIN_INTERVAL = 65.0
START = int(datetime(2016, 11, 1, 16, 0, 0, tzinfo=timezone.utc).timestamp())
END = int(datetime(2024, 11, 1, 16, 0, 0, tzinfo=timezone.utc).timestamp())

SUBREDDITS = ["malaysia", "MalaysianPF", "BursaMalaysia", "bursabets", "investing"]
QUERIES = ["genting", "genm", "genting malaysia", "3182", "4715"]

_last = 0.0


def _get(url: str, retries: int = 5) -> str | None:
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


TAG_RE = re.compile(r"<[^>]+>")
BR_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)


def clean(text: str | None) -> str | None:
    if text is None:
        return None
    text = BR_RE.sub(" ", text)
    text = TAG_RE.sub("", text)
    text = (
        text.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
        .replace("&nbsp;", " ")
    )
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def parse_feed(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "xml")
    out = []
    for e in soup.find_all("entry"):
        id_el = e.find("id")
        title_el = e.find("title")
        updated_el = e.find("updated")
        author_el = e.find("author/name")
        if not id_el or not updated_el:
            continue
        native = id_el.get_text(strip=True)
        if not native.startswith("t3_"):
            continue
        try:
            dt = datetime.fromisoformat(updated_el.get_text(strip=True).replace("Z", "+00:00"))
        except ValueError:
            continue
        link_el = e.find("link")
        content_el = e.find("content")
        out.append(
            {
                "id": native[3:],
                "fullname": native,
                "title": title_el.get_text(" ", strip=True) if title_el else "",
                "author": author_el.get_text(strip=True) if author_el else None,
                "created_utc": int(dt.timestamp()),
                "permalink": link_el.get("href") if link_el else None,
                "selftext": clean(content_el.get_text() if content_el else None),
                "discovery": "reddit_rss",
            }
        )
    return out


def discover(sub: str, query: str) -> tuple[list[dict], dict]:
    posts: dict[str, dict] = {}
    after: str | None = None
    pages = 0
    errors: list[str] = []
    while pages < 30:
        url = (
            f"https://www.reddit.com/r/{sub}/search.rss?"
            f"q={requests.utils.quote(query)}&restrict_sr=1&sort=new&limit=100"
        )
        if after:
            url += f"&after={after}"
        html = _get(url)
        pages += 1
        if not html:
            errors.append("no feed")
            break
        rows = parse_feed(html)
        if not rows:
            break
        new = 0
        for p in rows:
            if p["id"] not in posts:
                posts[p["id"]] = p
                new += 1
        oldest = min(p["created_utc"] for p in rows)
        newest = max(p["created_utc"] for p in rows)
        print(
            f"  r/{sub} {query!r} page {pages}: {len(rows)} rows, {new} new, "
            f"{datetime.fromtimestamp(oldest, timezone.utc):%Y-%m-%d}.."
            f"{datetime.fromtimestamp(newest, timezone.utc):%Y-%m-%d}",
            flush=True,
        )
        if oldest <= START:
            break
        last = rows[-1]
        if last["fullname"] == after or new == 0:
            errors.append("pagination stopped")
            break
        after = last["fullname"]
    return list(posts.values()), {"pages": pages, "errors": errors}


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--subreddits", nargs="*", default=SUBREDDITS)
    ap.add_argument("--queries", nargs="*", default=QUERIES)
    args = ap.parse_args()
    all_posts: dict[str, dict] = {}
    queries: dict[str, dict] = {}
    for sub in args.subreddits:
        for query in args.queries:
            key = f"r/{sub}:{query}"
            print(f"== {key} ==", flush=True)
            rows, stats = discover(sub, query)
            added = 0
            for p in rows:
                if START <= p["created_utc"] < END and p["id"] not in all_posts:
                    all_posts[p["id"]] = p
                    added += 1
            queries[key] = {**stats, "rows": len(rows), "new_to_pool": added}
            print(f"  -> {len(rows)} rows, {added} new in-window", flush=True)
    result = {
        "window": {"start_utc": START, "end_utc": END},
        "queries": queries,
        "posts": sorted(all_posts.values(), key=lambda p: p["created_utc"]),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nwrote {len(all_posts)} unique in-window posts to {OUT}", flush=True)
    print(json.dumps(queries, indent=1), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
