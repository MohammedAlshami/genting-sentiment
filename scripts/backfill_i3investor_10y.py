#!/usr/bin/env python3
"""Backfill i3investor forum threads for GENTING (3182) and GENM (4715).

Covers the eight-year window 2 Nov 2016 00:00 MYT -> 1 Nov 2024 23:59:59 MYT.
The existing 2024-2026 files are left untouched and are never overwritten by
this script.

Timestamp handling is identical to scripts/collect_i3investor.py: absolute
YYYY-MM-DD HH:MM page timestamps are used where shown, exact comservlet
DD/MM/YYYY h:mm AM/PM timestamps fill in the recent tail, and any remaining
relative labels are estimated from the global comment-id sequence and clamped
to the label's age bucket (flagged raw.time_confidence="relative").

Usage:
    python3 scripts/backfill_i3investor_10y.py --stock both
    python3 scripts/backfill_i3investor_10y.py --stock GENTING --start-page 400 --end-page 401
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
import random
import re
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup
from curl_cffi import requests

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "raw"
CACHE_DIR = Path("/tmp/opencode/genting_i3_cache")
BASE = "https://klse.i3investor.com"
TZ = ZoneInfo("Asia/Kuala_Lumpur")

WINDOW_START = datetime(2016, 11, 2, 0, 0, tzinfo=TZ)
WINDOW_START_TS = int(WINDOW_START.timestamp())
WINDOW_END = datetime(2024, 11, 1, 23, 59, 59, tzinfo=TZ)
WINDOW_END_TS = int(WINDOW_END.timestamp())
OUT_SUFFIX = "2016-2024"

STOCKS = {
    "GENTING": {
        "ticker": "GENTING",
        "channel": "GENTING",
        "code": "3182",
        "pid": "800000520",
        "title": "Stock: [GENTING]: GENTING BHD",
    },
    "GENM": {
        "ticker": "GENM",
        "channel": "GENM",
        "code": "4715",
        "pid": "800000712",
        "title": "Stock: [GENM]: GENTING MALAYSIA BERHAD",
    },
}

ABS_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")
REL_RE = re.compile(r"^(\d+)\s+(minute|hour|day|week|month)s?\s+ago$", re.I)
DMY_RE = re.compile(r"^\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2} [AP]M$", re.I)


# --------------------------------------------------------------------------- #
# HTTP client
# --------------------------------------------------------------------------- #


class Client:
    def __init__(
        self,
        min_interval: float = 1.15,
        refresh: bool = False,
        proxy_mode: str = "auto",
        refetch_proxy: bool = False,
    ):
        self.min_interval = min_interval
        self.refresh = refresh
        self.proxy_mode = proxy_mode
        self.refetch_proxy = refetch_proxy
        self.session = requests.Session(impersonate="chrome")
        self.last_request = 0.0
        self.last_proxy_request = 0.0
        self.proxy_min_interval = max(1.5, min_interval)
        self.requests_made = 0
        self.retries = 0
        self.cache_hits = 0
        self.proxy_requests = 0
        self.direct_blocked_until = 0.0
        self.direct_fails = 0
        self.last_proxy_name = None
        self.last_detected_lang = None
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _proxy_get(self, url: str) -> str:
        """Fetch through a server-side proxy when Cloudflare blocks us.

        Two Google Translate front ends are tried.  They return the original
        server-rendered HTML with comment bodies intact (the translation is
        applied client-side), plus a detected-language marker we record for
        provenance.  allorigins returns the original HTML without translation.
        """
        from urllib.parse import quote, urlsplit

        parts = urlsplit(url)
        gt_host = parts.netloc.replace(".", "-") + ".translate.goog"
        gt_query = parts.query + ("&" if parts.query else "") + "_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en"
        gt_url = f"https://{gt_host}{parts.path}?{gt_query}"
        allorigins_url = "https://api.allorigins.win/raw?url=" + quote(url, safe="")
        web_hosts = [
            "translate.google.com",
            "translate.google.co.uk",
            "translate.google.com.my",
            "translate.google.com.sg",
            "translate.google.com.au",
            "translate.google.co.nz",
            "translate.google.co.in",
            "translate.google.com.ph",
            "translate.google.co.th",
            "translate.google.com.hk",
            "translate.google.com.tw",
            "translate.google.co.jp",
            "translate.google.de",
            "translate.google.fr",
            "translate.google.ca",
        ]

        google_candidates = [("google_translate", gt_url)]
        for host in web_hosts:
            google_candidates.append(
                (
                    "google_web:" + host,
                    f"https://{host}/translate?sl=auto&tl=en&u=" + quote(url, safe=""),
                )
            )
        candidates = google_candidates + [("allorigins", allorigins_url)]
        if self.proxy_mode == "google":
            candidates = google_candidates
        elif self.proxy_mode == "allorigins":
            candidates = [("allorigins", allorigins_url)]

        last_error = None
        for attempt in range(20):
            # Rotate the starting candidate so a 429 on one Google front end
            # does not always penalise the same request order.
            order = candidates[attempt % len(candidates):] + candidates[:attempt % len(candidates)]
            for name, proxy_url in order:
                wait = self.proxy_min_interval - (time.monotonic() - self.last_proxy_request)
                if wait > 0:
                    time.sleep(wait)
                try:
                    r = requests.Session(impersonate="chrome").get(proxy_url, timeout=120)
                    self.last_proxy_request = time.monotonic()
                    self.proxy_requests += 1
                    self.requests_made += 1
                    if r.status_code == 200 and len(r.text) > 5000 and "data-commentid" in r.text:
                        lang = None
                        m = re.search(r'data-detected-source-language="([^"]*)"', r.text)
                        if m:
                            lang = m.group(1)
                        self.last_proxy_name = name
                        self.last_detected_lang = lang
                        return r.text
                    print(f"    proxy[{name}] HTTP {r.status_code} len={len(r.text)}", file=sys.stderr)
                    last_error = f"HTTP {r.status_code}"
                except Exception as exc:  # noqa: BLE001
                    print(f"    proxy[{name}] {type(exc).__name__}: {exc}", file=sys.stderr)
                    last_error = f"{type(exc).__name__}: {exc}"
                time.sleep(1.5)
            delay = min(30, 2.0 * (attempt + 1)) + random.uniform(0, 2.0)
            self.retries += 1
            print(f"    proxy retry {attempt + 1} in {delay:.1f}s ({last_error})", file=sys.stderr)
            time.sleep(delay)
        raise RuntimeError(f"proxy failed after retries: {url} ({last_error})")

    def _cache_paths(self, key: str) -> tuple[Path, Path]:
        h = hashlib.sha256(key.encode()).hexdigest()[:24]
        return CACHE_DIR / f"{h}.html", CACHE_DIR / f"{h}.json"

    def _wait(self) -> None:
        wait = self.min_interval - (time.monotonic() - self.last_request)
        if wait > 0:
            time.sleep(wait)

    def _sleep_backoff(self, attempt: int) -> None:
        delay = min(60, 2.0 ** attempt) + random.uniform(0, 0.75)
        self.retries += 1
        print(f"    retry in {delay:.1f}s", file=sys.stderr)
        time.sleep(delay)

    def _post_direct(self, url: str, **kwargs):
        for attempt in range(7):
            self._wait()
            try:
                r = self.session.post(url, timeout=60, **kwargs)
                self.last_request = time.monotonic()
                self.requests_made += 1
                if r.status_code == 200:
                    return r
                if r.status_code in (403, 429, 500, 502, 503, 504):
                    print(f"    HTTP {r.status_code} for {url}", file=sys.stderr)
                    if r.status_code == 403:
                        self.session = requests.Session(impersonate="chrome")
                    self._sleep_backoff(attempt)
                    continue
                r.raise_for_status()
            except Exception as exc:  # noqa: BLE001
                self.last_request = time.monotonic()
                print(f"    {type(exc).__name__}: {exc}", file=sys.stderr)
                self._sleep_backoff(attempt)
        raise RuntimeError(f"failed after retries: POST {url}")

    def _do(self, method: str, url: str, **kwargs):
        if method != "GET":
            return self._post_direct(url, **kwargs), None

        if self.proxy_mode == "direct":
            for attempt in range(7):
                self._wait()
                try:
                    r = self.session.get(url, timeout=60, **kwargs)
                    self.last_request = time.monotonic()
                    self.requests_made += 1
                    if r.status_code == 200:
                        return r, None
                    if r.status_code in (403, 429, 500, 502, 503, 504):
                        print(f"    HTTP {r.status_code} for {url}", file=sys.stderr)
                        self._sleep_backoff(attempt)
                        continue
                    r.raise_for_status()
                except Exception as exc:  # noqa: BLE001
                    self.last_request = time.monotonic()
                    print(f"    {type(exc).__name__}: {exc}", file=sys.stderr)
                    self._sleep_backoff(attempt)
            raise RuntimeError(f"failed after retries: GET {url}")

        deadline = time.monotonic() + 2400.0
        attempt = 0
        while time.monotonic() < deadline:
            now = time.monotonic()
            if self.proxy_mode in ("google", "allorigins") or now < self.direct_blocked_until:
                try:
                    return None, self._proxy_get(url)
                except Exception as exc:  # noqa: BLE001
                    print(f"    proxy fallback failed: {exc}", file=sys.stderr)
                    if self.proxy_mode in ("google", "allorigins"):
                        self._sleep_backoff(attempt)
                        attempt += 1
                        continue
                    wait = min(60.0, max(0.0, self.direct_blocked_until - time.monotonic()))
                    if wait > 0:
                        time.sleep(wait)
                    continue

            # Direct attempt.  A 403 starts a cooldown; while it lasts every
            # page goes through the proxy, then direct is probed again.
            self._wait()
            try:
                r = self.session.get(url, timeout=60, **kwargs)
                self.last_request = time.monotonic()
                self.requests_made += 1
                if r.status_code == 200:
                    self.direct_fails = 0
                    return r, None
                if r.status_code == 403:
                    self.direct_fails += 1
                    cooldown = min(1800.0, 300.0 * (2 ** (self.direct_fails - 1)))
                    self.direct_blocked_until = time.monotonic() + cooldown
                    self.session = requests.Session(impersonate="chrome")
                    print(
                        f"    HTTP 403 for {url}; {cooldown:.0f}s proxy cooldown",
                        file=sys.stderr,
                    )
                    try:
                        return None, self._proxy_get(url)
                    except Exception as exc:  # noqa: BLE001
                        print(f"    proxy fallback failed: {exc}", file=sys.stderr)
                    continue
                if r.status_code == 429:
                    # Cloudflare's soft rate limit: pause direct access and use
                    # a proxy for the next pages, then probe direct again.
                    self.direct_blocked_until = time.monotonic() + 120.0
                    print(f"    HTTP 429 for {url}; 120s proxy cooldown", file=sys.stderr)
                    try:
                        return None, self._proxy_get(url)
                    except Exception as exc:  # noqa: BLE001
                        print(f"    proxy fallback failed: {exc}", file=sys.stderr)
                    continue
                if r.status_code in (500, 502, 503, 504):
                    print(f"    HTTP {r.status_code} for {url}", file=sys.stderr)
                    self._sleep_backoff(attempt)
                    attempt += 1
                    continue
                r.raise_for_status()
            except Exception as exc:  # noqa: BLE001
                self.last_request = time.monotonic()
                print(f"    {type(exc).__name__}: {exc}", file=sys.stderr)
                self._sleep_backoff(attempt)
                attempt += 1
        raise RuntimeError(f"failed after retries: GET {url}")

    def _cached(self, key: str, method: str, url: str, force: bool = False, **kwargs):
        html_path, meta_path = self._cache_paths(key)
        if not force and not self.refresh and html_path.exists() and meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text())
                if not (self.refetch_proxy and meta.get("via_proxy")):
                    self.cache_hits += 1
                    return html_path.read_text(encoding="utf-8", errors="replace"), meta
            except Exception:  # noqa: BLE001
                pass
        r, proxy_html = self._do(method, url, **kwargs)
        if proxy_html is not None:
            crawl_utc = int(time.time())
            meta = {
                "url": url,
                "crawl_utc": crawl_utc,
                "date_header": None,
                "status": 200,
                "via_proxy": True,
                "proxy_name": self.last_proxy_name,
                "detected_source_language": self.last_detected_lang,
            }
            html_path.write_text(proxy_html, encoding="utf-8")
            meta_path.write_text(json.dumps(meta), encoding="utf-8")
            return proxy_html, meta
        try:
            crawl_utc = int(parsedate_to_datetime(r.headers["Date"]).timestamp())
        except Exception:  # noqa: BLE001
            crawl_utc = int(time.time())
        meta = {
            "url": url,
            "crawl_utc": crawl_utc,
            "date_header": r.headers.get("Date"),
            "status": r.status_code,
        }
        html_path.write_text(r.text, encoding="utf-8")
        meta_path.write_text(json.dumps(meta), encoding="utf-8")
        return r.text, meta

    def get(self, url: str, key: str | None = None, force: bool = False):
        return self._cached(key or f"GET {url}", "GET", url, force=force)

    def post(self, url: str, data: dict, key: str | None = None, headers: dict | None = None, force: bool = False):
        return self._cached(
            key or f"POST {url} {sorted(data.items())}",
            "POST",
            url,
            force=force,
            data=data,
            headers=headers or {},
        )


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #


def parse_abs(text: str) -> int:
    dt = datetime.strptime(text.strip(), "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
    return int(dt.timestamp())


def parse_dmy(text: str) -> int:
    dt = datetime.strptime(text.strip().upper(), "%d/%m/%Y %I:%M %p").replace(tzinfo=TZ)
    return int(dt.timestamp())


def clean_body(el) -> str:
    if el is None:
        return ""
    # BeautifulSoup decodes entities; turn block breaks into spaces.
    text = el.get_text(" ", strip=True)
    return " ".join(text.split())


def parse_forum_page(html: str, crawl_utc: int) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    rows = []
    for seq, d in enumerate(soup.select("div.comment-info-div[data-commentid]")):
        cid = (d.get("data-commentid") or "").strip()
        if not cid:
            continue
        t_el = d.select_one("span.me-1")
        time_text = t_el.get_text(strip=True) if t_el else ""
        author_el = d.select_one("p.subtitle a")
        body_el = d.select_one("p.comment")
        rows.append(
            {
                "native_id": cid,
                "pageid": (d.get("data-pageid") or "").strip(),
                "forumtitle": (d.get("data-forumtitle") or "").strip(),
                "postuserid": (d.get("data-postuserid") or "").strip(),
                "author": author_el.get_text(strip=True) if author_el else None,
                "body": clean_body(body_el),
                "time_text": time_text,
                "crawl_utc": crawl_utc,
                "seq": seq,
            }
        )
    # A page can render the same comment twice only if the site itself did so.
    seen = set()
    uniq = []
    for row in rows:
        if row["native_id"] in seen:
            continue
        seen.add(row["native_id"])
        uniq.append(row)
    return uniq


def parse_comservlet(html: str) -> tuple[dict[str, int], dict[str, str], int | None, int]:
    """Return (comment_id -> epoch, comment_id -> original text, total, count)."""
    soup = BeautifulSoup(html, "lxml")
    out: dict[str, int] = {}
    texts: dict[str, str] = {}
    for div in soup.select("div.comtb[id]"):
        ident = div.get("id") or ""
        if not (ident.startswith("c") and ident[1:].isdigit()):
            continue
        t = div.select_one("span.comdt")
        if not t:
            continue
        text = t.get_text(strip=True)
        if not DMY_RE.match(text):
            continue
        out[ident[1:]] = parse_dmy(text)
        texts[ident[1:]] = text
    total = None
    m = re.search(r"Showing\s+[\d,]+\s+of\s+([\d,]+)\s+comments", html)
    if m:
        total = int(m.group(1).replace(",", ""))
    return out, texts, total, len(out)


def get_last_page(client: Client, pid: str) -> int:
    html, _ = client.get(f"{BASE}/web/forum/forum-thread/{pid}", key=f"thread-base {pid}")
    pages = [int(x) for x in re.findall(rf"forum-thread/{pid}\?p=(\d+)", html)]
    if not pages:
        raise RuntimeError(f"no pagination found for {pid}")
    return max(pages)


def get_total_and_first(client: Client, stock: dict) -> dict:
    pid = stock["pid"]
    # Total comments and exact recent timestamps.
    com_html, _ = client.post(
        f"{BASE}/comservlet.jsp",
        data={"aa": "sa", "p": pid},
        key=f"comservlet {pid}",
        headers={
            "Referer": f"{BASE}/jsp/scl/community.jsp?m=1",
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    cs, cs_texts, total, cs_count = parse_comservlet(com_html)

    # First post of the thread (page 1) for the post record.
    html, _ = client.get(
        f"{BASE}/web/forum/forum-thread/{pid}?p=1", key=f"thread-page {pid} 1"
    )
    rows = parse_forum_page(html, 0)
    first_ts = None
    first_text = None
    for row in rows:
        if ABS_RE.match(row["time_text"]):
            first_ts = parse_abs(row["time_text"])
            first_text = row["time_text"]
            break
    return {
        "comservlet": cs,
        "comservlet_texts": cs_texts,
        "total": total,
        "comservlet_count": cs_count,
        "first_ts": first_ts,
        "first_text": first_text,
    }


def page_max_ts(client: Client, pid: str, page: int) -> int | None:
    html, meta = client.get(
        f"{BASE}/web/forum/forum-thread/{pid}?p={page}", key=f"thread-page {pid} {page}"
    )
    rows = parse_forum_page(html, meta["crawl_utc"])
    ts = [parse_abs(r["time_text"]) for r in rows if ABS_RE.match(r["time_text"])]
    return max(ts) if ts else None


def page_min_ts(client: Client, pid: str, page: int) -> int | None:
    html, meta = client.get(
        f"{BASE}/web/forum/forum-thread/{pid}?p={page}", key=f"thread-page {pid} {page}"
    )
    rows = parse_forum_page(html, meta["crawl_utc"])
    ts = [parse_abs(r["time_text"]) for r in rows if ABS_RE.match(r["time_text"])]
    return min(ts) if ts else None


def get_last_content_page(client: Client, pid: str, sentinel: int) -> tuple[int, int]:
    """The pagination max is the disabled 'next' page; find the last real page."""
    for page in (sentinel, sentinel - 1, sentinel - 2):
        if page < 1:
            continue
        html, meta = client.get(
            f"{BASE}/web/forum/forum-thread/{pid}?p={page}",
            key=f"thread-page {pid} {page}",
        )
        rows = parse_forum_page(html, meta["crawl_utc"])
        if rows:
            return page, len(rows)
    raise RuntimeError(f"no content page found near sentinel {sentinel} for {pid}")


# --------------------------------------------------------------------------- #
# Timestamp resolution
# --------------------------------------------------------------------------- #


def bucket_for_label(label: str, anchor: int) -> tuple[int, int] | None:
    label = label.strip()
    if label.lower() == "just now":
        return anchor - 60, anchor
    m = REL_RE.match(label)
    if not m:
        return None
    n = int(m.group(1))
    unit = m.group(2).lower()
    width = {
        "minute": 60,
        "hour": 3600,
        "day": 86400,
        "week": 7 * 86400,
        "month": 30 * 86400,
    }[unit]
    return anchor - (n + 1) * width, anchor - n * width


def interpolate(anchors: list[tuple[int, int]], x: int) -> int | None:
    if not anchors:
        return None
    ids = [a[0] for a in anchors]
    i = bisect.bisect_left(ids, x)
    if i == 0:
        return anchors[0][1]
    if i == len(anchors):
        return anchors[-1][1]
    x0, t0 = anchors[i - 1]
    x1, t1 = anchors[i]
    if x1 == x0:
        return t0
    return int(round(t0 + (t1 - t0) * (x - x0) / (x1 - x0)))


def resolve_timestamps(
    rows_by_stock: dict[str, list[dict]],
    comservlet: dict[str, dict[str, int]],
    global_anchors: list[tuple[int, int]],
    window_end: int,
) -> dict:
    stats = {
        "absolute_page": 0,
        "absolute_comservlet": 0,
        "relative": 0,
        "relative_clamped": 0,
        "relative_outside_bucket": 0,
        "monotonic_fixes": 0,
        "unknown_time_text": Counter(),
    }

    # First pass: exact timestamps.
    for ticker, rows in rows_by_stock.items():
        cs = comservlet.get(ticker, {})
        for row in rows:
            text = row["time_text"]
            if ABS_RE.match(text):
                row["created_utc"] = parse_abs(text)
                row["time_confidence"] = "absolute"
                row["time_source"] = "forum_page"
                stats["absolute_page"] += 1
            elif row["native_id"] in cs:
                row["created_utc"] = cs[row["native_id"]]
                row["time_confidence"] = "absolute"
                row["time_source"] = "comservlet"
                stats["absolute_comservlet"] += 1
            else:
                row["created_utc"] = None
                row["time_confidence"] = "relative"
                row["time_source"] = "id_interpolation_label_clamped"
                stats["relative"] += 1

    # Second pass: relative estimates.
    for ticker, rows in rows_by_stock.items():
        for row in rows:
            if row["created_utc"] is not None:
                continue
            bucket = bucket_for_label(row["time_text"], row["crawl_utc"])
            if bucket is None:
                stats["unknown_time_text"][row["time_text"]] += 1
                # Never leave a null: place at the page's crawl time as a last resort.
                row["created_utc"] = row["crawl_utc"]
                row["time_precision"] = "coarse"
                continue
            lo, hi = bucket
            prior = interpolate(global_anchors, int(row["native_id"]))
            if prior is None:
                prior = (lo + hi) // 2
            t = min(max(prior, lo), hi)
            if t != prior:
                stats["relative_clamped"] += 1
            row["created_utc"] = t
            row["time_precision"] = "estimated"

    # Enforce monotonic order within each thread (page/seq is already ascending).
    for ticker, rows in rows_by_stock.items():
        prev = WINDOW_START_TS - 1
        for row in rows:
            if row["created_utc"] < prev:
                row["created_utc"] = prev
                stats["monotonic_fixes"] += 1
            prev = row["created_utc"]
        nxt = window_end + 1
        for row in reversed(rows):
            if row["created_utc"] > nxt:
                row["created_utc"] = nxt
                stats["monotonic_fixes"] += 1
            nxt = row["created_utc"]

    # Validate bucket membership for estimated rows (report only).
    for ticker, rows in rows_by_stock.items():
        for row in rows:
            if row.get("time_precision") != "estimated":
                continue
            b = bucket_for_label(row["time_text"], row["crawl_utc"])
            if b and not (b[0] <= row["created_utc"] <= b[1]):
                stats["relative_outside_bucket"] += 1
    return stats


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def crawl_stock(client: Client, stock: dict, total_comments: int | None) -> tuple[list[dict], dict]:
    pid = stock["pid"]
    ticker = stock["ticker"]
    info: dict = {"ticker": ticker, "pid": pid, "pages": [], "errors": []}

    sentinel = get_last_page(client, pid)
    last_content_page, last_page_rows = get_last_content_page(client, pid, sentinel)
    info["sentinel_page"] = sentinel
    info["last_content_page"] = last_content_page
    info["last_page_rows"] = last_page_rows
    print(
        f"{ticker}: sentinel {sentinel}, last content page "
        f"{last_content_page} ({last_page_rows} rows)"
    )

    # First page whose newest post is >= window start.
    lo, hi = 1, last_content_page
    while lo < hi:
        mid = (lo + hi) // 2
        mx = page_max_ts(client, pid, mid)
        print(f"  start search p={mid}: max={mx}")
        if mx is not None and mx >= WINDOW_START_TS:
            hi = mid
        else:
            lo = mid + 1
    start_page = lo

    # First page whose oldest post is > window end (entirely after the window).
    lo, hi = start_page, last_content_page
    while lo < hi:
        mid = (lo + hi) // 2
        mn = page_min_ts(client, pid, mid)
        print(f"  end search p={mid}: min={mn}")
        if mn is not None and mn > WINDOW_END_TS:
            hi = mid
        else:
            lo = mid + 1
    after_page = lo
    end_page = max(start_page, after_page - 1)
    info["start_page"] = start_page
    info["after_page"] = after_page
    info["end_page"] = end_page
    print(f"{ticker}: pages {start_page}..{after_page} (last in-window page {end_page})")

    rows: list[dict] = []
    pages: list[int] = []
    pre_count_start = 0
    after_count_end = 0
    relative_rows = 0
    for page in range(start_page, after_page + 1):
        html, meta = client.get(
            f"{BASE}/web/forum/forum-thread/{pid}?p={page}",
            key=f"thread-page {pid} {page}",
        )
        parsed = parse_forum_page(html, meta["crawl_utc"])
        for row in parsed:
            row["page"] = page
            row["url"] = f"{BASE}/web/forum/forum-thread/{pid}?p={page}"
            if ABS_RE.match(row["time_text"]):
                ts = parse_abs(row["time_text"])
                if ts < WINDOW_START_TS:
                    if page == start_page:
                        pre_count_start += 1
                    continue
                if ts > WINDOW_END_TS:
                    if page == end_page:
                        after_count_end += 1
                    continue
            else:
                relative_rows += 1
            rows.append(row)
        pages.append(page)
        if page % 25 == 0 or page == after_page:
            print(f"  {ticker}: fetched p={page} ({len(rows)} in-window rows)")

    # Deduplicate by native comment id, preserving first occurrence.
    by_id: dict[str, dict] = {}
    dups = 0
    for row in rows:
        if row["native_id"] in by_id:
            dups += 1
            continue
        by_id[row["native_id"]] = row
    rows = sorted(by_id.values(), key=lambda r: (r["page"], r["seq"]))
    info["unique_rows"] = len(rows)
    info["duplicates"] = dups
    info["relative_rows_before_resolution"] = relative_rows
    info["pre_count_start_page"] = pre_count_start
    info["after_count_end_page"] = after_count_end
    info["pages_fetched"] = sorted(set(pages))

    # Reconcile against the site's own comment counter.
    pre_window = (start_page - 1) * 50 + pre_count_start
    if end_page < last_content_page:
        after_window = (
            after_count_end
            + (last_content_page - end_page - 1) * 50
            + last_page_rows
        )
    else:
        after_window = after_count_end
    info["pre_window"] = pre_window
    info["after_window"] = after_window
    info["total_comments"] = total_comments
    if total_comments is not None:
        info["in_window_reconciled"] = total_comments - pre_window - after_window
        info["reconciliation_delta"] = len(rows) - info["in_window_reconciled"]
    else:
        info["in_window_reconciled"] = None
        info["reconciliation_delta"] = None
    info["first_kept_id"] = rows[0]["native_id"] if rows else None
    info["last_kept_id"] = rows[-1]["native_id"] if rows else None
    return rows, info


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stock", choices=["GENTING", "GENM", "both"], default="both")
    ap.add_argument("--start-page", type=int, default=None, help="override binary search")
    ap.add_argument("--end-page", type=int, default=None, help="override last page")
    ap.add_argument("--refresh", action="store_true", help="ignore the local page cache")
    ap.add_argument("--min-interval", type=float, default=1.15)
    ap.add_argument(
        "--proxy-mode",
        choices=["auto", "google", "allorigins", "direct"],
        default="auto",
        help="auto: direct first, proxy on 403/429; google/allorigins: force that proxy",
    )
    ap.add_argument(
        "--refetch-proxy",
        action="store_true",
        help="ignore cached pages that were fetched through a proxy",
    )
    args = ap.parse_args(argv)

    tickers = ["GENTING", "GENM"] if args.stock == "both" else [args.stock]
    client = Client(
        min_interval=args.min_interval,
        refresh=args.refresh,
        proxy_mode=args.proxy_mode,
        refetch_proxy=args.refetch_proxy,
    )

    # Fetch metadata and the exact-timestamp endpoint for both threads first.
    meta: dict[str, dict] = {}
    comservlet: dict[str, dict[str, int]] = {}
    comservlet_texts: dict[str, dict[str, str]] = {}
    for ticker in tickers:
        stock = STOCKS[ticker]
        info = get_total_and_first(client, stock)
        comservlet[ticker] = info["comservlet"]
        comservlet_texts[ticker] = info["comservlet_texts"]
        meta[ticker] = {
            "total_comments": info["total"],
            "first_post_ts": info["first_ts"],
            "first_post_time_text": info["first_text"],
            "comservlet_count": info["comservlet_count"],
        }
        print(
            f"{ticker}: total={meta[ticker]['total_comments']} "
            f"first={meta[ticker]['first_post_time_text']} comservlet={meta[ticker]['comservlet_count']}"
        )

    rows_by_stock: dict[str, list[dict]] = {}
    infos: dict[str, dict] = {}
    for ticker in tickers:
        stock = STOCKS[ticker]
        if args.start_page or args.end_page:
            # Small-range test mode: fetch only the requested pages.
            pid = stock["pid"]
            last = args.end_page or get_last_page(client, pid)
            start = args.start_page or last
            rows = []
            for page in range(start, last + 1):
                html, m = client.get(
                    f"{BASE}/web/forum/forum-thread/{pid}?p={page}",
                    key=f"thread-page {pid} {page}",
                )
                parsed = parse_forum_page(html, m["crawl_utc"])
                for row in parsed:
                    row["page"] = page
                    row["url"] = f"{BASE}/web/forum/forum-thread/{pid}?p={page}"
                rows.extend(parsed)
            rows_by_stock[ticker] = rows
            infos[ticker] = {
                "ticker": ticker,
                "pid": pid,
                "pages_fetched": list(range(start, last + 1)),
                "unique_rows": len(rows),
                "test_mode": True,
            }
            continue

        rows, info = crawl_stock(
            client,
            stock,
            meta[ticker]["total_comments"],
        )
        rows_by_stock[ticker] = rows
        infos[ticker] = info

    # Global anchors: every exact timestamp observed in either thread, plus the
    # comservlet timestamps (same global comment-id sequence).  Build this from
    # the page text before resolve_timestamps() sets time_confidence.
    anchor_map: dict[int, int] = {}
    for ticker in tickers:
        for row in rows_by_stock[ticker]:
            if ABS_RE.match(row["time_text"]):
                anchor_map[int(row["native_id"])] = parse_abs(row["time_text"])
        for cid, ts in comservlet.get(ticker, {}).items():
            anchor_map.setdefault(int(cid), ts)
    anchors = sorted(anchor_map.items())
    # Drop any anchor that breaks the global id -> time monotonicity.
    clean = []
    for cid, ts in anchors:
        if clean and ts < clean[-1][1]:
            continue
        clean.append((cid, ts))
    anchors = clean
    print(f"global anchors: {len(anchors)}")

    window_end = WINDOW_END_TS
    stats = resolve_timestamps(rows_by_stock, comservlet, anchors, window_end)

    # Attach the original comservlet timestamp strings for provenance.
    for ticker in tickers:
        for row in rows_by_stock[ticker]:
            if row.get("time_source") == "comservlet":
                txt = comservlet_texts[ticker].get(row["native_id"])
                if txt:
                    row["comservlet_time_text"] = txt

    # Build output records.
    outputs: dict[str, list[dict]] = {}
    for ticker in tickers:
        stock = STOCKS[ticker]
        rows = rows_by_stock[ticker]
        # Filter again now that relative rows have timestamps.
        rows = [
            r
            for r in rows
            if WINDOW_START_TS <= r["created_utc"] <= WINDOW_END_TS
        ]
        # Stable order by timestamp then id.
        rows.sort(key=lambda r: (r["created_utc"], int(r["native_id"])))
        post = {
            "record_type": "post",
            "source": "i3investor",
            "channel": stock["channel"],
            "native_id": stock["pid"],
            "ticker": stock["ticker"],
            "title": stock["title"],
            "author": None,
            "author_id": None,
            "created_utc": meta[ticker]["first_post_ts"]
            or int(datetime(2011, 11, 28, tzinfo=TZ).timestamp()),
            "url": f"{BASE}/web/forum/forum-thread/{stock['pid']}",
            "body": None,
            "score": None,
            "num_comments": meta[ticker]["total_comments"],
            "lang": None,
            "raw": {
                "forum_id": stock["pid"],
                "stock_code": stock["code"],
                "first_post_time_text": meta[ticker]["first_post_time_text"],
                "total_comments_at_crawl": meta[ticker]["total_comments"],
                "timestamp_note": (
                    "Thread creation time is the first displayed post; it predates the "
                    "collection window by design."
                ),
            },
        }
        records = [post]
        for row in rows:
            raw = {
                "time_text": row["time_text"],
                "page": row["page"],
                "postuserid": row["postuserid"],
                "forumtitle": row["forumtitle"],
                "time_confidence": row["time_confidence"],
                "time_source": row["time_source"],
                "crawl_utc": row["crawl_utc"],
            }
            if row.get("time_precision"):
                raw["time_precision"] = row["time_precision"]
            if row.get("comservlet_time_text"):
                raw["comservlet_time_text"] = row["comservlet_time_text"]
            if row["body"].strip().lower().replace(" ", "") == "postremoved.why?":
                raw["body_status"] = "removed_placeholder"
            rec = {
                "record_type": "reply",
                "source": "i3investor",
                "channel": stock["channel"],
                "native_id": row["native_id"],
                "post_native_id": stock["pid"],
                "parent_native_id": None,
                "depth": 0,
                "author": row["author"],
                "author_id": row["postuserid"] or None,
                "created_utc": int(row["created_utc"]),
                "body": row["body"],
                "score": None,
                "url": row["url"],
                "lang": None,
                "raw": raw,
            }
            records.append(rec)
        outputs[ticker] = records

    # Write files and a stats sidecar for the report.
    all_stats = {
        "stocks": {},
        "timestamp_resolution": stats,
        "anchors": len(anchors),
        "requests_made": client.requests_made,
        "cache_hits": client.cache_hits,
        "retries": client.retries,
    }
    for ticker in tickers:
        path = OUT_DIR / f"i3investor_{ticker}_{OUT_SUFFIX}.jsonl"
        write_jsonl(path, outputs[ticker])
        rows = [r for r in outputs[ticker] if r["record_type"] == "reply"]
        times = [r["created_utc"] for r in rows]
        all_stats["stocks"][ticker] = {
            **infos[ticker],
            "records": len(outputs[ticker]),
            "replies": len(rows),
            "min_utc": min(times) if times else None,
            "max_utc": max(times) if times else None,
            "min_myt": datetime.fromtimestamp(min(times), TZ).isoformat() if times else None,
            "max_myt": datetime.fromtimestamp(max(times), TZ).isoformat() if times else None,
            "empty_bodies": sum(1 for r in rows if not r["body"].strip()),
            "distinct_authors": len({r["author_id"] for r in rows if r["author_id"]}),
            "by_confidence": dict(Counter(r["raw"]["time_confidence"] for r in rows)),
            "by_page": {
                "first": min(r["raw"]["page"] for r in rows) if rows else None,
                "last": max(r["raw"]["page"] for r in rows) if rows else None,
                "count": len({r["raw"]["page"] for r in rows}),
            },
            "total_comments_at_crawl": meta[ticker]["total_comments"],
        }
        print(f"wrote {path}: {len(outputs[ticker])} records")

    stats_path = Path("/tmp/opencode/i3_backfill_2016_2024_stats.json")
    stats_path.write_text(json.dumps(all_stats, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"stats: {stats_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
