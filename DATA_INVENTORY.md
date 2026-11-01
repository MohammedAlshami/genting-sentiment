# Data inventory

Every dataset in the repository, with coverage, size and usability notes.
Counts are from `data/genting.db` on 2 Nov 2026; the compressed dump in this repo
restores to the same numbers.

## Totals

| Dataset | Count |
|---|---:|
| Conversation replies / comments | **217,451** |
| Conversation posts / videos / threads | **6,990** |
| Full news articles | **864** |
| Daily price bars | **4,917** (GENTING 2,459 + GENM 2,458) |
| LLM-scored replies | **9,015** across **119 months** |
| Structured financial rows | **2,962** |
| Ownership rows | **65** |
| Corporate-action rows | **40** |
| Company documents | **2,972 files / 482 PDFs / 848 MB** |

## Conversation data

| Source | Posts / items | Replies | Date range (UTC) | Authors | Usable for sentiment? | Caveats |
|---|---:|---:|---|---:|---|---|
| **KLSE Screener** | 2 threads | **118,886** | 2018-03-06 → 2026-11-01 | 6,179 | Yes | Public archive starts Mar 2018; no 2016–2018 |
| **i3investor** | 2 threads | **74,143** | 2016-11-02 → 2026-11-01 | 2,563 | Yes | 4,150 replies carry relative timestamps; full crawl still running |
| **YouTube** | 812 videos | **12,628** | 2017-05-17 → 2026-11-01 | 6,587 | Yes, with timestamp caveat | 4,148 comments are relative-time estimates; many are about the video, not the stock |
| **Moomoo Malaysia** | 4,782 feed posts | **8,657** | 2024-11-06 → 2026-11-01 | 2,047 | Replies yes; posts need filtering | See moomoo section below |
| **TikTok** | 84 videos | **1,145** | 2024-11-28 → 2026-11-01 | 889 | Yes, short-form | Short/emoji comments; platform only has recent years |
| **Lowyat.NET** | 31 threads | **847** | 2016-12-13 → 2026-10-28 | 388 | Yes | Low volume after 2022 |
| **Cari** | 19 threads | **486** | 2016-11-04 → 2026-10-26 | 65 | Yes | Activity collapses after 2020 |
| **Reddit** | 77 threads | **422** | 2017-09-04 → 2026-10-28 | 285 | Yes | 59 deleted/empty post bodies |
| **Facebook public** | 74 posts | **133** | 2025-02-13 → 2026-10-21 | 116 | Yes, partial | Public pages only; groups are login-walled |
| **i3 blogs** | 155 posts | **61** | 2024-12-05 → 2025-12-08 | 12 | Yes | Blog commentary, not forum |
| **Instagram** | 41 posts | **43** | 2025-08-15 → 2026-10-30 | 36 | Yes, small | Public posts only |
| **Telegram** | 241 posts | 0 replies | 2024-11-08 → 2026-10-30 | — | Posts only | Channel messages, login-walled |
| **LinkedIn** | 16 posts | 0 replies | 2025-12-31 → 2026-10-29 | — | Posts only | Public page |
| **TradingView** | 2 posts | 0 replies | 2024-12-20 → 2025-04-10 | — | Posts only | Tiny |
| **Bursa filings** | 563 posts | — | 2024-11-25 → 2026-10-26 | — | Reference | Official announcements |
| **Company events** | 89 posts | — | 2024-11-22 → 2026-10-29 | — | Reference | Curated event log |

`replies` has **0 empty bodies**. `posts` has 813 empty bodies (mostly media-only or deleted posts).

## Moomoo detail

| Metric | Value |
|---|---:|
| Replies | **8,657** |
| Reply authors | 2,047 |
| Empty replies | 0 |
| Replies shorter than 5 chars | 424 |
| Replies shorter than 15 chars | 1,510 |
| Duplicate body groups | 137 |
| `[emoji]` markers | 232 |
| `[empty]` markers | 41 |
| `[image]` markers | 24 |
| Feed posts | **4,782** |
| — short stock comments (`feed_type=5`) | 4,044 |
| — long-form posts (`feed_type=3`) | 532 |
| — news wraps / promotions (`feed_type=4`) | 146 |
| — blog-style posts (`feed_type=8`) | 56 |
| — other (`feed_type=9`) | 4 |
| Posts with empty body | 622 |
| Language field | `null` on every record |

Usable: the **8,657 replies** are usable for sentiment, but filter `[emoji]`, `[image]`,
`[empty]` and very short bodies. For "retail opinion", use post types **3, 5 and 8**;
exclude type 4 (news wraps / warrant promotions). Moomoo served the English-locale
rendering, so some Chinese text is translated or untranslated. Coverage is only
Nov 2024 → Nov 2026.

## News

| Publisher | Articles |
|---|---:|
| The Star | 267 |
| The Edge Malaysia | 202 |
| GGRAsia | 56 |
| NST | 54 |
| BusinessToday | 49 |
| The Malaysian Reserve | 48 |
| Free Malaysia Today | 27 |
| KLSE Screener | 26 |
| The Sun | 21 |
| Malay Mail | 18 |
| Other 21 publishers | 96 |
| **Total** | **864** |

Coverage 2016-11-02 → 2026-10-29. 95%+ full text. Usable for event context and
headlines; not used as retail sentiment.

## Market and company data

| Table | Rows | Coverage |
|---|---:|---|
| `prices` | 4,917 | 2016-10-31 → 2026-10-30, daily OHLCV |
| `financials` | 2,962 | FY2024 → 2Q2026, GENTING + GENM |
| `ownership` | 65 | 2025-03-17 → 2026-10-26 |
| `company_actions` | 40 | 2024-11-25 → 2026-10-23 |
| `company_docs` | 2,972 files | 1998 → 2026; 482 PDFs, 848 MB |

The 482 company PDFs and extracted text are in the **`data-v1` release**
(`company_docs.zip`, 650 MB), not in git.

## LLM sentiment

| Metric | Value |
|---|---:|
| Classified replies | **9,015** |
| Months covered | **119** |
| Label: bullish | 2,504 |
| Label: bearish | 2,586 |
| Label: neutral | 3,925 |
| Model | `opencode-go/deepseek-v4.1-flash#low` |
| Rubric | integer level 0–10 → score / 10 |

| Source | Classified | Mean | Bullish | Bearish | Neutral |
|---|---:|---:|---:|---:|---:|
| KLSE Screener | 4,202 | 0.493 | 31.9% | 31.9% | 36.1% |
| i3investor | 2,710 | 0.514 | 34.4% | 25.8% | 39.9% |
| YouTube | 1,123 | 0.466 | 7.2% | 24.0% | 68.7% |
| Moomoo | 564 | 0.482 | 24.6% | 29.8% | 45.6% |
| TikTok | 194 | 0.468 | 2.6% | 21.1% | 76.3% |
| Lowyat | 123 | 0.459 | 1.6% | 30.1% | 68.3% |
| Facebook | 42 | 0.457 | 2.4% | 33.3% | 64.3% |
| Reddit | 25 | 0.440 | 4.0% | 40.0% | 56.0% |
| Instagram | 18 | 0.433 | 0% | 33.3% | 66.7% |
| Cari | 12 | 0.500 | 0% | 0% | 100% |
| i3 blogs | 2 | 0.600 | 50% | 0% | 50% |

This is a **stratified sample**, not all 217,451 replies. The website shows the
sample size for every month.

## Analysis files

| File | Contents |
|---|---|
| `00_audit.md` | source coverage audit |
| `01_volume_monthly.csv` | monthly reply volume |
| `02_prices_monthly.csv` | 2-year monthly closes |
| `02_prices_monthly_10y.csv` | 10-year monthly closes |
| `03_event_reactions.csv` | price reaction around events |
| `04_news_events.csv` | news event index |
| `05_topic_share_monthly.csv` | topic shares |
| `06_keyword_polarity_monthly.csv` | keyword bull/bear counts |
| `07_company_events.csv` | company event log |
| `07_sentiment_monthly.csv` | VADER/lexicon monthly sentiment |
| `08_sentiment_by_source.csv` | lexicon sentiment by source |
| `08_news_examples.md` | news examples |
| `09_sentiment_examples.md` | lexicon sentiment examples |
| `10_audit_findings.md` | data-quality findings |
| `11_story_outline.md` | website narrative outline |
| `12_llm_sentiment_monthly.csv` | LLM monthly sentiment |
| `12b_llm_sentiment_monthly_by_ticker.csv` | LLM by month and ticker |
| `12c_llm_sentiment_by_source.csv` | LLM by source |
| `13_llm_sentiment_report.md` | LLM coverage and quality report |
| `14_llm_sentiment_examples.md` | highest-confidence examples |

## Raw files

- 50 JSONL files, **239 MB** (excluding the 308 MB transient HTML cache, not shipped).
- 385 LLM audit batch files, **3.1 MB**.
- `data/genting.sql.gz`, **25 MB** compressed, restores to 217,451 replies.
- `data/company_docs/`, 848 MB, in the `data-v1` release.
