#!/usr/bin/env python3
"""Fill the pre-2022-09 Reddit gap with anchor-based Arctic Shift searches.

The long ``before`` walk from 2024-11 stalls around a 2022-09 cursor on this
API.  Instead of relying on one continuous cursor, this script starts a short
backward page at each year-ish anchor and keeps up to two pages per anchor.
Results are merged into the collection pool by post id.

Output: /tmp/opencode/reddit_gap_2016_2024.json
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://arctic-shift.photon-reddit.com/api"
UA = "genting-sentiment/0.2 (research backfill)"
OUT = Path("/tmp/opencode/reddit_gap_2016_2024.json")
PAGE_SIZE = 25
START = int(datetime(2016, 11, 1, 16, tzinfo=timezone.utc).timestamp())
END = int(datetime(2024, 11, 1, 16, tzinfo=timezone.utc).timestamp())

# (label, before cursor).  Anchors are deliberately offset from the failing
# 2022-09-26 cursor.
ANCHORS = [
    ("2022-09", int(datetime(2022, 9, 1, tzinfo=timezone.utc).timestamp())),
    ("2022-06", int(datetime(2022, 6, 1, tzinfo=timezone.utc).timestamp())),
    ("2022-01", int(datetime(2022, 1, 1, tzinfo=timezone.utc).timestamp())),
    ("2021-01", int(datetime(2021, 1, 1, tzinfo=timezone.utc).timestamp())),
    ("2020-01", int(datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp())),
    ("2019-01", int(datetime(2019, 1, 1, tzinfo=timezone.utc).timestamp())),
    ("2018-01", int(datetime(2018, 1, 1, tzinfo=timezone.utc).timestamp())),
    ("2017-01", int(datetime(2017, 1, 1, tzinfo=timezone.utc).timestamp())),
]

_last = 0.0


def _get(params: dict, retries: int = 5) -> dict | None:
    global _last
    url = f"{BASE}/posts/search?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(retries):
        wait = 1.5 - (time.monotonic() - _last)
        if wait > 0:
            time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                _last = time.monotonic()
                return json.load(r)
        except urllib.error.HTTPError as exc:
            _last = time.monotonic()
            if exc.code not in (422, 429, 500, 502, 503, 504):
                raise
            delay = 10 * (attempt + 1)
            print(f"    retry {attempt + 1}/{retries} in {delay}s: HTTP {exc.code}", flush=True)
            time.sleep(delay)
        except Exception as exc:  # noqa: BLE001
            _last = time.monotonic()
            print(f"    retry {attempt + 1}/{retries}: {exc}", flush=True)
            time.sleep(10 * (attempt + 1))
    return None


def main() -> int:
    posts: dict[str, dict] = {}
    log = {}
    for label, cursor in ANCHORS:
        print(f"== anchor {label} before={cursor} ==", flush=True)
        pages = 0
        found = 0
        errors = []
        while pages < 1 and cursor > START:
            payload = _get(
                {
                    "title": "genting",
                    "subreddit": "malaysia",
                    "before": cursor,
                    "limit": PAGE_SIZE,
                }
            )
            pages += 1
            if payload is None:
                errors.append(f"failed at {cursor}")
                break
            data = payload.get("data") or []
            if not data:
                break
            new = 0
            for p in data:
                if p["id"] not in posts:
                    posts[p["id"]] = p
                    new += 1
            found += len(data)
            oldest = min(int(p.get("created_utc") or 0) for p in data)
            print(
                f"  {label} page {pages}: {len(data)} rows, {new} new, "
                f"{datetime.fromtimestamp(oldest, timezone.utc):%Y-%m-%d}.."
                f"{datetime.fromtimestamp(max(int(p['created_utc']) for p in data), timezone.utc):%Y-%m-%d}",
                flush=True,
            )
            if len(data) < PAGE_SIZE:
                break
            cursor = oldest + 1
        log[label] = {"pages": pages, "rows": found, "errors": errors}
    result = {
        "window": {"start_utc": START, "end_utc": END},
        "anchors": log,
        "posts": sorted(posts.values(), key=lambda p: p["created_utc"]),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {len(posts)} posts to {OUT}", flush=True)
    print(json.dumps(log, indent=1), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
