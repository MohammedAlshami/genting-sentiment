#!/usr/bin/env python3
"""Probe one public URL with a real (Xvfb) browser and dump HTML + visible text.

Usage: xvfb-run -a python3 scripts/social_probe.py URL OUTSTEM [wait_seconds]
No cookies, no login. Used only to establish what logged-out visitors can see.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import nodriver as uc


async def main() -> int:
    url = sys.argv[1]
    stem = Path(sys.argv[2])
    wait = float(sys.argv[3]) if len(sys.argv) > 3 else 6.0

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
        page = await browser.get(url)
        await page.sleep(wait)
        html = await page.get_content()
        stem.with_suffix(".html").write_text(html, encoding="utf-8")
        try:
            text = await page.evaluate("document.body.innerText")
        except Exception:
            text = ""
        stem.with_suffix(".txt").write_text(text or "", encoding="utf-8")
        print("URL:", page.url)
        print("TITLE:", await page.evaluate("document.title"))
        print("HTML:", len(html), "TEXT:", len(text or ""))
        print((text or "")[:3000])
    finally:
        browser.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
