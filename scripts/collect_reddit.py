"""Collect selected Malaysian-Genting Reddit threads through Arctic Shift.

Reddit's own JSON/search endpoints return 403 from this machine, so threads are
discovered with web search + Arctic Shift's title search, then fetched here.
Writes data/raw/reddit_threads.jsonl and a JSON fetch summary used for the
human-readable report. Re-running rewrites both files from scratch.
"""

from __future__ import annotations

import html
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://arctic-shift.photon-reddit.com/api"
UA = "genting-sentiment/0.1 (research collector)"
PAGE_SIZE = 100
MIN_INTERVAL = 1.2  # seconds between API calls
OUT = Path("data/raw/reddit_threads.jsonl")
SUMMARY = Path("/tmp/opencode/reddit_fetch_summary.json")

# Threads whose subject is Genting Berhad / Genting Malaysia as a company:
# shares, corporate actions, results, credit ratings, control and major legal
# matters. Tourism/theme-park/toll/casino-consumer threads are excluded.
THREADS = [
    {"id": "1opmo58", "ticker": "GENM", "note": "MP questions GENM share movements before privatisation"},
    {"id": "1opou5j", "ticker": "GENM", "note": "Genting takeover offer for GENM explained"},
    {"id": "1owh1lr", "ticker": "GENM", "note": "Takeover offer extended to 1 Dec"},
    {"id": "1pbvq10", "ticker": "GENM", "note": "Privatisation bid fails; GENM stays listed"},
    {"id": "1t00g2r", "ticker": "GENM", "note": "Court halts Sky City project; Genting Malaysia Group wins suit"},
    {"id": "1tm1dpb", "ticker": "GENM", "note": "HLIB HOLD call after weak 1QFY26"},
    {"id": "1vo3uee", "ticker": "GENTING", "note": "Genting Singapore H1 profit falls (Genting Berhad subsidiary)"},
    {"id": "1wb90ta", "ticker": "GENM", "note": "Fitch downgrades GENM to BBB-"},
    {"id": "1w0fd3h", "ticker": "GENM", "note": "Chinese-language GENM 4715 results analysis"},
    {"id": "1x4lwlt", "ticker": "GENTING", "note": "Genting shares fall most in 28 years on rights issue"},
    {"id": "1x4rj3v", "ticker": "GENTING", "note": "r/BursaMalaysia video: Genting crashes 23%, buy or avoid"},
    {"id": "1xdgakx", "ticker": "GENTING", "note": "Rights issue allocation discussion (r/MalaysianPF)"},
    {"id": "1xdgbx3", "ticker": "GENTING", "note": "Same rights-issue post crossposted to r/MalaysiaPF"},
]

_last_call = 0.0


def _get(path: str, params: dict, retries: int = 7) -> dict:
    global _last_call
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    last_err: Exception | None = None
    for attempt in range(retries):
        wait = MIN_INTERVAL - (time.monotonic() - _last_call)
        if wait > 0:
            time.sleep(wait)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                _last_call = time.monotonic()
                return json.load(resp)
        except Exception as exc:  # HTTPError, URLError, timeout, bad JSON
            _last_call = time.monotonic()
            last_err = exc
            code = getattr(exc, "code", None)
            # 422 is Arctic Shift's overloaded-worker timeout; retry with backoff.
            if code is not None and code not in (422, 429, 500, 502, 503, 504):
                raise
            delay = min(60, 5 * (2**attempt))
            print(f"    retry {attempt + 1}/{retries} in {delay}s: {exc}")
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
        if new == 0 or newest == cursor:
            notes.append(
                f"pagination stopped at cursor {cursor} with a full page and no new ids"
            )
            break
        cursor = newest

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

        print(f"fetching {pid} r/{post.get('subreddit')} — {post.get('title')}")
        try:
            comments, pages, notes = fetch_comments(pid)
            error = None
        except Exception as exc:
            comments, pages, notes, error = [], 0, [], str(exc)
            print(f"  ERROR {error}")

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
        for c in comments:
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
                # Preserve the row; the archive sometimes stores an empty body.
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

        ts = [int(c.get("created_utc") or 0) for c in comments]
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
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nwrote {len(records)} records to {OUT} ({len(summary)} threads)")
    print(f"summary: {SUMMARY}")


if __name__ == "__main__":
    main()
