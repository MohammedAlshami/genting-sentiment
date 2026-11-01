#!/usr/bin/env python3
"""Discover Reddit posts mentioning Genting/GENM for 2 Nov 2016 .. 1 Nov 2024.

Reddit's own JSON endpoints return 403 from this machine and its Atom search
feed is aggressively rate-limited, so discovery uses the Arctic Shift archive
API.  ``/api/posts/search`` with a title filter plus a single ``before`` cursor
is reliable; range queries (``after`` + ``before``) often time out, so the
collector walks backwards from the window end one page at a time.

Output: /tmp/opencode/reddit_2016_2024_candidates.json
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://arctic-shift.photon-reddit.com/api"
UA = "genting-sentiment/0.2 (research backfill)"
PAGE_SIZE = 25
MIN_INTERVAL = 1.2
OUT = Path("/tmp/opencode/reddit_2016_2024_candidates.json")

# Window: 2 Nov 2016 00:00 MYT -> 1 Nov 2024 23:59:59 MYT (UTC+8).
START = int(datetime(2016, 11, 1, 16, 0, 0, tzinfo=timezone.utc).timestamp())
END = int(datetime(2024, 11, 1, 16, 0, 0, tzinfo=timezone.utc).timestamp())

SUBREDDITS = [
    "malaysia",
    "MalaysianPF",
    "MalaysiaPF",
    "BursaMalaysia",
    "bursabets",
    "investing",
    "stocks",
    "StockMarket",
    "SecurityAnalysis",
]
KEYWORDS = ["genting", "genm", "3182", "4715"]

_last = 0.0


def _get(path: str, params: dict, retries: int = 5) -> dict:
    global _last
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    last_err: Exception | None = None
    for attempt in range(retries):
        wait = MIN_INTERVAL - (time.monotonic() - _last)
        if wait > 0:
            time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                _last = time.monotonic()
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            _last = time.monotonic()
            last_err = exc
            if exc.code not in (422, 429, 500, 502, 503, 504):
                raise
            delay = min(45, 6 * (attempt + 1))
            print(f"    retry {attempt + 1}/{retries} in {delay}s: HTTP {exc.code}", flush=True)
            time.sleep(delay)
        except Exception as exc:  # noqa: BLE001 - network/timeout/bad JSON
            _last = time.monotonic()
            last_err = exc
            delay = min(45, 6 * (attempt + 1))
            print(f"    retry {attempt + 1}/{retries} in {delay}s: {exc}", flush=True)
            time.sleep(delay)
    raise RuntimeError(f"giving up on {path} {params}: {last_err}")


def discover(subreddit: str, keyword: str) -> tuple[list[dict], dict]:
    posts: dict[str, dict] = {}
    cursor = END
    pages = 0
    errors: list[str] = []
    while pages < 80:
        params = {
            "title": keyword,
            "subreddit": subreddit,
            "before": cursor,
            "limit": PAGE_SIZE,
        }
        try:
            payload = _get("/posts/search", params)
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))
            break
        data = payload.get("data") or []
        pages += 1
        if not data:
            break
        new = 0
        for post in data:
            if post["id"] not in posts:
                posts[post["id"]] = post
                new += 1
        oldest = min(int(p.get("created_utc") or 0) for p in data)
        newest = max(int(p.get("created_utc") or 0) for p in data)
        print(
            f"  r/{subreddit} {keyword!r} page {pages}: {len(data)} rows, {new} new, "
            f"{datetime.fromtimestamp(oldest, timezone.utc):%Y-%m-%d}.."
            f"{datetime.fromtimestamp(newest, timezone.utc):%Y-%m-%d}",
            flush=True,
        )
        if len(data) < PAGE_SIZE:
            break
        if oldest <= START:
            break
        if oldest >= cursor:
            errors.append(f"cursor did not move: {cursor} -> {oldest}")
            break
        # before= is exclusive; +1 re-includes the boundary second so posts
        # sharing that second are not skipped.  Duplicates are removed by id.
        cursor = oldest + 1
    return list(posts.values()), {"pages": pages, "errors": errors}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subreddits", nargs="*", default=SUBREDDITS)
    ap.add_argument("--keywords", nargs="*", default=KEYWORDS)
    args = ap.parse_args()

    all_posts: dict[str, dict] = {}
    queries: dict[str, dict] = {}

    def dump() -> None:
        result = {
            "window": {"start_utc": START, "end_utc": END, "start_date": "2016-11-02", "end_date": "2024-11-01"},
            "queries": queries,
            "posts": sorted(all_posts.values(), key=lambda p: int(p.get("created_utc") or 0)),
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")

    for sub in args.subreddits:
        for kw in args.keywords:
            key = f"r/{sub}:{kw}"
            print(f"== {key} ==", flush=True)
            try:
                rows, stats = discover(sub, kw)
            except Exception as exc:  # noqa: BLE001
                print(f"  FATAL {exc}", flush=True)
                queries[key] = {"pages": 0, "errors": [str(exc)], "posts": 0}
                continue
            added = 0
            for post in rows:
                if post["id"] not in all_posts:
                    all_posts[post["id"]] = post
                    added += 1
            queries[key] = {**stats, "posts": len(rows), "new_to_pool": added}
            print(f"  -> {len(rows)} title matches, {added} new to pool", flush=True)
            dump()

    result = {
        "window": {"start_utc": START, "end_utc": END, "start_date": "2016-11-02", "end_date": "2024-11-01"},
        "queries": queries,
        "posts": sorted(all_posts.values(), key=lambda p: int(p.get("created_utc") or 0)),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nwrote {len(all_posts)} unique posts to {OUT}", flush=True)
    print(json.dumps(queries, indent=1), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
