#!/usr/bin/env python3
"""Collect public Instagram posts/comments about Genting (logged out).

Each seed URL is opened in a real browser (Xvfb, headful). Instagram serves the
post caption, exact taken_at timestamp, like/comment counts and the first page of
comments to logged-out visitors. No login, cookies or captcha solving.

Usage:
  xvfb-run -a python3 scripts/collect_instagram.py seeds.json --out data/raw/instagram.jsonl
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import nodriver as uc

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "raw" / "cache" / "instagram"
WINDOW_START = int(datetime(2024, 11, 2, tzinfo=timezone.utc).timestamp())
WINDOW_END = int(datetime(2026, 11, 2, 23, 59, 59, tzinfo=timezone.utc).timestamp())


def code_from_url(url: str) -> str | None:
    m = re.search(r"instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)", url)
    return m.group(1) if m else None


def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)


def extract_payload(html: str) -> dict | None:
    for raw in re.findall(r'<script type="application/json"[^>]*>(.*?)</script>', html, re.S):
        if "xig_polaris_media" not in raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for obj in walk(data):
            media = obj.get("xig_polaris_media")
            if isinstance(media, dict):
                inner = media.get("if_not_gated_logged_out")
                if isinstance(inner, dict) and inner.get("code"):
                    merged = dict(inner)
                    if media.get("comments_connection"):
                        merged["comments_connection"] = media["comments_connection"]
                    return merged
                if media.get("code"):
                    return media
    return None


def parse_post(html: str, url: str, query: str | None) -> tuple[dict | None, list[dict], dict]:
    media = extract_payload(html)
    shortcode = code_from_url(url)
    log = {"url": url, "shortcode": shortcode, "query": query}
    if not media:
        log["reason"] = "no public media payload (login wall or deleted)"
        return None, [], log

    taken = media.get("taken_at")
    caption = (media.get("caption") or {}).get("text") or ""
    user = media.get("user") or {}
    username = user.get("username")
    like_count = media.get("like_count")
    comment_count = media.get("comment_count")
    log.update({"taken_at": taken, "username": username, "comments_total": comment_count})

    comments = []
    conn = media.get("comments_connection") or {}
    for edge in conn.get("edges") or []:
        node = edge.get("node") or {}
        text = (node.get("text") or "").strip()
        created = node.get("created_at")
        if not text or not isinstance(created, int):
            continue
        comments.append(
            {
                "id": str(node.get("pk") or node.get("id")),
                "created": created,
                "author": (node.get("user") or {}).get("username"),
                "author_id": (node.get("user") or {}).get("pk") or (node.get("user") or {}).get("id"),
                "text": text,
                "parent": str(node["parent_comment_id"]) if node.get("parent_comment_id") else None,
                "score": node.get("comment_like_count"),
            }
        )

    log["comments_captured"] = len(comments)
    if not isinstance(taken, int):
        log["reason"] = "no taken_at"
        return None, [], log
    if not (WINDOW_START <= taken <= WINDOW_END):
        log["reason"] = "outside window"
        return None, [], log

    ticker = "UNKNOWN"
    blob = (caption + " " + (media.get("accessibility_caption") or "")).lower()
    if any(k in blob for k in ("genm", "4715", "genting malaysia", "云顶大马")):
        ticker = "GENM"
    elif any(k in blob for k in ("genting", "genting berhad", "3182", "云顶")):
        ticker = "GENTING"

    title = next((ln.strip() for ln in caption.splitlines() if ln.strip()), "")
    if not title:
        title = f"{username or 'instagram'} post {shortcode}"
    if len(title) > 200:
        title = title[:197].rstrip() + "..."

    access_note = (
        "Fetched from the public Instagram post URL in a logged-out browser; "
        "Instagram rendered the caption, exact taken_at and the first page of comments."
    )
    post = {
        "record_type": "post",
        "source": "instagram",
        "channel": username or "unknown",
        "native_id": shortcode,
        "ticker": ticker,
        "title": title,
        "author": username,
        "author_id": user.get("pk") or user.get("id"),
        "created_utc": int(taken),
        "url": f"https://www.instagram.com/p/{shortcode}/",
        "body": caption or None,
        "score": like_count,
        "num_comments": comment_count,
        "lang": None,
        "raw": {
            "shortcode": shortcode,
            "media_id": media.get("pk"),
            "media_type": media.get("media_type"),
            "product_type": media.get("product_type"),
            "like_count": like_count,
            "comment_count": comment_count,
            "comments_captured": len(comments),
            "comment_gap": (comment_count - len(comments)) if isinstance(comment_count, int) else None,
            "taken_at": taken,
            "access_note": access_note,
            "discovery_query": query,
            "fetched_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    }

    replies = []
    for c in comments:
        if not (WINDOW_START <= c["created"] <= WINDOW_END):
            continue
        replies.append(
            {
                "record_type": "reply",
                "source": "instagram",
                "channel": username or "unknown",
                "native_id": c["id"],
                "post_native_id": shortcode,
                "parent_native_id": c["parent"],
                "depth": 1 if c["parent"] else 0,
                "author": c["author"],
                "author_id": str(c["author_id"]) if c["author_id"] else None,
                "created_utc": int(c["created"]),
                "body": c["text"],
                "score": c["score"],
                "url": f"https://www.instagram.com/p/{shortcode}/",
                "lang": None,
                "raw": {
                    "shortcode": shortcode,
                    "comment_count": comment_count,
                    "access_note": access_note,
                },
            }
        )
    return post, replies, log


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("seeds", type=Path)
    ap.add_argument("--out", type=Path, default=ROOT / "data/raw/instagram.jsonl")
    ap.add_argument("--log", type=Path, default=ROOT / "data/raw/instagram_fetch_log.json")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    seeds = json.loads(args.seeds.read_text(encoding="utf-8"))
    if args.limit:
        seeds = seeds[: args.limit]
    CACHE.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    seen: set[str] = set()
    logs: list[dict] = []
    skipped: list[dict] = []

    browser = await uc.start(
        headless=False,
        browser_args=["--no-sandbox", "--disable-dev-shm-usage", "--window-size=1400,1000", "--lang=en-US"],
    )
    try:
        page = await browser.get("https://www.instagram.com/")
        await page.sleep(3)
        for i, seed in enumerate(seeds, 1):
            url = seed["url"]
            code = code_from_url(url)
            if not code:
                skipped.append({"url": url, "reason": "no shortcode"})
                continue
            target = f"https://www.instagram.com/p/{code}/"
            cache_path = CACHE / f"{code}.html"
            if cache_path.exists() and cache_path.stat().st_size > 50_000:
                html = cache_path.read_text(encoding="utf-8")
            else:
                try:
                    await page.get(target)
                    await page.sleep(6)
                    html = await page.get_content()
                    cache_path.write_text(html, encoding="utf-8")
                    await page.sleep(3)
                except Exception as exc:
                    skipped.append({"url": url, "reason": f"nav error: {exc!r}"})
                    continue
            post, replies, log = parse_post(html, url, seed.get("query"))
            logs.append(log)
            if not post:
                skipped.append({"url": url, "reason": log.get("reason")})
                continue
            if post["native_id"] in seen:
                skipped.append({"url": url, "reason": "duplicate"})
                continue
            seen.add(post["native_id"])
            records.append(post)
            for rep in replies:
                if rep["native_id"] in seen:
                    continue
                seen.add(rep["native_id"])
                records.append(rep)
            print(f"[{i}/{len(seeds)}] {code} {datetime.fromtimestamp(post['created_utc'], timezone.utc):%Y-%m-%d} {post['channel']} comments={len(replies)}")
    finally:
        browser.stop()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    args.log.write_text(
        json.dumps(
            {
                "window_start_utc": WINDOW_START,
                "window_end_utc": WINDOW_END,
                "seeds": len(seeds),
                "posts_written": sum(1 for r in records if r["record_type"] == "post"),
                "replies_written": sum(1 for r in records if r["record_type"] == "reply"),
                "fetch_log": logs,
                "skipped": skipped,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"wrote {args.out}: {len(records)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
