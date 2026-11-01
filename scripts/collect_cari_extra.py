#!/usr/bin/env python3
"""Collect Genting threads from Cari's 股票，期货、外汇 forum (cforum.cari.com.my).

Cari is a large Malaysian Chinese forum. Its stock sub-forum has two long
running company threads (GENTING 3182 and GENM 4715) plus a 2026 rights-issue
thread. Pages are chronological; we walk backwards from the last page until a
page's oldest post predates the window, and keep only in-window posts.
"""

from __future__ import annotations

import html as H
import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = "https://cforum.cari.com.my"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
MYT = timezone(timedelta(hours=8))
WINDOW_START = int(datetime(2024, 11, 2, 0, 0, 0, tzinfo=MYT).timestamp())
WINDOW_END = int(datetime(2026, 11, 2, 23, 59, 59, tzinfo=MYT).timestamp())
CACHE = Path("/tmp/opencode/cari_cache")
OUT = Path("/tmp/opencode/cari_records.json")

THREADS = {
    "1519333": ("GENTING", "【GENTING 3182 交流专区 2】云顶"),
    "1567826": ("GENM", "【GENM 4715 交流专区】云顶马来西亚"),
    "5156218": ("GENM", "云顶大马（GENM,4715,主板消费产品服务组）"),
    "5178457": ("GENTING", "云顶跟股东拿 12.5 亿 Right Issue，你们的决定是什么？"),
}
DATE_RE = re.compile(r"发表于\s*(\d{1,2}-\d{1,2}-\d{4}\s+\d{1,2}:\d{2}\s*[AP]M)")


class Fetcher:
    def __init__(self) -> None:
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"})
        self.last = 0.0
        self.requests = 0

    def get(self, url: str) -> str | None:
        for attempt in range(5):
            wait = 1.2 - (time.time() - self.last)
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
                time.sleep(10 * (attempt + 1))
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
    # Drop quoted replies so the body is the author's own text.
    for q in node.select("blockquote, div.quote, div.quote-block"):
        q.decompose()
    text = node.get_text("\n")
    text = H.unescape(text).replace("\xa0", " ").replace("\u200b", "")
    text = text.strip()
    # Edit notice at the top (Discuz adds it when a post is modified).
    text = re.sub(r"^本帖最后由 .*?编辑\s*", "", text)
    # Discuz attachment boilerplate, not part of the post text.
    kept = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("fakename."):
            continue
        if "下载次数" in s and "KB" in s:
            continue
        if s in {"下载附件", "保存到相册"}:
            continue
        if re.fullmatch(r"\d{1,2}-\d{1,2}-\d{4}\s+\d{1,2}:\d{2}\s*[AP]M\s*上传", s):
            continue
        kept.append(s)
    text = "\n".join(kept)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_posts(html: str, tid: str, page: int) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    out = []
    for div in soup.select("div[id^='post_']"):
        m = re.fullmatch(r"post_(\d+)", div.get("id", ""))
        if not m:
            continue
        pid = m.group(1)
        date_el = div.select_one("em[id^='authorposton']")
        created = None
        time_text = None
        if date_el:
            time_text = date_el.get_text(" ", strip=True)
            dm = DATE_RE.search(time_text)
            if dm:
                try:
                    created = int(
                        datetime.strptime(dm.group(1), "%d-%m-%Y %I:%M %p")
                        .replace(tzinfo=MYT)
                        .astimezone(timezone.utc)
                        .timestamp()
                    )
                except ValueError:
                    created = None
        author = None
        author_id = None
        authi = div.select_one(".authi")
        if authi:
            a = authi.select_one('a[href*="uid="]')
            if a:
                author = a.get_text(strip=True) or None
                am = re.search(r"uid=(\d+)", a.get("href", ""))
                if am:
                    author_id = am.group(1)
            else:
                author = authi.get_text(" ", strip=True).split()[0] if authi.get_text(strip=True) else None
        body_el = div.select_one("td.t_f")
        body = clean_text(body_el)
        if not body:
            body = "[deleted]"
        # floor number from the post header
        floor = None
        for a in div.select("a[href*='pid=']"):
            t = a.get_text(strip=True)
            if t.isdigit():
                floor = int(t)
                break
        out.append(
            {
                "id": pid,
                "created_utc": created,
                "time_text": time_text,
                "author": author,
                "author_id": author_id,
                "body": body,
                "floor": floor,
                "page": page,
                "tid": tid,
            }
        )
    return out


def total_pages(html: str) -> int:
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(" ", strip=True)
    m = re.search(r"(\d+)\s*/\s*(\d+)\s*页", text)
    return int(m.group(2)) if m else 1


def collect(tid: str, f: Fetcher) -> tuple[str, str, list[dict], int]:
    CACHE.mkdir(parents=True, exist_ok=True)
    first_file = CACHE / f"{tid}_1.html"
    if first_file.exists():
        first = first_file.read_text()
    else:
        first = f.get(f"{BASE}/forum.php?mod=viewthread&tid={tid}")
        if first:
            first_file.write_text(first)
    if not first:
        raise RuntimeError(f"cannot load thread {tid}")
    soup = BeautifulSoup(first, "lxml")
    title = soup.title.get_text(strip=True).split(" - ")[0] if soup.title else f"Cari thread {tid}"
    pages = total_pages(first)
    all_posts: dict[str, dict] = {}
    page = pages
    while page >= 1:
        cf = CACHE / f"{tid}_{page}.html"
        if page == 1:
            html = first
        elif cf.exists():
            html = cf.read_text()
        else:
            html = f.get(f"{BASE}/forum.php?mod=viewthread&tid={tid}&page={page}")
            if not html:
                break
            cf.write_text(html)
        posts = parse_posts(html, tid, page)
        for p in posts:
            all_posts[p["id"]] = p
        stamps = [p["created_utc"] for p in posts if p["created_utc"]]
        page_min = min(stamps) if stamps else None
        print(
            f"    page {page}/{pages}: {len(posts)} posts, "
            + (datetime.fromtimestamp(page_min, MYT).strftime("%Y-%m-%d") if page_min else "no dates"),
            flush=True,
        )
        if page == 1:
            break
        if page_min is not None and page_min < WINDOW_START:
            break
        page -= 1
    kept = [
        p
        for p in all_posts.values()
        if p["created_utc"] is not None and WINDOW_START <= p["created_utc"] <= WINDOW_END
    ]
    kept.sort(key=lambda p: (p["created_utc"], int(p["id"])))
    return title, pages, kept, f.requests


def main() -> None:
    f = Fetcher()
    records = []
    summary = {}
    seen: set[tuple[str, str]] = set()
    for tid, (ticker, note) in THREADS.items():
        print(f"== {tid} {ticker} {note} ==", flush=True)
        title, pages, posts, reqs = collect(tid, f)
        op = posts[0] if posts else None
        # Opening post is fetched from page 1 separately if needed.
        first_html = (CACHE / f"{tid}_1.html").read_text() if (CACHE / f"{tid}_1.html").exists() else None
        op_rec = None
        if first_html:
            first_posts = [p for p in parse_posts(first_html, tid, 1) if p["created_utc"]]
            if first_posts:
                op_rec = min(first_posts, key=lambda p: p["created_utc"])
        if op_rec and op_rec["created_utc"] < WINDOW_START:
            anchor = WINDOW_START
            post_body = None
        elif op_rec:
            anchor = op_rec["created_utc"]
            post_body = op_rec.get("body")
        else:
            anchor = WINDOW_START
            post_body = None
        if ("cari", tid) not in seen:
            seen.add(("cari", tid))
            records.append(
                {
                    "record_type": "post",
                    "source": "cari",
                    "channel": "股票，期货、外汇",
                    "native_id": tid,
                    "ticker": ticker,
                    "title": title or note,
                    "author": op_rec.get("author") if op_rec else None,
                    "author_id": op_rec.get("author_id") if op_rec else None,
                    "created_utc": anchor,
                    "url": f"{BASE}/forum.php?mod=viewthread&tid={tid}",
                    "body": post_body,
                    "score": None,
                    "num_comments": len(posts),
                    "lang": "zh",
                    "raw": {
                        "thread_id": tid,
                        "forum": "股票，期货、外汇",
                        "pages": pages,
                        "op_created_utc": op_rec.get("created_utc") if op_rec else None,
                        "op_body": op_rec.get("body") if op_rec else None,
                        "window_start": "2024-11-02",
                        "window_end": "2026-11-02",
                        "title_full": title,
                    },
                }
            )
        for p in posts:
            if ("cari", p["id"]) in seen:
                continue
            seen.add(("cari", p["id"]))
            records.append(
                {
                    "record_type": "reply",
                    "source": "cari",
                    "channel": "股票，期货、外汇",
                    "native_id": p["id"],
                    "post_native_id": tid,
                    "parent_native_id": None,
                    "depth": 0,
                    "author": p["author"],
                    "author_id": p["author_id"],
                    "created_utc": p["created_utc"],
                    "body": p["body"],
                    "score": None,
                    "url": f"{BASE}/forum.php?mod=redirect&goto=findpost&ptid={tid}&pid={p['id']}",
                    "lang": "zh",
                    "raw": {
                        "post_id": p["id"],
                        "thread_id": tid,
                        "page": p["page"],
                        "floor": p["floor"],
                        "time_text": p["time_text"],
                    },
                }
            )
        summary[tid] = {
            "ticker": ticker,
            "title": title,
            "pages": pages,
            "kept": len(posts),
            "requests": reqs,
            "min": min((p["created_utc"] for p in posts), default=None),
            "max": max((p["created_utc"] for p in posts), default=None),
        }
    OUT.write_text(json.dumps({"records": records, "summary": summary}, ensure_ascii=False))
    print(f"wrote {len(records)} records to {OUT}", flush=True)
    print(json.dumps(summary, ensure_ascii=False, indent=1, default=str), flush=True)


if __name__ == "__main__":
    main()
