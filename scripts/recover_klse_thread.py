#!/usr/bin/env python3
"""Recover replies hidden behind a dead KLSE Screener cursor.

The public reply endpoint paginates by comment id:
    /v2/comments/view_replies/<parent>?last_id=<id>

For a few very long threads one returned cursor points into a gap (typically a
deleted reply / migration boundary) and the endpoint answers count=0 even though
the thread counter says older replies remain.  This helper walks the thread from
a chosen live cursor, and when a cursor comes back empty it steps down by a
small offset until it finds a live cursor again, so the older replies can still
be recovered.  It then merges the recovered in-window records into an existing
`klse_screener_<TICKER>_2016-2024.jsonl` file, preserving the synthetic post.

Usage:
    python3 scripts/recover_klse_thread.py \
        --file data/raw/klse_screener_GENTING_2016-2024.jsonl \
        --parent 386764 --start-cursor 7300000
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backfill_klse_10y as bf  # noqa: E402


def fetch_batch(f: bf.Fetcher, parent: str, cursor: str):
    payload = f.get(f"{bf.BASE}/v2/comments/view_replies/{parent}?last_id={cursor}")
    recs, _ = bf.parse_detail(payload.get("html") or "", "", parent)
    return recs, payload


def to_output(r: dict, post: dict) -> dict:
    """Convert the parser's internal record to the corpus JSONL schema."""
    return {
        "record_type": "reply",
        "source": "klse_screener",
        "channel": post["channel"],
        "native_id": r["id"],
        "post_native_id": post["native_id"],
        "parent_native_id": r["parent_id"],
        "depth": r["depth"],
        "author": r["author"],
        "author_id": r["author_id"],
        "created_utc": r["created_utc"],
        "body": r["body"],
        "score": r["score"],
        "url": f"{bf.BASE}/v2/comment/{r['id']}",
        "lang": None,
        "raw": {
            "comment_id": r["id"],
            "stock_code": post["native_id"],
            "datetime": r["datetime_text"],
            "likes": r["score"],
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, type=Path)
    ap.add_argument("--parent", required=True)
    ap.add_argument("--start-cursor", required=True)
    ap.add_argument("--max-batches", type=int, default=2000)
    args = ap.parse_args()

    path: Path = args.file
    if not path.exists():
        raise SystemExit(f"missing {path}")

    lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    post = lines[0]
    if post.get("record_type") != "post":
        raise SystemExit("first record is not the synthetic post")
    records = {
        r["native_id"]: r for r in lines[1:] if r.get("record_type") == "reply"
    }
    before = len(records)
    existing_for_parent = sum(
        1 for r in records.values() if r.get("parent_native_id") == args.parent
    )
    print(
        f"loaded {len(records)} replies ({existing_for_parent} under {args.parent})",
        flush=True,
    )

    f = bf.Fetcher()
    cursor = str(args.start_cursor)
    left: int | None = None
    batches = 0
    added = 0
    recovered_total = 0
    try:
        while batches < args.max_batches:
            recs, payload = fetch_batch(f, args.parent, cursor)
            batches += 1
            if not recs:
                print(
                    f"  batch {batches}: cursor {cursor} -> empty "
                    f"(left={left!r}), looking for a live cursor below it",
                    flush=True,
                )
                if left is not None and left <= 0:
                    break
                found = False
                for delta in (1, 10, 100, 1000, 5000, 10000, 50000, 100000, 500000, 1000000):
                    probe = max(1, int(cursor) - delta)
                    recs2, payload2 = fetch_batch(f, args.parent, str(probe))
                    if recs2:
                        print(
                            f"  batch {batches}: cursor {probe} (offset {delta}) -> "
                            f"{len(recs2)} replies",
                            flush=True,
                        )
                        cursor = str(probe)
                        recs, payload = recs2, payload2
                        found = True
                        break
                if not found:
                    print("  ! no live cursor found below the dead cursor; stopping", flush=True)
                    break
            else:
                print(
                    f"  batch {batches}: cursor {cursor} -> {len(recs)} replies, "
                    f"next={payload.get('last_id')} left={payload.get('replies_left_count')}",
                    flush=True,
                )

            stamps = [r["created_utc"] for r in recs if r.get("created_utc")]
            recovered_total += len(recs)
            for r in recs:
                ts = r.get("created_utc")
                if ts is None or not (bf.WINDOW_START <= ts <= bf.WINDOW_END):
                    continue
                if r["id"] not in records:
                    records[r["id"]] = to_output(r, post)
                    added += 1
            if stamps and min(stamps) < bf.WINDOW_START:
                print("  reached before window start; stopping", flush=True)
                break

            new_last = payload.get("last_id")
            new_left = payload.get("replies_left_count")
            left = int(new_left) if new_left is not None else None
            if not new_last or str(new_last) == cursor or (left is not None and left <= 0):
                break
            cursor = str(new_last)
    finally:
        f.s.close()

    if added == 0:
        print("no new in-window records; file unchanged", flush=True)
        return 0

    kept = sorted(records.values(), key=lambda r: (r["created_utc"], int(r["native_id"])))
    post["num_comments"] = len(kept)
    tmp = path.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(post, ensure_ascii=False) + "\n")
        for r in kept:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, path)
    print(
        f"added {added} in-window replies (fetched {recovered_total} over {batches} batches); "
        f"{before} -> {len(kept)} replies -> {path}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
