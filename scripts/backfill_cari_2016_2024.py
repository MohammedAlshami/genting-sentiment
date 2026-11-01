#!/usr/bin/env python3
"""Backfill Cari (cforum.cari.com.my) Genting threads for 2 Nov 2016 .. 1 Nov 2024.

Writes ``data/raw/cari_2016-2024.jsonl``.

Threads are the company threads in Cari's 股票，期货、外汇 board.  The two long
``交流专区`` threads (GENTING 3182 and GENM 4715) carry most of the discussion;
the shorter 2018-2023 threads are included when they are about the two listed
companies.  Genting Plantation (GENP), Ho Wah Genting, Genting Singapore (G13)
and Genting Hong Kong (S21) threads are excluded because they are different
listed companies.

One ``post`` per thread (title + opening text when the OP falls inside the
window) and one ``reply`` per in-window post.  Cari is a flat forum, so
``parent_native_id`` is null and ``depth`` is 0; replies keep
``post_native_id`` = thread id so they can be joined to the title.
"""

from __future__ import annotations

import argparse
import html as H
import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://cforum.cari.com.my"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
MYT = timezone(timedelta(hours=8))
WINDOW_START = int(datetime(2016, 11, 2, 0, 0, 0, tzinfo=MYT).timestamp())
WINDOW_END = int(datetime(2024, 11, 1, 23, 59, 59, tzinfo=MYT).timestamp())
CACHE = Path("/tmp/opencode/cari_2016_2024_cache")
OUT = ROOT / "data" / "raw" / "cari_2016-2024.jsonl"
SUMMARY = Path("/tmp/opencode/cari_2016_2024_summary.json")

# thread id: (ticker, note)
THREADS: dict[str, tuple[str, str]] = {
    # Long-running company threads.
    "1519333": ("GENTING", "【GENTING 3182 交流专区 2】云顶 (2009-2026)"),
    "1567826": ("GENM", "【GENM 4715 交流专区】云顶马来西亚 (2009-2026)"),
    # Standalone company / market threads.
    "4130715": ("GENTING", "云顶进场良机？(2018)"),
    "4199383": ("GENTING", "大家对云顶怎么看 (2019)"),
    "4272420": ("GENTING", "云顶 2016 年报数字疑问 (2021)"),
    "1157718": ("GENTING", "用十年的时间投资云顶 (2008-2018)"),
    "5039136": ("GENTING", "云顶有机会夺得澳门赌牌？(2022)"),
    "5040008": ("GENTING", "联号公司阿兹海默新药进展，云顶交投活跃 (2022)"),
    "5041061": ("GENTING", "大马股市周记：金务大、云顶、银丰、STRAITS (2022)"),
    "5046803": ("GENTING", "云顶、云顶大马 Q3 转亏为盈 (2022)"),
    "5035098": ("GENTING", "云顶和云顶大马 Q2 亏损猛减九成 (2022)"),
    "5057610": ("GENTING", "云顶 Q4 净亏 1.6871 亿令吉，派息 9 仙 (2023)"),
    "5057707": ("GENTING", "云顶和云顶大马派息每股 9 仙 (2023)"),
    # GENM-specific news (Macau licence, privatisation era).
    "5047608": ("GENM", "云顶大马抢不到澳门赌牌反是好事？(2022)"),
    "5047620": ("GENM", "云顶大马抢不到澳门赌牌反是好事？(2022, duplicate post)"),
    "5047416": ("GENM", "云顶大马公告：竞标澳门赌牌失败 (2022)"),
    "5046955": ("GENM", "现有 6 博企获澳门新赌牌，大马云顶出局 (2022)"),
}

DATE_RE = re.compile(r"发表于\s*(\d{1,2}-\d{1,2}-\d{4}\s+\d{1,2}:\d{2}\s*[AP]M)")


class Fetcher:
    def __init__(self) -> None:
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"})
        self.last = 0.0
        self.requests = 0

    def get(self, url: str) -> str | None:
        for attempt in range(6):
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
    for q in node.select("blockquote, div.quote, div.quote-block"):
        q.decompose()
    text = node.get_text("\n")
    text = H.unescape(text).replace("\xa0", " ").replace("\u200b", "")
    text = text.strip()
    text = re.sub(r"^本帖最后由 .*?编辑\s*", "", text)
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


def page_url(tid: str, page: int) -> str:
    return f"{BASE}/forum.php?mod=viewthread&tid={tid}&page={page}"


def collect(tid: str, f: Fetcher) -> tuple[str, int, list[dict], int]:
    CACHE.mkdir(parents=True, exist_ok=True)
    first_file = CACHE / f"{tid}_1.html"
    if first_file.exists():
        first = first_file.read_text(encoding="utf-8")
    else:
        first = f.get(page_url(tid, 1))
        if first:
            first_file.write_text(first, encoding="utf-8")
    if not first:
        raise RuntimeError(f"cannot load thread {tid}")

    soup = BeautifulSoup(first, "lxml")
    title = soup.title.get_text(strip=True).split(" - ")[0] if soup.title else f"Cari thread {tid}"
    pages = total_pages(first)
    all_posts: dict[str, dict] = {}
    pages_fetched = 0

    page = pages
    while page >= 1:
        cf = CACHE / f"{tid}_{page}.html"
        if page == 1:
            html = first
        elif cf.exists():
            html = cf.read_text(encoding="utf-8")
        else:
            html = f.get(page_url(tid, page))
            if not html:
                break
            cf.write_text(html, encoding="utf-8")
        posts = parse_posts(html, tid, page)
        pages_fetched += 1
        for p in posts:
            all_posts[p["id"]] = p
        stamps = [p["created_utc"] for p in posts if p["created_utc"]]
        page_min = min(stamps) if stamps else None
        page_max = max(stamps) if stamps else None
        print(
            f"    page {page}/{pages}: {len(posts)} posts, "
            + (
                f"{datetime.fromtimestamp(page_min, MYT):%Y-%m-%d}.."
                f"{datetime.fromtimestamp(page_max, MYT):%Y-%m-%d}"
                if page_min and page_max
                else "no dates"
            ),
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
    return title, pages, kept, pages_fetched


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("threads", nargs="*", default=list(THREADS))
    args = ap.parse_args()
    if OUT.exists():
        raise SystemExit(f"refusing to overwrite existing {OUT}")
    f = Fetcher()
    records: list[dict] = []
    summary: dict[str, dict] = {}
    seen: set[str] = set()
    for tid in args.threads:
        ticker, note = THREADS[tid]
        print(f"== {tid} {ticker} {note} ==", flush=True)
        title, pages, posts, pages_fetched = collect(tid, f)
        if not posts:
            print("  skip: no in-window posts", flush=True)
            summary[tid] = {"ticker": ticker, "title": title, "pages": pages, "kept": 0}
            continue
        # Opening post = earliest post rendered on page 1.  It is used for
        # thread metadata/body; it is not duplicated as a reply when it falls
        # inside the window.
        first_html = (CACHE / f"{tid}_1.html").read_text(encoding="utf-8")
        first_posts = [p for p in parse_posts(first_html, tid, 1) if p["created_utc"]]
        op = min(first_posts, key=lambda p: (p["created_utc"], int(p["id"]))) if first_posts else None
        op_ts = op["created_utc"] if op else None
        if op_ts and op_ts > WINDOW_END:
            print("  skip: OP after window", flush=True)
            summary[tid] = {"ticker": ticker, "title": title, "pages": pages, "kept": 0}
            continue
        op_in_window = bool(op_ts and WINDOW_START <= op_ts <= WINDOW_END)
        anchor = op_ts if op_in_window else WINDOW_START
        replies = [p for p in posts if not (op and p["id"] == op["id"])]
        if tid in seen:
            continue
        seen.add(tid)
        records.append(
            {
                "record_type": "post",
                "source": "cari",
                "channel": "股票，期货、外汇",
                "native_id": tid,
                "ticker": ticker,
                "title": title or note,
                "author": op.get("author") if op else None,
                "author_id": op.get("author_id") if op else None,
                "created_utc": anchor,
                "url": f"{BASE}/forum.php?mod=viewthread&tid={tid}",
                "body": op.get("body") if op_in_window else None,
                "score": None,
                "num_comments": len(replies),
                "lang": "zh",
                "raw": {
                    "thread_id": tid,
                    "forum": "股票，期货、外汇",
                    "pages": pages,
                    "pages_fetched": pages_fetched,
                    "op_native_id": op.get("id") if op else None,
                    "op_created_utc": op_ts,
                    "op_floor": op.get("floor") if op else None,
                    "op_in_window": op_in_window,
                    "op_body": op.get("body") if op else None,
                    "window_start": "2016-11-02",
                    "window_end": "2024-11-01",
                    "title_full": title,
                },
            }
        )
        for p in replies:
            if p["id"] in seen:
                continue
            seen.add(p["id"])
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
                        "thread_title": title,
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
            "pages_fetched": pages_fetched,
            "op_created_utc": op_ts,
            "replies": len(replies),
            "min": min((p["created_utc"] for p in replies), default=None),
            "max": max((p["created_utc"] for p in replies), default=None),
        }
        print(f"  kept {len(replies)} replies", flush=True)

    records.sort(key=lambda r: (r["created_utc"], r["record_type"], str(r["native_id"])))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(
        json.dumps({"window": [WINDOW_START, WINDOW_END], "requests": f.requests, "threads": summary},
                   indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"wrote {len(records)} records to {OUT}", flush=True)
    print(json.dumps(summary, ensure_ascii=False, indent=1, default=str), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
