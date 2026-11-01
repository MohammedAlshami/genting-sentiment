#!/usr/bin/env python3
"""Collect Bursa announcements for GENTING (3182) / GENM (4715) via KLSE Screener.

Saves raw HTML under data/raw/cache/company_events/ and a parsed JSON index
(data/raw/cache/company_events/announcements.json) with full announcement text.

The site paginates 30 items/page but page order is not strictly chronological;
we walk enough pages to pass 2024-11-02 and filter on the "Date Announced" field
in each detail page.
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data/raw/cache/company_events"
CACHE.mkdir(parents=True, exist_ok=True)

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept-Language": "en-MY,en;q=0.9"})
BASE = "https://www.klsescreener.com"


def get(url: str, cache: Path, sleep: float = 1.0) -> str:
    if cache.exists() and cache.stat().st_size > 2000:
        return cache.read_text(encoding="utf-8", errors="replace")
    last = None
    for attempt in range(4):
        try:
            r = S.get(url, timeout=40)
            if r.status_code == 200 and len(r.text) > 2000:
                cache.write_text(r.text, encoding="utf-8")
                time.sleep(sleep)
                return r.text
            last = f"HTTP {r.status_code}"
        except Exception as exc:  # noqa: BLE001
            last = repr(exc)
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"failed {url}: {last}")


def strip_html(fragment: str) -> str:
    s = re.sub(r"<script.*?</script>", " ", fragment, flags=re.S | re.I)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</(p|tr|div|h\d|li|table)>", "\n", s, flags=re.I)
    s = re.sub(r"</t[dh]>", " | ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = (
        s.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&#39;", "'")
        .replace("&quot;", '"')
        .replace("&rsquo;", "'")
        .replace("&ldquo;", '"')
        .replace("&rdquo;", '"')
    )
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def parse_list(html: str) -> list[dict]:
    out = []
    for m in re.finditer(
        r'<a href="(/v2/announcements/view/(\d+))"[^>]*class="announcement-item">(.*?)</a>',
        html,
        re.S,
    ):
        blk = m.group(3)
        d = re.search(r'<span class="day">(\d+)</span>\s*<span class="month">(\w+)</span>', blk)
        cat = re.search(r'<span class="category-tag[^"]*">([^<]+)</span>', blk)
        title = re.search(r'<div class="title">(.*?)</div>', blk, re.S)
        snip = re.search(r'<div class="snippet">(.*?)</div>', blk, re.S)
        out.append(
            {
                "id": m.group(2),
                "url": BASE + m.group(1),
                "day": int(d.group(1)) if d else None,
                "month": d.group(2) if d else None,
                "category": strip_html(cat.group(1)) if cat else None,
                "title": strip_html(title.group(1)) if title else None,
                "snippet": strip_html(snip.group(1)) if snip else "",
            }
        )
    return out


def parse_detail(html: str, meta: dict) -> dict:
    rec = dict(meta)
    # Announcement HTML lives inside <div id="main" class="table-responsive">.
    i = html.find('<div id="main" class="table-responsive">')
    j = html.find('<div class="ven_announcement_info">')
    body_html = html[i:j] if i != -1 and j != -1 else html
    rec["body"] = strip_html(body_html)
    date = re.search(r"Date Announced</td>\s*<td[^>]*>\s*([^<]+)</td>", html, re.I)
    if not date:
        date = re.search(r"Date Announced.*?(\d{1,2} \w{3} \d{4})", strip_html(html), re.S)
    rec["date_announced"] = date.group(1).strip() if date else None
    ref = re.search(r"Reference Number</td>\s*<td[^>]*>\s*([^<]+)</td>", html, re.I)
    rec["reference"] = ref.group(1).strip() if ref else None
    orig = re.search(r'href="([^"]*bursamalaysia\.com[^"]*ann_id=\d+[^"]*)"', html)
    rec["bursa_url"] = orig.group(1) if orig else None
    rec["attachments"] = [
        {"name": strip_html(n), "url": BASE + u}
        for u, n in re.findall(
            r"<a href='(/FileAccess/apbursaweb/download\?[^']+)'>\s*(.*?)</a>", html, re.S
        )
    ]
    return rec


def main() -> None:
    all_items: list[dict] = []
    for code, pages in (("3182", 9), ("4715", 12)):
        seen: set[str] = set()
        for page in range(1, pages + 1):
            url = f"{BASE}/v2/announcements/stock/{code}?page={page}"
            html = get(url, CACHE / f"list_{code}_{page}.html")
            items = parse_list(html)
            print(f"{code} page {page}: {len(items)} items", flush=True)
            for it in items:
                if it["id"] in seen:
                    continue
                seen.add(it["id"])
                it["code"] = code
                all_items.append(it)
    print(f"unique list items: {len(all_items)}", flush=True)

    detailed = []
    for n, it in enumerate(all_items, 1):
        cache = CACHE / f"detail_{it['id']}.html"
        html = get(it["url"], cache)
        rec = parse_detail(html, it)
        detailed.append(rec)
        if n % 20 == 0:
            print(f"detail {n}/{len(all_items)} {rec['date_announced']} {rec['title'][:60]}", flush=True)

    out = CACHE / "announcements.json"
    out.write_text(json.dumps(detailed, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {out} ({len(detailed)} records)")


if __name__ == "__main__":
    main()
