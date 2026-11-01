"""Collect the early-window / missed Reddit Genting threads into reddit_extra.jsonl.

Discovery was done separately (scripts/discover_reddit_extra.py). This fetches
each selected post and every comment in it through Arctic Shift, then drops any
record already present in the existing reddit_threads*.jsonl files.
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
UA = "genting-sentiment/0.1 (research collector)"
PAGE_SIZE = 100
MIN_INTERVAL = 2.5
WINDOW_START = int(datetime(2024, 11, 2, tzinfo=timezone.utc).timestamp())
WINDOW_END = int(datetime(2026, 11, 3, tzinfo=timezone.utc).timestamp())
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "reddit_extra.jsonl"

THREADS = [
    {"id": "1h3rrgq", "ticker": "GENM", "note": "Genting says no plans to reopen shuttered Malaysian casino floors"},
    {"id": "1husrkh", "ticker": "GENM", "note": "Genting opens new mass casino at Resorts World Genting"},
    {"id": "1ki9l9c", "ticker": "GENM", "note": "Genting's RM3.1bil New York gaming bet may backfire"},
    {"id": "1l7ho70", "ticker": "GENTING", "note": "How the Lim family built Genting's global empire"},
    {"id": "1mzlqz1", "ticker": "GENTING", "note": "GENTING RM2.95 testing critical support"},
    {"id": "1ohaj6s", "ticker": "GENM", "note": "What happens to GENM shares after privatisation"},
    {"id": "1o63n1w", "ticker": "GENTING", "note": "Genting to privatise Genting Malaysia at RM2.35"},
    {"id": "1vw3r3t", "ticker": "GENTING", "note": "Genting 2Q2026 results: revenue up, net loss"},
]

_last = 0.0


def _get(path: str, params: dict, retries: int = 10) -> dict:
    global _last
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    last_err: Exception | None = None
    for attempt in range(retries):
        wait = MIN_INTERVAL - (time.monotonic() - _last)
        if wait > 0:
            time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                _last = time.monotonic()
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            _last = time.monotonic()
            last_err = exc
            if exc.code not in (422, 429, 500, 502, 503, 504):
                raise
            delay = min(180, 10 * (1.6**attempt))
            print(f"    retry {attempt + 1}/{retries} in {delay:.0f}s: HTTP {exc.code}", flush=True)
            time.sleep(delay)
        except Exception as exc:
            _last = time.monotonic()
            last_err = exc
            delay = min(120, 10 * (1.6**attempt))
            print(f"    retry {attempt + 1}/{retries} in {delay:.0f}s: {exc}", flush=True)
            time.sleep(delay)
    raise RuntimeError(f"giving up on {path} {params}: {last_err}")


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


def existing_ids() -> set[str]:
    ids: set[str] = set()
    for path in sorted((ROOT / "data" / "raw").glob("reddit_threads*.jsonl")):
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ids.add(str(rec.get("native_id")))
    return ids


def fetch_comments(post_id: str) -> tuple[list[dict], int]:
    comments: dict[str, dict] = {}
    cursor: int | None = None
    pages = 0
    while True:
        params = {"link_id": post_id, "limit": PAGE_SIZE, "sort": "asc"}
        if cursor is not None:
            params["after"] = cursor
        page = _get("/comments/search", params).get("data") or []
        pages += 1
        new = 0
        for c in page:
            if c["id"] not in comments:
                comments[c["id"]] = c
                new += 1
        print(f"    comments page {pages}: {len(page)} rows, {new} new", flush=True)
        if len(page) < PAGE_SIZE or new == 0:
            break
        newest = max(int(c.get("created_utc") or 0) for c in page)
        if newest == cursor:
            break
        cursor = newest
    return sorted(comments.values(), key=lambda c: (int(c.get("created_utc") or 0), c["id"])), pages


def compute_depths(comments: list[dict]) -> tuple[dict[str, int], set[str]]:
    by_id = {c["id"]: c for c in comments}
    memo: dict[str, int] = {}
    missing: set[str] = set()

    def depth(cid: str, stack: set[str]) -> int:
        if cid in memo:
            return memo[cid]
        c = by_id.get(cid)
        if c is None:
            return 0
        if cid in stack:
            missing.add(cid)
            return 0
        parent = c.get("parent_id") or ""
        if parent.startswith("t3_"):
            value = 0
        elif parent.startswith("t1_"):
            pid = parent[3:]
            if pid not in by_id:
                missing.add(cid)
                value = 1
            else:
                value = depth(pid, stack | {cid}) + 1
        else:
            value = 0
            if parent:
                missing.add(cid)
        memo[cid] = value
        return value

    for c in comments:
        depth(c["id"], set())
    return memo, missing


def main() -> None:
    skip = existing_ids()
    print(f"existing reddit ids to skip: {len(skip)}", flush=True)
    ids = ",".join(t["id"] for t in THREADS)
    payload = _get("/posts/ids", {"ids": ids})
    posts = {p["id"]: p for p in (payload.get("data") or [])}

    records: list[dict] = []
    summary = []
    seen: set[tuple[str, str]] = set()
    for spec in THREADS:
        pid = spec["id"]
        post = posts.get(pid)
        if not post:
            print(f"MISSING {pid}", flush=True)
            continue
        print(f"fetching {pid} r/{post.get('subreddit')} {post.get('title')}", flush=True)
        comments, pages = fetch_comments(pid)
        comments = [
            c for c in comments
            if WINDOW_START <= int(c.get("created_utc") or 0) <= WINDOW_END
        ]
        depths, missing_parents = compute_depths(comments)
        post_url = reddit_url(post.get("permalink"), pid)
        body = clean(post.get("selftext"))
        if body in {"[removed]", "[deleted]"}:
            body = None
        if pid not in skip and ("reddit", pid) not in seen:
            seen.add(("reddit", pid))
            records.append({
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
            })
        for c in comments:
            cid = c["id"]
            if cid in skip or ("reddit", cid) in seen:
                continue
            seen.add(("reddit", cid))
            parent_raw = c.get("parent_id") or ""
            parent_native = parent_raw[3:] if parent_raw.startswith("t1_") else None
            cbody = clean(c.get("body")) or "[deleted]"
            raw = trim_comment(c)
            if cid in missing_parents:
                raw["parent_outside_window"] = True
            records.append({
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
            })
        stamps = [int(c.get("created_utc") or 0) for c in comments]
        summary.append({
            **spec,
            "subreddit": post.get("subreddit"),
            "title": post.get("title"),
            "post_created_utc": int(post.get("created_utc") or 0),
            "archive_num_comments": post.get("num_comments"),
            "comments_in_window": len(comments),
            "pages": pages,
            "min": min(stamps) if stamps else None,
            "max": max(stamps) if stamps else None,
        })

    records.sort(key=lambda r: (r["created_utc"], r["native_id"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    Path("/tmp/opencode/reddit_extra_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2)
    )
    print(f"wrote {len(records)} records to {OUT}", flush=True)
    print(json.dumps(summary, ensure_ascii=False, indent=1), flush=True)


if __name__ == "__main__":
    main()
