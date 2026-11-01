"""Validate collector JSONL against docs/collector_contract.md."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

MIN_TS = int(datetime(2024, 10, 1, tzinfo=timezone.utc).timestamp())
MAX_TS = int(datetime.now(timezone.utc).timestamp()) + 86400

REQUIRED = {
    "post": ["source", "native_id", "created_utc", "ticker", "title"],
    "reply": ["source", "native_id", "post_native_id", "created_utc", "body"],
    "article": ["source", "url", "title", "published_utc", "body"],
}


def validate(path: Path) -> tuple[list[str], list[str], dict]:
    errors: list[str] = []
    warnings: list[str] = []
    stats = {
        "file": str(path),
        "records": 0,
        "by_type": Counter(),
        "by_source": Counter(),
        "by_ticker": Counter(),
        "min_ts": None,
        "max_ts": None,
        "empty_bodies": 0,
        "duplicate_bodies": 0,
    }
    ids: set[str] = set()
    post_ids: set[tuple[str, str]] = set()
    body_hashes: dict[tuple[str, str], str] = {}
    replies: list[dict] = []

    with path.open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_no}: invalid JSON ({exc})")
                continue

            kind = rec.get("record_type")
            if kind not in REQUIRED:
                errors.append(f"line {line_no}: unknown record_type {kind!r}")
                continue

            stats["records"] += 1
            stats["by_type"][kind] += 1
            stats["by_source"][rec.get("source")] += 1

            if kind in ("post", "reply"):
                key = (rec.get("source"), str(rec.get("native_id")))
                if key in ids:
                    errors.append(f"line {line_no}: duplicate id {key}")
                ids.add(key)

            for field in REQUIRED[kind]:
                if rec.get(field) in (None, "", []):
                    errors.append(f"line {line_no}: {kind} missing {field}")

            ts = rec.get("created_utc") if kind != "article" else rec.get("published_utc")
            if ts is not None:
                if not isinstance(ts, int):
                    errors.append(f"line {line_no}: timestamp is not an int epoch")
                elif not (MIN_TS <= ts <= MAX_TS):
                    warnings.append(
                        f"line {line_no}: timestamp {ts} outside window "
                        f"({datetime.fromtimestamp(ts, timezone.utc):%Y-%m-%d})"
                    )
                else:
                    stats["min_ts"] = ts if stats["min_ts"] is None else min(stats["min_ts"], ts)
                    stats["max_ts"] = ts if stats["max_ts"] is None else max(stats["max_ts"], ts)

            if kind == "post":
                post_ids.add((rec.get("source"), str(rec.get("native_id"))))
                stats["by_ticker"][rec.get("ticker")] += 1
            elif kind == "reply":
                replies.append(rec)

            if kind in ("reply", "article"):
                body = (rec.get("body") or "").strip()
                if not body or body in {"[deleted]", "[removed]"}:
                    stats["empty_bodies"] += 1
                    warnings.append(f"line {line_no}: empty/deleted body")
                else:
                    h = hash(body)
                    bkey = (rec.get("source"), h)
                    if bkey in body_hashes:
                        stats["duplicate_bodies"] += 1
                    body_hashes[bkey] = rec.get("native_id") or rec.get("url")

    # Referential integrity within the file (a reply may reference a post in another file).
    known_posts = post_ids
    for rec in replies:
        key = (rec.get("source"), str(rec.get("post_native_id")))
        if known_posts and key not in known_posts:
            warnings.append(
                f"reply {rec.get('native_id')}: post {rec.get('post_native_id')} not in this file"
            )

    return errors, warnings, stats


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+", type=Path)
    args = ap.parse_args(argv)

    total_errors = 0
    for path in args.paths:
        if not path.exists():
            print(f"missing: {path}", file=sys.stderr)
            total_errors += 1
            continue
        errors, warnings, stats = validate(path)
        total_errors += len(errors)
        span = ""
        if stats["min_ts"]:
            span = (
                f" | {datetime.fromtimestamp(stats['min_ts'], timezone.utc):%Y-%m-%d}"
                f" → {datetime.fromtimestamp(stats['max_ts'], timezone.utc):%Y-%m-%d}"
            )
        print(f"\n{path}")
        print(
            f"  records={stats['records']} "
            f"{dict(stats['by_type'])} tickers={dict(stats['by_ticker'])}{span}"
        )
        print(
            f"  empty_or_deleted={stats['empty_bodies']} "
            f"duplicate_body_texts={stats['duplicate_bodies']}"
        )
        for w in warnings[:10]:
            print(f"  WARN {w}")
        if len(warnings) > 10:
            print(f"  ... {len(warnings) - 10} more warnings")
        for e in errors[:20]:
            print(f"  ERROR {e}")
        if len(errors) > 20:
            print(f"  ... {len(errors) - 20} more errors")

    print(f"\n{'FAIL' if total_errors else 'OK'}: {total_errors} errors")
    return 1 if total_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
