#!/usr/bin/env python3
"""Probe several public URLs in one browser session, politely.

Usage: xvfb-run -a python3 scripts/social_probe_multi.py OUTDIR WAIT URL [URL...]
Saves <n>.html / <n>.txt and prints visible-text previews.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import nodriver as uc


async def main() -> int:
    outdir = Path(sys.argv[1])
    wait = float(sys.argv[2])
    urls = sys.argv[3:]
    outdir.mkdir(parents=True, exist_ok=True)

    browser = await uc.start(
        headless=False,
        browser_args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--window-size=1400,1000",
            "--lang=en-US",
        ],
    )
    try:
        page = await browser.get("about:blank")
        for i, url in enumerate(urls, 1):
            try:
                await page.get(url)
                await page.sleep(wait)
                html = await page.get_content()
                text = await page.evaluate("document.body.innerText") or ""
                (outdir / f"{i:02d}.html").write_text(html, encoding="utf-8")
                (outdir / f"{i:02d}.txt").write_text(text, encoding="utf-8")
                title = await page.evaluate("document.title")
                print(f"\n=== [{i}] {url}\nFINAL: {page.url}\nTITLE: {title}\nHTML={len(html)} TEXT={len(text)}")
                print(text[:1200])
            except Exception as exc:
                print(f"\n=== [{i}] {url}\nERROR: {exc!r}")
            await page.sleep(3)
    finally:
        browser.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
