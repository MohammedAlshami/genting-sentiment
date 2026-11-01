"""Resumable Arctic Shift discovery for the full 2024-11-02 .. 2026-11-02 window.

Arctic Shift frequently answers 422 "Timeout. Maybe slow down a bit" when its
workers are busy. This script spaces requests, backs off exponentially and
caches every successful search page so a restart resumes where it stopped.
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://arctic-shift.photon-reddit.com/api"
UA = "genting-sentiment/0.1 (research collector)"
CACHE = Path("/tmp/opencode/reddit_extra_cache")
STATE = Path("/tmp/opencode/reddit_extra_state.json")
OUT = Path("/tmp/opencode/reddit_extra_posts.json")
MIN_INTERVAL = 4.0
MAX_RETRIES = 12

AFTER = int(datetime(2024, 11, 2, tzinfo=timezone.utc).timestamp())
BEFORE = int(datetime(2026, 11, 3, tzinfo=timezone.utc).timestamp())

_last = 0.0


def get(path: str, params: dict) -> dict:
    global _last
    key = re.sub(r"[^A-Za-z0-9_.-]+", "_", f"{path}_{urllib.parse.urlencode(params)}")[:200]
    cache_file = CACHE / (key + ".json")
    if cache_file.exists():
        return json.loads(cache_file.read_text())
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    last_err: Exception | None = None
    for attempt in range(MAX_RETRIES):
        wait = MIN_INTERVAL - (time.monotonic() - _last)
        if wait > 0:
            time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                _last = time.monotonic()
                payload = json.load(resp)
                CACHE.mkdir(parents=True, exist_ok=True)
                cache_file.write_text(json.dumps(payload))
                return payload
        except urllib.error.HTTPError as exc:
            _last = time.monotonic()
            last_err = exc
            if exc.code not in (422, 429, 500, 502, 503, 504):
                raise
            delay = min(180, 15 * (1.6**attempt))
            print(
                f"    retry {attempt + 1}/{MAX_RETRIES} in {delay:.0f}s: HTTP {exc.code}",
                flush=True,
            )
            time.sleep(delay)
        except Exception as exc:
            _last = time.monotonic()
            last_err = exc
            delay = min(120, 15 * (1.6**attempt))
            print(f"    retry {attempt + 1}/{MAX_RETRIES} in {delay:.0f}s: {exc}", flush=True)
            time.sleep(delay)
    raise RuntimeError(f"giving up on {path} {params}: {last_err}")


def search(sub: str, query: str, sink: dict[str, dict], cutoff: int | None = None) -> list[dict]:
    posts: dict[str, dict] = {}
    cursor: int | None = None
    while True:
        if cutoff and cursor and cursor >= cutoff:
            print("    cutoff reached before next page", flush=True)
            break
        params = {
            "subreddit": sub,
            "query": query,
            "after": cursor or AFTER,
            "before": BEFORE,
            "limit": 100,
            "sort": "asc",
        }
        data = get("/posts/search", params).get("data") or []
        fresh = 0
        for p in data:
            if p["id"] not in posts:
                posts[p["id"]] = p
                sink[p["id"]] = p
                fresh += 1
        OUT.write_text(json.dumps(sink, ensure_ascii=False))
        oldest = min((int(p.get("created_utc") or 0) for p in data), default=0)
        print(
            f"    page: {len(data)} rows, {fresh} new, "
            f"oldest={datetime.fromtimestamp(oldest, timezone.utc):%Y-%m-%d}",
            flush=True,
        )
        if len(data) < 100 or fresh == 0:
            break
        if cutoff and oldest >= cutoff:
            print(f"    cutoff reached at {datetime.fromtimestamp(oldest, timezone.utc):%Y-%m-%d}", flush=True)
            break
        newest = max(int(p.get("created_utc") or 0) for p in data)
        if newest == cursor:
            break
        cursor = newest
    return sorted(posts.values(), key=lambda p: p["created_utc"])


def main() -> None:
    subs = sys.argv[1:] or [
        "MalaysiaPF",
        "malaysia",
        "BursaMalaysia",
        "MalaysianPF",
        "bursabets",
        "investing",
        "MalaysiaPersonalFinance",
        "MalaysiaStock",
    ]
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    all_posts = json.loads(OUT.read_text()) if OUT.exists() else {}
    for spec in subs:
        if ":" in spec:
            sub, query = spec.split(":", 1)
        else:
            sub, query = spec, "genting"
        key = f"{sub}|{query}"
        if state.get(key, {}).get("done"):
            print(f"skip {key} (done)", flush=True)
            continue
        print(f"== r/{sub} query={query!r} ==", flush=True)
        cutoff = None
        if sub == "malaysia" and query == "genting":
            # Existing reddit_threads.jsonl already covers 2025-11 onward; stop
            # the broad r/malaysia travel-heavy sweep at the boundary.
            cutoff = int(datetime(2025, 11, 27, tzinfo=timezone.utc).timestamp())
        try:
            posts = search(sub, query, all_posts, cutoff=cutoff)
        except Exception as exc:
            print(f"  PARTIAL r/{sub}: {exc} (saved {len(all_posts)} total)", flush=True)
            OUT.write_text(json.dumps(all_posts, ensure_ascii=False))
            continue
        for p in posts:
            all_posts[p["id"]] = p
        state[key] = {"done": True, "count": len(posts)}
        OUT.write_text(json.dumps(all_posts, ensure_ascii=False))
        STATE.write_text(json.dumps(state, indent=1))
        print(f"  -> {len(posts)} posts (total {len(all_posts)})", flush=True)


if __name__ == "__main__":
    main()
