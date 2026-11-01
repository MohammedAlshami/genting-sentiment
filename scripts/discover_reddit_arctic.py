#!/usr/bin/env python3
"""Incremental Arctic Shift title search for the Reddit backfill.

Saves after every page so a server timeout never loses earlier results.  Only `after`
is sent (adding `before` makes the archive query time out), and rows are filtered to the
window locally.  A page that still fails after short retries is skipped and recorded.
"""

from __future__ import annotations

import datetime as dt
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://arctic-shift.photon-reddit.com/api"
UA = "genting-sentiment/0.2 (research backfill)"
OUT = Path("/tmp/opencode/backfill/reddit_arctic_candidates.json")
START = int(dt.datetime(2024, 11, 1, 16, 0, 0, tzinfo=dt.timezone.utc).timestamp())
END = int(dt.datetime(2025, 11, 1, 16, 0, 0, tzinfo=dt.timezone.utc).timestamp())

SUBS = [
    "malaysia",
    "MalaysiaPF",
    "MalaysianPF",
    "BursaMalaysia",
    "bursabets",
    "investing",
    "stocks",
    "StockMarket",
]
TERMS = ["genting", "GENM", "4715", "3182", "云顶"]

_last = 0.0
pool: dict[str, dict] = {}
notes: list[str] = []


def save() -> None:
    OUT.write_text(
        json.dumps(
            {
                "window": {"start_utc": START, "end_utc": END},
                "notes": notes,
                "posts": sorted(pool.values(), key=lambda p: p["created_utc"]),
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )


def get(params: dict, retries: int = 3) -> dict | None:
    global _last
    url = f"{BASE}/posts/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(retries):
        wait = 2.0 - (time.monotonic() - _last)
        if wait > 0:
            time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                _last = time.monotonic()
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            _last = time.monotonic()
            print(f"    retry {attempt + 1}/{retries} HTTP {exc.code}", flush=True)
            if exc.code not in (422, 429, 500, 502, 503, 504):
                return None
        except Exception as exc:  # noqa: BLE001
            _last = time.monotonic()
            print(f"    retry {attempt + 1}/{retries}: {exc}", flush=True)
        time.sleep(10 * (attempt + 1))
    return None


def main() -> None:
    for sub in SUBS:
        for term in TERMS:
            print(f"== r/{sub} title={term!r}", flush=True)
            after = START
            for page in range(4):
                payload = get(
                    {
                        "subreddit": sub,
                        "title": term,
                        "after": after,
                        "limit": 100,
                        "sort": "asc",
                    }
                )
                if payload is None:
                    notes.append(f"{sub}/{term}: page {page} failed at {after}")
                    break
                data = payload.get("data") or []
                in_window = [p for p in data if START <= int(p["created_utc"]) < END]
                for post in in_window:
                    pool[post["id"]] = post
                save()
                print(
                    f"    page {page}: {len(data)} rows, {len(in_window)} in window, total {len(pool)}",
                    flush=True,
                )
                if len(data) < 100 or not data:
                    break
                newest = max(int(p["created_utc"]) for p in data)
                if newest <= after:
                    notes.append(f"{sub}/{term}: cursor stuck at {after}")
                    break
                after = newest
                if after >= END:
                    break
    print(f"\n{len(pool)} candidates → {OUT}")
    for n in notes:
        print("NOTE", n)


if __name__ == "__main__":
    main()
