#!/usr/bin/env python3
"""Backfill KLSE Screener stock comments for 2016-11-02 .. 2024-11-01 MYT.

Writes data/raw/klse_screener_<TICKER>_2016-2024.jsonl.

Pagination is the "Load More" endpoint:
    /v2/comments/all/stock/<code>/<page>
returning {"count": n, "html": "..."}.  Pages are ordered by latest activity
(newest reply), so we walk backwards until the listing is exhausted.  The
listing normally shows only the last two replies of a card; cards with earlier
replies carry a "Previous replies (N)" link, so the detail page
/v2/comment/<id> is fetched, then /v2/comments/view_replies/<id>?last_id=...
is walked backwards in batches of 100 until the window start is passed (or the
endpoint returns no more replies).  This recovers hidden replies, not just the
two visible on the listing card.

Existing 2024-2026 corpus files are never touched; output names carry the
_2016-2024 suffix.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = "https://www.klsescreener.com"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
ROOT = Path(__file__).resolve().parents[1]
# Reuse the existing cache directory: listing pages 1-202 are refreshed below,
# while detail/reply cache entries are keyed by comment id and remain valid.
CACHE = Path("/tmp/opencode/klse_cache")
OUT = ROOT / "data" / "raw"

STOCKS = {
    "GENM": {"code": "4715", "name": "Genting Malaysia"},
    "GENTING": {"code": "3182", "name": "Genting Berhad"},
}

MYT = timezone(timedelta(hours=8))
WINDOW_START = int(datetime(2016, 11, 2, 0, 0, 0, tzinfo=MYT).timestamp())
WINDOW_END = int(datetime(2024, 11, 1, 23, 59, 59, tzinfo=MYT).timestamp())

# Always refresh the recent listing pages so page-number drift caused by new
# comments cannot create a hole at the boundary with the cached older pages.
REFRESH_PAGES = 205
MAX_PAGES = 1500
RUN_START = time.time()


class Fetcher:
    def __init__(self) -> None:
        self.s = requests.Session()
        self.s.headers.update(
            {
                "User-Agent": UA,
                "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": BASE + "/v2/discussion",
            }
        )
        self.requests = 0
        self.last = 0.0

    def get(self, url: str, *, json_mode: bool = True, xhr: bool = True):
        headers = None
        if not xhr:
            headers = {
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        for attempt in range(6):
            wait = 1.05 - (time.time() - self.last)
            if wait > 0:
                time.sleep(wait)
            self.last = time.time()
            self.requests += 1
            try:
                r = self.s.get(url, timeout=45, headers=headers)
            except requests.RequestException as exc:
                print(f"  ! {url} {exc}", flush=True)
                time.sleep(5 + attempt * 5)
                continue
            if r.status_code == 429 or 500 <= r.status_code < 600:
                delay = 10 * (attempt + 1)
                print(f"  ! HTTP {r.status_code} {url}; backoff {delay}s", flush=True)
                time.sleep(delay)
                continue
            if r.status_code != 200:
                if not xhr and r.status_code in (401, 403, 404, 410):
                    return None
                raise RuntimeError(f"HTTP {r.status_code} for {url}")
            if not json_mode:
                return r.text
            if not r.text.strip():
                # view_replies returns an empty 200 at the end of a thread.
                # Retry once in case it was transient.
                if attempt >= 1:
                    print(f"  . empty JSON payload from {url} (end of list)", flush=True)
                    return {"count": 0, "html": ""}
                time.sleep(2)
                continue
            try:
                return r.json()
            except ValueError:
                print(
                    f"  ! non-JSON response from {url}: {r.text[:160]!r}",
                    flush=True,
                )
                time.sleep(5 + attempt * 5)
                continue
        raise RuntimeError(f"giving up on {url}")


def parse_dt(text: str) -> int:
    dt = datetime.strptime(text.strip(), "%Y-%m-%d %H:%M:%S %z")
    return int(dt.astimezone(timezone.utc).timestamp())


def clean_text(node) -> str:
    if node is None:
        return ""
    for br in node.find_all("br"):
        br.replace_with("\n")
    text = node.get_text("\n")
    text = text.replace("\xa0", " ").replace("\u200b", "")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_card(el, stock_code: str, parent_id: str | None) -> dict | None:
    cid = el.get("id", "")
    m = re.fullmatch(r"comment-(\d+)", cid)
    if not m:
        return None
    cid = m.group(1)

    author_el = el.select_one("strong.text-primary")
    author = author_el.get_text(strip=True) if author_el else None
    author_id = None
    a = el.select_one('a[href^="/v2/users/comments/"]')
    if a:
        am = re.search(r"/v2/users/comments/(\d+)", a.get("href", ""))
        if am:
            author_id = am.group(1)

    body = clean_text(el.select_one("div.message-container"))
    date_el = el.select_one("[data-datetime]")
    dt_text = date_el.get("data-datetime") if date_el else None
    created = parse_dt(dt_text) if dt_text else None

    likes = None
    like_el = el.select_one(f'span.align-right.text-muted[data-id="{cid}"]')
    if like_el:
        lm = re.search(r"(\d+)\s*Like", like_el.get_text(" ", strip=True))
        likes = int(lm.group(1)) if lm else 0
    else:
        like_el = el.select_one(f'a.alike[data-id="{cid}"]')
        if like_el and like_el.get("data-count") is not None:
            likes = int(like_el["data-count"])

    is_reply = "comment-reply" in (el.get("class") or [])
    return {
        "id": cid,
        "author": author,
        "author_id": author_id,
        "body": body,
        "created_utc": created,
        "score": likes,
        "parent_id": parent_id,
        "depth": 1 if is_reply else 0,
        "datetime_text": dt_text,
        "stock": stock_code,
        "is_reply": is_reply,
    }


def parse_listing(html: str, stock_code: str) -> tuple[list[dict], list[str]]:
    soup = BeautifulSoup(html, "lxml")
    cards = soup.select('div.comment[id^="comment-"]')
    out: list[dict] = []
    with_prev: list[str] = []
    for card in cards:
        top = parse_card(card, stock_code, None)
        if not top:
            continue
        out.append(top)
        if "Previous replies" in card.get_text(" ", strip=True):
            with_prev.append(top["id"])
        for rep in card.select('div.comment-reply[id^="comment-"]'):
            rec = parse_card(rep, stock_code, top["id"])
            if rec:
                out.append(rec)
    return out, with_prev


def parse_detail(html: str, stock_code: str, parent_id: str) -> tuple[list[dict], dict | None]:
    soup = BeautifulSoup(html, "lxml")
    out: list[dict] = []
    parent_rec: dict | None = None
    for el in soup.select('div[id^="comment-"]'):
        cid = el.get("id", "")
        if not re.fullmatch(r"comment-\d+", cid):
            continue
        is_reply = "comment-reply" in (el.get("class") or [])
        rec = parse_card(el, stock_code, parent_id if is_reply else None)
        if rec:
            out.append(rec)
            if not is_reply:
                parent_rec = rec
    return out, parent_rec


def detail_more(html: str) -> tuple[str | None, int]:
    """Return (last_id, replies_left_count) for the 'previous replies' loader."""
    soup = BeautifulSoup(html, "lxml")
    el = soup.select_one("div.a-prev-replies-more[data-last-id]")
    if not el:
        return None, 0
    left = 0
    span = el.select_one("span.replies_left_count")
    if span:
        m = re.search(r"\d+", span.get_text())
        if m:
            left = int(m.group(0))
    return el.get("data-last-id"), left


def merge(records: dict[str, dict], recs: list[dict]) -> None:
    for rec in recs:
        old = records.get(rec["id"])
        if old is None:
            records[rec["id"]] = rec
        elif (not old["body"] and rec["body"]) or (old["created_utc"] is None and rec["created_utc"]):
            records[rec["id"]] = rec


def collect(ticker: str, code: str) -> tuple[list[dict], dict]:
    CACHE.mkdir(parents=True, exist_ok=True)
    f = Fetcher()
    records: dict[str, dict] = {}
    page = 1
    pages_done = 0
    cards_seen = 0
    detail_pages = 0
    detail_cached = 0
    reply_pages = 0
    reply_cached = 0
    last_seen: int | None = None
    stop = False
    while not stop:
        url = f"{BASE}/v2/comments/all/stock/{code}/{page}"
        cache_file = CACHE / f"{code}_{page}.json"
        use_cache = (
            page > REFRESH_PAGES
            and cache_file.exists()
            and cache_file.stat().st_mtime >= RUN_START
        )
        if use_cache:
            payload = json.loads(cache_file.read_text())
        else:
            payload = f.get(url)
            cache_file.write_text(json.dumps(payload))
        html = payload.get("html") or ""
        count = int(payload.get("count") or 0)
        page_records, with_prev = parse_listing(html, code)
        if not page_records:
            print(f"  page {page}: empty payload, end of archive", flush=True)
            break

        merge(records, page_records)
        cards_seen += len([r for r in page_records if r["depth"] == 0])
        stamps = [r["created_utc"] for r in page_records if r["created_utc"]]
        page_min = min(stamps) if stamps else 0
        page_max = max(stamps) if stamps else 0
        last_seen = page_min

        # Cards whose earlier replies are hidden need the detail page.
        for card_id in with_prev:
            detail_url = f"{BASE}/v2/comment/{card_id}"
            dfile = CACHE / f"detail_{card_id}.html"
            if dfile.exists():
                dhtml = dfile.read_text()
                detail_cached += 1
            else:
                dhtml = f.get(detail_url, json_mode=False, xhr=False)
                if dhtml is None:
                    dfile.write_text("")
                else:
                    dfile.write_text(dhtml)
                detail_pages += 1
            if not dhtml:
                print(f"  ! detail unavailable for comment {card_id}; using reply API", flush=True)
                last_id, left = "0", 0
                while True:
                    bfile = CACHE / f"replies_{card_id}_{last_id}.json"
                    if bfile.exists():
                        bpayload = json.loads(bfile.read_text())
                        reply_cached += 1
                    else:
                        bpayload = f.get(
                            f"{BASE}/v2/comments/view_replies/{card_id}?last_id={last_id}"
                        )
                        bfile.write_text(json.dumps(bpayload))
                        reply_pages += 1
                    brecs, _ = parse_detail(bpayload.get("html") or "", code, card_id)
                    merge(records, brecs)
                    b_stamps = [r["created_utc"] for r in brecs if r["created_utc"]]
                    new_last = bpayload.get("last_id")
                    new_left = int(bpayload.get("replies_left_count") or 0)
                    if not brecs:
                        break
                    if b_stamps and min(b_stamps) < WINDOW_START:
                        break
                    if not new_last or str(new_last) == str(last_id) or new_left <= 0:
                        break
                    last_id, left = str(new_last), new_left
                continue

            drecs, parent_rec = parse_detail(dhtml, code, card_id)
            merge(records, drecs)

            # The detail page renders at most the latest 100 replies.  Older
            # replies are fetched backwards in batches of 100.
            last_id, left = detail_more(dhtml)
            d_stamps = [r["created_utc"] for r in drecs if r["created_utc"]]
            if last_id and left > 0 and d_stamps and max(d_stamps) >= WINDOW_START:
                guard = 0
                while left > 0 and guard < 2000:
                    bfile = CACHE / f"replies_{card_id}_{last_id}.json"
                    if bfile.exists():
                        bpayload = json.loads(bfile.read_text())
                        reply_cached += 1
                    else:
                        bpayload = f.get(
                            f"{BASE}/v2/comments/view_replies/{card_id}?last_id={last_id}"
                        )
                        bfile.write_text(json.dumps(bpayload))
                        reply_pages += 1
                    brecs, _ = parse_detail(bpayload.get("html") or "", code, card_id)
                    merge(records, brecs)
                    b_stamps = [r["created_utc"] for r in brecs if r["created_utc"]]
                    new_last = bpayload.get("last_id")
                    new_left = int(bpayload.get("replies_left_count") or 0)
                    if not brecs:
                        break
                    if b_stamps and min(b_stamps) < WINDOW_START:
                        break
                    if not new_last or str(new_last) == str(last_id) or new_left <= 0:
                        break
                    last_id, left = str(new_last), new_left
                    guard += 1
                if guard >= 2000:
                    print(f"  ! reply guard hit for comment {card_id}", flush=True)

        pages_done += 1
        print(
            f"  page {page:4d}: {count:2d} cards, {len(page_records):3d} recs, "
            f"{page_min and datetime.fromtimestamp(page_min, MYT):%Y-%m-%d} .. "
            f"{page_max and datetime.fromtimestamp(page_max, MYT):%Y-%m-%d}",
            flush=True,
        )
        page += 1
        if count < 10:
            stop = True
        if page > MAX_PAGES:
            print("  ! page guard hit", flush=True)
            break

    kept = [
        r
        for r in records.values()
        if r["created_utc"] is not None
        and WINDOW_START <= r["created_utc"] <= WINDOW_END
    ]
    kept.sort(key=lambda r: (r["created_utc"], int(r["id"])))
    top_ids = {r["id"] for r in kept if r["depth"] == 0}
    orphans = [r for r in kept if r["depth"] == 1 and r["parent_id"] not in top_ids]
    stats = {
        "pages": pages_done,
        "cards": cards_seen,
        "detail_pages": detail_pages,
        "detail_cached": detail_cached,
        "reply_pages": reply_pages,
        "reply_cached": reply_cached,
        "requests": f.requests,
        "fetched": len(records),
        "kept": len(kept),
        "top_level": len(top_ids),
        "orphans": len(orphans),
        "orphan_parents": len({r["parent_id"] for r in orphans}),
        "min": min((r["created_utc"] for r in kept), default=None),
        "max": max((r["created_utc"] for r in kept), default=None),
    }
    return kept, stats


def write(ticker: str, code: str, recs: list[dict]) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"klse_screener_{ticker}_2016-2024.jsonl"
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing file: {path}")
    post = {
        "record_type": "post",
        "source": "klse_screener",
        "channel": ticker,
        "native_id": code,
        "ticker": ticker,
        "title": f"{ticker} ({code}) comments",
        "author": None,
        "author_id": None,
        "created_utc": WINDOW_START,
        "url": f"{BASE}/v2/comments/all/stock/{code}",
        "body": None,
        "score": None,
        "num_comments": len(recs),
        "lang": None,
        "raw": {
            "stock_code": code,
            "stock_name": STOCKS[ticker]["name"],
            "window_start": "2016-11-02",
            "window_end": "2024-11-01",
        },
    }
    lines = [json.dumps(post, ensure_ascii=False)]
    for r in recs:
        obj = {
            "record_type": "reply",
            "source": "klse_screener",
            "channel": ticker,
            "native_id": r["id"],
            "post_native_id": code,
            "parent_native_id": r["parent_id"],
            "depth": r["depth"],
            "author": r["author"],
            "author_id": r["author_id"],
            "created_utc": r["created_utc"],
            "body": r["body"],
            "score": r["score"],
            "url": f"{BASE}/v2/comment/{r['id']}",
            "lang": None,
            "raw": {
                "comment_id": r["id"],
                "stock_code": code,
                "datetime": r["datetime_text"],
                "likes": r["score"],
            },
        }
        lines.append(json.dumps(obj, ensure_ascii=False))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("tickers", nargs="*", default=list(STOCKS))
    args = ap.parse_args()
    summary = {}
    for ticker in args.tickers:
        ticker = ticker.upper()
        code = STOCKS[ticker]["code"]
        print(f"== {ticker} ({code}) ==", flush=True)
        recs, stats = collect(ticker, code)
        path = write(ticker, code, recs)
        stats["file"] = str(path)
        summary[ticker] = stats
        print(f"  wrote {len(recs)} replies -> {path}", flush=True)
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
