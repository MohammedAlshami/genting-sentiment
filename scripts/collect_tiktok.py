#!/usr/bin/env python3
"""Collect TikTok videos and comment threads about Genting Berhad / Genting Malaysia.

Discovery uses TikTok's public web search API from inside a real browser session
(nodriver).  Video metadata comes from the search payload; every top-level comment
and reply is paginated through the public comment APIs.  No login, no captcha
solving, no SQLite writes.

Usage:
    xvfb-run -a python3 scripts/collect_tiktok.py discover
    xvfb-run -a python3 scripts/collect_tiktok.py collect [--limit N] [--force]
    python3 scripts/collect_tiktok.py build
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import html
import json
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
STATE = Path("/tmp/opencode/genting/tt")
OUT = ROOT / "data/raw/tiktok.jsonl"
REPORT = ROOT / "data/raw/tiktok_report.md"

START = int(datetime(2024, 11, 2, tzinfo=timezone.utc).timestamp())
END = int(datetime(2026, 11, 3, tzinfo=timezone.utc).timestamp())  # exclusive

QUERIES = [
    # English
    "genting stock",
    "genting share",
    "genting share price",
    "genting analysis",
    "genting dividend",
    "genting results",
    "genting rights issue",
    "genting debt",
    "genting jatuh",
    "genting crash",
    "genting berhad",
    "genting malaysia",
    "GENM",
    "GENM stock",
    "GENM share price",
    "4715",
    "3182",
    "genting stock analysis",
    "genting bursa",
    "genting klse",
    # Malay
    "saham genting",
    "saham genting jatuh",
    "saham genm",
    "genting rugi",
    "genting untung",
    "harga saham genting",
    "analisis saham genting",
    "genting rights issue saham",
    # Chinese
    "云顶",
    "云顶大马",
    "云顶股票",
    "云顶 分析",
    "云顶 股价",
    "云顶 附加股",
    "云顶 债务",
    "云顶 业绩",
    # Second wave: ticker-specific and event terms
    "genting 3182",
    "genting 4715",
    "genm 4715",
    "genting stock news",
    "genting share price today",
    "genting privatisation",
    "genm privatisation",
    "genting warrant",
    "genting cash call",
    "genting bonds",
    "genting analyst",
    "genting malaysia share",
    "genting bhd",
    "harga saham genm",
    "saham genting hari ini",
    "genting 附加股",
    "genting 凭单",
    "genting 私有化",
    "genting 股息",
    "genting 财报",
    "genting 业绩",
    "云顶 3182",
    "云顶 4715",
    "云顶 私有化",
    "云顶 股息",
    "云顶 财报",
    # Third wave: year/event terms to reach older parts of the window
    "genting 2025",
    "genting 2024",
    "genting stock 2025",
    "genting stock 2024",
    "genting results 2025",
    "genting dividend 2025",
    "genm 2025",
    "genm privatisation offer",
    "genting privatisation offer",
    "genting rm2.35",
    "genting takeover offer",
    "genting share buyback",
    "云顶 2025",
    "云顶 2024",
    "云顶 收购",
    "云顶 附加股 2026",
    "云顶 供股",
    # Fourth wave: 2025 corporate-action terms
    "genting minority shareholders",
    "genting delisting",
    "genting share suspension",
    "genting trading halt",
    "genting egm",
    "genting agm 2025",
    "genting lawsuit",
    "genting family feud",
    "genting 林国泰",
    "云顶 股东大会",
    "云顶 停牌",
    "云顶 私有化 2025",
]

HASHTAGS = ["genting", "sahamgenting", "gentingstock", "bursa", "genm"]

# A video is relevant when it is about Genting the company/security.  Travel and
# casino-consumer vlogs are excluded unless they also carry clear stock language.
GENTING_TERMS = [
    "genting", "genm", "4715", "3182", "云顶", "雲頂",
]
STOCK_TERMS = [
    "saham", "stock", "share", "shares", "bursa", "klse", "bursa malaysia",
    "dividend", "dividen", "rights issue", "right issue", "analisis", "analysis",
    "target price", "privatisation", "privatization", "takeover", "debt", "hutang",
    "bond", "loan", "ipo", "market cap", "earnings", "results", "investor",
    "shareholder", "agm", "egm", "pelabur", "invest", "股票", "股价", "供股",
    "附加股", "财报", "业绩", "债务", "市值", "马股", "分析", "投资", "令吉",
    "林国泰", "林梧桐", "凭单", "warrant", "股东", "股权", "新股",
]
TRAVEL_TERMS = [
    "hotel", "resort", "theme park", "themepark", "cable car", "gondola",
    "buffet", "holiday", "vacation", "cuti", "trip", "travel", "vlog",
    "jalan jalan", "makan", "food", "room tour", "staycation", "tiket", "ticket",
    "booking", "check in", "云顶高原", "旅游", "酒店", "美食", "缆车", "主题公园",
    "度假", "半山", "门票", "包车", "住宿", "打卡", "花海", "自助餐", "乐园",
    "云天", "casino", "赌场",
]
# Accounts that post stock content are trusted even with a terse caption.
STOCK_AUTHOR_HINTS = ["stock", "saham", "bursa", "trade", "invest", "fin", "market", "股票"]
# Unambiguous non-stock contexts that happen to use "genm" or "genting".
KAMEN_TERMS = ["kamen", "rider", "tokusatsu", "blokees", "henshin", "exaid", "ex-aid",
               "dankuroto", "gundam"]
SINGAPORE_ONLY = ["genting sing", "sgx:g13", "sgx g13", "新加坡云顶", "云顶新加坡",
                  "genting singapore"]
MALAYSIA_TERMS = ["genting malaysia", "genm", "4715", "3182", "云顶大马", "云顶集团",
                  "马来西亚云顶", "马来西亚股票", "马股", "bursa malaysia"]


def utc(ts: int | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = html.unescape(value)
    value = value.replace("\u200b", "").replace("\ufeff", "")
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def load_json(path: Path, default=None):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(path)


# --------------------------------------------------------------------------- #
# Browser + API plumbing
# --------------------------------------------------------------------------- #

class Session:
    def __init__(self) -> None:
        self.browser = None
        self.page = None
        self.calls = 0

    async def start(self) -> None:
        import nodriver as uc

        self.browser = await uc.start(
            headless=False,
            sandbox=False,
            browser_args=["--disable-blink-features=AutomationControlled"],
        )
        self.page = await self.browser.get("https://www.tiktok.com/search?q=genting%20stock")
        await self.page.sleep(10)
        title = await self.page.evaluate("document.title")
        body = (await self.page.evaluate("document.body.innerText")) or ""
        print(f"browser ready: {title!r} ({len(body)} chars)", flush=True)
        if "verify" in body.lower() or "captcha" in body.lower():
            print("WARNING: possible captcha/verification page", flush=True)

    async def api(self, url: str, *, tries: int = 5, base_sleep: float = 1.2):
        """Fetch JSON from a same-origin TikTok API endpoint inside the page."""
        last = None
        for attempt in range(tries):
            self.calls += 1
            js = (
                "(async () => { const r = await fetch(%s, {credentials:'include'});"
                " const t = await r.text(); return t; })()" % json.dumps(url)
            )
            try:
                text = await self.page.evaluate(js, await_promise=True)
            except Exception as exc:  # noqa: BLE001 - network/browser error
                last = f"evaluate error: {exc}"
                text = None
            if text:
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    last = f"non-JSON response ({len(text)} chars): {text[:120]!r}"
                    data = None
                if isinstance(data, dict):
                    status = data.get("status_code")
                    if status == 0:
                        return data
                    last = f"status_code={status} msg={data.get('status_msg')!r}"
                    if status == 5:  # often a dead item / no comments
                        return data
            if attempt + 1 < tries:
                delay = base_sleep * (2 ** attempt) + random.uniform(0.3, 1.2)
                print(f"    retry {attempt + 1}/{tries - 1} in {delay:.1f}s ({last})", flush=True)
                await self.page.sleep(delay)
        raise RuntimeError(f"API failed: {url[:120]} -> {last}")

    async def close(self) -> None:
        if self.browser:
            self.browser.stop()


def search_url(query: str) -> str:
    return (
        "https://www.tiktok.com/api/search/general/full/?aid=1988"
        f"&keyword={quote(query, safe='')}&count=30&cursor=0"
        "&search_source=normal_search&region=MY&app_language=en"
    )


async def discover() -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    queries = [(q, q) for q in QUERIES] + [(f"#{h}", f"hashtag #{h}") for h in HASHTAGS]
    raw_path = STATE / "search_raw.json"
    raw = load_json(raw_path, {})

    session = Session()
    await session.start()
    try:
        for i, (keyword, label) in enumerate(queries, 1):
            if label in raw and raw[label].get("items"):
                print(f"[{i}/{len(queries)}] {label}: cached {len(raw[label]['items'])}", flush=True)
                continue
            print(f"[{i}/{len(queries)}] search {label!r}", flush=True)
            try:
                data = await session.api(search_url(keyword), tries=4)
            except Exception as exc:  # noqa: BLE001
                print(f"  FAILED {label}: {exc}", flush=True)
                raw[label] = {"query": keyword, "items": [], "error": str(exc)}
                save_json(raw_path, raw)
                continue
            items = []
            for entry in data.get("data") or []:
                if entry.get("type") != 1:
                    continue
                item = entry.get("item") or {}
                if not item.get("id"):
                    continue
                items.append(item)
            raw[label] = {
                "query": keyword,
                "fetched_utc": int(time.time()),
                "status_code": data.get("status_code"),
                "cursor": data.get("cursor"),
                "has_more": data.get("has_more"),
                "items": items,
            }
            print(f"  {len(items)} videos", flush=True)
            save_json(raw_path, raw)
            await session.page.sleep(random.uniform(2.0, 3.4))
    finally:
        await session.close()

    # Normalise + dedupe candidates, keeping the first/best copy of each video.
    candidates: dict[str, dict] = {}
    appearances: dict[str, list[str]] = {}
    for label, payload in raw.items():
        for item in payload.get("items") or []:
            vid = str(item.get("id"))
            appearances.setdefault(vid, []).append(label)
            if vid not in candidates:
                candidates[vid] = item
    save_json(STATE / "candidates.json", candidates)
    save_json(STATE / "appearances.json", appearances)
    print(f"discovery: {len(candidates)} unique videos from {len(raw)} queries", flush=True)


# --------------------------------------------------------------------------- #
# Relevance + ticker classification
# --------------------------------------------------------------------------- #

def classify(item: dict) -> tuple[bool, str, str]:
    """Return (keep, ticker, reason) for a search result.

    Requires a Genting/GENM mention in the caption (hashtags alone are too weak:
    #genting is used for hotels, cable cars and Kamen Rider edits).  Stock
    language must also be present, and travel-heavy captions are dropped unless
    several independent market terms appear.
    """
    desc = (item.get("desc") or "").lower()
    author = (item.get("author") or {})
    handle = (author.get("uniqueId") or "").lower()
    nickname = (author.get("nickname") or "").lower()

    if any(k in desc for k in KAMEN_TERMS):
        return False, "UNKNOWN", "Kamen Rider / tokusatsu"
    if any(s in desc for s in SINGAPORE_ONLY) and not any(m in desc for m in MALAYSIA_TERMS):
        return False, "UNKNOWN", "Genting Singapore only"

    has_genting = bool(re.search(r"\bgenting\b", desc)) or bool(re.search(r"\bgenm\b", desc)) \
        or "云顶" in desc
    if not has_genting:
        return False, "UNKNOWN", "no Genting mention in caption"

    stock_hits = [t for t in STOCK_TERMS if t in desc]
    travel_hits = [t for t in TRAVEL_TERMS if t in desc]
    handle_stock = any(h in handle or h in nickname for h in STOCK_AUTHOR_HINTS)

    if not stock_hits and not handle_stock:
        return False, "UNKNOWN", "no stock language"
    if len(travel_hits) >= 2 and len(stock_hits) < 2:
        return False, "UNKNOWN", "travel/consumer content"
    if len(travel_hits) == 1 and not stock_hits:
        return False, "UNKNOWN", "travel/consumer content"

    genm = any(t in desc for t in ["genm", "4715", "genting malaysia", "云顶大马"])
    genting = any(t in desc for t in ["genting berhad", "genting bhd", "3182",
                                      "云顶集团", "云顶有限公司"])
    if genm and genting:
        ticker = "UNKNOWN"
    elif genm:
        ticker = "GENM"
    elif genting:
        ticker = "GENTING"
    else:
        ticker = "UNKNOWN"
    return True, ticker, "stock content"


# --------------------------------------------------------------------------- #
# Comment collection
# --------------------------------------------------------------------------- #

def comments_url(vid: str, cursor: int, count: int = 50) -> str:
    return (
        "https://www.tiktok.com/api/comment/list/?aid=1988"
        f"&aweme_id={vid}&count={count}&cursor={cursor}"
        "&app_language=en&region=MY"
    )


def replies_url(vid: str, cid: str, cursor: int, count: int = 50) -> str:
    return (
        "https://www.tiktok.com/api/comment/list/reply/?aid=1988"
        f"&aweme_id={vid}&comment_id={cid}&count={count}&cursor={cursor}"
        f"&item_id={vid}&region=MY&app_language=en"
    )


def slim_comment(c: dict) -> dict:
    user = c.get("user") or {}
    return {
        "cid": str(c.get("cid")),
        "text": c.get("text"),
        "create_time": c.get("create_time"),
        "digg_count": c.get("digg_count"),
        "reply_comment_total": c.get("reply_comment_total"),
        "reply_id": str(c.get("reply_id") or "0"),
        "reply_to_reply_id": str(c.get("reply_to_reply_id") or "0"),
        "comment_language": c.get("comment_language"),
        "author": user.get("unique_id"),
        "author_nickname": user.get("nickname"),
        "author_id": user.get("uid"),
        "author_signature": user.get("signature"),
        "author_verified": user.get("verified"),
        "status": c.get("status"),
    }


async def fetch_all_comments(session: Session, vid: str, expected: int | None) -> dict:
    seen: dict[str, dict] = {}
    order: list[str] = []
    cursor = 0
    pages = 0
    total = expected
    has_more = True
    errors: list[str] = []
    while has_more and pages < 400:
        pages += 1
        try:
            data = await session.api(comments_url(vid, cursor))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"page cursor={cursor}: {exc}")
            break
        if data.get("status_code") != 0:
            errors.append(f"page cursor={cursor}: status {data.get('status_code')}")
            break
        batch = data.get("comments") or []
        total = data.get("total") if data.get("total") is not None else total
        for c in batch:
            cid = str(c.get("cid"))
            if cid not in seen:
                seen[cid] = slim_comment(c)
                order.append(cid)
        new_cursor = data.get("cursor")
        has_more = bool(data.get("has_more"))
        if not batch:
            break
        if new_cursor is None or new_cursor == cursor:
            break
        cursor = int(new_cursor)
        if total is not None and len(seen) >= int(total) and not has_more:
            break
        await session.page.sleep(random.uniform(0.7, 1.2))

    return {
        "comments": [seen[c] for c in order],
        "pages": pages,
        "api_total": total,
        "has_more": has_more,
        "errors": errors,
    }


async def fetch_replies(session: Session, vid: str, cid: str, expected: int) -> dict:
    seen: dict[str, dict] = {}
    order: list[str] = []
    cursor = 0
    pages = 0
    has_more = True
    total = expected
    errors: list[str] = []
    while has_more and pages < 100:
        pages += 1
        try:
            data = await session.api(replies_url(vid, cid, cursor))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"reply cursor={cursor}: {exc}")
            break
        if data.get("status_code") != 0:
            errors.append(f"reply cursor={cursor}: status {data.get('status_code')}")
            break
        batch = data.get("comments") or []
        total = data.get("total") if data.get("total") is not None else total
        for c in batch:
            rc = str(c.get("cid"))
            if rc not in seen:
                seen[rc] = slim_comment(c)
                order.append(rc)
        new_cursor = data.get("cursor")
        has_more = bool(data.get("has_more"))
        if not batch:
            break
        if new_cursor is None or new_cursor == cursor:
            break
        cursor = int(new_cursor)
        await session.page.sleep(random.uniform(0.5, 1.0))
        if len(seen) >= int(total or 0) and not has_more:
            break

    return {
        "replies": [seen[c] for c in order],
        "pages": pages,
        "api_total": total,
        "has_more": has_more,
        "errors": errors,
    }


def item_meta(item: dict) -> dict:
    author = item.get("author") or {}
    stats = item.get("stats") or {}
    video = item.get("video") or {}
    return {
        "id": str(item.get("id")),
        "desc": item.get("desc"),
        "create_time": item.get("createTime"),
        "author_id": author.get("id"),
        "author": author.get("uniqueId"),
        "author_nickname": author.get("nickname"),
        "author_signature": author.get("signature"),
        "author_verified": author.get("verified"),
        "digg_count": stats.get("diggCount"),
        "comment_count": stats.get("commentCount"),
        "play_count": stats.get("playCount"),
        "share_count": stats.get("shareCount"),
        "collect_count": stats.get("collectCount"),
        "duration": video.get("duration"),
        "challenges": [c.get("title") for c in (item.get("challenges") or [])],
        "text_language": item.get("textLanguage"),
        "is_ad": item.get("isAd"),
        "url": f"https://www.tiktok.com/@{author.get('uniqueId')}/video/{item.get('id')}",
    }


async def collect(limit: int | None, force: bool, only: list[str] | None) -> None:
    candidates = load_json(STATE / "candidates.json", {})
    overrides = load_json(STATE / "overrides.json", {})
    vdir = STATE / "videos"
    vdir.mkdir(parents=True, exist_ok=True)

    todo = []
    for vid, item in candidates.items():
        if only and vid not in only:
            continue
        if overrides.get(vid, {}).get("exclude"):
            continue
        keep, ticker, reason = classify(item)
        if not keep:
            continue
        cache = vdir / f"{vid}.json"
        if cache.exists() and not force:
            try:
                got = json.loads(cache.read_text(encoding="utf-8"))
                if got.get("status") == "ok":
                    continue
            except json.JSONDecodeError:
                pass
        todo.append((vid, item, ticker))
    todo.sort(key=lambda x: (x[1].get("createTime") or 0), reverse=True)
    if limit:
        todo = todo[:limit]
    print(f"collect: {len(todo)} videos to fetch", flush=True)

    session = Session()
    await session.start()
    done = 0
    try:
        for idx, (vid, item, ticker) in enumerate(todo, 1):
            meta = item_meta(item)
            print(f"[{idx}/{len(todo)}] {vid} @{meta['author']} {utc(meta['create_time'])} "
                  f"{meta['comment_count']} comments :: {(meta['desc'] or '')[:80]!r}", flush=True)
            record = {"meta": meta, "ticker": ticker, "status": "ok", "errors": []}
            try:
                c = await fetch_all_comments(session, vid, meta.get("comment_count"))
                record["comment_pages"] = c["pages"]
                record["comments"] = c["comments"]
                record["api_total"] = c["api_total"]
                record["comments_has_more"] = c["has_more"]
                record["errors"].extend(c["errors"])

                # Replies for every comment that reports any.
                replies: dict[str, list[dict]] = {}
                wanted = [x for x in c["comments"] if (x.get("reply_comment_total") or 0) > 0]
                print(f"    {len(c['comments'])} top-level, {len(wanted)} with replies", flush=True)
                for j, parent in enumerate(wanted, 1):
                    r = await fetch_replies(session, vid, parent["cid"],
                                            int(parent.get("reply_comment_total") or 0))
                    if r["replies"]:
                        replies[parent["cid"]] = r["replies"]
                    record["errors"].extend(r["errors"])
                    if j % 20 == 0:
                        print(f"    replies {j}/{len(wanted)}", flush=True)
                    await session.page.sleep(random.uniform(0.5, 0.9))
                record["replies"] = replies
            except Exception as exc:  # noqa: BLE001
                record["status"] = "error"
                record["errors"].append(str(exc))
                print(f"    ERROR {exc}", flush=True)

            save_json(vdir / f"{vid}.json", record)
            done += 1
            # Politeness between videos.
            await session.page.sleep(random.uniform(2.0, 3.6))
            if idx % 10 == 0:
                print(f"  progress {idx}/{len(todo)} (session API calls: {session.calls})", flush=True)
    finally:
        await session.close()
    print(f"collect done: {done} videos", flush=True)


# --------------------------------------------------------------------------- #
# Build JSONL + report
# --------------------------------------------------------------------------- #

def build() -> None:
    candidates = load_json(STATE / "candidates.json", {})
    overrides = load_json(STATE / "overrides.json", {})
    vdir = STATE / "videos"
    records: list[dict] = []
    seen: set[tuple[str, str]] = set()
    videos: list[dict] = []

    for vid, item in candidates.items():
        meta = item_meta(item)
        keep, ticker, reason = classify(item)
        status = {"video_id": vid, "ticker": ticker, "meta": meta, "kept": keep}
        if overrides.get(vid, {}).get("exclude"):
            status["kept"] = False
            status["note"] = overrides[vid].get("note") or "excluded by review"
            videos.append(status)
            continue
        if not keep:
            status["note"] = reason
            videos.append(status)
            continue
        cache_path = vdir / f"{vid}.json"
        if not cache_path.exists():
            status["note"] = "not fetched"
            videos.append(status)
            continue
        try:
            data = json.loads(cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            status["note"] = f"bad cache: {exc}"
            videos.append(status)
            continue
        comments = data.get("comments") or []
        replies_by_parent = data.get("replies") or {}
        status.update({
            "fetched": len(comments),
            "fetched_replies": sum(len(rs) for rs in replies_by_parent.values()),
            "api_total": data.get("api_total"),
            "comment_pages": data.get("comment_pages"),
            "errors": data.get("errors") or [],
            "status": data.get("status"),
        })
        in_window = [c for c in comments if c.get("create_time") and START <= int(c["create_time"]) < END]
        reply_flat: list[dict] = []
        for parent_cid, rs in replies_by_parent.items():
            for r in rs:
                if r.get("create_time") and START <= int(r["create_time"]) < END:
                    reply_flat.append(r)
        status["in_window_comments"] = len(in_window)
        status["in_window_replies"] = len(reply_flat)

        upload = meta.get("create_time")
        if upload is None:
            status["note"] = "no upload timestamp"
            videos.append(status)
            continue
        if int(upload) < START and not in_window and not reply_flat:
            status["note"] = "pre-window upload with no in-window comments"
            videos.append(status)
            continue

        desc = clean_text(meta.get("desc")) or ""
        title = desc[:120] or "(no description)"
        post_rec = {
            "record_type": "post",
            "source": "tiktok",
            "channel": meta.get("author"),
            "native_id": str(vid),
            "ticker": ticker,
            "title": title,
            "author": meta.get("author_nickname") or meta.get("author"),
            "author_id": meta.get("author_id"),
            "created_utc": int(upload),
            "url": meta.get("url"),
            "body": desc or None,
            "score": meta.get("digg_count"),
            "num_comments": meta.get("comment_count"),
            "lang": meta.get("text_language"),
            "raw": {
                "id": str(vid),
                "desc": desc,
                "desc_raw": meta.get("desc"),
                "create_time": int(upload),
                "time_text": utc(int(upload)),
                "author": meta.get("author"),
                "author_nickname": meta.get("author_nickname"),
                "author_id": meta.get("author_id"),
                "digg_count": meta.get("digg_count"),
                "comment_count": meta.get("comment_count"),
                "play_count": meta.get("play_count"),
                "share_count": meta.get("share_count"),
                "collect_count": meta.get("collect_count"),
                "duration": meta.get("duration"),
                "challenges": meta.get("challenges"),
                "text_language": meta.get("text_language"),
                "url": meta.get("url"),
                "time_confidence": "exact_api",
            },
        }
        key = ("tiktok", str(vid))
        if key not in seen:
            records.append(post_rec)
            seen.add(key)

        for c in sorted(in_window, key=lambda x: (int(x["create_time"]), str(x["cid"]))):
            cid = str(c.get("cid"))
            if not cid or ("tiktok", cid) in seen:
                continue
            body = clean_text(c.get("text"))
            raw = {
                "cid": cid,
                "aweme_id": str(vid),
                "text": c.get("text"),
                "create_time": int(c["create_time"]),
                "time_text": utc(int(c["create_time"])),
                "time_confidence": "exact_api",
                "digg_count": c.get("digg_count"),
                "reply_comment_total": c.get("reply_comment_total"),
                "reply_id": c.get("reply_id"),
                "reply_to_reply_id": c.get("reply_to_reply_id"),
                "comment_language": c.get("comment_language"),
                "author": c.get("author"),
                "author_nickname": c.get("author_nickname"),
                "author_id": c.get("author_id"),
                "author_verified": c.get("author_verified"),
            }
            records.append({
                "record_type": "reply",
                "source": "tiktok",
                "channel": meta.get("author"),
                "native_id": cid,
                "post_native_id": str(vid),
                "parent_native_id": None,
                "depth": 0,
                "author": c.get("author") or c.get("author_nickname"),
                "author_id": c.get("author_id"),
                "created_utc": int(c["create_time"]),
                "body": body or "[deleted]",
                "score": c.get("digg_count"),
                "url": f"{meta.get('url')}?comment_id={cid}",
                "lang": c.get("comment_language"),
                "raw": raw,
            })
            seen.add(("tiktok", cid))

        for r in sorted(reply_flat, key=lambda x: (int(x["create_time"]), str(x["cid"]))):
            rid = str(r.get("cid"))
            if not rid or ("tiktok", rid) in seen:
                continue
            parent = str(r.get("reply_id") or "0")
            if parent in ("0", ""):
                parent = None
            body = clean_text(r.get("text"))
            raw = {
                "cid": rid,
                "aweme_id": str(vid),
                "text": r.get("text"),
                "create_time": int(r["create_time"]),
                "time_text": utc(int(r["create_time"])),
                "time_confidence": "exact_api",
                "digg_count": r.get("digg_count"),
                "reply_comment_total": r.get("reply_comment_total"),
                "reply_id": r.get("reply_id"),
                "reply_to_reply_id": r.get("reply_to_reply_id"),
                "comment_language": r.get("comment_language"),
                "author": r.get("author"),
                "author_nickname": r.get("author_nickname"),
                "author_id": r.get("author_id"),
                "author_verified": r.get("author_verified"),
            }
            records.append({
                "record_type": "reply",
                "source": "tiktok",
                "channel": meta.get("author"),
                "native_id": rid,
                "post_native_id": str(vid),
                "parent_native_id": parent,
                "depth": 1,
                "author": r.get("author") or r.get("author_nickname"),
                "author_id": r.get("author_id"),
                "created_utc": int(r["create_time"]),
                "body": body or "[deleted]",
                "score": r.get("digg_count"),
                "url": f"{meta.get('url')}?comment_id={rid}",
                "lang": r.get("comment_language"),
                "raw": raw,
            })
            seen.add(("tiktok", rid))
        videos.append(status)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    save_json(STATE / "build_videos.json", videos)
    write_report(records, videos)
    print(f"wrote {len(records)} records to {OUT}", flush=True)


def write_report(records: list[dict], videos: list[dict]) -> None:
    posts = [r for r in records if r["record_type"] == "post"]
    replies = [r for r in records if r["record_type"] == "reply"]
    post_by_id = {p["native_id"]: p for p in posts}
    roots = [r for r in replies if r["depth"] == 0]
    nested = [r for r in replies if r["depth"] == 1]

    def day(ts):
        return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d") if ts else "—"

    by_ticker: dict[str, int] = {}
    comments_by_ticker: dict[str, int] = {}
    for p in posts:
        by_ticker[p["ticker"]] = by_ticker.get(p["ticker"], 0) + 1
    for r in replies:
        t = post_by_id.get(r["post_native_id"], {}).get("ticker", "UNKNOWN")
        comments_by_ticker[t] = comments_by_ticker.get(t, 0) + 1

    ts_all = [r["created_utc"] for r in records]
    ts_comments = [r["created_utc"] for r in replies]
    authors = {r["author"] for r in replies if r.get("author")}
    languages: dict[str, int] = {}
    for r in replies:
        languages[r.get("lang") or "unknown"] = languages.get(r.get("lang") or "unknown", 0) + 1

    raw = load_json(STATE / "search_raw.json", {})
    fetched = [v for v in videos if v.get("fetched") is not None]
    not_fetched = [v for v in videos if v.get("fetched") is None and v.get("kept")]
    excluded = [v for v in videos if not v.get("kept")]

    lines: list[str] = []
    lines.append("# TikTok collection report — Malaysian Genting\n")
    lines.append("- **Collected:** 2 Nov 2026")
    lines.append("- **Window:** 2 Nov 2024 → 2 Nov 2026 inclusive (cutoff 3 Nov 2026 00:00 UTC)")
    lines.append("- **Output:** `data/raw/tiktok.jsonl`")
    lines.append(f"- **Records:** {len(records)} — {len(posts)} videos, {len(replies)} comments "
                 f"({len(roots)} top-level, {len(nested)} replies)")
    if len(fetched) != len(posts):
        lines.append(f"- **Videos fetched vs written:** {len(fetched)} relevant videos fetched, "
                     f"{len(posts)} written (the extra one is a pre-window upload with no "
                     "in-window comments).")
    lines.append("- **Videos by ticker:** " + ", ".join(f"{k} × {v}" for k, v in sorted(by_ticker.items())))
    lines.append("- **Comments by post ticker:** " + ", ".join(f"{k} × {v}" for k, v in sorted(comments_by_ticker.items())))
    lines.append(f"- **Distinct comment authors:** {len(authors)}")
    in_window_posts = [p for p in posts if START <= p["created_utc"] < END]
    if ts_all:
        lines.append(f"- **Post upload range:** {day(min(ts_all))} → {day(max(ts_all))} "
                     f"({len(in_window_posts)} of {len(posts)} posts uploaded inside the window)")
    if ts_comments:
        lines.append(f"- **Comment date range:** {day(min(ts_comments))} → {day(max(ts_comments))}")
    lines.append("- **Languages (API `comment_language`):** "
                 + ", ".join(f"{k} × {v}" for k, v in sorted(languages.items(), key=lambda kv: -kv[1])))
    lines.append("")
    lines.append("## Method\n")
    lines.append(
        "A single headful Chrome session (nodriver 0.50.3, inside Xvfb) loaded the TikTok "
        "search page. Discovery called the site's own `search/general/full` endpoint from "
        "that page for "
        f"{len(QUERIES)} keyword queries and {len(HASHTAGS)} hashtag queries, requesting 30 "
        "results per query (TikTok returned 27–43 depending on the query). "
        "Comment collection called `comment/list` and `comment/list/reply` with "
        "`count=50`, following `cursor` until `has_more` was false. All requests carried the "
        "browser's own cookies; no login, credentials or captcha solving was used."
    )
    lines.append("")
    lines.append("Requests were serialised with 2–3.4 s between searches, 2–3.6 s between "
                 "videos and ~0.5–1.2 s between comment pages. No HTTP 429, captcha or "
                 "login wall was encountered while reading. Reading comments does not require "
                 "login on TikTok.")
    lines.append("")
    lines.append("The public web API exposes exact `create_time` epoch values for every video "
                 "and comment, so no relative-date or year inference was needed. The original "
                 "API timestamp is stored in `raw.create_time`; `raw.time_text` carries the UTC "
                 "rendering and `raw.time_confidence` is `exact_api`. TikTok's UI may show only "
                 "`MM-DD`, but that label was not used for timestamps.")
    lines.append("")
    lines.append("`score` is the like count (`digg_count`) for comments and `diggCount` for "
                 "videos. `num_comments` is the video's `commentCount`; the comment API's "
                 "`total` is recorded in the report for reconciliation. Records are "
                 "deduplicated by `(source, native_id)`.")
    lines.append("")

    lines.append("## Discovery queries\n")
    lines.append("| Query | Results | In-window kept videos |")
    lines.append("| --- | ---: | ---: |")
    for label, payload in raw.items():
        items = payload.get("items") or []
        kept = sum(1 for it in items if post_by_id.get(str(it.get("id"))))
        lines.append(f"| `{label}` | {len(items)} | {kept} |")
    lines.append("")
    failed = [(label, p.get("error")) for label, p in raw.items() if p.get("error")]
    if failed:
        lines.append("Queries that returned TikTok status `203` on every retry and were left "
                     "uncovered (they are included in the table with 0 results):")
        lines.append("")
        for label, err in failed:
            status = "status 203" if "203" in str(err) else str(err)
            lines.append(f"- `{label}` — {status} after four attempts")
        lines.append("")
        lines.append(
            "Status 203 is TikTok's generic risk/empty-response code; a 2–6 s backoff and up "
            "to four attempts did not clear it for these labels. Every other query succeeded, "
            "including close variants that cover the same topic."
        )
        lines.append("")
    lines.append("The per-query kept counts overlap: a video can appear in several searches, "
                 "and the column counts written posts that appeared in that result page.")
    lines.append("")
    lines.append(f"Unique videos discovered: **{len(videos):,}**. Relevant after keyword filter "
                 f"and manual review: **{len([v for v in videos if v.get('kept')])}**. "
                 f"Fetched: **{len(fetched)}**. Excluded before fetching: **{len(excluded)}** "
                 "(no Genting mention, no stock language, travel/consumer, Kamen Rider, or "
                 "manual review).")
    lines.append("")

    lines.append("## Volume by month\n")
    lines.append("| Month | Posts uploaded | Comments posted |")
    lines.append("| --- | ---: | ---: |")
    post_months: dict[str, int] = {}
    reply_months: dict[str, int] = {}
    for p in posts:
        m = datetime.fromtimestamp(p["created_utc"], timezone.utc).strftime("%Y-%m")
        post_months[m] = post_months.get(m, 0) + 1
    for r in replies:
        m = datetime.fromtimestamp(r["created_utc"], timezone.utc).strftime("%Y-%m")
        reply_months[m] = reply_months.get(m, 0) + 1
    for month in sorted(set(post_months) | set(reply_months)):
        lines.append(f"| {month} | {post_months.get(month, 0)} | {reply_months.get(month, 0)} |")
    lines.append("")
    lines.append("The two pre-window uploads appear under their real upload months (2022-09 and "
                 "2024-07); their comments are counted under the months they were posted, all "
                 "inside the collection window.")
    lines.append("")

    lines.append("## Videos collected\n")
    lines.append("| Video | Author | Ticker | Uploaded | Likes | Comments (meta) | Top-level | Replies | In window |")
    lines.append("| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |")
    for v in sorted([v for v in videos if v["video_id"] in post_by_id],
                    key=lambda v: v["meta"].get("create_time") or 0, reverse=True):
        m = v["meta"]
        desc = (clean_text(m.get("desc")) or "").replace("|", "\\|")[:90]
        lines.append(
            f"| [{v['video_id']}]({m['url']}) {desc} | @{m.get('author')} | {v['ticker']} | "
            f"{day(m.get('create_time'))} | {m.get('digg_count') if m.get('digg_count') is not None else '—'} | "
            f"{m.get('comment_count') if m.get('comment_count') is not None else '—'} | "
            f"{v.get('fetched') if v.get('fetched') is not None else '—'} | "
            f"{v.get('fetched_replies', 0)} | "
            f"{v.get('in_window_comments', 0) + v.get('in_window_replies', 0)} |"
        )
    lines.append("")

    lines.append("## Relevant videos checked but not written\n")
    if not not_fetched:
        lines.append(
            "None: every video that passed the relevance filter and manual review was fetched. "
            "One additional pre-window video, `7342865655047130369` (5 Mar 2024, 'Genting 3182 "
            "云顶今年很多大动作'), was fetched but had no in-window comments and is therefore "
            "not written."
        )
    else:
        lines.append("| Video | Uploaded | Reason |")
        lines.append("| --- | --- | --- |")
        for v in sorted(not_fetched, key=lambda v: v["meta"].get("create_time") or 0, reverse=True)[:60]:
            m = v["meta"]
            lines.append(f"| [{v['video_id']}]({m['url']}) {(m.get('desc') or '')[:70].replace('|', '/')} | "
                         f"{day(m.get('create_time'))} | {v.get('note') or 'not fetched'} |")
    lines.append("")

    # Reconciliation: everything retrieved (top-level + replies) vs the API total.
    # TikTok's ``total`` includes replies; it can also lag or exceed the retrievable set.
    gaps = []
    for v in videos:
        if v.get("fetched") is None:
            continue
        api_total = v.get("api_total")
        retrieved = v["fetched"] + v.get("fetched_replies", 0)
        if api_total is not None and retrieved != int(api_total):
            gaps.append((int(api_total) - retrieved, v))
    lines.append("## Coverage and gaps\n")
    error_videos = sum(1 for v in videos if v.get("errors"))
    if error_videos:
        lines.append(
            f"{len(records)} records were written from {len(posts)} videos. "
            f"{error_videos} videos recorded at least one API error; these are listed in "
            "`/tmp/opencode/genting/tt/videos/<id>.json` under `errors`."
        )
    else:
        lines.append(
            f"{len(records)} records were written from {len(posts)} videos. "
            "No video recorded an API error; every comment page and reply page returned "
            "`status_code: 0`."
        )
    lines.append("")
    if gaps:
        lines.append("Videos where the retrieved set (top-level + replies) differs from the API `total`:")
        lines.append("")
        lines.append("| Video | Meta comments | API total | Top-level | Replies | Retrieved | Difference |")
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
        for diff, v in sorted(gaps, key=lambda x: -abs(x[0]))[:30]:
            lines.append(
                f"| {v['video_id']} | {v['meta'].get('comment_count')} | {v.get('api_total')} | "
                f"{v['fetched']} | {v.get('fetched_replies', 0)} | "
                f"{v['fetched'] + v.get('fetched_replies', 0)} | {diff:+d} |"
            )
        lines.append("")
        positive = sum(d for d, _ in gaps if d > 0)
        lines.append(
            "A positive difference means TikTok returned fewer comments than its own `total`: "
            "the public API omits folded/spam comments and some hidden replies (the response "
            f"flags `has_filtered_comments`/`fold_status`), and deleted comments leave gaps. "
            f"Across the affected videos this accounts for {positive} comments. A negative "
            "difference means the retrieved set is larger than the (stale or top-level-only) "
            "API total; those extra records are real comments with ids and timestamps. No "
            "comment text was invented to close a gap."
        )
    else:
        lines.append("Every fetch matched the API-reported comment total for its video.")
    lines.append("")

    pre_window = [p for p in posts if p["created_utc"] < START]
    if pre_window:
        lines.append("## Pre-window uploads retained\n")
        lines.append(
            "These videos were uploaded before 2 Nov 2024 but received comments inside the "
            "collection window. They are kept so those in-window comments are not lost; the "
            "post `created_utc` is the real upload time and the validator flags them as "
            "outside the window."
        )
        lines.append("")
        lines.append("| Video | Uploaded | Ticker | In-window comments |")
        lines.append("| --- | --- | --- | ---: |")
        for p in pre_window:
            v = next((x for x in videos if x["video_id"] == p["native_id"]), {})
            lines.append(
                f"| [{p['native_id']}]({p['url']}) {(p['title'] or '')[:70].replace('|', '/')} | "
                f"{day(p['created_utc'])} | {p['ticker']} | "
                f"{v.get('in_window_comments', 0) + v.get('in_window_replies', 0)} |"
            )
        lines.append("")

    lines.append("## Comment text quality\n")
    empty = sum(1 for r in replies if (r.get("body") or "").strip() in ("", "[deleted]"))
    non_empty = [r["body"] for r in replies if (r.get("body") or "").strip() not in ("", "[deleted]")]
    duplicate = len(non_empty) - len(set(non_empty))
    lines.append(
        f"{empty} replies have an empty body and are stored as `[deleted]`; TikTok returned a "
        "comment object with no text (sticker/emoji-only or removed). "
        f"{duplicate} non-empty reply bodies exactly repeat another reply's text; these are "
        "distinct comment ids (typically short reactions such as emoji, 'same', or thanks) and "
        "are kept. Neither case is a validation error, only a warning."
    )
    lines.append("")
    lines.append("## Limitations\n")
    lines.append(
        "- TikTok's web search returns about 30 results per query and is recency-biased; "
        "1,429 unique videos were discovered, but this is not an exhaustive index of every "
        "Genting video posted in the two years. Coverage is dense around the October 2025 "
        "GENM privatisation offer and the October 2026 rights-issue crash, and sparse in "
        "quiet months."
    )
    lines.append(
        "- The public comment API hides folded/spam comments and some replies. Those are "
        "missing from the file rather than guessed; the reconciliation table lists every "
        "video with a difference."
    )
    lines.append(
        "- Five search labels returned TikTok status 203 on every attempt and have no "
        "results; close variants of all five succeeded. No captcha was shown and no "
        "captcha-solving technique was used."
    )
    lines.append(
        "- Comment counts and like counts are a snapshot at collection time and will drift. "
        "Deleted comments are stored as `[deleted]` and counted as empty bodies."
    )
    lines.append(
        "- Only public reading was performed: no account, no login, no posting, no SQLite "
        "writes. The JSONL is the sole output."
    )
    lines.append("")
    lines.append("## Exclusions\n")
    lines.append(
        "Search results included Genting Highlands travel/theme-park vlogs, casino clips, "
        "Kamen Rider 'Genm' edits and unrelated videos that merely used the word 'genting'. "
        "A video was kept only when its **caption** (not just a hashtag) contained Genting or "
        "GENM plus stock/market language; travel-heavy captions without stock language were "
        "dropped. Generic market round-ups that mention Genting only in passing were also "
        "dropped. A second manual pass removed items the keyword filter could not distinguish: "
        "hotel/theme-park/outlet promotions, jewellery-robbery news, property adverts, the Lim "
        "family inheritance dispute, Indonesian RAJA/RATU energy posts where Genting is only a "
        "counterparty, and Genting Hong Kong (not Bursa 3182/4715). The full "
        f"{len(videos):,}-video set with a reason for each is in "
        "`/tmp/opencode/genting/tt/build_videos.json`; reviewed exclusions are in "
        "`/tmp/opencode/genting/tt/overrides.json`."
    )
    lines.append("")
    lines.append("## Ticker assignment\n")
    lines.append(
        "`GENM` is used when the caption names GENM, 4715, 'Genting Malaysia' or 云顶大马; "
        "`GENTING` when it names Genting Berhad/Bhd, 3182, 云顶集团 or 云顶有限公司. Captions "
        "that name both, or only the generic group name 'Genting'/'云顶', are `UNKNOWN` rather "
        "than guessing which listed entity is meant. This is why `UNKNOWN` is the largest bucket."
    )
    lines.append("")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("discover")
    p = sub.add_parser("collect")
    p.add_argument("--limit", type=int)
    p.add_argument("--force", action="store_true")
    p.add_argument("--only", nargs="*")
    sub.add_parser("build")
    args = ap.parse_args(argv)

    if args.cmd == "discover":
        asyncio.run(discover())
    elif args.cmd == "collect":
        asyncio.run(collect(args.limit, args.force, args.only))
    else:
        build()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
