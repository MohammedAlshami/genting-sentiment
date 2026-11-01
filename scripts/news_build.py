#!/usr/bin/env python3
"""Stage 4: merge sources, filter to substantive Genting coverage, dedupe, write JSONL."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from news_lib import (  # noqa: E402
    CACHE,
    DATA,
    GENM_OPS,
    GENTING_STRONG,
    GENTING_WEAK,
    MARKET_ROUNDUP,
    TRAVEL,
    canonical_url,
    clean_text,
    sha1,
    title_similarity,
)

# Malaysian local window: 2 Nov 2025 00:00 MYT -> 2 Nov 2026 23:59:59 MYT.
START_TS = int(datetime(2025, 11, 1, 16, 0, tzinfo=timezone.utc).timestamp())
END_TS = int(datetime(2026, 11, 2, 16, 0, tzinfo=timezone.utc).timestamp())

PUBLISHERS = {
    "theedgemalaysia.com": ("news_theedge", "The Edge Malaysia", 1),
    "thestar.com.my": ("news_thestar", "The Star", 1),
    "charts.thestar.com.my": ("news_thestar", "The Star", 3),
    "nst.com.my": ("news_nst", "New Straits Times", 1),
    "malaymail.com": ("news_malaymail", "Malay Mail", 1),
    "freemalaysiatoday.com": ("news_fmt", "Free Malaysia Today", 1),
    "themalaysianreserve.com": ("news_malaysianreserve", "The Malaysian Reserve", 1),
    "thesun.my": ("news_thesun", "The Sun Malaysia", 1),
    "bernama.com": ("news_bernama", "Bernama", 1),
    "bernamabiz.com": ("news_bernama", "Bernama", 1),
    "ram.com.my": ("news_ramratings", "RAM Ratings", 1),
    "focusmalaysia.my": ("news_focusmalaysia", "Focus Malaysia", 1),
    "klsescreener.com": ("news_klsescreener", "KLSE Screener", 4),
    "businesstoday.com.my": ("news_businesstoday", "BusinessToday Malaysia", 1),
    "therakyatpost.com": ("news_therakyatpost", "The Rakyat Post", 1),
    "edgeprop.my": ("news_edgeprop", "EdgeProp Malaysia", 1),
    "thevibes.com": ("news_thevibes", "The Vibes", 1),
    "themalaysianinsight.com": ("news_themalaysianinsight", "The Malaysian Insight", 1),
    "malaysiakini.com": ("news_malaysiakini", "Malaysiakini", 1),
    "sinardaily.my": ("news_sinardaily", "Sinar Daily", 1),
    "thestar.com": ("news_thestar", "The Star", 1),
    "businesstimes.com.sg": ("news_businesstimes", "The Business Times", 2),
    "straitstimes.com": ("news_straitstimes", "The Straits Times", 2),
    "theedgesingapore.com": ("news_theedgesingapore", "The Edge Singapore", 2),
    "ggrasia.com": ("news_ggrasia", "GGRAsia", 2),
    "asgam.com": ("news_asgam", "Asia Gaming Brief", 2),
    "agbrief.com": ("news_agbrief", "Asia Gaming Brief", 2),
    "cdcgaming.com": ("news_cdcgaming", "CDC Gaming Reports", 2),
    "igamingbusiness.com": ("news_igamingbusiness", "iGaming Business", 2),
    "focusgn.com": ("news_focusgn", "Focus Gaming News", 2),
    "ggbmagazine.com": ("news_ggbmagazine", "GGB Magazine", 2),
    "scmp.com": ("news_scmp", "South China Morning Post", 2),
    "asia.nikkei.com": ("news_nikkei", "Nikkei Asia", 2),
    "bloomberg.com": ("news_bloomberg", "Bloomberg", 3),
    "reuters.com": ("news_reuters", "Reuters", 2),
    "yahoo.com": ("news_yahoo", "Yahoo Finance", 3),
    "says.com": ("news_says", "Says", 2),
    "varnam.my": ("news_varnam", "Varnam Malaysia", 2),
    "therakyatpost.com": ("news_therakyatpost", "The Rakyat Post", 1),
    "malaysia.news.yahoo.com": ("news_yahoo", "Yahoo Malaysia", 3),
    "sg.finance.yahoo.com": ("news_yahoo", "Yahoo Finance Singapore", 3),
}

# Directories / categories that are not news articles. Note that some publishers
# (e.g. Free Malaysia Today) put every article under /category/, so that segment
# must not be treated as a listing page.
NON_NEWS_PATH = re.compile(
    r"^/(tag|tags|author|authors|topic|topics|search|videos|gallery|photos|podcast|podcasts)(/|$)",
    re.I,
)

SUBSIDIARY_ONLY = re.compile(r"genting plantations|genp\b|genting singapore|gens\b|g13\b", re.I)
PLACE_ONLY = re.compile(r"genting\s+(tunnel|sempah|highlands road|premium outlet)|lpt|karak highway", re.I)
FIN_CONTEXT = re.compile(
    r"bursa|share|stock|rights issue|debt|bond|earning|profit|loss|revenue|dividend|"
    r"rating|fitch|moody|s&p|capital|takeover|privatis|acquisition|divest|stake|market|"
    r"results|quarter|financial|borrow|leverage|valuation|ipo|investor|analyst|"
    r"casino|resort|gaming|licence|license|new york|sentosa|rwg|genm|genting bhd|"
    r"upgrade|downgrade|target price|buy|sell|expansion|invest|collaborat|partnership|"
    r"joint venture|mou|memorandum|agreement|deal|brand value|net loss|net profit",
    re.I,
)
ESTATE = re.compile(
    r"estate|inheritance|heiress|founder|grandson|granddaughter|grandchild|trustee|court|trial|"
    r"administrator|family dispute|saga|will dispute|bequest|siew kim",
    re.I,
)
CRIME = re.compile(
    r"heist|robbery|arrest|nabbed|detain|kidnap|assault|police|cops?\b|drug|summons|"
    r"pile-up|accident|fire\b|killed|dead|murder|smuggl|gambling den",
    re.I,
)
EVENT = re.compile(
    r"concert|festival|showcase|arena of stars|lineup|line-up|music|party|techno|singer|"
    r"celebrat|showbiz|summit",
    re.I,
)
ROUNDUP = re.compile(
    r"trading ideas|companies in the news|brokers digest|stocks? with momentum|"
    r"top gainers|top losers|market close|market open|midday|bursa malaysia "
    r"(rises|slips|opens|closes|ends|lower|higher)|local equities|equities brief|"
    r"warrants|stock watch|market watcher|morning brief|closing bell",
    re.I,
)
PLACE_STORY = re.compile(
    r"\btoll\b|road charge|road fee|road privatisation|road safety|road project|\broad upgrade|"
    r"highway|traffic|property market|property project|entry fee|entry charge|access charge|"
    r"vehicle charge|vehicle entry|road users|tolls?\b|access road|concessionaire|"
    r"\bcaj\b|\btol\b|jalan genting|"
    r"\bmall\b|restaurant|buffet|scholarship|hotel|theme park|attraction|tourism|"
    r"homestay|residence|condo|housing|project(s)? meet|substation|waterfront",
    re.I,
)
NON_LISTED = re.compile(
    r"genting plantations|genting singapore|genting property|genting xintiandi|"
    r"genting sempah|genting tunnel|genting construction",
    re.I,
)
CORP_VERB = re.compile(
    r"propos|raise|divest|sell|buy|acquire|take over|takeover|privatis|post|report|"
    r"earn|issue|launch|sign|partner|develop|appoint|name|cut|downgrade|upgrade|"
    r"fall|rise|slip|surge|plunge|tumble|jump|drop|gain|lose|hit|face|seek|plan|"
    r"wins?|gets?|lands?|opens?|build|invest|return|pay|declare|complete",
    re.I,
)
LIFESTYLE = re.compile(
    r"scholarship|travel award|leading resort|wins? .*award|named .*resort|"
    r"cny in the sky|\bcny\b|care bears|fabulous fruits|buffet|dinner|food|restaurant|"
    r"sunset by neon|spookadilly|chin swee|temple|deity|kom genting|roller coaster|"
    r"road safety|slopes|bus driver|"
    r"rich list|richest|forbes|scion|university of life|viral video|quickcheck|"
    r"mcmc busts|goldsmith|robbery|heist|crash|incident|theme park|concert|"
    r"foreign fund flow|ipo oversubscribed|ho wah genting|genting hk|travellers international|"
    r"resorts world sentosa|\brws\b|tropicana|mercure|accor|"
    r"take note|things coming into effect|polis|ditumbuk|ditahan|samun|rompak",
    re.I,
)
TITLE_SUFFIXES = [
    "New Straits Times Online",
    "New Straits Times",
    "The Star Online",
    "The Star",
    "The Edge Malaysia",
    "The Edge Singapore",
    "Malay Mail",
    "Free Malaysia Today",
    "The Sun Malaysia",
    "The Sun",
    "Bernama",
    "Focus Malaysia",
    "The Malaysian Reserve",
    "EdgeProp.my",
    "GGRAsia",
    "Asia Gaming Brief",
    "CDC Gaming Reports",
    "CDC Gaming",
    "The Business Times",
    "The Straits Times",
    "Nikkei Asia",
    "Yahoo Finance",
    "KLSE Screener",
    "AGB",
]


def clean_title(title: str) -> str:
    t = clean_text(title or "")
    for s in TITLE_SUFFIXES:
        for sep in (" - ", " | ", " – ", " — ", " -", " |"):
            suffix = f"{sep}{s}"
            if t.endswith(suffix):
                t = t[: -len(suffix)].strip()
                break
    return t.strip()


def strip_publisher_boilerplate(body: str) -> str:
    """Remove subscribe/related-link furniture that trafilatura keeps."""
    body = re.sub(r"^\s*Advertisement\s+", "", body, flags=re.I)
    body = re.sub(r"\s*Select Voice\s+Select Speed.*$", "", body, flags=re.S | re.I)
    # Related-article block at the end (The Edge).
    idx = body.rfind("\nRead also:")
    if idx > len(body) * 0.6:
        body = body[:idx]
    patterns = [
        r"\nFollow us on Facebook and join our Telegram channel.*$",
        r"\nFollow our channels to receive property news updates.*$",
        r"\nFollow us on social media\s*:.*$",
        r"\nFollow us on our official\s*\n?WhatsApp channel.*$",
        r"\nTags / Keywords:.*$",
        r"\nReport a mistake.*$",
        r"\nRelated News\s*\n.*$",
        r"\nThis article first appeared in The Malaysian Reserve weekly print edition.*$",
        r"\nWritten byAGBrief Editorial.*$",
        r"\nMore from AGBrief Editorial.*$",
        r"^Daily Asia Gaming eBrief:[^\n]*\n",
        r"^Jangan lupa follow channel Telegram[^\n]*\n?",
        r"\n\.{5,}\s*\nEdgeProp monthly brings you.*$",
        r"\nSubscribe now for your free copy!.*$",
        r"\nSubscribe\s*\n×\s*\nDownload The Edge Singapore App.*$",
        r"\nDownload The Edge Singapore App.*$",
        r"\nGet credible investing ideas from our in-depth stock analysis.*$",
        r"\nRead also:.*$",
        r"\nGrab your copy of The Edge Malaysia this week.*$",
        r"\nSave by subscribing to us for your print and/or digital copy.*$",
        r"\nP/S: The Edge is also available on.*$",
        r"\nDecoding Asia newsletter:.*$",
        r"\nCopyright SPH Media\. All rights reserved\.$",
        r"\n© Copyright \d{4} by RAM Rating Services Berhad$",
        r"\nPublished by RAM Rating Services Berhad$",
    ]
    for pat in patterns:
        body = re.sub(pat, "", body, flags=re.S | re.I)
    return clean_text(body)


def publisher_for(url: str) -> tuple[str, str, int] | None:
    dom = urllib.parse.urlsplit(url).netloc.lower().replace("www.", "")
    for key, val in PUBLISHERS.items():
        if dom == key or dom.endswith("." + key):
            return val
    return None


def detect_lang(text: str) -> str:
    low = " " + text.lower() + " "
    ms = sum(
        low.count(w)
        for w in (" dan ", " yang ", " untuk ", " dengan ", " daripada ", " telah ", " akan ", " tidak ", " ini ")
    )
    en = sum(
        low.count(w)
        for w in (" the ", " and ", " of ", " to ", " in ", " is ", " that ", " for ", " with ", " said ")
    )
    return "ms" if ms > en * 1.4 else "en"


def tickers_for(text: str) -> list[str]:
    t = normalize_entities(text).lower()
    out = []
    if re.search(r"genting berhad|genting bhd|\b3182\b|genting group|genting conglomerate|genting overseas", t):
        out.append("GENTING")
    if re.search(r"genting malaysia|\bgenm\b|\b4715\b|resorts? world genting|genting highlands|"
                 r"resorts? world new york|genting new york|rwg\b|rwnyc", t):
        out.append("GENM")
    # A bare "Genting" in a corporate story is the listed parent (Genting Berhad).
    if not out and re.search(r"\bgenting\b", t) and not re.search(
        r"genting plantations|genting singapore", t
    ):
        out.append("GENTING")
    return out


def normalize_entities(text: str) -> str:
    """Expand trade-press abbreviations so the filters see full entity names."""
    text = re.sub(r"\bGEN\s+Bhd\b", "Genting Bhd", text, flags=re.I)
    text = re.sub(r"\bGEN\s+Malaysia\b", "Genting Malaysia", text, flags=re.I)
    text = re.sub(r"\bGEN\s+Singapore\b", "Genting Singapore", text, flags=re.I)
    text = re.sub(r"\bGENM\b", "GENM", text, flags=re.I)
    return text


def relevance(title: str, body: str) -> tuple[bool, str]:
    title = normalize_entities(title)
    body = normalize_entities(body)
    text = f"{title}\n{body}"
    if not GENTING_WEAK.search(text):
        return False, "no genting mention"
    n_strong = len(GENTING_STRONG.findall(text))
    n_genting = len(GENTING_WEAK.findall(text))
    n_in_title = len(re.findall(r"\bgenting\b|\bgenm\b|\b3182\b|\b4715\b", title, re.I))
    title_strong = bool(GENTING_STRONG.search(title))
    title_starts = bool(re.match(r"\s*(genting|genm)\b", title, re.I))
    title_fin = bool(FIN_CONTEXT.search(title))
    ops_title = bool(GENM_OPS.search(title))
    subsidiary = re.search(r"genting plantations|\bgenp\b|genting singapore|\bg13\b", title, re.I)
    parent_marker = re.search(
        r"genting berhad|genting bhd|genting malaysia|\bgenm\b|\b3182\b|\b4715\b|"
        r"genting (group|overseas|conglomerate)|genting[,&]|genting and",
        title,
        re.I,
    )

    if ESTATE.search(title):
        return False, "estate/family dispute"
    if TRAVEL.search(title) or re.search(
        r"dream cruises|genting dream|cruise|inside resorts world|connected ecosystem", title, re.I
    ):
        return False, "travel content"
    if EVENT.search(title) and not (title_fin and n_in_title >= 2):
        return False, "event/entertainment"
    if CRIME.search(title) and not title_strong:
        return False, "crime/incident brief"
    if LIFESTYLE.search(title):
        return False, "lifestyle/place"
    if re.match(r"^(genting singapore|gen singapore)\b", title, re.I):
        return False, "genting singapore only"
    if re.search(r"genting singapore", title, re.I) and not re.search(
        r"genting berhad|genting bhd|genting malaysia|\bgenm\b|\b3182\b|\b4715\b", title, re.I
    ):
        return False, "genting singapore only"
    if re.match(r"^(GENTING|GENM)\s*-\s", title):
        return False, "bursa announcement"
    if ROUNDUP.search(title):
        return False, "market roundup"
    if re.search(r"double cover|what happens when the disruptors", title, re.I):
        return False, "magazine preview"
    if title.count(",") >= 4:
        return False, "list headline"
    if title.count(",") >= 2 and n_in_title <= 2 and not title_strong:
        return False, "list headline"
    if PLACE_STORY.search(title) and not title_strong:
        return False, "place/policy story"
    if NON_LISTED.search(title) and not parent_marker:
        return False, "unlisted genting entity"
    if PLACE_ONLY.search(title) and not FIN_CONTEXT.search(title):
        return False, "place name only"
    # Market roundups that merely list the counter.
    if re.search(r"lead bursa (losers|gainers)|decliners overwhelm|bursa (losers|gainers)", title, re.I):
        return False, "market roundup"
    if MARKET_ROUNDUP.search(title) and n_in_title < 2 and not title_strong \
            and not re.search(r"stock today", title, re.I):
        return False, "market roundup"
    if re.search(r"\b(top gainers|top losers|midday|market close|market open|losers|gainers)\b", title, re.I) \
            and n_in_title < 2 and not title_strong:
        return False, "market roundup"
    # Genting Plantations / Genting Singapore stories are a different listed entity.
    if subsidiary and not parent_marker:
        return False, "subsidiary-only story"

    if title_strong:
        return True, "ok"
    if title_starts and (title_fin or CORP_VERB.search(title)):
        return True, "ok"
    if n_in_title and title_fin:
        return True, "ok"
    if n_in_title == 0:
        return False, "not about the company"
    if ops_title and (FIN_CONTEXT.search(body[:3000]) or n_genting >= 5):
        return True, "ok"
    if n_strong >= 2 and n_genting >= 3:
        return True, "ok"
    if n_genting >= 12 and n_strong >= 1 and FIN_CONTEXT.search(body[:4000]):
        return True, "ok"
    return False, "passing mention"


def load_fetched() -> list[dict]:
    path = CACHE / "fetched.json"
    if not path.exists():
        return []
    out = []
    for r in json.loads(path.read_text()):
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
    path = CACHE / "wp_posts.json"
    if not path.exists():
        return []
    out = []
    for r in json.loads(path.read_text()):
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DATA / "news_articles.jsonl")
    ap.add_argument("--report", type=Path, default=DATA / "news_report.md")
    ap.add_argument("--dump-rejects", type=Path, default=CACHE / "rejected.json")
    args = ap.parse_args()

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
            continue
        source, publisher, priority = pm
        if publisher == "The Edge Singapore":
            stats["syndicated_copy"] += 1
            continue
        if NON_NEWS_PATH.search(urllib.parse.urlsplit(url).path):
            stats["non_news_path"] += 1
            continue
        ts = rec.get("published_utc")
        if not ts:
            stats["no_timestamp"] += 1
            continue
        ts = int(ts)
        if not (START_TS <= ts <= END_TS):
            stats["out_of_window"] += 1
            continue
        title = clean_title(rec.get("title") or "")
        body = strip_publisher_boilerplate(clean_text(rec.get("body") or ""))
        if len(body) < 200:
            stats["teaser_only"] += 1
            continue
        if len(body) < 700 and re.search(
            r"subscribe|already a subscriber|sign in|log in|premium content|exclusive to",
            body[-600:],
            re.I,
        ):
            rec["paywalled"] = True
        if publisher in {"The Edge Singapore", "Nikkei Asia", "Bloomberg"} and len(body) < 1200:
            rec["paywalled"] = True
        if len(title) < 8 or len(body) < 120:
            stats["too_short"] += 1
            rejected.append({"url": url, "title": title, "reason": "too_short", "len": len(body)})
            continue
        ok, why = relevance(title, body)
        if not ok:
            stats[f"reject_{why.replace(' ', '_')}"] += 1
            rejected.append({"url": url, "title": title, "reason": why})
            continue
        tickers = tickers_for(f"{title}\n{body}")
        if not tickers:
            stats["no_ticker"] += 1
            rejected.append({"url": url, "title": title, "reason": "no_ticker"})
            continue
        out = {
            "record_type": "article",
            "source": source,
            "channel": publisher,
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
                "malaysian_publisher": publisher
                in {
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
                },
            },
        }
        if rec.get("google_url"):
            out["raw"]["google_news_url"] = rec["google_url"]
        prior = kept.get(url)
        if prior is None or len(out["body"]) > len(prior["body"]):
            kept[url] = out
    print(f"after URL dedupe: {len(kept)}")

    # Near-duplicate titles across publishers (syndicated copies).
    ordered = sorted(
        kept.values(),
        key=lambda r: (r["raw"]["priority"], -r["published_utc"], -len(r["body"])),
    )
    final: list[dict] = []
    for rec in ordered:
        dup = None
        for other in final:
            if title_similarity(rec["title"], other["title"]) >= 0.90:
                dup = other
                break
        if dup is None:
            final.append(rec)
        else:
            stats["near_dup_title"] += 1
            # Prefer the original publisher over an aggregator; otherwise longer body.
            if rec["raw"]["priority"] < dup["raw"]["priority"] or (
                rec["raw"]["priority"] == dup["raw"]["priority"]
                and len(rec["body"]) > len(dup["body"]) * 1.1
            ):
                idx = final.index(dup)
                final[idx] = rec
    final.sort(key=lambda r: r["published_utc"], reverse=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        for rec in final:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    args.dump_rejects.write_text(json.dumps(rejected, ensure_ascii=False, indent=0))
    print(f"wrote {len(final)} articles -> {args.out}")
    print("stats:", dict(stats))
    print("by publisher:")
    for k, v in Counter(r["channel"] for r in final).most_common():
        print(f"  {v:3d} {k}")
    print("by ticker:", Counter(t for r in final for t in r["tickers"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
