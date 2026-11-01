#!/usr/bin/env python3
"""Collect Bursa announcements for GENTING (3182) and GENM (4715) via mirrors.

Sources:
  KLSE Screener list + detail (dates, times, category, description, Bursa ann id)
  Bursa disclosure viewHtml (official body + attachment links; reachable via curl_cffi)
  i3investor announcement list (cross-check; only ~100 latest announcements are exposed)

Outputs:
  data/company_docs/announcements/pages/*.html       cached source pages
  data/company_docs/announcements/pdf/*.pdf          attachment PDFs
  data/company_docs/manifests/announcements.csv      one row per announcement
  data/raw/company_announcements.jsonl               contract records
  data/raw/i3_announcements.jsonl                    i3 cross-check records
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urljoin, unquote

from bs4 import BeautifulSoup
from curl_cffi import requests

ROOT = Path(__file__).resolve().parent.parent
ADIR = ROOT / "data" / "company_docs" / "announcements"
PAGEDIR = ADIR / "pages"
PDFDIR = ADIR / "pdf"
MAN = ROOT / "data" / "company_docs" / "manifests"
OUT_JSONL = ROOT / "data" / "raw" / "company_announcements.jsonl"
OUT_I3 = ROOT / "data" / "raw" / "i3_announcements.jsonl"
MANIFEST = MAN / "announcements.csv"

TICKERS = {"3182": ("GENTING", "Genting Berhad"), "4715": ("GENM", "Genting Malaysia Berhad")}
MYT = timezone(timedelta(hours=8))
START = datetime(2024, 11, 2, tzinfo=MYT)
END = datetime(2026, 11, 2, 23, 59, 59, tzinfo=MYT)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

_last = 0.0


def polite_get(url: str, cache: Path | None = None, tries: int = 4) -> str:
    global _last
    if cache and cache.exists() and cache.stat().st_size > 500:
        return cache.read_text(encoding="utf-8", errors="replace")
    wait = 1.15 - (time.time() - _last)
    if wait > 0:
        time.sleep(wait)
    last_err = None
    for attempt in range(1, tries + 1):
        try:
            r = requests.get(url, impersonate="chrome", timeout=25,
                             headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
            _last = time.time()
            if r.status_code == 200:
                text = r.text
                if cache:
                    cache.parent.mkdir(parents=True, exist_ok=True)
                    cache.write_text(text, encoding="utf-8")
                return text
            last_err = f"HTTP {r.status_code}"
            if r.status_code in (403, 429, 500, 502, 503, 504):
                time.sleep(3 * attempt)
                continue
            break
        except Exception as exc:  # noqa: BLE001
            last_err = str(exc)
            time.sleep(3 * attempt)
    raise RuntimeError(f"{url}: {last_err}")


def parse_ks_list(html: str, ticker: str, page: int) -> list[dict]:
    s = BeautifulSoup(html, "lxml")
    out = []
    for a in s.select("a.announcement-item"):
        h = a.get("href", "")
        m = re.search(r"/announcements/view/(\d+)", h)
        if not m:
            continue
        item = {
            "source_id": m.group(1),
            "url": urljoin("https://www.klsescreener.com", h),
            "day": a.select_one(".day").get_text(strip=True) if a.select_one(".day") else "",
            "month": a.select_one(".month").get_text(strip=True) if a.select_one(".month") else "",
            "time": a.select_one(".time-ago").get_text(strip=True) if a.select_one(".time-ago") else "",
            "category": a.select_one(".category-tag").get_text(strip=True) if a.select_one(".category-tag") else "",
            "title": a.select_one(".title").get_text(" ", strip=True) if a.select_one(".title") else "",
            "snippet": a.select_one(".snippet").get_text(" ", strip=True) if a.select_one(".snippet") else "",
            "ticker": ticker,
            "page": page,
        }
        out.append(item)
    return out


def parse_ks_detail(html: str) -> dict:
    s = BeautifulSoup(html, "lxml")
    title_tag = s.find("title")
    title = title_tag.get_text(strip=True).split(" | ")[0] if title_tag else ""
    text = s.get_text("\n", strip=True)

    def after(label: str) -> str | None:
        lines = [x.strip() for x in text.splitlines()]
        for i, line in enumerate(lines):
            if line == label and i + 1 < len(lines):
                return lines[i + 1].strip()
        return None

    body = ""
    # Description block: between "Description" and "Announcement Info".
    m = re.search(r"\nDescription\n(.*?)\nAnnouncement Info\n", text, re.S)
    if m:
        body = m.group(1).strip()
    bursa = None
    for a in s.find_all("a", href=True):
        if "ann_id=" in a["href"]:
            bursa = a["href"]
            break
    ann_id = None
    if bursa:
        mm = re.search(r"ann_id=(\d+)", bursa)
        if mm:
            ann_id = mm.group(1)
    return {
        "title": title,
        "date_text": after("Date Announced"),
        "category": after("Category"),
        "reference": after("Reference Number"),
        "company": after("Company Name"),
        "stock": after("Stock Name"),
        "body": body,
        "bursa_url": bursa,
        "ann_id": ann_id,
    }


def parse_bursa(html: str) -> dict:
    s = BeautifulSoup(html, "lxml")
    text = s.get_text("\n", strip=True)
    # Body is the largest block in #D_GA_Content / .ck-content.
    body = ""
    node = s.select_one("#D_GA_Content") or s.select_one(".ck-content")
    if node:
        body = node.get_text("\n", strip=True)
    if not body:
        m = re.search(r"\nDescription\n(.*?)\nAnnouncement Info\n", text, re.S)
        body = m.group(1).strip() if m else ""
    attachments = []
    for a in s.find_all("a", href=True):
        href = a["href"]
        if "/FileAccess/apbursaweb/download" in href or "attachment" in href.lower():
            name = a.get_text(" ", strip=True) or unquote(href.split("name=")[-1])
            attachments.append({"name": name, "url": urljoin("https://disclosure.bursamalaysia.com", href)})
    # Announcement info
    info = {}
    for label in ("Company Name", "Stock Name", "Date Announced", "Category", "Reference Number"):
        m = re.search(rf"\n{label}\n([^\n]+)", text)
        if m:
            info[label] = m.group(1).strip()
    return {"body": body, "attachments": attachments, "info": info}


def parse_dt(text: str, time_text: str) -> datetime | None:
    m = re.search(r"(\d{1,2}) ([A-Z][a-z]{2}) (\d{4})", text or "")
    if not m:
        return None
    dt = datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%d %b %Y")
    tm = re.search(r"(\d{1,2}):(\d{2})\s*(am|pm)", (time_text or "").lower())
    if tm:
        hh, mi, ap = int(tm.group(1)), int(tm.group(2)), tm.group(3)
        if ap == "pm" and hh != 12:
            hh += 12
        if ap == "am" and hh == 12:
            hh = 0
        dt = dt.replace(hour=hh, minute=mi)
    return dt.replace(tzinfo=MYT)


def safe_name(name: str, maxlen: int = 80) -> str:
    name = unquote(name)
    name = re.sub(r"[^\w.\- ]+", "_", name).strip().replace(" ", "_")
    return name[:maxlen] or "attachment"


def fetch_attachment(url: str, dest: Path) -> dict | None:
    global _last
    if dest.exists() and dest.stat().st_size > 1000:
        return {"file": str(dest.relative_to(ROOT)), "bytes": dest.stat().st_size,
                "sha256": sha256(dest), "pages": pdf_pages(dest)}
    wait = 1.15 - (time.time() - _last)
    if wait > 0:
        time.sleep(wait)
    try:
        r = requests.get(url, impersonate="chrome", timeout=30, headers={"User-Agent": UA})
        _last = time.time()
        if r.status_code == 200 and r.content.startswith(b"%PDF"):
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(r.content)
            return {"file": str(dest.relative_to(ROOT)), "bytes": len(r.content),
                    "sha256": sha256(dest), "pages": pdf_pages(dest)}
    except Exception:  # noqa: BLE001
        pass
    return None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_pages(path: Path) -> int:
    try:
        from pypdf import PdfReader
        return len(PdfReader(str(path)).pages)
    except Exception:  # noqa: BLE001
        return 0


NO_ATTACHMENT_CATEGORIES = (
    "changes in shareholdings", "change in the interest of subs",
    "changes in director's interest", "dealings in listed securities",
    "change in boardroom", "change in audit committee", "change in risk committee",
    "change in remuneration committee", "change in nomination committee",
    "listing circulars", "notice of book closure", "special dividend",
)


def collect(tickers: list[str], pages: int, delay: float = 1.15, start_page: int = 1) -> list[dict]:
    global _last
    PAGEDIR.mkdir(parents=True, exist_ok=True)
    PDFDIR.mkdir(parents=True, exist_ok=True)
    MAN.mkdir(parents=True, exist_ok=True)

    all_items = []
    for code in tickers:
        ticker, company = TICKERS[code]
        for page in range(start_page, pages + 1):
            url = f"https://www.klsescreener.com/v2/announcements/stock/{code}?page={page}"
            cache = PAGEDIR / f"ks_list_{ticker}_p{page}.html"
            print(f"LIST {ticker} p{page}", flush=True)
            html = polite_get(url, cache)
            items = parse_ks_list(html, ticker, page)
            print(f"  {len(items)} items", flush=True)
            if not items:
                break
            for it in items:
                it["code"] = code
                it["company"] = company
            all_items.extend(items)

    # Deduplicate by KS id
    seen = {}
    for it in all_items:
        seen[it["source_id"]] = it
    all_items = list(seen.values())

    records = []
    for i, it in enumerate(all_items, 1):
        ticker = it["ticker"]
        detail_url = it["url"]
        cache = PAGEDIR / f"ks_detail_{it['source_id']}.html"
        try:
            html = polite_get(detail_url, cache)
            d = parse_ks_detail(html)
        except Exception as exc:  # noqa: BLE001
            print(f"[{i}/{len(all_items)}] detail failed {detail_url}: {exc}", flush=True)
            continue
        dt = parse_dt(d.get("date_text"), it.get("time"))
        if not dt:
            print(f"[{i}/{len(all_items)}] no date {detail_url}", flush=True)
            continue
        if dt < START or dt > END:
            continue

        rec = {
            "source": "bursa_filing",
            "record_type": "announcement",
            "ticker": ticker,
            "company": it["company"],
            "native_id": f"bursa:{d.get('ann_id')}" if d.get("ann_id") else f"ks:{it['source_id']}",
            "created_utc": int(dt.timestamp()),
            "created_myt": dt.isoformat(),
            "date": dt.strftime("%Y-%m-%d"),
            "time": it.get("time"),
            "category": d.get("category") or it.get("category"),
            "title": re.sub(r"^(GENTING|GENM)\s*-\s*", "", d.get("title") or it.get("title") or ""),
            "body": d.get("body") or it.get("snippet") or "",
            "url": d.get("bursa_url") or detail_url,
            "ks_url": detail_url,
            "reference": d.get("reference"),
            "ann_id": d.get("ann_id"),
            "attachments": [],
            "raw": {
                "category": d.get("category") or it.get("category"),
                "attachment_url": None,
                "ks_id": it["source_id"],
                "ks_page": it["page"],
                "snippet": it.get("snippet"),
                "title_full": d.get("title") or it.get("title"),
            },
        }

        # Routine shareholding notices never carry an attachment; the mirror's
        # body is complete, so skip the extra Bursa request for them.
        cat_l = (rec["category"] or "").lower()
        skip_bursa = any(x in cat_l for x in NO_ATTACHMENT_CATEGORIES)

        # Official Bursa page: body + attachments.
        if d.get("ann_id") and not skip_bursa:
            bhtml = polite_get(
                f"https://disclosure.bursamalaysia.com/FileAccess/viewHtml?e={d['ann_id']}",
                PAGEDIR / f"bursa_{d['ann_id']}.html",
            )
            b = parse_bursa(bhtml)
            if b["body"] and len(b["body"]) > len(rec["body"]):
                rec["body"] = b["body"]
            for j, att in enumerate(b["attachments"], 1):
                name = safe_name(att["name"])
                dest = PDFDIR / f"{d['ann_id']}_{j}_{name}"
                if not dest.suffix.lower() == ".pdf":
                    dest = dest.with_suffix(".pdf")
                info = fetch_attachment(att["url"], dest)
                if info:
                    info["name"] = att["name"]
                    info["url"] = att["url"]
                    rec["attachments"].append(info)
            if rec["attachments"]:
                rec["raw"]["attachment_url"] = rec["attachments"][0]["url"]

        records.append(rec)
        print(f"[{i}/{len(all_items)}] {ticker} {dt.date()} {rec['category'][:30]} | {rec['title'][:60]} | att={len(rec['attachments'])}", flush=True)

    records.sort(key=lambda r: (r["ticker"], r["created_utc"]))
    return records


def write_outputs(records: list[dict], append: bool = False) -> None:
    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    if append and OUT_JSONL.exists():
        merged = {}
        for line in OUT_JSONL.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                merged[r.get("native_id") or r.get("ks_url")] = r
        for r in records:
            merged[r.get("native_id") or r.get("ks_url")] = r
        records = sorted(merged.values(), key=lambda r: (r["ticker"], r["created_utc"]))
    with OUT_JSONL.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    fields = ["ticker", "company", "date", "time", "created_utc", "category", "title",
              "ann_id", "reference", "url", "ks_url", "body_chars", "attachments", "attachment_files"]
    with MANIFEST.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in records:
            w.writerow({
                "ticker": r["ticker"], "company": r["company"], "date": r["date"],
                "time": r["time"], "created_utc": r["created_utc"],
                "category": r["category"], "title": r["title"], "ann_id": r["ann_id"],
                "reference": r["reference"], "url": r["url"], "ks_url": r["ks_url"],
                "body_chars": len(r["body"] or ""),
                "attachments": len(r["attachments"]),
                "attachment_files": ";".join(a["file"] for a in r["attachments"]),
            })
    print(f"wrote {OUT_JSONL} ({len(records)} records)")
    print(f"wrote {MANIFEST}")


def collect_i3(tickers: list[str]) -> None:
    """i3investor only exposes ~100 latest announcements; save as cross-check."""
    recs = []
    for code in tickers:
        ticker = TICKERS[code][0]
        url = f"https://klse.i3investor.com/web/stock/announcement/{code}"
        cache = PAGEDIR / f"i3_list_{ticker}.html"
        print(f"I3 LIST {ticker}", flush=True)
        html = polite_get(url, cache)
        m = re.search(r"const dtdata = (\[\[.*?\]\]);", html, re.S)
        if not m:
            print("  no dtdata", flush=True)
            continue
        try:
            data = json.loads(m.group(1))
        except Exception as exc:  # noqa: BLE001
            print("  bad dtdata", exc, flush=True)
            continue
        for date_s, title_html in data:
            tm = re.search(r"/web/announcement/detail/(\d+)", title_html)
            title = BeautifulSoup(title_html, "lxml").get_text(" ", strip=True)
            recs.append({
                "source": "i3investor", "record_type": "announcement", "ticker": ticker,
                "native_id": tm.group(1) if tm else None,
                "date": date_s, "title": title,
                "url": f"https://klse.i3investor.com/web/announcement/detail/{tm.group(1)}" if tm else url,
                "created_utc": int(datetime.strptime(date_s, "%Y-%m-%d").replace(tzinfo=MYT).timestamp()),
                "raw": {},
            })
        print(f"  {len(data)} items", flush=True)
    with OUT_I3.open("w", encoding="utf-8") as fh:
        for r in recs:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {OUT_I3} ({len(recs)} records)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=8)
    ap.add_argument("--tickers", default="3182,4715")
    ap.add_argument("--i3", action="store_true")
    ap.add_argument("--start-page", type=int, default=1)
    ap.add_argument("--append", action="store_true")
    args = ap.parse_args()
    tickers = [t.strip() for t in args.tickers.split(",") if t.strip()]
    if args.i3:
        collect_i3(tickers)
    else:
        records = collect(tickers, args.pages, start_page=args.start_page)
        write_outputs(records, append=args.append)


if __name__ == "__main__":
    main()
