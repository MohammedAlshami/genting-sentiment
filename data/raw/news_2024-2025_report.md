# Genting news collection — 2 Nov 2024 to 1 Nov 2025

Window: **2 Nov 2024 00:00 MYT → 1 Nov 2025 23:59:59 MYT** (`1730476800`–`1762012799` epoch UTC).

## Summary

- Articles written: **250**
- Candidate article pages fetched: **508**
- Malaysian-publisher articles: **150** (60%)
- Tickers (an article can carry both): GENM 199, GENTING 166
- Date range: **2024-11-05 06:00 UTC → 2025-10-31 07:55 UTC**
- Paywalled / stubbed records: **11**
- Body length: min 269, median 2450, max 19985 chars
- Authors present: 94/250

## Requests made

- article_fetch: 641
- article_fetch_amp: 60
- google_news_rss: 1150
- resolve_batchexecute: 501
- resolve_page: 501
- wp_api: 11

## Articles by publisher

| Publisher | Articles |
|---|---:|
| BusinessToday Malaysia | 44 |
| The Edge Malaysia | 41 |
| GGRAsia | 36 |
| The Star | 19 |
| The Malaysian Reserve | 19 |
| Asia Gaming Brief | 18 |
| New Straits Times | 11 |
| Free Malaysia Today | 8 |
| The Business Times | 8 |
| CDC Gaming Reports | 4 |
| Yahoo Finance | 3 |
| World Casino Directory | 3 |
| RAM Ratings | 2 |
| iGaming Expert | 2 |
| Malay Mail | 2 |
| iGaming Business | 2 |
| The Sun Malaysia | 2 |
| News 3 Las Vegas | 2 |
| The Nevada Independent | 2 |
| Moomoo | 1 |
| Focus Malaysia | 1 |
| The Straits Times | 1 |
| VegasSlotsOnline | 1 |
| Focus Gaming News | 1 |
| Spectrum News 1 | 1 |
| Yogonet | 1 |
| London Post | 1 |
| GGB Magazine | 1 |
| Gambling News | 1 |
| Blooloop | 1 |
| Fifth Person | 1 |
| The Real Deal | 1 |
| City AM | 1 |
| EdgeProp Malaysia | 1 |
| World of Buzz | 1 |
| Gaming Intelligence | 1 |
| Las Vegas Review-Journal | 1 |
| Fortune | 1 |
| Upstream | 1 |
| Travel Weekly | 1 |
| The Tribune (Bahamas) | 1 |

## Articles by month

| Month (UTC) | Articles |
|---|---:|
| 2024-11 | 15 |
| 2024-12 | 15 |
| 2025-01 | 10 |
| 2025-02 | 23 |
| 2025-03 | 28 |
| 2025-04 | 5 |
| 2025-05 | 23 |
| 2025-06 | 15 |
| 2025-07 | 16 |
| 2025-08 | 29 |
| 2025-09 | 18 |
| 2025-10 | 53 |

## Candidate filtering

| Reason dropped | Candidates |
|---|---:|
| not about the company | 284 |
| place_event | 168 |
| unmapped_publisher | 84 |
| lifestyle/place | 56 |
| subsidiary_entity | 34 |
| market roundup | 32 |
| place/policy story | 31 |
| genting singapore only | 29 |
| crime/incident brief | 24 |
| passing mention | 21 |
| list headline | 14 |
| event/entertainment | 11 |
| no genting mention | 8 |
| unlisted genting entity | 8 |
| roundup_y1 | 7 |
| bursa announcement | 6 |
| travel content | 6 |
| estate/family dispute | 4 |
| boilerplate_body | 1 |

## Method

- Discovery: Google News RSS (`hl=en-MY&gl=MY&ceid=MY:en`) with 92 queries, walked month by month and split further whenever a slice hit the ~90-item RSS cap.
- Google News redirect links were resolved to canonical publisher URLs through the batchexecute decoder; dedupe by canonical URL, then by title similarity ≥0.90.
- Full text: trafilatura first, readability and BeautifulSoup fallbacks; The Star `?s=app` and NST AMP variants where the canonical page is JS-heavy.
- Five to seven publisher WordPress REST APIs were queried directly for full text.
- Politeness: ≥1.15 s between requests to the same publisher, exponential backoff on 429/5xx, browser-impersonating curl_cffi session.

## Gaps and caveats

- Thin months (<8 articles): 2025-04 (5).
- Google News RSS only indexes what it has crawled; very old items and articles removed from publisher sitemaps may be missing. The count is therefore a floor, not a census.
- Bernama is a known gap: its article pages serve only a subscription notice (`Please email to digitalsales@bernama.com...`), so no usable public body could be extracted. One relevant Bernama 3Q24 result item was discarded for this reason.
- The Star premium articles sometimes serve only the first 2-3 paragraphs to non-subscribers. Those records are kept with the public text and `raw.paywalled=true`; 11 records are flagged in total.
- April 2025 is genuinely thin (5 articles): targeted weekly re-queries of the top ten search terms returned no additional corporate stories for the month.
- No Genting Berhad / Genting Malaysia article was published on 2-4 Nov 2024 or 1 Nov 2025 in the recovered index; the first record is 5 Nov 2024 and the last is 31 Oct 2025.
- The Edge Malaysia weekly editions are dated by their online publication timestamp (`article:published_time`), which can be a few days after the print cover date.
- Genting Singapore, Genting Plantations and other separately listed Genting entities are excluded; pure place/lifestyle/concert copy set in Genting Highlands is also excluded as not being about the two issuers.
- The collection is English-language, matching the year-two corpus. Malay- and Chinese-language coverage from Berita Harian, Sinar Harian, Oriental Daily and similar outlets is not systematically covered.
- A small number of Edge quarterly-results articles that Google News did not surface were recovered through supplementary web search and fetched directly; all bodies still come from the publisher page, not from snippets.
- This file ends at 1 Nov 2025 23:59:59 MYT; the year-two file starts at 2 Nov 2025 00:00 MYT, so there is no overlap.
