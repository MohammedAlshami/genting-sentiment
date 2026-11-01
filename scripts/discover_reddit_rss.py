#!/usr/bin/env python3
"""Reddit RSS discovery (full-text) for the earlier-year backfill.

The Atom search feed matches title and body, including possessives such as "Genting's"
that Arctic Shift's title tokenizer misses.  Pages backwards with after=t3_<id> until the
start of the window.  Saves after each page; 429s are retried slowly.
"""

from __future__ import annotations

import datetime as dt
import json
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

OUT = Path("/tmp/opencode/backfill/reddit_rss_candidates.json")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
NS = {"a": "http://www.w3.org/2005/Atom"}
START = dt.datetime(2024, 11, 1, 16, 0, 0, tzinfo=dt.timezone.utc)
END = dt.datetime(2025, 11, 1, 16, 0, 0, tzinfo=dt.timezone.utc)
START_S, END_S = int(START.timestamp()), int(END.timestamp())
SUBS = ["malaysia", "MalaysiaPF", "MalaysianPF", "BursaMalaysia", "bursabets"]
TERMS = ["genting", "GENM"]

_last = 0.0
pool: dict[str, dict] = {}
notes: list[str] = []


def save() -> None:
    OUT.write_text(
        json.dumps(
            {
                "window": {"start_utc": START_S, "end_utc": END_S},
                "notes": notes,
                "posts": sorted(pool.values(), key=lambda p: p["created_utc_est"] or 0),
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )


def fetch(url: str, retries: int = 4) -> bytes | None:
    global _last
    for attempt in range(retries):
        wait = 10.0 - (time.monotonic() - _last)
        if wait > 0:
            time.sleep(wait)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as resp:
                _last = time.monotonic()
                return resp.read()
        except urllib.error.HTTPError as exc:
            _last = time.monotonic()
            print(f"    retry {attempt + 1}/{retries} HTTP {exc.code}", flush=True)
            if exc.code not in (429, 500, 502, 503, 504):
                return None
            time.sleep(90 if exc.code == 429 else 20 * (attempt + 1))
        except Exception as exc:  # noqa: BLE001
            _last = time.monotonic()
            print(f"    retry {attempt + 1}/{retries}: {exc}", flush=True)
            time.sleep(20 * (attempt + 1))
    return None


def main() -> None:
    for sub in SUBS:
        for term in TERMS:
            print(f"== r/{sub} q={term!r}", flush=True)
            after = None
            for page in range(20):
                params = {"q": term, "restrict_sr": "1", "sort": "new", "t": "all"}
                if after:
                    params["after"] = f"t3_{after}"
                url = f"https://www.reddit.com/r/{sub}/search.rss?" + urllib.parse.urlencode(params)
                body = fetch(url)
                if body is None:
                    notes.append(f"{sub}/{term}: page {page} failed")
                    break
                try:
                    root = ET.fromstring(body)
                except ET.ParseError as exc:
                    notes.append(f"{sub}/{term}: bad XML at {page}: {exc}")
                    break
                entries = root.findall("a:entry", NS)
                if not entries:
                    break
                oldest = None
                for entry in entries:
                    raw_id = entry.findtext("a:id", default="", namespaces=NS)
                    pid = raw_id[3:] if raw_id.startswith("t3_") else None
                    updated = entry.findtext("a:updated", default="", namespaces=NS)
                    if not pid or not updated:
                        continue
                    try:
                        ts = int(dt.datetime.fromisoformat(updated.replace("Z", "+00:00")).timestamp())
                    except ValueError:
                        continue
                    oldest = ts if oldest is None else min(oldest, ts)
                    if START_S <= ts < END_S and pid not in pool:
                        pool[pid] = {
                            "id": pid,
                            "title": entry.findtext("a:title", default="", namespaces=NS),
                            "created_utc_est": ts,
                            "query": term,
                            "subreddit": sub,
                        }
                save()
                print(
                    f"    page {page}: {len(entries)} rows, oldest "
                    f"{dt.datetime.fromtimestamp(oldest, dt.timezone.utc):%Y-%m-%d}, total {len(pool)}",
                    flush=True,
                )
                if oldest is None or oldest < START_S:
                    break
                nxt = entries[-1].findtext("a:id", default="", namespaces=NS)
                nxt = nxt[3:] if nxt.startswith("t3_") else None
                if not nxt or nxt == after:
                    break
                after = nxt
    print(f"\n{len(pool)} candidates → {OUT}")
    for n in notes:
        print("NOTE", n)


if __name__ == "__main__":
    main()
