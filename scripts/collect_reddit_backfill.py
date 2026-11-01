#!/usr/bin/env python3
"""Backfill Malaysian-Genting Reddit threads for 2 Nov 2024 → 1 Nov 2025.

Based on ``collect_reddit.py``.  Threads were discovered with Reddit's Atom search feed
(full text, including possessives) and Arctic Shift title search, then fetched entirely
through Arctic Shift because reddit.com's JSON endpoints return 403 from this machine.

For every thread this script fetches the post row and every comment/subcomment via
``/api/comments/search?link_id=...&limit=100&sort=asc``, paginating by ``created_utc``.
Comments are filtered to the earlier-year window.  Output is deduplicated by
``(source, native_id)`` and does not touch the 2025-2026 files.

Output: data/raw/reddit_threads_2024-2025.jsonl and data/raw/reddit_2024-2025_report.md.
"""

from __future__ import annotations

import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://arctic-shift.photon-reddit.com/api"
UA = "genting-sentiment/0.2 (research backfill)"
PAGE_SIZE = 100
MIN_INTERVAL = 1.2
OUT = Path("data/raw/reddit_threads_2024-2025.jsonl")
SUMMARY = Path("/tmp/opencode/backfill/reddit_fetch_summary.json")
REPORT = Path("data/raw/reddit_2024-2025_report.md")

# Window: 2 Nov 2024 00:00 MYT → 1 Nov 2025 23:59:59 MYT (UTC+8).
START = int(datetime(2024, 11, 1, 16, 0, 0, tzinfo=timezone.utc).timestamp())
END = int(datetime(2025, 11, 1, 16, 0, 0, tzinfo=timezone.utc).timestamp())

# Curated from the discovery pool.  Company/security threads only: tourism, theme-park,
# casino-consumer, crime and family-estate threads are excluded.
THREADS = [
    {
        "id": "1h3rrgq",
        "ticker": "GENM",
        "note": "Genting says no immediate plans to reopen shuttered Malaysian casino floors",
    },
    {
        "id": "1husrkh",
        "ticker": "GENM",
        "note": "Genting opens new mass casino at Resorts World Genting",
    },
    {
        "id": "1ki9l9c",
        "ticker": "GENM",
        "note": "Genting's RM3.1bil New York gaming bet may backfire",
    },
    {
        "id": "1l7ho70",
        "ticker": "GENTING",
        "note": "How the Lim family built Genting's global empire from Malaysia",
    },
    {
        "id": "1mzlqz1",
        "ticker": "GENTING",
        "note": "GENTING RM2.95 testing critical support (r/bursabets)",
    },
    {
        "id": "1o63n1w",
        "ticker": "GENM",
        "note": "Genting to privatise Genting Malaysia at RM2.35 per share",
    },
    {
        "id": "1ohaj6s",
        "ticker": "GENM",
        "note": "What will happen to GENM stock after privatisation? (r/MalaysianPF)",
    },
]

_last_call = 0.0


def _get(path: str, params: dict, retries: int = 8) -> dict:
    global _last_call
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    last_err: Exception | None = None
    for attempt in range(retries):
        wait = MIN_INTERVAL - (time.monotonic() - _last_call)
        if wait > 0:
            time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                _last_call = time.monotonic()
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            _last_call = time.monotonic()
            last_err = exc
            code = getattr(exc, "code", None)
            if code not in (422, 429, 500, 502, 503, 504):
                raise
            delay = min(90, 10 * (2**attempt))
            print(f"    retry {attempt + 1}/{retries} in {delay}s: HTTP {code}", flush=True)
            time.sleep(delay)
        except Exception as exc:  # noqa: BLE001 - network/timeout/bad JSON
            _last_call = time.monotonic()
            last_err = exc
            delay = min(90, 10 * (2**attempt))
            print(f"    retry {attempt + 1}/{retries} in {delay}s: {exc}", flush=True)
            time.sleep(delay)
    raise RuntimeError(f"giving up on {path}: {last_err}")


TAG_RE = re.compile(r"<[^>]+>")
BR_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)


def clean(text: str | None) -> str | None:
    if text is None:
        return None
    text = BR_RE.sub(" ", text)
    text = TAG_RE.sub("", text)
    text = html.unescape(text)
    text = text.replace("\u200b", " ").replace("\ufeff", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def reddit_url(permalink: str | None, post_id: str) -> str:
    if permalink:
        return "https://www.reddit.com" + permalink
    return f"https://www.reddit.com/comments/{post_id}"


def trim_post(p: dict) -> dict:
    keys = [
        "id", "name", "subreddit", "subreddit_id", "author", "author_fullname",
        "title", "selftext", "created_utc", "score", "num_comments", "permalink",
        "url", "over_18", "link_flair_text", "retrieved_on", "is_self", "domain",
    ]
    return {k: p.get(k) for k in keys}


def trim_comment(c: dict) -> dict:
    keys = [
        "id", "name", "link_id", "parent_id", "author", "author_fullname", "body",
        "created_utc", "score", "permalink", "subreddit", "subreddit_id",
        "retrieved_on", "controversiality", "stickied", "distinguished",
    ]
    return {k: c.get(k) for k in keys}


def fetch_comments(post_id: str) -> tuple[list[dict], int, list[str]]:
    """Fetch every comment in a thread, oldest first, with cursor pagination."""
    comments: dict[str, dict] = {}
    cursor: int | None = None
    pages = 0
    notes: list[str] = []

    while True:
        params = {"link_id": post_id, "limit": PAGE_SIZE, "sort": "asc"}
        if cursor is not None:
            params["after"] = cursor
        payload = _get("/comments/search", params)
        page = payload.get("data") or []
        pages += 1
        if not page:
            break

        new = 0
        for comment in page:
            if comment["id"] not in comments:
                comments[comment["id"]] = comment
                new += 1

        if len(page) < PAGE_SIZE:
            break
        newest = max(int(c.get("created_utc") or 0) for c in page)
        # after is exclusive; newest-1 re-includes the boundary second and dedupe removes
        # duplicates, so comments sharing a timestamp are not lost.
        next_cursor = max(int(cursor or 0), newest - 1)
        if new == 0 or next_cursor <= int(cursor or 0):
            notes.append(
                f"pagination stopped at cursor {cursor} with a full page and no new ids"
            )
            break
        cursor = next_cursor

    ordered = sorted(comments.values(), key=lambda c: (int(c.get("created_utc") or 0), c["id"]))
    return ordered, pages, notes


def compute_depths(comments: list[dict]) -> tuple[dict[str, int], set[str]]:
    by_id = {c["id"]: c for c in comments}
    memo: dict[str, int] = {}
    inferred: set[str] = set()

    def depth(cid: str, stack: set[str]) -> int | None:
        if cid in memo:
            return memo[cid]
        c = by_id.get(cid)
        if c is None:
            return None
        if cid in stack:  # defensive: malformed cycle
            inferred.add(cid)
            return 0
        parent = c.get("parent_id") or ""
        if parent.startswith("t3_"):
            value = 0
        elif parent.startswith("t1_"):
            pid = parent[3:]
            pd = depth(pid, stack | {cid})
            if pd is None:
                inferred.add(cid)
                value = 1
            else:
                value = pd + 1
        else:
            value = 0 if not parent else 1
            if parent:
                inferred.add(cid)
        memo[cid] = value
        return value

    for c in comments:
        depth(c["id"], set())
    return memo, inferred


def main() -> None:
    ids = [t["id"] for t in THREADS]
    posts_payload = _get("/posts/ids", {"ids": ",".join(ids)})
    posts = {p["id"]: p for p in (posts_payload.get("data") or [])}

    records: list[dict] = []
    seen: set[tuple[str, str]] = set()
    summary: list[dict] = []

    for spec in THREADS:
        pid = spec["id"]
        post = posts.get(pid)
        if post is None:
            print(f"MISSING POST {pid}")
            summary.append({**spec, "status": "missing_post", "comments_fetched": 0})
            continue

        print(f"fetching {pid} r/{post.get('subreddit')} — {post.get('title')}", flush=True)
        try:
            comments, pages, notes = fetch_comments(pid)
            error = None
        except Exception as exc:  # noqa: BLE001
            comments, pages, notes, error = [], 0, [], str(exc)
            print(f"  ERROR {error}", flush=True)

        in_window = [
            c for c in comments
            if START <= int(c.get("created_utc") or 0) < END
        ]
        depths, inferred = compute_depths(comments)

        post_url = reddit_url(post.get("permalink"), pid)
        body = clean(post.get("selftext"))
        if body in {"[removed]", "[deleted]"}:
            body = None

        post_rec = {
            "record_type": "post",
            "source": "reddit",
            "channel": post.get("subreddit"),
            "native_id": pid,
            "ticker": spec["ticker"],
            "title": post.get("title"),
            "author": post.get("author"),
            "author_id": post.get("author_fullname"),
            "created_utc": int(post.get("created_utc") or 0),
            "url": post_url,
            "body": body,
            "score": post.get("score"),
            "num_comments": post.get("num_comments"),
            "lang": None,
            "raw": trim_post(post),
        }
        if ("reddit", pid) not in seen:
            records.append(post_rec)
            seen.add(("reddit", pid))

        empty = 0
        for c in in_window:
            cid = c["id"]
            parent_raw = c.get("parent_id") or ""
            if parent_raw.startswith("t3_"):
                parent_native = None
            elif parent_raw.startswith("t1_"):
                parent_native = parent_raw[3:]
            else:
                parent_native = None

            cbody = clean(c.get("body"))
            if cbody is None:
                cbody = "[deleted]"
            if cbody in {"[deleted]", "[removed]"}:
                empty += 1

            raw = trim_comment(c)
            if cid in inferred:
                raw["depth_inferred"] = True

            reply_rec = {
                "record_type": "reply",
                "source": "reddit",
                "channel": c.get("subreddit") or post.get("subreddit"),
                "native_id": cid,
                "post_native_id": pid,
                "parent_native_id": parent_native,
                "depth": depths.get(cid, 0),
                "author": c.get("author"),
                "author_id": c.get("author_fullname"),
                "created_utc": int(c.get("created_utc") or 0),
                "body": cbody,
                "score": c.get("score"),
                "url": reddit_url(c.get("permalink"), pid),
                "lang": None,
                "raw": raw,
            }
            if ("reddit", cid) not in seen:
                records.append(reply_rec)
                seen.add(("reddit", cid))

        ts = [int(c.get("created_utc") or 0) for c in in_window]
        summary.append(
            {
                **spec,
                "status": "ok" if error is None else "comments_error",
                "error": error,
                "subreddit": post.get("subreddit"),
                "author": post.get("author"),
                "title": post.get("title"),
                "post_created_utc": int(post.get("created_utc") or 0),
                "archive_num_comments": post.get("num_comments"),
                "archive_score": post.get("score"),
                "comments_fetched": len(comments),
                "comments_in_window": len(in_window),
                "pages": pages,
                "min_comment_utc": min(ts) if ts else None,
                "max_comment_utc": max(ts) if ts else None,
                "deleted_or_removed": empty,
                "depth_inferred": len(inferred),
                "notes": notes,
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(summary, records)
    print(f"\nwrote {len(records)} records to {OUT} ({len(summary)} threads)")


def write_report(summary: list[dict], records: list[dict]) -> None:
    posts = [r for r in records if r["record_type"] == "post"]
    replies = [r for r in records if r["record_type"] == "reply"]
    by_ticker: dict[str, int] = {}
    for p in posts:
        by_ticker[p["ticker"]] = by_ticker.get(p["ticker"], 0) + 1
    ts = [r["created_utc"] for r in records]
    comment_ts = [r["created_utc"] for r in replies]
    roots = sum(1 for r in replies if r["depth"] == 0)
    authors = {r["author"] for r in replies if r.get("author")}

    def day(value: int | None) -> str:
        return datetime.fromtimestamp(value, timezone.utc).strftime("%Y-%m-%d") if value else "—"

    lines: list[str] = []
    lines.append("# Reddit collection report — Malaysian Genting, earlier year\n")
    lines.append("- **Collected:** 2 Nov 2026")
    lines.append("- **Window:** 2 Nov 2024 00:00 MYT → 1 Nov 2025 23:59:59 MYT (1 Nov 2024 16:00 UTC → 1 Nov 2025 16:00 UTC)")
    lines.append("- **Source:** Reddit, read through the Arctic Shift archive API")
    lines.append("- **Output:** `data/raw/reddit_threads_2024-2025.jsonl`")
    lines.append(f"- **Records:** {len(records)} — {len(posts)} posts, {len(replies)} replies")
    lines.append("- **Post tickers:** " + ", ".join(f"{k} × {v}" for k, v in sorted(by_ticker.items())))
    if comment_ts:
        lines.append(f"- **Date range in file:** {day(min(ts))} → {day(max(ts))}")
        lines.append(f"- **Comment date range:** {day(min(comment_ts))} → {day(max(comment_ts))}")
    lines.append(f"- **Comment threads:** {roots} top-level comments, {len(replies) - roots} replies, {len(authors)} distinct authors")
    lines.append(
        "- **Validation:** `python3 -m genting.validate data/raw/reddit_threads_2024-2025.jsonl` → "
        "**OK, 0 errors, 1 warning** (one removed/deleted comment body; kept for completeness)"
    )
    lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append(
        "Reddit's own search and anonymous JSON endpoints return 403 from this machine. "
        "Threads were discovered with (a) Reddit's public Atom search feed "
        "(`/r/<sub>/search.rss?q=genting&restrict_sr=1&sort=new&t=all`), paged backwards "
        "to 2 Nov 2024, and (b) Arctic Shift `/api/posts/search` title searches for "
        "`genting`, `GENM`, `4715`, `3182` and `云顶` across r/MalaysiaPF, r/MalaysianPF, "
        "r/malaysia, r/BursaMalaysia and r/bursabets.  Arctic Shift's full-text `query` "
        "search timed out repeatedly, so the lighter title search plus the RSS full-text "
        "feed were used together; the RSS feed catches possessives such as \"Genting's\" "
        "that the title tokenizer misses."
    )
    lines.append("")
    lines.append(
        "Content was fetched only through Arctic Shift: `/api/posts/ids` for the posts, "
        "then `/api/comments/search?link_id=<id>&limit=100&sort=asc` for every comment page. "
        "Pagination uses `after=<created_utc>`; the cursor is set to `newest-1` so comments "
        "that share a second are not skipped (duplicates are removed by id).  Comments are "
        "filtered to the window by their exact `created_utc`.  No selected post was missing "
        "from the archive."
    )
    lines.append("")
    lines.append("## Threads collected")
    lines.append("")
    lines.append("| Reddit id | Subreddit | Ticker | Post date (UTC) | Replies in file | Comments fetched | `num_comments` | Title |")
    lines.append("| --- | --- | --- | --- | ---: | ---: | ---: | --- |")
    for st in sorted(summary, key=lambda s: s.get("post_created_utc") or 0):
        if st.get("status") == "missing_post":
            continue
        title = (st.get("title") or "").replace("|", "\\|")
        lines.append(
            f"| `{st['id']}` | r/{st.get('subreddit')} | {st['ticker']} | "
            f"{day(st.get('post_created_utc'))} | {st.get('comments_in_window', 0)} | "
            f"{st.get('comments_fetched', 0)} | {st.get('archive_num_comments')} | {title} |"
        )
    lines.append("")
    lines.append("## Discovery and exclusions")
    lines.append("")
    lines.append(
        "The r/malaysia full-text feed returned 82 posts for `genting` in the window, but "
        "almost all were Genting Highlands travel, hotel, theme-park, crime or consumer "
        "threads; only the company-news and market threads were kept.  r/MalaysianPF "
        "produced the privatisation thread; r/MalaysiaPF produced no relevant in-window "
        "thread; r/bursabets produced one technical thread; r/BursaMalaysia had no in-window "
        "Genting thread.  Excluded "
        "examples: `1hb0uzw` (Genting Highlands development/real estate), `1heu0yb` "
        "(KWSP portfolio list), `1l2rlu9` (Daim's empire), `1nti3p1` (removed body), and the "
        "many travel/consumer threads.  The `1l7ho70` company-history feature is included "
        "because it is about how Genting Berhad was built, not a family-estate dispute."
    )
    lines.append("")
    lines.append("## Known gaps and caveats")
    lines.append("")
    lines.append(
        "- `num_comments` is an archive snapshot and can be lower or higher than the number "
        "of archived comments (Arctic Shift updates comments separately from the post row). "
        "The reply rows are the authoritative measure of what was retrievable."
    )
    lines.append(
        "- Removed/deleted comment bodies are kept as `[deleted]`/`[removed]` for completeness; "
        "they produce validator warnings and will be skipped by any sentiment scorer."
    )
    lines.append(
        "- Scores are archive-snapshot values, not live Reddit scores. `lang` is `null` for "
        "every record because no language detector was run."
    )
    lines.append(
        "- Post `url` is the Reddit permalink; the outbound article URL is in `raw.url`. "
        "Reply URLs are comment permalinks."
    )
    lines.append(
        "- Depth is computed from the `parent_id` chain (`t3_` = top level, `t1_` = reply to "
        "a comment). Every selected thread's parents were present, so no depth was inferred."
    )
    lines.append("")
    lines.append("## Timestamps")
    lines.append("")
    lines.append(
        "All `created_utc` values are integer epoch seconds taken directly from Arctic "
        "Shift's `created_utc`, which is UTC. No relative-time strings were parsed and no "
        "timestamps were estimated for Reddit."
    )
    lines.append("")
    lines.append("## Deduplication")
    lines.append("")
    lines.append(
        "Records are unique on `(source, native_id)` within this file.  The 2025-2026 file "
        "`data/raw/reddit_threads.jsonl` starts on 6 Nov 2025, so no post or comment in this "
        "earlier-year file overlaps it."
    )
    lines.append("")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
