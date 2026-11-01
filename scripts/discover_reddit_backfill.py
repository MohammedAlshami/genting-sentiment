#!/usr/bin/env python3
"""Discover Malaysian Genting Reddit threads in the 2024-11 → 2025-11 year.

Reddit's own search/JSON endpoints return 403 from this machine, so discovery uses
Arctic Shift's keyword search restricted to the relevant subreddits.  Only the `after`
bound is sent: adding `before` makes the archive query time out.  Results are fetched
ascending from the start of the window and filtered locally to the end of the window.

The API frequently returns HTTP 422 "Timeout. Maybe slow down a bit" under load.  Every
call is retried with a long backoff; a query that still fails is recorded in `notes`
rather than being silently dropped.

Output: /tmp/opencode/backfill/reddit_candidates.json (candidate pool for curation).
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
OUT = Path("/tmp/opencode/backfill/reddit_candidates.json")

# Window: 2 Nov 2024 00:00 MYT → 1 Nov 2025 23:59:59 MYT (UTC+8).
START = int(dt.datetime(2024, 11, 1, 16, 0, 0, tzinfo=dt.timezone.utc).timestamp())
END = int(dt.datetime(2025, 11, 1, 16, 0, 0, tzinfo=dt.timezone.utc).timestamp())

SUBS = [
    "MalaysiaPF",
    "MalaysianPF",
    "malaysia",
    "BursaMalaysia",
    "bursabets",
    "investing",
    "stocks",
    "StockMarket",
]
TERMS = ["genting", "GENM", "3182", "4715", "云顶", "云顶大马"]

MIN_INTERVAL = 2.5
_last_call = 0.0


def get(path: str, params: dict, retries: int = 6) -> dict | None:
    global _last_call
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(retries):
        wait = MIN_INTERVAL - (time.monotonic() - _last_call)
        if wait > 0:
            time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                _last_call = time.monotonic()
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            _last_call = time.monotonic()
            body = exc.read()[:160].decode("utf-8", "replace")
            print(f"    retry {attempt + 1}/{retries} HTTP {exc.code}: {body}", flush=True)
            if exc.code not in (422, 429, 500, 502, 503, 504):
                return None
        except Exception as exc:  # noqa: BLE001 - network/timeout/JSON
            _last_call = time.monotonic()
            print(f"    retry {attempt + 1}/{retries}: {exc}", flush=True)
        time.sleep(min(90, 15 * (attempt + 1)))
    return None


def search(sub: str, field: str, term: str) -> tuple[dict[str, dict], list[str]]:
    found: dict[str, dict] = {}
    notes: list[str] = []
    after = START
    for page in range(20):
        params = {
            "subreddit": sub,
            field: term,
            "after": after,
            "limit": 100,
            "sort": "asc",
        }
        payload = get("/posts/search", params)
        if payload is None:
            notes.append(f"{sub}/{field}={term}: failed at cursor {after}")
            break
        data = payload.get("data") or []
        for post in data:
            found[post["id"]] = post
        in_range = [p for p in data if p["created_utc"] < END]
        if data:
            print(
                f"    page {page}: {len(data)} rows, {len(in_range)} in window, "
                f"last {dt.datetime.fromtimestamp(data[-1]['created_utc'], dt.timezone.utc):%Y-%m-%d}",
                flush=True,
            )
        if len(data) < 100 or not data:
            break
        newest = max(int(p["created_utc"]) for p in data)
        if newest <= after:
            notes.append(f"{sub}/{field}={term}: cursor stuck at {after}")
            break
        after = newest
        if after >= END:
            break
    return found, notes


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pool: dict[str, dict] = {}
    notes: list[str] = []
    blocks = 0
    for sub in SUBS:
        for term in TERMS:
            print(f"== r/{sub} title={term!r}", flush=True)
            found, n = search(sub, "title", term)
            blocks += 1
            notes.extend(n)
            new = 0
            for pid, post in found.items():
                if pid not in pool:
                    pool[pid] = post
                    new += 1
            print(f"    unique total {len(pool)} (+{new})", flush=True)
            time.sleep(MIN_INTERVAL)
        # Body mentions catch posts whose title does not name Genting.
        print(f"== r/{sub} selftext='genting'", flush=True)
        found, n = search(sub, "selftext", "genting")
        blocks += 1
        notes.extend(n)
        new = 0
        for pid, post in found.items():
            if pid not in pool:
                pool[pid] = post
                new += 1
        print(f"    unique total {len(pool)} (+{new})", flush=True)
        time.sleep(MIN_INTERVAL)

    in_window = {
        pid: p for pid, p in pool.items() if START <= int(p["created_utc"]) < END
    }
    OUT.write_text(
        json.dumps(
            {
                "window": {"start_utc": START, "end_utc": END},
                "queries": {"subs": SUBS, "terms": TERMS, "query_blocks": blocks},
                "notes": notes,
                "posts": sorted(in_window.values(), key=lambda p: p["created_utc"]),
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"\n{len(in_window)} in-window candidates from {len(pool)} fetched → {OUT}")
    for n in notes:
        print("NOTE", n)


if __name__ == "__main__":
    main()
