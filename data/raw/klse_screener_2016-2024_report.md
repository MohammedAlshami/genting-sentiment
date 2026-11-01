# KLSE Screener comments — 2016-2024 backfill

**Source:** `klse_screener` (per-stock comment stream)
**Requested window:** 2016-11-02 00:00:00 MYT → 2024-11-01 23:59:59 MYT
(2016-11-01 16:00:00 UTC → 2024-11-01 15:59:59 UTC, inclusive; 2,922 days)
**Collectors:** `scripts/backfill_klse_10y.py`; `scripts/recover_klse_thread.py`
for the dead-cursor recovery described below.
**Status:** complete for the public archive; validation passes with 0 errors.

The existing 2024-2026 corpus files were **not** modified:

- `data/raw/klse_screener_GENTING.jsonl`
- `data/raw/klse_screener_GENM.jsonl`
- `data/raw/klse_screener_GENTING_2024-2025.jsonl`
- `data/raw/klse_screener_GENM_2024-2025.jsonl`

## Files

| File | Records | Posts | Replies | Top-level comments | Nested replies | Unique authors | Reply range (MYT) |
|---|---:|---:|---:|---:|---:|---:|---|
| `data/raw/klse_screener_GENTING_2016-2024.jsonl` | 56,753 | 1 | 56,752 | 3,980 | 52,772 | 2,627 | 2018-03-07 10:00:01 → 2024-11-01 20:19:23 |
| `data/raw/klse_screener_GENM_2016-2024.jsonl` | 31,588 | 1 | 31,587 | 5,248 | 26,339 | 3,828 | 2018-03-06 15:41:46 → 2024-11-01 20:11:46 |

Each file starts with one synthetic `post` record for the stock (`native_id` =
Bursa code, title `GENTING (3182) comments` / `GENM (4715) comments`). Every
comment is a `reply` record: `depth: 0` for a top-level stock comment,
`depth: 1` for a reply shown under a top-level comment. `post_native_id` is the
stock code; `num_comments` equals the number of reply records in that file.

### Counts by year

| Year | GENTING | GENM |
|---|---:|---:|
| 2018 (from March) | 139 | 917 |
| 2019 | 1,905 | 7,033 |
| 2020 | 8,507 | 9,488 |
| 2021 | 10,558 | 5,269 |
| 2022 | 6,303 | 1,999 |
| 2023 | 10,796 | 2,808 |
| 2024 (to 1 Nov) | 18,544 | 4,073 |
| **Total replies** | **56,752** | **31,587** |

## Collection method

- Listing endpoint:
  `GET https://www.klsescreener.com/v2/comments/all/stock/<code>/<page>`
  with `X-Requested-With: XMLHttpRequest`. It returns
  `{"count": 10, "html": "..."}` and is the site's "Load More" endpoint.
- Ten top-level cards per page, ordered by latest activity. Pagination walked
  forward to the end of the public archive: GENTING page 588 had 7 cards and
  page 589 returned `count: 0`; GENM page 723 had 4 cards and page 724 returned
  `count: 0`.
- A listing card normally shows only its last two replies. Every card containing
  `Previous replies (N)` was opened at `/v2/comment/<id>` to obtain the visible
  reply list, then older replies were walked backwards with
  `GET /v2/comments/view_replies/<comment_id>?last_id=<oldest_id>`, 100 at a
  time, until the batch passed 2016-11-02 or the endpoint had no more replies.
- Detail pages that returned HTTP 401/403/404/410 (70: 21 GENTING, 49 GENM)
  were recovered through the public reply endpoint, starting at `?last_id=0`
  and continuing backwards in the same way. Parent bodies, authors and dates
  came from the listing card.
- Pages 1-205 of each listing were fetched fresh on this run to avoid page-drift
  holes caused by new comments. Older pages were cached after first fetch.
- Detail and reply cache entries from the earlier 2024-2025 run were reused when
  present; new entries were fetched. All HTTP requests were spaced at least
  1.05 s apart, with backoff on 429/5xx.

### Pages and requests

| Stock | Listing pages | Cards seen | Detail pages (fresh / cached) | Reply batches (fresh / cached) | HTTP requests in main pass |
|---|---:|---:|---:|---:|---:|
| GENTING (3182) | 588 | 5,877 | 1,202 / 379 | 64 / 151 | 1,854 |
| GENM (4715) | 723 | 7,224 | 1,261 / 827 | 100 / 58 | 2,018 |

The `requests` column is the fetcher's own counter for the main pass and excludes
cache reads. A separate recovery pass for GENTING comment `386764` made 333 more
reply-batch requests (see below), for 4,205 HTTP requests in total.

## The `386764` recovery (important)

GENTING comment `386764` (the 2019 "日落西山你不陪…" poem) is a very long running
thread. Its page advertises **33,777 earlier replies**, but the cursor returned by
the public reply endpoint (`last_id=7347443`) answers `{"count":0,"html":""}`.
That is a dead cursor at a deletion/migration boundary around 2024-11-21.

A live cursor just above the boundary (`last_id=7300000`) returns the replies
immediately below it. Walking that chain backwards recovered **33,181 in-window
replies** in 333 batches, from reply id `386850` (2019-10-10 17:04:46 MYT) to
2024-11-01 20:01:01 MYT. No batch in the chain returned an empty payload, so
there is no internal hole in the recovered range.

Completeness check: `33,777 − 33,181 = 596`. Those 596 replies fall after this
file's last recovered reply (2024-11-01 20:01) and before the first publicly
served reply of the next segment (2024-11-22 12:19); they are outside this
file's 2024-11-01 cut-off. They are also absent from the existing
`klse_screener_GENTING_2024-2025.jsonl`, whose first `386764` reply is dated
2024-11-22; that adjacent file was not modified, per the task rules. This is the
one known cross-file gap left in the corpus.

## Archive coverage and gaps

- **The public comment archive starts in March 2018.** The earliest comment
  records are 2018-03-06 (GENM) and 2018-03-07 (GENTING). Comment ids are small
  (four digits) and the listing endpoint returns `count: 0` immediately past the
  last page, so there are no 2016-2017 comments to collect from this source.
  The requested window includes 2,922 days; **489-490 days (2016-11-02 →
  2018-03-05/06) have no source records**.
- Effective collected span: **2018-03-06 → 2024-11-01** (2,432-2,433 days).
- Zero-activity days inside that span: **496 of 2,432 for GENTING** (1,936 active
  days) and **496 of 2,433 for GENM** (1,937 active days). These are quiet days,
  not collection stops: the listing pages are continuous through the whole span
  and end only at the archive boundary.
- The longest zero runs are in the sparse first months of the archive:
  - GENTING: 59 days (2018-03-08 → 2018-05-05) and another 59 days
    (2018-06-22 → 2018-08-19).
  - GENM: 34 days (2018-08-31 → 2018-10-03), 28 days (2018-04-18 → 2018-05-15).
  - After 2018-10-31 the longest zero run is 9 days for each stock.
- No empty or deleted bodies were written. Duplicate body texts are distinct
  native comment ids (short repeated reactions); 143 extra GENTING and 79 extra
  GENM bodies were counted, not deduplicated.

## Orphan parents

**Zero orphan parents in both files.** Every `depth: 1` reply's
`parent_native_id` resolves to a top-level comment that is present in the same
file. This includes all 33,181 recovered replies under `386764`. Replies whose
top-level parent was created before 2016-11-02 would be orphans, but the archive
does not contain any pre-2016 parents.

## Validation

```text
python3 -m genting.validate data/raw/klse_screener_GENTING_2016-2024.jsonl
  records=56753 {'post': 1, 'reply': 56752}
  empty_or_deleted=0 duplicate_body_texts=143
  OK: 0 errors

python3 -m genting.validate data/raw/klse_screener_GENM_2016-2024.jsonl
  records=31588 {'post': 1, 'reply': 31587}
  empty_or_deleted=0 duplicate_body_texts=79
  OK: 0 errors
```

The validator prints one warning per historical record because its built-in
`MIN_TS` is 2024-10-01 (it was written for the 2024-2026 corpus). These are
expected out-of-window warnings for a 2016-2024 backfill, not errors. Separate
checks confirmed every reply timestamp is inside
`2016-11-02 00:00:00 MYT .. 2024-11-01 23:59:59 MYT`, every native id is unique,
and every file has exactly one post.

## Timestamps and fields

The site renders `data-datetime="YYYY-MM-DD HH:MM:SS +0800"` in
Asia/Kuala_Lumpur time; values were converted to integer UTC epoch seconds.
The synthetic post is anchored at `2016-11-02 00:00:00 MYT` = `1478016000`.
Scores are the site's "Like" counts; comments with no likes are stored as `0`.
`lang` is left `null` because the corpus mixes English, Chinese, Malay and
Manglish. No SQLite database was written.
