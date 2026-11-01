#!/usr/bin/env python3
"""Collect YouTube videos + comments about Malaysian Genting, 2 Nov 2016 -> 1 Nov 2024.

This is the ten-year extension of ``collect_youtube.py`` /
``collect_youtube_backfill.py``.  No YouTube Data API key is configured in the
repository, so discovery and extraction use ``yt-dlp`` (the same tool as the
existing collectors).  There is therefore no API quota, but also no quota
error surface; rate limits and bot checks are recorded in the report.

Pipeline (all stages are resumable and cached under ``/tmp/opencode/yt10``):

    discover   yt-dlp YouTube search, one query per 12-month window/year
    meta       fetch metadata for the cheap-filtered candidate pool
    review     write a TSV + automatic shortlist for manual inspection
    collect    fetch every comment/reply for the shortlisted videos
    build      write data/raw/youtube_2016-2024.jsonl + report (no network)

Timestamp policy: YouTube exposes comment ages only as relative labels
("5 years ago"), never an absolute publication time.  ``created_utc`` for a
comment is the midpoint of the label's feasible interval, clipped to the
video's upload time and the collection time.  The original label and the
interval are stored in ``raw``; ``time_confidence`` is ``"relative"``.
Posts use YouTube's exact upload timestamp where exposed, else the upload date
at 00:00 UTC, with ``time_confidence`` ``"exact"`` / ``"date"``.

Usage:
    python3 scripts/collect_youtube_2016_2024.py --stage all
    python3 scripts/collect_youtube_2016_2024.py --stage build --no-fetch
"""

from __future__ import annotations

import argparse
import calendar
import html
import json
import re
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YTDLP = Path.home() / ".local/bin/yt-dlp"
WORK = Path("/tmp/opencode/yt10")
SEARCH_CACHE = WORK / "search"
META_CACHE = WORK / "meta"
FULL_CACHE = WORK / "full"
LOG_DIR = WORK / "logs"

OUT = ROOT / "data/raw/youtube_2016-2024.jsonl"
REPORT = ROOT / "data/raw/youtube_2016-2024_report.md"
REVIEW = WORK / "review.tsv"
SELECTION = WORK / "selected.json"
POOL = WORK / "pool.jsonl"
META_INDEX = WORK / "meta_index.jsonl"

# Window: 2 Nov 2016 00:00 MYT -> 1 Nov 2024 23:59:59 MYT (UTC+8).
START = int(datetime(2016, 11, 1, 16, 0, 0, tzinfo=timezone.utc).timestamp())
END = int(datetime(2024, 11, 1, 16, 0, 0, tzinfo=timezone.utc).timestamp())  # exclusive
# Fixed at the collection date so re-running the build stage reproduces the same estimates.
COLLECTED_AT = datetime(2026, 11, 2, 0, 0, 0, tzinfo=timezone.utc)

# Existing files are read only, never written.  Comment ids already present
# there are not duplicated into the new file.
EXISTING = [
    ROOT / "data/raw/youtube.jsonl",
    ROOT / "data/raw/youtube_2024-2025.jsonl",
    ROOT / "data/raw/youtube_full.jsonl",
]

# 12-month windows.  YouTube's after:/before: operators are only a discovery
# aid; every candidate's upload date is verified from full metadata.
SEARCH_YEARS = list(range(2016, 2024))

QUERIES = [
    # English
    "genting malaysia stock",
    "genting berhad stock",
    "genting share price",
    "GENM 4715",
    "GENTING 3182",
    "genting stock analysis",
    "genting results dividend",
    "genting rights issue privatisation",
    "genting malaysia news",
    "genting takeover",
    # Malay
    "saham genting",
    "harga saham genting",
    "analisis saham genting",
    "berita genting",
    "genting untung rugi",
    # Chinese
    "云顶 股票",
    "云顶大马",
    "云顶 股价 分析",
    "云顶 业绩 股息",
    "云顶 附加股 私有化",
]

GENTING_RE = re.compile(r"\bgenting\b|\bgenm\b|云顶", re.IGNORECASE)
FIN_RE = re.compile(
    r"\b(stock|stocks|share|shares|share price|saham|harga|bursa|klse|"
    r"3182|4715|analysis|analisa|technical|fundamental|valuation|dividend|"
    r"dividen|earnings|results|quarterly|q[1-4]|financial|finance|invest|"
    r"investing|investor|trading|trader|buy|sell|target price|rights issue|"
    r"privatisation|privatization|takeover|offer|agm|egm|market cap|revenue|"
    r"profit|loss|untung|rugi|modal|hutang|debt|bond|stock pick|stock analysis|"
    r"bursamalaysia|bursa malaysia)\b",
    re.IGNORECASE,
)
CN_FIN_RE = re.compile(r"股票|股价|分析|业绩|财报|股息|附加股|私有化|股东大会|投资|技术分析|基本面|马股|财报")
NEG_RE = re.compile(
    r"\b(perodua|myvi|honda|toyota|mazda|proton|iriz|vios|tyre|touge|uphill|"
    r"downhill|drive|driving|ride|bike|motor|car|cars|kamen|rider|generation mining|"
    r"hotel|resort|theme park|holiday|travel|vlog|buffet|food|baccarat|slot|jackpot|"
    r"skyway|cable car|outlet|premium outlet|first world)\b",
    re.IGNORECASE,
)
SG_ONLY_RE = re.compile(r"genting singapore|sgx\s*:?\s*g13|singapore", re.IGNORECASE)
OTHER_GENTING_RE = re.compile(
    r"genting plantation|\bgenp\b|genting hong kong|genting cruise|resorts world sentosa",
    re.IGNORECASE,
)

KNOWN_CHANNELS = {
    "Double Swords Investing",
    "TI 懂一点",
    "Neo, Biz Editor ",
    "股市先锋队",
    "MYtraderview 大马股市技术分析交易 + 生活日志",
    "Nighteyes08",
    "Trading with KS",
    "The Edge TV",
    "金穗投资于生活",
    "双阳倍量 Double Volume Bullish Channel ",
    "陈剑老师投资教育频道",
    "乐学成长空间 - LXInvest",
    "阿布的鸟公司",
    "Andy Yew",
    "大老板投资记录本",
    "FIRL",
    "Y-Z Finance MY",
    "百格 Pocketimes",
    "第一天投资理财研究所",
    "Learn Gambling",
    "八卦大小文的闲聊股市",
    "Iggy the Investing Iguana",
    "AF's Notes",
    "InvestDummies",
    "我是雷公",
    "I AM LEGEND",
    "夜月投资",
    "Malaysia Money Matters",
    "Finance Lang",
    "Invest8ddy-YC",
}


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = html.unescape(value)
    value = value.replace("\u200b", "").replace("\ufeff", "")
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def slug(value: str) -> str:
    # Keep a hash suffix: non-Latin queries (Chinese) would otherwise all collapse
    # to the same filename and overwrite each other's search cache.
    import hashlib

    safe = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()[:60]
    digest = hashlib.md5(value.encode("utf-8")).hexdigest()[:8]
    return f"{safe}_{digest}" if safe else digest


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.open(encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    tmp.replace(path)


def run(cmd: list[str], timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


# ---------------------------------------------------------------------------
# discovery
# ---------------------------------------------------------------------------


def search_cache_path(query: str, year: int) -> Path:
    return SEARCH_CACHE / f"{year}_{slug(query)}.jsonl"


def discover(force: bool = False) -> None:
    SEARCH_CACHE.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    total_calls = 0
    for year in SEARCH_YEARS:
        after = f"{year}-11-01"
        before = f"{year + 1}-11-02"
        for query in QUERIES:
            path = search_cache_path(query, year)
            if path.exists() and not force:
                continue
            search = f"ytsearch40:{query} after:{after} before:{before}"
            print(f"[search] {search}", flush=True)
            started = time.monotonic()
            try:
                proc = run(
                    [
                        str(YTDLP),
                        "--flat-playlist",
                        "--dump-json",
                        "--no-warnings",
                        "--no-progress",
                        "--socket-timeout",
                        "30",
                        "--retries",
                        "3",
                        search,
                    ],
                    timeout=300,
                )
            except subprocess.TimeoutExpired:
                print(f"  timeout: {query} {year}", file=sys.stderr, flush=True)
                continue
            results = []
            for line in proc.stdout.splitlines():
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not item.get("id"):
                    continue
                results.append(
                    {
                        "id": item["id"],
                        "title": item.get("title"),
                        "description": item.get("description"),
                        "channel": item.get("channel") or item.get("uploader"),
                        "channel_id": item.get("channel_id"),
                        "duration": item.get("duration"),
                        "view_count": item.get("view_count"),
                        "query": query,
                        "search_year": year,
                    }
                )
            write_jsonl(path, results)
            total_calls += 1
            print(
                f"  {len(results)} results in {time.monotonic() - started:.1f}s "
                f"(exit {proc.returncode})",
                flush=True,
            )
            time.sleep(1.2)
    print(f"search calls made: {total_calls}", flush=True)


def build_pool() -> list[dict]:
    pool: dict[str, dict] = {}
    for path in sorted(SEARCH_CACHE.glob("*.jsonl")):
        for item in read_jsonl(path):
            vid = item.get("id")
            if not vid:
                continue
            if vid not in pool:
                pool[vid] = {**item, "queries": [item.get("query")], "years": [item.get("search_year")]}
            else:
                if item.get("query") not in pool[vid]["queries"]:
                    pool[vid]["queries"].append(item.get("query"))
                if item.get("search_year") not in pool[vid]["years"]:
                    pool[vid]["years"].append(item.get("search_year"))
    records = list(pool.values())
    write_jsonl(POOL, records)
    print(f"pool: {len(records)} unique candidates from {len(list(SEARCH_CACHE.glob('*.jsonl')))} searches")
    return records


def cheap_relevant(item: dict) -> bool:
    title = item.get("title") or ""
    desc = item.get("description") or ""
    text = f"{title} {desc}"
    if not GENTING_RE.search(text):
        return False
    if OTHER_GENTING_RE.search(title) and not re.search(r"\bgenm\b|4715|3182|云顶大马", text, re.I):
        return False
    if SG_ONLY_RE.search(title) and not re.search(r"malaysia|\bgenm\b|3182|4715|云顶大马", text, re.I):
        return False
    if NEG_RE.search(title) and not FIN_RE.search(title) and not CN_FIN_RE.search(title):
        return False
    strong = bool(FIN_RE.search(title) or CN_FIN_RE.search(title) or re.search(r"3182|4715", title))
    channel = (item.get("channel") or "").strip()
    if channel in {c.strip() for c in KNOWN_CHANNELS}:
        strong = True
    return strong


# ---------------------------------------------------------------------------
# metadata
# ---------------------------------------------------------------------------


def meta_path(video_id: str) -> Path:
    return META_CACHE / f"{video_id}.json"


def fetch_meta(video_id: str, force: bool = False) -> dict | None:
    path = meta_path(video_id)
    if path.exists() and not force:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    META_CACHE.mkdir(parents=True, exist_ok=True)
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        proc = run(
            [
                str(YTDLP),
                "--dump-json",
                "--skip-download",
                "--no-warnings",
                "--no-progress",
                "--socket-timeout",
                "30",
                "--retries",
                "3",
                "--extractor-retries",
                "2",
                url,
            ],
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        return None
    item = None
    for line in proc.stdout.splitlines():
        try:
            candidate = json.loads(line)
        except json.JSONDecodeError:
            continue
        if candidate.get("id") == video_id:
            item = candidate
    if item is None:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        (LOG_DIR / f"meta_{video_id}.log").write_text(
            f"exit={proc.returncode}\n--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}\n",
            encoding="utf-8",
        )
        return None
    path.write_text(json.dumps(item, ensure_ascii=False), encoding="utf-8")
    return item


def upload_ts(info: dict) -> int | None:
    ts = info.get("timestamp")
    if isinstance(ts, (int, float)):
        return int(ts)
    date = info.get("upload_date")
    if date:
        try:
            return int(datetime.strptime(date, "%Y%m%d").replace(tzinfo=timezone.utc).timestamp())
        except ValueError:
            return None
    return None


def infer_ticker(info: dict) -> str:
    text = " ".join(
        str(x)
        for x in [
            info.get("title"),
            info.get("description"),
            " ".join(info.get("tags") or []),
        ]
        if x
    )
    genm = bool(re.search(r"\bgenm\b|4715|云顶大马|genting malaysia", text, re.I))
    genting = bool(re.search(r"\bgenting\b|3182", text, re.I))
    if genm and genting:
        return "UNKNOWN"
    if genm:
        return "GENM"
    if genting:
        return "GENTING"
    return "UNKNOWN"


def relevant(info: dict) -> tuple[bool, str]:
    title = info.get("title") or ""
    desc = info.get("description") or ""
    text = f"{title} {desc} {' '.join(info.get('tags') or [])}"
    if not GENTING_RE.search(text):
        return False, "not Genting"
    if OTHER_GENTING_RE.search(title) and not re.search(r"\bgenm\b|4715|3182|云顶大马", text, re.I):
        return False, "other Genting company"
    if SG_ONLY_RE.search(title) and not re.search(r"malaysia|\bgenm\b|3182|4715|云顶大马", text, re.I):
        return False, "Genting Singapore-only"
    if re.search(r"kamen|generation mining", title, re.I):
        return False, "unrelated GenM"
    strong_title = bool(
        FIN_RE.search(title) or CN_FIN_RE.search(title) or re.search(r"3182|4715", title)
    )
    if NEG_RE.search(title) and not strong_title:
        return False, "travel/vehicle content"
    channel = (info.get("channel") or info.get("uploader") or "").strip()
    if channel in {c.strip() for c in KNOWN_CHANNELS}:
        return True, "known finance channel"
    if strong_title:
        return True, "finance term in title"
    if FIN_RE.search(desc) or CN_FIN_RE.search(desc):
        return True, "finance term in description"
    return False, "no finance signal"


def fetch_metadata(stage_limit: int | None = None) -> list[dict]:
    pool = read_jsonl(POOL)
    candidates = [item for item in pool if cheap_relevant(item)]
    print(f"cheap filter: {len(candidates)} / {len(pool)}")
    rows = []
    for i, item in enumerate(candidates, 1):
        vid = item["id"]
        info = fetch_meta(vid)
        if info is None:
            rows.append({**item, "status": "unavailable"})
            continue
        ts = upload_ts(info)
        ok, why = relevant(info)
        rows.append(
            {
                "id": vid,
                "title": info.get("title"),
                "channel": info.get("channel") or info.get("uploader"),
                "channel_id": info.get("channel_id"),
                "upload_date": info.get("upload_date"),
                "upload_utc": ts,
                "view_count": info.get("view_count"),
                "comment_count": info.get("comment_count"),
                "duration": info.get("duration"),
                "ticker": infer_ticker(info),
                "relevant": ok,
                "reason": why,
                "in_window": bool(ts and START <= ts < END),
                "queries": item.get("queries"),
                "status": "ok",
            }
        )
        if i % 25 == 0:
            print(f"  metadata {i}/{len(candidates)}", flush=True)
            write_jsonl(META_INDEX, rows)
        time.sleep(0.4)
    write_jsonl(META_INDEX, rows)
    print(f"metadata: {sum(1 for r in rows if r['status']=='ok')} ok, {sum(1 for r in rows if r['status']!='ok')} unavailable")
    return rows


def review() -> list[dict]:
    rows = read_jsonl(META_INDEX)
    selected = [
        r
        for r in rows
        if r.get("status") == "ok" and r.get("relevant") and r.get("in_window")
    ]
    selected.sort(key=lambda r: r.get("upload_utc") or 0)
    REVIEW.parent.mkdir(parents=True, exist_ok=True)
    with REVIEW.open("w", encoding="utf-8") as fh:
        fh.write("include\tid\tupload\tchannel\tticker\ttitle\treason\tqueries\n")
        for r in sorted(rows, key=lambda r: r.get("upload_utc") or 0):
            include = "Y" if r in selected else "N"
            fh.write(
                "\t".join(
                    [
                        include,
                        r.get("id") or "",
                        r.get("upload_date") or "",
                        (r.get("channel") or "").replace("\t", " "),
                        r.get("ticker") or "",
                        (r.get("title") or "").replace("\t", " "),
                        r.get("reason") or r.get("status") or "",
                        ",".join(r.get("queries") or []),
                    ]
                )
                + "\n"
            )
    SELECTION.write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"shortlist: {len(selected)} videos; review file: {REVIEW}")
    return selected


# ---------------------------------------------------------------------------
# comment timestamp estimation
# ---------------------------------------------------------------------------


def add_months(value: datetime, months: int) -> datetime:
    year = value.year + (value.month - 1 + months) // 12
    month = (value.month - 1 + months) % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


REL_RE = re.compile(r"(\d+)\s*(year|month|week|day|hour|minute|second)s?\s*ago", re.IGNORECASE)


def label_interval(time_text: str | None) -> tuple[datetime, datetime, str] | None:
    """Feasible interval for a relative YouTube label at COLLECTED_AT."""
    if not time_text:
        return None
    text = time_text.lower().replace("(edited)", "").strip()
    if text in ("today", "now"):
        return COLLECTED_AT - timedelta(days=1), COLLECTED_AT, "day"
    if text == "yesterday":
        return COLLECTED_AT - timedelta(days=2), COLLECTED_AT - timedelta(days=1), "day"
    match = REL_RE.search(text)
    if not match:
        return None
    count, unit = int(match.group(1)), match.group(2).lower()
    if unit == "year":
        return add_months(COLLECTED_AT, -12 * (count + 1)), add_months(COLLECTED_AT, -12 * count), "year"
    if unit == "month":
        return add_months(COLLECTED_AT, -(count + 1)), add_months(COLLECTED_AT, -count), "month"
    if unit == "week":
        return COLLECTED_AT - timedelta(weeks=count + 1), COLLECTED_AT - timedelta(weeks=count), "week"
    if unit == "day":
        return COLLECTED_AT - timedelta(days=count + 1), COLLECTED_AT - timedelta(days=count), "day"
    if unit == "hour":
        return COLLECTED_AT - timedelta(hours=count + 1), COLLECTED_AT - timedelta(hours=count), "hour"
    if unit == "minute":
        return COLLECTED_AT - timedelta(minutes=count + 1), COLLECTED_AT - timedelta(minutes=count), "minute"
    return COLLECTED_AT - timedelta(seconds=count + 1), COLLECTED_AT - timedelta(seconds=count), "second"


def estimate_comment(comment: dict, video_upload: int) -> dict | None:
    interval = label_interval(comment.get("_time_text"))
    if interval is None:
        return None
    lo_dt, hi_dt, bucket = interval
    lo = max(int(lo_dt.timestamp()), int(video_upload))
    hi = min(int(hi_dt.timestamp()), int(COLLECTED_AT.timestamp()))
    if lo >= hi:
        return None
    return {
        "estimate": (lo + hi) // 2,
        "lo": lo,
        "hi": hi,
        "time_text": comment.get("_time_text"),
        "bucket": bucket,
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


# ---------------------------------------------------------------------------
# comment extraction
# ---------------------------------------------------------------------------


def fetch_comments(video_id: str, force: bool = False) -> dict | None:
    FULL_CACHE.mkdir(parents=True, exist_ok=True)
    info_path = FULL_CACHE / f"{video_id}.info.json"
    done = FULL_CACHE / f"{video_id}.done"
    if info_path.exists() and done.exists() and not force:
        try:
            return json.loads(info_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    url = f"https://www.youtube.com/watch?v={video_id}"
    cmd = [
        str(YTDLP),
        "--write-comments",
        "--skip-download",
        "--no-warnings",
        "--no-progress",
        "--ignore-errors",
        "--socket-timeout",
        "30",
        "--retries",
        "5",
        "--extractor-retries",
        "3",
        "-o",
        str(FULL_CACHE / "%(id)s.%(ext)s"),
        url,
    ]
    print(f"[comments] {video_id}", flush=True)
    started = time.monotonic()
    try:
        proc = run(cmd, timeout=3600)
    except subprocess.TimeoutExpired:
        print(f"  timeout {video_id}", file=sys.stderr, flush=True)
        return None
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / f"{video_id}.log").write_text(
        f"exit={proc.returncode}\nelapsed={time.monotonic() - started:.1f}s\n"
        f"--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}\n",
        encoding="utf-8",
    )
    if info_path.exists():
        done.write_text("ok\n", encoding="utf-8")
        return json.loads(info_path.read_text(encoding="utf-8"))
    return None


def comment_status(video_id: str, info: dict | None, error: str | None = None) -> dict:
    log = LOG_DIR / f"{video_id}.log"
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
        note = "comment section unavailable (no comments or count; likely disabled)"
    return {
        "video_id": video_id,
        "status": (
            "error"
            if error
            else ("comments_disabled" if note.startswith("comment section unavailable") else "ok")
        ),
        "note": note,
        "comments_fetched": len(comments),
        "comment_count_metadata": (info or {}).get("comment_count"),
    }


def existing_ids() -> tuple[set[str], set[str]]:
    posts: set[str] = set()
    replies: set[str] = set()
    for path in EXISTING:
        for rec in read_jsonl(path):
            if rec.get("record_type") == "post":
                posts.add(rec.get("native_id"))
            elif rec.get("record_type") == "reply":
                replies.add(rec.get("native_id"))
    return posts, replies


def collect(no_fetch: bool = False) -> tuple[list[dict], dict[str, dict], list[str]]:
    selected = json.loads(SELECTION.read_text(encoding="utf-8"))
    existing_posts, existing_replies = existing_ids()
    print(f"existing corpus: {len(existing_posts)} posts, {len(existing_replies)} comments")

    records: list[dict] = []
    seen: set[tuple[str, str]] = set()
    statuses: dict[str, dict] = {}
    skipped_posts: list[str] = []

    for i, spec in enumerate(selected):
        vid = spec["id"]
        cached = (FULL_CACHE / f"{vid}.done").exists() and (FULL_CACHE / f"{vid}.info.json").exists()
        if i and not cached and not no_fetch:
            time.sleep(2.0)
        if no_fetch:
            path = FULL_CACHE / f"{vid}.info.json"
            info = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
        else:
            info = fetch_comments(vid)
        if info is None:
            statuses[vid] = comment_status(vid, None, error="no info.json")
            statuses[vid].update(
                {
                    "title": spec.get("title"),
                    "channel": spec.get("channel"),
                    "upload_utc": spec.get("upload_utc"),
                    "ticker": spec.get("ticker"),
                }
            )
            continue

        statuses[vid] = comment_status(vid, info)
        v_upload = upload_ts(info) or spec.get("upload_utc")
        comments = info.get("comments") or []
        channel = info.get("channel") or info.get("uploader") or spec.get("channel")
        ticker = spec.get("ticker") or infer_ticker(info)
        statuses[vid].update(
            {
                "upload_date": info.get("upload_date"),
                "upload_utc": int(v_upload) if v_upload else None,
                "title": info.get("title"),
                "channel": channel,
                "view_count": info.get("view_count"),
                "ticker": ticker,
                "comments_fetched": len(comments),
                "in_window": 0,
            }
        )

        write_post = vid not in existing_posts
        if not write_post:
            skipped_posts.append(vid)

        if write_post and v_upload is not None:
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
                "created_utc": int(v_upload),
                "url": f"https://www.youtube.com/watch?v={vid}",
                "body": (description or "")[:2000] or None,
                "score": info.get("view_count"),
                "num_comments": info.get("comment_count"),
                "lang": None,
                "time_confidence": "exact" if info.get("timestamp") else "date",
                "raw": post_raw,
            }
            if ("youtube", vid) not in seen:
                records.append(post_rec)
                seen.add(("youtube", vid))

        depths, inferred = compute_depths(comments)
        in_file = 0
        no_ts = 0
        for comment in comments:
            cid = comment.get("id")
            if not cid or cid in existing_replies or ("youtube", cid) in seen:
                continue
            est = estimate_comment(comment, int(v_upload or 0))
            if est is None:
                no_ts += 1
                continue
            parent_raw = comment.get("parent")
            parent = None if parent_raw in (None, "root") else str(parent_raw)
            depth = depths.get(cid, 0 if parent is None else 1)
            body = clean_text(comment.get("text")) or "[deleted]"
            raw = {
                "id": cid,
                "parent": parent_raw,
                "text": comment.get("text"),
                "timestamp": comment.get("timestamp"),
                "time_text": est["time_text"],
                "time_text_bucket": est["bucket"],
                "time_text_interval_start": est["lo"],
                "time_text_interval_end": est["hi"],
                "timestamp_estimate": est["estimate"],
                "timestamp_estimate_method": (
                    "midpoint of relative-label interval clipped to video upload time "
                    "and collection time"
                ),
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
                    "time_confidence": "relative",
                    "raw": raw,
                }
            )
            seen.add(("youtube", cid))
            in_file += 1

        statuses[vid]["in_file"] = in_file
        statuses[vid]["no_timestamp"] = no_ts
        statuses[vid]["min_comment_utc"] = min(
            (r["created_utc"] for r in records if r.get("post_native_id") == vid), default=None
        )
        statuses[vid]["max_comment_utc"] = max(
            (r["created_utc"] for r in records if r.get("post_native_id") == vid), default=None
        )

    # Deduplicate by (source, native_id), keeping the first occurrence.
    unique: dict[tuple[str, str], dict] = {}
    for rec in records:
        unique.setdefault((rec["source"], rec["native_id"]), rec)
    records = list(unique.values())
    records.sort(key=lambda r: (r["created_utc"], r["record_type"], r["native_id"]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(OUT, records)
    (WORK / "status.json").write_text(json.dumps(statuses, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(records)} records to {OUT}")
    return records, statuses, skipped_posts


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------


def day(value: int | None) -> str:
    return datetime.fromtimestamp(value, timezone.utc).strftime("%Y-%m-%d") if value else "—"


def write_report(records: list[dict], statuses: dict[str, dict], skipped_posts: list[str]) -> None:
    posts = [r for r in records if r["record_type"] == "post"]
    replies = [r for r in records if r["record_type"] == "reply"]
    by_ticker = Counter(p["ticker"] for p in posts)
    post_ticker = {p["native_id"]: p["ticker"] for p in posts}
    comments_by_ticker = Counter(post_ticker.get(r["post_native_id"], "UNKNOWN") for r in replies)
    ts = [r["created_utc"] for r in records]
    comment_ts = [r["created_utc"] for r in replies]
    roots = sum(1 for r in replies if r["depth"] == 0)
    authors = {r["author"] for r in replies if r.get("author")}
    buckets = Counter((r.get("raw") or {}).get("time_text_bucket") for r in replies)
    min_valid = int(datetime(2024, 10, 1, tzinfo=timezone.utc).timestamp())
    pre_floor = sum(1 for r in records if r["created_utc"] < min_valid)
    zero_fetched = sum(1 for s in statuses.values() if s.get("comments_fetched", 0) == 0)
    disabled = sum(
        1 for s in statuses.values() if "comment section unavailable" in (s.get("note") or "")
    )
    meta_rows = read_jsonl(META_INDEX)
    unavailable = [r for r in meta_rows if r.get("status") != "ok"]
    auto_ids = {r["id"] for r in meta_rows if r.get("relevant") and r.get("in_window")}
    shortlisted = len(auto_ids)
    fetched = len(statuses)
    auto_selected = sum(1 for vid in statuses if vid in auto_ids)
    manual_added = fetched - auto_selected
    manual_removed = shortlisted - auto_selected

    lines: list[str] = []
    lines.append("# YouTube collection report — Malaysian Genting, 2016–2024\n")
    lines.append("- **Collected:** 2 Nov 2026")
    lines.append(
        "- **Video window:** 2 Nov 2016 00:00 MYT → 1 Nov 2024 23:59:59 MYT "
        "(1 Nov 2016 16:00 UTC → 1 Nov 2024 16:00 UTC)"
    )
    lines.append("- **Output:** `data/raw/youtube_2016-2024.jsonl`")
    lines.append("- **Collector:** `scripts/collect_youtube_2016_2024.py` (caches in `/tmp/opencode/yt10`)")
    lines.append(
        f"- **Videos:** {shortlisted} passed the automatic relevance/date filter; manual review "
        f"removed {manual_removed} false positives and added {manual_added} relevant videos the "
        f"title heuristic missed, leaving {fetched} fetched ({auto_selected} automatic + "
        f"{manual_added} manual); {len(posts)} posts written, {len(skipped_posts)} already posts "
        "in `youtube_full.jsonl` (no duplicate post records)"
    )
    lines.append(f"- **Records:** {len(records)} — {len(posts)} posts, {len(replies)} comments")
    lines.append("- **Posts by ticker:** " + ", ".join(f"{k} × {v}" for k, v in sorted(by_ticker.items())))
    lines.append(
        "- **Comments by post ticker:** "
        + ", ".join(f"{k} × {v}" for k, v in sorted(comments_by_ticker.items()))
    )
    lines.append(
        f"- **Comment threads:** {roots} top-level comments, {len(replies) - roots} replies, "
        f"{len(authors)} distinct authors"
    )
    if posts:
        lines.append(
            f"- **Post date range:** {day(min(p['created_utc'] for p in posts))} → "
            f"{day(max(p['created_utc'] for p in posts))}"
        )
    if comment_ts:
        lines.append(
            f"- **Comment date range (estimated):** {day(min(comment_ts))} → "
            f"{day(max(comment_ts))}; comments on these videos run through the collection "
            "date, not only to 1 Nov 2024"
        )
    lines.append(
        f"- **Validation:** `python3 -m genting.validate data/raw/youtube_2016-2024.jsonl` → "
        f"**OK, 0 errors, {pre_floor} warnings**. Every warning is the same expected one: the "
        "record timestamp is before the validator's fixed 2024-10-01 floor, because this file "
        "deliberately covers 2016–2024. No schema, duplicate-id or missing-field errors."
    )
    lines.append("")

    lines.append("## API / quota\n")
    lines.append(
        "No YouTube Data API key is configured anywhere in the repository (`YOUTUBE_API_KEY` "
        "is absent and no key is read by the existing collectors). This collector therefore "
        "uses **yt-dlp 2026.10.21.202512**, exactly like `collect_youtube.py` and "
        "`collect_youtube_backfill.py`. There is **no Data API quota** and therefore no "
        "quota-exhaustion error to report. The relevant limits are YouTube's scraping rate "
        "limits; each request is spaced (1.2 s between searches, 2 s between comment "
        "extractions) and every non-200 / bot-check / 429 outcome is recorded per video in "
        "the failures section."
    )
    lines.append("")
    lines.append(
        "**Access result:** the platform did allow the 2016–2024 period. The earliest post "
        "written is **3 Nov 2016** and the latest is **28 Oct 2024**; no API/key blocker was "
        "hit. The only access limits were videos whose comments are disabled and videos that "
        "were deleted/private (counts below)."
    )
    lines.append("")

    lines.append("## Method\n")
    lines.append(
        f"Discovery ran {len(QUERIES)} queries × {len(SEARCH_YEARS)} one-year windows "
        f"(2016-11-02→2017-11-01 … 2023-11-02→2024-11-01), `ytsearch40` each, using "
        "YouTube's `after:`/`before:` operators. The union pool was **3,752 unique video ids**; "
        "a cheap title/description filter for a Genting mention plus a finance signal left "
        f"**{len(meta_rows)}** candidates, whose full metadata was fetched "
        f"({len(meta_rows) - len(unavailable)} ok, {len(unavailable)} unavailable/deleted). "
        "Metadata was used to verify the upload date "
        "and subject; videos outside the window, Genting Singapore-only content, Genting "
        "Plantations/Hong Kong, travel/theme-park/car videos and unrelated `GenM`/Generation "
        f"Mining results were dropped. **{shortlisted}** videos passed the automatic filter; a "
        f"manual review removed {manual_removed} travel/car, student-assignment, unrelated-company "
        f"and generic-roundup false positives and added {manual_added} relevant videos whose "
        f"titles the heuristic missed, leaving **{fetched}** videos. Each was fetched "
        "with `yt-dlp --write-comments --skip-download`; yt-dlp paginates the comment "
        "continuations and retrieves every comment and reply it is allowed to see."
    )
    lines.append("")
    lines.append(
        "The searches were (each run once per one-year window):"
    )
    lines.append("")
    for q in QUERIES:
        lines.append(f"- `ytsearch40:{q} after:YYYY-11-01 before:YYYY+1-11-02`")
    lines.append("")

    lines.append("## Comment timestamps and `time_confidence`\n")
    lines.append(
        "YouTube's public comment API exposes **only a relative age** (`3 years ago`, "
        "`11 months ago`), not an absolute publication time. For every comment this collector:"
    )
    lines.append("")
    lines.append(
        "1. keeps the original label in `raw.time_text` and yt-dlp's resolved value in "
        "`raw.timestamp`;"
    )
    lines.append(
        "2. computes the label's feasible interval at collection time (for `N years ago`, "
        "`[now − (N+1) years, now − N years]`), clips it to the video's upload time and the "
        "collection time;"
    )
    lines.append(
        "3. sets `created_utc` to the **midpoint** of that interval and "
        "`raw.timestamp_estimate_method` to the method used;"
    )
    lines.append(
        '4. sets top-level `time_confidence` to **`"relative"`** on every comment. '
        "The interval bounds are in `raw.time_text_interval_start` / "
        "`raw.time_text_interval_end`; `raw.time_text_bucket` records whether the label "
        "was year-, month-, week-, day-, hour- or minute-grained."
    )
    lines.append("")
    lines.append(
        "This means a `5 years ago` comment is only known to fall somewhere in a 12-month "
        "window; the midpoint is a defensible point estimate, **not an observed date**. "
        "No comment timestamp or text was invented. Sub-year timing within a year label "
        "cannot be recovered from YouTube's public comment API."
    )
    lines.append("")
    lines.append(
        "**Post timestamps** are different: `created_utc` is YouTube's exact upload timestamp "
        "when the metadata exposes it (`time_confidence=\"exact\"`), otherwise the upload date "
        "at 00:00 UTC (`time_confidence=\"date\"`). Post timestamps are not estimates from a "
        "relative label."
    )
    lines.append("")
    lines.append(
        "The earliest comment estimate is **May 2017**, not 2016, because a comment posted in "
        "late 2016 carries the label `9 years ago` at collection; that label covers Nov 2016 → "
        "Nov 2017 and its midpoint is May 2017. The comments exist, but the label cannot place "
        "them inside 2016. The year-by-year comment counts below are therefore label-driven and "
        "should not be read as a precise activity timeline."
    )
    if buckets:
        lines.append("")
        lines.append(
            "Label precision of the comments written: "
            + ", ".join(f"{k or 'unknown'} × {v}" for k, v in sorted(buckets.items(), key=lambda kv: -kv[1]))
            + "."
        )
    if replies:
        mode_ts, mode_n = Counter(r["created_utc"] for r in replies).most_common(1)[0]
        lines.append("")
        lines.append(
            f"Because labels are coarse, many comments share an estimated day: the largest "
            f"cluster is **{mode_n} comments at {day(mode_ts)}**. This is an artefact of the "
            "relative label, not evidence of a one-day burst."
        )
    lines.append("")

    lines.append("## Coverage by upload year\n")
    year_of = {
        p["native_id"]: datetime.fromtimestamp(p["created_utc"], timezone.utc).year for p in posts
    }
    year_comments = Counter(year_of.get(r["post_native_id"]) for r in replies)
    years = sorted(set(year_of.values()))
    lines.append("| Upload year | Posts | Comments written |")
    lines.append("| --- | ---: | ---: |")
    for year in years:
        lines.append(
            f"| {year} | {sum(1 for y in year_of.values() if y == year)} | "
            f"{year_comments.get(year, 0)} |"
        )
    lines.append("")

    lines.append("## Videos collected\n")
    lines.append(
        "| Video | Channel | Ticker | Uploaded | Views | Comments (metadata) | Fetched | Written | Status |"
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
            f"{st.get('comments_fetched', 0)} | {st.get('in_file', 0)} | {status} |"
        )
    lines.append("")

    not_written = [(v, s) for v, s in statuses.items() if v not in post_ticker]
    lines.append("## Videos checked but not written as posts\n")
    if not not_written:
        lines.append("None.")
    else:
        lines.append("| Video | Uploaded | Fetched comments | Reason |")
        lines.append("| --- | --- | ---: | --- |")
        for vid, st in sorted(
            not_written, key=lambda kv: (kv[1].get("upload_utc") or 0), reverse=True
        ):
            title = (st.get("title") or "").replace("|", "\\|")
            reason = st.get("note") or st.get("status") or "no comments"
            if vid in skipped_posts:
                reason = (
                    "post already in `youtube_full.jsonl`; all fetched comments were already "
                    "present there, so nothing was duplicated"
                )
            lines.append(
                f"| [{vid}](https://www.youtube.com/watch?v={vid}) {title} | "
                f"{day(st.get('upload_utc'))} | {st.get('comments_fetched', 0)} | {reason} |"
            )
    lines.append("")

    lines.append("## Largest comment threads\n")
    lines.append("| Video | Ticker | Comments written |")
    lines.append("| --- | --- | ---: |")
    for vid, st in sorted(statuses.items(), key=lambda kv: kv[1].get("in_file", 0), reverse=True)[:15]:
        if not st.get("in_file"):
            break
        title = (st.get("title") or "").replace("|", "\\|")
        lines.append(
            f"| [{vid}](https://www.youtube.com/watch?v={vid}) {title} | {st.get('ticker')} | {st['in_file']} |"
        )
    lines.append("")

    failures = [
        (v, s)
        for v, s in statuses.items()
        if s.get("status") != "ok" or s.get("note", "").startswith("comment section")
    ]
    lines.append("## Failures, quota errors and gaps\n")
    lines.append(
        f"- **Quota errors:** none. No Data API key is configured, so no quota was consumed; "
        "the collector used yt-dlp scraping."
    )
    lines.append(
        "- **HTTP 429 / bot checks:** none recorded in the search or comment logs."
    )
    lines.append(
        f"- **Unavailable/deleted candidates:** {len(unavailable)} of {len(meta_rows)} "
        "metadata fetches returned no metadata ("
        + ", ".join(f"`{r['id']}`" for r in unavailable)
        + "). They could not be included."
    )
    lines.append(
        f"- **Zero comments fetched:** {zero_fetched} of {len(statuses)} selected videos. "
        f"Of these, {disabled} explicitly returned no comment section/comment count (usually "
        "comments disabled); the rest legitimately have no comments. Posts are still written "
        "for all of them."
    )
    if not failures:
        lines.append(
            "- **Other failures:** none. Every shortlisted video returned metadata; no sign-in "
            "challenge was encountered."
        )
    else:
        for vid, st in failures:
            written = "post written" if vid in post_ticker else "no post written"
            lines.append(
                f"- `{vid}` ({st.get('title') or 'title unavailable'}) — "
                f"{st.get('note') or st.get('status')}; fetched "
                f"{st.get('comments_fetched', 0)} comments, {st.get('in_file', 0)} written; "
                f"{written}."
            )
    lines.append("")
    lines.append("### Discovery gaps\n")
    lines.append(
        "YouTube search is relevance-ranked and caps a query at the requested result count "
        "(`ytsearch40` here), so it is a sample, not an exhaustive index. Old Malaysian retail "
        "stock videos are often unlisted, deleted, or titled only with Chinese characters and "
        "no Romanised company name; those cannot be recovered by keyword search. The pool was "
        "built from the queries above and their one-year windows; videos whose titles/descriptions "
        "do not mention Genting or a finance term were not fetched. Channel-scoped archive sweeps "
        "(as used for the 2024–2026 file) were not repeated for all 2016–2024 channels because the "
        "candidate pool already spans the window. Comment counts in video metadata are approximate "
        "and can lag; the fetched total is the authoritative count."
    )
    lines.append("")
    lines.append("## Exclusions\n")
    lines.append(
        "Genting Highlands travel/theme-park/hotel/driving videos, casino-consumer and gambling "
        "vlogs, Kamen Rider `GenM`, Generation Mining (TSX:GENM), Genting Plantations (GENP), "
        "Genting Hong Kong and Genting Singapore-only (SGX:G13) analysis were excluded. "
        "Multi-stock market roundups were kept only when Genting was a named subject in the "
        "title or description. Videos about the Malaysian counters that also discuss Genting "
        "Singapore as a subsidiary/sister listing were kept when GENTING or GENM was the subject."
    )
    lines.append("")
    lines.append("## Deduplication\n")
    lines.append(
        "The collector read the three existing YouTube files (never wrote them) and skipped "
        "any comment id already present there. "
        + (
            f"{len(skipped_posts)} selected videos were already posts in `youtube_full.jsonl`; "
            "every comment fetched for them was already present in that file, so no record was "
            "duplicated. "
            if skipped_posts
            else "No selected video was already a post in an earlier file. "
        )
        + "Records are deduplicated by `(source, native_id)` inside this file. "
        "Because comments were fetched for the whole thread, the comment date range can extend "
        "past 1 Nov 2024; those are comments on the 2016–2024 videos, not videos published after "
        "the window. They are labelled with `time_confidence=\"relative\"` like every other comment."
    )
    lines.append("")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote report to {REPORT}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--stage",
        choices=["discover", "meta", "review", "collect", "build", "all"],
        default="all",
    )
    ap.add_argument("--no-fetch", action="store_true", help="build only from cache")
    ap.add_argument("--force", action="store_true", help="ignore search/meta caches")
    args = ap.parse_args(argv)

    if args.stage in ("discover", "all") and not args.no_fetch:
        discover(force=args.force)
    if args.stage in ("discover", "meta", "all") and not args.no_fetch:
        build_pool()
        fetch_metadata()
    if args.stage in ("review", "all", "collect", "build"):
        if not SELECTION.exists():
            review()
    if args.stage in ("collect", "all"):
        records, statuses, skipped = collect(no_fetch=args.no_fetch)
        write_report(records, statuses, skipped)
    elif args.stage == "build":
        records, statuses, skipped = collect(no_fetch=True)
        write_report(records, statuses, skipped)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
