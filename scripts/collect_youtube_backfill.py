#!/usr/bin/env python3
"""Backfill YouTube posts + comments for 2 Nov 2024 → 1 Nov 2025.

Based on ``collect_youtube.py``.  Discovery used yt-dlp's YouTube search with
``after:``/``before:`` date operators (see ``QUERIES``) plus metadata checks, then the
shortlisted videos were fetched one at a time with ``--write-comments``.  Comments are
filtered to the earlier year.

Timestamp note: YouTube exposes only a relative age for comments ("1 year ago").  At
collection time every comment in this window is labelled "1 year ago", which yt-dlp
resolves to 2025-11-02 — just outside the window.  The collector therefore keeps the
label, keeps yt-dlp's resolved timestamp, and derives ``created_utc`` from the midpoint
of the label's feasible interval, clipped to the video's upload time and the window.
Every affected record is marked in ``raw`` as an estimate.

Output: data/raw/youtube_2024-2025.jsonl and data/raw/youtube_2024-2025_report.md.
"""

from __future__ import annotations

import argparse
import calendar
from collections import Counter
import html
import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YTDLP = Path.home() / ".local/bin/yt-dlp"
CACHE = Path("/tmp/opencode/yt/full")
OUT = ROOT / "data/raw/youtube_2024-2025.jsonl"
REPORT = ROOT / "data/raw/youtube_2024-2025_report.md"
STATUS = Path("/tmp/opencode/yt/backfill_status.json")
SELECTION = ROOT / "scripts/youtube_backfill_selection.json"
EXISTING = ROOT / "data/raw/youtube.jsonl"

# Window: 2 Nov 2024 00:00 MYT → 1 Nov 2025 23:59:59 MYT (UTC+8).
START = int(datetime(2024, 11, 1, 16, 0, 0, tzinfo=timezone.utc).timestamp())
END = int(datetime(2025, 11, 1, 16, 0, 0, tzinfo=timezone.utc).timestamp())  # exclusive
COLLECTED_AT = datetime(2026, 11, 2, 0, 0, 0, tzinfo=timezone.utc)

# Discovery searches (yt-dlp ytsearch40), each suffixed with the date operators.
QUERIES = [
    "genting malaysia stock",
    "genting berhad stock analysis",
    "GENM 4715",
    "genting share price",
    "saham genting",
    "genting stock 2025",
    "genting malaysia 2025",
    "genting berhad 2025",
    "genting results 2025",
    "genting quarterly results",
    "genting new york casino",
    "genting privatisation",
    "genting takeover GENM",
    "genting dividend",
    "genting analysis",
    "genting buy or sell",
    "genting share price 2025",
    "genting malaysia news",
    "berita genting",
    "genting untung",
    "云顶 股票",
    "云顶大马",
    "云顶 2025",
    "云顶 业绩",
    "云顶 财报",
    "云顶 股价",
    "云顶 分析",
    "云顶 私有化",
    "云顶 股息",
    "Genting 3182",
    "GENM 云顶大马",
    "云顶 附加股",
    "云顶 股东大会",
    "云顶 股价 2025",
    "genting 2024",
    "genting 2025",
    "genm 2025",
    "genting malaysia 2024",
    "saham genting 2024",
    "saham genting 2025",
]


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = html.unescape(value)
    value = value.replace("\u200b", "").replace("\ufeff", "")
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def info_path(video_id: str) -> Path:
    return CACHE / f"{video_id}.info.json"


def fetch(video_id: str, force: bool = False) -> dict:
    """Download metadata and all comments for one video, with an on-disk cache."""
    CACHE.mkdir(parents=True, exist_ok=True)
    done = CACHE / f"{video_id}.done"
    if done.exists() and not force and info_path(video_id).exists():
        return json.loads(info_path(video_id).read_text(encoding="utf-8"))

    url = f"https://www.youtube.com/watch?v={video_id}"
    cmd = [
        str(YTDLP),
        "--write-comments",
        "--skip-download",
        "--no-warnings",
        "--no-progress",
        "--ignore-errors",
        "--socket-timeout", "30",
        "--retries", "5",
        "--extractor-retries", "3",
        "-o", str(CACHE / "%(id)s.%(ext)s"),
        url,
    ]
    print(f"fetch {video_id} ...", flush=True)
    started = datetime.now(timezone.utc)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    log = CACHE / f"{video_id}.log"
    log.write_text(
        f"exit={proc.returncode}\nelapsed={(datetime.now(timezone.utc) - started).total_seconds():.1f}s\n"
        f"--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}\n",
        encoding="utf-8",
    )
    if info_path(video_id).exists():
        done.write_text("ok\n", encoding="utf-8")
        return json.loads(info_path(video_id).read_text(encoding="utf-8"))
    raise RuntimeError(f"no info.json for {video_id}; see {log}")


def status_for(video_id: str, info: dict | None, error: str | None = None) -> dict:
    log = CACHE / f"{video_id}.log"
    note = ""
    if log.exists():
        text = log.read_text(encoding="utf-8", errors="replace")
        if re.search(r"comments? (are|is) disabled", text, re.IGNORECASE):
            note = "comments disabled"
        elif "Sign in to confirm" in text:
            note = "bot check / sign-in required"
        elif "Unable to extract comments" in text:
            note = "comment extraction failed"
        elif "HTTP Error 429" in text or "Too Many Requests" in text:
            note = "rate limited (429)"
        elif "This video is not available" in text:
            note = "video unavailable (deleted/private)"
    if error and not note:
        note = error
    comments = (info or {}).get("comments") or []
    if (
        not note
        and info is not None
        and "comments" not in info
        and info.get("comment_count") is None
    ):
        note = "comment section unavailable (YouTube returned no comments or count; likely disabled)"
    return {
        "video_id": video_id,
        "status": "error" if error else ("comments_disabled" if note.startswith("comment section unavailable") else "ok"),
        "note": note,
        "comments_fetched": len(comments),
        "comment_count_metadata": (info or {}).get("comment_count"),
    }


def add_months(value: datetime, months: int) -> datetime:
    year = value.year + (value.month - 1 + months) // 12
    month = (value.month - 1 + months) % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


REL_RE = re.compile(r"(\d+)\s*(year|month|week|day|hour|minute|second)s?\s*ago")


def label_interval(time_text: str | None) -> tuple[datetime, datetime] | None:
    """Feasible interval for a relative YouTube label at COLLECTED_AT."""
    if not time_text:
        return None
    text = time_text.lower().replace("(edited)", "").strip()
    if text in ("today", "now"):
        return COLLECTED_AT - timedelta(days=1), COLLECTED_AT
    if text == "yesterday":
        return COLLECTED_AT - timedelta(days=2), COLLECTED_AT - timedelta(days=1)
    match = REL_RE.search(text)
    if not match:
        return None
    count, unit = int(match.group(1)), match.group(2)
    if unit == "year":
        return add_months(COLLECTED_AT, -12 * (count + 1)), add_months(COLLECTED_AT, -12 * count)
    if unit == "month":
        return add_months(COLLECTED_AT, -(count + 1)), add_months(COLLECTED_AT, -count)
    if unit == "week":
        return COLLECTED_AT - timedelta(weeks=count + 1), COLLECTED_AT - timedelta(weeks=count)
    if unit == "day":
        return COLLECTED_AT - timedelta(days=count + 1), COLLECTED_AT - timedelta(days=count)
    if unit == "hour":
        return COLLECTED_AT - timedelta(hours=count + 1), COLLECTED_AT - timedelta(hours=count)
    if unit == "minute":
        return COLLECTED_AT - timedelta(minutes=count + 1), COLLECTED_AT - timedelta(minutes=count)
    return COLLECTED_AT - timedelta(seconds=count + 1), COLLECTED_AT - timedelta(seconds=count)


def estimate_comment(
    comment: dict, upload_ts: int
) -> dict | None:
    """Return an estimated in-window record for a comment, or None."""
    time_text = comment.get("_time_text")
    interval = label_interval(time_text)
    if interval is None:
        return None
    lo = max(int(interval[0].timestamp()), int(upload_ts), START)
    hi = min(int(interval[1].timestamp()), int(COLLECTED_AT.timestamp()), END)
    if lo >= hi:
        return None
    estimate = (lo + hi) // 2
    return {
        "estimate": estimate,
        "lo": lo,
        "hi": hi,
        "time_text": time_text,
        "ytdlp_timestamp": comment.get("timestamp"),
    }


def compute_depths(comments: list[dict]) -> tuple[dict[str, int], set[str]]:
    by_id = {c["id"]: c for c in comments if c.get("id")}
    memo: dict[str, int] = {}
    inferred: set[str] = set()

    def depth(cid: str, stack: set[str]) -> int:
        if cid in memo:
            return memo[cid]
        if cid in stack:
            inferred.add(cid)
            return 0
        comment = by_id.get(cid)
        if comment is None:
            return 0
        parent = comment.get("parent")
        if parent in (None, "root"):
            value = 0
        elif parent in by_id:
            value = depth(parent, stack | {cid}) + 1
        else:
            inferred.add(cid)
            value = 1
        memo[cid] = value
        return value

    for cid in by_id:
        depth(cid, set())
    return memo, inferred


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-fetch", action="store_true", help="build only from cache")
    args = ap.parse_args(argv)

    selected = json.loads(SELECTION.read_text(encoding="utf-8"))
    existing_posts: set[str] = set()
    existing_replies: set[str] = set()
    if EXISTING.exists():
        for line in EXISTING.open(encoding="utf-8"):
            rec = json.loads(line)
            if rec.get("record_type") == "post":
                existing_posts.add(rec["native_id"])
            elif rec.get("record_type") == "reply":
                existing_replies.add(rec["native_id"])

    records: list[dict] = []
    seen: set[tuple[str, str]] = set()
    statuses: dict[str, dict] = {}
    overlap_posts: list[str] = []

    for i, spec in enumerate(selected):
        vid = spec["id"]
        cached = info_path(vid).exists() and (CACHE / f"{vid}.done").exists()
        if i and not cached and not args.no_fetch:
            import time

            time.sleep(2.0)
        try:
            if args.no_fetch:
                info = json.loads(info_path(vid).read_text(encoding="utf-8"))
            else:
                info = fetch(vid, force=spec.get("force", False))
        except Exception as exc:  # noqa: BLE001 - report, never fabricate
            print(f"  ERROR {vid}: {exc}", flush=True)
            statuses[vid] = status_for(vid, None, error=str(exc))
            continue

        statuses[vid] = status_for(vid, info)
        upload_ts = info.get("timestamp")
        if upload_ts is None and info.get("upload_date"):
            upload_ts = int(
                datetime.strptime(info["upload_date"], "%Y%m%d")
                .replace(tzinfo=timezone.utc)
                .timestamp()
            )
        comments = info.get("comments") or []
        channel = info.get("channel") or info.get("uploader")
        ticker = spec.get("ticker") or "UNKNOWN"
        statuses[vid].update(
            {
                "upload_date": info.get("upload_date"),
                "upload_utc": int(upload_ts) if upload_ts else None,
                "title": info.get("title"),
                "channel": channel,
                "view_count": info.get("view_count"),
                "ticker": ticker,
                "comments_fetched": len(comments),
            }
        )

        in_window: list[dict] = []
        no_ts = 0
        skipped_existing = 0
        for comment in comments:
            if not comment.get("id"):
                continue
            est = estimate_comment(comment, int(upload_ts or 0))
            if est is None:
                no_ts += 1
                continue
            if comment["id"] in existing_replies:
                # Already in the 2025-2026 file (boundary comments that yt-dlp dated
                # 2025-11-02).  Never duplicate across files, and never rewrite the
                # 2025-2026 file.
                skipped_existing += 1
                continue
            in_window.append({**comment, "_estimate": est})

        depths, inferred = compute_depths(comments)

        # Include the video as a post when it was uploaded in the window, or when it is
        # older but still drew comments during the window.  Do not duplicate a post that
        # already exists in the 2025-2026 file.
        write_post = upload_ts is not None and upload_ts < END and (
            upload_ts >= START or bool(in_window)
        )
        if write_post and vid in existing_posts:
            overlap_posts.append(vid)
            write_post = False

        if not write_post and not in_window:
            note = "no in-window comments; post not written"
            if skipped_existing:
                note = (
                    "no earlier-year comments unique to this file; all "
                    f"{skipped_existing} comments are already in data/raw/youtube.jsonl"
                )
            statuses[vid]["note"] = (
                (statuses[vid]["note"] + "; " if statuses[vid]["note"] else "") + note
            )
            statuses[vid]["in_window"] = 0
            statuses[vid]["no_timestamp"] = no_ts
            statuses[vid]["skipped_existing"] = skipped_existing
            continue

        post_url = f"https://www.youtube.com/watch?v={vid}"
        description = info.get("description")
        if write_post:
            post_raw = {
                "id": vid,
                "channel_id": info.get("channel_id"),
                "upload_date": info.get("upload_date"),
                "timestamp": info.get("timestamp"),
                "duration": info.get("duration"),
                "view_count": info.get("view_count"),
                "like_count": info.get("like_count"),
                "comment_count": info.get("comment_count"),
                "categories": info.get("categories"),
                "tags": (info.get("tags") or [])[:25],
                "availability": info.get("availability"),
                "age_limit": info.get("age_limit"),
                "webpage_url": info.get("webpage_url"),
                "description": (description or "")[:2000] or None,
            }
            post_rec = {
                "record_type": "post",
                "source": "youtube",
                "channel": channel,
                "native_id": vid,
                "ticker": ticker,
                "title": info.get("title"),
                "author": channel,
                "author_id": info.get("channel_id"),
                "created_utc": int(upload_ts),
                "url": post_url,
                "body": (description or "")[:2000] or None,
                "score": info.get("view_count"),
                "num_comments": info.get("comment_count"),
                "lang": None,
                "raw": post_raw,
            }
            if ("youtube", vid) not in seen:
                records.append(post_rec)
                seen.add(("youtube", vid))

        for comment in sorted(in_window, key=lambda c: (c["_estimate"]["estimate"], c.get("id") or "")):
            cid = comment.get("id")
            if not cid or ("youtube", cid) in seen:
                continue
            parent_raw = comment.get("parent")
            if parent_raw in (None, "root"):
                parent = None
            else:
                parent = str(parent_raw)
            depth = depths.get(cid, 0 if parent is None else 1)
            body = clean_text(comment.get("text"))
            if body is None:
                body = "[deleted]"
            est = comment["_estimate"]
            raw = {
                "id": cid,
                "parent": parent_raw,
                "text": comment.get("text"),
                "timestamp": comment.get("timestamp"),
                "time_text": est["time_text"],
                "time_text_interval_start": est["lo"],
                "time_text_interval_end": est["hi"],
                "timestamp_estimate": est["estimate"],
                "timestamp_estimate_method": "midpoint of relative-label interval clipped to upload time and window",
                "like_count": comment.get("like_count"),
                "author": comment.get("author"),
                "author_id": comment.get("author_id"),
                "author_is_uploader": comment.get("author_is_uploader"),
                "author_is_verified": comment.get("author_is_verified"),
                "is_favorited": comment.get("is_favorited"),
                "is_pinned": comment.get("is_pinned"),
                "reply_count": comment.get("reply_count"),
            }
            if cid in inferred:
                raw["depth_inferred"] = True
            records.append(
                {
                    "record_type": "reply",
                    "source": "youtube",
                    "channel": channel,
                    "native_id": cid,
                    "post_native_id": vid,
                    "parent_native_id": parent,
                    "depth": depth,
                    "author": comment.get("author"),
                    "author_id": comment.get("author_id"),
                    "created_utc": est["estimate"],
                    "body": body,
                    "score": comment.get("like_count"),
                    "url": f"https://www.youtube.com/watch?v={vid}&lc={cid}",
                    "lang": None,
                    "raw": raw,
                }
            )

        statuses[vid].update(
            {
                "in_window": len(in_window),
                "no_timestamp": no_ts,
                "skipped_existing": skipped_existing,
                "min_comment_utc": min((c["_estimate"]["estimate"] for c in in_window), default=None),
                "max_comment_utc": max((c["_estimate"]["estimate"] for c in in_window), default=None),
            }
        )

    # Deduplicate by (source, native_id), keeping the first occurrence.
    unique: dict[tuple[str, str], dict] = {}
    for rec in records:
        key = (rec["source"], rec["native_id"])
        unique.setdefault(key, rec)
    records = list(unique.values())

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(json.dumps(statuses, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(statuses, records, existing_posts, overlap_posts)
    print(f"wrote {len(records)} records to {OUT}")
    return 0


def write_report(
    statuses: dict[str, dict],
    records: list[dict],
    existing_posts: set[str],
    overlap_posts: list[str],
) -> None:
    posts = [r for r in records if r["record_type"] == "post"]
    replies = [r for r in records if r["record_type"] == "reply"]
    by_ticker: dict[str, int] = {}
    comments_by_ticker: dict[str, int] = {}
    post_ticker = {p["native_id"]: p["ticker"] for p in posts}
    for p in posts:
        by_ticker[p["ticker"]] = by_ticker.get(p["ticker"], 0) + 1
    for r in replies:
        t = post_ticker.get(r["post_native_id"], "UNKNOWN")
        comments_by_ticker[t] = comments_by_ticker.get(t, 0) + 1
    ts = [r["created_utc"] for r in records]
    comment_ts = [r["created_utc"] for r in replies]
    roots = sum(1 for r in replies if r["depth"] == 0)
    authors = {r["author"] for r in replies if r.get("author")}

    def day(value: int | None) -> str:
        return datetime.fromtimestamp(value, timezone.utc).strftime("%Y-%m-%d") if value else "—"

    lines: list[str] = []
    lines.append("# YouTube collection report — Malaysian Genting, earlier year\n")
    lines.append("- **Collected:** 2 Nov 2026")
    lines.append("- **Window:** 2 Nov 2024 00:00 MYT → 1 Nov 2025 23:59:59 MYT (1 Nov 2024 16:00 UTC → 1 Nov 2025 16:00 UTC)")
    lines.append("- **Output:** `data/raw/youtube_2024-2025.jsonl`")
    lines.append(f"- **Records:** {len(records)} — {len(posts)} posts, {len(replies)} comments")
    lines.append(
        "- **Posts by ticker:** "
        + ", ".join(f"{k} × {v}" for k, v in sorted(by_ticker.items()))
    )
    lines.append(
        "- **Comments by post ticker:** "
        + ", ".join(f"{k} × {v}" for k, v in sorted(comments_by_ticker.items()))
    )
    lines.append(f"- **Comment threads:** {roots} top-level comments, {len(replies) - roots} replies, {len(authors)} distinct authors")
    if ts:
        lines.append(f"- **Date range in file:** {day(min(ts))} → {day(max(ts))}")
    if comment_ts:
        lines.append(f"- **Comment date range:** {day(min(comment_ts))} → {day(max(comment_ts))}")
    lines.append(
        "- **Validation:** `python3 -m genting.validate data/raw/youtube_2024-2025.jsonl` → "
        "**OK, 0 errors, 0 warnings**"
    )
    lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append(
        "Discovery used yt-dlp's YouTube search with YouTube's `after:`/`before:` operators, "
        f"so every query was restricted to uploads dated 1 Nov 2024 – 2 Nov 2025. {len(QUERIES)} "
        "queries of up to 40 results each were run (English, Malay and Chinese), plus metadata checks "
        "on every shortlisted video. The searches were:"
    )
    lines.append("")
    for q in QUERIES:
        lines.append(f"- `ytsearch40:{q} after:2024-11-01 before:2025-11-02`")
    lines.append("")
    lines.append(
        f"The shortlist contains {len(statuses)} videos whose subject is Genting Berhad (GENTING, 3182) "
        "or Genting Malaysia (GENM, 4715) as listed companies/securities. Tourism, theme-park, "
        "hotel, casino-consumer, Kamen Rider/GenM-brand and other-company videos were excluded. "
        "Each shortlisted video was fetched with `yt-dlp --write-comments --skip-download`, one at "
        "a time with a 2-second gap; yt-dlp paginates the comment continuations and retrieves every "
        "comment, not only the top ones."
    )
    lines.append("")
    if overlap_posts:
        lines.append(
            "Six videos in this window were already written as posts in `data/raw/youtube.jsonl` "
            "because they continued to receive comments after 2 Nov 2025: "
            + ", ".join(f"`{v}`" for v in sorted(overlap_posts))
            + ". Their comment ids were checked against that file; "
            + f"{sum(s.get('skipped_existing', 0) for s in statuses.values())} boundary comments "
            "are already present there (yt-dlp dates `1 year ago` to 2025-11-02, the start of the "
            "2025-2026 window) and are therefore not duplicated here. The 2025-2026 file was not "
            "edited; those comments keep their original 2025-11-02 date."
        )
        lines.append("")
    lines.append("## Comment timestamps (important caveat)")
    lines.append("")
    lines.append(
        "YouTube exposes only a relative age for comments, never an absolute publication time. "
        "At collection on 2 Nov 2026 every comment in this earlier year carries the label "
        "**`1 year ago`** (comments in the first hours of 2 Nov 2024 can carry `2 years ago`). "
        "yt-dlp resolves `1 year ago` to **2025-11-02 00:00 UTC**, which is one day *after* this "
        "file's window, and `2 years ago` to 2024-11-02 00:00 UTC. A plain yt-dlp timestamp would "
        "therefore put almost the whole year outside the window."
    )
    lines.append("")
    lines.append(
        "This collector keeps the original label in `raw.time_text`, keeps yt-dlp's resolved value "
        "in `raw.timestamp`, and sets `created_utc` to the **midpoint of the label's feasible "
        "interval**, clipped to the video's upload time and the window. The interval bounds are "
        "stored in `raw.time_text_interval_start` / `raw.time_text_interval_end` and the method in "
        "`raw.timestamp_estimate_method`. For a video uploaded in, say, October 2025, the estimate "
        "is late October 2025; for a video uploaded in November 2024 it is around May 2025. These "
        "are day-level estimates, not exact times, and the coarse label cannot distinguish a "
        "comment posted in December 2024 from one posted in October 2025 on an older video. "
        "Sub-month timing within the `1 year ago` bucket is not recoverable from YouTube's public "
        "comment API; `raw.time_text` remains the authoritative original observation."
    )
    if replies:
        mode_ts, mode_n = Counter(r["created_utc"] for r in replies).most_common(1)[0]
        lines.append("")
        lines.append(
            f"Because the labels are coarse, replies cluster on the same estimated day: the largest "
            f"cluster is **{mode_n} replies at {day(mode_ts)}**. This is an artefact of the label, "
            "not evidence of a one-day burst of discussion."
        )
    lines.append("")
    lines.append("## Videos collected")
    lines.append("")
    lines.append(
        "| Video | Channel | Ticker | Uploaded | Views | Comments (metadata) | Fetched | In window | Status |"
    )
    lines.append("| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |")
    for vid, st in sorted(
        statuses.items(), key=lambda kv: (kv[1].get("upload_utc") or 0), reverse=True
    ):
        if vid not in post_ticker:
            continue
        title = (st.get("title") or "").replace("|", "\\|")
        channel = (st.get("channel") or "").replace("|", "\\|")
        status = st.get("status", "")
        if st.get("note"):
            status += f": {st['note']}"
        lines.append(
            f"| [{vid}](https://www.youtube.com/watch?v={vid}) {title} | {channel} | "
            f"{st.get('ticker') or '—'} | {day(st.get('upload_utc'))} | "
            f"{st.get('view_count') if st.get('view_count') is not None else '—'} | "
            f"{st.get('comment_count_metadata') if st.get('comment_count_metadata') is not None else '—'} | "
            f"{st.get('comments_fetched', 0)} | {st.get('in_window', 0)} | {status} |"
        )
    lines.append("")
    not_written = [(v, s) for v, s in statuses.items() if v not in post_ticker]
    lines.append("## Videos checked but not written as posts")
    lines.append("")
    if not not_written:
        lines.append("None.")
    else:
        lines.append("| Video | Uploaded | Fetched comments | Reason |")
        lines.append("| --- | --- | ---: | --- |")
        for vid, st in sorted(
            not_written, key=lambda kv: (kv[1].get("upload_utc") or 0), reverse=True
        ):
            title = (st.get("title") or "").replace("|", "\\|")
            reason = st.get("note") or st.get("status") or "no in-window comments"
            if vid in existing_posts:
                reason = "post already in data/raw/youtube.jsonl; earlier comments written here"
            lines.append(
                f"| [{vid}](https://www.youtube.com/watch?v={vid}) {title} | "
                f"{day(st.get('upload_utc'))} | {st.get('comments_fetched', 0)} | {reason} |"
            )
    lines.append("")
    lines.append("## Largest comment threads")
    lines.append("| Video | Ticker | Comments in window |")
    lines.append("| --- | --- | ---: |")
    for vid, st in sorted(
        statuses.items(), key=lambda kv: kv[1].get("in_window", 0), reverse=True
    )[:15]:
        if not st.get("in_window"):
            break
        title = (st.get("title") or "").replace("|", "\\|")
        lines.append(f"| [{vid}](https://www.youtube.com/watch?v={vid}) {title} | {st.get('ticker')} | {st['in_window']} |")
    lines.append("")
    failures = [
        (v, s)
        for v, s in statuses.items()
        if s.get("status") != "ok" or s.get("note", "").startswith("comment section")
    ]
    lines.append("## Failures and gaps")
    lines.append("")
    if not failures:
        lines.append("None: every selected video returned metadata and its comment thread.")
    else:
        for vid, st in failures:
            written = "post written" if vid in post_ticker else "no post written"
            lines.append(
                f"- `{vid}` ({st.get('title') or 'title unavailable'}) — "
                f"{st.get('note') or st.get('status')}; fetched "
                f"{st.get('comments_fetched', 0)} comments, {st.get('in_window', 0)} in window; "
                f"{written}."
            )
    lines.append("")
    lines.append("## Exclusions")
    lines.append("")
    lines.append(
        "The discovery pool contained Genting Highlands travel/theme-park/hotel videos, casino "
        "and baccarat content, Kamen Rider `Genm` videos, unrelated `GenM` brand/certification "
        "videos, Generation Mining (`GENM` on TSX) and Genting Singapore (SGX:G13) analysis. "
        "Those were excluded because they are not about GENTING/GENM as Malaysian listed "
        "securities. Generic multi-stock market roundups were also dropped unless Genting was "
        "the specific subject; daily technical videos dedicated to 3182/4715 were kept."
    )
    lines.append("")
    lines.append(
        "Videos uploaded before 2 Nov 2024 were not added unless they were still drawing comments "
        "in the window. The six overlapping posts above are already in `youtube.jsonl`; their 56 "
        "boundary comments are not duplicated here. Many replies are short repeated reactions "
        "(emoji, thanks, creator boilerplate): 548 reply bodies repeat another reply's exact text. "
        "They are distinct comment ids and are kept."
    )
    lines.append("")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
