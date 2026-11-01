#!/usr/bin/env python3
"""Backfill Reddit Genting/GENM posts and comments for 2 Nov 2016 .. 1 Nov 2024.

Reads the Arctic Shift title-search pool and the Reddit Atom full-text pool,
filters to posts about Genting Berhad / Genting Malaysia (not Genting Highlands
travel), hydrates post rows, fetches every comment in each selected thread, and
writes ``data/raw/reddit_2016-2024.jsonl``.

Output contract follows ``docs/collector_contract.md``.  Comments keep
``parent_native_id`` and computed ``depth``; the post title is copied into each
reply's ``raw.thread_title`` so a classifier can use thread context without a
join.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://arctic-shift.photon-reddit.com/api"
UA = "genting-sentiment/0.2 (research backfill)"
PAGE_SIZE = 100
MIN_INTERVAL = 1.4
OUT = ROOT / "data" / "raw" / "reddit_2016-2024.jsonl"
SUMMARY = Path("/tmp/opencode/reddit_2016_2024_summary.json")
DISCOVERY = Path("/tmp/opencode/reddit_2016_2024_candidates.json")
RSS_DISCOVERY = Path("/tmp/opencode/reddit_rss_2016_2024_candidates.json")
GAP_DISCOVERY = Path("/tmp/opencode/reddit_gap_2016_2024.json")
COMPANY_PROBE = Path("/tmp/opencode/reddit_company_title_probe.json")
YEAR_PROBE = Path("/tmp/opencode/reddit_2016_probe.json")

# 2 Nov 2016 00:00 MYT -> 1 Nov 2024 23:59:59 MYT.
START = int(datetime(2016, 11, 1, 16, 0, 0, tzinfo=timezone.utc).timestamp())
END = int(datetime(2024, 11, 1, 16, 0, 0, tzinfo=timezone.utc).timestamp())

FINANCE_SUBS = {
    "malaysianpf", "malaysiapf", "bursamalaysia", "bursabets",
    "investing", "stocks", "stockmarket", "securityanalysis",
}

TICKER_RE = re.compile(r"\b(genm|4715|3182)\b", re.I)
GENTING_RE = re.compile(r"\bgenting\b", re.I)
COMPANY_RE = re.compile(
    r"""
    \bgenm\b|\b4715\b|\b3182\b
    |genting\s+(?:malaysia|berhad|bhd|group|singapore|hong\s+kong|new\s+york|
                   shares?|stock|stocks|earnings|results|profit|loss|revenue|
                   dividend|privatis\w*|takeover|rights\s+issue|ipo|bond|
                   credit|fitch|moody|market\s+cap|valuation|analyst|
                   target\s+price|klci|fbm|bursa|lawsuit|sued|macau|
                   casino\s+tax|gaming\s+tax|licen[cs]e|
                   mass\s+casino|gaming\s+bet)
    |resorts\s+world\s+genting
    |lim\s+(?:family|kok\s+thay)
    """,
    re.I | re.X,
)
FIN_RE = re.compile(
    r"""
    \b(?:genm|4715|3182|bursa|klse|klci|fbm|stock|stocks|shares?|shareholder|
         dividend|earnings|revenue|profit|loss|quarter|q[1-4]|fy\d{2}|
         valuation|analyst|target\s+price|market\s+cap|market\s+capitalisation|
         privatis\w*|takeover|rights\s+issue|ipo|bond|credit\s+rating|fitch|
         moody|debt|casino\s+tax|gaming\s+tax|gaming\s+revenue|net\s+loss|
         net\s+profit|investor|investment|sued|lawsuit|regulator|regulatory|
         delisting|suspension|suspended|trading\s+halt|buyback|placement|
         1mdb|superyacht|equanimity|settles|settlement)\b
    |casino\s+(?:open|opens|opening|reopen|reopens|close|closes|closing|
                 shut|shuts|license|licence|tax|revenue|earnings|floors)
    |new\s+(?:mass\s+)?casino|mass\s+casino
    |gaming\s+bet|new\s+york|macau|las\s+vegas
    |resorts\s+world\s+genting
    |lim\s+(?:family|kok\s+thay)
    """,
    re.I | re.X,
)
TRAVEL_RE = re.compile(
    r"""
    \b(?:highlands?|theme\s+park|skyworlds|hotel|resort|premium\s+outlet|
         cable\s+car|awana|bus|parking|condo|homestay|airbnb|food|restaurant|
         weather|trip|travel|visit|stay|room|ticket|zoo|snow\s+world|
         holiday|vacation|itinerary|roadtrip|
         chin\s+swee|hawker|traffic|jam|road|view|sunrise|sunset|hike|
         waterfall|mall|shopping|casino\s+trip|gambling\s+trip)\b
    """,
    re.I | re.X,
)

TAG_RE = re.compile(r"<[^>]+>")
BR_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)

_last = 0.0


def _get(path: str, params: dict, retries: int = 6) -> dict:
    global _last
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    last_err: Exception | None = None
    for attempt in range(retries):
        wait = MIN_INTERVAL - (time.monotonic() - _last)
        if wait > 0:
            time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                _last = time.monotonic()
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            _last = time.monotonic()
            last_err = exc
            if exc.code not in (422, 429, 500, 502, 503, 504):
                raise
            delay = min(60, 8 * (attempt + 1))
            print(f"    retry {attempt + 1}/{retries} in {delay}s: HTTP {exc.code}", flush=True)
            time.sleep(delay)
        except Exception as exc:  # noqa: BLE001
            _last = time.monotonic()
            last_err = exc
            delay = min(60, 8 * (attempt + 1))
            print(f"    retry {attempt + 1}/{retries} in {delay}s: {exc}", flush=True)
            time.sleep(delay)
    raise RuntimeError(f"giving up on {path} {params}: {last_err}")


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


def load_candidates() -> tuple[dict[str, dict], dict]:
    posts: dict[str, dict] = {}
    meta: dict = {}
    for path in (DISCOVERY, RSS_DISCOVERY, GAP_DISCOVERY, COMPANY_PROBE, YEAR_PROBE):
        if not path.exists():
            meta[path.name] = "missing"
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        meta[path.name] = {"queries": data.get("queries", {}), "count": len(data.get("posts", []))}
        for p in data.get("posts", []):
            pid = p.get("id")
            if not pid:
                continue
            if pid in posts:
                # Prefer the fuller Arctic row, but keep the discovery source.
                if posts[pid].get("discovery") != "arctic" and p.get("discovery") == "arctic":
                    p["discovery"] = posts[pid].get("discovery", p.get("discovery"))
                    posts[pid] = p
                else:
                    posts[pid].setdefault("discovery", p.get("discovery"))
            else:
                posts[pid] = p
    return posts, meta


CASINO_NEWS_RE = re.compile(
    r"""
    (?:closing|closes|closed|shut|shuts|opening|opens|reopen|reopens|upgrade|
        sale|sold|tax|licen[cs]e|revenue|earnings|rob|robbed|raid|raided)
    \s+(?:\w+\s+){0,3}genting\s+casino
    |genting\s+casino\s+(?:closing|closes|closed|shut|shuts|opening|opens|
                            reopen|reopens|upgrade|sale|sold|tax|licen[cs]e|
                            revenue|earnings|rob|robbed|raid|raided)
    """,
    re.I | re.X,
)
CRIME_RE = re.compile(
    r"\b(robbed|robbery|theft|stolen|murder|killed|died|arrested|police|scam|cheat|fraud|prostitute|drugs?)\b",
    re.I,
)


def classify(post: dict) -> tuple[str, str] | None:
    title = post.get("title") or ""
    body = post.get("selftext") or ""
    sub = (post.get("subreddit") or "").lower()

    title_ticker = TICKER_RE.search(title)
    title_company = COMPANY_RE.search(title)
    title_genting = GENTING_RE.search(title)
    title_finance = FIN_RE.search(title)
    title_travel = TRAVEL_RE.search(title)
    body_company = COMPANY_RE.search(body)
    body_finance = FIN_RE.search(body)
    body_genting = GENTING_RE.search(body)

    if not (title_genting or title_ticker or body_genting or body_company):
        return None
    if CRIME_RE.search(title) and not title_ticker:
        return None
    if re.search(r"\binheritance\s+saga\b|\bfamily\s+feud\b", title, re.I):
        return None
    if re.search(r"what\s+are\s+your\s+thoughts|so\s+many\s+cases|cases\s+like\s+this", title, re.I):
        return None
    if re.search(r"\bworking\s+(?:at|in)\b", title, re.I):
        return None
    if re.search(r"\b(working\s+at|working\s+in|jobs?|hiring|career|salary|interview|internship)\b", title, re.I) and not (title_ticker or title_finance):
        return None
    if re.search(
        r"\b(lost\s+a\s+lot|baccarat|problem\s+gambling|gambling\s+addiction|"
        r"what\s+are\s+your\s+thoughts|so\s+many\s+cases|cases\s+like\s+this)\b",
        title,
        re.I,
    ) and not (title_ticker or title_finance):
        return None
    if re.search(r"khám\s+phá|thành\s+phố|cao\s+nguyên|du\s+lịch|chuyến\s+đi", title, re.I) and not title_finance:
        return None
    if title_travel and not title_ticker and not title_company and not (title_genting and title_finance):
        return None
    if re.search(r"\bgenm\b", f"{title} {body}", re.I) and not re.search(r"\bgenting\b", f"{title} {body}", re.I):
        if sub in {"investing", "stocks", "stockmarket", "securityanalysis"}:
            return None
    if re.search(
        r"\b(problem gambling|gambling addiction|my father|my mother|my husband|"
        r"my wife|my son|my daughter|help me|need advice)\b",
        title,
        re.I,
    ) and not title_ticker:
        return None

    if title_ticker:
        reason = "ticker"
    elif title_company:
        reason = "company-title"
    elif sub in FINANCE_SUBS and (title_genting or body_genting):
        reason = "finance-sub"
    elif title_genting and (title_finance or CASINO_NEWS_RE.search(title)) and not title_travel:
        reason = "finance-title"
    elif not title_genting and body_company and body_finance and not title_travel:
        reason = "body-company+finance"
    else:
        return None

    title_l = title.lower()
    text_l = f"{title} {body}".lower()
    if re.search(r"\b(genm|4715)\b", title_l) or "genting malaysia" in title_l:
        ticker = "GENM"
    elif re.search(r"\b(genting|3182)\b", title_l) or "genting berhad" in title_l or "genting group" in title_l:
        ticker = "GENTING"
    elif re.search(r"\b(genm|4715)\b", text_l) or "genting malaysia" in text_l:
        ticker = "GENM"
    else:
        ticker = "GENTING"
    return ticker, reason


def mentioned_tickers(post: dict) -> list[str]:
    text = f"{post.get('title') or ''} {post.get('selftext') or ''}"
    out = []
    if re.search(r"\b(genm|4715)\b|genting\s+malaysia", text, re.I):
        out.append("GENM")
    if re.search(r"\b(genting|3182)\b|genting\s+berhad|genting\s+group", text, re.I):
        out.append("GENTING")
    return out or ["GENTING"]


def fetch_comments(post_id: str) -> tuple[list[dict], int, list[str]]:
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
        for c in page:
            if c["id"] not in comments:
                comments[c["id"]] = c
                new += 1
        if len(page) < PAGE_SIZE:
            break
        newest = max(int(c.get("created_utc") or 0) for c in page)
        next_cursor = max(int(cursor or 0), newest - 1)
        if new == 0 or next_cursor <= int(cursor or 0):
            notes.append(f"pagination stopped at cursor {cursor} with a full page and no new ids")
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
        if cid in stack:
            inferred.add(cid)
            return 0
        parent = c.get("parent_id") or ""
        if parent.startswith("t3_"):
            value = 0
        elif parent.startswith("t1_"):
            pd = depth(parent[3:], stack | {cid})
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


def hydrate(posts: list[dict]) -> None:
    """Fill missing archive fields (score, num_comments, permalink) from /posts/ids."""
    need = [p["id"] for p in posts if p.get("score") is None or not p.get("permalink")]
    for i in range(0, len(need), 100):
        chunk = need[i : i + 100]
        payload = _get("/posts/ids", {"ids": ",".join(chunk)})
        rows = {r["id"]: r for r in (payload.get("data") or [])}
        for p in posts:
            r = rows.get(p["id"])
            if r:
                for k, v in r.items():
                    if p.get(k) in (None, "") and v not in (None, ""):
                        p[k] = v


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-posts", type=int, default=0)
    args = ap.parse_args()
    if OUT.exists():
        raise SystemExit(f"refusing to overwrite existing {OUT}")

    candidates, discovery_meta = load_candidates()
    print(f"candidate pool: {len(candidates)} posts", flush=True)
    selected: list[dict] = []
    skipped = {"outside_window": 0, "irrelevant": 0}
    for p in candidates.values():
        ts = int(p.get("created_utc") or 0)
        if not (START <= ts < END):
            skipped["outside_window"] += 1
            continue
        cls = classify(p)
        if cls is None:
            skipped["irrelevant"] += 1
            continue
        p["_ticker"], p["_reason"] = cls
        selected.append(p)
    selected = list({p["id"]: p for p in selected}.values())
    selected.sort(key=lambda p: int(p.get("created_utc") or 0))
    print(f"selected {len(selected)} posts ({skipped})", flush=True)
    for p in selected:
        print(
            f"  {datetime.fromtimestamp(int(p['created_utc']), timezone.utc):%Y-%m-%d} "
            f"r/{p.get('subreddit')} {p['_ticker']} {p['id']} — {p.get('title','')[:90]}",
            flush=True,
        )
    if args.dry_run:
        return 0

    existing: set[str] = set()
    for path in sorted((ROOT / "data" / "raw").glob("reddit*.jsonl")):
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                existing.add(str(rec.get("native_id")))
    before = len(selected)
    selected = [p for p in selected if p["id"] not in existing]
    if len(selected) != before:
        print(f"skipped {before - len(selected)} ids already in existing reddit files", flush=True)
    if args.max_posts:
        selected = selected[: args.max_posts]

    hydrate(selected)
    records: list[dict] = []
    seen: set[str] = set()
    summary: list[dict] = []
    for n, post in enumerate(selected, 1):
        pid = post["id"]
        print(f"[{n}/{len(selected)}] {pid} r/{post.get('subreddit')} — {post.get('title','')[:80]}", flush=True)
        try:
            comments, pages, notes = fetch_comments(pid)
            error = None
        except Exception as exc:  # noqa: BLE001
            comments, pages, notes, error = [], 0, [], str(exc)
            print(f"  ERROR {error}", flush=True)
        depths, inferred = compute_depths(comments)
        in_window = [c for c in comments if START <= int(c.get("created_utc") or 0) < END]

        body = clean(post.get("selftext"))
        if body in {"[removed]", "[deleted]"}:
            body = None
        raw = trim_post(post)
        raw.update(
            {
                "discovery": post.get("discovery") or "arctic_title",
                "mentioned_tickers": mentioned_tickers(post),
                "relevance": post["_reason"],
            }
        )
        post_rec = {
            "record_type": "post",
            "source": "reddit",
            "channel": post.get("subreddit"),
            "native_id": pid,
            "ticker": post["_ticker"],
            "title": post.get("title"),
            "author": post.get("author"),
            "author_id": post.get("author_fullname"),
            "created_utc": int(post.get("created_utc") or 0),
            "url": reddit_url(post.get("permalink"), pid),
            "body": body,
            "score": post.get("score"),
            "num_comments": post.get("num_comments"),
            "lang": None,
            "raw": raw,
        }
        if pid not in seen:
            records.append(post_rec)
            seen.add(pid)

        empty = 0
        for c in in_window:
            cid = c["id"]
            if cid in seen:
                continue
            seen.add(cid)
            parent_raw = c.get("parent_id") or ""
            parent_native = parent_raw[3:] if parent_raw.startswith("t1_") else None
            cbody = clean(c.get("body"))
            if cbody is None:
                cbody = "[deleted]"
            if cbody in {"[deleted]", "[removed]"}:
                empty += 1
            craw = trim_comment(c)
            craw["thread_title"] = post.get("title")
            if cid in inferred:
                craw["depth_inferred"] = True
            records.append(
                {
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
                    "raw": craw,
                }
            )

        ts = [int(c.get("created_utc") or 0) for c in in_window]
        summary.append(
            {
                "id": pid,
                "subreddit": post.get("subreddit"),
                "ticker": post["_ticker"],
                "title": post.get("title"),
                "created_utc": int(post.get("created_utc") or 0),
                "archive_num_comments": post.get("num_comments"),
                "comments_fetched": len(comments),
                "comments_in_window": len(in_window),
                "pages": pages,
                "min_comment_utc": min(ts) if ts else None,
                "max_comment_utc": max(ts) if ts else None,
                "deleted_or_removed": empty,
                "depth_inferred": len(inferred),
                "error": error,
                "notes": notes,
            }
        )

    records.sort(key=lambda r: (r["created_utc"], 0 if r["record_type"] == "post" else 1, str(r["native_id"])))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(
        json.dumps(
            {
                "window": [START, END],
                "candidate_pool": len(candidates),
                "discovery": discovery_meta,
                "selected_posts": len(selected),
                "records": len(records),
                "skipped": skipped,
                "threads": summary,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    posts = sum(1 for r in records if r["record_type"] == "post")
    replies = sum(1 for r in records if r["record_type"] == "reply")
    print(f"\nwrote {len(records)} records ({posts} posts, {replies} replies) to {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
