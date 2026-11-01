#!/usr/bin/env python3
"""Collect the moomoo Malaysia stock community feed for GENTING / GENM.

The community page is server-rendered with window.__INITIAL_STATE__, but the
list paginates through:

    GET https://www.moomoo.com/community/nnq/stock-feedlist2
        ?type=500&load_list_type=1&stock_id=<id>&num=10[&more_mark=<token>]

Each response contains 20 feed items (the server ignores num>10) plus a new
`more_mark` cursor.  Comments are fetched per feed with:

    GET https://www.moomoo.com/community/nnq/get-feed-comment-list
        ?feed_id=<id>&module_id=0&more_mark=<cursor>&req_type=1&comment_count=100

Long posts whose list `summary.is_complete` is false are expanded from the
server-rendered feed detail page (/community/feed/<id>), which carries the full
`detail.moduleData` block tree.

Output follows docs/collector_contract.md.
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "raw"
CACHE_DIR = Path("/tmp/opencode/moomoo/cache")

API_ROOT = "https://www.moomoo.com/community/nnq/"
FEED_PATH = "stock-feedlist2"
COMMENT_PATH = "get-feed-comment-list"

SOURCE = "moomoo_my"

# Window: 2 Nov 2025 00:00 MYT (UTC+8) through 2 Nov 2026 inclusive.
MYT = timezone(timedelta(hours=8))
WINDOW_START = int(datetime(2025, 11, 2, tzinfo=MYT).timestamp())  # 2025-11-01 16:00 UTC
WINDOW_END = int(datetime(2026, 11, 3, tzinfo=MYT).timestamp())    # 2026-11-02 16:00 UTC

TICKERS = {
    "GENTING": {
        "stock_id": "83893613193791",
        "code": "3182",
        "market": "3182-BMS",
        "name": "Genting Berhad",
    },
    "GENM": {
        "stock_id": "83893613193949",
        "code": "4715",
        "market": "4715-BMS",
        "name": "Genting Malaysia",
    },
}

DELAY = 1.05
MAX_RETRIES = 5
MAX_FEED_PAGES = 1200
MAX_COMMENT_PAGES = 60
MAX_DETAIL_PAGES = 4000


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def clean_text(value) -> str:
    """Strip HTML, decode entities, normalise whitespace."""
    if value is None:
        return ""
    s = str(value)
    if not s:
        return ""
    s = html_lib.unescape(s)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</p\s*>", "\n", s)
    s = re.sub(r"(?i)</div\s*>", "\n", s)
    s = BeautifulSoup(s, "lxml").get_text(" ")
    s = s.replace("\u200b", "").replace("\xa0", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def rich_text_to_text(items) -> str:
    """Render moomoo rich_text items (posts/comments) as plain text.

    type 0 = text, type 3 = stock mention, type 7 = hyperlink.
    Images (4), section markers (5) and emoticons (1) are skipped.
    """
    parts: list[str] = []
    for it in items or []:
        if not isinstance(it, dict):
            continue
        typ = it.get("type")
        if typ == 0:
            parts.append(it.get("text") or "")
        elif typ == 3:
            stock = it.get("stock") or {}
            ext = stock.get("extend_info") or {}
            label = ext.get("full_name") or stock.get("stock_name") or ""
            if label:
                parts.append(label)
        elif typ == 7:
            link = it.get("text_link") or {}
            if link.get("text"):
                parts.append(link["text"])
    return clean_text("".join(parts))


def module_text(blocks) -> str:
    """Render the feed-detail moduleData block tree as plain text."""
    def walk(node) -> str:
        if isinstance(node, dict):
            typ = node.get("type")
            if typ == 6:
                return " "
            if isinstance(node.get("text"), str):
                return node["text"]
            out = []
            for key, val in node.items():
                if key in ("text", "attrs"):
                    continue
                out.append(walk(val))
            return "".join(out)
        if isinstance(node, list):
            return "".join(walk(v) for v in node)
        return ""

    paragraphs: list[str] = []
    for block in blocks or []:
        if not isinstance(block, dict):
            continue
        if block.get("type") == 0:
            txt = clean_text(walk(block.get("data")))
            if txt:
                paragraphs.append(txt)
        elif block.get("type") in (2, 3):
            # quote / stock card blocks occasionally carry text
            txt = clean_text(walk(block))
            if txt:
                paragraphs.append(txt)
    return "\n".join(paragraphs).strip()


def to_epoch(value) -> int | None:
    if value in (None, "", 0, "0"):
        return None
    try:
        ts = float(str(value))
    except (TypeError, ValueError):
        return None
    if ts > 10_000_000_000:  # milliseconds
        ts = ts / 1000
    return int(ts)


class Collector:
    def __init__(self, ticker: str, cfg: dict, no_cache: bool = False):
        self.ticker = ticker
        self.cfg = cfg
        self.no_cache = no_cache
        self.session = curl_requests.Session(impersonate="chrome")
        self.last_request = 0.0
        self.requests_made = 0
        self.feed_pages = 0
        self.comment_requests = 0
        self.detail_requests = 0
        self.errors: list[str] = []
        self.referer = f"https://www.moomoo.com/stock/{cfg['market']}/community"
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _wait(self) -> None:
        elapsed = time.time() - self.last_request
        if elapsed < DELAY:
            time.sleep(DELAY - elapsed)

    def _get(self, url: str, params: dict | None = None, kind: str = "api"):
        last_err = None
        for attempt in range(1, MAX_RETRIES + 1):
            self._wait()
            try:
                r = self.session.get(
                    url,
                    params=params,
                    timeout=75,
                    headers={
                        "Referer": self.referer,
                        "Accept": "application/json, text/plain, */*",
                        "Accept-Language": "en-US,en;q=0.9",
                    },
                )
                self.last_request = time.time()
                self.requests_made += 1
                if r.status_code == 200 and r.text and not r.text.lstrip().startswith("<"):
                    return r
                last_err = f"HTTP {r.status_code} body={r.text[:120]!r}"
                if r.status_code not in (429, 500, 502, 503, 504) and r.status_code < 500:
                    # non-retryable but still return for caller diagnostics
                    return r
            except Exception as exc:  # noqa: BLE001
                self.last_request = time.time()
                last_err = f"{type(exc).__name__}: {exc}"
            wait = min(60, 5 * attempt)
            log(f"  {kind} retry {attempt}/{MAX_RETRIES} in {wait}s ({last_err})")
            time.sleep(wait)
        raise RuntimeError(f"request failed after {MAX_RETRIES} tries: {last_err}")

    def api_json(self, path: str, params: dict, kind: str) -> dict:
        r = self._get(API_ROOT + path, params, kind)
        try:
            data = r.json()
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"bad JSON from {path}: {exc}: {r.text[:200]!r}") from exc
        code = data.get("code", data.get("result"))
        if code not in (0, "0", None):
            raise RuntimeError(f"{path} returned code={code} message={data.get('message')!r}")
        return data

    def _feed_page(self, index: int, more_mark: str | None) -> dict:
        cache_file = CACHE_DIR / f"feed_{self.ticker}_{index:04d}.json"
        if cache_file.exists() and not self.no_cache:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        params = {
            "type": "500",
            "load_list_type": "1",
            "stock_id": self.cfg["stock_id"],
            "num": "10",
        }
        if more_mark:
            params["more_mark"] = more_mark
        data = self.api_json(FEED_PATH, params, f"feed p{index}")
        cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return data

    def collect_feed(self, max_pages: int = MAX_FEED_PAGES) -> list[dict]:
        posts: dict[str, dict] = {}
        mark = None
        page = 0
        oldest_seen = None
        while page < max_pages:
            data = self._feed_page(page, mark)
            feeds = data.get("feed") or []
            if not feeds:
                log(f"  feed page {page}: empty response, stopping")
                break
            self.feed_pages += 1

            for f in feeds:
                fid = str(((f.get("feed_comm") or {}).get("feed_id")) or "")
                if fid and fid not in posts:
                    posts[fid] = f
            stamps = [to_epoch((f.get("feed_comm") or {}).get("timestamp")) for f in feeds]
            stamps = [s for s in stamps if s]
            page_oldest = min(stamps) if stamps else None
            page_newest = max(stamps) if stamps else None
            if page_oldest:
                oldest_seen = page_oldest if oldest_seen is None else min(oldest_seen, page_oldest)

            if page % 10 == 0:
                shown = datetime.fromtimestamp(page_oldest, MYT).strftime("%Y-%m-%d") if page_oldest else "?"
                log(
                    f"  page {page:03d}: {len(feeds)} feeds, oldest {shown}, "
                    f"cumulative {len(posts)}"
                )

            has_more = int(data.get("has_more") or 0)
            next_mark = data.get("more_mark")
            if not has_more or not next_mark:
                log(f"  feed exhausted on page {page} (has_more={has_more})")
                break
            if next_mark == mark:
                log(f"  feed cursor did not advance on page {page}, stopping")
                break
            # Once every post on a page predates the window we are done.
            if page_newest is not None and page_newest < WINDOW_START:
                log(f"  page {page} fully before window, stopping")
                break
            mark = next_mark
            page += 1
        if page >= max_pages and int(data.get("has_more") or 0):
            self.errors.append(f"hit feed page cap ({max_pages}) with has_more=1")

        log(f"  feed done: {self.feed_pages} pages, {len(posts)} unique posts")
        return list(posts.values())

    def _comment_cache(self, feed_id: str) -> Path:
        return CACHE_DIR / f"comments_{self.ticker}_{feed_id}.json"

    def collect_comments(self, feed: dict) -> list[dict]:
        fid = str((feed.get("feed_comm") or {}).get("feed_id"))
        total = int(feed.get("comments_total_count") or 0)
        embedded = feed.get("comment_items") or []
        has_more_embedded = bool(feed.get("has_more_comments"))

        cache_file = self._comment_cache(fid)
        if cache_file.exists() and not self.no_cache:
            return json.loads(cache_file.read_text(encoding="utf-8"))

        # The feed payload already contains every comment for most posts.
        if total and not has_more_embedded and len(embedded) >= total:
            cache_file.write_text(json.dumps(embedded, ensure_ascii=False), encoding="utf-8")
            return embedded
        if total == 0 and not embedded:
            cache_file.write_text("[]", encoding="utf-8")
            return []

        comments: list[dict] = []
        seen: set[str] = set()
        mark = "0"
        for page in range(MAX_COMMENT_PAGES):
            data = self.api_json(
                COMMENT_PATH,
                {
                    "feed_id": fid,
                    "module_id": "0",
                    "more_mark": mark,
                    "req_type": "1",
                    "comment_count": "100",
                },
                f"comments {fid} p{page}",
            )
            self.comment_requests += 1
            payload = data.get("data") or {}
            batch = payload.get("comment_list") or []
            for c in batch:
                cid = str(c.get("comment_id") or "")
                if cid and cid not in seen:
                    seen.add(cid)
                    comments.append(c)
            if not int(payload.get("has_more") or 0):
                break
            nxt = str(payload.get("more_mark") or "0")
            if not nxt or nxt == "0" or nxt == mark:
                break
            mark = nxt
        else:
            self.errors.append(f"comment pagination cap for feed {fid}")

        if len(comments) < total:
            self.errors.append(
                f"feed {fid}: comments_total_count={total} but API returned {len(comments)}"
            )
        if not comments and embedded:
            comments = embedded
        cache_file.write_text(json.dumps(comments, ensure_ascii=False), encoding="utf-8")
        return comments

    def _detail_cache(self, feed_id: str) -> Path:
        return CACHE_DIR / f"detail_{self.ticker}_{feed_id}.json"

    def collect_detail(self, feed: dict) -> dict | None:
        fid = str((feed.get("feed_comm") or {}).get("feed_id"))
        cache_file = self._detail_cache(fid)
        if cache_file.exists() and not self.no_cache:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        url = f"https://www.moomoo.com/community/feed/{fid}"
        r = self._get(url, None, f"detail {fid}")
        self.detail_requests += 1
        if r.status_code != 200:
            self.errors.append(f"detail {fid}: HTTP {r.status_code}")
            return None
        text = r.text or ""
        pos = text.find("window.__INITIAL_STATE__")
        if pos < 0:
            self.errors.append(f"detail {fid}: no __INITIAL_STATE__")
            cache_file.write_text("null", encoding="utf-8")
            return None
        brace = text.find("{", pos)
        try:
            state, _ = json.JSONDecoder().raw_decode(text[brace:])
        except Exception as exc:  # noqa: BLE001
            self.errors.append(f"detail {fid}: JSON decode {exc}")
            cache_file.write_text("null", encoding="utf-8")
            return None
        detail = state.get("detail") or {}
        if not detail:
            self.errors.append(f"detail {fid}: empty detail")
            cache_file.write_text("null", encoding="utf-8")
            return None
        body = module_text(detail.get("moduleData") or [])
        out = {
            "feed_id": fid,
            "title": clean_text(detail.get("feedTitle")),
            "body": body,
            "flatten_text": clean_text(detail.get("feedFlattenText")),
            "module_data": detail.get("moduleData") or [],
            "count": detail.get("count") or {},
            "author_id": str((detail.get("authorInfo") or {}).get("userId") or ""),
            "author": (detail.get("authorInfo") or {}).get("nickName"),
            "url": r.url,
        }
        cache_file.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
        return out


def post_body(feed: dict) -> str:
    summary = feed.get("summary") or {}
    candidates = [
        rich_text_to_text(summary.get("rich_text") or []),
        clean_text(feed.get("content")),
        clean_text(feed.get("content_html")),
    ]
    return max(candidates, key=len).strip()


def make_title(feed: dict, detail: dict | None, body: str) -> str:
    title = clean_text(feed.get("feed_title")) or (detail or {}).get("title") or ""
    title = title.strip()
    if title:
        return title
    for line in (body or "").splitlines():
        first = re.sub(r"^(?:\s*\$[^$]{1,80}\$\s*)+", "", line).strip()
        if first:
            if len(first) > 160:
                cut = first[:160]
                if " " in cut:
                    cut = cut.rsplit(" ", 1)[0]
                return cut
            return first
    ts = to_epoch((feed.get("feed_comm") or {}).get("timestamp"))
    day = datetime.fromtimestamp(ts, MYT).strftime("%Y-%m-%d") if ts else "unknown-date"
    return f"[media post] {day}"


def build_post(feed: dict, detail: dict | None) -> dict:
    fc = feed.get("feed_comm") or {}
    fid = str(fc.get("feed_id"))
    ts = to_epoch(fc.get("timestamp"))
    body = post_body(feed)
    if detail and detail.get("body") and len(detail["body"]) > len(body):
        body = detail["body"]
    if not body and detail and detail.get("flatten_text"):
        body = detail["flatten_text"]
    # The stock tag is auto-inserted by moomoo at the start of most posts.
    # Keep it in `raw`, but do not make it the post body (otherwise media-only
    # posts look as if they contain text).
    body = re.sub(r"^(?:\s*\$[^$]{1,80}\$\s*)+", "", body).strip()
    slug = (fc.get("url_slugname") or "").strip()
    url = (
        f"https://www.moomoo.com/community/feed/{slug}-{fid}"
        if slug
        else f"https://www.moomoo.com/community/feed/{fid}"
    )
    author_info = feed.get("author_info") or {}
    like = feed.get("like") or {}
    raw = {
        "feed_id": fid,
        "feed_type": fc.get("feed_type"),
        "timestamp": fc.get("timestamp"),
        "url_slugname": slug,
        "feed_title": feed.get("feed_title") or "",
        "content": feed.get("content"),
        "content_html": feed.get("content_html") or "",
        "summary": {
            "is_complete": (feed.get("summary") or {}).get("is_complete"),
            "rich_text": [
                {
                    "type": it.get("type"),
                    "text": it.get("text"),
                    "stock": ((it.get("stock") or {}).get("extend_info") or {}).get("full_name"),
                    "link": (it.get("text_link") or {}).get("link"),
                    "link_text": (it.get("text_link") or {}).get("text"),
                    "image": ((it.get("pic") or {}).get("big_pic") or {}).get("url"),
                }
                for it in ((feed.get("summary") or {}).get("rich_text") or [])
                if isinstance(it, dict)
            ],
        },
        "comments_total_count": feed.get("comments_total_count"),
        "has_more_comments": feed.get("has_more_comments"),
        "more_comment_id": feed.get("more_comment_id"),
        "like": {"liked_num": like.get("liked_num")},
        "browse_count": feed.get("browse_count"),
        "share_count": feed.get("share_count"),
        "feed_from": feed.get("feed_from"),
        "author": {
            "user_id": str(author_info.get("user_id") or ""),
            "nick_name": author_info.get("nick_name"),
            "signature": author_info.get("signature"),
        },
        "detail_fetched": detail is not None,
        "detail_url": (detail or {}).get("url"),
    }
    return {
        "record_type": "post",
        "source": SOURCE,
        "channel": None,
        "native_id": fid,
        "ticker": None,
        "title": make_title(feed, detail, body),
        "author": author_info.get("nick_name"),
        "author_id": str(author_info.get("user_id") or "") or None,
        "created_utc": ts,
        "url": url,
        "body": body,
        "score": like.get("liked_num"),
        "num_comments": int(feed.get("comments_total_count") or 0),
        "lang": None,
        "raw": raw,
    }


def build_comments(post_native_id: str, post_url: str, comments: list[dict]) -> list[dict]:
    by_id: dict[str, dict] = {}
    for c in comments:
        cid = str(c.get("comment_id") or "")
        if cid:
            by_id[cid] = c

    depth_cache: dict[str, int] = {}

    def depth_of(cid: str, stack: frozenset[str] = frozenset()) -> int:
        if cid in depth_cache:
            return depth_cache[cid]
        if cid in stack:
            return 0
        c = by_id.get(cid)
        if not c:
            return 0
        parent = str(c.get("reply_to_comment_id") or "0")
        if parent in ("0", "", "None"):
            d = 0
        elif parent not in by_id:
            d = 1
        else:
            d = depth_of(parent, stack | {cid}) + 1
        depth_cache[cid] = d
        return d

    out: list[dict] = []
    for c in comments:
        cid = str(c.get("comment_id") or "")
        if not cid:
            continue
        ts = to_epoch(c.get("timestamp"))
        if ts is None:
            continue
        author = c.get("author") or {}
        parent = str(c.get("reply_to_comment_id") or "0")
        parent_id = None if parent in ("0", "", "None") else parent
        body = rich_text_to_text(c.get("rich_text_items") or [])
        emoji_ids = [
            (it.get("emotion") or {}).get("emotion")
            for it in (c.get("rich_text_items") or [])
            if isinstance(it, dict) and it.get("type") == 1
        ]
        has_image = bool(c.get("picture_items")) or any(
            isinstance(it, dict) and it.get("type") == 4
            for it in (c.get("rich_text_items") or [])
        )
        if not body:
            # Keep an explicit marker for comments whose payload has no text:
            # custom emoji, image-only, or a deleted/blank body.
            if emoji_ids:
                body = "[emoji]"
            elif has_image:
                body = "[image]"
            else:
                body = "[empty]"
        like = c.get("like") or {}
        raw = {
            "comment_id": cid,
            "timestamp": c.get("timestamp"),
            "status": c.get("status"),
            "module_id": c.get("module_id"),
            "reply_to_comment_id": c.get("reply_to_comment_id"),
            "reply_to_user": {
                "user_id": str((c.get("reply_to_user") or {}).get("user_id") or "") or None,
                "nick_name": (c.get("reply_to_user") or {}).get("nick_name"),
            },
            "pictures": [
                (p.get("big_pic") or p.get("org_pic") or {}).get("url")
                for p in (c.get("picture_items") or [])
                if isinstance(p, dict)
            ],
            "like": {"liked_num": like.get("liked_num")},
            "current_lang": c.get("current_lang"),
            "original_lang": c.get("original_lang"),
            "emoji_ids": emoji_ids,
            "rich_text_items": [
                {
                    "type": it.get("type"),
                    "text": it.get("text"),
                    "link": (it.get("text_link") or {}).get("link"),
                    "link_text": (it.get("text_link") or {}).get("text"),
                }
                for it in (c.get("rich_text_items") or [])
                if isinstance(it, dict)
            ],
        }
        out.append(
            {
                "record_type": "reply",
                "source": SOURCE,
                "channel": None,
                "native_id": cid,
                "post_native_id": post_native_id,
                "parent_native_id": parent_id,
                "depth": depth_of(cid),
                "author": author.get("nick_name"),
                "author_id": str(author.get("user_id") or "") or None,
                "created_utc": ts,
                "body": body,
                "score": like.get("liked_num"),
                "url": post_url,
                "lang": None,
                "raw": raw,
            }
        )
    out.sort(key=lambda r: (r["created_utc"], r["native_id"]))
    return out


def collect_ticker(
    ticker: str, no_cache: bool = False, limit_posts: int = 0, feed_pages: int = 0
) -> dict:
    cfg = TICKERS[ticker]
    col = Collector(ticker, cfg, no_cache=no_cache)
    log(f"=== {ticker} ({cfg['name']}, {cfg['market']}) ===")
    feeds = col.collect_feed(feed_pages or MAX_FEED_PAGES)

    # Filter to the window (inclusive) and deduplicate by feed id.
    in_window = []
    for f in feeds:
        ts = to_epoch((f.get("feed_comm") or {}).get("timestamp"))
        if ts is None:
            col.errors.append(f"feed missing timestamp: {(f.get('feed_comm') or {}).get('feed_id')}")
            continue
        if WINDOW_START <= ts <= WINDOW_END:
            in_window.append(f)
    in_window.sort(key=lambda f: to_epoch((f.get("feed_comm") or {}).get("timestamp")))
    if limit_posts:
        in_window = in_window[:limit_posts]

    log(f"  {len(in_window)} posts inside window; fetching bodies/comments")

    records: list[dict] = []
    seen_ids: set[str] = set()
    detail_count = 0
    for i, feed in enumerate(in_window, 1):
        fid = str((feed.get("feed_comm") or {}).get("feed_id"))
        if fid in seen_ids:
            continue
        seen_ids.add(fid)

        detail = None
        summary = feed.get("summary") or {}
        preview = post_body(feed)
        # `summary.is_complete` is not fully reliable: some long posts are cut
        # off mid-sentence with a trailing ellipsis while still flagged true.
        needs_detail = (not summary.get("is_complete")) or bool(
            re.search(r"(?:\.{2,}|…)\s*$", preview)
        )
        if needs_detail and detail_count < MAX_DETAIL_PAGES:
            detail = col.collect_detail(feed)
            detail_count += 1

        post = build_post(feed, detail)
        post["channel"] = ticker
        post["ticker"] = ticker
        records.append(post)

        comments = col.collect_comments(feed)
        replies = build_comments(fid, post["url"], comments)
        for r in replies:
            r["channel"] = ticker
            r["ticker"] = ticker
        records.extend(replies)

        if i % 100 == 0:
            log(
                f"  posts {i}/{len(in_window)} | replies so far "
                f"{sum(1 for r in records if r['record_type']=='reply')}"
            )

    out_path = OUT_DIR / f"{SOURCE}_{ticker}.jsonl"
    tmp = out_path.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    os.replace(tmp, out_path)

    posts_n = sum(1 for r in records if r["record_type"] == "post")
    replies_n = len(records) - posts_n
    log(
        f"  wrote {out_path.name}: {posts_n} posts, {replies_n} replies, "
        f"{col.requests_made} requests, {len(col.errors)} issues"
    )
    return {
        "ticker": ticker,
        "posts": posts_n,
        "replies": replies_n,
        "records": len(records),
        "feed_pages": col.feed_pages,
        "requests": col.requests_made,
        "comment_requests": col.comment_requests,
        "detail_requests": col.detail_requests,
        "errors": col.errors,
        "output": str(out_path),
        "min_ts": min((r["created_utc"] for r in records if r.get("created_utc")), default=None),
        "max_ts": max((r["created_utc"] for r in records if r.get("created_utc")), default=None),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ticker", choices=["GENTING", "GENM", "both"], default="both")
    ap.add_argument("--no-cache", action="store_true", help="ignore API response cache")
    ap.add_argument("--limit-posts", type=int, default=0, help="debug: only emit N posts")
    ap.add_argument("--feed-pages", type=int, default=0, help="debug: stop after N feed pages")
    args = ap.parse_args(argv)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    tickers = ["GENTING", "GENM"] if args.ticker == "both" else [args.ticker]
    summaries = []
    for t in tickers:
        summaries.append(
            collect_ticker(
                t,
                no_cache=args.no_cache,
                limit_posts=args.limit_posts,
                feed_pages=args.feed_pages,
            )
        )
        (OUT_DIR / f".{SOURCE}_{t}_summary.json").write_text(
            json.dumps(summaries[-1], ensure_ascii=False, indent=2), encoding="utf-8"
        )
    print(json.dumps(summaries, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
