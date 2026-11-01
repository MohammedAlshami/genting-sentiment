# Genting news collection report

**Output:** `data/raw/news_articles.jsonl`
**Window:** 2 Nov 2025 → 2 Nov 2026 (Malaysian time, UTC+8)
**Records:** 298 full-text articles from 24 publishers
**Validation:** `python3 -m genting.validate data/raw/news_articles.jsonl` → **OK, 0 errors**, 0 empty bodies, 0 duplicate body texts.

---

## 1. What was collected

| Metric | Value |
| --- | --- |
| Articles | **298** |
| Malaysian publishers | **187** |
| International / regional publishers | **111** |
| Distinct publishers | 24 |
| Total words of body text | ~121,300 |
| Median article length | 2,441 characters |
| Earliest article | 2025-11-02 04:02 MYT |
| Latest article | 2026-10-29 14:00 MYT |
| Languages | English 297, Malay 1 |
| Paywalled (public stub only) | 2 (both Nikkei Asia) |

Each record has `record_type: "article"`, `source` (`news_<publisher>`), `channel`, canonical `url`,
`title`, `author` where the page shows one, integer `published_utc`, full `body`, `tickers`,
`lang`, and a small `raw` object containing the publisher, extractor, paywall flag,
Google News URL, and `malaysian_publisher` (boolean).

### Tickers

| Ticker | Articles |
| --- | --- |
| `GENM` (Genting Malaysia, Bursa 4715) | 251 |
| `GENTING` (Genting Berhad, Bursa 3182) | 222 |

Many articles cover both companies and carry both tickers.

### Publishers

| Publisher | Scope | Articles |
| --- | --- | ---: |
| GGRAsia | intl (Asian gaming trade) | 47 |
| BusinessToday Malaysia | MY | 45 |
| The Edge Malaysia | MY | 44 |
| The Star | MY | 43 |
| Asia Gaming Brief | intl (Asian gaming trade) | 37 |
| New Straits Times | MY | 22 |
| The Malaysian Reserve | MY | 17 |
| CDC Gaming Reports | intl | 8 |
| Free Malaysia Today | MY | 6 |
| The Business Times (SG) | intl | 5 |
| Focus Gaming News | intl | 4 |
| iGaming Business | intl | 3 |
| Malay Mail | MY | 3 |
| The Rakyat Post | MY | 2 |
| Nikkei Asia | intl | 2 |
| The Straits Times (SG) | intl | 2 |
| Bernama | MY | 1 |
| South China Morning Post | intl | 1 |
| Yahoo Finance | intl | 1 |
| EdgeProp Malaysia | MY | 1 |
| Varnam Malaysia | MY | 1 |
| RAM Ratings | MY | 1 |
| KLSE Screener | MY | 1 |
| GGB Magazine | intl | 1 |

The main file deliberately includes regional/international trade coverage of Genting Berhad and
Genting Malaysia because it carries the same corporate events and is useful for sentiment.
Every record is flagged `raw.malaysian_publisher`; filter on it for a Malaysian-only view
(187 records).

### Monthly distribution

| Month | Articles |
| --- | ---: |
| Nov 2025 | 42 |
| Dec 2025 | 60 |
| Jan 2026 | 3 |
| Feb 2026 | 12 |
| Mar 2026 | 9 |
| Apr 2026 | 25 |
| May 2026 | 26 |
| Jun 2026 | 6 |
| Jul 2026 | 14 |
| Aug 2026 | 26 |
| Sep 2026 | 37 |
| Oct 2026 | 38 |

The January, March and June troughs are genuine: those months carried mostly
Genting Plantations, Genting Singapore, estate-dispute, road-charge and lifestyle stories,
which are outside the two-company scope.

---

## 2. Method

### Discovery
- **43 Google News RSS queries** (`hl=en-MY&gl=MY&ceid=MY:en`) built from the brief:
  `"Genting" Malaysia`, `"Genting Berhad"`, `"Genting Malaysia"`, `GENM`,
  `"Genting rights issue"`, `"Genting 3182"`, `"Genting debt"`, `"Resorts World Genting"`,
  `"Genting New York"`, `"Genting Bhd"`, `"Genting group"`, plus earnings, dividend, bond,
  sukuk, Fitch/Moody's, layoffs, tax, share-price and result queries, and `site:` queries for
  The Edge, The Star, NST, The Malaysian Reserve, Focus Malaysia, Bernama, The Sun, Malay Mail,
  FMT, KLSE Screener, The Malaysian Insight, Malaysiakini, The Rakyat Post, The Vibes and EdgeProp.
- A single year-long Google News query is ranked and capped at ~50 items, so every query was
  walked **month by month** and split recursively whenever a slice hit the cap: 579 RSS
  requests. This raised the raw discovery set from 1,348 to **4,070 items**.
- **WordPress REST APIs** were used for full-text search of BusinessToday Malaysia, GGRAsia,
  The Rakyat Post, The Sun and The Malaysian Reserve (621 matching posts in the window).
- **KLSE Screener** stock-news pages for 3182 and 4715 were checked; its news items are
  republished copies of the original publishers, so they were used only when no original was
  available.

### Google News link resolution
Google News RSS links are opaque redirects. Each was resolved through Google's
`batchexecute` endpoint (`Fbv4je`) using the `data-n-a-sg` / `data-n-a-ts` tokens from the
article page. 1,061 candidate links were resolved; 0 unresolved.

### Extraction
- Requested pages with `curl_cffi` (`impersonate="chrome"`), browser-like headers and
  ≥1.15 s between requests to the same publisher, with exponential backoff on 429/5xx.
- `trafilatura` first, then `readability-lxml`, then a BeautifulSoup fallback.
- **New Straits Times** serves a JS shell on the canonical URL; its AMP page was used.
- **The Star** serves truncated bodies on some first requests; its public `?s=app` view was
  used and short bodies were re-fetched. No login or paywall bypass was used.
- Boilerplate (subscribe prompts, related-link blocks, "Follow us", copyright lines) was
  stripped. Bodies are normalised whitespace, no HTML.
- Paywall rule: body is only the public portion **and** a subscriber/sign-in marker is present.
  Two Nikkei Asia records meet this; `raw.paywalled = true`.

### Relevance filter
An article was kept only if it substantively concerns Genting Berhad / Genting Malaysia /
GENM / 3182 / 4715. Dropped categories (with counts in the build log):
- passing mentions in market roundups and "Trading ideas"/"Companies in the news" lists;
- Genting Plantations (GENP), Genting Singapore (GENS/G13), Genting Property and
  Genting Xintiandi stories — different listed/private entities;
- estate/inheritance disputes involving the Lim family;
- Genting Highlands travel, hotels, restaurants, concerts, theme-park, road/toll and
  property stories that are about the place rather than the companies;
- crime/accident briefs at the resort that do not mention the companies;
- Bursa announcements (moved to the bonus file).

### Deduplication
- Canonical URL (tracking parameters stripped, `www`/trailing slash normalised).
- Near-duplicate titles at 0.90 sequence similarity, preferring the original publisher over
  aggregators (KLSE Screener) and the longer body.
- The Edge Singapore's syndicated copies of The Edge Malaysia stories were removed
  (13 records).

---

## 3. Known gaps and caveats

1. **Bernama is under-represented (1 article).** Google News returns many Bernama market
   roundups that only mention Genting in passing; company-specific Bernama pieces are largely
   syndicated from other outlets. The one retained piece is the IDSS suspension brief.
2. **No Malay or Chinese-language depth.** Only one Malay article survived the relevance
   filter; Chinese-language Malaysian outlets (Sin Chew, Nanyang, China Press) were not
   separately harvested. The brief's queries and publisher list were English-language.
3. **Foreign local-news coverage is excluded.** US local outlets covering Resorts World New
   York City (Queens Gazette, CBS New York, etc.) and Las Vegas outlets covering Resorts World
   Las Vegas were only kept when the article substantively named Genting Berhad/Malaysia.
   This keeps the file about the listed companies rather than every property mention.
4. **Paywalls.** Two Nikkei Asia pieces are public stubs only (`raw.paywalled=true`). The Star
   and The Edge Malaysia full text was available through their public web/app views.
5. **Timestamp precision.** Google News often exposes only a date (07:00 GMT placeholder).
   Page metadata (`article:published_time`, JSON-LD `datePublished`) was preferred where
   present; otherwise the Google timestamp is used. URL-date cross-checks found **0**
   mismatches greater than one day.
6. **Title suffixes.** Publisher suffixes (" - The Star", " | New Straits Times", etc.) were
   stripped; a few titles retain the publisher's own headline punctuation.
7. **Author coverage** is best for The Star (42/43), NST (22/22), FMT (6/6), Malay Mail (3/3) and
   the trade press that publishes bylines. The Edge, BusinessToday and GGRAsia do not expose a
   byline in their article HTML, so `author` is `null` for those.

---

## 4. Bonus: Bursa Malaysia announcements

**Output:** `data/raw/bursa_announcements.jsonl`
**Records:** 376 (65 Genting Berhad + 311 Genting Malaysia), all with extracted announcement text.

- Source: Bursa Malaysia company-announcement search API
  (`/api/v1/announcements/search?company=3182|4715&ann_type=company`), window 2 Nov 2025 →
  2 Nov 2026.
- Full text from `disclosure.bursamalaysia.com/FileAccess/viewHtml?e=<ann_id>`.
- Fields: `record_type: "announcement"`, `source`, `channel`, `native_id`, `ticker`,
  `stock_code`, `company`, `title`, `published_utc`, `url`, `body`, `raw`.
- Bursa publishes these with **date only**; `published_utc` is set to **12:00 MYT** on the
  announcement date and `raw.time_precision` records this. Do not treat it as a precise time.

---

## 5. Reproduction

```bash
python3 scripts/news_discover.py      # initial Google News queries
python3 scripts/news_discover2.py     # month-by-month deep discovery
python3 scripts/news_resolve.py       # resolve Google News redirects
python3 scripts/news_wp.py            # WordPress REST full-text posts
python3 scripts/news_fetch.py         # fetch + extract article bodies
python3 scripts/news_repair.py        # second pass for truncated Star bodies
python3 scripts/news_build.py         # filter, dedupe, write JSONL + rejects
python3 scripts/bursa_collect.py      # bonus Bursa announcements
python3 -m genting.validate data/raw/news_articles.jsonl
```

Caches live under `data/raw/cache/` (`gn/`, `gn_deep/`, `articles/`, `resolved.json`,
`fetched.json`, `wp_posts.json`, `rejected.json`) so re-runs do not refetch.
