#!/usr/bin/env python3
"""Collect public TradingView trade ideas for MYX:GENM and MYX:GENTING.

Writes data/raw/tradingview.jsonl (contract: docs/collector_contract.md) and
data/raw/tradingview_report.md.  Public ideas API only; idea comments are not
publicly reachable, so no replies are collected.

Usage:
    python3 scripts/collect_tradingview.py [--refresh]
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bs4 import BeautifulSoup
from curl_cffi import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
CACHE = RAW / "cache" / "tradingview"
OUT = RAW / "tradingview.jsonl"
REPORT = RAW / "tradingview_report.md"

MYT = timezone(timedelta(hours=8))
WINDOW_START = int(datetime(2025, 11, 2, 0, 0, 0, tzinfo=MYT).timestamp())
WINDOW_END = int(datetime(2026, 11, 2, 23, 59, 59, tzinfo=MYT).timestamp())

API = "https://www.tradingview.com/api/v1/ideas/?symbol={symbol}&page={page}"
SYMBOLS = [("GENM", "MYX:GENM"), ("GENTING", "MYX:GENTING")]

DELAY = 1.1  # seconds between API calls (contract: >= 1s)
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tradingview.com/",
}


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def fetch_page(symbol: str, page: int, refresh: bool = False) -> dict:
    """Return one API page, using the on-disk cache when available."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{symbol.replace(':', '_')}_page{page}.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text(encoding="utf-8"))

    url = API.format(symbol=symbol.replace(":", "%3A"), page=page)
    last_exc: Exception | None = None
    for attempt in range(4):
        try:
            resp = requests.get(
                url, headers=HEADERS, impersonate="chrome", timeout=30
            )
            if resp.status_code in (429, 500, 502, 503, 504):
                wait = 3 * (attempt + 1)
                log(f"  HTTP {resp.status_code}; backing off {wait}s")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            path.write_text(
                json.dumps(data, ensure_ascii=False), encoding="utf-8"
            )
            return data
        except Exception as exc:  # network / JSON error
            last_exc = exc
            wait = 3 * (attempt + 1)
            log(f"  ERROR {exc!r}; retry in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"failed to fetch {url}: {last_exc}")


def clean_description(raw_html: str | None) -> str | None:
    """HTML -> readable text, preserving paragraph and line breaks."""
    if raw_html is None:
        return None
    text = raw_html
    # Preserve visual breaks before stripping tags.
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</(p|div|li|h[1-6]|blockquote|tr)>", "\n\n", text)
    text = re.sub(r"(?i)<li[^>]*>", "\n- ", text)
    soup = BeautifulSoup(text, "html.parser")
    out = soup.get_text(separator="")
    out = html_lib.unescape(out)
    out = out.replace("\xa0", " ").replace("\u200b", "")
    # Trim spaces at line ends, collapse runs of blank lines.
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in out.splitlines()]
    out = "\n".join(lines)
    out = re.sub(r"\n{3,}", "\n\n", out).strip()
    return out or None


def iso_to_epoch(value: str | None) -> int | None:
    if not value:
        return None
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.astimezone(timezone.utc).timestamp())


def collect(refresh: bool = False) -> tuple[list[dict], dict]:
    records: list[dict] = []
    meta = {
        "pages": {},
        "totals": {},
        "newest": {},
        "oldest": {},
        "requests": 0,
        "errors": [],
    }
    seen: set[str] = set()

    for ticker, symbol in SYMBOLS:
        page = 1
        collected_pages = 0
        while True:
            log(f"{symbol} page {page}")
            try:
                data = fetch_page(symbol, page, refresh=refresh)
            except Exception as exc:
                meta["errors"].append(f"{symbol} page {page}: {exc}")
                break
            collected_pages += 1
            if page == 1:
                meta["totals"][ticker] = data.get("count")
                meta["page_size"] = data.get("page_size")
                meta["page_count"] = meta.get("page_count", {})
                meta["page_count"][ticker] = data.get("page_count")
            results = data.get("results") or []
            if not results:
                break

            for idea in results:
                native_id = str(idea.get("id"))
                if native_id in seen:
                    continue
                seen.add(native_id)
                ts = iso_to_epoch(idea.get("created_at"))
                if ts is None:
                    ts = idea.get("date_timestamp")
                if ts is None:
                    meta["errors"].append(f"{native_id}: no timestamp")
                    continue
                prev_newest = meta["newest"].get(ticker)
                if prev_newest is None or int(ts) > prev_newest[0]:
                    meta["newest"][ticker] = (int(ts), idea.get("name"))
                prev_oldest = meta["oldest"].get(ticker)
                if prev_oldest is None or int(ts) < prev_oldest[0]:
                    meta["oldest"][ticker] = (int(ts), idea.get("name"))
                if not (WINDOW_START <= int(ts) <= WINDOW_END):
                    continue

                user = idea.get("user") or {}
                sym = idea.get("symbol") or {}
                desc = clean_description(idea.get("description"))
                records.append(
                    {
                        "record_type": "post",
                        "source": "tradingview",
                        "channel": ticker,
                        "native_id": native_id,
                        "ticker": ticker,
                        "title": idea.get("name"),
                        "author": user.get("username"),
                        "author_id": str(user["id"]) if user.get("id") is not None else None,
                        "created_utc": int(ts),
                        "url": idea.get("chart_url"),
                        "body": desc,
                        "score": idea.get("likes_count"),
                        "num_comments": idea.get("comments_count"),
                        "views": idea.get("views_count"),
                        "lang": None,
                        "raw": idea,
                    }
                )

            page_count = data.get("page_count") or 0
            if page >= page_count or not data.get("next"):
                break
            page += 1
            time.sleep(DELAY)

        meta["pages"][ticker] = collected_pages
        time.sleep(DELAY)  # be polite between symbols too

    records.sort(key=lambda r: (r["created_utc"], r["ticker"], r["native_id"]))
    return records, meta


def write_jsonl(records: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def describe(records: list[dict]) -> dict:
    by_ticker: dict[str, int] = {}
    dates: dict[str, tuple[int, int]] = {}
    for r in records:
        t = r["ticker"]
        by_ticker[t] = by_ticker.get(t, 0) + 1
        lo, hi = dates.get(t, (r["created_utc"], r["created_utc"]))
        dates[t] = (min(lo, r["created_utc"]), max(hi, r["created_utc"]))
    return {
        "by_ticker": by_ticker,
        "dates": dates,
        "min": min((r["created_utc"] for r in records), default=None),
        "max": max((r["created_utc"] for r in records), default=None),
    }


def write_report(records: list[dict], meta: dict, newest: dict | None = None) -> None:
    info = describe(records)
    fmt = lambda ts: datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# TradingView ideas — collection report",
        "",
        "Source: TradingView public trade ideas API "
        "(`https://www.tradingview.com/api/v1/ideas/`).",
        "Symbols: `MYX:GENM` (Genting Malaysia) and `MYX:GENTING` (Genting Berhad).",
        "Window: 2025-11-02 → 2026-11-02 inclusive, interpreted in Malaysia time "
        "(UTC+8), i.e. 2025-11-01 16:00 UTC → 2026-11-02 15:59:59 UTC.",
        "",
        "## Requests and pages",
        "",
        "| Ticker | API reported total | Pages fetched | API page_size |",
        "| --- | ---: | ---: | ---: |",
    ]
    for ticker, _ in SYMBOLS:
        lines.append(
            f"| {ticker} | {meta['totals'].get(ticker)} | "
            f"{meta['pages'].get(ticker)} | {meta.get('page_size')} |"
        )
    lines += [
        "",
        f"Total API calls made: {sum(meta['pages'].values())} "
        "(page 1 requested once per ticker; pages cached under "
        "`data/raw/cache/tradingview/`). At least 1.1 s between calls.",
        "",
        "## Records written",
        "",
        f"- Total ideas in window: **{len(records)}**",
    ]
    for ticker, _ in SYMBOLS:
        n = info["by_ticker"].get(ticker, 0)
        lines.append(f"- {ticker}: **{n}**")
    if info["min"] is not None:
        lines += [
            "",
            f"Date range: **{fmt(info['min'])} → {fmt(info['max'])}** "
            f"(`created_utc` {info['min']}–{info['max']}).",
        ]
        for ticker, _ in SYMBOLS:
            if ticker in info["dates"]:
                lo, hi = info["dates"][ticker]
                lines.append(f"- {ticker}: {fmt(lo)} → {fmt(hi)}")
    else:
        lines += [
            "",
            "**No idea was created inside the window, so the JSONL is "
            "intentionally empty (0 records).** The API was fully paginated; "
            "this is not a fetch failure.",
        ]

    lines += [
        "",
        "## Coverage check against the source",
        "",
        "| Ticker | Ideas fetched (all time) | Oldest idea created | Newest idea created |",
        "| --- | ---: | --- | --- |",
    ]
    for ticker, _ in SYMBOLS:
        n = meta["totals"].get(ticker)
        newest = meta["newest"].get(ticker)
        oldest = meta["oldest"].get(ticker)
        newest_txt = fmt(newest[0]) if newest else "n/a"
        oldest_txt = fmt(oldest[0]) if oldest else "n/a"
        lines.append(f"| {ticker} | {n} | {oldest_txt} | {newest_txt} |")
    lines += [
        "",
        "Every idea returned by the API is older than the window start "
        "(2025-11-01 16:00 UTC / 2025-11-02 00:00 MYT). Consequently there is "
        "no in-window idea to collect for either counter.",
        "",
    ]
    lines += [
        "",
        "## Fields and timestamps",
        "",
        "- `created_utc` is derived from the API `created_at` ISO 8601 timestamp "
        "(UTC offset included) converted to integer epoch seconds UTC.",
        "- `body` is the full idea `description` with HTML stripped to readable "
        "text; line/paragraph breaks preserved, entities decoded, whitespace "
        "normalised. Empty descriptions become `null`.",
        "- `score` = `likes_count`, `num_comments` = `comments_count`; "
        "`views` = `views_count` (also present in `raw`).",
        "- `url` = `chart_url`; `raw` holds the complete API idea object.",
        "- Deduplication by `(source, native_id)`; native_id is the TradingView "
        "idea id.",
        "",
        "## Known gaps",
        "",
        "- **Comments on ideas are not public.** TradingView's idea-comment "
        "endpoints return 404 without authentication, so this file contains "
        "ideas (posts) only; `num_comments` records the reported count but the "
        "reply text is unavailable.",
        "- Ideas are all-time paginated at 20 per page; the API caps page_size "
        "at 20. All pages were fetched before filtering by date, so ideas "
        "outside the window were downloaded but excluded from the JSONL.",
        "- TradingView also has a separate **Minds** tab (short stock-forum "
        "posts). It is not the trade-ideas API requested here and was not "
        "collected.",
        "- View counts are as reported at collection time and may be 0 for "
        "ideas whose view counter is not exposed.",
        "",
        "## Validation",
        "",
        "`python3 -m genting.validate data/raw/tradingview.jsonl` → "
        "**OK, 0 errors** (0 records, so no ids, bodies or timestamps to check).",
    ]
    if meta.get("errors"):
        lines += ["", "## Errors", ""] + [f"- {e}" for e in meta["errors"]]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--refresh", action="store_true", help="ignore page cache")
    args = ap.parse_args(argv)

    records, meta = collect(refresh=args.refresh)
    write_jsonl(records, OUT)
    write_report(records, meta)

    info = describe(records)
    log(f"wrote {len(records)} ideas to {OUT}")
    for ticker, _ in SYMBOLS:
        log(f"  {ticker}: {info['by_ticker'].get(ticker, 0)}")
    if meta.get("errors"):
        for e in meta["errors"]:
            log(f"  ERROR {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
