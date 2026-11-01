#!/usr/bin/env python3
"""Collect Bursa Malaysia company announcements for GENTING (3182) and GENM (4715).

Source: KLSE Screener mirror of Bursa announcements (Bursa direct returns 403).
  listing: https://www.klsescreener.com/v2/announcements/stock/<code>?category=&page=N
  detail : https://www.klsescreener.com/v2/announcements/view/<id>

Writes data/raw/company_filings.jsonl (record_type "post", source "bursa_filing").
Also downloads announcement PDF attachments to data/company_docs/announcements/.

HTML is cached under /tmp/opencode/gent/cache so re-runs are cheap.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bs4 import BeautifulSoup
from curl_cffi import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw"
DOCS = ROOT / "data" / "company_docs"
CACHE = Path("/tmp/opencode/gent/cache")
BASE = "https://www.klsescreener.com"
DETAIL_BASE = "https://disclosure.bursamalaysia.com"

STOCKS = {"GENTING": "3182", "GENM": "4715"}
MYT = timezone(timedelta(hours=8))
WINDOW_START = int(datetime(2024, 11, 2, 0, 0, 0, tzinfo=MYT).timestamp())
WINDOW_END = int(datetime(2026, 11, 2, 23, 59, 59, tzinfo=MYT).timestamp())

MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}


class Fetcher:
    def __init__(self) -> None:
        self.s = requests.Session(impersonate="chrome")
        self.s.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-MY,en;q=0.9",
        })
        self.last = 0.0
        self.requests = 0

    def get(self, url: str, binary: bool = False):
        for attempt in range(5):
            wait = 1.05 - (time.time() - self.last)
            if wait > 0:
                time.sleep(wait)
            self.last = time.time()
            self.requests += 1
            try:
                r = self.s.get(url, timeout=60)
            except Exception as exc:  # noqa: BLE001
                print(f"  ! {url} {exc}", flush=True)
                time.sleep(5 + attempt * 5)
                continue
            if r.status_code in (429, 500, 502, 503, 504):
                delay = 10 * (attempt + 1)
                print(f"  ! HTTP {r.status_code} {url}; backoff {delay}s", flush=True)
                time.sleep(delay)
                continue
            if r.status_code != 200:
                raise RuntimeError(f"HTTP {r.status_code} for {url}")
            return r.content if binary else r.text
        raise RuntimeError(f"giving up on {url}")


def cached_get(f: Fetcher, url: str, key: str, binary: bool = False):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / key
    if path.exists():
        return path.read_bytes() if binary else path.read_text(encoding="utf-8", errors="replace")
    data = f.get(url, binary=binary)
    if binary:
        path.write_bytes(data)
    else:
        path.write_text(data, encoding="utf-8")
    return data


def parse_listing(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    out = []
    for a in soup.select("a.announcement-item"):
        href = a.get("href") or ""
        m = re.search(r"/v2/announcements/view/(\d+)", href)
        if not m:
            continue
        date_box = a.select_one(".date-box")
        day = month = None
        if date_box:
            d = date_box.select_one(".day")
            mo = date_box.select_one(".month")
            day = int(d.get_text(strip=True)) if d and d.get_text(strip=True).isdigit() else None
            month = MONTHS.get(mo.get_text(strip=True)) if mo else None
        meta = a.select_one(".meta")
        company = cat = time_text = None
        if meta:
            c = meta.select_one(".company-label")
            company = c.get_text(strip=True) if c else None
            c = meta.select_one(".category-tag")
            cat = c.get_text(" ", strip=True) if c else None
            c = meta.select_one(".time-ago")
            time_text = c.get_text(strip=True) if c else None
        title_el = a.select_one(".title")
        snippet_el = a.select_one(".snippet")
        out.append({
            "id": m.group(1),
            "url": BASE + href,
            "day": day,
            "month": month,
            "company": company,
            "category": cat,
            "time_text": time_text,
            "title": title_el.get_text(" ", strip=True) if title_el else None,
            "snippet": snippet_el.get_text(" ", strip=True) if snippet_el else None,
        })
    return out


def assign_years(items: list[dict], first_year: int) -> None:
    """Reverse-chronological list: year drops when the month wraps Jan -> Dec."""
    year = first_year
    prev_month = None
    for it in items:
        month = it.get("month")
        if month is None:
            it["year"] = year
            continue
        if prev_month is not None and month > prev_month:
            year -= 1
        it["year"] = year
        it["date"] = f"{year:04d}-{month:02d}-{it['day']:02d}"
        prev_month = month


def parse_detail(html: str, url: str, listing: dict) -> dict:
    soup = BeautifulSoup(html, "lxml")
    title = None
    if soup.title:
        title = re.sub(r"\s*\|\s*KLSE Screener\s*$", "", soup.title.get_text(" ", strip=True)).strip()
    # "GENTING - <real title>" -> keep the real title but retain the stock prefix
    info = {}
    for tr in soup.select("table tr"):
        th = tr.select_one(".formContentLabelH, .formContentLabel")
        td = tr.select_one(".formContentDataH, .formContentData")
        if th and td:
            info.setdefault(th.get_text(" ", strip=True), td.get_text(" ", strip=True).strip())

    body_el = soup.select_one("#D_GA_Content") or soup.select_one("#D_GA_Content".lower())
    if body_el:
        body = body_el.get_text("\n", strip=True)
    else:
        pre = soup.select_one("td.formContentData pre")
        body = pre.get_text("\n", strip=True) if pre else ""

    # Many Bursa templates (shareholding notices, listing circulars) do not use
    # #D_GA_Content; take the whole announcement panel instead.
    ann = soup.select_one("div.bursa-ann")
    if ann:
        for tag in ann.select("script, style"):
            tag.decompose()
        panel = ann.get_text("\n", strip=True)
        cut = panel.find("Announcement Info")
        if cut > 0:
            panel = panel[:cut]
        if len(panel.strip()) > len(body.strip()):
            body = panel

    # Normalise whitespace but keep paragraph breaks.
    body = body.replace("\xa0", " ")
    body = re.sub(r"[ \t\r\f\v]+", " ", body)
    body = re.sub(r" *\n *", "\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()

    subject = None
    desc = None
    for tr in soup.select("table.InputTable2 tr"):
        th = tr.select_one("td.formContentLabel")
        td = tr.select_one("td.formContentData")
        if not th or not td:
            continue
        label = th.get_text(" ", strip=True)
        val = td.get_text("\n", strip=True)
        if label == "Subject":
            subject = val
        elif label == "Description":
            desc = val

    attachments = []
    for a in soup.select("a[href]"):
        h = a.get("href") or ""
        if "FileAccess" in h or "/FileAccess/" in h:
            name = a.get_text(" ", strip=True) or h.rsplit("=", 1)[-1]
            if h.startswith("/"):
                h = DETAIL_BASE + h
            attachments.append({"name": name, "url": h})

    announced = info.get("Date Announced")
    created = None
    date_iso = None
    if announced:
        m = re.search(r"(\d{1,2}) (\w{3}) (\d{4})", announced)
        if m:
            day, mon, yr = int(m.group(1)), MONTHS[m.group(2)], int(m.group(3))
            date_iso = f"{yr:04d}-{mon:02d}-{day:02d}"
            hh = mm = 0
            tm = re.search(r"(\d{1,2}):(\d{2})\s*(am|pm)", listing.get("time_text") or "", re.I)
            if tm:
                hh, mm = int(tm.group(1)), int(tm.group(2))
                if tm.group(3).lower() == "pm" and hh != 12:
                    hh += 12
                if tm.group(3).lower() == "am" and hh == 12:
                    hh = 0
            dt = datetime(yr, mon, day, hh, mm, tzinfo=MYT)
            created = int(dt.astimezone(timezone.utc).timestamp())

    return {
        "title": title,
        "company_name": info.get("Company Name"),
        "stock_name": info.get("Stock Name"),
        "date_announced": announced,
        "date_iso": date_iso,
        "category": info.get("Category") or listing.get("category"),
        "reference": info.get("Reference Number"),
        "subject": subject,
        "description": desc,
        "body": body,
        "attachments": attachments,
    }



def normalize_type(rec: dict) -> str:
    t = (rec.get("title") or "").upper()
    d = (rec["raw"].get("description") or "").upper()
    c = (rec["raw"].get("category") or "").upper()
    blob = t + " " + d
    if "FINANCIAL RESULTS" in c:
        return "financial_results"
    if "RIGHTS ISSUE" in blob or "FUND RAISING" in blob:
        return "rights_issue"
    if "TAKE-OVER" in blob or "TAKEOVER" in blob or "TAKE-OVER OFFER" in c:
        return "takeover"
    if "LITIGATION" in blob:
        return "litigation"
    if ("MEDIUM TERM NOTES" in blob or "MTN" in blob or "SUBORDINATED" in blob
            or "TENDER OFFER" in blob):
        return "bond_mtn"
    if "BUY BACK" in blob or "BUY-BACK" in blob:
        return "buyback"
    if "DIVIDEND" in blob or "BOOK CLOSURE" in blob or "ENTITLEMENT" in c:
        return "dividend"
    if ("SUB. S-HLDR" in t or "SUBSTANTIAL SHAREHOLDER" in c
            or "SUBSTANTIAL SHAREHOLDER" in blob):
        return "substantial_shareholder"
    if ("DIRECTOR'S INTEREST" in t or "DIRECTOR'S INTEREST" in c
            or "DEALINGS IN LISTED SECURITIES" in t):
        return "director_dealing"
    if "GENERAL MEETING" in c or "ANNUAL GENERAL MEETING" in blob:
        return "agm_egm"
    if "ANNUAL REPORT" in blob:
        return "annual_report"
    if "CIRCULAR" in blob:
        return "circular"
    if "BOARDROOM" in c or "COMMITTEE" in c or "PRINCIPAL OFFICER" in c:
        return "governance"
    if "LISTING CIRCULAR" in c or "SUSPENSION" in blob or "RESUMPTION" in blob:
        return "listing_circular"
    return "other"


def enrich(records: list[dict]) -> None:
    manifest_path = DOCS / "pdf_manifest.json"
    by_id: dict[str, list[str]] = {}
    if manifest_path.exists():
        for v in json.loads(manifest_path.read_text()).values():
            by_id.setdefault(v["native_id"], []).append(v["local"])
    for rec in records:
        rec["raw"]["local_pdfs"] = sorted(by_id.get(rec["native_id"], []))
        rec["raw"]["normalized_type"] = normalize_type(rec)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers", nargs="*", default=list(STOCKS))
    ap.add_argument("--no-details", action="store_true")
    ap.add_argument("--max-pages", type=int, default=40)
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    f = Fetcher()
    all_records = []

    for ticker in args.tickers:
        code = STOCKS[ticker.upper()]
        print(f"== {ticker} ({code}) listing ==", flush=True)
        listing: list[dict] = []
        seen: set[str] = set()
        page = 1
        stop = False
        while not stop and page <= args.max_pages:
            url = f"{BASE}/v2/announcements/stock/{code}?category=&page={page}"
            html = cached_get(f, url, f"{code}_list_{page}.html")
            items = parse_listing(html)
            new = [i for i in items if i["id"] not in seen]
            for i in new:
                seen.add(i["id"])
            listing.extend(new)
            # year inference across the whole sequence
            assign_years(listing, 2026)
            oldest = listing[-1].get("date") if listing else None
            print(f"  page {page}: {len(items)} items, oldest {oldest}", flush=True)
            if not new:
                break
            if oldest and oldest < "2024-11-01":
                stop = True
            page += 1
        # keep through the window, plus a small margin for year-inference errors
        listing = [i for i in listing if i.get("date") and "2024-10-01" <= i["date"] <= "2026-11-03"]
        listing.sort(key=lambda i: (i["date"], -int(i["id"])))

        records = []
        for n, item in enumerate(listing, 1):
            if args.no_details:
                continue
            html = cached_get(f, item["url"], f"detail_{item['id']}.html")
            d = parse_detail(html, item["url"], item)
            if not d["date_iso"]:
                print(f"  ! no date for {item['id']}", flush=True)
                continue
            ts = d["date_iso"]
            if not ("2024-11-02" <= ts <= "2026-11-02"):
                continue
            body = d["body"] or d["description"] or d["subject"] or item.get("snippet") or ""
            # date + wall-clock time as shown on the listing (Malaysia time)
            hh = mm = 0
            tm = re.search(r"(\d{1,2}):(\d{2})\s*(am|pm)", item.get("time_text") or "", re.I)
            if tm:
                hh, mm = int(tm.group(1)), int(tm.group(2))
                if tm.group(3).lower() == "pm" and hh != 12:
                    hh += 12
                if tm.group(3).lower() == "am" and hh == 12:
                    hh = 0
            dt = datetime.strptime(d["date_iso"], "%Y-%m-%d").replace(
                hour=hh, minute=mm, tzinfo=MYT)
            title = d["title"] or item.get("title") or ""
            for _ in range(2):
                prefix = f"{ticker.upper()} - "
                if title.startswith(prefix):
                    title = title[len(prefix):]
            rec = {
                "record_type": "post",
                "source": "bursa_filing",
                "channel": ticker.upper(),
                "native_id": f"klse_screener:{item['id']}",
                "ticker": ticker.upper(),
                "title": title.strip() or None,
                "author": None,
                "author_id": None,
                "created_utc": int(dt.astimezone(timezone.utc).timestamp()),
                "url": item["url"],
                "body": body,
                "score": None,
                "num_comments": None,
                "lang": "en",
                "raw": {
                    "announcement_id": item["id"],
                    "company_name": d["company_name"],
                    "stock_name": d["stock_name"],
                    "date_announced": d["date_announced"],
                    "time_text": item.get("time_text"),
                    "category": d["category"],
                    "listing_category": item.get("category"),
                    "reference": d["reference"],
                    "subject": d["subject"],
                    "description": d["description"],
                    "attachments": d["attachments"],
                    "snippet": item.get("snippet"),
                    "bursa_original_url": None,
                },
            }
            # link to the original Bursa announcement if present
            for a in BeautifulSoup(html, "lxml").select("a[href]"):
                h = a.get("href") or ""
                if "bursamalaysia.com/market_information/announcements" in h:
                    rec["raw"]["bursa_original_url"] = h
                    break
            records.append(rec)
            if n % 25 == 0:
                print(f"  {n}/{len(listing)} details", flush=True)

        records.sort(key=lambda r: (r["created_utc"], r["native_id"]))
        all_records.extend(records)
        print(f"  -> {len(records)} announcements in window for {ticker}", flush=True)

    all_records.sort(key=lambda r: (r["created_utc"], r["native_id"]))
    enrich(all_records)
    path = OUT / "company_filings.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for rec in all_records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"wrote {len(all_records)} -> {path}; requests={f.requests}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
