#!/usr/bin/env python3
"""Stage 3: fetch each article, extract full text, cache the result."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests as cffi_requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from news_lib import (  # noqa: E402
    CACHE,
    canonical_url,
    clean_text,
    http_get,
    jsonld_objects,
    meta_content,
    parse_pubdate,
    sha1,
    strip_tags,
)

ARTICLE_CACHE = CACHE / "articles"
ARTICLE_CACHE.mkdir(parents=True, exist_ok=True)

SKIP_URL = re.compile(
    r"/(quote|seasonality|chart|charts|marketwatch|stocks?)(/|\?|$)"
    r"|finance\.yahoo\.com/quote/"
    r"|/v2/comment/",
    re.I,
)

BOILERPLATE_LINES = {
    "already a subscriber? log in",
    "get 20% off the star digital access",
    "cancel anytime. ad-free. unlimited access with perks.",
    "thank you for your report!",
    "follow us on our official whatsapp channel for breaking news alerts and key updates!",
    "subscribe now",
    "live",
    "advertisement",
    "download and unlock more today",
    "share this article",
    "read more",
}


def strip_boilerplate(body: str) -> str:
    lines = []
    for ln in body.split("\n"):
        s = ln.strip()
        if s.lower() in BOILERPLATE_LINES:
            continue
        if s.lower().startswith("already a subscriber"):
            continue
        if s.lower().startswith("get 20% off the star digital access"):
            continue
        lines.append(ln)
    return clean_text("\n".join(lines))


def page_variant(url: str, domain: str) -> str:
    """Publisher-specific URL variant that serves the public full text."""
    if "thestar.com.my" in domain:
        sep = "&" if "?" in url else "?"
        return url + sep + "s=app"
    return url


def extract_trafilatura(html_text: str, url: str) -> str | None:
    try:
        import trafilatura

        txt = trafilatura.extract(
            html_text,
            url=url,
            include_comments=False,
            include_tables=False,
            include_links=False,
            include_images=False,
            deduplicate=True,
        )
        return clean_text(txt) if txt else None
    except Exception:
        return None


def extract_readability(html_text: str) -> str | None:
    try:
        from readability import Document

        doc = Document(html_text)
        txt = strip_tags(doc.summary())
        return txt if txt else None
    except Exception:
        return None


def extract_bs4(html_text: str) -> str | None:
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_text, "lxml")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form", "noscript"]):
            tag.decompose()
        node = soup.find("article")
        if node is None:
            for sel in ("div.article-content", "div.article-body", "div.story", "div.content", "main"):
                node = soup.select_one(sel)
                if node:
                    break
        node = node or soup.body or soup
        txt = clean_text(node.get_text("\n"))
        return txt if len(txt) > 250 else None
    except Exception:
        return None


def get_title(html_text: str) -> str | None:
    for key in ("og:title", "twitter:title"):
        v = meta_content(html_text, key)
        if v:
            return clean_text(v)
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html_text, re.S | re.I)
    if m:
        t = strip_tags(m.group(1))
        if t:
            return t
    m = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.S | re.I)
    return clean_text(strip_tags(m.group(1))) if m else None


def get_author(html_text: str) -> str | None:
    v = meta_content(html_text, "author", "article:author", "parsely-author", "sailthru.author")
    if v:
        v = re.sub(r"^By\s+", "", v.strip(), flags=re.I)
        if v and not v.lower().startswith(("http", "www.")):
            return v
    for obj in jsonld_objects(html_text):
        a = obj.get("author")
        if isinstance(a, dict):
            a = a.get("name")
        if isinstance(a, list) and a:
            a = a[0].get("name") if isinstance(a[0], dict) else a[0]
        if isinstance(a, str) and a.strip():
            return a.strip()
    return None


def get_published(html_text: str) -> int | None:
    for key in (
        "article:published_time",
        "article:published",
        "datePublished",
        "date",
        "pubdate",
        "publish-date",
        "parsely-pub-date",
        "sailthru.date",
        "DC.date.issued",
    ):
        v = meta_content(html_text, key)
        if v:
            dt = parse_pubdate(v)
            if dt:
                return int(dt.timestamp())
    for obj in jsonld_objects(html_text):
        for key in ("datePublished", "dateCreated", "dateModified"):
            v = obj.get(key)
            if isinstance(v, str):
                dt = parse_pubdate(v)
                if dt:
                    return int(dt.timestamp())
    for m in re.finditer(r'<time[^>]+datetime=["\']([^"\']+)["\']', html_text, re.I):
        dt = parse_pubdate(m.group(1))
        if dt:
            return int(dt.timestamp())
    return None


PAYWALL_MARKERS = re.compile(
    r"subscribe to (continue|read)|subscriber[- ]only|premium content|for subscribers"
    r"|sign in to (continue|read)|already a subscriber|paywall|to continue reading"
    r"|this article is (exclusive|available) to",
    re.I,
)


def fetch_one(session: cffi_requests.Session, url: str, google_pub: int | None) -> dict:
    cp = ARTICLE_CACHE / f"{sha1(url)}.json"
    if cp.exists():
        return json.loads(cp.read_text())
    domain = urllib.parse.urlsplit(url).netloc
    rec = {
        "url": url,
        "final_url": url,
        "http_status": None,
        "title": None,
        "author": None,
        "published_utc": None,
        "body": None,
        "extractor": None,
        "paywalled": False,
    }
    if SKIP_URL.search(url):
        rec["skip_reason"] = "utility_page"
        cp.write_text(json.dumps(rec, ensure_ascii=False))
        return rec
    r = http_get(page_variant(url, domain), session=session, timeout=45, tries=3)
    if r is None:
        rec["skip_reason"] = "fetch_failed"
        cp.write_text(json.dumps(rec, ensure_ascii=False))
        return rec
    rec["http_status"] = r.status_code
    rec["final_url"] = r.url
    if r.status_code >= 400:
        rec["skip_reason"] = f"http_{r.status_code}"
        cp.write_text(json.dumps(rec, ensure_ascii=False))
        return rec
    html_text = r.text
    rec["title"] = get_title(html_text)
    rec["author"] = get_author(html_text)
    rec["published_utc"] = get_published(html_text)
    body = extract_trafilatura(html_text, url)
    if body and len(body) >= 350:
        rec["extractor"] = "trafilatura"
    else:
        alt = extract_readability(html_text)
        if alt and len(alt) > len(body or ""):
            body, rec["extractor"] = alt, "readability"
        alt = extract_bs4(html_text)
        if alt and len(alt) > len(body or ""):
            body, rec["extractor"] = alt, "bs4"
    # NST is JS-heavy on the canonical page; the AMP page carries the full body.
    if "nst.com.my" in domain and (
        len(body or "") < 700 or not re.search(r"genting|kuala lumpur", body or "", re.I)
    ):
        m = re.search(r'<link[^>]+rel=["\']amphtml["\'][^>]+href=["\']([^"\']+)', html_text, re.I)
        alt_url = m.group(1) if m else None
        if not alt_url and "/amp/" not in url:
            parts = urllib.parse.urlsplit(url)
            alt_url = urllib.parse.urlunsplit(
                (parts.scheme, parts.netloc, "/amp" + parts.path, parts.query, "")
            )
        if alt_url:
            r2 = http_get(alt_url, session=session, timeout=45, tries=2)
            if r2 is not None and r2.status_code == 200:
                alt = extract_trafilatura(r2.text, alt_url) or extract_bs4(r2.text)
                if alt and len(alt) > len(body or ""):
                    body, rec["extractor"] = alt, "trafilatura_amp"
    body = strip_boilerplate(clean_text(body or ""))
    text_l = html_text.lower()
    if len(body) < 700 and PAYWALL_MARKERS.search(text_l[-250000:]):
        rec["paywalled"] = True
    if body and PAYWALL_MARKERS.search(body[-1200:]):
        rec["paywalled"] = True
    rec["body"] = body or None
    cp.write_text(json.dumps(rec, ensure_ascii=False))
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--discovery", type=Path, default=CACHE / "discovery.json")
    ap.add_argument("--resolved", type=Path, default=CACHE / "resolved.json")
    ap.add_argument("--out", type=Path, default=CACHE / "fetched.json")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    items = json.loads(args.discovery.read_text())
    state = json.loads(args.resolved.read_text())
    by_url: dict[str, dict] = {}
    for it in items:
        u = state.get(it["google_url"])
        if not u:
            continue
        cu = canonical_url(u)
        if cu in by_url:
            continue
        it = dict(it)
        it["url"] = cu
        by_url[cu] = it
    cands = list(by_url.values())
    cands.sort(key=lambda x: urllib.parse.urlsplit(x["url"]).netloc)
    if args.limit:
        cands = cands[: args.limit]
    print(f"{len(cands)} candidate URLs")

    session = cffi_requests.Session()
    last_hit: dict[str, float] = {}
    out = []
    t0 = time.time()
    for i, it in enumerate(cands, 1):
        domain = urllib.parse.urlsplit(it["url"]).netloc
        wait = 1.15 - (time.time() - last_hit.get(domain, 0))
        if wait > 0:
            time.sleep(wait)
        rec = fetch_one(session, it["url"], it.get("published_utc"))
        last_hit[domain] = time.time()
        rec = dict(rec)
        rec["google_title"] = it.get("title")
        rec["google_source"] = it.get("source")
        rec["google_published_utc"] = it.get("published_utc")
        rec["google_url"] = it.get("google_url")
        out.append(rec)
        if i % 20 == 0 or i == len(cands):
            print(f"  [{i}/{len(cands)}] {time.time()-t0:.0f}s", flush=True)
            args.out.write_text(json.dumps(out, ensure_ascii=False))
    args.out.write_text(json.dumps(out, ensure_ascii=False))
    ok = sum(1 for r in out if r.get("body"))
    short = sum(1 for r in out if r.get("body") and len(r["body"]) < 500)
    print(f"done: {ok} with body, {short} short, {sum(1 for r in out if r.get('paywalled'))} paywalled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
