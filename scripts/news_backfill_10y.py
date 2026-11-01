#!/usr/bin/env python3
"""Backfill Genting news for 2 Nov 2016 00:00 MYT -> 1 Nov 2024 23:59:59 MYT.

Stages: discover (Google News RSS, quarter-sized windows) -> WordPress REST
supplement -> resolve Google redirects -> fetch/extract full text -> build JSONL
-> report. State lives under data/raw/cache/news_10y so earlier runs are
untouched. No SQLite writes.
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
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from curl_cffi import requests as cffi_requests

sys.path.insert(0, str(Path(__file__).resolve().parent))

from news_lib import (  # noqa: E402
    DATA,
    canonical_url,
    clean_text,
    http_get,
    meta_content,
    parse_pubdate,
    sha1,
    strip_tags,
    title_similarity,
)
import news_build as _nb  # noqa: E402
import news_y1 as _y1  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CACHE = DATA / "cache" / "news_10y"
GN_CACHE = CACHE / "gn"
ART_CACHE = CACHE / "articles"
for _d in (CACHE, GN_CACHE, ART_CACHE):
    _d.mkdir(parents=True, exist_ok=True)

DISCOVERY = CACHE / "discovery.json"
RESOLVED = CACHE / "resolved.json"
FETCHED = CACHE / "fetched.json"
FAILURES = CACHE / "fetch_failures.json"
WP_POSTS = CACHE / "wp_posts.json"
STATS = CACHE / "stats.json"
REJECTED = CACHE / "rejected.json"

# 2 Nov 2016 00:00 MYT -> 1 Nov 2024 23:59:59 MYT, represented as a half-open
# UTC interval.
START_TS = int(datetime(2016, 11, 1, 16, 0, tzinfo=timezone.utc).timestamp())
END_TS = int(datetime(2024, 11, 1, 16, 0, tzinfo=timezone.utc).timestamp())
WINDOW_START = datetime.fromtimestamp(START_TS, timezone.utc)
WINDOW_END = datetime.fromtimestamp(END_TS, timezone.utc)
MYT = timezone(timedelta(hours=8))

OUT_JSONL = DATA / "news_articles_2016-2024.jsonl"
OUT_REPORT = DATA / "news_2016-2024_report.md"

# Malaysian outlets already represented in the corpus, plus a few Malaysian
# business desks that occasionally carry the story. Foreign Genting Singapore /
# cruise trade press is deliberately excluded.
EXTRA_PUBLISHERS = {
    "theborneopost.com": ("news_borneopost", "The Borneo Post", 1),
    "dayakdaily.com": ("news_dayakdaily", "DayakDaily", 1),
    "sinarharian.com.my": ("news_sinarharian", "Sinar Harian", 1),
    "bharian.com.my": ("news_beritaharian", "Berita Harian", 1),
    "hmetro.com.my": ("news_hmetro", "Harian Metro", 1),
    "utusan.com.my": ("news_utusan", "Utusan Malaysia", 1),
    "themalaysianreserve.com": ("news_malaysianreserve", "The Malaysian Reserve", 1),
    "thesun.my": ("news_thesun", "The Sun Malaysia", 1),
    "focusmalaysia.my": ("news_focusmalaysia", "Focus Malaysia", 1),
    "businesstoday.com.my": ("news_businesstoday", "BusinessToday Malaysia", 1),
    "thevibes.com": ("news_thevibes", "The Vibes", 1),
    "therakyatpost.com": ("news_therakyatpost", "The Rakyat Post", 1),
    "sinardaily.my": ("news_sinardaily", "Sinar Daily", 1),
}

PUBLISHERS = dict(_nb.PUBLISHERS)
PUBLISHERS.update(EXTRA_PUBLISHERS)
_nb.PUBLISHERS.update(EXTRA_PUBLISHERS)

# Malaysia-only scope: drop Singapore editions / foreign sister papers even
# when Google News labels them with a familiar brand.
EXCLUDED_HOSTS = {
    "theedgesingapore.com",
    "edgeprop.sg",
    "businesstimes.com.sg",
    "straitstimes.com",
    "scmp.com",
    "asia.nikkei.com",
}

ALLOWED_SOURCE_HINTS = (
    "the edge malaysia",
    "the edge",
    "the star",
    "new straits times",
    "nst online",
    "nst",
    "malay mail",
    "free malaysia today",
    "the malaysian reserve",
    "the sun",
    "bernama",
    "focus malaysia",
    "business today",
    "businesstoday",
    "klse screener",
    "the rakyat post",
    "trp",
    "the vibes",
    "the malaysian insight",
    "malaysiakini",
    "edgeprop",
    "sinar daily",
    "sinar harian",
    "berita harian",
    "harian metro",
    "utusan",
    "borneo post",
    "dayak daily",
)

TITLE_HINT = re.compile(
    r"genting|genm|3182|4715|resorts? world|rwg\b|rwnyc|lim kok thay|"
    r"casino|gaming|integrated resort|theme park",
    re.I,
)
# A few substantive items omit the parent name from the headline.
ALLOW_TITLE = re.compile(
    r"pan malaysian pools redeems|corporate: genting group gets nod|"
    r"in genting, the house folds|frankly speaking: landmarks",
    re.I,
)

# 38 entity/finance angles; run against every quarter.
GN_QUERIES = [
    "Genting",
    '"Genting Malaysia"',
    '"Genting Berhad"',
    '"Genting Bhd"',
    "GENM",
    '"Resorts World Genting"',
    '"Genting Highlands"',
    '"Genting group"',
    '"Genting shares"',
    '"Genting earnings"',
    '"Genting results"',
    '"Genting dividend"',
    '"Genting debt"',
    '"Genting bond"',
    '"Genting rating"',
    '"Genting casino"',
    '"Genting tax"',
    '"Genting licence"',
    '"Genting lawsuit"',
    '"Genting takeover"',
    '"Genting privatisation"',
    '"Genting stake"',
    '"Genting acquisition"',
    '"Genting disposal"',
    '"Genting target price"',
    '"Genting analyst"',
    '"Genting 3182"',
    '"Genting 4715"',
    '"Genting AGM"',
    '"Genting CEO"',
    '"Genting Lim Kok Thay"',
    '"Genting family feud"',
    '"Genting SkyWorlds"',
    '"Genting theme park"',
    '"Genting New York"',
    '"Genting Miami"',
    '"Genting Bimini"',
    '"Genting UK"',
    # Outlet-targeted queries recover older pieces that the broad ranking drops.
    "site:theedgemalaysia.com Genting",
    "site:thestar.com.my Genting",
    "site:nst.com.my Genting",
    "site:malaymail.com Genting",
    "site:freemalaysiatoday.com Genting",
    "site:themalaysianreserve.com Genting",
    "site:thesun.my Genting",
    "site:bernama.com Genting",
    "site:focusmalaysia.my Genting",
    "site:businesstoday.com.my Genting",
    "site:klsescreener.com Genting",
    "site:therakyatpost.com Genting",
    "site:thevibes.com Genting",
    "site:themalaysianinsight.com Genting",
    "site:malaysiakini.com Genting",
    "site:edgeprop.my Genting",
    "site:sinardaily.my Genting",
]

# Site-scoped queries run first so the most valuable archive leads are
# available even if the broad sweep is interrupted.
GN_QUERIES = [q for q in GN_QUERIES if q.startswith("site:")] + [
    q for q in GN_QUERIES if not q.startswith("site:")
]

# Second-pass outlet queries: the single site: query per outlet misses items
# ranked below Google's cut, so re-ask with the entity names.
EXTRA_QUERIES = [
    'site:theedgemalaysia.com "Genting Malaysia"',
    "site:theedgemalaysia.com GENM",
    'site:theedgemalaysia.com "Resorts World Genting"',
    'site:theedgemalaysia.com "Genting Bhd"',
    'site:thestar.com.my "Genting Malaysia"',
    "site:thestar.com.my GENM",
    'site:nst.com.my "Genting Malaysia"',
    'site:malaymail.com "Genting Malaysia"',
    'site:freemalaysiatoday.com "Genting Malaysia"',
    'site:themalaysianreserve.com "Genting Malaysia"',
    'site:thesun.my "Genting Malaysia"',
    'site:klsescreener.com "Genting Malaysia"',
    'site:edgeprop.my "Genting Malaysia"',
]

CAP = 90


def load_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return default
    return default


def save_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=0), encoding="utf-8")


def bump(key: str, n: int = 1) -> None:
    s = load_json(STATS, {"requests": {}})
    req = s.setdefault("requests", {})
    req[key] = req.get(key, 0) + n
    save_json(STATS, s)


def add_months(d: date, months: int) -> date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    # All windows start on the 1st/2nd, so day clamping is not needed here.
    return date(y, m, 1)


def quarter_windows() -> list[tuple[date, date]]:
    out = []
    for y in range(2016, 2025):
        for q in range(4):
            s = date(y, q * 3 + 1, 1)
            e = add_months(s, 3)
            s = max(s, date(2016, 11, 2))
            e = min(e, date(2024, 11, 2))
            if s < e:
                out.append((s, e))
    return out


def gn_rss_url(query: str, start: date, end: date) -> str:
    q = f"{query} after:{start:%Y-%m-%d} before:{end:%Y-%m-%d}"
    return (
        "https://news.google.com/rss/search?q="
        + re.sub(r"\s+", "+", q)
        + "&hl=en-MY&gl=MY&ceid=MY:en"
    )


def fetch_window(
    query: str, start: date, end: date, out: dict[str, dict], depth: int = 0
) -> None:
    url = gn_rss_url(query, start, end)
    cp = GN_CACHE / f"{sha1(url)}.xml"
    if cp.exists():
        xml_text = cp.read_text(encoding="utf-8", errors="replace")
    else:
        r = http_get(url, timeout=45)
        bump("google_news_rss")
        if r is None or r.status_code != 200:
            print(f"    FAIL {start}..{end} {query}", flush=True)
            return
        xml_text = r.text
        cp.write_text(xml_text, encoding="utf-8")
        time.sleep(1.2)
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return
    raw_items = root.findall(".//item")
    span_days = (end - start).days
    if len(raw_items) >= CAP and span_days > 6 and depth < 3:
        mid = start + (end - start) / 2
        mid = date(mid.year, mid.month, mid.day)
        if start < mid < end:
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
        if pub is None or not (START_TS <= int(pub.timestamp()) < END_TS):
            continue
        title = (it.findtext("title") or "").strip()
        rec = {
            "google_url": link,
            "google_id": (it.findtext("guid") or "").strip(),
            "title": _y1.strip_publisher(title, source),
            "title_raw": title,
            "source": source,
            "published_utc": int(pub.timestamp()),
            "pub_text": it.findtext("pubDate"),
            "query": query,
            "site_query": query.startswith("site:"),
            "discovered_via": "google_news_deep",
        }
        out.setdefault(link, rec)


def stage_discover() -> None:
    out = {it["google_url"]: it for it in load_json(DISCOVERY, [])}
    before = len(out)
    windows = quarter_windows()
    print(f"{len(GN_QUERIES)} queries x {len(windows)} quarters; starting with {before}", flush=True)
    for qi, q in enumerate(GN_QUERIES, 1):
        for a, b in windows:
            fetch_window(q, a, b, out)
        print(f"[{qi}/{len(GN_QUERIES)}] {q}: total {len(out)} (+{len(out)-before})", flush=True)
        before = len(out)
        # Persist after every query so a later stage can start on a stable
        # snapshot even while the sweep continues.
        items = sorted(out.values(), key=lambda x: x["published_utc"], reverse=True)
        save_json(DISCOVERY, items)
    items = sorted(out.values(), key=lambda x: x["published_utc"], reverse=True)
    save_json(DISCOVERY, items)
    print(f"wrote {len(items)} discovery items -> {DISCOVERY}")
    print("by source:", Counter(x.get("source") for x in items).most_common(25))


# ---------------------------------------------------------------- wordpress ---
WP_SITES = {
    "thesun.my": "https://thesun.my",
    "therakyatpost.com": "https://www.therakyatpost.com",
}


def stage_star_queryly() -> None:
    """The Star's own Queryly search exposes its archive (sort=date, oldest first)."""
    out = {it["google_url"]: it for it in load_json(DISCOVERY, [])}
    before = len(out)
    key = "6ddd278bf17648ac"
    imported = 0
    for page in range(40):
        url = (
            "https://api.queryly.com/json.aspx?queryly_key="
            f"{key}&query=genting&endindex={page*100}&batchsize=100"
            "&showfaceted=false&sort=date&extendeddatafields=creator,pubdate,description"
        )
        r = http_get(url, timeout=40)
        bump("queryly_star")
        if r is None or r.status_code != 200:
            print(f"  Star Queryly page {page}: FAIL", flush=True)
            break
        try:
            data = r.json()
        except Exception:
            print(f"  Star Queryly page {page}: bad JSON", flush=True)
            break
        items = data.get("items") or []
        if not items:
            break
        newest = 0
        oldest = 0
        for it in items:
            ts = int(it.get("pubdateunix") or 0)
            if not ts:
                continue
            newest = max(newest, ts)
            oldest = ts if not oldest else min(oldest, ts)
            if not (START_TS <= ts < END_TS):
                continue
            link = (it.get("link") or "").strip()
            if not link or link in out:
                continue
            out[link] = {
                "google_url": link,
                "google_id": str(it.get("_id") or ""),
                "title": clean_text(it.get("title") or ""),
                "title_raw": it.get("title") or "",
                "source": "The Star",
                "published_utc": ts,
                "pub_text": it.get("pubdate") or "",
                "query": "star_queryly",
                "site_query": True,
                "direct_url": True,
                "discovered_via": "star_queryly",
            }
            imported += 1
        print(
            f"  Star Queryly page {page}: {len(items)} items, "
            f"{datetime.fromtimestamp(oldest, MYT):%Y-%m-%d}.."
            f"{datetime.fromtimestamp(newest, MYT):%Y-%m-%d}, +{len(out)-before} total",
            flush=True,
        )
        save_json(DISCOVERY, sorted(out.values(), key=lambda x: x["published_utc"], reverse=True))
        if oldest and oldest < START_TS:
            break
        time.sleep(1.1)
    print(f"Star Queryly imported {imported} in-window items", flush=True)


def stage_star_queryly_years() -> None:
    """Year-scoped Star searches recover 2016-2019 items the date walk misses."""
    out = {it["google_url"]: it for it in load_json(DISCOVERY, [])}
    before = len(out)
    key = "6ddd278bf17648ac"
    for year in range(2016, 2020):
        for page in range(4):
            url = (
                "https://api.queryly.com/json.aspx?queryly_key="
                f"{key}&query=genting+{year}&endindex={page*100}&batchsize=100"
                "&showfaceted=false&extendeddatafields=creator,pubdate,description"
            )
            r = http_get(url, timeout=40)
            bump("queryly_star_year")
            if r is None or r.status_code != 200:
                print(f"  Star {year} page {page}: FAIL", flush=True)
                break
            try:
                items = r.json().get("items") or []
            except Exception:
                break
            if not items:
                break
            for it in items:
                ts = int(it.get("pubdateunix") or 0)
                if not (START_TS <= ts < END_TS):
                    continue
                link = (it.get("link") or "").strip()
                if not link or link in out:
                    continue
                out[link] = {
                    "google_url": link,
                    "google_id": str(it.get("_id") or ""),
                    "title": clean_text(it.get("title") or ""),
                    "title_raw": it.get("title") or "",
                    "source": "The Star",
                    "published_utc": ts,
                    "pub_text": it.get("pubdate") or "",
                    "query": f"star_queryly_{year}",
                    "site_query": True,
                    "direct_url": True,
                    "discovered_via": "star_queryly_year",
                }
            print(
                f"  Star {year} page {page}: {len(items)} items, +{len(out)-before} total",
                flush=True,
            )
            save_json(DISCOVERY, sorted(out.values(), key=lambda x: x["published_utc"], reverse=True))
            if len(items) < 100:
                break
            time.sleep(1.1)


def stage_discover_extra() -> None:
    out = {it["google_url"]: it for it in load_json(DISCOVERY, [])}
    before = len(out)
    windows = quarter_windows()
    print(f"{len(EXTRA_QUERIES)} extra queries x {len(windows)} quarters; starting with {before}", flush=True)
    for qi, q in enumerate(EXTRA_QUERIES, 1):
        b = len(out)
        for a, end in windows:
            fetch_window(q, a, end, out)
        print(f"[{qi}/{len(EXTRA_QUERIES)}] {q}: +{len(out)-b} (total {len(out)})", flush=True)
        save_json(DISCOVERY, sorted(out.values(), key=lambda x: x["published_utc"], reverse=True))


def stage_wp() -> None:
    session = cffi_requests.Session()
    records: list[dict] = []
    for name, base in WP_SITES.items():
        for term in ("genting", "genm"):
            page = 1
            site_count = 0
            while page <= 20:
                url = (
                    f"{base}/wp-json/wp/v2/posts?search={term}&per_page=100&page={page}"
                    "&after=2016-11-01T00:00:00&before=2024-11-02T00:00:00"
                    "&_fields=id,date,date_gmt,link,title,content,author"
                )
                try:
                    r = session.get(url, impersonate="chrome", timeout=45)
                except Exception as exc:
                    print(f"{name}/{term} page {page}: ERR {exc}", flush=True)
                    break
                bump("wp_api")
                if r.status_code == 400:
                    break
                if r.status_code != 200:
                    print(f"{name}/{term} page {page}: HTTP {r.status_code}", flush=True)
                    break
                try:
                    posts = r.json()
                except Exception:
                    print(f"{name}/{term} page {page}: bad JSON", flush=True)
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
                        try:
                            dt = datetime.fromisoformat(p["date_gmt"]).replace(tzinfo=timezone.utc)
                        except Exception:
                            dt = None
                    if dt is None and p.get("date"):
                        try:
                            dt = datetime.fromisoformat(p["date"]).astimezone(timezone.utc)
                        except Exception:
                            dt = None
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
                            "origin": "wp_api",
                        }
                    )
                    site_count += 1
                if len(posts) < 100:
                    break
                page += 1
                time.sleep(1.2)
            print(f"{name}/{term}: {site_count} posts", flush=True)
    by = {r["url"]: r for r in records if r.get("url")}
    records = list(by.values())
    save_json(WP_POSTS, records)
    print(f"wrote {len(records)} WP posts -> {WP_POSTS}")


# ------------------------------------------------------------------ resolve ---
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


def allowed_source(source: str | None) -> bool:
    s = (source or "").lower()
    return any(h in s for h in ALLOWED_SOURCE_HINTS)


def stage_resolve() -> None:
    items = load_json(DISCOVERY, [])
    state: dict[str, str | None] = load_json(RESOLVED, {})
    todo = [
        it
        for it in items
        if it["google_url"] not in state
        and allowed_source(it.get("source"))
        and (
            TITLE_HINT.search(it.get("title") or "")
            or ALLOW_TITLE.search(it.get("title") or "")
        )
    ]
    print(f"{len(state)} cached, {len(todo)} to resolve", flush=True)
    session = cffi_requests.Session()
    t0 = time.time()
    for i, it in enumerate(todo, 1):
        url = resolve_one(session, it["google_url"])
        state[it["google_url"]] = url
        if i % 50 == 0 or i == len(todo):
            save_json(RESOLVED, state)
            ok = sum(1 for v in state.values() if v)
            print(f"  [{i}/{len(todo)}] resolved={ok} elapsed={time.time()-t0:.0f}s", flush=True)
        time.sleep(0.4)
    save_json(RESOLVED, state)
    good = sum(1 for v in state.values() if v)
    print(f"done: {good}/{len(state)} resolved")


# -------------------------------------------------------------------- fetch ---
SKIP_URL = re.compile(
    r"/(quote|seasonality|chart|charts|marketwatch|stocks?)(/|\?|$)"
    r"|finance\.yahoo\.com/quote/"
    r"|/v2/comment/",
    re.I,
)
NON_NEWS_PATH = re.compile(
    r"^/(tag|tags|author|authors|topic|topics|search|videos|gallery|photos|podcast|podcasts"
    r"|announcements?|category/category)(/|$)",
    re.I,
)
ANNOUNCEMENT_URL = re.compile(r"klsescreener\.com/v2/announcements/", re.I)


NST_NAV = re.compile(
    r"Nation 2027 Budget|HOT FM Kool FM|NST TV NST Podcast|1Klassifieds", re.I
)
BERNAMA_PLACEHOLDER = re.compile(
    r"Please email to\s*digitalsales@bernama\.com|BERNAMA provides up-to-date authentic",
    re.I,
)


def extract_nst_body(html_text: str) -> str | None:
    """Old NST pages embed the story HTML in a JSON blob with HTML entities."""
    for pat in (
        r'body_with_inline(?:&quot;|")\s*:\s*(?:&quot;|")(.*?)'
        r'(?:&quot;|")\s*,\s*(?:&quot;|")(?:word_count|premium|tags|author)',
        r'"body_with_inline"\s*:\s*"(.*?)"\s*,\s*"',
    ):
        m = re.search(pat, html_text, re.S)
        if not m:
            continue
        raw = html.unescape(html.unescape(m.group(1)))
        raw = (
            raw.replace("\\/", "/")
            .replace("\\n", "\n")
            .replace("\\r", "")
            .replace("\\t", " ")
            .replace('\\"', '"')
        )
        txt = strip_tags(raw)
        if len(txt) > 200:
            return txt
    return _y1.extract_nst_body(html_text)


def fetch_one(
    session: cffi_requests.Session,
    url: str,
    google_pub: int | None = None,
    google_title: str | None = None,
) -> dict:
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
        "description": None,
        "extractor": None,
        "paywalled": False,
        "wayback": False,
    }
    if SKIP_URL.search(url) or ANNOUNCEMENT_URL.search(url):
        rec["skip_reason"] = "utility_or_announcement"
        cp.write_text(json.dumps(rec, ensure_ascii=False))
        return rec
    r = http_get(_y1.page_variant(url, domain), session=session, timeout=30, tries=3)
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
    rec["title"] = _y1.get_title(html_text)
    rec["author"] = _y1.get_author(html_text)
    rec["published_utc"] = _y1.get_published(html_text)
    rec["description"] = meta_content(html_text, "description", "og:description", "twitter:description")
    body = _y1.extract_trafilatura(html_text, url)
    if body and len(body) >= 350:
        rec["extractor"] = "trafilatura"
    else:
        alt = _y1.extract_readability(html_text)
        if alt and len(alt) > len(body or ""):
            body, rec["extractor"] = alt, "readability"
        alt = _y1.extract_bs4(html_text)
        if alt and len(alt) > len(body or ""):
            body, rec["extractor"] = alt, "bs4"
    if "nst.com.my" in domain and len(body or "") < 900:
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
                alt = _y1.extract_trafilatura(r2.text, alt_url) or _y1.extract_bs4(r2.text)
                if alt and len(alt) > len(body or ""):
                    body, rec["extractor"] = alt, "trafilatura_amp"
        nst_body = extract_nst_body(html_text)
        if nst_body and (
            len(nst_body) > len(body or "")
            or NST_NAV.search((body or "")[:1200])
            or len(body or "") < 900
        ):
            body, rec["extractor"] = nst_body, "nst_body_json"
        if body and NST_NAV.search(body[:1200]):
            body = ""
    body = _y1.strip_boilerplate(clean_text(body or ""))
    # Some pages block extraction entirely; keep the page description rather
    # than dropping the article, and flag it as truncated.
    if len(body) < 200 and rec["description"]:
        desc = clean_text(rec["description"])
        if len(desc) >= 120:
            body = desc
            rec["extractor"] = "meta_description"
    text_l = html_text.lower()
    if len(body) < 700 and _y1.PAYWALL_MARKERS.search(text_l[-250000:]):
        rec["paywalled"] = True
    if body and _y1.PAYWALL_MARKERS.search(body[-1200:]):
        rec["paywalled"] = True
    if body and BERNAMA_PLACEHOLDER.search(body):
        rec["paywalled"] = True
        rec["truncated"] = True
        rec["skip_reason"] = "paywall_placeholder"
        body = ""
    rec["truncated"] = bool(
        rec.get("truncated") or rec["paywalled"] or rec["extractor"] == "meta_description"
    )
    rec["body"] = body or None
    cp.write_text(json.dumps(rec, ensure_ascii=False))
    return rec


def wayback_fetch(session: cffi_requests.Session, url: str) -> dict | None:
    api = "https://archive.org/wayback/available?url=" + urllib.parse.quote(url, safe="")
    try:
        r = session.get(api, impersonate="chrome", timeout=30)
    except Exception:
        return None
    bump("wayback_api")
    time.sleep(1.2)
    if r.status_code != 200:
        return None
    try:
        snap = (r.json().get("archived_snapshots") or {}).get("closest") or {}
    except Exception:
        return None
    if not snap.get("available") or not snap.get("url"):
        return None
    ts = snap.get("timestamp") or "20200101000000"
    raw_url = f"https://web.archive.org/web/{ts}id_/{url}"
    r2 = http_get(raw_url, session=session, timeout=60, tries=2)
    bump("wayback_fetch")
    time.sleep(1.2)
    if r2 is None or r2.status_code != 200:
        return None
    html_text = r2.text
    body = _y1.extract_trafilatura(html_text, url)
    if not body or len(body) < 350:
        body = _y1.extract_readability(html_text) or _y1.extract_bs4(html_text)
    body = _y1.strip_boilerplate(clean_text(body or ""))
    if len(body) < 200 or BERNAMA_PLACEHOLDER.search(body):
        return None
    return {
        "url": url,
        "final_url": raw_url,
        "http_status": r2.status_code,
        "title": _y1.get_title(html_text),
        "author": _y1.get_author(html_text),
        "published_utc": _y1.get_published(html_text),
        "body": body,
        "description": None,
        "extractor": "wayback",
        "paywalled": False,
        "wayback": True,
        "truncated": False,
    }


def stage_fetch() -> None:
    items = load_json(DISCOVERY, [])
    state = load_json(RESOLVED, {})
    by_url: dict[str, dict] = {}
    for it in items:
        u = state.get(it["google_url"])
        if not u:
            continue
        cu = canonical_url(u)
        if not cu:
            continue
        host = urllib.parse.urlsplit(cu).netloc.lower().replace("www.", "")
        if any(host == h or host.endswith("." + h) for h in EXCLUDED_HOSTS):
            continue
        if not any(host == k or host.endswith("." + k) for k in PUBLISHERS):
            continue
        if NON_NEWS_PATH.search(urllib.parse.urlsplit(cu).path):
            continue
        if not (
            TITLE_HINT.search(it.get("title") or "")
            or ALLOW_TITLE.search(it.get("title") or "")
        ):
            continue
        it = dict(it)
        it["url"] = cu
        prior = by_url.get(cu)
        if prior is None or (it.get("site_query") and not prior.get("site_query")):
            by_url[cu] = it
    cands = list(by_url.values())
    cands.sort(key=lambda x: (urllib.parse.urlsplit(x["url"]).netloc, x["published_utc"]))
    print(f"{len(cands)} candidate URLs", flush=True)

    session = cffi_requests.Session()
    last_hit: dict[str, float] = {}
    out = load_json(FETCHED, [])
    done = {r["url"] for r in out}
    failures = load_json(FAILURES, [])
    fail_by_url = {f["url"]: f for f in failures}
    t0 = time.time()
    for i, it in enumerate(cands, 1):
        if it["url"] in done:
            continue
        domain = urllib.parse.urlsplit(it["url"]).netloc
        wait = 1.15 - (time.time() - last_hit.get(domain, 0))
        if wait > 0:
            time.sleep(wait)
        rec = dict(fetch_one(session, it["url"], it.get("published_utc"), it.get("title")))
        last_hit[domain] = time.time()
        if not rec.get("body"):
            # One polite archive attempt for dead/blocked publisher pages.
            wb = wayback_fetch(session, it["url"]) if rec.get("http_status") in (403, 404, 410) or rec.get("skip_reason") else None
            if wb:
                rec = wb
        rec["google_title"] = it.get("title")
        rec["google_source"] = it.get("source")
        rec["google_published_utc"] = it.get("published_utc")
        rec["google_url"] = it.get("google_url")
        rec["site_query"] = it.get("site_query")
        rec["publisher_hint"] = it.get("source")
        out.append(rec)
        done.add(it["url"])
        if not rec.get("body"):
            fail_by_url[it["url"]] = {
                "url": it["url"],
                "title": it.get("title"),
                "source": it.get("source"),
                "status": rec.get("http_status"),
                "reason": rec.get("skip_reason") or "no_body",
                "published_utc": it.get("published_utc"),
            }
        if i % 25 == 0 or i == len(cands):
            save_json(FETCHED, out)
            save_json(FAILURES, list(fail_by_url.values()))
            ok = sum(1 for r in out if r.get("body"))
            print(
                f"  [{i}/{len(cands)}] {time.time()-t0:.0f}s bodies={ok} "
                f"failures={len(fail_by_url)}",
                flush=True,
            )
    save_json(FETCHED, out)
    save_json(FAILURES, list(fail_by_url.values()))
    s = load_json(STATS, {"requests": {}})
    s["fetch_candidates"] = len(cands)
    s["fetched_records"] = len(out)
    save_json(STATS, s)
    ok = sum(1 for r in out if r.get("body"))
    short = sum(1 for r in out if r.get("body") and len(r["body"]) < 500)
    print(
        f"done: {ok} with body, {short} short, "
        f"{sum(1 for r in out if r.get('paywalled'))} paywalled, {len(fail_by_url)} failures"
    )


# -------------------------------------------------------------------- build ---
SUBSIDIARY_ONLY = re.compile(
    r"genting plantations?|\bgenp\b|genting singapore|\bg13\b|genting hong kong|"
    r"genting hk\b|gentinghk|genting property|genting cruise|dream cruises|genting dream|"
    r"cruise line|resorts world cruises|resorts world sentosa|"
    r"genting hotel in singapore|\brws\b|travellers international|ho wah genting",
    re.I,
)
PARENT_MARKER = re.compile(
    r"genting berhad|genting bhd|genting malaysia|\bgenm\b|\b3182\b|\b4715\b|"
    r"genting (group|overseas|conglomerate)|genting[,&]|genting and",
    re.I,
)
ROUNDUP = re.compile(
    r"^(top stock market|fbm klci climbs|genting leads bulls|lifts bursa at the open|"
    r"bursa (rises|slips|opens|closes|ends|lower|higher)|market close|market open|"
    r"midday|closing bell|morning brief)|top gainers|top losers|stocks? with momentum|"
    r"trading ideas|companies in the news|brokers digest",
    re.I,
)
OFF_TOPIC = re.compile(
    r"afa infrastructure|toll collection|expressway concession|ho wah genting|genting hk|"
    r"genting sempah|genting tunnel|batang kali|karak highway|\blpt\b|"
    r"genting premium outlet|technical charting|technical analysis|"
    r"annual report & cg report|universal studios|property in genting|genting klang|"
    r"genting valley|winter wonderland|nak pergi|ada plan nak pergi|perkara penting|"
    r"finishing touches|private jet into africa|genting land deal|sold genting land|"
    r"genting ups the lifestyle game|help shore up klci|haunted hotel|"
    r"aladdin and the magic lamp|\bmigf\b|"
    r"from genting chief|malton.*genting land|"
    r"genting chairman launches new singapore venture",
    re.I,
)
# A corporate/financial signal strong enough to override the generic
# place/lifestyle/incident keyword screens below.
CORP_STRONG = re.compile(
    r"profit|loss|revenue|earnings?|results?|quarter|\bq[1-4]\b|dividend|debt|bond|"
    r"sukuk|loan|borrow|rating|fitch|moody|credit|target price|analyst|upgrade|"
    r"downgrade|share|stock|stake|acquire|acquisition|dispose|divest|sell|buy|"
    r"takeover|merger|privatis|buyout|rights issue|placement|ipo|delist|impair|"
    r"capex|investment|invest|expand|expansion|joint venture|\bjv\b|partnership|"
    r"collaborat|mou|contract|concession|licen[cs]e|casino|gaming|integrated resort|"
    r"theme park|resort|hotel|business|recovery|reopen|closure|shut|layoff|retrench|"
    r"manpower|staff|ceo|cfo|chairman|board|appoint|resign|agm|egm|shareholder|"
    r"financial|bankruptcy|default|restructur|litigation|lawsuit|sue|claim|"
    r"arbitration|tribunal|fine|penalty|tax|duty|levy|asset|sale|lease|new york|"
    r"miami|bimini|bahamas|london|\buk\b|egypt|indonesia|india|macau",
    re.I,
)
# Incident/crime copy set in or near Genting Highlands is not company news.
CRIME_INCIDENT = re.compile(
    r"crash|accident|\bfire\b|landslide|tree falls?|tumbang|hempap|robbery|heist|"
    r"murder|killed|dead|drown|police|arrest|nabbed|detain|charged|didakwa|curi|"
    r"pecah masuk|samun|rompak|\brob\b|robbed|raiders|armed|missing|flood|traffic|"
    r"\bbus\b|\broad\b|highway|toll",
    re.I,
)
# Leisure/place copy: only kept when the headline also carries a corporate angle.
PLACE_EVENT = re.compile(
    r"eatery|restaurant|\bfood\b|burger|dining|concert|singer|festival|\bevent\b|"
    r"promo|ticket|staycation|\bvisit\b|\btour\b|cycling|ltdl|attraction|tourism|"
    r"tourist|visitor|holiday|travel|\bmall\b|residence|condo|housing|\bcbd\b|"
    r"king.s park|tiger|wildlife|vaccination|badminton|olympic|durian|experience|"
    r"f&b|sustainability|theme park ride|roller coaster|zouk|nightclub|\bbash\b|"
    r"fiesta|valentine|spreads cheer|\bchildren\b|^entertainment:|^party\b|"
    r"#showbiz|to perform|entertain fans|making her|careers open day|year of|"
    r"celebrate the year|discover fun|fun with|local talents|high note|seafood|"
    r"wantau|five guys|tropicana|windcity|drive to genting|oil palm|greenpeace|"
    r"kopitiam|chee cheong fun|train to busan|cinema|film distributor|"
    r"movie premiere|grand banks yachts|"
    r"^here.s what|^what.s open|^first look|^a look|^photos?\b|^video\b|^watch\b|"
    r"^inside\b|^review\b",
    re.I,
)
PLACE_ONLY = re.compile(r"genting highlands", re.I)
OPERATING_MARKER = re.compile(
    r"genting (berhad|bhd|malaysia|group)|genm|resorts? world|\brwg\b|casino|gaming|"
    r"theme park|integrated resort",
    re.I,
)
FIN_OVERRIDE = re.compile(
    r"\bprofit|\bloss|revenue|earnings?|results?|quarter|\bq[1-4]\b|dividend|\bdebt\b|"
    r"\bbond\b|sukuk|\bloan|borrow|\brating\b|fitch|moody|target price|analyst|\bupgrade|"
    r"\bdowngrade|\bshares?\b|\bstocks?\b|\bstake\b|acquire|acquisition|dispose|"
    r"divest|\bsell\b|\bbuy\b|takeover|merger|privatis|buyout|rights issue|capex|"
    r"investment|\binvest|\bexpand|joint venture|partnership|\bmou\b|\bcontract|"
    r"licen[cs]e|bankruptcy|default|restructur|litigation|lawsuit|\bsue\b|"
    r"\bclaim\b|\bfine\b|penalty|\btax\b",
    re.I,
)


# The base relevance filter treats "theme park", "hotel" and "court" as
# lifestyle/place signals. These overrides keep stories where those words are
# part of a genuine corporate, legal or boardroom story.
CORP_RESCUE = re.compile(
    r"\bboard\b|\bdirector\b|\bcfo\b|\bceo\b|deputy chairman|chairman|resign|"
    r"retire|appoint|\bnamed\b|ordered to pay|\bpay\b|sued|lawsuit|settlement|"
    r"tribunal|damages|\bfine\b|acquire|acquisition|\bsell\b|\bsale\b|\bstake\b|"
    r"equity|injection|disposal|\bland\b|invest|investment|RM\d|\bbillion\b|"
    r"\bmillion\b|earnings|profit|revenue|quarter|analyst|target price|\brating\b|"
    r"upgrade|downgrade|theme park|skyworlds|casino|reopen|closure",
    re.I,
)
PROMO = re.compile(
    r"tips|what to expect|sneak peek|guide|review|\bvisit\b|ticket|\bdeals?\b|"
    r"pricing|picturesque|temple|stuck|victim|what.s new|things to know|here.s|"
    r"concert|singer|showbiz|\bfood\b|restaurant|seafood|staycation|"
    r"rooms in genting|trip to genting|fun in genting|snowfall|blaze|stolen|"
    r"naked|brawl|robbery|theft|charged|crash|accident|landslide|\bfire\b|"
    r"\bbus\b|\broad\b|toll|traffic|tunnel|ecrl|property|residence|condo|"
    r"premium outlet|cable car|trip\b",
    re.I,
)


def fix_mojibake(text: str) -> str:
    """Undo common UTF-8-as-Latin-1 damage in older WordPress bodies."""
    text = text or ""
    if re.search(r"â€|Ã|Â", text):
        try:
            text = text.encode("latin-1").decode("utf-8")
        except Exception:
            pass
    for bad, good in (
        ("â€TM", "'"),
        ("â€ ̃", "'"),
        ("â€˜", "'"),
        ("â€œ", '"'),
        ("â€\u009d", '"'),
        ("â€“", "-"),
        ("â€”", "—"),
        ("â€¦", "…"),
        ("Â ", " "),
    ):
        text = text.replace(bad, good)
    return text


def local_publisher_for(url: str):
    host = urllib.parse.urlsplit(url).netloc.lower().replace("www.", "")
    if any(host == h or host.endswith("." + h) for h in EXCLUDED_HOSTS):
        return None
    for key, val in PUBLISHERS.items():
        if host == key or host.endswith("." + key):
            return val
    return None


def load_candidates() -> list[dict]:
    out = []
    for r in load_json(FETCHED, []):
        if not r.get("body") or r.get("skip_reason"):
            continue
        out.append(
            {
                "url": r["url"],
                "title": r.get("title") or r.get("google_title"),
                "author": r.get("author"),
                "published_utc": r.get("published_utc") or r.get("google_published_utc"),
                "google_published_utc": r.get("google_published_utc"),
                "body": r["body"],
                "publisher_hint": r.get("publisher_hint"),
                "origin": "fetch",
                "extractor": r.get("extractor"),
                "paywalled": bool(r.get("paywalled")),
                "truncated": bool(r.get("truncated")),
                "wayback": bool(r.get("wayback")),
                "google_url": r.get("google_url"),
                "google_title": r.get("google_title"),
            }
        )
    for r in load_json(WP_POSTS, []):
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
                "truncated": False,
                "wayback": False,
                "google_url": None,
                "google_title": None,
            }
        )
    return out


def stage_build() -> None:
    raw = load_candidates()
    print(f"loaded {len(raw)} candidate records")
    stats = Counter()
    rejected = []
    kept: dict[str, dict] = {}
    for rec in raw:
        url = canonical_url(rec["url"] or "")
        if not url or not url.startswith("http"):
            stats["bad_url"] += 1
            continue
        pm = local_publisher_for(url)
        if not pm:
            stats["unmapped_publisher"] += 1
            rejected.append({"url": url, "title": rec.get("title"), "reason": "unmapped_publisher"})
            continue
        source, publisher, priority = pm
        path = urllib.parse.urlsplit(url).path
        if NON_NEWS_PATH.search(path) or ANNOUNCEMENT_URL.search(url):
            stats["non_news_path"] += 1
            continue
        ts = rec.get("published_utc")
        if not ts:
            stats["no_timestamp"] += 1
            continue
        ts = int(ts)
        if not (START_TS <= ts < END_TS):
            gts = rec.get("google_published_utc")
            if gts and START_TS <= int(gts) < END_TS:
                ts = int(gts)
            else:
                stats["out_of_window"] += 1
                continue
        title = _y1.clean_title(fix_mojibake(rec.get("title") or ""))
        body = _y1.strip_publisher_boilerplate(
            clean_text(fix_mojibake(rec.get("body") or ""))
        )
        if len(body) < 200:
            stats["too_short"] += 1
            rejected.append({"url": url, "title": title, "reason": "too_short", "len": len(body)})
            continue
        if len(title) < 8:
            stats["short_title"] += 1
            rejected.append({"url": url, "title": title, "reason": "short_title"})
            continue
        if ANNOUNCEMENT_URL.search(url) or re.match(r"^(GENTING|GENM)\s*-\s", title):
            stats["bursa_announcement"] += 1
            rejected.append({"url": url, "title": title, "reason": "bursa_announcement"})
            continue
        if OFF_TOPIC.search(title) or ROUNDUP.search(title):
            stats["reject_roundup"] += 1
            rejected.append({"url": url, "title": title, "reason": "roundup"})
            continue
        if re.search(
            r"slot machine|jackpot|winnings|wheel of prosperity|casino chip theft|"
            r"chip theft|strike on .*slot",
            title,
            re.I,
        ):
            stats["reject_gambling_win"] += 1
            rejected.append({"url": url, "title": title, "reason": "gambling_win"})
            continue
        allowed_title = bool(ALLOW_TITLE.search(title))
        if not allowed_title and not re.search(
            r"genting|genm|3182|4715|resorts? world|\brwg\b", title, re.I
        ):
            stats["reject_no_subject"] += 1
            rejected.append({"url": url, "title": title, "reason": "no_company_in_title"})
            continue
        if re.match(r"^(GENM|GENTING)\s*[-–:]?\s*(4715|3182)?$", title, re.I):
            stats["reject_ticker_page"] += 1
            rejected.append({"url": url, "title": title, "reason": "ticker_page"})
            continue
        if SUBSIDIARY_ONLY.search(title) and not PARENT_MARKER.search(title):
            stats["reject_subsidiary"] += 1
            rejected.append({"url": url, "title": title, "reason": "subsidiary_only"})
            continue
        if CRIME_INCIDENT.search(title) and not FIN_OVERRIDE.search(title):
            stats["reject_incident"] += 1
            rejected.append({"url": url, "title": title, "reason": "incident/crime"})
            continue
        if PLACE_ONLY.search(title) and not OPERATING_MARKER.search(title):
            stats["reject_place_only"] += 1
            rejected.append({"url": url, "title": title, "reason": "place_only"})
            continue
        if PLACE_EVENT.search(title) and not FIN_OVERRIDE.search(title):
            stats["reject_place_event"] += 1
            rejected.append({"url": url, "title": title, "reason": "place_event"})
            continue
        if _y1.JUNK_TITLE.search(title) and not (
            CORP_STRONG.search(title) or _y1.FIN_STRONG.search(title)
        ):
            stats["reject_place_event"] += 1
            rejected.append({"url": url, "title": title, "reason": "place_event"})
            continue
        if body.lower().lstrip().startswith("risk disclaimer") or BERNAMA_PLACEHOLDER.search(body):
            stats["reject_boilerplate_body"] += 1
            rejected.append({"url": url, "title": title, "reason": "boilerplate_body"})
            continue
        ok, why = _y1.relevance_y1(title, body)
        if not ok and allowed_title:
            ok, why = True, "ok"
            stats["rescued_allow_title"] += 1
        if (
            not ok
            and why == "estate/family dispute"
            and re.search(r"founder.s widow dies|lim siew kim.*dies", title, re.I)
        ):
            ok, why = True, "ok"
            stats["rescued_obituary"] += 1
        if (
            not ok
            and why
            in {
                "lifestyle/place",
                "place/policy story",
                "passing mention",
                "event/entertainment",
                "estate/family dispute",
            }
            and CORP_RESCUE.search(title)
            and not PROMO.search(title)
        ):
            ok, why = True, "ok"
            stats["rescued_relevance"] += 1
        if not ok:
            stats[f"reject_{why.replace(' ', '_')}"] += 1
            rejected.append({"url": url, "title": title, "reason": why})
            continue
        tickers = _y1.tickers_y1(title, body)
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
            "lang": _nb.detect_lang(body),
            "raw": {
                "publisher": publisher,
                "origin": rec.get("origin"),
                "extractor": rec.get("extractor"),
                "paywalled": bool(rec.get("paywalled")),
                "truncated": bool(rec.get("truncated") or rec.get("paywalled")),
                "wayback": bool(rec.get("wayback")),
                "priority": priority,
                "malaysian_publisher": True,
                "full_text_chars": len(body),
            },
        }
        if rec.get("google_url"):
            out["raw"]["google_news_url"] = rec["google_url"]
        prior = kept.get(url)
        if prior is None:
            kept[url] = out
        else:
            stats["duplicate_url"] += 1
            if len(out["body"]) > len(prior["body"]):
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
    save_json(REJECTED, rejected)
    s = load_json(STATS, {"requests": {}})
    s["build"] = dict(stats)
    s["candidates_loaded"] = len(raw)
    s["written"] = len(final)
    save_json(STATS, s)
    print(f"wrote {len(final)} articles -> {OUT_JSONL}")
    print("stats:", dict(stats))
    for k, v in Counter(r["channel"] for r in final).most_common():
        print(f"  {v:3d} {k}")
    print("by ticker:", Counter(t for r in final for t in r["tickers"]))


# ------------------------------------------------------------------- report ---
def fmt_myt(ts: int) -> str:
    return datetime.fromtimestamp(ts, MYT).strftime("%Y-%m-%d %H:%M MYT")


def stage_report() -> None:
    recs = [json.loads(line) for line in OUT_JSONL.open(encoding="utf-8") if line.strip()]
    stats = load_json(STATS, {})
    build_stats = stats.get("build", {})
    req = stats.get("requests", {})
    failures = load_json(FAILURES, [])
    pub = Counter(r["channel"] for r in recs)
    tick = Counter(t for r in recs for t in r["tickers"])
    months = Counter(datetime.fromtimestamp(r["published_utc"], MYT).strftime("%Y-%m") for r in recs)
    years = Counter(datetime.fromtimestamp(r["published_utc"], MYT).strftime("%Y") for r in recs)
    truncated = [r for r in recs if (r.get("raw") or {}).get("truncated")]
    paywalled = [r for r in recs if (r.get("raw") or {}).get("paywalled")]
    wayback = [r for r in recs if (r.get("raw") or {}).get("wayback")]
    full = [r for r in recs if len(r["body"]) >= 800 and not (r.get("raw") or {}).get("truncated")]
    full500 = [r for r in recs if len(r["body"]) >= 500 and not (r.get("raw") or {}).get("truncated")]
    bodies = sorted(len(r["body"]) for r in recs) or [0]
    ts = [r["published_utc"] for r in recs]
    failure_reasons = Counter(f.get("reason") or "unknown" for f in failures)
    failure_sources = Counter(f.get("source") or "?" for f in failures)
    dedupe_total = sum(
        build_stats.get(k, 0) for k in ("duplicate_url", "duplicate_body", "near_dup_title")
    )

    lines = [
        "# Genting news collection — 2 Nov 2016 to 1 Nov 2024",
        "",
        "Window: **2 Nov 2016 00:00 MYT → 1 Nov 2024 23:59:59 MYT** "
        f"(`{START_TS}`–`{END_TS - 1}` epoch UTC, half-open).",
        "",
        "## Summary",
        "",
        f"- Articles written: **{len(recs)}**",
        f"- Discovery links (all sources): **{len(load_json(DISCOVERY, []))}**; "
        f"unique mapped candidate URLs: **{stats.get('fetch_candidates', 0)}**",
        f"- Candidate page results stored: **{len(load_json(FETCHED, []))}**",
        f"- Tickers (an article can carry both): "
        + ", ".join(f"{k} {v}" for k, v in tick.most_common()),
        f"- Date range: **{fmt_myt(min(ts))} → {fmt_myt(max(ts))}**" if ts else "- Date range: n/a",
        f"- Full-text rate (body ≥800 chars, not truncated): **{len(full)}/{len(recs)} "
        f"({len(full)/max(len(recs),1):.1%})**; body ≥500 chars: "
        f"**{len(full500)}/{len(recs)} ({len(full500)/max(len(recs),1):.1%})**",
        f"- Truncated / paywalled records: **{len(truncated)}** "
        f"(paywalled flag: {len(paywalled)}, archived via Wayback: {len(wayback)})",
        f"- Body length: min {bodies[0]}, median {bodies[len(bodies)//2]}, max {bodies[-1]} chars",
        f"- Authors present: {sum(1 for r in recs if r.get('author'))}/{len(recs)}",
        f"- Deduped candidates removed: **{dedupe_total}** "
        f"(URL {build_stats.get('duplicate_url', 0)}, body {build_stats.get('duplicate_body', 0)}, "
        f"near-title {build_stats.get('near_dup_title', 0)})",
        f"- Candidate pages with no retained body: **{len(failures)}** ("
        + ", ".join(f"{k} {v}" for k, v in failure_reasons.most_common())
        + ")",
        "",
        "## Requests made",
        "",
    ]
    for k, v in sorted(req.items()):
        lines.append(f"- {k}: {v}")
    lines += ["", "## Articles by publisher", "", "| Publisher | Articles |", "|---|---:|"]
    for k, v in pub.most_common():
        lines.append(f"| {k} | {v} |")
    lines += ["", "## Articles by year (MYT)", "", "| Year | Articles |", "|---|---:|"]
    for y in range(2016, 2025):
        lines.append(f"| {y} | {years.get(str(y), 0)} |")
    lines += ["", "## Articles by month (MYT)", "", "| Month | Articles |", "|---|---:|"]
    cur = date(2016, 11, 1)
    while cur < date(2024, 11, 1):
        key = cur.strftime("%Y-%m")
        lines.append(f"| {key} | {months.get(key, 0)} |")
        cur = add_months(cur, 1)
    lines += ["", "## Candidate filtering", "", "| Reason dropped | Candidates |", "|---|---:|"]
    for k, v in Counter(build_stats).most_common():
        if k.startswith("reject_") or k in {
            "too_short", "short_title", "no_timestamp", "out_of_window", "non_news_path",
            "unmapped_publisher", "no_ticker", "bursa_announcement", "bad_url",
            "reject_ticker_page",
        }:
            lines.append(f"| {k} | {v} |")
    lines += ["", "## Fetch failures", "", "| Reason | Articles |", "|---|---:|"]
    for k, v in failure_reasons.most_common():
        lines.append(f"| {k} | {v} |")
    if failure_sources:
        lines += ["", "| Source hint | Failures |", "|---|---:|"]
        for k, v in failure_sources.most_common(20):
            lines.append(f"| {k} | {v} |")
    lines += ["", "## Method", ""]
    lines += [
        "- Discovery: Google News RSS (`hl=en-MY&gl=MY&ceid=MY:en`) using entity, "
        "finance and outlet-scoped queries, walked across "
        f"{len(quarter_windows())} quarter windows; any slice hitting the ~{CAP}-item "
        "RSS cap was split recursively.",
        "- Redirect resolution: Google News batchexecute decoder to canonical publisher URL.",
        "- Full text: trafilatura, readability and BeautifulSoup fallbacks; The Star `?s=app`, "
        "NST AMP and NST embedded-body JSON; page meta description only as a last-resort "
        "truncated fallback.",
        "- The Sun and The Rakyat Post were additionally queried through their public "
        "WordPress REST APIs. The Star archive was walked through its public Queryly "
        "search API (3,190 indexed matches), which yielded 2020-2024 items that Google "
        "News had ranked below the cut.",
        "- Dedupe: canonical URL, then exact body hash, then title similarity ≥0.90.",
        "- Politeness: ≥1.15 s per host for article fetches, 1.2 s for Google News RSS, "
        "0.4 s for redirect resolution, exponential backoff on 429/5xx.",
        "",
        "## Gaps and caveats",
        "",
    ]
    all_months = []
    cur = date(2016, 11, 1)
    while cur < date(2024, 11, 1):
        all_months.append(cur.strftime("%Y-%m"))
        cur = add_months(cur, 1)
    zero = [m for m in all_months if months.get(m, 0) == 0]
    thin = [m for m in all_months if 0 < months.get(m, 0) < 3]
    if zero:
        lines.append(f"- Months with no recovered articles ({len(zero)}): {', '.join(zero)}.")
    if thin:
        lines.append(
            f"- Thin months with 1–2 articles ({len(thin)}): "
            + ", ".join(f"{m} ({months[m]})" for m in thin)
            + "."
        )
    lines += [
        "- Google News RSS indexes only what it has crawled. 2016–2019 coverage is much "
        "thinner than 2020–2024, so the total is a floor rather than a census.",
        "- Bernama serves only a subscription notice on every article page, and "
        "BusinessToday / EdgeProp returned HTTP 403 to the article fetcher; those pages "
        "were dropped rather than storing non-article text, and are counted in the fetch "
        "failure table. Nine of those entries are deliberate exclusions of KLSE Screener "
        "announcement/utility pages rather than retrieval failures. No record in this file "
        "needed a `raw.truncated=true` flag because no partial body was retained without a "
        "usable article lead.",
        "- Genting Singapore, Genting Plantations, Genting Hong Kong/cruise and other "
        "separately listed Genting entities are excluded unless the story is explicitly "
        "about Genting Berhad or Genting Malaysia.",
        "- Place/lifestyle/concert copy set in Genting Highlands is excluded. KLSE Screener "
        "bursa announcements are excluded; its news pages are retained when they carry an "
        "article body.",
        "- Dates come from publisher metadata where present, otherwise from the Google News "
        "`pubDate` (which is often date-only, normalised to 08:00 UTC).",
        "",
    ]
    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote report -> {OUT_REPORT}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "stage",
        choices=[
            "discover", "discover_extra", "star_queryly", "star_queryly_years", "wp",
            "resolve", "fetch", "build", "report", "all"
        ],
    )
    args = ap.parse_args()
    if args.stage in ("discover", "all"):
        stage_discover()
    if args.stage in ("discover_extra", "all"):
        stage_discover_extra()
    if args.stage in ("star_queryly", "all"):
        stage_star_queryly()
    if args.stage in ("star_queryly_years", "all"):
        stage_star_queryly_years()
    if args.stage in ("wp", "all"):
        stage_wp()
    if args.stage in ("resolve", "all"):
        stage_resolve()
    if args.stage in ("fetch", "all"):
        stage_fetch()
    if args.stage in ("build", "all"):
        stage_build()
    if args.stage in ("report", "all"):
        stage_report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
