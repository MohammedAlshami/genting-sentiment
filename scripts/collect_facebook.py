#!/usr/bin/env python3
"""Collect publicly accessible Facebook posts/comments about Genting stock.

Only logged-out, public HTML is used: no cookies, no credentials, no login wall
is bypassed. Facebook serves a handful of public page posts and up to ten top
comments per post in the logged-out HTML; this collector records exactly what
was visible.

Discovery: DuckDuckGo HTML and Yahoo web search with ``site:facebook.com``
queries. The search results are not fetched here; their URLs are the seed list.
"""

from __future__ import annotations

import base64
import hashlib
import html as html_lib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "raw" / "cache" / "facebook" / "posts"
OUT = ROOT / "data" / "raw" / "facebook_public.jsonl"
REPORT = ROOT / "data" / "raw" / "facebook_report.md"
MANIFEST = ROOT / "data" / "raw" / "cache" / "facebook" / "manifest.json"

WINDOW_START = int(datetime(2024, 11, 2, tzinfo=timezone.utc).timestamp())
WINDOW_END = int(datetime(2026, 11, 2, 23, 59, 59, tzinfo=timezone.utc).timestamp())

# Curated seeds: public posts whose text is about Genting Berhad (GENTING,
# 3182) or Genting Malaysia (GENM, 4715), found via search-engine discovery.
# ticker is assigned only where the post's own text is unambiguous.
SEEDS = [
    # --- October 2026 rights issue / share-price collapse ---
    {
        "url": "https://www.facebook.com/elitistaofficial/posts/saham-genting-jatuh-17-ke-paras-terendah-sejak-2007-selepas-umum-nak-kumpul-moda/1134586812440649/",
        "ticker": "GENTING",
        "query": "site:facebook.com genting saham",
    },
    {
        "url": "https://www.facebook.com/nanyang.nysp/posts/%E4%BA%91%E9%A1%B6%E5%A4%A7%E9%A9%ACgenm4715%E4%B8%BB%E6%9D%BF%E6%B6%88%E8%B4%B9%E8%82%A1%E8%82%A1%E4%BB%B7%E8%B7%8C%E5%B9%85%E8%A7%A6%E5%8F%8A%E9%A9%AC%E4%BA%A4%E6%89%80%E8%A7%84%E5%AE%9A%E7%9A%84%E5%8D%96%E7%A9%BA%E4%BB%B7%E6%A0%BC%E9%99%90%E5%88%B6%E5%AF%BC%E8%87%B4%E8%AF%A5%E8%82%A1%E7%9A%84%E5%8D%B3%E6%97%A5%E5%8D%96%E7%A9%BAidss%E6%9A%82%E5%81%9C%E6%98%8E%E6%97%A98%E6%97%B630%E5%88%86%E6%89%8D%E6%81%A2%E5%A4%8D%E5%8D%97%E6%B4%8B%E5%95%86%E6%8A%A5-%E4%BA%91%E9%A1%B6%E5%A4%A7%E9%A9%AC-genm-%E8%82%A1%E4%BB%B7-%E6%96%B0%E9%97%BB/1538328294995121/",
        "ticker": "GENM",
        "query": "site:facebook.com GENM 4715",
    },
    {
        "url": "https://www.facebook.com/theedgemalaysia/posts/highlight-genting-bhd-klgenting-plans-to-undertake-a-proposed-rights-issue-to-ra/1565242995647549/",
        "ticker": "GENTING",
        "query": "site:facebook.com genting rights issue",
    },
    {
        "url": "https://www.facebook.com/sharestraders/posts/what-happen-to-genting-shareskey-details-of-the-drop-the-cash-call-genting-annou/1899278771194349/",
        "ticker": "GENTING",
        "query": "site:facebook.com genting rights issue",
    },
    {
        "url": "https://www.facebook.com/nstonline/posts/nstbusinesstimes-genting-bhds-proposed-rm125-billion-rights-issue-is-expected-to/1569508338544066/",
        "ticker": "GENTING",
        "query": "site:facebook.com genting rights issue",
    },
    {
        "url": "https://www.facebook.com/TheStarOnline/posts/genting-bhd-has-proposed-a-rights-issue-to-raise-fresh-cash-amid-rising-credit-c/1602101698619016/",
        "ticker": "GENTING",
        "query": "site:facebook.com genting rights issue",
    },
    {
        "url": "https://www.facebook.com/61581865126018/posts/%E9%A2%84%E7%AE%97%E6%A1%882027%E4%B9%9F%E5%B8%AE%E4%B8%8D%E5%88%B0%E5%AE%83%E4%BA%86%E4%BD%A0%E4%B8%80%E5%AE%9A%E8%A6%81%E7%9F%A5%E9%81%93%E7%9A%84%E4%BA%91%E9%A1%B6%E6%B6%88%E6%81%AF/122158909905062170/",
        "ticker": "GENTING",
        "query": "site:facebook.com genting rights issue",
    },
    {
        "url": "https://www.facebook.com/business2corp/posts/%E4%B8%96%E7%BA%AA%E5%A4%A7%E8%B7%B3%E6%B0%B4%E4%BA%91%E9%A1%B63182%E5%8D%95%E6%97%A5%E7%8B%82%E6%B3%BB2287%E8%B7%8C%E8%87%B3145%E4%BB%A4%E5%90%89%E5%B8%82%E5%80%BC%E8%B7%8C%E7%A0%B470/1092465360429055/",
        "ticker": "GENTING",
        "query": "site:facebook.com genting 3182",
    },
    {
        "url": "https://www.facebook.com/moneypov/videos/%E4%BA%91%E9%A1%B6%E8%82%A1%E4%BB%B7%E5%A4%A7%E8%B7%8C23%E8%83%8C%E5%90%8E%E5%88%B0%E5%BA%95%E5%8F%91%E7%94%9F%E4%BB%80%E4%B9%88%E4%BA%8B%E8%BF%99%E6%AC%A1-rights-issue%E5%8F%AF%E8%83%BD%E4%B8%8D/3213436635514573/",
        "ticker": "GENTING",
        "query": "site:facebook.com genting rights issue",
    },
    {
        "url": "https://www.facebook.com/9shares.my/posts/%E4%BA%91%E9%A1%B6genting-3182%E8%82%A1%E4%BB%B7%E4%BD%8E%E8%BF%B7%E9%9B%86%E5%9B%A2%E4%B8%BB%E5%B8%AD%E4%B8%B9%E6%96%AF%E9%87%8C%E6%9E%97%E5%9B%BD%E6%B3%B0%E7%BB%A7%E7%BB%AD%E9%97%B7%E5%A3%B0%E6%89%AB%E8%B4%A7/1415792820671438/",
        "ticker": "GENTING",
        "query": "site:facebook.com genting 3182",
    },
    # --- 2025-2026 privatisation of GENM by Genting Bhd ---
    {
        "url": "https://www.facebook.com/nazrieconomics/posts/apa-sebenarnya-cerita-genting-nak-beli-genting-ni-ceritanya-begini-genting-bhd-s/821796710787542/",
        "ticker": "GENM",
        "query": "site:facebook.com genting saham",
    },
    {
        "url": "https://www.facebook.com/DagangNews/posts/menurut-genting-pengambilalihan-ini-bertujuan-memperoleh-kawalan-statutori-ke-at/1435686615226251/",
        "ticker": "GENM",
        "query": "site:facebook.com genting saham",
    },
    {
        "url": "https://www.facebook.com/LatestMalaysia/posts/genting-bhd-proposes-rm674-billion-privatisation-of-genting-malaysia-offering-rm/1224327853049730/",
        "ticker": "GENM",
        "query": "site:facebook.com genting privatization",
    },
    {
        "url": "https://www.facebook.com/BFMradio/posts/-genting-plans-to-privatise-genting-malaysia-through-rm674-billion-buyout-offeri/1368895061274802/",
        "ticker": "GENM",
        "query": "site:facebook.com genting privatization",
    },
    {
        "url": "https://www.facebook.com/financemalaysia/posts/breaking-newsgenting-makes-rm674bil-privatisation-bid-for-genm-by-offering-rm235/1411255851002614/",
        "ticker": "GENM",
        "query": "site:facebook.com genm saham",
    },
    {
        "url": "https://www.facebook.com/financemalaysia/posts/update-genm-privatisationtoday-the-total-shares-held-by-genting-is-50105-%EF%B8%8F-hence/1431799182281614/",
        "ticker": "GENM",
        "query": "site:facebook.com genm saham",
    },
    {
        "url": "https://www.facebook.com/theedgemalaysia/posts/genting-is-looking-to-take-genting-malaysia-private-at-rm235-per-share-this-and-/1248351164003402/",
        "ticker": "GENM",
        "query": "site:facebook.com \"genting malaysia\" saham",
    },
    {
        "url": "https://www.facebook.com/RinggitDanSen/photos/genting-cadang-swastakan-genting-malaysia-bernilai-rm674-biliongenting-bhd-hari-/1235505301945523/",
        "ticker": "GENM",
        "query": "site:facebook.com genting saham",
    },
    {
        "url": "https://www.facebook.com/theedgemalaysia/videos/edge-weekly-should-genting-malaysia-shareholders-stay-or-fold/818056110997808/",
        "ticker": "GENM",
        "query": "site:facebook.com \"genting malaysia\" saham",
    },
    {
        "url": "https://www.facebook.com/ZietInvests/videos/gentings-privatization-bid-might-be-stalled-but-they-arent-folding-their-cards-y/908376261790250/",
        "ticker": "GENM",
        "query": "site:facebook.com genting privatization",
    },
    {
        "url": "https://www.facebook.com/financialfreedom001/videos/%E4%BA%91%E9%A1%B6%E5%8F%AF%E4%BB%A5%E5%94%94q%E6%B4%BE%E6%81%AF-%E9%97%AE%E4%BD%A0%E6%AD%BB%E6%9C%AA/1536737354196451/",
        "ticker": "GENM",
        "query": "site:facebook.com \"云顶\" 股票",
    },
    {
        "url": "https://www.facebook.com/8TV.NEWS/videos/%E4%BA%91%E9%A1%B6%E6%96%A567%E4%BA%BF%E7%A7%81%E6%9C%89%E5%8C%96-%E4%BA%91%E9%A1%B6%E5%A4%A7%E9%A9%AC%E6%96%99%E9%A9%AC%E8%82%A1%E4%B8%8B%E5%B8%8220251014-%E5%85%AB%E5%BA%A6%E7%A9%BA%E9%97%B4/1314511780144642/",
        "ticker": "GENM",
        "query": "site:facebook.com \"云顶\" 股票",
    },
    # --- Other in-window GENTING/GENM stock posts ---
    {
        "url": "https://www.facebook.com/thebusinesstimes/posts/genting-berhad-now-sits-at-the-lowest-investment-grade-level-after-moodys-and-sp/1409265698088121/",
        "ticker": "GENTING",
        "query": "site:facebook.com \"genting berhad\" saham",
    },
    {
        "url": "https://www.facebook.com/theedgemalaysia/posts/hot-stock-genting-bhds-klgenting-shares-fell-nearly-5-on-friday-morning-after-it/1518213140350535/",
        "ticker": "GENTING",
        "query": "site:facebook.com \"genting berhad\" saham",
    },
    {
        "url": "https://www.facebook.com/bursascreener/posts/-stock-pick-spotlight-genting-3182-fbmklcigenting-slipped-to-rm295-after-testing/1188705799942940/",
        "ticker": "GENTING",
        "query": "site:facebook.com genting 3182",
    },
    {
        "url": "https://www.facebook.com/TIAcademyMandarin/videos/genting-3182-%E8%82%A1%E4%BB%B7%E4%B8%8B%E8%B7%8C%E7%9C%9F%E6%AD%A3%E5%8E%9F%E5%9B%A0-%E8%B7%8C%E7%A0%B4%E5%BA%84%E5%AE%B6%E4%BB%B7%E4%BD%8D%E6%98%AF%E6%9C%BA%E4%BC%9A%E5%90%97foll/1930200921190563/",
        "ticker": "GENTING",
        "query": "site:facebook.com genting 3182",
    },
    {
        "url": "https://www.facebook.com/TIAcademyMandarin/videos/%E4%BA%91%E9%A1%B6-genm-4715-%E8%82%A1%E4%BB%B7rm17%E7%AE%97%E4%BE%BF%E5%AE%9C%E4%BA%86%E5%90%97followers-top-fansgenm-%E4%BA%91%E9%A1%B6-%E9%A9%AC%E8%82%A1-4715-gentinghighlands-%E4%BA%91%E9%A1%B6%E8%82%A1%E7%A5%A8/1429956592529333/",
        "ticker": "GENM",
        "query": "site:facebook.com GENM 4715",
    },
    {
        "url": "https://www.facebook.com/TIAcademyMandarin/videos/genm-4715%E8%82%A1%E4%BB%B7%E8%B7%8C%E5%88%B0%E8%BF%99%E9%87%8C%E5%8F%8D%E5%BC%B9%E5%BA%84%E5%AE%B6%E4%BB%B7%E4%BD%8D%E5%9C%A8-rm2-%E6%98%AF%E6%9C%BA%E4%BC%9A%E5%90%97followers3%E6%9C%883%E5%8F%B7cny%E5%A4%A7%E4%BC%98%E6%83%A05%E4%B8%AA%E4%BD%8D%E5%AD%90%E7%9C%8B%E7%95%99%E8%A8%80-4715-genm-genting-%E4%BA%91%E9%A1%B6-%E9%A9%AC%E8%82%A1/1587249179179724/",
        "ticker": "GENM",
        "query": "site:facebook.com genting 3182",
    },
    {
        "url": "https://www.facebook.com/TIAcademyMandarin/posts/%E6%AF%8F%E6%97%A5%E8%81%8A%E4%B8%80%E8%82%A1genting-malaysia-berhadgenm4715%E4%BB%8A%E5%A4%A9%E6%88%91%E4%BB%AC%E6%9D%A5%E8%81%8A%E4%B8%80%E8%81%8A%E6%9C%AC%E5%9C%B0%E7%9F%A5%E5%90%8D%E8%93%9D%E7%AD%B9%E8%82%A1-%E4%BA%91%E9%A1%B6%E5%A4%A7%E9%A9%ACgenting-malaysia-berhad-/1179823977500134/",
        "ticker": "GENM",
        "query": "site:facebook.com genm 4715 2025",
    },
    {
        "url": "https://www.facebook.com/TIAcademyMandarin/videos/genm-4715-%E7%A7%81%E6%9C%89%E5%8C%96%E5%A4%B1%E8%B4%A5%E4%BD%86%E6%98%AF%E8%82%A1%E4%BB%B7%E4%B8%8B%E8%B7%8C%E4%BA%86%E6%8A%95%E8%B5%84%E8%80%85%E8%A6%81%E5%B0%8F%E5%BF%83followers%E9%A9%AC%E8%82%A1-genm-4715-genting-%E4%BA%91%E9%A1%B6/878968144470181/",
        "ticker": "GENM",
        "query": "site:facebook.com genm 4715 2025",
    },
    {
        "url": "https://www.facebook.com/Windscopo001/posts/1486926086127859/",
        "ticker": "GENM",
        "query": "site:facebook.com genm 4715 2025",
    },
    {
        "url": "https://www.facebook.com/9shares.my/photos/%E7%A9%86%E8%BF%AA%E4%B8%8B%E8%B0%83%E4%BA%91%E9%A1%B6%E9%9B%86%E5%9B%A2%E4%BA%91%E9%A1%B6%E5%A4%A7%E9%A9%AC%E5%8F%8A%E6%96%B0%E5%8A%A0%E5%9D%A1%E4%BA%91%E9%A1%B6%E8%AF%84%E7%BA%A7%E4%BA%91%E9%A1%B6genting-3812%E5%8F%8A%E4%BA%91%E9%A1%B6%E5%A4%A7%E9%A9%ACgenm-4715%E8%82%A1%E4%BB%B7%E5%9C%A8%E5%91%A8%E4%B8%80%E5%8F%8C%E5%8F%8C%E6%8F%92%E6%B0%B4%E5%9B%BD%E9%99%85%E8%AF%84%E4%BB%85%E6%9C%BA%E6%9E%84%E7%A9%86%E8%BF%AA%E8%AF%84%E7%BA%A7moodys-rating/1166283722289017/",
        "ticker": "GENTING",
        "query": "site:facebook.com genm 4715 2025",
    },
    {
        "url": "https://www.facebook.com/kc.goh.52/photos/-genm4715%E9%87%8F%E4%BB%B7%E6%97%B6%E7%A9%BA%E5%86%8D%E5%BA%A6%E5%8E%8B%E7%BC%A9%E5%88%A9%E5%A5%BD%E7%9C%8B%E9%87%8D%E8%BF%94248%E5%88%A9%E7%A9%BA%E6%81%90%E8%80%83%E9%AA%8C146%E9%98%B2%E7%BA%BF%E5%BF%AB%E9%80%9F%E9%97%AE%E7%AD%94%E2%91%A0-%E8%8B%A5%E6%B6%88%E6%81%AF%E5%88%A9%E5%A5%BD%E7%9F%AD%E6%9C%9F-%E4%B8%AD%E6%9C%9F-%E9%95%BF%E6%9C%9F%E7%9B%AE%E6%A0%87%E7%9F%AD%E6%9C%9F12%E5%91%A8%E8%8B%A5%E6%94%BE%E9%87%8F%E7%AA%81%E7%A0%B4-214223%E7%9F%AD%E7%BA%BF%E4%B9%B0%E7%9B%98%E5%B0%86%E5%9B%9E%E6%B5%81/10239625256394195/",
        "ticker": "GENM",
        "query": "site:facebook.com genm 4715 2025",
    },
    {
        "url": "https://www.facebook.com/BZbiznews/photos/%E4%B8%8A%E5%B8%82%E5%85%AC%E5%8F%B8%E5%8A%A8%E6%80%81%E4%BB%A4%E5%90%89%E5%9B%9E%E5%8D%87%E7%BE%8E%E5%85%83%E8%B4%B7%E6%AC%BE%E8%8A%82%E7%9C%81%E7%BA%B8%E4%B8%8A%E5%88%A9%E6%81%AF-%E4%BA%91%E9%A1%B6%E5%A4%A7%E9%A9%AC%E9%A6%96%E5%AD%A3%E5%87%80%E5%88%A9%E6%B6%A826%E4%BA%91%E9%A1%B6%E5%A4%A7%E9%A9%ACgenm4715%E4%B8%BB%E6%9D%BF%E6%B6%88%E8%B4%B9%E8%82%A12025%E8%B4%A2%E6%94%BF%E5%B9%B4%E7%AC%AC1%E5%AD%A3%E8%90%A5%E6%94%B6%E9%99%8D%E8%8E%B7%E5%88%A9%E8%B5%B7%E4%BD%86%E8%BF%99%E5%92%8C%E5%85%AC%E5%8F%B8%E4%B8%9A%E5%8A%A1%E8%BF%90%E8%90%A5%E6%97%A0%E5%85%B3%E4%BA%91%E9%A1%B6%E5%A4%A7%E9%A9%AC/589666134150210/",
        "ticker": "GENM",
        "query": "site:facebook.com genm 4715 2025",
    },
    {
        "url": "https://www.facebook.com/starbizmy/posts/genting-declared-a-final-single-tier-dividend-of-50-sen-per-ordinary-share-for-f/1561850332614907/",
        "ticker": "GENTING",
        "query": "site:facebook.com genting dividend 2025",
    },
    {
        "url": "https://www.facebook.com/BilyonaryoPh/posts/malaysian-billionaire-lim-kok-thays-genting-has-slashed-its-dividend-after-posti/1251912973810814/",
        "ticker": "GENTING",
        "query": "site:facebook.com genting dividend 2025",
    },
    {
        "url": "https://www.facebook.com/starbizmy/posts/1189820653151212/",
        "ticker": "GENM",
        "query": "site:facebook.com genm 2024 saham",
    },
]


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode()).hexdigest()[:12]


def decode_json_string(text: str | None) -> str | None:
    """Decode \\uXXXX escapes captured from Facebook's embedded JSON."""
    if not text:
        return text
    try:
        return json.loads('"' + text.replace('"', '\\"') + '"')
    except json.JSONDecodeError:
        return text


def norm(text: str | None) -> str:
    if not text:
        return ""
    text = html_lib.unescape(text)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fetch(url: str) -> tuple[str, int, str]:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{sha1(url)}.html"
    if path.exists() and path.stat().st_size > 10_000:
        return path.read_text(encoding="utf-8"), 200, url
    last_err = None
    for attempt in range(3):
        try:
            r = requests.get(url, impersonate="chrome", timeout=45, allow_redirects=True)
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(2**attempt * 3)
                continue
            path.write_text(r.text, encoding="utf-8")
            time.sleep(2.0)
            return r.text, r.status_code, str(r.url)
        except Exception as exc:  # network errors
            last_err = exc
            time.sleep(2**attempt * 3)
    raise RuntimeError(f"fetch failed for {url}: {last_err!r}")


def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk(value)


def load_json_scripts(html: str):
    objects = []
    for raw in re.findall(r'<script type="application/json"[^>]*>(.*?)</script>', html, re.S):
        try:
            objects.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return objects


def decode_comment_id(value: str | None) -> str | None:
    if not value:
        return None
    try:
        padded = value + "=" * (-len(value) % 4)
        return base64.b64decode(padded).decode("utf-8", "replace")
    except Exception:
        return None


def pick_post_id(html: str, objects) -> str | None:
    counts: dict[str, int] = {}
    for obj in walk(objects):
        pid = obj.get("post_id")
        if isinstance(pid, str) and pid.isdigit():
            counts[pid] = counts.get(pid, 0) + 1
    if counts:
        return max(counts, key=counts.get)
    # fall back to the URL's numeric id (video/photo id)
    nums = re.findall(r"/(\d+)/?$", html)
    return nums[-1] if nums else None


def main() -> int:
    records: list[dict] = []
    seen: set[tuple[str, str]] = set()
    fetch_log = []
    skipped = []

    for seed in SEEDS:
        url = seed["url"]
        html, status, final_url = fetch(url)
        objects = load_json_scripts(html)

        post_id = pick_post_id(html, objects)
        if not post_id:
            skipped.append({"url": url, "reason": "no post id"})
            continue

        # Find the main story object (post with a message) if present.
        story = None
        for obj in walk(objects):
            if (
                obj.get("__typename") == "Story"
                and str(obj.get("post_id")) == post_id
                and isinstance(obj.get("comet_sections"), dict)
            ):
                msg = (
                    ((obj.get("comet_sections") or {}).get("content") or {})
                    .get("story", {})
                    .get("message")
                    or {}
                ).get("text")
                if msg:
                    story = obj
                    break

        message = ""
        author = None
        author_id = None
        created = None
        time_source = None

        if story:
            message = (
                ((story.get("comet_sections") or {}).get("content") or {})
                .get("story", {})
                .get("message", {})
                .get("text", "")
            )
            created = story.get("creation_time")
            time_source = "story.creation_time"
            actors = story.get("actors") or []
            if actors:
                author = actors[0].get("name")
                author_id = actors[0].get("id")

        # Video pages: the story post id differs from the video id, so take the
        # video id from the URL and use that video's publish_time.
        if created is None:
            video_match = re.search(r"/(?:videos|reel)/(?:[^/]+/)?(\d+)/?$", url)
            video_id = video_match.group(1) if video_match else None
            if video_id:
                m = re.search(r'"videoId":"' + re.escape(video_id) + r'"', html)
                if m:
                    pm = re.search(r'"publish_time":(\d+)', html[m.start() : m.start() + 1500])
                    if pm:
                        created = int(pm.group(1))
                        time_source = "video.publish_time"

        # Photo / post pages without a Story: nearest creation_time to post_id.
        if created is None:
            for m in re.finditer(r'"post_id":"' + re.escape(post_id) + r'"', html):
                window = html[max(0, m.start() - 2500) : m.start() + 2500]
                times = re.findall(r'"creation_time":(\d+)', window)
                if times:
                    created = int(times[0])
                    time_source = "story.creation_time (near post_id)"
                    break

        # Last resort: the first creation_time on the page.
        if created is None:
            times = re.findall(r'"creation_time":(\d+)', html)
            if times:
                created = int(times[0])
                time_source = "first creation_time on page"

        # Message fallback: the longest message that matches og:description.
        og_desc = ""
        m = re.search(r'<meta property="og:description" content="([^"]*)"', html)
        if m:
            og_desc = norm(html_lib.unescape(m.group(1)))
        if not message:
            candidates = []
            for m in re.finditer(r'"message":\{"text":"((?:[^"\\]|\\.)*)"', html):
                try:
                    text = json.loads('"' + m.group(1) + '"')
                except json.JSONDecodeError:
                    continue
                text = norm(text)
                if text:
                    candidates.append(text)
            if candidates:
                # Prefer the candidate sharing the og:description prefix.
                prefix = og_desc[:40]
                match = [c for c in candidates if prefix and c.startswith(prefix)]
                message = match[0] if match else max(candidates, key=len)
            elif og_desc:
                message = og_desc

        if not message and og_desc:
            message = og_desc

        # Author fallback: actors array.
        if not author:
            am = re.search(r'"actors":\[\{"__typename":"User","name":"([^"]+)"', html)
            if am:
                author = html_lib.unescape(decode_json_string(am.group(1)))
                aid = re.search(
                    r'"actors":\[\{"__typename":"User","name":"' + re.escape(am.group(1)) + r'","id":"(\d+)"',
                    html,
                )
                if aid:
                    author_id = aid.group(1)

        if author:
            author = html_lib.unescape(decode_json_string(author))

        # Comments: all Comment nodes rendered in the logged-out page.
        comments: dict[str, dict] = {}
        for obj in walk(objects):
            if obj.get("__typename") != "Comment":
                continue
            body = (obj.get("body") or {}).get("text")
            if not body or not body.strip():
                continue
            cid = obj.get("legacy_fbid")
            if not cid:
                decoded = decode_comment_id(obj.get("id"))
                if decoded and "_" in decoded:
                    cid = decoded.rsplit("_", 1)[-1]
            if not cid:
                continue
            parent = None
            pd = obj.get("comment_direct_parent") or {}
            decoded_parent = decode_comment_id(pd.get("id"))
            if decoded_parent and "_" in decoded_parent:
                parent = decoded_parent.rsplit("_", 1)[-1]
            comments[str(cid)] = {
                "id": str(cid),
                "parent": parent,
                "depth": int(obj.get("depth") or 0),
                "created": obj.get("created_time"),
                "author": (obj.get("author") or {}).get("name"),
                "author_id": (obj.get("author") or {}).get("id"),
                "body": norm(body),
            }

        total_m = re.search(
            r'"comment_rendering_instance":\{"comments":\{"total_count":(\d+)\}', html
        )
        comment_total = int(total_m.group(1)) if total_m else None

        # Keep only comments with a timestamp in the window.
        comment_rows = []
        for c in sorted(comments.values(), key=lambda x: x["created"] or 0):
            if not c["created"] or not isinstance(c["created"], int):
                continue
            if not (WINDOW_START <= c["created"] <= WINDOW_END):
                continue
            comment_rows.append(c)

        if created is None or not (WINDOW_START <= created <= WINDOW_END):
            skipped.append(
                {
                    "url": url,
                    "post_id": post_id,
                    "created_utc": created,
                    "reason": "outside window or no timestamp",
                }
            )
            continue

        channel = "unknown"
        path = url.split("facebook.com/", 1)[-1]
        if path.startswith("groups/"):
            channel = "groups/" + path.split("/", 2)[1]
        else:
            channel = path.split("/", 1)[0]

        # Prefer the first substantive line: skip blank lines and lines that are
        # only hashtags/mentions/emoji, which are common on Facebook captions.
        lines = [ln.strip() for ln in message.splitlines() if ln.strip()]
        title = ""
        for line in lines:
            bare = re.sub(r"[#@][^\s#@]+", "", line).strip()
            bare = re.sub(r"[\W_]+", "", bare, flags=re.UNICODE)
            if len(bare) >= 14:
                title = line
                break
        if not title and lines:
            title = lines[0]
        if not title:
            title = f"{author or channel} post {post_id}"
        if len(title) > 200:
            title = title[:197].rstrip() + "..."

        raw = {
            "post_id": post_id,
            "story_id": story.get("id") if story else None,
            "page_id": author_id,
            "comment_total_count": comment_total,
            "comments_captured": len(comment_rows),
            "comment_gap": (comment_total - len(comment_rows))
            if comment_total is not None
            else None,
            "privacy": "Public" if '"description":"Public"' in html else None,
            "time_source": time_source,
            "discovery_query": seed["query"],
            "seed_ticker": seed["ticker"],
            "access_note": (
                "Fetched from the direct public post URL without cookies or login; "
                "Facebook served the post body and the top comments in logged-out HTML."
            ),
            "fetched_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "http_status": status,
            "final_url": final_url,
            "og_title": norm(
                (re.search(r'<meta property="og:title" content="([^"]*)"', html) or [None, None])[1]
            )[:1000]
            if re.search(r'<meta property="og:title" content="([^"]*)"', html)
            else None,
            "og_description": og_desc[:2000] or None,
            "body_truncated": bool(re.search(r"(\.\.\.|…)\s*$", message)),
        }

        post = {
            "record_type": "post",
            "source": "facebook",
            "channel": channel,
            "native_id": post_id,
            "ticker": seed["ticker"],
            "title": title,
            "author": author,
            "author_id": author_id,
            "created_utc": int(created),
            "url": url,
            "body": message or None,
            "score": None,
            "num_comments": comment_total,
            "lang": None,
            "raw": raw,
        }
        key = ("facebook", post_id)
        if key in seen:
            skipped.append({"url": url, "post_id": post_id, "reason": "duplicate post id"})
            continue
        seen.add(key)
        records.append(post)

        for c in comment_rows:
            ckey = ("facebook", c["id"])
            if ckey in seen:
                continue
            seen.add(ckey)
            sep = "&" if "?" in url else "?"
            records.append(
                {
                    "record_type": "reply",
                    "source": "facebook",
                    "channel": channel,
                    "native_id": c["id"],
                    "post_native_id": post_id,
                    "parent_native_id": c["parent"],
                    "depth": c["depth"],
                    "author": c["author"],
                    "author_id": c["author_id"],
                    "created_utc": int(c["created"]),
                    "body": c["body"],
                    "score": None,
                    "url": f"{url}{sep}comment_id={c['id']}",
                    "lang": None,
                    "raw": {
                        "post_id": post_id,
                        "comment_total_count": comment_total,
                        "comments_captured": len(comment_rows),
                        "comment_gap": (comment_total - len(comment_rows))
                        if comment_total is not None
                        else None,
                        "access_note": post["raw"]["access_note"],
                    },
                }
            )

        fetch_log.append(
            {
                "url": url,
                "post_id": post_id,
                "status": status,
                "created_utc": int(created),
                "comments_total": comment_total,
                "comments_captured": len(comment_rows),
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    log = {
        "window_start_utc": WINDOW_START,
        "window_end_utc": WINDOW_END,
        "seeds": len(SEEDS),
        "posts_written": sum(1 for r in records if r["record_type"] == "post"),
        "replies_written": sum(1 for r in records if r["record_type"] == "reply"),
        "fetch_log": fetch_log,
        "skipped": skipped,
    }
    (OUT.parent / "facebook_fetch_log.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    print(f"wrote {OUT} ({len(records)} records)")
    print(f"posts={log['posts_written']} replies={log['replies_written']}")
    for entry in skipped:
        print("skipped:", entry)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
