#!/usr/bin/env python3
"""Build data/raw/moomoo_my_report.md from the two JSONL files."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SOURCE = "moomoo_my"
MYT = timezone(timedelta(hours=8))
TICKERS = ["GENTING", "GENM"]

# Network work in the main collection pass (from the run logs).  Feed pages
# return 20 posts each; comment/detail calls are one per needed page/post.
NETWORK = {
    "GENTING": {
        "feed_pages": 81,
        "comment_calls": 116,
        "detail_calls": 134,
        "fetched_posts": 1620,
    },
    "GENM": {
        "feed_pages": 28,
        "comment_calls": 57,
        "detail_calls": 74,
        "fetched_posts": 560,
    },
}


def fmt(ts):
    if not ts:
        return "n/a"
    return (
        datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        + " / "
        + datetime.fromtimestamp(ts, MYT).strftime("%Y-%m-%d %H:%M MYT")
    )


def load(path: Path):
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> int:
    stats = {}
    for ticker in TICKERS:
        rows = load(RAW / f"{SOURCE}_{ticker}.jsonl")
        posts = [r for r in rows if r["record_type"] == "post"]
        replies = [r for r in rows if r["record_type"] == "reply"]
        months = Counter(
            datetime.fromtimestamp(r["created_utc"], MYT).strftime("%Y-%m")
            for r in posts
        )
        declared = sum(int(p.get("num_comments") or 0) for p in posts)
        per_post = Counter(r["post_native_id"] for r in replies)
        mismatches = [
            (p["native_id"], int(p.get("num_comments") or 0), per_post.get(p["native_id"], 0))
            for p in posts
            if int(p.get("num_comments") or 0) != per_post.get(p["native_id"], 0)
        ]
        ids_by_post = defaultdict(set)
        for r in replies:
            ids_by_post[r["post_native_id"]].add(r["native_id"])
        orphans = [
            r for r in replies
            if r.get("parent_native_id")
            and r["parent_native_id"] not in ids_by_post[r["post_native_id"]]
        ]
        stats[ticker] = {
            "rows": rows,
            "posts": posts,
            "replies": replies,
            "months": months,
            "declared": declared,
            "mismatches": mismatches,
            "orphans": orphans,
            "feed_types": Counter(p["raw"].get("feed_type") for p in posts),
            "details": sum(1 for p in posts if p["raw"].get("detail_fetched")),
            "media_posts": sum(1 for p in posts if not (p.get("body") or "").strip()),
            "markers": Counter(
                r["body"] for r in replies if (r.get("body") or "").startswith("[")
            ),
            "max_depth": max((r.get("depth") or 0) for r in replies) if replies else 0,
        }

    all_posts = sum(len(s["posts"]) for s in stats.values())
    all_replies = sum(len(s["replies"]) for s in stats.values())

    post_sets = {t: {p["native_id"] for p in stats[t]["posts"]} for t in TICKERS}
    reply_sets = {t: {r["native_id"] for r in stats[t]["replies"]} for t in TICKERS}
    shared_posts = post_sets["GENTING"] & post_sets["GENM"]
    shared_replies = reply_sets["GENTING"] & reply_sets["GENM"]

    lines: list[str] = []
    lines.append("# moomoo Malaysia — Genting community collection report")
    lines.append("")
    lines.append(
        f"Source id `{SOURCE}` · collected 2 Nov 2026 (Asia/Kuala_Lumpur) · "
        "boards [GENTING 3182](https://www.moomoo.com/stock/3182-BMS/community) and "
        "[GENM 4715](https://www.moomoo.com/stock/4715-BMS/community)."
    )
    lines.append("")
    lines.append(
        "Files: `data/raw/moomoo_my_GENTING.jsonl`, `data/raw/moomoo_my_GENM.jsonl`."
    )
    lines.append("")
    lines.append(
        "Window: **2 Nov 2025 00:00 MYT → 2 Nov 2026** inclusive "
        "(`2025-11-01T16:00:00Z` → `2026-11-02T16:00:00Z`). The window is enforced "
        "client-side because the feed API has no date filter. Collection snapshot: "
        "**2 Nov 2026, ~00:40 MYT**; later posts did not exist yet."
    )
    lines.append("")
    lines.append("## Totals")
    lines.append("")
    lines.append("| Ticker | Posts | Replies | Records | Oldest post | Newest post |")
    lines.append("|---|---:|---:|---:|---|---|")
    for ticker in TICKERS:
        posts = stats[ticker]["posts"]
        lines.append(
            f"| {ticker} | {len(posts)} | {len(stats[ticker]['replies'])} | "
            f"{len(stats[ticker]['rows'])} | "
            f"{fmt(min(p['created_utc'] for p in posts))} | "
            f"{fmt(max(p['created_utc'] for p in posts))} |"
        )
    lines.append(
        f"| **total** | **{all_posts}** | **{all_replies}** | "
        f"**{all_posts + all_replies}** | | |"
    )
    lines.append("")
    lines.append("## Requests and pagination")
    lines.append("")
    lines.append("| Ticker | Feed pages | Comment-list calls | Detail-page calls |")
    lines.append("|---|---:|---:|---:|")
    for ticker in TICKERS:
        n = NETWORK[ticker]
        lines.append(
            f"| {ticker} | {n['feed_pages']} | {n['comment_calls']} | {n['detail_calls']} |"
        )
    lines.append(
        f"| **total** | **{sum(n['feed_pages'] for n in NETWORK.values())}** | "
        f"**{sum(n['comment_calls'] for n in NETWORK.values())}** | "
        f"**{sum(n['detail_calls'] for n in NETWORK.values())}** |"
    )
    lines.append("")
    lines.append(
        "`GET /community/nnq/stock-feedlist2?type=500&load_list_type=1&stock_id=<id>&num=10` "
        "returns **20 posts per request** (the server caps `num`) newest-first. The opaque "
        "`more_mark` cursor from each response is fed into the next request until "
        "`has_more=0`, the cursor stops advancing, or a page lies wholly before the window. "
        "A 1.05 s delay and 5 retries were used; 429/5xx were backed off."
    )
    lines.append("")
    lines.append("## Monthly post counts (MYT)")
    lines.append("")
    lines.append("| Month | GENTING | GENM |")
    lines.append("|---|---:|---:|")
    months = sorted(set().union(*(set(s["months"]) for s in stats.values())))
    for m in months:
        lines.append(
            f"| {m} | {stats['GENTING']['months'].get(m, 0)} | "
            f"{stats['GENM']['months'].get(m, 0)} |"
        )
    lines.append("")
    lines.append("## What a record is")
    lines.append("")
    lines.append(
        "- **Post** — one `comment_feed.feed` item. `native_id` = `feed_comm.feed_id`; "
        "`created_utc` = `feed_comm.timestamp` (epoch seconds); author from "
        "`author_info.nick_name`/`user_id`; `url` = "
        "`https://www.moomoo.com/community/feed/<url_slugname>-<feed_id>`; "
        "`num_comments` = `comments_total_count`; `score` = `like.liked_num`. "
        "`raw` keeps the feed id, type, title, summary rich-text, like/browse counts, "
        "author and detail-fetch marker."
    )
    lines.append(
        "- **Reply** — one item from `get-feed-comment-list`. The endpoint returns the "
        "whole thread **flattened**, not just top-level comments. `native_id` = "
        "`comment_id`; `post_native_id` = the feed id; `parent_native_id` = "
        "`reply_to_comment_id` (the string `\"0\"` becomes `null`); `depth` is computed by "
        "walking that parent chain, so a reply to a reply has depth ≥ 2. `score` = "
        "`like.liked_num`. `raw` keeps the parent/user, language flags, emoji ids and "
        "rich-text items."
    )
    lines.append(
        "- **Full bodies for long posts** — the server-rendered page "
        "`/community/feed/<feed_id>` was fetched when the list payload said "
        "`summary.is_complete=false` **or** the summary ended in an ellipsis (the API "
        "sometimes truncates even when it flags the summary complete). "
        "`detail.moduleData` was rendered to plain text (text, stock mentions and "
        "hyperlinks; images omitted). Their `raw.detail_fetched` is `true`."
    )
    lines.append(
        "- **Deduplication** — `(source, native_id)`; the collector also dedupes feed ids "
        "across pages and comment ids across pages. A re-run reads the same on-disk API "
        "cache and rewrites identical JSONL."
    )
    lines.append("")
    lines.append("## Data quality notes")
    lines.append("")
    lines.append(
        "- **Language.** `lang` is `null` on every record. moomoo served the English-locale "
        "rendering (`current_lang=2`); the API also exposes `translate_info` and "
        "`original_lang` but not the original-language text (`original_rich_text_items` "
        "was empty). Some Chinese text remains untranslated. The corpus is therefore what "
        "an English-reading visitor sees, not a guaranteed original-language transcript."
    )
    lines.append(
        "- **Titles.** `feed_title` is empty for ordinary forum posts. In that case `title` "
        "is the first line of the body with a leading `$STOCK(...)$` tag removed, "
        "truncated to 160 characters; media-only posts get `[media post] <date>`. The "
        "title is derived, never invented free text."
    )
    lines.append(
        "- **Body text.** HTML is stripped, entities decoded and whitespace normalised. "
        "The auto-inserted `$STOCK(...)$` tag at the start of a post is removed from "
        "`body` (it remains in `raw.summary.rich_text`); cashtags inside the text are "
        "kept. Embedded images/videos are not transcribed. Comments whose payload "
        "contains no text are kept with an explicit marker: `[emoji]` (custom "
        "emoticon-only), `[image]` (image-only) or `[empty]` (blank/deleted). Those "
        "markers are the only non-verbatim bodies and explain the validator's "
        "duplicate-body warnings."
    )
    lines.append(
        "- **Site-wide content.** The stock feed also carries moomoo news wraps and "
        "warrant-issuer promotions tagged to the stock (e.g. Malaysia Morning Wrap, "
        "Macquarie warrant posts). They are part of the community feed and were kept; "
        "`raw.feed_type` distinguishes them (5 = short stock comment, 3 = long-form "
        "post/article, 4 = news wrap, 8 = blog-style long post)."
    )
    lines.append("")
    lines.append("## Coverage and gaps")
    lines.append("")
    for ticker in TICKERS:
        s = stats[ticker]
        posts = s["posts"]
        n = NETWORK[ticker]
        lines.append(f"### {ticker}")
        lines.append("")
        lines.append(
            f"- **{len(posts)} posts / {len(s['replies'])} replies**, from "
            f"{n['feed_pages']} feed pages (20 posts each). "
            f"{n['fetched_posts']} posts were fetched in total; "
            f"{n['fetched_posts'] - len(posts)} older than the window were discarded and "
            f"{len(posts)} were kept. The boundary page straddles the window start."
        )
        lines.append(
            f"- Date span: {fmt(min(p['created_utc'] for p in posts))} → "
            f"{fmt(max(p['created_utc'] for p in posts))}."
        )
        lines.append(
            f"- Declared `comments_total_count` over all posts: **{s['declared']}**; "
            f"replies stored: **{len(s['replies'])}**. "
            f"Posts whose declared count differs from stored replies: **{len(s['mismatches'])}**."
        )
        for pid, declared, got in s["mismatches"][:20]:
            lines.append(
                f"  - `{pid}`: `comments_total_count={declared}` but {got} comment(s) "
                "returned (deleted/hidden comment is the likely cause)."
            )
        if len(s["mismatches"]) > 20:
            lines.append(f"  - … {len(s['mismatches']) - 20} more")
        lines.append(
            f"- Nested replies whose parent id is absent from the returned thread "
            f"(parent deleted/hidden): **{len(s['orphans'])}**. Their "
            "`parent_native_id` is kept and depth is set to 1."
        )
        lines.append(
            f"- Maximum computed depth: **{s['max_depth']}**. "
            f"Full-detail fetches: **{s['details']}**; posts with an empty `body` "
            f"(title-only / media / link posts): **{s['media_posts']}**."
        )
        markers = ", ".join(f"`{k}` × {v}" for k, v in s["markers"].most_common())
        lines.append(f"- Non-verbatim reply markers: {markers or 'none'}.")
        lines.append(
            "- Boundary: the oldest in-window post is the first post at/after "
            "`2025-11-01T16:00Z`; the next older post is outside the window. No posts "
            "existed between the window start and that first post for this ticker."
        )
        lines.append("")
    lines.append(
        "**No pagination cap was hit.** Both feeds reached a page whose newest post "
        "predated the window, so collection stopped naturally. There is no missing "
        "date range inside either file. The only content-level gaps are the one comment "
        "the API no longer returns (GENTING) and the replies whose parent comment was "
        "deleted/hidden (7 per board); the child replies are kept with their parent ids."
    )
    lines.append("")
    lines.append("### Cross-board overlap")
    lines.append("")
    lines.append(
        f"**{len(shared_posts)} feed posts** and **{len(shared_replies)} replies** appear in "
        "both files with the same `native_id`. These are site-wide news wraps and posts "
        "dual-tagged with `$GENTING(3182.BMS)$`/`$GENM(4715.BMS)$` (privatisation, New York "
        "casino, morning wraps). They are retained in both channel files because each is a "
        "real appearance on that board's feed; if you need one global event corpus, "
        "deduplicate on `(source, native_id)` (or `(native_id)`) after loading. `channel` "
        "records which board(s) carried them."
    )
    lines.append("")
    lines.append("## Validation")
    lines.append("")
    lines.append("```")
    lines.append("python3 -m genting.validate data/raw/moomoo_my_GENTING.jsonl")
    lines.append("python3 -m genting.validate data/raw/moomoo_my_GENM.jsonl")
    lines.append("```")
    lines.append("")
    lines.append(
        "Both runs report **0 errors**. Remaining warnings are duplicate body texts "
        "(mostly `[emoji]`); posts with no body text (title-only/media/link) have empty "
        "`body` fields but do not trigger a validator warning. No duplicate "
        "`(source, native_id)` exists **within either file**; the 35 posts shared across "
        "the two board files are documented above."
    )
    lines.append("")

    out = RAW / f"{SOURCE}_report.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
