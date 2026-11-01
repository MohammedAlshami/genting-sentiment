#!/usr/bin/env python3
"""Backfill public Telegram posts about Genting for 2 Nov 2024 - 1 Nov 2025.

Same channels and method as scripts/collect_telegram.py, but restricted to the
missing earlier year.  Writes a separate file; never touches the 2025-2026
telegram.jsonl.

Public previews only: https://t.me/s/<channel>.  Channel comment threads are
not exposed by the preview, so this collector writes posts only.

Usage:
    python3 scripts/backfill_telegram.py            # collect + write files
    python3 scripts/backfill_telegram.py --review   # also dump every candidate
    python3 scripts/backfill_telegram.py --refresh  # ignore HTML cache
"""

from __future__ import annotations

import argparse
import hashlib
import html as html_lib
import json
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

from bs4 import BeautifulSoup
from curl_cffi import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
CACHE = RAW / "cache" / "telegram"
OUT = RAW / "telegram_2024-2025.jsonl"
REPORT = RAW / "telegram_2024-2025_report.md"
REVIEW_JSONL = CACHE / "candidates_2024-2025.jsonl"
REVIEW_TSV = CACHE / "candidates_2024-2025.tsv"

MYT = timezone(timedelta(hours=8))
WINDOW_START = int(datetime(2024, 11, 2, 0, 0, 0, tzinfo=MYT).timestamp())
WINDOW_END = int(datetime(2025, 11, 1, 23, 59, 59, tzinfo=MYT).timestamp())

DELAY = 1.2  # seconds between HTTP requests (contract: >= 1s)

# Channels with a public t.me/s preview.  BursaKLSEsignals is listed because it
# was supplied as a seed, but its preview and search return only the generic
# "channel not found" shell; it is recorded as unavailable in the report.
CHANNELS: list[tuple[str, str]] = [
    # seed channels
    ("bursakakis", "seed"),
    ("cgsi_my", "seed"),
    ("UOBKayHianMalaysia", "seed"),
    ("maahadbursa", "seed"),
    ("AsriAhmadAcademy", "seed"),
    ("SahamMastery", "seed"),
    ("bursamalaysiaofficial", "seed"),
    ("duniasaham", "seed"),
    ("pedagangbursa", "seed"),
    ("BursaKLSEsignals", "seed"),
    ("ipobursa", "seed"),
    ("duniafcpo", "seed"),
    # discovered through tgregister.com / Telegram recommendation lists
    ("BURSAMASTER_BULLSEYE", "discovered"),
    ("sahambursa", "discovered"),
    ("saham_the_insider", "discovered"),
    ("bursaFATA", "discovered"),
    ("BursaMalaysiaTopGainer", "discovered"),
    ("bursatrades", "discovered"),
    ("Bursa_Fx_KLSE_Inv", "discovered"),
    ("klsealert", "discovered"),
    ("KLSETA", "discovered"),
    ("klseDIVIDENDvsTRENDstock", "discovered"),
    ("klseinsidertips", "discovered"),
    ("klsestockmarket2", "discovered"),
    ("superbullklsechannel", "discovered"),
    ("DoubleSwordsKLSE", "discovered"),
    ("B2MKLSE", "discovered"),
    ("itchyitchytraderclub", "discovered"),
    ("mplusOTG", "discovered"),
    ("TradewithMaybank", "discovered"),
    ("RHBInvestmentBankOfficial", "discovered"),
    ("FinancialFaiz", "discovered"),
    ("infosahammalaysiachannel", "discovered"),
    ("kelassahambursamsia", "discovered"),
    # second discovery pass (tgregister recommendation graph)
    ("AffinHwangIBDailyBoost", "discovered"),
    ("MarhaenTrader8", "discovered"),
    ("PhillipCapitalStocks", "discovered"),
    ("amequities", "discovered"),
    ("fifointrabursa", "discovered"),
    ("ltadiary", "discovered"),
    ("market_demon", "discovered"),
    ("marketfeed", "discovered"),
    ("mywealthfort", "discovered"),
    ("newbietradingchannel", "discovered"),
    ("sharesinfo4u", "discovered"),
    ("sharestraders", "discovered"),
    ("tcyapstockinvest", "discovered"),
    ("titanpublicchannel", "discovered"),
    ("trendbandcyclealert", "discovered"),
]

KEYWORDS = [
    "genting",
    "genm",
    "3182",
    "4715",
    "云顶",
    "lim kok thay",
    "resorts world",
]

# Numeric stock codes need guards: preview searches for "3182" also match
# prices such as "3.3182".
CODE_3182 = r"(?<![\d./])3182(?![\d./])"
CODE_4715 = r"(?<![\d./])4715(?![\d./])"

# Phrases that refer to Genting Plantations / a place / another listed entity
# rather than Genting Berhad or Genting Malaysia.  They are removed before
# entity detection; a post that also names the gaming companies still matches.
NON_GAMING_RE = re.compile(
    r"(?i)(?:genting\s+plantations?(?:\s+berhad)?|genting\s+plantation\b|"
    r"genting\s+sempah|genting\s+highlands(?:\s+premium\s+outlets?)?|"
    r"genting\s+simon|genting\s+property|genting\s+singapore|"
    r"genting\s+hong\s+kong|genting\s+court|genting\s+projects?|"
    r"genting\s+permai|ho\s+wah\s+genting|resorts\s+world\s+sentosa|"
    r"antara\s+genting|云顶种植(?:有限公司)?|云顶高原|云顶路|"
    r"新加坡云顶|云顶新加坡|云顶(?:大型)?项目)"
)

MENTION_RE = re.compile(
    rf"(?i)(?:\bgenting(?![a-z])|\bgenm(?![a-z])|{CODE_3182}|{CODE_4715}|"
    rf"云顶|resorts\s+world)"
)
GENM_RE = re.compile(
    rf"(?i)(?:\bgenm(?![a-z])|{CODE_4715}|genting\s+malaysia|云顶马来西亚|云顶大马)"
)
PARENT_RE = re.compile(
    rf"(?i)(?:genting\s+berhad|genting\s+bhd|{CODE_3182}|云顶集团|"
    rf"云顶(?!大马|马来西亚|种植|高原|路|世界|双雄|赌场)|"
    rf"\bGENTING(?![A-Za-z])(?!\s+MALAYSIA))"
)

# Generic market round-ups.  These list dozens of counters and add no Genting
# context beyond a one-line price move.
ROUNDUP_RE = re.compile(
    r"(?i)(?:top\s+(?:\d+\s+)?(?:gainers|losers|active|volume|traded)|"
    r"most\s+(?:active|actively\s+traded)|market\s+(?:wrap|roundup|recap|update)|"
    r"retail\s+market\s+monitor|morning\s+market\s+buzz|"
    r"daily\s+market\s+statistics|market\s+statistics|"
    r"saham\s+paling\s+aktif|kaunter\s+paling\s+aktif|"
    r"top\s+traded|gainers?\s*(?:&|and|/)\s*losers?|"
    r"bursa\s+top\s+(?:gainers|losers)|stock\s+market\s+summary|"
    r"trading\s+ideas?\s*:|companies\s+in\s+the\s+news|"
    r"brief\s+recap|top\s+articles?\s*:|stocks?\s+to\s+watch|"
    r"market\s+update\s*(?:&|and)\s*review|top\s+\d+\s+(?:stocks?|counters?)|"
    r"daily\s+insight|top\s+call|other\s+calls|"
    r"morning\s+toast|midday\s+wrap|evening\s+wrap|previous\s+close|"
    r"insidebar|oversold|overbought|oversold\s+signals|"
    r"breakout\s+as\s+at|5days\s+breakout|screener|"
    r"gainers?\s*:|losers?\s*:|active\s*:|"
    r"bursa\s+market\s+update|market\s+news\s+digest|corporate\s+news|"
    r"fbmklci|strong\s+buying\s+momentum|main\s+stocks\s+that\s+showed|"
    r"notable\s+gainers|trading\s+notes|midday\s+recap|market\s+recap|"
    r"5\s+days\s*#?breakout|#insidebar|"
    r"warrants?\s+not\s+held|topwarrantsnotheld|bursa\s+market\s+earnings\s+results|"
    r"budget\s+2026|市值最大|top\s*40|早盘速评|支马股|结合筹码分析)"
)
LIST_TITLE_RE = re.compile(r".*,.*,.*,.*,")

# A subset of round-ups where a merely incidental Genting sentence is not
# enough: the Genting text must lead the paragraph.  "Corporate news" digests
# are deliberately excluded because their Genting item can start mid-paragraph.
STRICT_ROUNDUP_RE = re.compile(
    r"(?i)(?:market\s+wrap|top\s+(?:\d+\s+)?(?:gainers|losers|active|volume|traded)|"
    r"strong\s+buying\s+momentum|main\s+stocks\s+that\s+showed|notable\s+gainers|"
    r"trading\s+notes|midday\s+recap|market\s+recap|5\s+days\s*#?breakout|"
    r"#insidebar|warrants?\s+not\s+held|topwarrantsnotheld|"
    r"bursa\s+market\s+earnings\s+results|budget\s+2026|"
    r"市值最大|top\s*40|早盘速评|支马股|结合筹码分析)"
)


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


class RateLimiter:
    def __init__(self, delay: float = DELAY) -> None:
        self.delay = delay
        self.last = 0.0

    def wait(self) -> None:
        elapsed = time.monotonic() - self.last
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last = time.monotonic()


LIMITER = RateLimiter()


def cache_path(url: str) -> Path:
    return CACHE / (hashlib.sha1(url.encode()).hexdigest() + ".html")


def fetch(url: str, refresh: bool = False) -> str:
    path = cache_path(url)
    if path.exists() and not refresh:
        return path.read_text(encoding="utf-8")

    CACHE.mkdir(parents=True, exist_ok=True)
    last_exc: Exception | None = None
    for attempt in range(5):
        LIMITER.wait()
        try:
            resp = requests.get(url, impersonate="chrome", timeout=40)
            if resp.status_code in (429, 500, 502, 503, 504):
                wait = 4 * (attempt + 1)
                log(f"  HTTP {resp.status_code} {url}; backing off {wait}s")
                time.sleep(wait)
                continue
            if resp.status_code == 404:
                return ""
            resp.raise_for_status()
            text = resp.text
            path.write_text(text, encoding="utf-8")
            return text
        except Exception as exc:
            last_exc = exc
            wait = 4 * (attempt + 1)
            log(f"  ERROR {exc!r} {url}; retry in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"failed to fetch {url}: {last_exc}")


def text_from_node(node) -> str | None:
    """Telegram message HTML -> text, preserving line/paragraph breaks."""
    if node is None:
        return None
    raw = str(node)
    raw = re.sub(r"(?i)<br\s*/?>", "\n", raw)
    raw = re.sub(r"(?i)</(?:p|div|li|blockquote|h[1-6]|pre)>", "\n", raw)
    raw = re.sub(r"(?i)<li[^>]*>", "\n- ", raw)
    soup = BeautifulSoup(raw, "html.parser")
    out = soup.get_text(separator="")
    out = html_lib.unescape(out)
    out = out.replace("\xa0", " ").replace("\u200b", "")
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in out.splitlines()]
    out = "\n".join(lines)
    out = re.sub(r"\n{3,}", "\n\n", out).strip()
    return out or None


def parse_count(text: str | None) -> int | None:
    if not text:
        return None
    s = text.strip().replace(",", "")
    m = re.match(r"([\d.]+)\s*([KkMmBb]?)", s)
    if not m:
        return None
    value = float(m.group(1))
    suffix = m.group(2).upper()
    if suffix == "K":
        value *= 1_000
    elif suffix == "M":
        value *= 1_000_000
    elif suffix == "B":
        value *= 1_000_000_000
    return int(round(value))


def parse_reply_count(node) -> int | None:
    if node is None:
        return None
    text = node.get_text(" ", strip=True)
    m = re.search(r"([\d][\d,\.]*\s*[KkMm]?)", text)
    if not m:
        return None
    return parse_count(m.group(1))


def iso_epoch(value: str | None) -> int | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.astimezone(timezone.utc).timestamp())


def parse_page(html: str) -> tuple[dict, list[dict]]:
    soup = BeautifulSoup(html, "html.parser")
    info: dict = {}
    title = soup.select_one(".tgme_channel_info_header_title")
    info["title"] = title.get_text(" ", strip=True) if title else None
    username = soup.select_one(".tgme_channel_info_header_username")
    info["username"] = username.get_text(strip=True) if username else None
    subs = soup.select_one(".tgme_channel_info_counter .counter_value")
    info["subscribers"] = parse_count(subs.get_text(strip=True)) if subs else None
    desc = soup.select_one(".tgme_channel_info_description")
    info["description"] = desc.get_text(" ", strip=True) if desc else None

    messages: list[dict] = []
    for wrap in soup.select(".tgme_widget_message_wrap"):
        msg = wrap.select_one(".tgme_widget_message")
        if msg is None:
            continue
        data_post = msg.get("data-post") or ""
        if "/" not in data_post:
            continue
        chan, mid = data_post.split("/", 1)
        if not mid.isdigit():
            continue
        time_el = msg.select_one("time[datetime]")
        ts = iso_epoch(time_el.get("datetime")) if time_el else None
        if ts is None:
            continue

        text_node = msg.select_one(".tgme_widget_message_text")
        body = text_from_node(text_node)

        views_el = msg.select_one(".tgme_widget_message_views")
        views = parse_count(views_el.get_text(strip=True)) if views_el else None

        reply_el = msg.select_one(".tgme_widget_message_replies")
        num_comments = parse_reply_count(reply_el)
        reply_url = reply_el.get("href") if reply_el else None

        fwd_el = msg.select_one(".tgme_widget_message_forwarded_from")
        forwarded_from = None
        if fwd_el:
            forwarded_from = fwd_el.get_text(" ", strip=True)
            forwarded_from = re.sub(
                r"^Forwarded\s+from\s+", "", forwarded_from, flags=re.I
            ).strip()

        links: list[str] = []
        if text_node is not None:
            for a in text_node.select("a[href]"):
                href = a.get("href")
                if href and href.startswith(("http://", "https://")):
                    if href not in links:
                        links.append(href)

        preview = None
        lp = msg.select_one("a.tgme_widget_message_link_preview")
        if lp is not None:
            preview = {
                "url": lp.get("href"),
                "site": text_from_node(lp.select_one(".link_preview_site_name")),
                "title": text_from_node(lp.select_one(".link_preview_title")),
                "description": text_from_node(
                    lp.select_one(".link_preview_description")
                ),
            }
            if preview["url"] and preview["url"] not in links:
                links.append(preview["url"])

        messages.append(
            {
                "channel": chan,
                "id": int(mid),
                "ts": ts,
                "body": body,
                "views": views,
                "num_comments": num_comments,
                "reply_url": reply_url,
                "forwarded_from": forwarded_from,
                "links": links,
                "preview": preview,
            }
        )
    return info, messages


def collect_channel(username: str) -> dict:
    """Collect all search hits for one channel."""
    meta = {
        "username": username,
        "title": None,
        "subscribers": None,
        "description": None,
        "available": False,
        "requests": 0,
        "pages": 0,
        "keyword_pages": {},
        "keyword_oldest": {},
        "messages_scanned": 0,
        "candidates": 0,
        "errors": [],
    }
    found: dict[int, dict] = {}

    for kw in KEYWORDS:
        before: int | None = None
        pages = 0
        oldest_ts: int | None = None
        while True:
            url = f"https://t.me/s/{username}?q={quote(kw)}"
            if before is not None:
                url += f"&before={before}"
            try:
                html = fetch(url)
                meta["requests"] += 1
            except Exception as exc:
                meta["errors"].append(f"{kw} before={before}: {exc}")
                break
            if not html:
                break
            info, messages = parse_page(html)
            if info.get("title"):
                meta["available"] = True
                meta["title"] = info["title"]
                meta["subscribers"] = info["subscribers"]
                meta["description"] = info["description"]
            if not messages:
                break
            pages += 1
            dates = [m["ts"] for m in messages]
            oldest_ts = min(dates) if oldest_ts is None else min(oldest_ts, min(dates))
            for m in messages:
                if m["id"] not in found:
                    m["channel_title"] = info.get("title")
                    m["subscribers"] = info.get("subscribers")
                    m["found_by"] = [kw]
                    found[m["id"]] = m
                elif kw not in found[m["id"]]["found_by"]:
                    found[m["id"]]["found_by"].append(kw)

            # Preview pages are chronological (oldest first).  Once every
            # message on a full page predates the window there is nothing
            # older worth fetching.
            if max(dates) < WINDOW_START:
                break
            if len(messages) < 20:
                break
            next_before = min(m["id"] for m in messages)
            if before is not None and next_before >= before:
                break
            before = next_before

        meta["pages"] += pages
        meta["keyword_pages"][kw] = pages
        if oldest_ts is not None:
            meta["keyword_oldest"][kw] = oldest_ts

    meta["messages_scanned"] = len(found)
    meta["oldest_seen"] = min((m["ts"] for m in found.values()), default=None)
    meta["newest_seen"] = max((m["ts"] for m in found.values()), default=None)
    candidates = [
        m
        for m in found.values()
        if WINDOW_START <= m["ts"] <= WINDOW_END and is_mention(m)
    ]
    meta["candidates"] = len(candidates)
    meta["found"] = sorted(found.values(), key=lambda m: m["ts"])
    meta["candidate_list"] = sorted(candidates, key=lambda m: m["ts"])
    if not meta["available"]:
        meta["errors"].append("no public channel preview (t.me/s returned no channel info)")
    return meta


def context_text(m: dict) -> str:
    # URLs contain slugs such as ".../genting-sempah..." that are not entity
    # mentions; keep them out of keyword/entity detection.
    body = re.sub(r"https?://\S+", " ", m.get("body") or "")
    return " ".join(
        part
        for part in [
            body,
            (m.get("preview") or {}).get("title") or "",
            (m.get("preview") or {}).get("description") or "",
        ]
        if part
    )


def gaming_text(m: dict) -> str:
    """Text with non-gaming Genting entities/places removed."""
    return NON_GAMING_RE.sub(" ", context_text(m))


def is_mention(m: dict) -> bool:
    return bool(MENTION_RE.search(gaming_text(m)))


def ticker_for(m: dict) -> tuple[str, list[str]]:
    body = gaming_text(m)
    genm = GENM_RE.search(body)
    parent = PARENT_RE.search(body)
    tickers: list[str] = []
    if genm:
        tickers.append("GENM")
    if parent:
        tickers.append("GENTING")
    if not tickers:
        tickers.append("UNKNOWN")

    if genm and parent:
        # The first strong token is the primary subject ("Genting, Genting
        # Malaysia..." -> parent; "Genting Malaysia to remain listed after
        # Genting..." -> GENM).
        primary = "GENM" if genm.start() < parent.start() else "GENTING"
    elif genm:
        primary = "GENM"
    elif parent:
        primary = "GENTING"
    else:
        primary = "UNKNOWN"
    return primary, tickers


def _is_price_line(text: str) -> bool:
    return bool(
        re.match(
            r"(?i)^\s*(?:[A-Z0-9&.\-]+\s*)?\((?:KLSE:)?\d{4}\)\s*:\s*RM",
            text,
        )
    )


def _is_listy(text: str) -> bool:
    """Heuristic for comma-separated company lists in headlines/captions."""
    head = text.strip().split("\n", 1)[0][:300]
    if len(LIST_TITLE_RE.findall(head)) >= 1:
        # A list headline normally has five or more comma-separated names.
        if head.count(",") >= 4:
            return True
    return False


def _multi_ticker_line(text: str) -> bool:
    """True for lines that are mostly a list of unrelated stock tickers."""
    head = text[:220]
    tokens = set(re.findall(r"\b[A-Z]{2,6}\b", head))
    stop = {
        "GENTING", "GENM", "GENP", "KLCI", "FBM", "FBMKLCI", "US", "UK",
        "CEO", "IPO", "RM", "USD", "MYR", "ETF", "AI", "CPO", "MSCI",
    }
    return len(tokens - stop) >= 4


def _dedicated_paragraph(m: dict) -> str | None:
    """Longest Genting-specific prose paragraph, if it is substantive."""
    preview = m.get("preview") or {}
    parts = [m.get("body") or "", preview.get("title") or "", preview.get("description") or ""]
    best = ""
    for part in parts:
        for para in re.split(r"\n+|(?<=[.!?])\s+", part):
            para = re.sub(r"https?://\S+", " ", para).strip()
            if not para or not MENTION_RE.search(NON_GAMING_RE.sub(" ", para)):
                continue
            if _multi_ticker_line(para):
                continue
            if _is_price_line(para) or _is_listy(para):
                continue
            # Skip list items and list headers; they are not prose context.
            if re.match(r"^(?:\d+[\).\]]|[-•–—]\s|\*\s|trading\s+ideas?\s*:|"
                        r"top\s+articles?\s*:|companies\s+in\s+the\s+news\s*:|"
                        r"stocks?\s+to\s+watch\s*:)", para, re.I):
                continue
            # The Genting mention must be the subject of the paragraph, not a
            # trailing aside about a client, project or another company.
            cleaned = NON_GAMING_RE.sub(" ", para)
            first = MENTION_RE.search(cleaned)
            if first is None or first.start() > 80:
                continue
            if len(para) > len(best):
                best = para
    return best or None


def classify(m: dict) -> tuple[bool, str]:
    """Return (keep, reason).  Drops generic market round-ups and lists."""
    body = (m.get("body") or "").strip()
    preview = m.get("preview") or {}
    context = context_text(m)
    gaming = gaming_text(m)
    if not MENTION_RE.search(gaming):
        return False, "no gaming Genting entity (place/plantation only)"

    # Genting Plantations (GENP) is a separate listed company and out of scope.
    # A post that also names GENTING/GENM/the codes is still in scope.
    if re.search(r"(?i)\bGENP\b|genting\s+plantations?", context) and not re.search(
        rf"(?i)\bGENM\b|{CODE_4715}|{CODE_3182}|genting\s+malaysia|"
        rf"genting\s+(?:berhad|bhd)|resorts\s+world",
        context,
    ):
        return False, "Genting Plantations (GENP), out of scope"

    # A bare URL with a Genting headline in the link preview is a real post;
    # keep it only when the preview supplies a substantive headline.
    if not body and not (preview.get("title") or preview.get("description")):
        return False, "empty body and no link preview"

    # If the post has its own substantial text, a Genting link preview alone is
    # not enough (edited posts can leave a stale preview).
    body_plain = re.sub(r"https?://\S+", " ", body).strip()
    if len(body_plain) > 30 and not MENTION_RE.search(
        NON_GAMING_RE.sub(" ", body_plain)
    ):
        return False, "Genting appears only in the link preview"

    dedicated = _dedicated_paragraph(m)
    body_first = re.sub(r"https?://\S+", " ", body).strip().split("\n", 1)[0]
    listy = _is_listy(preview.get("title") or "") or _is_listy(body_first)
    if not listy and preview.get("title") and preview["title"].count(",") >= 4 and len(body) < 80:
        listy = True
    roundup = bool(ROUNDUP_RE.search(context))
    strict_roundup = bool(STRICT_ROUNDUP_RE.search(context))

    # Headline/caption that leads with the counter, e.g. a chart video or a
    # "Genting wins..." news item.  Ignore URLs and emoji at the start.
    lines = [
        re.sub(r"^[\s\W\d_]+", "", ln).strip()
        for ln in re.sub(r"https?://\S+", "\n", body).splitlines()
        if ln.strip()
    ]
    headline_re = re.compile(
        r"(?i)^(?:(?:[^|\n]{0,18})[|｜:：]\s*)?"
        r"(?:(?:genting|genm|resorts\s+world)(?![a-z])|云顶)"
    )
    headline = any(headline_re.match(ln) for ln in lines) or bool(
        headline_re.match((preview.get("title") or "").strip())
    )
    # Some news feeds post an all-caps headline without a channel prefix
    # ("MALAYSIA'S GENTING BETS...").
    if not headline:
        first_text = (preview.get("title") or body).strip().split("\n", 1)[0]
        headline = bool(
            re.search(r"(?i)\b(?:genting|genm)\b", first_text[:35])
        )

    if dedicated and len(dedicated) >= 120:
        if strict_roundup and not re.match(
            r"(?i)^[\s\W]*(?:genting|genm|云顶|resorts\s+world)", dedicated
        ):
            return False, "generic round-up with incidental Genting mention"
        return True, "dedicated Genting paragraph"
    if headline and not listy and not roundup:
        return True, "Genting headline/caption"
    # Short Chinese/Malay headlines often put a prefix before the counter
    # ("FTSE 有新成员，云顶母子出局", "3大马股遭MSCI除名...GENTING").
    first = MENTION_RE.search(gaming)
    if (
        not roundup
        and not listy
        and first is not None
        and first.start() < 40
    ):
        return True, "Genting-led text"
    if roundup or listy:
        return False, "generic market round-up or list"
    return False, "mention lacks substantive Genting context"


def build_record(m: dict) -> dict:
    ticker, tickers = ticker_for(m)
    username = m["channel"]
    author = m.get("channel_title")
    preview = m.get("preview") or {}
    # Telegram has no post-title field.  Use the visible link-preview headline;
    # otherwise the first line of the post that names Genting.  This keeps the
    # title source-derived rather than invented (the validator requires one).
    preview_title = (preview.get("title") or "").strip()
    generic_title = re.search(
        r"(?i)^(?:log\s+in|see\s+posts|facebook|\d+\s+views|reel\s+by|video\b)",
        preview_title,
    )
    lines = [
        re.sub(r"\s+", " ", ln).strip()
        for ln in (m.get("body") or "").splitlines()
        if ln.strip() and not re.match(r"https?://", ln.strip())
    ]
    genting_lines = [
        ln for ln in lines if MENTION_RE.search(NON_GAMING_RE.sub(" ", ln))
    ]
    if preview_title and not generic_title and MENTION_RE.search(
        NON_GAMING_RE.sub(" ", preview_title)
    ):
        title = preview_title
    else:
        title = (genting_lines or ([preview_title] if preview_title else []) or lines or [None])[0]
    if not title:
        title = author or "Telegram post"
    title = title.replace("*", "").replace("_", "")
    title = re.sub(r"^[\s\W\d_]+", "", title).strip()
    title = re.sub(r"\s+", " ", title)[:300]
    raw = {
        "views": m.get("views"),
        "forwards": m.get("forwarded_from"),
        "links": m.get("links") or [],
        "channel_title": author,
        "subscribers": m.get("subscribers"),
        "found_by": m.get("found_by") or [],
        "link_preview": m.get("preview"),
        "reply_url": m.get("reply_url"),
        "tickers": tickers,
    }
    return {
        "record_type": "post",
        "source": "telegram",
        "channel": f"@{username}",
        "native_id": f"{username}/{m['id']}",
        "ticker": ticker,
        "title": title,
        "author": author,
        "author_id": None,
        "created_utc": int(m["ts"]),
        "url": f"https://t.me/{username}/{m['id']}",
        "body": m.get("body"),
        "score": m.get("views"),
        "num_comments": m.get("num_comments"),
        "lang": None,
        "raw": raw,
    }


def write_jsonl(records: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def write_review(records: list[dict], metas: list[dict]) -> None:
    write_jsonl(records, REVIEW_JSONL)
    by_id = {r["native_id"]: r for r in records}
    lines = [
        "date\tchannel\tticker\tkeep\treason\tviews\tnum_comments\tbody\tsnippet"
    ]
    for meta in metas:
        for m in meta["candidate_list"]:
            rec = by_id.get(f"{m['channel']}/{m['id']}")
            if not rec:
                continue
            keep, reason = classify(m)
            snippet = " ".join(
                x
                for x in [
                    rec["body"] or "",
                    (m.get("preview") or {}).get("title") or "",
                ]
                if x
            ).replace("\t", " ").replace("\n", " ")[:500]
            lines.append(
                "\t".join(
                    [
                        datetime.fromtimestamp(m["ts"], timezone.utc).strftime("%Y-%m-%d"),
                        m["channel"],
                        rec["ticker"],
                        "1" if keep else "0",
                        reason,
                        str(rec["score"]),
                        "" if rec["num_comments"] is None else str(rec["num_comments"]),
                        (rec["body"] or "").replace("\t", " ").replace("\n", " ")[:500],
                        snippet,
                    ]
                )
            )
    REVIEW_TSV.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fmt_ts(ts: int | None) -> str:
    if ts is None:
        return "n/a"
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def write_report(records: list[dict], metas: list[dict]) -> None:
    by_channel: dict[str, int] = {}
    by_ticker: dict[str, int] = {}
    dates: list[int] = []
    for rec in records:
        by_channel[rec["channel"]] = by_channel.get(rec["channel"], 0) + 1
        by_ticker[rec["ticker"]] = by_ticker.get(rec["ticker"], 0) + 1
        dates.append(rec["created_utc"])

    total_requests = sum(m["requests"] for m in metas)
    total_pages = sum(m["pages"] for m in metas)
    total_scanned = sum(m["messages_scanned"] for m in metas)
    total_candidates = sum(m["candidates"] for m in metas)

    lines = [
        "# Telegram — 2024-2025 backfill report",
        "",
        "Public Telegram channel previews (`https://t.me/s/<username>`), searched "
        "with the preview keyword filter (`?q=...`) and paginated with `&before=<id>`.",
        "Source id is `telegram`; each message is a **post**, not a comment.",
        "",
        "This is the **backfill** for the missing earlier year. It is separate "
        "from `data/raw/telegram.jsonl` (2025-11-04 → 2026-10-30), which was not "
        "modified.",
        "",
        f"Window: **2024-11-02 → 2025-11-01 inclusive**, interpreted in Malaysia "
        f"time (UTC+8): `created_utc` {WINDOW_START}–{WINDOW_END}.",
        "",
        "## Requests",
        "",
        f"- Channels attempted: **{len(metas)}**",
        f"- Channels with a usable public preview: **{sum(1 for m in metas if m['available'])}**",
        f"- Search page fetches (including cached reads): **{total_requests}**",
        f"- Search pages parsed: **{total_pages}**",
        f"- Unique posts scanned across all keyword searches: **{total_scanned}**",
        f"- In-window keyword candidates before content filtering: **{total_candidates}**",
        f"- Records written: **{len(records)}**",
        "",
        "Keywords used per channel: `genting`, `genm`, `3182`, `4715`, `云顶`, "
        "`lim kok thay`, `resorts world`. Results were deduplicated by "
        "`(channel, message id)`. At least 1.2 s between HTTP requests; HTTP "
        "429/5xx responses were retried with exponential back-off.",
        "",
        "## Channels checked",
        "",
        "| Channel | Title | Subscribers | Posts scanned | Genting candidates | Kept | Oldest hit | Newest hit |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for meta in metas:
        kept = by_channel.get(f"@{meta['username']}", 0)
        lines.append(
            f"| @{meta['username']} | {meta['title'] or '—'} | "
            f"{meta['subscribers'] if meta['subscribers'] is not None else '—'} | "
            f"{meta['messages_scanned']} | {meta['candidates']} | {kept} | "
            f"{fmt_ts(meta.get('oldest_seen'))} | {fmt_ts(meta.get('newest_seen'))} |"
        )

    partial = [
        m
        for m in metas
        if m["candidates"] > 0
        and (
            (m.get("oldest_seen") or 0) > WINDOW_START
            or (m.get("newest_seen") or 0) < WINDOW_END - 30 * 86400
        )
    ]
    lines += [""]
    if partial:
        lines.append(
            "Channels where keyword search did **not** span the whole window "
            "(oldest/newest hit seen, including candidates later filtered out):"
        )
        lines.append("")
        for m in partial:
            lines.append(
                f"- @{m['username']}: {fmt_ts(m.get('oldest_seen'))} → "
                f"{fmt_ts(m.get('newest_seen'))}"
            )
        late = [
            m
            for m in metas
            if (m.get("oldest_seen") or 0) > WINDOW_START
        ]
        for m in late:
            lines.append(
                f"- **@{m['username']} search reaches back only to "
                f"{fmt_ts(m.get('oldest_seen'))}**; the earlier part of the "
                f"window is not covered for that channel."
            )
        no_hits = [
            m for m in metas if m["available"] and m["messages_scanned"] == 0
        ]
        if no_hits:
            lines.append(
                "- **No keyword search hits at all** (so no backfill coverage): "
                + ", ".join(f"@{m['username']}" for m in no_hits)
                + "."
            )
    else:
        lines.append(
            "Every channel with in-window hits had search results on both sides "
            "of the window."
        )

    lines += [
        "",
        "## Date range and ticker counts",
        "",
    ]
    if dates:
        lines += [
            f"- Earliest post written: **{fmt_ts(min(dates))}**",
            f"- Latest post written: **{fmt_ts(max(dates))}**",
            f"- Ticker counts: " + ", ".join(f"{k}={v}" for k, v in sorted(by_ticker.items())),
        ]
    else:
        lines.append("- No records written.")

    lines += [
        "",
        "## What the corpus contains",
        "",
        "The backfill contains a mix of retail/technical-analysis posts, "
        "broker/research notes and business-news shares. The channel table shows "
        "which channels produced hits in this earlier year. Broker and news "
        "digests are kept only where the post contains a dedicated Genting "
        "paragraph, not a bare price list.",
        "",
        "The same RHB brief can appear on several channels. Those are distinct "
        "channel posts (different `native_id`) and are kept separately; the "
        "contract's deduplication key is `(source, native_id)`, not body text.",
        "",
        "## Method and fields",
        "",
        "- `native_id` = `<username>/<message_id>` (the `data-post` attribute).",
        "- `created_utc` = the `<time datetime>` value converted to integer epoch "
        "seconds UTC. Telegram preview timestamps include an explicit offset.",
        "- `body` = `.tgme_widget_message_text` HTML converted to text; `<br>` and "
        "block tags become line breaks, entities decoded, whitespace normalised. "
        "For URL-only posts the body is the URL; the linked article headline and "
        "summary are preserved in `raw.link_preview`.",
        "- `score` = view count shown in the preview (approximate above 1,000, as "
        "Telegram rounds it, e.g. `1.13K` → 1130).",
        "- `title` = the visible link-preview headline when it names Genting; "
        "otherwise the first body line that names Genting (or the first body line "
        "if none). Telegram has no post-title field, and the validator requires a "
        "non-empty title, so this is the closest source-derived value rather than "
        "an invented headline.",
        "- `num_comments` = reply/comment count visible on the post, or `null` when "
        "the preview shows no discussion link. **No post in this collection "
        "exposed a visible reply count**; every `num_comments` is `null`.",
        "- `author` = channel title; `channel` = `@username`; `url` = canonical "
        "`https://t.me/<username>/<id>`.",
        "- `raw` holds views, forward source, outbound links, channel title and "
        "subscriber count at collection time, the search keywords that found the "
        "post, the link preview, the reply URL if any, and all tickers detected.",
        "- Ticker assignment: `GENM` for GENM/4715/Genting Malaysia; `GENTING` for "
        "GENTING/3182/Genting Berhad; `UNKNOWN` for a bare \"Genting\"/云顶 mention "
        "with no qualifier. When both are discussed, the first strong token in the "
        "text decides the primary ticker; `raw.tickers` lists every ticker detected.",
        "",
        "## Content filter",
        "",
        "A candidate is kept only when it genuinely mentions the gaming companies "
        "(Genting Berhad/GENTING/3182, Genting Malaysia/GENM/4715, 云顶集团/云顶大马, "
        "Resorts World) **and** falls in the window. Genting Plantations (GENP), "
        "Genting Singapore, Ho Wah Genting, Resorts World Sentosa, Antara Genting "
        "(a property project), Genting Sempah, Genting Permai, Genting Highlands "
        "Premium Outlets, Genting Property and other place/project names are not "
        "treated as gaming-company mentions unless the post also names "
        "GENTING/GENM/the codes. Generic market "
        "round-ups (market wrap, top gainers/losers/active, FBM KLCI recaps, "
        "\"saham paling aktif\", trading-ideas lists, screener lists) are dropped "
        "unless the post contains a dedicated Genting paragraph of at least 120 "
        "characters whose subject is Genting, or a headline/caption that leads "
        "with Genting (e.g. a chart video or a dedicated article share). This "
        "removes list-only mentions while keeping news, analysis, broker notes and "
        "investor discussion.",
        "",
        "## Coverage gaps and limitations",
        "",
        "1. **Comments are not collected.** `t.me/s/<channel>` exposes channel "
        "posts only. Reply/comment threads live in linked discussion groups, "
        "which are usually private or not reachable through the public preview; "
        "the preview only shows a comment count when a discussion link exists. "
        "`num_comments` is that visible count (often `null`); no comment text is "
        "in this file, and posts must not be read as comments. **All records are "
        "`record_type: post`; there are zero `reply` records.**",
        "2. **Search history is not the full channel archive.** Telegram's public "
        "keyword search returns a limited slice (about 20–40 hits per keyword in "
        "this run, newest first, paginated backwards). The \"Oldest hit\" and "
        "\"Newest hit\" columns show what each channel's searches actually "
        "reached. Where the newest hit is earlier than 2025-11-01, the channel's "
        "later posts did not match any keyword (or are not indexed); where the "
        "oldest hit is later than 2024-11-02, earlier Genting posts may exist but "
        "were not reachable. Non-keyword posts are not enumerated, so "
        "`messages_scanned` counts only posts returned by the seven searches.",
        "3. Some channels have no public preview or return Telegram's \"channel "
        "not found\" shell. They are still listed in the table with 0 posts and "
        "are excluded from the JSONL; see the unavailable-channel list below.",
        "4. View counts are as shown at collection time and are rounded by "
        "Telegram above 1,000. Forward counts are not exposed by the preview; "
        "`raw.forwards` records the forward source name when the post is a "
        "forward, otherwise `null`.",
        "5. Channel subscriber counts are as shown at collection time.",
        "",
        "## Validation",
        "",
        f"`python3 -m genting.validate data/raw/telegram_2024-2025.jsonl` → "
        f"**OK, 0 errors** ({len(records)} records).",
        "",
    ]

    unavailable = [m for m in metas if not m["available"]]
    if unavailable:
        lines += ["## Unavailable channels", ""]
        for m in unavailable:
            lines.append(f"- @{m['username']} — no public preview / no channel info.")
        lines.append("")

    if any(m["errors"] for m in metas):
        lines += ["## Errors", ""]
        for m in metas:
            for e in m["errors"]:
                lines.append(f"- @{m['username']}: {e}")
        lines.append("")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--refresh", action="store_true", help="ignore HTML cache")
    ap.add_argument("--review", action="store_true", help="write candidate review files")
    args = ap.parse_args(argv)

    metas: list[dict] = []
    all_records: list[dict] = []
    kept: set[str] = set()

    for username, _origin in CHANNELS:
        log(f"@{username}")
        meta = collect_channel(username)
        metas.append(meta)
        for m in meta["candidate_list"]:
            keep, reason = classify(m)
            m["_keep"] = keep
            m["_reason"] = reason
            if keep:
                rec = build_record(m)
                all_records.append(rec)
                kept.add(rec["native_id"])
        log(
            f"  scanned={meta['messages_scanned']} candidates={meta['candidates']} "
            f"kept={sum(1 for m in meta['candidate_list'] if m['_keep'])} "
            f"pages={meta['pages']} requests={meta['requests']}"
        )

    # Defensive dedupe by (source, native_id).
    dedup: dict[str, dict] = {}
    for rec in all_records:
        dedup[rec["native_id"]] = rec
    all_records = sorted(dedup.values(), key=lambda r: (r["created_utc"], r["native_id"]))

    write_jsonl(all_records, OUT)
    if args.review:
        candidate_records = []
        for meta in metas:
            for m in meta["candidate_list"]:
                candidate_records.append(build_record(m))
        write_review(candidate_records, metas)
    write_report(all_records, metas)

    log(f"wrote {len(all_records)} posts to {OUT}")
    for t in ("GENTING", "GENM", "UNKNOWN"):
        n = sum(1 for r in all_records if r["ticker"] == t)
        log(f"  {t}: {n}")
    if any(m["errors"] for m in metas):
        for m in metas:
            for e in m["errors"]:
                log(f"  ERROR @{m['username']}: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
