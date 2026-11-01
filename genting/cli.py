"""Command line interface for collecting Genting discussion."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from . import config, db, render
from .sources import arctic


def log(message: str) -> None:
    print(message, file=sys.stderr)


def ingest_thread(conn, post_id: str, refresh: bool = True) -> tuple[dict, list[dict], bool]:
    """Fetch and store one thread plus its full comment tree.

    Returns (post, comments, was_new).
    """
    existing = db.get_thread(conn, post_id)
    if existing and not refresh:
        comments = db.get_comments(conn, post_id)
        return dict(existing), [dict(c) for c in comments], False

    post = arctic.fetch_post(post_id)
    db.upsert_thread(conn, post)
    conn.commit()

    comments = arctic.fetch_comments(post_id)
    for comment in comments:
        db.upsert_comment(conn, post_id, comment)
    conn.commit()

    return post, comments, existing is None


def cmd_ingest_thread(args) -> int:
    post_id = arctic.parse_post_id(args.url_or_id)
    conn = db.connect(args.db)
    run_id = db.start_run(conn, "reddit", "thread", post_id)
    try:
        post, comments, was_new = ingest_thread(conn, post_id, refresh=not args.no_refresh)
    except arctic.ArcticShiftError as exc:
        db.finish_run(conn, run_id, 0, f"error: {exc}")
        log(f"error: {exc}")
        return 1

    db.finish_run(conn, run_id, 1 + len(comments))
    state = "new" if was_new else "updated"
    log(
        f"{state}: r/{post['subreddit']} {post['id']} — "
        f"{len(comments)} comments "
        f"({sum(1 for c in comments if (c.get('depth') or 0) > 0)} nested replies)"
    )

    if not args.no_print:
        stored = db.get_thread(conn, post_id)
        stored_comments = db.get_comments(conn, post_id)
        print(render.render_thread(stored, stored_comments))
    return 0


def cmd_show_thread(args) -> int:
    conn = db.connect(args.db)
    thread = db.get_thread(conn, arctic.parse_post_id(args.thread_id))
    if thread is None:
        log(f"thread {args.thread_id} is not in the database")
        return 1
    comments = db.get_comments(conn, thread["id"])
    print(render.render_thread(thread, comments))
    return 0


def cmd_export_thread(args) -> int:
    conn = db.connect(args.db)
    thread = db.get_thread(conn, arctic.parse_post_id(args.thread_id))
    if thread is None:
        log(f"thread {args.thread_id} is not in the database")
        return 1
    comments = db.get_comments(conn, thread["id"])

    out = Path(args.out) if args.out else None
    if args.format == "md":
        text = render.render_thread(thread, comments)
        if out:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")
            log(f"wrote {out} ({len(text):,} chars)")
        else:
            print(text, end="")
        return 0

    lines = [json.dumps({"type": "thread", **dict(thread)})]
    lines += [json.dumps({"type": "comment", **dict(c)}) for c in comments]
    payload = "\n".join(lines) + "\n"
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
        log(f"wrote {out} ({len(lines)} records)")
    else:
        print(payload, end="")
    return 0


def cmd_collect(args) -> int:
    conn = db.connect(args.db)
    subreddits = args.subreddit or config.SUBREDDITS
    keywords = args.keyword or config.KEYWORDS
    after = int(time.time()) - args.days * 86400

    seen: set[str] = set()
    threads_new = threads_seen = comments_new = errors = 0

    for subreddit in subreddits:
        for keyword in keywords:
            log(f"searching r/{subreddit} for {keyword!r} since {args.days}d ago")
            run_id = db.start_run(conn, "reddit", "search", f"r/{subreddit}:{keyword}")
            found = 0
            try:
                for post in arctic.search_posts(subreddit, keyword, after=after):
                    thread_id = post["id"]
                    if thread_id in seen:
                        continue
                    seen.add(thread_id)
                    found += 1

                    cached = db.get_thread(conn, thread_id)
                    if cached and not args.refresh:
                        threads_seen += 1
                        continue

                    try:
                        _, comments, _ = ingest_thread(conn, thread_id, refresh=args.refresh)
                    except arctic.ArcticShiftError as exc:
                        errors += 1
                        log(f"  ! {thread_id}: {exc}")
                        continue

                    was_new = cached is None
                    threads_new += int(was_new)
                    threads_seen += int(not was_new)
                    comments_new += len(comments)
                    log(f"  + {thread_id} {len(comments):>4} comments  {post.get('title', '')[:70]}")
                    time.sleep(config.REQUEST_DELAY)
            except arctic.ArcticShiftError as exc:
                errors += 1
                log(f"  ! search failed: {exc}")
            finally:
                db.finish_run(conn, run_id, found)

    log(
        f"done: {threads_new} new threads, {threads_seen} already stored, "
        f"{comments_new} new comments, {errors} errors"
    )
    return 0 if errors == 0 else 2


def cmd_list_threads(args) -> int:
    conn = db.connect(args.db)
    rows = conn.execute(
        """
        SELECT t.id, t.subreddit, t.created_utc, t.score, t.title,
               COUNT(c.id) AS stored_comments
        FROM threads t
        LEFT JOIN comments c ON c.thread_id = t.id
        GROUP BY t.id
        ORDER BY t.created_utc DESC
        LIMIT ?
        """,
        (args.limit,),
    ).fetchall()

    if not rows:
        log("database is empty — run collect or ingest-thread first")
        return 0

    for row in rows:
        print(
            f"{row['id']}  r/{row['subreddit']:<14} "
            f"{render.fmt_time(row['created_utc'])[:10]}  "
            f"{row['stored_comments']:>4} comments  "
            f"{row['score']:>5} pts  {row['title'][:80]}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="genting", description=__doc__)
    parser.add_argument("--db", help="SQLite path (default: data/genting.db)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("ingest-thread", help="store one thread, all comments and sub-comments")
    p.add_argument("url_or_id", help="Reddit URL, t3_ id or bare post id")
    p.add_argument("--no-refresh", action="store_true", help="skip if already stored")
    p.add_argument("--no-print", action="store_true", help="do not print the transcript")
    p.set_defaults(func=cmd_ingest_thread)

    p = sub.add_parser("show-thread", help="print a stored thread as markdown")
    p.add_argument("thread_id")
    p.set_defaults(func=cmd_show_thread)

    p = sub.add_parser("export-thread", help="export a stored thread")
    p.add_argument("thread_id")
    p.add_argument("--format", choices=["md", "jsonl"], default="md")
    p.add_argument("--out", help="output path (default: stdout)")
    p.set_defaults(func=cmd_export_thread)

    p = sub.add_parser("collect", help="search configured subreddits and store matching threads")
    p.add_argument("--days", type=int, default=config.DEFAULT_LOOKBACK_DAYS)
    p.add_argument("--subreddit", action="append", help="override subreddit list (repeatable)")
    p.add_argument("--keyword", action="append", help="override keyword list (repeatable)")
    p.add_argument("--refresh", action="store_true", help="re-fetch threads already in the database")
    p.set_defaults(func=cmd_collect)

    p = sub.add_parser("list-threads", help="show stored threads")
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_list_threads)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
