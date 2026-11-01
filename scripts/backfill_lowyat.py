#!/usr/bin/env python3
"""Backfill Lowyat.NET Genting threads for 2024-11-02 .. 2025-11-01 MYT.

Writes data/raw/lowyat_<TICKER>_2024-2025.jsonl.  Forum threads are flat: the
thread is represented by one synthetic `post` record (anchored at the window
start when the thread predates the window, otherwise at the real opening post),
and every forum post in the window is a `reply` (depth 0).  Pagination is
/topic/<id>/+<offset> with 20 posts per page; we walk backwards from the last
page until a page's oldest post predates the window.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path("/tmp/opencode/lowyat_cache")
OUT = ROOT / "data" / "raw"
BASE = "https://forum.lowyat.net"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
MYT = timezone(timedelta(hours=8))
WINDOW_START = int(datetime(2024, 11, 2, 0, 0, 0, tzinfo=MYT).timestamp())
WINDOW_END = int(datetime(2025, 11, 1, 23, 59, 59, tzinfo=MYT).timestamp())

THREADS = {
    # thread id: (ticker, note)
    "662423": ("GENM", "Genting Malaysia (thread started 2008)"),
    "5114727": ("GENM", "Sime Darby or Genm? (thread started 2021)"),
    "5498125": ("GENM", "Genting, Genm to be dropped from FBM KLCI"),
    "5515321": ("GENM", "Genting Malaysia have 456 tables and 3012 slots"),
    "5536525": ("GENTING", "Genting Group 2026: Global Challenges"),
}

DATE_FMT = "%b %d %Y, %I:%M %p"


class Fetcher:
    def __init__(self) -> None:
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": UA, "Accept-Language": "en-MY,en;q=0.9"})
        self.requests = 0
        self.last = 0.0
        self.s.get(BASE + "/", timeout=30)

    def get(self, url: str) -> str | None:
        for attempt in range(5):
            wait = 1.1 - (time.time() - self.last)
            if wait > 0:
                time.sleep(wait)
            self.last = time.time()
            self.requests += 1
            try:
                r = self.s.get(url, timeout=45)
            except requests.RequestException as exc:
                print(f"  ! {url} {exc}", flush=True)
                time.sleep(5 + attempt * 5)
                continue
            if r.status_code == 429 or 500 <= r.status_code < 600:
                delay = 10 * (attempt + 1)
                print(f"  ! HTTP {r.status_code}; backoff {delay}s", flush=True)
                time.sleep(delay)
                continue
            if r.status_code != 200:
                print(f"  ! HTTP {r.status_code} {url}", flush=True)
                return None
            return r.text
        return None


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


def parse_date(text: str) -> tuple[int | None, str]:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r",\s*updated .*$", "", text)
    m = re.search(r"([A-Z][a-z]{2} \d{1,2} \d{4}, \d{1,2}:\d{2} [AP]M)", text)
    if m:
        raw = m.group(1)
        try:
            dt = datetime.strptime(raw, DATE_FMT).replace(tzinfo=MYT)
            return int(dt.astimezone(timezone.utc).timestamp()), raw
        except ValueError:
            return None, raw
    m = re.search(r"(Today|Yesterday), (\d{1,2}:\d{2} [AP]M)", text)
    if m:
        now = datetime.now(MYT)
        day = now if m.group(1) == "Today" else now - timedelta(days=1)
        raw = m.group(0)
        try:
            dt = datetime.strptime(
                f"{day:%b %d %Y}, {m.group(2)}", DATE_FMT
            ).replace(tzinfo=MYT)
            return int(dt.astimezone(timezone.utc).timestamp()), raw
        except ValueError:
            return None, raw
    return None, text


def parse_posts(html: str, tid: str, page: int, forum: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    out = []
    for table in soup.select("table.post_table[id^='post_']"):
        pid = table.get("id", "").replace("post_", "")
        if not pid.isdigit():
            continue
        author_el = table.select_one("span.normalname a")
        author = author_el.get_text(strip=True) if author_el else None
        if author is None:
            nn = table.select_one("span.normalname")
            if nn:
                author = nn.get_text(" ", strip=True) or None
        author_id = None
        m = re.search(r"MID=(\d+)", str(table))
        if m:
            author_id = m.group(1)
        date_el = None
        for span in table.select("span.postdetails"):
            if parse_date(span.get_text(" ", strip=True))[0] is not None:
                date_el = span
                break
        created, time_text = (None, "")
        if date_el:
            created, time_text = parse_date(date_el.get_text(" ", strip=True))
        body_el = table.select_one("div.postcolor.post_text")
        edits = []
        media = []
        if body_el:
            for ed in body_el.select("span.edit"):
                edits.append(ed.get_text(" ", strip=True))
                ed.extract()
            for img in body_el.select("img"):
                src = img.get("src")
                if src:
                    media.append(src)
        body = clean_text(body_el)
        if not body:
            if media:
                body = "[image]"
            elif body_el and body_el.select("iframe, video, embed, object"):
                body = "[embedded media]"
            else:
                body = "[no text]"
        likes = 0
        rb = table.select_one("div.reactionsBar")
        if rb:
            rtext = rb.get_text(" ", strip=True)
            other = re.search(r"(\d+)\s+others?\s+liked", rtext)
            likes = len(rb.select("a[href^='/user/']"))
            if other:
                likes += int(other.group(1))
        post_number = None
        for a in table.select("a[href^='#']"):
            pm = re.fullmatch(r"#(\d+)", a.get_text(strip=True))
            if pm:
                post_number = int(pm.group(1))
                break
        out.append(
            {
                "id": pid,
                "author": author,
                "author_id": author_id,
                "body": body,
                "created_utc": created,
                "time_text": time_text,
                "score": likes,
                "page": page,
                "forum": forum,
                "edited": "; ".join(edits) if edits else None,
                "media": media,
                "post_number": post_number,
            }
        )
    return out


def page_url(tid: str, page: int) -> str:
    if page <= 1:
        return f"{BASE}/topic/{tid}"
    return f"{BASE}/topic/{tid}/+{(page - 1) * 20}"


def collect(tid: str, fetcher: Fetcher) -> tuple[dict, list[dict], dict]:
    CACHE.mkdir(parents=True, exist_ok=True)
    cache_last = CACHE / f"{tid}_latest.html"
    if cache_last.exists():
        html = cache_last.read_text()
    else:
        html = fetcher.get(f"{BASE}/topic/{tid}/latest")
        if html is None:
            raise RuntimeError(f"cannot load thread {tid}")
        cache_last.write_text(html)

    soup = BeautifulSoup(html, "lxml")
    title_el = soup.find("title")
    title = title_el.get_text(strip=True) if title_el else f"Lowyat thread {tid}"
    pm = re.search(r"Page (\d+) of (\d+)", html)
    last_page = int(pm.group(2)) if pm else 1
    forum_el = soup.select_one("a[href='/StockExchange']")
    forum = "Stock Exchange"
    if forum_el is None:
        for a in soup.select("a[href^='/']"):
            href = a.get("href", "")
            if href in ("/Kopitiam", "/SeriousKopitiam"):
                forum = a.get_text(strip=True) or href.strip("/")
                break
    print(f"  {tid}: {title[:70]!r} pages={last_page} forum={forum}", flush=True)

    all_posts: dict[str, dict] = {}
    pages_fetched = 0
    for page in range(last_page, 0, -1):
        cf = CACHE / f"{tid}_{page}.html"
        if cf.exists():
            phtml = cf.read_text()
        else:
            phtml = html if page == last_page else fetcher.get(page_url(tid, page))
            if phtml is None:
                break
            cf.write_text(phtml)
        posts = parse_posts(phtml, tid, page, forum)
        pages_fetched += 1
        for p in posts:
            all_posts[p["id"]] = p
        stamps = [p["created_utc"] for p in posts if p["created_utc"]]
        page_min = min(stamps) if stamps else None
        print(
            f"    page {page}: {len(posts)} posts, "
            f"min={datetime.fromtimestamp(page_min, MYT):%Y-%m-%d}"
            if page_min
            else f"    page {page}: {len(posts)} posts, no dates",
            flush=True,
        )
        if page == 1 or (page_min is not None and page_min < WINDOW_START):
            break

    # Make sure the opening post is available for thread metadata even when the
    # backward walk stopped on page 2.
    if 1 not in {p["page"] for p in all_posts.values()}:
        cf = CACHE / f"{tid}_1.html"
        if cf.exists():
            phtml = cf.read_text()
        else:
            phtml = fetcher.get(page_url(tid, 1))
            if phtml:
                cf.write_text(phtml)
        if phtml:
            for p in parse_posts(phtml, tid, 1, forum):
                all_posts[p["id"]] = p
            pages_fetched += 1

    kept = [
        p
        for p in all_posts.values()
        if p["created_utc"] and WINDOW_START <= p["created_utc"] <= WINDOW_END
    ]
    kept.sort(key=lambda p: (p["created_utc"], int(p["id"])))

    op = None
    if 1 in {p["page"] for p in all_posts.values()}:
        firsts = [p for p in all_posts.values() if p["page"] == 1]
        firsts.sort(key=lambda p: (p["created_utc"] or 0, int(p["id"])))
        op = firsts[0] if firsts else None
    meta = {
        "tid": tid,
        "title": title,
        "forum": forum,
        "last_page": last_page,
        "pages_fetched": pages_fetched,
        "op": op,
        "kept": len(kept),
    }
    return meta, kept, {"requests": fetcher.requests}


def write(ticker: str, threads: list[tuple[dict, list[dict]]]) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"lowyat_{ticker}_2024-2025.jsonl"
    lines = []
    for meta, posts in threads:
        op = meta["op"] or {}
        started = op.get("created_utc")
        first_num = op.get("post_number")
        # If the real opening post is not rendered (deleted/removed), do not
        # attribute the thread to the author of the first visible reply.
        op_rendered = first_num in (None, 1)
        anchor = started if started and started >= WINDOW_START else WINDOW_START
        post = {
            "record_type": "post",
            "source": "lowyat",
            "channel": meta["forum"],
            "native_id": meta["tid"],
            "ticker": ticker,
            "title": meta["title"],
            "author": op.get("author") if op_rendered else None,
            "author_id": op.get("author_id") if op_rendered else None,
            "created_utc": anchor,
            "url": f"{BASE}/topic/{meta['tid']}",
            "body": None,
            "score": None,
            "num_comments": len(posts),
            "lang": None,
            "raw": {
                "thread_id": meta["tid"],
                "forum": meta["forum"],
                "total_pages": meta["last_page"],
                "op_native_id": op.get("id") if op_rendered else None,
                "op_created_utc": started if op_rendered else None,
                "op_author": op.get("author") if op_rendered else None,
                "thread_started_utc": started if op_rendered else None,
                "thread_started_myt": (
                    datetime.fromtimestamp(started, MYT).strftime("%Y-%m-%d %H:%M:%S")
                    if started and op_rendered
                    else None
                ),
                "op_rendered": op_rendered,
                "first_visible_post_number": first_num,
                "first_visible_post_utc": started,
                "first_visible_author": op.get("author"),
                "started_before_window": (
                    bool(started and started < WINDOW_START) if op_rendered else None
                ),
                "window_start": "2024-11-02",
                "window_end": "2025-11-01",
            },
        }
        lines.append(json.dumps(post, ensure_ascii=False))
        for p in posts:
            obj = {
                "record_type": "reply",
                "source": "lowyat",
                "channel": meta["forum"],
                "native_id": p["id"],
                "post_native_id": meta["tid"],
                "parent_native_id": None,
                "depth": 0,
                "author": p["author"],
                "author_id": p["author_id"],
                "created_utc": p["created_utc"],
                "body": p["body"],
                "score": p["score"],
                "url": f"{BASE}/topic/{meta['tid']}/+{(p['page'] - 1) * 20}#entry{p['id']}",
                "lang": None,
                "raw": {
                    "post_id": p["id"],
                    "thread_id": meta["tid"],
                    "forum": meta["forum"],
                    "time_text": p["time_text"],
                    "page": p["page"],
                    "post_number": p.get("post_number"),
                    "likes": p["score"],
                    "edited": p.get("edited"),
                    "media": p.get("media") or None,
                },
            }
            lines.append(json.dumps(obj, ensure_ascii=False))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("threads", nargs="*", default=list(THREADS))
    args = ap.parse_args()
    fetcher = Fetcher()
    by_ticker: dict[str, list[tuple[dict, list[dict]]]] = {}
    summary = {}
    for tid in args.threads:
        ticker = THREADS[tid][0]
        print(f"== {tid} ({ticker}) ==", flush=True)
        meta, posts, stats = collect(tid, fetcher)
        by_ticker.setdefault(ticker, []).append((meta, posts))
        summary[tid] = {
            "ticker": ticker,
            "title": meta["title"],
            "forum": meta["forum"],
            "pages": meta["pages_fetched"],
            "kept": len(posts),
            "min": min((p["created_utc"] for p in posts), default=None),
            "max": max((p["created_utc"] for p in posts), default=None),
        }
    for ticker, threads in by_ticker.items():
        path = write(ticker, threads)
        print(f"  wrote {sum(len(p) for _, p in threads)} posts -> {path}", flush=True)
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
