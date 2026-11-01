#!/usr/bin/env python3
"""Discover Lowyat.NET threads with Genting in the title, active 2024-11..2026-11.

Search results are ordered by last post, but show only relative times ("2w
ago"). We paginate until a whole page is clearly older than the window, then
probe each title match at /topic/<id>/latest for exact dates and page count.
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

BASE = "https://forum.lowyat.net"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
MYT = timezone(timedelta(hours=8))
WINDOW_START = datetime(2024, 11, 2, tzinfo=MYT)
OUT = Path("/tmp/opencode/lowyat_extra_candidates.json")
DATE_FMT = "%b %d %Y, %I:%M %p"
KEYWORDS = ["genting", "genm", "3182", "4715"]
FORUMS = {
    "172": "Stock Exchange",
    "153": "Finance / Business",
    "23": "Kopitiam",
    "175": "Serious Kopitiam",
}
TITLE_RE = re.compile(r"\b(genting|genm|3182|4715)\b", re.I)


class Fetcher:
    def __init__(self) -> None:
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": UA, "Accept-Language": "en-MY,en;q=0.9"})
        self.last = 0.0
        self.requests = 0
        self.s.get(BASE + "/", timeout=30)

    def _pace(self) -> None:
        wait = 1.1 - (time.time() - self.last)
        if wait > 0:
            time.sleep(wait)
        self.last = time.time()
        self.requests += 1

    def post(self, url: str, data: list[tuple[str, str]]) -> str | None:
        for attempt in range(5):
            self._pace()
            try:
                r = self.s.post(url, data=data, timeout=45)
            except requests.RequestException as exc:
                print(f"  ! POST {url} {exc}", flush=True)
                time.sleep(5 + attempt * 5)
                continue
            if r.status_code == 429 or 500 <= r.status_code < 600:
                time.sleep(10 * (attempt + 1))
                continue
            if r.status_code != 200:
                print(f"  ! HTTP {r.status_code} POST {url}", flush=True)
                return None
            return r.text
        return None

    def get(self, url: str) -> str | None:
        for attempt in range(5):
            self._pace()
            try:
                r = self.s.get(url, timeout=45)
            except requests.RequestException as exc:
                print(f"  ! GET {url} {exc}", flush=True)
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


def relative_age(text: str) -> float | None:
    """Return approximate age in days from '2w ago', '14y ago' etc."""
    m = re.search(r"(\d+)\s*(y|mo|w|d|h|m)\s*ago", text, re.I)
    if not m:
        return None
    n = int(m.group(1))
    unit = m.group(2).lower()
    return {
        "y": 365.0,
        "mo": 30.0,
        "w": 7.0,
        "d": 1.0,
        "h": 1 / 24,
        "m": 1 / 1440,
    }[unit] * n


def parse_search(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    out: dict[str, dict] = {}
    for tr in soup.select("tr"):
        anchors = [
            a
            for a in tr.select('a[href*="showtopic="], a[href^="/topic/"]')
            if a.get_text(strip=True) and "Last post by" not in a.get_text()
        ]
        if not anchors:
            continue
        a = anchors[0]
        m = re.search(r"(?:showtopic=|/topic/)(\d+)", a.get("href", ""))
        if not m:
            continue
        tid = m.group(1)
        title = H.unescape(a.get_text(" ", strip=True))
        forum_el = tr.select_one("span.forumdesc a")
        forum = forum_el.get_text(strip=True) if forum_el else None
        row_text = tr.get_text(" | ", strip=True)
        age = relative_age(row_text)
        if tid not in out:
            out[tid] = {"tid": tid, "title": title, "forum": forum, "age_days": age}
        else:
            if age is not None and (out[tid]["age_days"] is None or age < out[tid]["age_days"]):
                out[tid]["age_days"] = age
    return list(out.values())


def parse_latest(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    title_el = soup.find("title")
    title = title_el.get_text(strip=True) if title_el else ""
    pm = re.search(r"Page (\d+) of (\d+)", html)
    last_page = int(pm.group(2)) if pm else 1
    dates = []
    for span in soup.select("span.postdetails"):
        m = re.search(r"([A-Z][a-z]{2} \d{1,2} \d{4}, \d{1,2}:\d{2} [AP]M)", span.get_text(" ", strip=True))
        if m:
            try:
                dates.append(
                    int(
                        datetime.strptime(m.group(1), DATE_FMT)
                        .replace(tzinfo=MYT)
                        .astimezone(timezone.utc)
                        .timestamp()
                    )
                )
            except ValueError:
                pass
    return {"title": title, "last_page": last_page, "dates": dates}


def main() -> int:
    f = Fetcher()
    candidates: dict[str, dict] = {}
    log = {}
    for kw in KEYWORDS:
        for fid, forum_name in FORUMS.items():
            print(f"== search {kw!r} in {forum_name} ({fid}) ==", flush=True)
            data = [
                ("keywords", kw),
                ("searchsubs", "1"),
                ("prune", "0"),
                ("prune_type", "newer"),
                ("sort_key", "last_post"),
                ("sort_order", "desc"),
                ("search_in", "titles"),
                ("result_type", "topics"),
                ("forums[]", fid),
            ]
            html = f.post(f"{BASE}/index.php?act=Search&CODE=01", data)
            pages = 0
            kept_rows = 0
            while html:
                pages += 1
                rows = parse_search(html)
                page_min_age = max((r["age_days"] for r in rows if r["age_days"] is not None), default=None)
                fresh = 0
                for row in rows:
                    if not TITLE_RE.search(row["title"]):
                        continue
                    kept_rows += 1
                    row["keyword"] = kw
                    row["search_forum"] = forum_name
                    if row["tid"] not in candidates:
                        candidates[row["tid"]] = row
                        fresh += 1
                print(
                    f"  page {pages}: {len(rows)} rows, {fresh} new title matches, "
                    f"oldest~{page_min_age:.0f}d" if page_min_age is not None else f"  page {pages}: {len(rows)} rows",
                    flush=True,
                )
                sm = re.search(r"Page \d+ of (\d+)", html)
                total_pages = int(sm.group(1)) if sm else 1
                # All rows on this page are older than 3 years -> stop.
                if page_min_age is not None and page_min_age > 3 * 365:
                    break
                if pages >= total_pages:
                    break
                nxt = None
                soup = BeautifulSoup(html, "lxml")
                for a in soup.select('a[href*="act=Search"]'):
                    href = a.get("href", "")
                    if "st=" in href and a.get_text(strip=True) in ("›", "»", "Next"):
                        nxt = H.unescape(href)
                        break
                if not nxt:
                    # numeric next page link fallback
                    want = str(pages + 1)
                    for a in soup.select('a[href*="act=Search"]'):
                        if a.get_text(strip=True) == want:
                            nxt = H.unescape(a.get("href", ""))
                            break
                if not nxt:
                    break
                html = f.get(nxt)
            log[f"{kw}/{fid}"] = {"pages": pages, "matches": kept_rows}

    print(f"\ncandidates with Genting in title: {len(candidates)}", flush=True)
    probed = []
    for tid, row in sorted(candidates.items(), key=lambda kv: kv[1]["age_days"] or 9e9):
        html = f.get(f"{BASE}/topic/{tid}/latest")
        if not html:
            row["probe_error"] = "no latest page"
            probed.append(row)
            continue
        meta = parse_latest(html)
        row.update(
            {
                "probe_title": meta["title"],
                "last_page": meta["last_page"],
                "last_post_utc": max(meta["dates"]) if meta["dates"] else None,
            }
        )
        probed.append(row)
        last = row["last_post_utc"]
        print(
            f"  probe {tid}: pages={meta['last_page']} last="
            + (datetime.fromtimestamp(last, MYT).strftime("%Y-%m-%d") if last else "?"),
            flush=True,
        )

    result = {
        "search": log,
        "requests": f.requests,
        "candidates": probed,
        "in_window": [
            r
            for r in probed
            if (r.get("last_post_utc") or 0) >= int(WINDOW_START.timestamp())
        ],
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1))
    print(f"wrote {OUT}; in-window threads={len(result['in_window'])} requests={f.requests}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
