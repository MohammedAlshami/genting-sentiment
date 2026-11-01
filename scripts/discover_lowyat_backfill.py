#!/usr/bin/env python3
"""Enumerate every Lowyat title match for Genting/GENM and probe recent ones.

The IPB search result row's final span.lastaction holds the thread's last-post
age ("2w ago", "1y ago", ...).  Threads whose last post could fall in or after
the 2024-11-02 window are opened at /latest to get the exact last-post date.
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
OUT = Path("/tmp/opencode/backfill")
DATE_FMT = "%b %d %Y, %I:%M %p"
CUTOFF = int(datetime(2024, 9, 1, tzinfo=MYT).timestamp())


class Fetcher:
    def __init__(self) -> None:
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": UA, "Accept-Language": "en-MY,en;q=0.9"})
        self.last = 0.0
        self.requests = 0

    def _pace(self) -> None:
        wait = 1.1 - (time.time() - self.last)
        if wait > 0:
            time.sleep(wait)
        self.last = time.time()
        self.requests += 1

    def get(self, url: str) -> str | None:
        for attempt in range(5):
            self._pace()
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

    def post(self, url: str, data: list[tuple[str, str]]) -> str | None:
        for attempt in range(5):
            self._pace()
            try:
                r = self.s.post(url, data=data, timeout=45, allow_redirects=True)
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


def rel_days(text: str) -> int | None:
    text = re.sub(r"\s+", " ", text or "").strip().lower()
    if "today" in text:
        return 0
    if "yesterday" in text:
        return 1
    m = re.search(r"(\d+)\s*([wdmy])\s*ago", text)
    if m:
        n = int(m.group(1))
        return n * {"d": 1, "w": 7, "m": 30, "y": 365}[m.group(2)]
    return None


def parse_rows(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    out = []
    for tr in soup.select("tr"):
        anchors = [
            a
            for a in tr.select('a[href*="showtopic="], a[href^="/topic/"]')
            if a.get_text(strip=True) not in ("", "Last post by:")
        ]
        if not anchors:
            continue
        a = anchors[0]
        m = re.search(r"(?:showtopic=|/topic/)(\d+)", a.get("href", ""))
        if not m:
            continue
        tid = m.group(1)
        title = H.unescape(a.get_text(" ", strip=True))
        fm = re.search(r"showforum=(\d+)", str(tr))
        spans = tr.select("span.lastaction")
        last_rel = spans[-1].get_text(" ", strip=True) if spans else ""
        out.append(
            {
                "tid": tid,
                "title": title,
                "forum_id": fm.group(1) if fm else None,
                "last_rel": last_rel,
                "last_rel_days": rel_days(last_rel),
            }
        )
    return out


def next_page_url(html: str, current: int) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    best: tuple[int, str] | None = None
    for a in soup.select('a[href*="st="]'):
        href = H.unescape(a.get("href", ""))
        m = re.search(r"[?&]st=(\d+)", href)
        if not m:
            continue
        st = int(m.group(1))
        if st <= current:
            continue
        if best is None or st < best[0]:
            best = (st, href)
    return best[1] if best else None


def parse_latest(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    title_el = soup.find("title")
    title = title_el.get_text(strip=True) if title_el else ""
    pm = re.search(r"Page (\d+) of (\d+)", html)
    last_page = int(pm.group(2)) if pm else 1
    dates = []
    for span in soup.select("span.postdetails"):
        m = re.search(
            r"([A-Z][a-z]{2} \d{1,2} \d{4}, \d{1,2}:\d{2} [AP]M)",
            span.get_text(" ", strip=True),
        )
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
    OUT.mkdir(parents=True, exist_ok=True)
    f = Fetcher()
    if not f.get(BASE + "/"):
        raise SystemExit("cannot reach lowyat")

    keywords = ["genting", "genm", "3182", "4715"]
    forums = ["172", "153", "23", "175"]
    rows: dict[str, dict] = {}
    search_log = {}
    for kw in keywords:
        for forum in forums:
            data = [
                ("keywords", kw),
                ("forums[]", forum),
                ("searchsubs", "1"),
                ("prune", "0"),
                ("prune_type", "newer"),
                ("sort_key", "last_post"),
                ("sort_order", "desc"),
                ("search_in", "titles"),
                ("result_type", "topics"),
            ]
            html = f.post(f"{BASE}/index.php?act=Search&CODE=01", data)
            if not html:
                continue
            total_pages = 1
            page = 0
            while html:
                page += 1
                sm = re.search(r"Page \d+ of (\d+)", html)
                total_pages = int(sm.group(1)) if sm else 1
                page_rows = parse_rows(html)
                for row in page_rows:
                    row["keyword"] = kw
                    row["search_forum"] = forum
                    prev = rows.get(row["tid"])
                    if prev is None or (row["last_rel_days"] is not None and (prev.get("last_rel_days") is None or row["last_rel_days"] < prev["last_rel_days"])):
                        rows[row["tid"]] = row
                print(f"  search {kw} f{forum}: page {page}/{total_pages}, {len(page_rows)} rows", flush=True)
                if page >= total_pages:
                    break
                nxt = next_page_url(html, (page - 1) * 25)
                if not nxt:
                    break
                html = f.get(nxt)
            search_log[f"{kw}/f{forum}"] = {"pages": total_pages}

    print(f"title matches: {len(rows)}", flush=True)
    known = {
        "5515321", "5536525", "5581190", "662423", "5114727", "5498125",
        "5063606", "4952702", "4897753", "5074895", "610474", "3571982", "1110023",
    }
    to_probe = []
    for tid, row in rows.items():
        days = row.get("last_rel_days")
        estimated = None
        if days is not None:
            estimated = int((datetime.now(MYT) - timedelta(days=days)).timestamp())
        if tid in known or (estimated is not None and estimated >= CUTOFF):
            to_probe.append(tid)

    print(f"probing {len(to_probe)} recent/known threads", flush=True)
    probed = []
    for tid in sorted(set(to_probe)):
        row = rows[tid]
        html = f.get(f"{BASE}/topic/{tid}/latest")
        if not html:
            row["probe_error"] = "no latest page"
        else:
            meta = parse_latest(html)
            row.update(
                {
                    "probe_title": meta["title"],
                    "last_page": meta["last_page"],
                    "page_dates": meta["dates"],
                    "last_post_utc": max(meta["dates"]) if meta["dates"] else None,
                }
            )
        probed.append(row)
        last = row.get("last_post_utc")
        print(
            f"  probe {tid}: pages={row.get('last_page')} last="
            + (datetime.fromtimestamp(last, MYT).strftime("%Y-%m-%d") if last else "?"),
            flush=True,
        )

    (OUT / "lowyat_candidates2.json").write_text(
        json.dumps({"search": search_log, "rows": list(rows.values()), "probed": probed}, indent=2)
    )
    print(f"wrote candidates2 requests={f.requests}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
