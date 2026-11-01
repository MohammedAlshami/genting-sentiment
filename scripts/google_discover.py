#!/usr/bin/env python3
"""Discover public post URLs with Google (browser) and resolve redirects.

Usage: xvfb-run -a python3 scripts/google_discover.py OUT.json QUERY [QUERY...]

Google is queried in a real logged-out browser (no account, no captcha solving).
Result links are Google /goto?url= redirects; those are resolved with plain
HTTP HEAD/GET without following into the target page.
"""
from __future__ import annotations

import asyncio
import json
import sys
import urllib.parse
from pathlib import Path

import nodriver as uc
from curl_cffi import requests


def resolve(href: str) -> str | None:
    if not href:
        return None
    if href.startswith("https://www.google.com/goto?url="):
        try:
            r = requests.get(href, impersonate="chrome", timeout=20, allow_redirects=False)
            loc = r.headers.get("location")
            if loc:
                return loc
        except Exception:
            return None
    if href.startswith("http") and "google.com" not in href:
        return href
    return None


async def main() -> int:
    out = Path(sys.argv[1])
    queries = sys.argv[2:]
    browser = await uc.start(
        headless=False,
        browser_args=["--no-sandbox", "--disable-dev-shm-usage", "--window-size=1400,1000", "--lang=en-US"],
    )
    results: list[dict] = []
    try:
        page = await browser.get("https://www.google.com/ncr")
        await page.sleep(2)
        for query in queries:
            url = "https://www.google.com/search?hl=en&num=30&q=" + urllib.parse.quote(query)
            await page.get(url)
            await page.sleep(4)
            title = await page.evaluate("document.title")
            body = await page.evaluate("document.body.innerText") or ""
            if isinstance(body, dict):
                body = str(body)
            print(f"\n=== {query}\nTITLE: {title}")
            if "unusual traffic" in str(body).lower() or "captcha" in str(body).lower():
                print("CHALLENGE - stopping")
                break
            js = (
                "JSON.stringify(Array.from(document.querySelectorAll('a'))"
                ".filter(a => a.href.includes('/goto?url=') || a.href.includes('http'))"
                ".map(a => a.href + '\\t' + (a.innerText||'').replace(/\\s+/g,' ').trim()))"
            )
            raw = await page.evaluate(js)
            if isinstance(raw, dict):
                raw = raw.get("value", "[]")
            try:
                rows = json.loads(raw or "[]")
            except Exception:
                rows = []
            seen: set[str] = set()
            count = 0
            for row in rows:
                href, _, text = str(row).partition("\t")
                if "/goto?url=" not in href:
                    continue
                target = resolve(href)
                if not target or target in seen:
                    continue
                seen.add(target)
                results.append({"query": query, "url": target, "title": text, "engine": "google"})
                count += 1
                print(target, "|", text[:110])
            print("resolved:", count)
            await page.sleep(3)
    finally:
        browser.stop()
        out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nwrote {out} ({len(results)} urls)")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
