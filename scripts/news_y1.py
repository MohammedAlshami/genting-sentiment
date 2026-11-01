#!/usr/bin/env python3
"""Collect Genting news for 2 Nov 2024 00:00 MYT -> 1 Nov 2025 23:59:59 MYT.

Stages: discover (Google News RSS, month-sized windows) -> resolve Google
redirects -> fetch/extract full text -> WordPress REST APIs -> build JSONL.
All state lives under data/raw/cache/news_y1 so the year-two run is untouched.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from curl_cffi import requests as cffi_requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

from news_lib import (  # noqa: E402
    DATA,
    GENTING_WEAK,
    canonical_url,
    clean_text,
    http_get,
    jsonld_objects,
    meta_content,
    parse_pubdate,
    sha1,
    strip_tags,
    title_similarity,
)
from news_discover import GN_QUERIES, strip_publisher  # noqa: E402
from news_build import (  # noqa: E402
    clean_title,
    detect_lang,
    publisher_for,
    relevance,
    strip_publisher_boilerplate,
    tickers_for,
)
import news_build as _news_build  # noqa: E402

# Additional publishers that routinely cover Genting's Malaysian and overseas
# operations. Priorities follow the year-two mapping (1 = Malaysian, 2 = trade).
EXTRA_PUBLISHERS = {
    "fifthperson.com": ("news_fifthperson", "Fifth Person", 2),
    "fortune.com": ("news_fortune", "Fortune", 2),
    "blooloop.com": ("news_blooloop", "Blooloop", 2),
    "asianjournal.com": ("news_asianjournal", "Asian Journal", 2),
    "commercialobserver.com": ("news_commercialobserver", "Commercial Observer", 2),
    "queenseagle.com": ("news_queenseagle", "Queens Daily Eagle", 2),
    "costar.com": ("news_costar", "CoStar News", 2),
    "spectrumlocalnews.com": ("news_spectrumlocalnews", "Spectrum News 1", 2),
    "timesunion.com": ("news_timesunion", "Times Union", 2),
    "thenevadaindependent.com": ("news_nevadaindependent", "The Nevada Independent", 2),
    "reviewjournal.com": ("news_reviewjournal", "Las Vegas Review-Journal", 2),
    "news3lv.com": ("news_news3lv", "News 3 Las Vegas", 2),
    "travelweekly.com": ("news_travelweekly", "Travel Weekly", 2),
    "hotel-online.com": ("news_hotelonline", "Hotel Online", 3),
    "skift.com": ("news_skift", "Skift", 2),
    "gamingintelligence.com": ("news_gamingintelligence", "Gaming Intelligence", 2),
    "igamingexpert.com": ("news_igamingexpert", "iGaming Expert", 2),
    "gamblingnews.com": ("news_gamblingnews", "Gambling News", 2),
    "yogonet.com": ("news_yogonet", "Yogonet", 2),
    "london-post.co.uk": ("news_londonpost", "London Post", 3),
    "cityam.com": ("news_cityam", "City AM", 2),
    "tribune242.com": ("news_tribune242", "The Tribune (Bahamas)", 2),
    "news.worldcasinodirectory.com": ("news_worldcasinodirectory", "World Casino Directory", 3),
    "therealdeal.com": ("news_therealdeal", "The Real Deal", 2),
    "upstreamonline.com": ("news_upstream", "Upstream", 2),
    "oedigital.com": ("news_oedigital", "OE Digital", 3),
    "worldofbuzz.com": ("news_worldofbuzz", "World of Buzz", 2),
    "moomoo.com": ("news_moomoo", "Moomoo", 3),
    "vegasslotsonline.com": ("news_vegasslotsonline", "VegasSlotsOnline", 3),
}
_news_build.PUBLISHERS.update(EXTRA_PUBLISHERS)

ROOT = Path(__file__).resolve().parent.parent
CACHE = DATA / "cache" / "news_y1"
GN_CACHE = CACHE / "gn"
ART_CACHE = CACHE / "articles"
for _d in (CACHE, GN_CACHE, ART_CACHE):
    _d.mkdir(parents=True, exist_ok=True)

DISCOVERY = CACHE / "discovery.json"
RESOLVED = CACHE / "resolved.json"
FETCHED = CACHE / "fetched.json"
WP_POSTS = CACHE / "wp_posts.json"
STATS = CACHE / "stats.json"

# 2 Nov 2024 00:00 MYT .. 1 Nov 2025 23:59:59 MYT (UTC+8).
START_TS = int(datetime(2024, 11, 1, 16, 0, tzinfo=timezone.utc).timestamp())
END_TS = int(datetime(2025, 11, 1, 16, 0, tzinfo=timezone.utc).timestamp())
WINDOW_START = datetime.fromtimestamp(START_TS, timezone.utc)
WINDOW_END = datetime.fromtimestamp(END_TS, timezone.utc)

OUT_JSONL = DATA / "news_articles_2024-2025.jsonl"
OUT_REPORT = DATA / "news_2024-2025_report.md"

# Articles recovered through supplementary web search (mostly Edge quarterly
# results pieces that Google News did not return). Fetched directly.
MANUAL_URLS = [
    "https://theedgemalaysia.com/node/735900",
    "https://theedgemalaysia.com/node/735867",
    "https://theedgemalaysia.com/node/746169",
    "https://theedgemalaysia.com/node/757280",
    "https://theedgemalaysia.com/node/768649",
    "https://www.thestar.com.my/business/business-news/2025/02/27/genting-anticipates-continued-growth-in-tourism-and-gaming",
    "https://www.thestar.com.my/business/business-news/2025/02/28/genting-stocks-tumble-as-earnings-disappoint-analysts-cut-forecasts",
]

# Base Google News queries plus year-one specific angles.
Y1_QUERIES = GN_QUERIES + [
    '"Genting Malaysia" results',
    '"Genting Malaysia" earnings',
    '"Genting Malaysia" lawsuit',
    '"Genting Malaysia" Bimini',
    '"Genting Malaysia" New York',
    '"Genting Malaysia" dividend',
    '"Genting Malaysia" tax',
    '"Genting Berhad" debt',
    '"Genting Berhad" dividend',
    '"Genting Bhd" results',
    '"Genting Bhd" shares',
    "Genting shares fall",
    "Genting shares rise",
    "Genting casino closure",
    "Genting Miami",
    "Genting Bahamas",
    "Genting UK casino",
    "Genting Energy",
    "Genting Oil",
    "Genting Plantations",
    "GENM rights issue",
    "GENM dividend",
    "GENM results",
    '"Resorts World Genting" casino',
    '"Genting SkyWorlds"',
    '"Genting Highlands" casino',
    'site:theedgemalaysia.com "Genting Malaysia"',
    'site:theedgemalaysia.com GENM',
    'site:thestar.com.my "Genting Malaysia"',
    'site:thestar.com.my GENM',
    'site:nst.com.my "Genting Malaysia"',
    'site:malaymail.com Genting',
    'site:thesun.my Genting',
    'site:freemalaysiatoday.com Genting',
    'site:focusmalaysia.my Genting',
    'site:businesstoday.com.my Genting',
    'site:klsescreener.com Genting',
    'site:themalaysianreserve.com "Genting Malaysia"',
    'site:bernama.com "Genting Malaysia"',
    'site:thevibes.com Genting',
    'site:therakyatpost.com Genting',
    'site:edgeprop.my Genting',
    'site:sinardaily.my Genting',
    'site:malaysiakini.com Genting',
    'site:themalaysianinsight.com Genting',
    'site:theborneopost.com Genting',
    'site:dayakdaily.com Genting',
    'site:thestar.com.my "Resorts World Genting"',
    'site:theedgemalaysia.com "Resorts World Genting"',
]

CAP = 90


def load_stats() -> dict:
    if STATS.exists():
        try:
            return json.loads(STATS.read_text())
        except Exception:
            pass
    return {"requests": Counter()}


def save_stats(stats: dict) -> None:
    stats["requests"] = dict(stats["requests"])
    STATS.write_text(json.dumps(stats, ensure_ascii=False, indent=1))


def bump(key: str, n: int = 1) -> None:
    s = load_stats()
    s["requests"][key] = s["requests"].get(key, 0) + n
    STATS.write_text(json.dumps(s, ensure_ascii=False, indent=1))


def gn_rss_url(query: str, start: datetime, end: datetime) -> str:
    q = f"{query} after:{start:%Y-%m-%d} before:{end:%Y-%m-%d}"
    return (
        "https://news.google.com/rss/search?q="
        + re.sub(r"\s+", "+", q)
        + "&hl=en-MY&gl=MY&ceid=MY:en"
    )


def fetch_window(query: str, start: datetime, end: datetime, out: dict, depth: int = 0) -> None:
    url = gn_rss_url(query, start, end)
    cp = GN_CACHE / f"{sha1(url)}.xml"
    if cp.exists():
        xml_text = cp.read_text(encoding="utf-8", errors="replace")
    else:
        r = http_get(url, timeout=45)
        bump("google_news_rss")
        if r is None or r.status_code != 200:
            print(f"    FAIL {start:%Y-%m-%d}..{end:%Y-%m-%d} {query}", flush=True)
            return
        xml_text = r.text
        cp.write_text(xml_text, encoding="utf-8")
        time.sleep(1.15)
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return
    raw_items = root.findall(".//item")
    span_days = (end - start).days
    if len(raw_items) >= CAP and span_days > 2 and depth < 4:
        mid = start + (end - start) / 2
        fetch_window(query, start, mid, out, depth + 1)
        fetch_window(query, mid, end, out, depth + 1)
        return
    for it in raw_items:
        link = (it.findtext("link") or "").strip()
        if not link:
            continue
        src_el = it.find("source")
        source = (src_el.text or "").strip() if src_el is not None else None
        pub = parse_pubdate(it.findtext("pubDate"))
        if pub is None or not (WINDOW_START <= pub < WINDOW_END + timedelta(days=2)):
            continue
        title = (it.findtext("title") or "").strip()
        rec = {
            "google_url": link,
            "google_id": (it.findtext("guid") or "").strip(),
            "title": strip_publisher(title, source),
            "title_raw": title,
            "source": source,
            "published_utc": int(pub.timestamp()),
            "pub_text": it.findtext("pubDate"),
            "query": query,
            "discovered_via": "google_news_deep",
        }
        if link not in out:
            out[link] = rec


def stage_discover() -> None:
    out: dict[str, dict] = {}
    if DISCOVERY.exists():
        for it in json.loads(DISCOVERY.read_text()):
            out[it["google_url"]] = it
    before = len(out)
    windows = []
    cur = WINDOW_START
    while cur < WINDOW_END:
        nxt = (cur.replace(day=1) + timedelta(days=32)).replace(day=1)
        windows.append((cur, min(nxt, WINDOW_END)))
        cur = nxt
    print(f"{len(Y1_QUERIES)} queries x {len(windows)} months; starting with {before} items", flush=True)
    for qi, q in enumerate(Y1_QUERIES, 1):
        for a, b in windows:
            fetch_window(q, a, b, out)
        print(f"[{qi}/{len(Y1_QUERIES)}] {q}: total {len(out)} (+{len(out)-before})", flush=True)
        before = len(out)
    items = sorted(out.values(), key=lambda x: x["published_utc"], reverse=True)
    DISCOVERY.write_text(json.dumps(items, ensure_ascii=False, indent=1))
    print(f"wrote {len(items)} discovery items -> {DISCOVERY}")


# ---------------------------------------------------------------- resolve ----
def resolve_one(session: cffi_requests.Session, google_url: str) -> str | None:
    if "news.google.com" not in google_url:
        return google_url
    base = google_url.split("?")[0]
    r = http_get(base, session=session, timeout=30, tries=2)
    bump("resolve_page")
    if r is None:
        return None
    if "news.google.com" not in r.url:
        return r.url
    h = r.text
    sg = re.search(r'data-n-a-sg="([^"]+)"', h)
    ts = re.search(r'data-n-a-ts="([^"]+)"', h)
    aid = re.search(r'data-n-a-id="([^"]+)"', h)
    if not (sg and ts and aid):
        return None
    payload = [
        "garturlreq",
        [
            ["X", "X", ["X", "X"], None, None, 1, 1, "US:en", None, 1, None, None, None, None, None, 0, 1],
            "X",
            "X",
            1,
            [1, 1, 1],
            1,
            1,
            None,
            0,
            0,
            None,
            0,
        ],
        aid.group(1),
        int(ts.group(1)),
        sg.group(1),
    ]
    f_req = [[["Fbv4je", json.dumps(payload, separators=(",", ":"))]]]
    data = "f.req=" + urllib.parse.quote(json.dumps(f_req, separators=(",", ":")))
    try:
        r2 = session.post(
            "https://news.google.com/_/DotsSplashUi/data/batchexecute",
            data=data,
            headers={
                "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            },
            impersonate="chrome",
            timeout=30,
        )
    except Exception:
        return None
    bump("resolve_batchexecute")
    if r2.status_code != 200:
        return None
    m = re.search(r'\[\\"garturlres\\",\\"(.*?)\\"', r2.text)
    if not m:
        return None
    url = m.group(1).replace("\\\\u003d", "=").replace("\\\\u0026", "&")
    url = url.replace("\\u003d", "=").replace("\\u0026", "&")
    if not url.startswith("http"):
        return None
    return url


def stage_discover_span() -> None:
    """Year-long query pass; Google returns its top-ranked items per query."""
    out: dict[str, dict] = {}
    if DISCOVERY.exists():
        for it in json.loads(DISCOVERY.read_text()):
            out[it["google_url"]] = it
    before = len(out)
    for qi, q in enumerate(Y1_QUERIES, 1):
        fetch_window(q, WINDOW_START, WINDOW_END, out)
        if qi % 10 == 0:
            print(f"[{qi}/{len(Y1_QUERIES)}] total {len(out)} (+{len(out)-before})", flush=True)
    items = sorted(out.values(), key=lambda x: x["published_utc"], reverse=True)
    DISCOVERY.write_text(json.dumps(items, ensure_ascii=False, indent=1))
    print(f"wrote {len(items)} discovery items -> {DISCOVERY}")


def stage_resolve() -> None:
    items = json.loads(DISCOVERY.read_text())
    state: dict[str, str | None] = {}
    if RESOLVED.exists():
        state = json.loads(RESOLVED.read_text())
    todo = [
        it
        for it in items
        if it["google_url"] not in state
        and re.search(r"genting|genm|3182|4715|云顶|resorts world|rwg|rwnyc", it["title"], re.I)
    ]
    print(f"{len(state)} cached, {len(todo)} to resolve", flush=True)
    session = cffi_requests.Session()
    t0 = time.time()
    for i, it in enumerate(todo, 1):
        url = resolve_one(session, it["google_url"])
        state[it["google_url"]] = url
        if i % 50 == 0 or i == len(todo):
            RESOLVED.write_text(json.dumps(state, ensure_ascii=False, indent=0))
            ok = sum(1 for v in state.values() if v)
            print(f"  [{i}/{len(todo)}] resolved={ok} elapsed={time.time()-t0:.0f}s", flush=True)
        time.sleep(0.4)
    RESOLVED.write_text(json.dumps(state, ensure_ascii=False, indent=0))
    good = sum(1 for v in state.values() if v)
    print(f"done: {good}/{len(state)} resolved")


# ------------------------------------------------------------------ fetch ----
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


def extract_nst_body(html_text: str) -> str | None:
    """NST embeds the story HTML in a JSON blob; trafilatura only sees the nav."""
    m = re.search(
        r'body_with_inline(?:&quot;|")\s*:\s*(?:&quot;|")(.*?)(?:&quot;|")\s*,\s*'
        r'(?:&quot;|")premium',
        html_text,
        re.S,
    )
    if not m:
        return None
    raw = html.unescape(m.group(1))
    raw = html.unescape(raw).replace("\\/", "/")
    raw = raw.replace("\\n", "\n").replace("\\r", "").replace("\\t", " ")
    raw = raw.replace('\\"', '"')
    txt = strip_tags(raw)
    return txt if len(txt) > 200 else None


def fetch_one(session: cffi_requests.Session, url: str) -> dict:
    cp = ART_CACHE / f"{sha1(url)}.json"
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
    r = http_get(page_variant(url, domain), session=session, timeout=22, tries=2)
    bump("article_fetch")
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
    if "nst.com.my" in domain and len(body or "") < 700:
        m = re.search(r'<link[^>]+rel=["\']amphtml["\'][^>]+href=["\']([^"\']+)', html_text, re.I)
        alt_url = m.group(1) if m else None
        if not alt_url and "/amp/" not in url:
            parts = urllib.parse.urlsplit(url)
            alt_url = urllib.parse.urlunsplit(
                (parts.scheme, parts.netloc, "/amp" + parts.path, parts.query, "")
            )
        if alt_url:
            r2 = http_get(alt_url, session=session, timeout=45, tries=2)
            bump("article_fetch_amp")
            if r2 is not None and r2.status_code == 200:
                alt = extract_trafilatura(r2.text, alt_url) or extract_bs4(r2.text)
                if alt and len(alt) > len(body or ""):
                    body, rec["extractor"] = alt, "trafilatura_amp"
    body = strip_boilerplate(clean_text(body or ""))
    if "nst.com.my" in domain:
        nst_body = strip_boilerplate(clean_text(extract_nst_body(html_text) or ""))
        if len(nst_body) > len(body):
            body, rec["extractor"] = nst_body, "nst_body_json"
    text_l = html_text.lower()
    if len(body) < 700 and PAYWALL_MARKERS.search(text_l[-250000:]):
        rec["paywalled"] = True
    if body and PAYWALL_MARKERS.search(body[-1200:]):
        rec["paywalled"] = True
    rec["body"] = body or None
    cp.write_text(json.dumps(rec, ensure_ascii=False))
    return rec


def stage_fetch() -> None:
    items = json.loads(DISCOVERY.read_text())
    state = json.loads(RESOLVED.read_text()) if RESOLVED.exists() else {}
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
    for mu in MANUAL_URLS:
        cu = canonical_url(mu)
        if cu not in by_url:
            cands.append(
                {
                    "url": cu,
                    "google_title": None,
                    "google_source": None,
                    "google_published_utc": None,
                    "google_url": None,
                }
            )
    cands.sort(key=lambda x: urllib.parse.urlsplit(x["url"]).netloc)
    print(f"{len(cands)} candidate URLs", flush=True)

    session = cffi_requests.Session()
    last_hit: dict[str, float] = {}
    out = []
    t0 = time.time()
    for i, it in enumerate(cands, 1):
        domain = urllib.parse.urlsplit(it["url"]).netloc
        wait = 1.15 - (time.time() - last_hit.get(domain, 0))
        if wait > 0:
            time.sleep(wait)
        rec = dict(fetch_one(session, it["url"]))
        last_hit[domain] = time.time()
        rec["google_title"] = it.get("title")
        rec["google_source"] = it.get("source")
        rec["google_published_utc"] = it.get("published_utc")
        rec["google_url"] = it.get("google_url")
        out.append(rec)
        if i % 25 == 0 or i == len(cands):
            print(f"  [{i}/{len(cands)}] {time.time()-t0:.0f}s", flush=True)
            FETCHED.write_text(json.dumps(out, ensure_ascii=False))
    FETCHED.write_text(json.dumps(out, ensure_ascii=False))
    ok = sum(1 for r in out if r.get("body"))
    short = sum(1 for r in out if r.get("body") and len(r["body"]) < 500)
    print(
        f"done: {ok} with body, {short} short, "
        f"{sum(1 for r in out if r.get('paywalled'))} paywalled"
    )


# --------------------------------------------------------------- wordpress ----
WP_SITES = {
    "businesstoday.com.my": "https://www.businesstoday.com.my",
    "ggrasia.com": "https://ggrasia.com",
    "therakyatpost.com": "https://www.therakyatpost.com",
    "thesun.my": "https://thesun.my",
    "themalaysianreserve.com": "https://www.themalaysianreserve.com",
    "focusmalaysia.my": "https://focusmalaysia.my",
    "thevibes.com": "https://thevibes.com",
}


def stage_wp() -> None:
    session = cffi_requests.Session()
    records: list[dict] = []
    for name, base in WP_SITES.items():
        page = 1
        site_count = 0
        while page <= 15:
            url = (
                f"{base}/wp-json/wp/v2/posts?search=genting&per_page=100&page={page}"
                "&after=2024-11-01T00:00:00&before=2025-11-02T00:00:00"
                "&_fields=id,date,date_gmt,link,title,content,author,excerpt"
            )
            try:
                r = session.get(url, impersonate="chrome", timeout=45)
            except Exception as exc:
                print(f"{name} page {page}: ERR {exc}")
                break
            bump("wp_api")
            if r.status_code == 400:
                break
            if r.status_code != 200:
                print(f"{name} page {page}: HTTP {r.status_code}")
                if r.status_code in (429, 500, 502, 503, 504):
                    time.sleep(3)
                break
            try:
                posts = r.json()
            except Exception:
                print(f"{name} page {page}: bad JSON")
                break
            if not posts:
                break
            for p in posts:
                title = strip_tags((p.get("title") or {}).get("rendered", ""))
                body = strip_tags((p.get("content") or {}).get("rendered", ""))
                if not title or not body:
                    continue
                dt = None
                if p.get("date_gmt"):
                    dt = datetime.fromisoformat(p["date_gmt"]).replace(tzinfo=timezone.utc)
                elif p.get("date"):
                    dt = datetime.fromisoformat(p["date"]).astimezone(timezone.utc)
                if dt is None:
                    continue
                records.append(
                    {
                        "url": p.get("link"),
                        "title": clean_text(title),
                        "author": None,
                        "published_utc": int(dt.timestamp()),
                        "body": body,
                        "publisher": name,
                        "wp_id": p.get("id"),
                    }
                )
                site_count += 1
            if len(posts) < 100:
                break
            page += 1
            time.sleep(1.15)
        print(f"{name}: {site_count} posts", flush=True)
    by = {r["url"]: r for r in records if r.get("url")}
    records = list(by.values())
    WP_POSTS.write_text(json.dumps(records, ensure_ascii=False))
    print(f"wrote {len(records)} -> {WP_POSTS}")


# ------------------------------------------------------------------ build ----
def relevance_y1(title: str, body: str) -> tuple[bool, str]:
    """Year-one filter: base rules plus subsidiary-brand and legal-story overrides."""
    tl = (title or "").lower()
    bl = (body or "").lower()
    # "related-party" trips the entertainment keyword "party".
    probe_title = re.sub(r"related[- ]party", "related transaction", title or "", flags=re.I)
    ok, why = relevance(probe_title, body)
    if ok:
        return True, why
    company_in_title = re.search(
        r"genting (berhad|bhd|malaysia|group|americas)|genm\b|\b3182\b|\b4715\b", tl
    )
    # Corporate litigation involving Genting is substantive, not an estate story
    # (the base filter keys on the word "court").
    if why == "estate/family dispute" and re.search(r"\bgenting\b", tl) and re.search(
        r"court|lawsuit|suit|litigation|dispute|tribunal|arbitration|shareholder", tl
    ):
        return True, "ok"
    # Subsidiary brands whose headlines omit the parent name but whose body is
    # about Genting Berhad (RWLV) or Genting Malaysia (RWNYC/Catskills/Bimini/RWG).
    if why in ("not about the company", "passing mention", "place/policy story") and re.search(
        r"resorts world (las vegas|new york|nyc|ny|catskills|bimini|genting)|\brwg\b|\brwlv\b|\brwnyc\b",
        tl,
    ):
        n_genting = len(re.findall(r"\bgenting\b", bl))
        if n_genting >= 1 and re.search(
            r"genting (berhad|bhd|malaysia|group|americas|uk|energy)|\bgenm\b|\b3182\b|\b4715\b", bl
        ):
            return True, "ok"
    # Property/place keywords should not veto a finance headline.
    if why == "place/policy story" and re.search(
        r"bond|merger|acquisition|takeover|buyout|\bdeal\b|sale|debt|profit|revenue|earnings|"
        r"valuation|stake|million|billion",
        tl,
    ):
        return True, "ok"
    # Tourism-demand stories that are really earnings outlooks for the group.
    if why == "place/policy story" and re.search(r"genting", tl) and re.search(
        r"tourism|tourist", tl
    ) and re.search(r"boon|lift|aids|earnings|revenue|profit", tl):
        return True, "ok"
    # "Genting requests trading suspension", "Genting unit lays keel ..." and
    # similar corporate-action headlines that carry no finance noun.
    if why == "passing mention" and re.match(r"\s*(genting|genm)\b", tl) and re.search(
        r"request|suspend|halt|resume|lays?|keel|deliver|construct|announce|propose|bid|"
        r"appoint|confirm|deny|acquire|dispose|divest|sell|buy|takeover|merger|in the red",
        tl,
    ):
        return True, "ok"
    # Any other group-level headline whose body is explicitly about Genting Bhd
    # (e.g. "Genting in the red after closing Britain", "Genting to add 100MW").
    if why == "passing mention" and re.match(r"\s*genting\b", tl) and re.search(
        r"\bgenting (berhad|bhd|malaysia)\b", bl
    ):
        return True, "ok"
    return ok, why


def tickers_y1(title: str, body: str) -> list[str]:
    text = f"{title}\n{body}".lower()
    out: list[str] = []
    if re.search(
        r"genting berhad|genting bhd|\b3182\b|genting group|genting conglomerate|genting overseas|"
        r"resorts world las vegas|\brwlv\b|genting energy|\bflng\b|genting uk",
        text,
    ):
        out.append("GENTING")
    if re.search(
        r"genting malaysia|\bgenm\b|\b4715\b|resorts world genting|genting highlands|"
        r"resorts world new york|resorts world ny\b|genting new york|\brwnyc\b|catskills|bimini|"
        r"genting americas|\brwg\b",
        text,
    ):
        out.append("GENM")
    if not out and re.search(r"\bgenting\b", text):
        out.append("GENTING")
    return out



def load_fetched() -> list[dict]:
    if not FETCHED.exists():
        return []
    out = []
    for r in json.loads(FETCHED.read_text()):
        if not r.get("body") or r.get("skip_reason"):
            continue
        title = r.get("title")
        if (not title or len(title) < 25) and r.get("google_title"):
            title = r["google_title"]
            if r.get("google_source") and title.endswith(" - " + r["google_source"]):
                title = title[: -(len(r["google_source"]) + 3)].strip()
        out.append(
            {
                "url": r["url"],
                "title": title or r.get("google_title"),
                "author": r.get("author"),
                "published_utc": r.get("published_utc") or r.get("google_published_utc"),
                "body": r["body"],
                "publisher_hint": r.get("google_source"),
                "origin": "fetch",
                "extractor": r.get("extractor"),
                "paywalled": bool(r.get("paywalled")),
                "google_url": r.get("google_url"),
            }
        )
    return out


def load_wp() -> list[dict]:
    if not WP_POSTS.exists():
        return []
    out = []
    for r in json.loads(WP_POSTS.read_text()):
        out.append(
            {
                "url": r["url"],
                "title": r["title"],
                "author": r.get("author"),
                "published_utc": r["published_utc"],
                "body": r["body"],
                "publisher_hint": r.get("publisher"),
                "origin": "wp_api",
                "extractor": "wp_api",
                "paywalled": False,
                "google_url": None,
            }
        )
    return out


MALAYSIAN_PUBLISHERS = {
    "The Edge Malaysia",
    "The Star",
    "New Straits Times",
    "Malay Mail",
    "Free Malaysia Today",
    "The Malaysian Reserve",
    "The Sun Malaysia",
    "Bernama",
    "Focus Malaysia",
    "KLSE Screener",
    "BusinessToday Malaysia",
    "The Rakyat Post",
    "EdgeProp Malaysia",
    "The Vibes",
    "Sinar Daily",
    "Says",
    "Varnam Malaysia",
    "RAM Ratings",
}

# Place/lifestyle/event copy that merely happens at Genting Highlands, and
# subsidiary-only stories (Genting Plantations, Genting Singapore).
JUNK_TITLE = re.compile(
    r"\bconcert\b|\btour\b|\blive in\b|dazzl|showcase|arena of stars|"
    r"lion dance|tarian singa|mooncake|\braya\b|christmas|\bcny\b|festive|"
    r"stargazing|hotspot|nature trail|litter|rubbish|\bsnow\b|"
    r"landslide|runtuh|road closure|\bmissing\b|charged|brawl|\bfight\b|robbery|"
    r"\bcrash\b|motosikal|penunggang|airbnb|residences|condominium|"
    r"casino win|winnings|jackpot|turtle conservation|halal champion|vacation vibes|"
    r"visitor arrivals|foreign investors|net sell|disney|richard marx|\bmltr\b|kenny g|"
    r"\btea\b|hotpot|dining|buffet|restaurant|\bfood\b|hotel\b|resort review|staycation|"
    r"\bproperty\b|real estate|discount|promo|\bevent\b|\bshow\b|"
    r"\bcafe\b|café|heated pool|runaway bus|pillar|ticket|"
    r"sports car|turned away|"
    r"get up close|gentleman.s ride|winning big|rm800,?000",
    re.I,
)
FIN_STRONG = re.compile(
    r"profit|revenue|earnings?|debt|bond|takeover|privatis|buyout|acquire|acquisition|"
    r"dispose|divest|dividend|rating|fitch|moody|credit|results?|quarter|\bq[1-4]\b|"
    r"\bceo\b|\bcfo\b|appoint|resign|licen[cs]e|casino floor|gaming|new york|las vegas|"
    r"bimini|catskills|empire resorts|\bflng\b|stem cell|\bklci\b|msci|suspension|"
    r"target price|valuation|stake|delist|financial|share repurchase",
    re.I,
)
ROUNDUP_Y1 = re.compile(
    r"^top stock market|^fbm klci climbs|^genting leads bulls|lifts bursa at the open|"
    r"^thomson medical|\byinson\b|\beco world\b",
    re.I,
)
OFF_TOPIC = re.compile(
    r"afa infrastructure|toll collection|expressway concession", re.I
)
SUBSIDIARY_TITLE = re.compile(r"genting plantation|\bgenp\b|genting sing\b", re.I)
PARENT_TITLE = re.compile(r"genting berhad|genting bhd|genting malaysia|\bgenm\b", re.I)


def stage_build() -> None:
    raw = load_fetched() + load_wp()
    print(f"loaded {len(raw)} candidate records")
    stats = Counter()
    rejected = []
    kept: dict[str, dict] = {}
    for rec in raw:
        url = canonical_url(rec["url"] or "")
        if not url or not url.startswith("http"):
            stats["bad_url"] += 1
            continue
        pm = publisher_for(url)
        if not pm:
            stats["unmapped_publisher"] += 1
            rejected.append({"url": url, "title": rec.get("title"), "reason": "unmapped_publisher"})
            continue
        source, publisher, priority = pm
        if re.search(
            r"^/(tag|tags|author|authors|topic|topics|search|videos|gallery|photos|podcast|podcasts)(/|$)",
            urllib.parse.urlsplit(url).path,
            re.I,
        ):
            stats["non_news_path"] += 1
            continue
        ts = rec.get("published_utc")
        if not ts:
            stats["no_timestamp"] += 1
            continue
        ts = int(ts)
        if not (START_TS <= ts < END_TS):
            stats["out_of_window"] += 1
            continue
        title = clean_title(rec.get("title") or "")
        body = strip_publisher_boilerplate(clean_text(rec.get("body") or ""))
        if source == "news_thestar" and len(body) < 700:
            rec["paywalled"] = True
        if SUBSIDIARY_TITLE.search(title) and not PARENT_TITLE.search(title):
            stats["reject_subsidiary_entity"] += 1
            rejected.append({"url": url, "title": title, "reason": "subsidiary_entity"})
            continue
        if OFF_TOPIC.search(title) or ROUNDUP_Y1.search(title):
            stats["reject_roundup_y1"] += 1
            rejected.append({"url": url, "title": title, "reason": "roundup_y1"})
            continue
        if JUNK_TITLE.search(title) and not FIN_STRONG.search(title):
            stats["reject_place_event"] += 1
            rejected.append({"url": url, "title": title, "reason": "place_event"})
            continue
        if body.lower().lstrip().startswith("risk disclaimer"):
            stats["reject_boilerplate_body"] += 1
            rejected.append({"url": url, "title": title, "reason": "boilerplate_body"})
            continue
        if len(title) < 8 or len(body) < 120:
            stats["too_short"] += 1
            rejected.append({"url": url, "title": title, "reason": "too_short", "len": len(body)})
            continue
        ok, why = relevance_y1(title, body)
        if not ok:
            stats[f"reject_{why.replace(' ', '_')}"] += 1
            rejected.append({"url": url, "title": title, "reason": why})
            continue
        tickers = tickers_y1(title, body)
        if not tickers:
            stats["no_ticker"] += 1
            rejected.append({"url": url, "title": title, "reason": "no_ticker"})
            continue
        out = {
            "record_type": "article",
            "source": source,
            "channel": publisher,
            "publisher": publisher,
            "url": url,
            "title": title,
            "author": rec.get("author") or None,
            "published_utc": ts,
            "body": body,
            "summary": None,
            "tickers": tickers,
            "lang": detect_lang(body),
            "raw": {
                "publisher": publisher,
                "origin": rec.get("origin"),
                "extractor": rec.get("extractor"),
                "paywalled": bool(rec.get("paywalled")),
                "priority": priority,
                "malaysian_publisher": publisher in MALAYSIAN_PUBLISHERS,
            },
        }
        if rec.get("google_url"):
            out["raw"]["google_news_url"] = rec["google_url"]
        prior = kept.get(url)
        if prior is None or len(out["body"]) > len(prior["body"]):
            kept[url] = out
    print(f"after URL dedupe: {len(kept)}")

    ordered = sorted(
        kept.values(),
        key=lambda r: (r["raw"]["priority"], -r["published_utc"], -len(r["body"])),
    )
    final: list[dict] = []
    seen_bodies: set[str] = set()
    for rec in ordered:
        body_hash = sha1(rec["body"])
        if body_hash in seen_bodies:
            stats["duplicate_body"] += 1
            continue
        seen_bodies.add(body_hash)
        dup = None
        for other in final:
            if title_similarity(rec["title"], other["title"]) >= 0.90:
                dup = other
                break
        if dup is None:
            final.append(rec)
        else:
            stats["near_dup_title"] += 1
            if rec["raw"]["priority"] < dup["raw"]["priority"] or (
                rec["raw"]["priority"] == dup["raw"]["priority"]
                and len(rec["body"]) > len(dup["body"]) * 1.1
            ):
                final[final.index(dup)] = rec
    final.sort(key=lambda r: r["published_utc"], reverse=True)
    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSONL.open("w", encoding="utf-8") as fh:
        for rec in final:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    (CACHE / "rejected_y1.json").write_text(json.dumps(rejected, ensure_ascii=False, indent=0))
    print(f"wrote {len(final)} articles -> {OUT_JSONL}")
    print("stats:", dict(stats))
    for k, v in Counter(r["channel"] for r in final).most_common():
        print(f"  {v:3d} {k}")
    print("by ticker:", Counter(t for r in final for t in r["tickers"]))


# ----------------------------------------------------------------- report ----
def stage_report() -> None:
    recs = [json.loads(line) for line in OUT_JSONL.open(encoding="utf-8") if line.strip()]
    stats = load_stats()
    req = stats.get("requests", {})
    pub = Counter(r["channel"] for r in recs)
    tick = Counter(t for r in recs for t in r["tickers"])
    months = Counter(datetime.fromtimestamp(r["published_utc"], timezone.utc).strftime("%Y-%m") for r in recs)
    paywalled = [r for r in recs if (r.get("raw") or {}).get("paywalled")]
    msian = [r for r in recs if (r.get("raw") or {}).get("malaysian_publisher")]
    bodies = sorted(len(r["body"]) for r in recs) or [0]
    ts = [r["published_utc"] for r in recs]

    def fmt(tsv: int) -> str:
        return datetime.fromtimestamp(tsv, timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Genting news collection — 2 Nov 2024 to 1 Nov 2025",
        "",
        "Window: **2 Nov 2024 00:00 MYT → 1 Nov 2025 23:59:59 MYT** "
        f"(`{START_TS}`–`{END_TS - 1}` epoch UTC).",
        "",
        "## Summary",
        "",
        f"- Articles written: **{len(recs)}**",
        f"- Candidate article pages fetched: **{sum(1 for _ in json.loads(FETCHED.read_text())) if FETCHED.exists() else 0}**",
        f"- Malaysian-publisher articles: **{len(msian)}** ({len(msian)/max(len(recs),1):.0%})",
        f"- Tickers (an article can carry both): " + ", ".join(f"{k} {v}" for k, v in tick.most_common()),
        f"- Date range: **{fmt(min(ts))} → {fmt(max(ts))}**" if ts else "- Date range: n/a",
        f"- Paywalled / stubbed records: **{len(paywalled)}**",
        f"- Body length: min {bodies[0]}, median {bodies[len(bodies)//2]}, max {bodies[-1]} chars",
        f"- Authors present: {sum(1 for r in recs if r.get('author'))}/{len(recs)}",
        "",
        "## Requests made",
        "",
    ]
    for k, v in sorted(req.items()):
        lines.append(f"- {k}: {v}")
    lines += ["", "## Articles by publisher", "", "| Publisher | Articles |", "|---|---:|"]
    for k, v in pub.most_common():
        lines.append(f"| {k} | {v} |")
    lines += ["", "## Articles by month", "", "| Month (UTC) | Articles |", "|---|---:|"]
    cur = datetime(2024, 11, 1, tzinfo=timezone.utc)
    while cur < datetime(2025, 11, 1, tzinfo=timezone.utc):
        key = cur.strftime("%Y-%m")
        lines.append(f"| {key} | {months.get(key, 0)} |")
        cur = (cur.replace(day=1) + timedelta(days=32)).replace(day=1)
    rej_path = CACHE / "rejected_y1.json"
    if rej_path.exists():
        rej = json.loads(rej_path.read_text())
        rc = Counter(x.get("reason") for x in rej)
        lines += ["", "## Candidate filtering", "", "| Reason dropped | Candidates |", "|---|---:|"]
        for k, v in rc.most_common():
            lines.append(f"| {k} | {v} |")
    lines += ["", "## Method", ""]
    lines += [
        "- Discovery: Google News RSS (`hl=en-MY&gl=MY&ceid=MY:en`) with "
        f"{len(Y1_QUERIES)} queries, walked month by month and split further whenever a "
        "slice hit the ~90-item RSS cap.",
        "- Google News redirect links were resolved to canonical publisher URLs through "
        "the batchexecute decoder; dedupe by canonical URL, then by title similarity ≥0.90.",
        "- Full text: trafilatura first, readability and BeautifulSoup fallbacks; The Star "
        "`?s=app` and NST AMP variants where the canonical page is JS-heavy.",
        "- Five to seven publisher WordPress REST APIs were queried directly for full text.",
        "- Politeness: ≥1.15 s between requests to the same publisher, exponential backoff "
        "on 429/5xx, browser-impersonating curl_cffi session.",
        "",
        "## Gaps and caveats",
        "",
    ]
    all_months = []
    cur = datetime(2024, 11, 1, tzinfo=timezone.utc)
    while cur < datetime(2025, 11, 1, tzinfo=timezone.utc):
        all_months.append(cur.strftime("%Y-%m"))
        cur = (cur.replace(day=1) + timedelta(days=32)).replace(day=1)
    gaps = [m for m in all_months if months.get(m, 0) < 8]
    zero = [m for m in all_months if months.get(m, 0) == 0]
    if zero:
        lines.append(f"- Months with no recovered articles: {', '.join(zero)}.")
    if gaps:
        lines.append(
            "- Thin months (<8 articles): "
            + ", ".join(f"{m} ({months[m]})" for m in sorted(gaps))
            + "."
        )
    lines += [
        "- Google News RSS only indexes what it has crawled; very old items and articles "
        "removed from publisher sitemaps may be missing. The count is therefore a floor, "
        "not a census.",
        "- Bernama is a known gap: its article pages serve only a subscription notice "
        "(`Please email to digitalsales@bernama.com...`), so no usable public body could "
        "be extracted. One relevant Bernama 3Q24 result item was discarded for this reason.",
        "- The Star premium articles sometimes serve only the first 2-3 paragraphs to "
        "non-subscribers. Those records are kept with the public text and "
        f"`raw.paywalled=true`; {len(paywalled)} records are flagged in total.",
        "- April 2025 is genuinely thin (5 articles): targeted weekly re-queries of the "
        "top ten search terms returned no additional corporate stories for the month.",
        "- No Genting Berhad / Genting Malaysia article was published on 2-4 Nov 2024 or "
        "1 Nov 2025 in the recovered index; the first record is 5 Nov 2024 and the last "
        "is 31 Oct 2025.",
        "- The Edge Malaysia weekly editions are dated by their online publication "
        "timestamp (`article:published_time`), which can be a few days after the print "
        "cover date.",
        "- Genting Singapore, Genting Plantations and other separately listed Genting "
        "entities are excluded; pure place/lifestyle/concert copy set in Genting "
        "Highlands is also excluded as not being about the two issuers.",
        "- The collection is English-language, matching the year-two corpus. Malay- and "
        "Chinese-language coverage from Berita Harian, Sinar Harian, Oriental Daily and "
        "similar outlets is not systematically covered.",
        "- A small number of Edge quarterly-results articles that Google News did not "
        "surface were recovered through supplementary web search and fetched directly; "
        "all bodies still come from the publisher page, not from snippets.",
        "- This file ends at 1 Nov 2025 23:59:59 MYT; the year-two file starts at "
        "2 Nov 2025 00:00 MYT, so there is no overlap.",
        "",
    ]
    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote report -> {OUT_REPORT}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "stage",
        choices=["discover", "discover_span", "resolve", "fetch", "wp", "build", "report", "all"],
    )
    args = ap.parse_args()
    if args.stage in ("discover", "all"):
        stage_discover()
    if args.stage in ("discover_span", "all"):
        stage_discover_span()
    if args.stage in ("resolve", "all"):
        stage_resolve()
    if args.stage in ("fetch", "all"):
        stage_fetch()
    if args.stage in ("wp", "all"):
        stage_wp()
    if args.stage in ("build", "all"):
        stage_build()
    if args.stage in ("report", "all"):
        stage_report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
