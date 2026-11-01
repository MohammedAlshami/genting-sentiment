"""Validate and import collector JSONL into the SQLite store.

Usage:
    python3 -m genting.import_raw                 # all data/raw/*.jsonl
    python3 -m genting.import_raw data/raw/x.jsonl
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from . import store, validate

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"


def migrate_legacy_reddit(conn: sqlite3.Connection) -> dict:
    """Copy the original Reddit-specific tables into posts/replies once."""
    stats = {"posts": 0, "replies": 0}
    tables = {
        r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    if not {"threads", "comments"} <= tables:
        return stats
    if conn.execute("SELECT 1 FROM posts WHERE source='reddit' LIMIT 1").fetchone():
        return stats

    for row in conn.execute("SELECT * FROM threads").fetchall():
        d = dict(row)
        conn.execute(
            """
            INSERT OR IGNORE INTO posts (id, source, channel, native_id, ticker, title,
                author, created_utc, url, body, score, num_comments, collected_at, raw_json)
            VALUES (?, 'reddit', ?, ?, 'GENTING', ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"reddit:{d['id']}", d.get("subreddit"), d["id"], d.get("title"),
                d.get("author"), d.get("created_utc"),
                f"https://www.reddit.com{d['permalink']}" if d.get("permalink") else None,
                d.get("selftext"), d.get("score"), d.get("num_comments"),
                d.get("fetched_at"), d.get("raw_json"),
            ),
        )
        stats["posts"] += 1

    for row in conn.execute("SELECT * FROM comments").fetchall():
        d = dict(row)
        parent = d.get("parent_id") or ""
        parent_native = parent[3:] if parent.startswith("t1_") else None
        conn.execute(
            """
            INSERT OR IGNORE INTO replies (id, source, channel, native_id, post_native_id,
                parent_native_id, depth, author, created_utc, body, score, url,
                collected_at, raw_json)
            VALUES (?, 'reddit', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"reddit:{d['id']}", None, d["id"], d["thread_id"], parent_native,
                d.get("depth"), d.get("author"), d.get("created_utc"), d.get("body"),
                d.get("score"),
                f"https://www.reddit.com{d['permalink']}" if d.get("permalink") else None,
                d.get("fetched_at"), d.get("raw_json"),
            ),
        )
        stats["replies"] += 1

    conn.commit()
    return stats


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="*", type=Path, help="JSONL files (default: data/raw/*.jsonl)")
    ap.add_argument("--db", help="SQLite path")
    ap.add_argument("--force", action="store_true", help="import even if validation reports errors")
    args = ap.parse_args(argv)

    paths = args.paths or sorted(RAW.glob("*.jsonl"))
    if not paths:
        print("no JSONL files found", file=sys.stderr)
        return 1

    conn = store.connect(args.db)
    migrated = migrate_legacy_reddit(conn)
    if migrated["posts"] or migrated["replies"]:
        print(f"migrated legacy reddit: {migrated}")

    total = {"post": 0, "reply": 0, "article": 0, "skipped": 0}
    failures = 0

    for path in paths:
        errors, warnings, _ = validate.validate(path)
        if errors and not args.force:
            failures += 1
            print(f"SKIP {path}: {len(errors)} validation errors")
            for e in errors[:5]:
                print(f"  {e}")
            continue
        stats = store.import_jsonl(conn, path)
        for k in total:
            total[k] += stats.get(k, 0)
        print(f"OK   {path.name}: {stats}  ({len(warnings)} warnings)")

    print(f"\nimported: {total}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
