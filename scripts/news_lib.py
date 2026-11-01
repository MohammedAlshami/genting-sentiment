"""Shared helpers for the Genting news collector."""

from __future__ import annotations

import hashlib
import html
import json
import re
import time
import unicodedata
import urllib.parse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from curl_cffi import requests as cffi_requests

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "raw"
CACHE = DATA / "cache"
CACHE.mkdir(parents=True, exist_ok=True)

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

# Window: 2 Nov 2025 -> 2 Nov 2026 inclusive (Malaysian local dates).
WINDOW_START = datetime(2025, 11, 2, 0, 0, tzinfo=timezone.utc)
WINDOW_END = datetime(2026, 11, 3, 0, 0, tzinfo=timezone.utc)

MALAYSIAN_PUBLISHERS = {
    "the edge malaysia",
    "the star",
    "new straits times",
    "nst online",
    "malaysian reserve",
    "the malaysian reserve",
    "focus malaysia",
    "bernama",
    "the sun",
    "malay mail",
    "free malaysia today",
    "klse screener",
    "the malaysian insight",
    "malaysiakini",
    "the rakyat post",
    "the vibes",
    "edgeprop",
    "the business times",
    "the borneo post",
    "dayak daily",
    "sinar daily",
    "sinar harian",
    "berita harian",
    "harian metro",
    "utusan malaysia",
    "the star online",
    "thestar",
    "astro awani",
    "tv3",
    "bfm",
    "the malaysia reserve",
}

# Entity patterns that indicate the article is really about the two companies.
GENTING_STRONG = re.compile(
    r"\bgenting\s+(berhad|bhd)\b"
    r"|\bgenting\s+malaysia\b"
    r"|\bgenm\b"
    r"|\b3182\b"
    r"|\b4715\b"
    r"|\bgenting\s+group\b"
    r"|\bgenting\s+conglomerate\b",
    re.I,
)
GENTING_WEAK = re.compile(r"\bgenting\b", re.I)
GENM_OPS = re.compile(
    r"resorts?\s+world\s+genting|genting\s+highlands|resorts?\s+world\s+new\s+york"
    r"|genting\s+new\s+york|rwgt|rw\s+genting",
    re.I,
)
# Things that are about the place, not the company.
TRAVEL = re.compile(
    r"things to do|travel guide|hotel review|staycation|day trip|weekend getaway"
    r"|listicle|where to eat|what to eat|tourist attraction|holiday guide",
    re.I,
)
MARKET_ROUNDUP = re.compile(
    r"^(bursa|klse|market|stocks?|equities|wall street|asia stocks|morning brief|closing bell)"
    r"|top gainers|top losers|market close|market open|stock market today|taking stock",
    re.I,
)


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def cache_path(name: str, key: str, ext: str) -> Path:
    d = CACHE / name
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{sha1(key)}{ext}"


def http_get(
    url: str,
    *,
    session: cffi_requests.Session | None = None,
    timeout: int = 40,
    tries: int = 3,
    headers: dict | None = None,
    allow_redirects: bool = True,
) -> cffi_requests.Response | None:
    """GET with browser impersonation and exponential backoff on 429/5xx."""
    s = session or cffi_requests
    hdrs = {"Accept-Language": "en-MY,en;q=0.9,ms;q=0.8", "User-Agent": UA}
    if headers:
        hdrs.update(headers)
    last = None
    for attempt in range(tries):
        try:
            r = s.get(
                url,
                impersonate="chrome",
                timeout=timeout,
                headers=hdrs,
                allow_redirects=allow_redirects,
            )
            if r.status_code in (429, 500, 502, 503, 504):
                last = r
                time.sleep(2 ** attempt * 2)
                continue
            return r
        except Exception as exc:  # network errors
            last = exc
            time.sleep(2 ** attempt * 2)
    if isinstance(last, Exception):
        print(f"    GET failed {url}: {last}")
    elif last is not None:
        print(f"    GET {url}: HTTP {last.status_code}")
    return None


def parse_pubdate(text: str | None) -> datetime | None:
    if not text:
        return None
    try:
        dt = parsedate_to_datetime(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(text.strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            continue
    return None


def clean_text(text: str) -> str:
    text = html.unescape(text or "")
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u00a0", " ").replace("\u200b", "")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [ln.strip() for ln in text.split("\n")]
    return "\n".join(lines).strip()


def canonical_url(url: str) -> str:
    if not url:
        return url
    try:
        p = urllib.parse.urlsplit(url)
    except Exception:
        return url
    q = [
        (k, v)
        for k, v in urllib.parse.parse_qsl(p.query, keep_blank_values=False)
        if not k.lower().startswith(("utm_", "fbclid", "gclid", "mc_", "ref", "cmpid"))
        and k.lower() not in {"output", "oc", "hl", "gl", "ceid"}
    ]
    path = re.sub(r"/amp/?$", "", p.path)
    path = re.sub(r"/+$", "", path) or "/"
    return urllib.parse.urlunsplit((p.scheme.lower(), p.netloc.lower(), path, urllib.parse.urlencode(q), ""))


def jsonld_objects(html_text: str) -> list[dict]:
    out: list[dict] = []
    for m in re.finditer(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html_text,
        re.S | re.I,
    ):
        raw = m.group(1).strip()
        try:
            obj = json.loads(raw)
        except Exception:
            continue
        stack = [obj]
        while stack:
            cur = stack.pop()
            if isinstance(cur, list):
                stack.extend(cur)
            elif isinstance(cur, dict):
                out.append(cur)
                if "@graph" in cur:
                    stack.append(cur["@graph"])
    return out


def meta_content(html_text: str, *names: str) -> str | None:
    for name in names:
        pats = [
            rf'<meta[^>]+(?:property|name|itemprop)=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']*)',
            rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]+(?:property|name|itemprop)=["\']{re.escape(name)}["\']',
        ]
        for pat in pats:
            m = re.search(pat, html_text, re.I)
            if m:
                return html.unescape(m.group(1)).strip()
    return None


def strip_tags(text: str) -> str:
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return clean_text(html.unescape(text))


def title_similarity(a: str, b: str) -> float:
    from difflib import SequenceMatcher

    def norm(s: str) -> str:
        s = re.sub(r"\s*[-|–]\s*(the star|nst online|the edge malaysia|malay mail|"
                   r"free malaysia today|the sun|bernama|focus malaysia|the malaysian reserve).*$",
                   "", s, flags=re.I)
        s = re.sub(r"[^a-z0-9 ]+", " ", s.lower())
        return re.sub(r"\s+", " ", s).strip()

    return SequenceMatcher(None, norm(a), norm(b)).ratio()
