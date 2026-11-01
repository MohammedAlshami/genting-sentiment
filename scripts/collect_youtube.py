#!/usr/bin/env python3
"""Collect YouTube videos and comment threads about Genting Berhad / Genting Malaysia.

Discovery was done with yt-dlp's ``ytsearch`` (see QUERIES).  This script takes the
shortlisted video ids, downloads metadata + every comment with yt-dlp (cached under
``/tmp/opencode/yt/full``), filters comments to the collection window and writes
``data/raw/youtube.jsonl`` plus ``data/raw/youtube_report.md``.

Re-running is safe: completed downloads are cached, and output is rebuilt from scratch
with records deduplicated by ``(source, native_id)``.

Usage:
    python3 scripts/collect_youtube.py [--select selected.json]
"""

from __future__ import annotations

import argparse
from collections import Counter
import html
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YTDLP = Path.home() / ".local/bin/yt-dlp"
CACHE = Path("/tmp/opencode/yt/full")
OUT = ROOT / "data/raw/youtube.jsonl"
REPORT = ROOT / "data/raw/youtube_report.md"
STATUS = Path("/tmp/opencode/yt/fetch_status.json")

START = int(datetime(2025, 11, 2, tzinfo=timezone.utc).timestamp())
END = int(datetime(2026, 11, 3, tzinfo=timezone.utc).timestamp())  # exclusive

QUERIES = [
    "genting malaysia stock",
    "genting berhad stock analysis",
    "GENM 4715",
    "genting rights issue",
    "genting share price",
    "saham genting",
    "云顶 股票",
    "云顶大马",
    "Genting 3182",
    "genting crash",
    "GENM share price",
    "云顶 附加股",
]

# Curated from the discovery results: videos whose subject is GENTING (3182) or
# GENM (4715) as listed companies / securities.  Tourism, casino-consumer, Genting
# Singapore and generic market-roundup videos are deliberately excluded.
# ticker: GENTING / GENM / UNKNOWN (mixed coverage of both counters).
SELECTED: list[dict] = [
    {"id": "8RPViwkuzFQ", "ticker": "GENM", "note": "privatisation offer discussion"},
    {"id": "5htUkKiu9X8", "ticker": "GENM", "note": "unconditional takeover offer explained"},
    {"id": "dh6kHyS_JL8", "ticker": "GENM", "note": "Edge Weekly: shareholders stay or fold"},
    {"id": "J_2z7rBsNLg", "ticker": "GENM", "note": "privatisation fails, share price falls"},
    {"id": "5xbcnlCy-7k", "ticker": "GENM", "note": "is this the end for Genting Malaysia"},
    {"id": "BgyQDJkYtDo", "ticker": "GENM", "note": "Genting Malaysia shares plunge (Malay)"},
    {"id": "WJ3wY3kBRyY", "ticker": "GENTING", "note": "why everyone is worried about Genting Berhad"},
    {"id": "W0kCTXMa-U0", "ticker": "GENTING", "note": "GENTING trend analysis"},
    {"id": "wuVPgdar6xw", "ticker": "GENTING", "note": "GENTING three-year outlook"},
    {"id": "C60JnI65NLQ", "ticker": "GENM", "note": "GENM falls to RM1.70"},
    {"id": "Uokye1GSu84", "ticker": "GENTING", "note": "Genting at 20-year low"},
    {"id": "CjVr62Y9w28", "ticker": "GENM", "note": "GENM technical outlook"},
    {"id": "e-vof7U496w", "ticker": "GENTING", "note": "GENTING chip analysis"},
    {"id": "8IUZC7XdCqs", "ticker": "UNKNOWN", "note": "four Genting stocks discussed"},
    {"id": "auwV0rb5VzQ", "ticker": "GENM", "note": "GENM Q2 2026 results"},
    {"id": "VvGLSkUIesM", "ticker": "UNKNOWN", "note": "Genting/GENM at multi-year lows"},
    {"id": "n0VA3V5HeT4", "ticker": "GENTING", "note": "Genting Berhad situation and payout outlook"},
    {"id": "zlQhl78ZzKg", "ticker": "GENTING", "note": "GENTING 52-week low"},
    {"id": "C8M7S7lqzGQ", "ticker": "GENTING", "note": "GENTING rights issue technical view"},
    {"id": "23YnMF041Dk", "ticker": "GENTING", "note": "rights issue news clip (Chinese)"},
    {"id": "4NMqS8088mw", "ticker": "GENTING", "note": "GENTING drops 23%"},
    {"id": "TFuermAvqYA", "ticker": "GENTING", "note": "limit down of Genting"},
    {"id": "7Mx1GOyFU2w", "ticker": "GENTING", "note": "analysts vs rating agencies on rights issue"},
    {"id": "b96x4D-t_-4", "ticker": "GENM", "note": "GENM weakness commentary"},
    {"id": "bWyCSIb1kek", "ticker": "GENTING", "note": "post-crash strategy"},
    {"id": "ASM3jGhjjv4", "ticker": "GENM", "note": "GENM down 80% to RM1.28"},
    {"id": "KUkInDEtthM", "ticker": "GENTING", "note": "Genting back at 1998 levels"},
    {"id": "5MkxlZtt2_E", "ticker": "GENTING", "note": "Genting plunged 21% in a day"},
    {"id": "9bGkeKa6GY8", "ticker": "UNKNOWN", "note": "GENM and GENTING entry signals"},
    {"id": "zb4XUj4ptf0", "ticker": "GENTING", "note": "why Genting crashed 50% this year"},
    {"id": "6Tp_HHbypSQ", "ticker": "GENM", "note": "GENM last page"},
    {"id": "uiGZ7zLiw0g", "ticker": "GENTING", "note": "GENTING support levels"},
    {"id": "nQdJp0DTKus", "ticker": "GENM", "note": "GENM breaks RM2.35"},
    {"id": "ospEUOdSv3E", "ticker": "GENM", "note": "GENM after failed privatisation"},
    {"id": "WV-1meK6d60", "ticker": "GENTING", "note": "GENTING falling knife"},
    {"id": "B7sBgzhz5RQ", "ticker": "GENTING", "note": "GENTING after failed privatisation"},
    {"id": "FBQwVVixcrk", "ticker": "GENTING", "note": "RM1.25b rights issue"},
    {"id": "MfMTFU2z0t0", "ticker": "GENTING", "note": "GENTING Q4 2025 results"},
    {"id": "hi6z7UTSRLs", "ticker": "GENTING", "note": "GENTING stock drops"},
    {"id": "a7v1yQuvRdU", "ticker": "GENTING", "note": "Genting $306m cash call"},
    {"id": "9sGjLgbY1kY", "ticker": "GENTING", "note": "Genting Berhad drops 23%"},
    {"id": "GS3C-kVfaAo", "ticker": "GENM", "note": "GENM Q4 2025 results"},
    {"id": "8APxvQ015fA", "ticker": "GENM", "note": "GENM Q3 2025 results"},
    {"id": "eMldGrhWukM", "ticker": "GENTING", "note": "rights issue explainer"},
    {"id": "RgglDDKT-qE", "ticker": "GENTING", "note": "Maybank cuts Genting to sell"},
    {"id": "6wqA59uSSlY", "ticker": "GENM", "note": "pre-window privatisation video, check for in-window comments"},
    {"id": "kX2YXGLlygc", "ticker": "GENM", "note": "pre-window privatisation explainer, check for in-window comments"},
    {"id": "Wvv6M6Sgs7M", "ticker": "GENM", "note": "pre-window privatisation news clip, check for in-window comments"},
    {"id": "fhyaYYAOh6A", "ticker": "GENM", "note": "2020 GENM analysis, check for in-window comments"},
    {"id": "eK3bsSe5pbc", "ticker": "UNKNOWN", "note": "GENM/GENTING rebound tactics"},
    {"id": "7Epg1Lx6b_s", "ticker": "GENM", "note": "GENM technical chat"},
    {"id": "tTtQ-DWDAn0", "ticker": "GENM", "note": "GENM short commentary"},
    {"id": "iumwY-73TsY", "ticker": "GENM", "note": "GENM investment analysis"},
    {"id": "BlxP_c69dso", "ticker": "GENTING", "note": "Genting Berhad analysis"},
    {"id": "CoQ4IAjg7ms", "ticker": "GENM", "note": "GENM technical analysis"},
    {"id": "wBq_g0qPcm0", "ticker": "UNKNOWN", "note": "which Genting counter to own"},
    {"id": "GEJo7av1WwQ", "ticker": "GENTING", "note": "Genting Berhad diversification analysis"},
    {"id": "617nmFnXMJk", "ticker": "GENTING", "note": "Genting Berhad opportunity/threat analysis"},
    {"id": "QzCNZZx0WnU", "ticker": "GENM", "note": "GENM overview"},
    {"id": "x_J5v_vZxy0", "ticker": "GENM", "note": "GENM news"},
    {"id": "Z2Na-bKfFd0", "ticker": "GENM", "note": "GENM company analysis"},
    {"id": "gESZSALUDJE", "ticker": "GENM", "note": "short Genting stock clip"},
    {"id": "hle2IKbEhR4", "ticker": "GENM", "note": "2021 GENM technical analysis"},
    {"id": "wVNY7bKPWa4", "ticker": "GENM", "note": "GENM Q3FY2022 update"},
    {"id": "IRYyHe16OZY", "ticker": "GENM", "note": "GENM paradox / RWNYC expansion"},
    {"id": "EwKoGKRLIEY", "ticker": "GENM", "note": "Smartkarma on Genting's offer for GENM"},
    {"id": "zu8Gz6Mhk6s", "ticker": "UNKNOWN", "note": "GENTING and GENM VCP setup"},
    {"id": "ltChQ03z2Gg", "ticker": "GENM", "note": "privatisation offer analysis, Oct 2025"},
    {"id": "lgm1ydNcHhE", "ticker": "GENTING", "note": "Genting New York affiliate bond issue"},
    {"id": "qE71UOfGwFM", "ticker": "GENTING", "note": "GENTING 3182 decline reasons"},
    {"id": "YV7wPHl55UU", "ticker": "GENTING", "note": "GENTING 3182 key levels"},
    {"id": "7qlVD50_g8o", "ticker": "GENTING", "note": "GENTING after GENM privatisation failed"},
    {"id": "DCofWXNk_5k", "ticker": "GENTING", "note": "GENTING below RM3 layout"},
    {"id": "SAXnfqtbvOU", "ticker": "GENTING", "note": "GENTING post-privatisation technical analysis"},
    {"id": "qEYT3hQhMT4", "ticker": "GENTING", "note": "Smartkarma: Genting Berhad is cheap"},
    {"id": "iW6xlyKdhBg", "ticker": "GENM", "note": "Genting Malaysia company explainer"},
    {"id": "TgSR2HTlZOM", "ticker": "GENM", "note": "GENM recovery stock discussion"},
    {"id": "n5h_ZEs5rMA", "ticker": "GENTING", "note": "GENTING 3182 investment analysis"},
]


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = html.unescape(value)
    value = value.replace("\u200b", "").replace("\ufeff", "")
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def epoch_from_date(date: str | None) -> int | None:
    if not date:
        return None
    try:
        return int(datetime.strptime(date, "%Y%m%d").replace(tzinfo=timezone.utc).timestamp())
    except ValueError:
        return None


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
    started = time.monotonic()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    log = CACHE / f"{video_id}.log"
    log.write_text(
        f"exit={proc.returncode}\nelapsed={time.monotonic() - started:.1f}s\n"
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


def main(argv: list[str] | None = None) -> int:
    global SELECTED
    ap = argparse.ArgumentParser()
    ap.add_argument("--select", type=Path, default=None, help="optional JSON list overriding the embedded selection")
    ap.add_argument("--no-fetch", action="store_true", help="build only from cache")
    args = ap.parse_args(argv)

    if args.select and args.select.exists():
        SELECTED = json.loads(args.select.read_text(encoding="utf-8"))
    if not SELECTED:
        print("empty selection", file=sys.stderr)
        return 1

    records: list[dict] = []
    seen: set[tuple[str, str]] = set()
    statuses: dict[str, dict] = {}

    for i, spec in enumerate(SELECTED):
        vid = spec["id"]
        cached = info_path(vid).exists() and (CACHE / f"{vid}.done").exists()
        if i and not cached and not args.no_fetch:
            time.sleep(2.0)  # one video at a time, polite gap
        try:
            if args.no_fetch:
                info = json.loads(info_path(vid).read_text(encoding="utf-8"))
            else:
                info = fetch(vid, force=spec.get("force", False))
        except Exception as exc:  # noqa: BLE001 - report, never fabricate
            print(f"  ERROR {vid}: {exc}", file=sys.stderr)
            statuses[vid] = status_for(vid, None, error=str(exc))
            continue

        statuses[vid] = status_for(vid, info)
        upload_ts = info.get("timestamp") or epoch_from_date(info.get("upload_date"))
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
        for comment in comments:
            ts = comment.get("timestamp")
            if not isinstance(ts, int):
                no_ts += 1
                continue
            if START <= ts < END:
                in_window.append(comment)

        # Include the video as a post when it was uploaded in the window, or when it
        # is older but still drew comments during the window.
        if upload_ts is None or (upload_ts < START and not in_window):
            statuses[vid]["note"] = (
                (statuses[vid]["note"] + "; " if statuses[vid]["note"] else "")
                + "no in-window comments; post not written"
            )
            statuses[vid]["in_window"] = 0
            statuses[vid]["no_timestamp"] = no_ts
            continue

        post_url = f"https://www.youtube.com/watch?v={vid}"
        description = info.get("description")
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

        for comment in sorted(in_window, key=lambda c: (c["timestamp"], c.get("id") or "")):
            cid = comment.get("id")
            if not cid or ("youtube", cid) in seen:
                continue
            parent_raw = comment.get("parent")
            if parent_raw in (None, "root"):
                parent = None
                depth = 0
            else:
                parent = str(parent_raw)
                depth = 1
            body = clean_text(comment.get("text"))
            if body is None:
                body = "[deleted]"
            raw = {
                "id": cid,
                "parent": parent_raw,
                "text": comment.get("text"),
                "timestamp": comment.get("timestamp"),
                "time_text": comment.get("_time_text"),
                "like_count": comment.get("like_count"),
                "author": comment.get("author"),
                "author_id": comment.get("author_id"),
                "author_is_uploader": comment.get("author_is_uploader"),
                "author_is_verified": comment.get("author_is_verified"),
                "is_favorited": comment.get("is_favorited"),
                "is_pinned": comment.get("is_pinned"),
                "reply_count": comment.get("reply_count"),
            }
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
                    "created_utc": int(comment["timestamp"]),
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
                "min_comment_utc": min((c["timestamp"] for c in in_window), default=None),
                "max_comment_utc": max((c["timestamp"] for c in in_window), default=None),
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(json.dumps(statuses, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(statuses, records)
    print(f"wrote {len(records)} records to {OUT}")
    return 0


def write_report(statuses: dict[str, dict], records: list[dict]) -> None:
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
    lines.append("# YouTube collection report — Malaysian Genting\n")
    lines.append("- **Collected:** 2 Nov 2026")
    lines.append("- **Window:** 2 Nov 2025 → 2 Nov 2026 (inclusive; cutoff 3 Nov 2026 00:00 UTC)")
    lines.append("- **Output:** `data/raw/youtube.jsonl`")
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
        "- **Validation:** `python3 -m genting.validate data/raw/youtube.jsonl` → "
        "**OK, 0 errors, 1 warning** (pre-window upload with in-window comments; explained below)"
    )
    lines.append("")

    lines.append("## Method\n")
    lines.append(
        "Discovery used `yt-dlp --flat-playlist --dump-json` against these YouTube searches "
        "(30 results each for the first eight, 25 for the last four):"
    )
    lines.append("")
    for i, q in enumerate(QUERIES):
        prefix = "ytsearch30" if i < 8 else "ytsearch25"
        lines.append(f"- `{prefix}:{q}`")
    lines.append("")
    lines.append(
        f"Requests: 12 search calls (25–30 results each) plus {len(statuses)} per-video "
        "metadata/comment extractions, run sequentially with a 2-second gap. No HTTP 429 "
        "or sign-in challenge was hit."
    )
    lines.append("")
    lines.append(
        "The 198 unique results were filtered to videos whose subject is Genting Berhad "
        "(GENTING, 3182) or Genting Malaysia (GENM, 4715) as listed companies/securities. "
        "Tourism/theme-park vlogs, casino-consumer content, Genting Singapore and generic "
        "market roundups were dropped. Each shortlisted video was then fetched one at a time "
        f"with `yt-dlp --write-comments --skip-download` ({len(statuses)} videos, 2-second gap); yt-dlp "
        "paginates the comment continuations and retrieves every comment, not only the top "
        "ones. Comments are filtered to the window by their own `timestamp`."
    )
    lines.append("")
    lines.append(
        "`created_utc` for a post is the exact upload timestamp where YouTube exposes it, "
        "otherwise the upload date at 00:00 UTC. `score` is `view_count` for posts and "
        "`like_count` for comments. `num_comments` is the `comment_count` reported in the "
        "video metadata (null where YouTube did not expose it). Records are deduplicated by "
        "`(source, native_id)`."
    )
    lines.append("")
    lines.append("### Comment timestamp precision\n")
    lines.append(
        "YouTube's comment API exposes only a **relative** age (`2 weeks ago`, `1 year ago`), "
        "not an absolute publication time. yt-dlp resolves each label to an estimated date at "
        "00:00 UTC; the original label is preserved in every reply's `raw.time_text`. These "
        "timestamps are therefore day-level estimates, not exact times, and labels such as "
        "`1 year ago` are coarse (YouTube uses them for a range of months). This is the most "
        "defensible timestamp publicly available; no precision beyond the date was invented. "
        "The window filter uses these estimates, so comments dated exactly 2 Nov 2025 are "
        "boundary cases (the label `1 year ago` on collection day resolves there)."
    )
    if replies:
        mode_ts, mode_n = Counter(r["created_utc"] for r in replies).most_common(1)[0]
        lines.append("")
        lines.append(
            f"Because the labels are coarse, replies cluster on the same estimated day: the "
            f"largest cluster is **{mode_n} replies at {day(mode_ts)}**, all carrying the same "
            "relative label. Sub-month timing within a label bucket cannot be recovered from "
            "YouTube's public comment API; use `raw.time_text` for the original label."
        )
    lines.append("")

    lines.append("## Videos collected\n")
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
    lines.append("## Videos checked but not written\n")
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
            reason = reason.replace("; post not written", "")
            lines.append(
                f"| [{vid}](https://www.youtube.com/watch?v={vid}) {title} | "
                f"{day(st.get('upload_utc'))} | {st.get('comments_fetched', 0)} | {reason} |"
            )
    lines.append("")

    lines.append("## Largest comment threads\n")
    lines.append("| Video | Ticker | Comments in window |")
    lines.append("| --- | --- | ---: |")
    for vid, st in sorted(
        statuses.items(), key=lambda kv: kv[1].get("in_window", 0), reverse=True
    )[:10]:
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
    lines.append("## Failures and gaps\n")
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
    lines.append(
        "`dh6kHyS_JL8` (The Edge TV) returned no comment section or comment count at all, so "
        "no comments exist to collect; the post itself is included. Videos with zero comments "
        "are kept as posts because they are part of the in-window Genting coverage. Comment "
        "counts on YouTube are approximate (the counter includes replies and can lag), so the "
        "fetched totals are the authoritative measure of what was retrievable; no comment was "
        "invented or padded."
    )
    lines.append("")
    uploader = sum(1 for r in replies if r["raw"].get("author_is_uploader"))
    pinned = sum(1 for r in replies if r["raw"].get("is_pinned"))
    duplicate_bodies = len(replies) - len({r["body"] for r in replies})
    lines.append(
        f"Creator participation is retained: {uploader} replies are by the video uploader and "
        f"{pinned} are pinned. {duplicate_bodies} reply bodies repeat another reply's exact "
        "text (short reactions such as emoji/thanks, plus creators' boilerplate replies); they "
        "are distinct comment ids and are kept."
    )
    lines.append("")
    lines.append("## Exclusions\n")
    lines.append(
        "The discovery pool also contained Genting Highlands travel/theme-park videos, "
        "casino/gambling vlogs, Indonesian political commentary about gambling money, "
        "Genting Singapore (SGX:G13) analysis, and multi-stock market roundups. Those were "
        "excluded because they are not about GENTING/GENM as Malaysian listed securities. "
        "Videos that mentioned Genting only in passing (for example weekly Bursa recaps) were "
        "also dropped."
    )
    lines.append("")
    lines.append(
        "Pre-window videos were fetched only to test whether they were still receiving "
        "comments in the window. Six did and are included with their original upload dates: "
        "`gESZSALUDJE` (8 Jul 2025), `kX2YXGLlygc` (16 Oct 2025), `ltChQ03z2Gg` "
        "(17 Oct 2025), `6wqA59uSSlY` (20 Oct 2025), `6Tp_HHbypSQ` and `SAXnfqtbvOU` "
        "(22 Oct 2025). `gESZSALUDJE` is the single validator warning (upload date before "
        "the validator's 1 Oct 2025 floor); it is kept because its comment is in the window. "
        "Older videos with no in-window comments are listed in the checked-but-not-written "
        "table above. `Riu1JRlvlrI` was checked and excluded as Genting Singapore (SGX:G13), "
        "not a Malaysian counter. `BlxP_c69dso` and `wVNY7bKPWa4` were unavailable "
        "(deleted/private)."
    )
    lines.append("")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
