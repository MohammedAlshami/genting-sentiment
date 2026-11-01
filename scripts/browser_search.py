#!/usr/bin/env python3
"""Run a web search in a real browser and print result links.

Usage: xvfb-run -a python3 scripts/browser_search.py "query" [engine]
Engines: bing (default), google, yahoo.
No login, no captcha solving; if a challenge appears it is reported and left alone.
"""
from __future__ import annotations

import asyncio
import sys
import urllib.parse

import nodriver as uc


async def main() -> int:
    query = sys.argv[1]
    engine = sys.argv[2] if len(sys.argv) > 2 else "bing"
    if engine == "google":
        url = "https://www.google.com/search?hl=en&num=30&q=" + urllib.parse.quote(query)
        sel = "a"
    elif engine == "yahoo":
        url = "https://search.yahoo.com/search?p=" + urllib.parse.quote(query)
        sel = "a"
    else:
        url = "https://www.bing.com/search?setlang=en&count=30&q=" + urllib.parse.quote(query)
        sel = "li.b_algo h2 a"

    browser = await uc.start(
        headless=False,
        browser_args=["--no-sandbox", "--disable-dev-shm-usage", "--window-size=1400,1000", "--lang=en-US"],
    )
    try:
        page = await browser.get(url)
        await page.sleep(4)
        text = await page.evaluate("document.body.innerText") or ""
        print("FINAL:", page.url)
        print("TITLE:", await page.evaluate("document.title"))
        if any(x in text.lower() for x in ("captcha", "unusual traffic", "verify you are human")):
            print("CHALLENGE DETECTED")
            print(text[:500])
            return 2
        js = (
            "JSON.stringify(Array.from(document.querySelectorAll(" + repr(sel) + "))"
            ".map(a => a.href + '\\t' + (a.innerText||'').replace(/\\s+/g,' ').trim()))"
        )
        try:
            raw = await page.evaluate(js)
        except Exception as exc:
            print("eval failed", exc)
            raw = "[]"
        if isinstance(raw, dict):
            raw = raw.get("value", "[]")
        if not isinstance(raw, str):
            raw = str(raw)
        try:
            import json as _json

            rows = _json.loads(raw)
        except Exception:
            rows = []
        links = []
        for row in rows or []:
            href, _, title = str(row).partition("\t")
            links.append({"h": href, "t": title})
        for item in links[:40]:
            print(item["h"], "|", item["t"][:120])
        print("COUNT", len(links))
    finally:
        browser.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
