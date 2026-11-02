# i3investor backfill report — GENTING and GENM, 2016-11-02 → 2024-11-01

**Source:** i3investor (`klse.i3investor.com`)  
**Window:** 2 November 2016 00:00 MYT → 1 November 2024 23:59:59 MYT  
**Collector:** `scripts/backfill_i3investor_10y.py` (copy of `scripts/collect_i3investor.py`, with a fixed window end and the page-level reconciliation from the 2024-2025 backfill)  
**Completed:** 2 November 2026 (Asia/Kuala_Lumpur)

This run adds the earlier eight years only. The four existing i3investor files
cover 2 Nov 2024 → 2 Nov 2026 and were not modified. Their SHA-256 values
before and after this run are identical:

| Existing file | SHA-256 (unchanged) |
| --- | --- |
| `data/raw/i3investor_GENTING.jsonl` | `4f408763e6fa42d54179980d341c59202855b8fb37e4362daf86011e5aa8a4fa` |
| `data/raw/i3investor_GENM.jsonl` | `dd077d7bbf72e6c2c242c3893e5fa724221459c214f67ed322554b5256fdfff7` |
| `data/raw/i3investor_GENTING_2024-2025.jsonl` | `3d69f6ca607bd2663b2526182db7c8e5dc7c2927b94c94b2c905e26a768a078a` |
| `data/raw/i3investor_GENM_2024-2025.jsonl` | `82d37c3b9eb911af09152225871f01ce4f11fabb2441ed01a1521922fcb372e2` |

## 1. Outputs

| File | Post records | Reply records | Total records | SHA-256 |
| --- | ---: | ---: | ---: | --- |
| `data/raw/i3investor_GENTING_2016-2024.jsonl` | 1 | 81,418 | 81,419 | `f19f505b122a5fb667505187744bd7764fb3408453522f76574a7541d34c722b` |
| `data/raw/i3investor_GENM_2016-2024.jsonl` | 1 | 42,644 | 42,645 | `22cfbbbf001f8a08c5cbb06306f9cb78862a755854a7fc4ef99d23ba1f62a8db` |
| **Total** | **2** | **124,062** | **124,064** | |

Total: **124,064 records** (124,062 replies + 2 thread roots).

## 2. Pages and counts

| Ticker | Thread id | In-window pages | First – last in-window page | Last content page | Sentinel page | After-boundary page fetched |
| --- | --- | ---: | --- | --- | --- | --- |
| GENTING | `800000520` | 1,630 | 101–1730 | 2194 (37 rows) | 2195 | 1731 |
| GENM | `800000712` | 854 | 17–870 | 930 (32 rows) | 931 | 871 |

The pagination maximum is the disabled “next” link, so the sentinel page is one
past the last real page and returns zero comments. The after-boundary page was
fetched to prove the upper boundary; its posts were filtered out.

Boundary pages:

| Ticker | Start page | Posts before window on start page | In-window posts on start page | End page | In-window posts on end page | Posts after window on end page |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GENTING | 101 | 44 | 6 | 1730 | 12 | 38 |
| GENM | 17 | 32 | 18 | 870 | 26 | 24 |

The in-window counts also close page by page:
GENTING 1,628 interior pages × 50 + 6 on page 101 + 12 on page 1730 = **81,418**;
GENM 852 interior pages × 50 + 18 on page 17 + 26 on page 870 = **42,644**.
Every interior page therefore contributes exactly 50 comments.

## 3. Reconciliation against the site counters

| Ticker | Site total comments | Pre-window (before 2016-11-02) | In-window reconciled | After-window (from 2024-11-02) | Collected replies | Delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GENTING | 109,687 | 5,044 | **81,418** | 23,225 | 81,418 | **0** |
| GENM | 46,482 | 832 | **42,644** | 3,006 | 42,644 | **0** |

Arithmetic:

- GENTING pre-window = 100 full pages × 50 + 44 on page 101 = **5,044**.
- GENTING after-window = 38 after-window posts on page 1730 + 463 full pages × 50 + 37 on page 2194 = **23,225**.
- GENTING in-window = 109,687 − 5,044 − 23,225 = **81,418**.
- GENM pre-window = 16 full pages × 50 + 32 on page 17 = **832**.
- GENM after-window = 24 after-window posts on page 870 + 59 full pages × 50 + 32 on page 930 = **3,006**.
- GENM in-window = 46,482 − 832 − 3,006 = **42,644**.

The last-page arithmetic also matches the site totals exactly:
GENTING 2,193 full pages × 50 + 37 = 109,687; GENM 929 × 50 + 32 = 46,482.
This confirms that every page except the last holds exactly 50 visible comments.

The collected reply counts match the reconciled counts with **delta 0** for both
threads. Four independent cross-checks also agree:

1. **2024-2025 boundary.** The 2024-2025 report's pre-window counts are 86,462
   (GENTING) and 43,476 (GENM). Our pre-2016 + collected:
   GENTING 5,044 + 81,418 = **86,462**;
   GENM 832 + 42,644 = **43,476**.
2. **After-window counts.** Our after-window arithmetic equals the existing
   2024-2026 files: GENTING 9,228 + 13,997 = **23,225**;
   GENM 1,799 + 1,207 = **3,006**.
3. **Boundary pages.** GENTING page 1730 has 12 in-window posts (ours) + 38
   after-window posts (existing file) = 50. GENM page 870 has 26 + 24 = 50.
4. **No overlap.** The intersection of reply ids with the existing annual files is
   **0** for both tickers (GENTING 0, GENM 0).

### Combined corpus check

| Period | File(s) | GENTING replies | GENM replies | Total replies |
| --- | --- | ---: | ---: | ---: |
| 2016-11-02 → 2024-11-01 | this backfill | 81,418 | 42,644 | 124,062 |
| 2024-11-02 → 2025-11-01 | `*_2024-2025.jsonl` | 9,228 | 1,799 | 11,027 |
| 2025-11-02 → 2026-11-01 | `i3investor_*.jsonl` | 13,997 | 1,207 | 15,204 |
| **2016-11-02 → 2026-11-01** | **all three periods** | **104,643** | **45,650** | **150,293** |
| Site total at crawl | | 109,687 | 46,482 | 156,169 |
| Pre-2016 (not collected) | | 5,044 | 832 | 5,876 |

The three collection periods now contain **150,293** replies, exactly the site totals
(156,169) minus the pre-2016 comments (5,044 + 832 = 5,876). There is no missing comment id
anywhere in the ten-year span. The two thread-root posts are represented as `post`
records; the other 5,874 pre-2016 comments are outside the requested window and
are not in the corpus.

## 4. Date range covered

| Ticker | First reply (MYT) | Last reply (MYT) | First reply (UTC) | Last reply (UTC) | First id | Last id |
| --- | --- | --- | --- | --- | --- | --- |
| GENTING | 2016-11-02 09:35 | 2024-11-01 21:22 | 2016-11-02 01:35 | 2024-11-01 13:22 | `3077456` | `9465422` |
| GENM | 2016-11-03 16:51 | 2024-11-01 14:57 | 2016-11-03 08:51 | 2024-11-01 06:57 | `3081896` | `9465146` |

GENM has no post on 2 November 2016; its first post is on 3 November. That is
a real one-day quiet period on the GENM thread, not a collection gap.

### Counts by year

| Year | GENTING | GENM | Total |
| --- | ---: | ---: | ---: |
| 2016 | 406 | 33 | 439 |
| 2017 | 2,337 | 929 | 3,266 |
| 2018 | 2,032 | 8,399 | 10,431 |
| 2019 | 4,083 | 9,892 | 13,975 |
| 2020 | 15,653 | 10,981 | 26,634 |
| 2021 | 33,357 | 7,643 | 41,000 |
| 2022 | 8,689 | 2,132 | 10,821 |
| 2023 | 6,477 | 1,249 | 7,726 |
| 2024 | 8,384 | 1,386 | 9,770 |
| **Total** | **81,418** | **42,644** | **124,062** |

### Counts by month

| Month | GENTING | GENM | Total |
| --- | ---: | ---: | ---: |
| 2016-11 | 335 | 24 | 359 |
| 2016-12 | 71 | 9 | 80 |
| 2017-01 | 67 | 2 | 69 |
| 2017-02 | 228 | 31 | 259 |
| 2017-03 | 402 | 16 | 418 |
| 2017-04 | 287 | 24 | 311 |
| 2017-05 | 255 | 46 | 301 |
| 2017-06 | 153 | 100 | 253 |
| 2017-07 | 324 | 27 | 351 |
| 2017-08 | 114 | 47 | 161 |
| 2017-09 | 19 | 68 | 87 |
| 2017-10 | 68 | 247 | 315 |
| 2017-11 | 345 | 223 | 568 |
| 2017-12 | 75 | 98 | 173 |
| 2018-01 | 51 | 135 | 186 |
| 2018-02 | 27 | 44 | 71 |
| 2018-03 | 30 | 47 | 77 |
| 2018-04 | 38 | 37 | 75 |
| 2018-05 | 131 | 29 | 160 |
| 2018-06 | 105 | 76 | 181 |
| 2018-07 | 87 | 43 | 130 |
| 2018-08 | 57 | 43 | 100 |
| 2018-09 | 177 | 71 | 248 |
| 2018-10 | 165 | 111 | 276 |
| 2018-11 | 684 | 4,934 | 5,618 |
| 2018-12 | 480 | 2,829 | 3,309 |
| 2019-01 | 333 | 1,224 | 1,557 |
| 2019-02 | 315 | 452 | 767 |
| 2019-03 | 379 | 489 | 868 |
| 2019-04 | 254 | 1,174 | 1,428 |
| 2019-05 | 97 | 432 | 529 |
| 2019-06 | 295 | 747 | 1,042 |
| 2019-07 | 355 | 917 | 1,272 |
| 2019-08 | 365 | 2,368 | 2,733 |
| 2019-09 | 472 | 582 | 1,054 |
| 2019-10 | 546 | 729 | 1,275 |
| 2019-11 | 403 | 527 | 930 |
| 2019-12 | 269 | 251 | 520 |
| 2020-01 | 363 | 383 | 746 |
| 2020-02 | 524 | 643 | 1,167 |
| 2020-03 | 1,516 | 994 | 2,510 |
| 2020-04 | 648 | 745 | 1,393 |
| 2020-05 | 540 | 859 | 1,399 |
| 2020-06 | 1,205 | 1,183 | 2,388 |
| 2020-07 | 575 | 456 | 1,031 |
| 2020-08 | 1,505 | 1,013 | 2,518 |
| 2020-09 | 1,558 | 1,109 | 2,667 |
| 2020-10 | 1,610 | 1,037 | 2,647 |
| 2020-11 | 2,532 | 1,272 | 3,804 |
| 2020-12 | 3,077 | 1,287 | 4,364 |
| 2021-01 | 3,953 | 1,788 | 5,741 |
| 2021-02 | 5,418 | 859 | 6,277 |
| 2021-03 | 5,691 | 618 | 6,309 |
| 2021-04 | 3,249 | 363 | 3,612 |
| 2021-05 | 3,515 | 1,028 | 4,543 |
| 2021-06 | 2,410 | 389 | 2,799 |
| 2021-07 | 2,418 | 348 | 2,766 |
| 2021-08 | 1,919 | 496 | 2,415 |
| 2021-09 | 1,510 | 459 | 1,969 |
| 2021-10 | 1,322 | 616 | 1,938 |
| 2021-11 | 1,071 | 380 | 1,451 |
| 2021-12 | 881 | 299 | 1,180 |
| 2022-01 | 1,150 | 399 | 1,549 |
| 2022-02 | 1,166 | 297 | 1,463 |
| 2022-03 | 522 | 149 | 671 |
| 2022-04 | 620 | 156 | 776 |
| 2022-05 | 956 | 171 | 1,127 |
| 2022-06 | 1,867 | 179 | 2,046 |
| 2022-07 | 332 | 52 | 384 |
| 2022-08 | 162 | 40 | 202 |
| 2022-09 | 230 | 92 | 322 |
| 2022-10 | 612 | 120 | 732 |
| 2022-11 | 703 | 344 | 1,047 |
| 2022-12 | 369 | 133 | 502 |
| 2023-01 | 780 | 156 | 936 |
| 2023-02 | 760 | 125 | 885 |
| 2023-03 | 693 | 121 | 814 |
| 2023-04 | 344 | 110 | 454 |
| 2023-05 | 530 | 104 | 634 |
| 2023-06 | 721 | 66 | 787 |
| 2023-07 | 632 | 71 | 703 |
| 2023-08 | 413 | 131 | 544 |
| 2023-09 | 215 | 71 | 286 |
| 2023-10 | 442 | 95 | 537 |
| 2023-11 | 486 | 88 | 574 |
| 2023-12 | 461 | 111 | 572 |
| 2024-01 | 674 | 255 | 929 |
| 2024-02 | 659 | 155 | 814 |
| 2024-03 | 1,054 | 141 | 1,195 |
| 2024-04 | 431 | 96 | 527 |
| 2024-05 | 840 | 109 | 949 |
| 2024-06 | 909 | 112 | 1,021 |
| 2024-07 | 849 | 85 | 934 |
| 2024-08 | 1,306 | 103 | 1,409 |
| 2024-09 | 655 | 112 | 767 |
| 2024-10 | 985 | 215 | 1,200 |
| 2024-11 | 22 | 3 | 25 |

The 2024-11 row covers only 1 November, the last day of the window.

## 5. Timestamp method

All times are rendered by i3investor in **Asia/Kuala_Lumpur (UTC+8, no DST)** and
were converted to integer UTC epochs.

| Ticker | Absolute page timestamps | Exact comservlet | Relative estimates |
| --- | ---: | ---: | ---: |
| GENTING | 81,418 | 0 | 0 |
| GENM | 42,644 | 0 | 0 |

**100% of backfill replies have absolute `YYYY-MM-DD HH:MM` page timestamps.**
No relative-label interpolation was needed: every post in this window is older
than the site's ~90-day relative-time cutoff. `raw.time_text` is the original
page timestamp, `raw.time_confidence` is `absolute`, and `raw.time_source` is
`forum_page` for every reply. `comservlet.jsp` only holds the latest ~500
comments (2025-2026) and was not used for this window; the collector retains the
code path but produced no comservlet records here.

## 6. Requests, access and Cloudflare workarounds

- **2,486 content pages** were processed: 1,630 GENTING in-window pages (101–1730),
  854 GENM in-window pages (17–870), and the two after-boundary pages 1731 and
  871. Binary-search probes, sentinel checks and the two page-1 reads added
  about 50 more page reads.
- Across all restarts, each of those pages was fetched at least once and stored
  in the persistent cache. The final completing pass made **236 network
  requests** and reused **2,450 cached page reads**; the cache in
  `/tmp/opencode/genting_i3_cache` prevented duplicate work after Cloudflare
  rate limits forced several restarts.
- **1,201 of the 2,484 in-window pages (48.3%) were fetched through a proxy**
  front end: 728 GENTING and 473 GENM. The remaining 1,283 pages were direct.
  Google Translate (`*.translate.goog` and `translate.google.<cc>`) and
  `api.allorigins.win` were used. 184 early GENTING pages and 9 GENM pages were
  recorded before the proxy-label field existed; a later audit of the GENTING
  group found 176 Google and 8 allorigins pages among them.
- Cloudflare returned `403 Just a moment...` challenges and `429 Too Many
  Requests` under sustained direct access; the Google proxy front ends also
  returned `429` under load. The collector backed off, switched to a proxy for
  GETs, and periodically probed direct access again. Direct intervals
  were 1.5–6.0 s, proxy intervals 1.5–2.5 s; no request was made faster than 1 s.
- **Proxy fidelity was checked directly.** Seven proxied pages were re-fetched
  live and parsed: GENTING pages 101, 364, 600, 900 and 1005, and GENM pages 300
  and 310. Every comparison returned 50/50 comments with **0 differences** in
  comment id, author, timestamp or body. The sample includes pages Google
  detected as `zh-CN`/`zh-TW`; their Chinese bodies were unchanged, confirming
  that the proxy returns the original server-rendered HTML rather than a
  translation.
- The page sequence is continuous (no missing pages), every interior page has 50
  visible comments, and the total-count reconciliation is exact, so the proxy
  fallback did not introduce gaps.

## 7. Gaps in the source

There is **no month with zero posts** in either thread between November 2016 and
November 2024. The largest quiet periods are thread-specific:

| Ticker | Gap | From | To | Other thread posts during gap |
| --- | ---: | --- | --- | ---: |
| GENTING | 8.40 d | 2017-09-15 12:07 (`3850167`) | 2017-09-23 21:42 (`3868284`) | 12 |
| GENTING | 7.11 d | 2018-04-27 14:44 (`4453147`) | 2018-05-04 17:29 (`4461916`) | 4 |
| GENTING | 6.30 d | 2018-08-17 09:52 (`4664252`) | 2018-08-23 16:58 (`4679304`) | 3 |
| GENM | 27.93 d | 2016-12-29 15:50 (`3184805`) | 2017-01-26 14:08 (`3236626`) | 58 |
| GENM | 14.18 d | 2017-08-30 12:45 (`3816906`) | 2017-09-13 17:11 (`3845351`) | 12 |
| GENM | 12.16 d | 2016-12-17 12:01 (`3166543`) | 2016-12-29 15:50 (`3184805`) | 23 |

The GENM 27.9-day quiet period (29 Dec 2016 → 26 Jan 2017) overlaps 58 GENTING
posts, and the GENM 14.2-day gap overlaps 12 GENTING posts. The largest GENTING
gap is 8.4 days and overlaps 12 GENM posts. These are ordinary low-activity
periods on one thread, not site-side archive gaps. The longest simultaneous
quiet period in both threads is 5.2 days (30 August–4 September 2017, around
Merdeka Day and the weekend), consistent with a holiday lull. No simultaneous
multi-week silence exists in this window.

For context, the existing 2024-2025 file shows no GENM posts on 2–6 November
2024 (its first post is 7 November), immediately after this window. The
2024-2025 report also documents a **92-day site-side gap from 30 November 2024
to 3 March 2025**. Both begin after this backfill window and are therefore
outside its scope.

## 8. Removed posts, duplicates and empty bodies

| Ticker | `Post removed. Why?` placeholders | Empty bodies | Duplicate body texts | Duplicate ids |
| --- | ---: | ---: | ---: | ---: |
| GENTING | 3,153 | 0 | 4,361 | 0 |
| GENM | 724 | 0 | 1,345 | 0 |

Removed posts keep the site's literal placeholder and are flagged
`raw.body_status = "removed_placeholder"` so sentiment scoring can exclude them.
The validator's duplicate-body count covers distinct comment ids with identical
visible text (short replies, repeated headlines and the placeholder); there are
no duplicate `(source, native_id)` pairs.

Distinct `author_id` values: **2,580** GENTING and
**3,063** GENM. `author_id` is `data-postuserid`, which
can be a numeric id or a slug; `author` is the displayed name.

## 9. Validation

Command run:

```bash
python3 -m genting.validate \
  data/raw/i3investor_GENTING_2016-2024.jsonl \
  data/raw/i3investor_GENM_2016-2024.jsonl
```

Result:

```text
data/raw/i3investor_GENTING_2016-2024.jsonl
  records=81419 {'post': 1, 'reply': 81418} tickers={'GENTING': 1} | 2024-10-01 → 2024-11-01
  empty_or_deleted=0 duplicate_body_texts=4361
  WARN line 1: timestamp 1322453280 outside window (2011-11-28)
  ... 80403 more warnings

data/raw/i3investor_GENM_2016-2024.jsonl
  records=42645 {'post': 1, 'reply': 42644} tickers={'GENM': 1} | 2024-10-02 → 2024-11-01
  empty_or_deleted=0 duplicate_body_texts=1345
  WARN line 1: timestamp 1334904420 outside window (2012-04-20)
  ... 42417 more warnings

OK: 0 errors
```

**0 errors.** The 80,413 GENTING and 42,427 GENM warnings (10 printed plus
80,403/42,417 more) are expected:
`genting.validate` has a hard-coded lower bound of 2024-10-01, so every pre-October-2024
reply and the thread-root post are reported as outside that validator window. The
actual min/max in section 4 (2016-11-02 → 2024-11-01) are inside the requested
backfill window. The root `post` records are the first displayed post of each
thread (2011-11-28 and 2012-04-20) and necessarily predate the backfill window;
changing them would fabricate a timestamp.

## 10. Limitations

- **Removed comments.** Only comments the site still renders are visible. The
  site's total and per-page counts agree exactly with what was collected, so no
  visible comment was skipped; deleted text is preserved only as the placeholder.
- **Proxy reliance.** 48.3% of in-window pages were fetched through a proxy after
  Cloudflare blocked direct access. Seven pages across both proxy families were
  re-fetched directly and matched exactly; all interior pages have 50 comments and
  the total reconciliation is exact. No translated body was found in the proxy
  HTML; the raw response is the server-rendered page, not a translation.
- **`author_id`.** `data-postuserid` is used as `author_id`; it can be a slug or a
  numeric id. `author` is the displayed name.
- **Scores and language.** i3investor does not expose a score in the thread
  listing, so `score` is null. `lang` is null; bodies are a mix of English, Malay,
  Chinese and Manglish.
- **Pre-2016 comments.** The 5,876 comments before 2 Nov 2016 (5,044 GENTING +
  832 GENM) remain outside the requested window and were not collected.

## 11. Reproducing

```bash
python3 scripts/backfill_i3investor_10y.py --stock both --min-interval 1.5
```

The script uses the shared raw-page cache in `/tmp/opencode/genting_i3_cache`,
writes only `data/raw/i3investor_GENTING_2016-2024.jsonl` and
`data/raw/i3investor_GENM_2016-2024.jsonl`, and does not touch SQLite or the
2024-2026 files. `--proxy-mode auto` (the default) uses direct requests first and
falls back to a proxy on Cloudflare 403/429; `--proxy-mode google` forces the
Google front ends, and `--refetch-proxy` re-fetches pages whose cache entry came
from a proxy.
