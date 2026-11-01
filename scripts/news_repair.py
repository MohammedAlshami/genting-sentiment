#!/usr/bin/env python3
"""Stage 3c: second pass for pages that served a truncated first response."""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

from curl_cffi import requests as cffi_requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from news_fetch import (  # noqa: E402
    extract_bs4,
    extract_readability,
    extract_trafilatura,
    get_author,
    get_published,
    get_title,
    strip_boilerplate,
)
from news_lib import CACHE, clean_text, http_get, sha1  # noqa: E402

FETCHED = CACHE / "fetched.json"
ARTICLE_CACHE = CACHE / "articles"


def extract(html_text: str, url: str) -> tuple[str | None, str | None]:
    body = extract_trafilatura(html_text, url)
    ex = "trafilatura" if body and len(body) >= 350 else None
    if not ex:
        alt = extract_readability(html_text)
        if alt and len(alt) > len(body or ""):
            body, ex = alt, "readability"
        alt = extract_bs4(html_text)
        if alt and len(alt) > len(body or ""):
            body, ex = alt, "bs4"
    return (strip_boilerplate(clean_text(body or "")) or None), ex


def main() -> int:
    recs = json.loads(FETCHED.read_text())
    session = cffi_requests.Session()
    targets = [
        r for r in recs
        if "thestar.com.my" in r["url"] and not r["url"].startswith("https://charts.")
    ]
    print(f"refetching {len(targets)} Star articles")
    improved = 0
    for i, r in enumerate(targets, 1):
        url = r["url"]
        sep = "&" if "?" in url else "?"
        variant = url + sep + "s=app&r=2"
        resp = http_get(variant, session=session, timeout=45, tries=2)
        if resp is not None and resp.status_code == 200:
            body, ex = extract(resp.text, url)
            if body and len(body) > len(r.get("body") or ""):
                r["body"] = body
                r["extractor"] = ex
                r["paywalled"] = bool(
                    re.search(r"already a subscriber|subscribe to continue", body[-800:], re.I)
                )
                improved += 1
                (ARTICLE_CACHE / f"{sha1(url)}.json").write_text(
                    json.dumps(
                        {
                            "url": url,
                            "final_url": url,
                            "http_status": 200,
                            "title": get_title(resp.text) or r.get("title"),
                            "author": get_author(resp.text) or r.get("author"),
                            "published_utc": get_published(resp.text) or r.get("published_utc"),
                            "body": body,
                            "extractor": ex,
                            "paywalled": r["paywalled"],
                        },
                        ensure_ascii=False,
                    )
                )
        if i % 20 == 0:
            print(f"  {i}/{len(targets)} improved={improved}", flush=True)
        time.sleep(1.15)
    FETCHED.write_text(json.dumps(recs, ensure_ascii=False))
    print(f"improved {improved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
