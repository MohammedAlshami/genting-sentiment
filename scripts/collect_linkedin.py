#!/usr/bin/env python3
"""Collect public LinkedIn company posts about Genting (logged out).

LinkedIn renders the latest company posts in JSON-LD on the public company page.
Individual post pages also expose JSON-LD with datePublished, like count and
commentCount. Comment bodies are login-gated ("To view or add a comment, sign
in"), so no reply records are produced; the count is preserved.

Usage:
  python3 scripts/collect_linkedin.py --out data/raw/linkedin.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "raw" / "cache" / "linkedin"
WINDOW_START = int(datetime(2024, 11, 2, tzinfo=timezone.utc).timestamp())
WINDOW_END = int(datetime(2026, 11, 2, 23, 59, 59, tzinfo=timezone.utc).timestamp())

COMPANIES = [
    {"slug": "genting-berhad", "name": "Genting Berhad", "ticker": "GENTING"},
    {"slug": "resorts-world-genting", "name": "Resorts World Genting", "ticker": "GENM"},
]

EXTRA_POSTS = [
    # Public posts found through search-engine discovery.
    "https://www.linkedin.com/posts/pirginezra_genting-shares-tumble-most-since-1998-on-activity-7515309138923491330-g4Rn",
]


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode()).hexdigest()[:12]


def fetch(url: str) -> tuple[str, int]:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{sha1(url)}.html"
    if path.exists() and path.stat().st_size > 20_000:
        return path.read_text(encoding="utf-8"), 200
    last = None
    for attempt in range(3):
        try:
            r = requests.get(url, impersonate="chrome", timeout=45, allow_redirects=True)
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(2**attempt * 3)
                continue
            path.write_text(r.text, encoding="utf-8")
            time.sleep(2.5)
            return r.text, r.status_code
        except Exception as exc:
            last = exc
            time.sleep(2**attempt * 3)
    raise RuntimeError(f"fetch failed {url}: {last!r}")


def ld_objects(html: str) -> list[dict]:
    out = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            d = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        items = d.get("@graph", [d]) if isinstance(d, dict) else d
        if isinstance(items, dict):
            items = [items]
        for it in items:
            if isinstance(it, dict):
                out.append(it)
    return out


def infer_ticker(text: str) -> str:
    t = (text or "").lower()
    if any(k in t for k in ("genm", "4715", "genting malaysia", "云顶大马")):
        return "GENM"
    if any(k in t for k in ("genting", "3182", "云顶")):
        return "GENTING"
    return "UNKNOWN"


def parse_iso(value: str | None) -> int | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return int(dt.timestamp())
    except ValueError:
        return None


def post_from_ld(obj: dict, fallback_channel: str, ticker: str, source_url: str) -> dict | None:
    if obj.get("@type") != "SocialMediaPosting":
        return None
    url = obj.get("mainEntityOfPage") or obj.get("@id") or obj.get("url")
    if isinstance(url, dict):
        url = url.get("@id") or url.get("url")
    text = obj.get("text") or obj.get("headline") or ""
    if not url or not text:
        return None
    m = re.search(r"activity-(\d+)", str(url))
    native_id = m.group(1) if m else sha1(str(url))
    created = parse_iso(obj.get("datePublished"))
    if created is None or not (WINDOW_START <= created <= WINDOW_END):
        return None
    author = (obj.get("author") or {}).get("name") if isinstance(obj.get("author"), dict) else None
    if isinstance(obj.get("author"), list) and obj["author"]:
        author = (obj["author"][0] or {}).get("name") or author
    like = None
    stat = obj.get("interactionStatistic")
    if isinstance(stat, dict) and "LikeAction" in str(stat.get("interactionType")):
        like = stat.get("userInteractionCount")
    elif isinstance(stat, list):
        for s in stat:
            if isinstance(s, dict) and "LikeAction" in str(s.get("interactionType")):
                like = s.get("userInteractionCount")
    comment_count = obj.get("commentCount")
    if isinstance(comment_count, str) and comment_count.isdigit():
        comment_count = int(comment_count)

    title = next((ln.strip() for ln in str(text).splitlines() if ln.strip()), "")
    if len(title) > 200:
        title = title[:197].rstrip() + "..."

    # Defensive: if LinkedIn ever exposes public comment objects, map them.
    replies = []
    comments = obj.get("comment")
    if isinstance(comments, list):
        for c in comments:
            if not isinstance(c, dict):
                continue
            ctext = c.get("text") or ""
            cdate = parse_iso(c.get("dateCreated") or c.get("datePublished"))
            if not ctext or cdate is None:
                continue
            cauthor = c.get("author")
            cauthor = cauthor.get("name") if isinstance(cauthor, dict) else cauthor
            replies.append(
                {
                    "record_type": "reply",
                    "source": "linkedin",
                    "channel": fallback_channel,
                    "native_id": str(c.get("@id") or sha1(ctext + str(cdate))),
                    "post_native_id": native_id,
                    "parent_native_id": None,
                    "depth": 0,
                    "author": cauthor,
                    "author_id": None,
                    "created_utc": cdate,
                    "body": ctext,
                    "score": None,
                    "url": str(url),
                    "lang": None,
                    "raw": {"access_note": "Public LinkedIn JSON-LD comment object."},
                }
            )

    post = {
        "record_type": "post",
        "source": "linkedin",
        "channel": fallback_channel,
        "native_id": native_id,
        "ticker": ticker,
        "title": title or f"LinkedIn post {native_id}",
        "author": author,
        "author_id": None,
        "created_utc": created,
        "url": str(url),
        "body": text or None,
        "score": like,
        "num_comments": comment_count,
        "lang": None,
        "raw": {
            "activity_id": native_id,
            "company_page": source_url,
            "like_count": like,
            "comment_count": comment_count,
            "comments_public": False,
            "access_note": (
                "Public LinkedIn page HTML served logged-out; comment bodies are "
                "login-gated, so only the public post and its comment count are stored."
            ),
            "fetched_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    }
    return post, replies


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "data/raw/linkedin.jsonl")
    ap.add_argument("--log", type=Path, default=ROOT / "data/raw/linkedin_fetch_log.json")
    args = ap.parse_args()

    records: list[dict] = []
    seen: set[str] = set()
    logs = []

    for company in COMPANIES:
        url = f"https://www.linkedin.com/company/{company['slug']}/"
        html, status = fetch(url)
        objs = ld_objects(html)
        posts = [o for o in objs if o.get("@type") == "SocialMediaPosting"]
        logs.append({"url": url, "status": status, "ld_posts": len(posts)})
        for obj in posts:
            parsed = post_from_ld(obj, company["slug"], company["ticker"], url)
            if not parsed:
                continue
            post, replies = parsed
            if post["native_id"] in seen:
                continue
            seen.add(post["native_id"])
            records.append(post)
            for rep in replies:
                if rep["native_id"] in seen:
                    continue
                seen.add(rep["native_id"])
                records.append(rep)

    for url in EXTRA_POSTS:
        try:
            html, status = fetch(url)
        except Exception as exc:
            logs.append({"url": url, "error": repr(exc)})
            continue
        objs = ld_objects(html)
        posts = [o for o in objs if o.get("@type") == "SocialMediaPosting"]
        logs.append({"url": url, "status": status, "ld_posts": len(posts)})
        # The first object is the post itself; others may be recommendations.
        for obj in posts:
            author = (obj.get("author") or {}).get("name") if isinstance(obj.get("author"), dict) else ""
            is_target = "activity-" + str(re.search(r"activity-(\d+)", url).group(1)) in str(obj.get("@id") or "")
            if not is_target and author and "Genting" not in str(author):
                continue
            parsed = post_from_ld(obj, "linkedin-public", infer_ticker(obj.get("text") or ""), url)
            if not parsed:
                continue
            post, replies = parsed
            if post["native_id"] in seen:
                continue
            seen.add(post["native_id"])
            records.append(post)
            for rep in replies:
                if rep["native_id"] in seen:
                    continue
                seen.add(rep["native_id"])
                records.append(rep)

    records.sort(key=lambda r: (r["record_type"] != "post", r["created_utc"]))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    posts = [r for r in records if r["record_type"] == "post"]
    args.log.write_text(
        json.dumps(
            {
                "window_start_utc": WINDOW_START,
                "window_end_utc": WINDOW_END,
                "posts_written": len(posts),
                "replies_written": len(records) - len(posts),
                "min_created_utc": min((p["created_utc"] for p in posts), default=None),
                "max_created_utc": max((p["created_utc"] for p in posts), default=None),
                "fetch_log": logs,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"wrote {args.out}: {len(records)} records ({len(posts)} posts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
