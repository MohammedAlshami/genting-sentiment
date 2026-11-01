# KLSE Screener comments — 2024-2025 backfill

**Source:** `klse_screener` (per-stock comment stream)
**Window:** 2024-11-02 00:00 MYT → 2025-11-01 23:59:59 MYT
(2024-11-01 16:00 UTC → 2025-11-01 15:59:59 UTC, inclusive)
**Collector:** `scripts/backfill_klse.py` (copy of `scripts/collect_klse.py`)
**Status:** complete; validation passes with 0 errors.

The existing 2025-2026 files were **not** modified:

- `data/raw/klse_screener_GENTING.jsonl`
- `data/raw/klse_screener_GENM.jsonl`

## Files

| File | Records | Posts | Replies | Top-level comments | Replies to comments | Unique authors | Reply range (MYT) |
|---|---:|---:|---:|---:|---:|---:|---|
| `data/raw/klse_screener_GENTING_2024-2025.jsonl` | 12,759 | 1 | 12,758 | 988 | 11,770 | 636 | 2024-11-02 09:41:05 → 2025-11-01 21:52:59 |
| `data/raw/klse_screener_GENM_2024-2025.jsonl` | 6,380 | 1 | 6,379 | 1,230 | 5,149 | 957 | 2024-11-02 08:35:11 → 2025-11-01 17:46:21 |

Each file starts with one synthetic `post` record for the stock (`native_id` =
Bursa code, title `GENTING (3182) comments` / `GENM (4715) comments`). Every
comment is a `reply` record: `depth: 0` for a top-level stock comment,
`depth: 1` for a comment displayed as a reply. `post_native_id` is the stock
code.

## Collection method

- Listing endpoint:
  `GET https://www.klsescreener.com/v2/comments/all/stock/<code>/<page>`
  with `X-Requested-With: XMLHttpRequest`. It returns JSON
  `{"count": 10, "html": "..."}` and is the site's "Load More" endpoint.
- Ten top-level cards per page, ordered by latest activity. Pagination walked
  forward until two consecutive pages had a newest timestamp before
  2024-11-02 (two look-back pages guard against ordering drift).
- A listing card normally shows only its last two replies. Any card containing
  `Previous replies (N)` was opened at `/v2/comment/<id>` to get the full
  visible reply list.
- Detail pages render at most the latest 100 replies. Earlier replies were
  walked backwards with
  `GET /v2/comments/view_replies/<comment_id>?last_id=<oldest_id>`, 100 at a
  time, until a batch's newest timestamp was before the window start or the
  endpoint returned `count: 0`.
- Empty 200 responses from `view_replies` are treated as end-of-list after one
  retry. A non-empty non-JSON response is retried with backoff; no 429/5xx was
  seen in either run.

### Pages and requests

| Stock | Listing pages | Cards seen | Detail pages | Reply batches | HTTP requests (successful pass) |
|---|---:|---:|---:|---:|---:|
| GENTING (3182) | 194 | 1,940 | 379 | 151 | 316 |
| GENM (4715) | 201 | 2,010 | 559 | 31 | not printed by the run |

The GENTING figure is the `requests` counter of the successful pass; it reuses
same-day cache entries from the 2025-2026 run, so it is lower than the total
number of pages above. The GENM pass wrote its file (validated separately
afterwards), then the process crashed while walking a GENTING reply thread
before printing its summary; the page/detail/reply counts above were recovered
from the run log and the on-disk cache.

## Orphan parents

A reply whose top-level parent was created before 2024-11-02 is kept (the reply
itself is in the window) but its parent is outside the file, so
`parent_native_id` points outside the file.

| File | Orphan replies | Share | Main parents |
|---|---:|---:|---|
| GENTING | 8,801 | 69.0% | `386764` 8,764; `2949791` 14; `6746125` 9; `7258019` 5; `7296451` 3 |
| GENM | 205 | 3.2% | `6287549` 94; `7245083` 76; `6327233` 15; `6960789` 10; `6816487` 4 |

`386764` is a GENTING top-level comment created in 2019 that became the main
running discussion. Its first direct reply in this pull is dated 2024-11-22;
there are no replies between 2024-11-02 and 2024-11-21. The collector recovered
8,764 in-window replies for it; the existing 2025-2026 file has 3,336 more.
Those two counts sum to exactly 12,100, the number of direct replies returned
from 2024-11-22 through 2026-11-01, which is a useful completeness check.

## Gaps

Zero-activity days are ordinary quiet days, not collection gaps: the collector
did not stop on them and the surrounding pages are continuous.

### GENTING — 355 of 365 days active (10 zero days)

`2024-11-16`, `2024-12-21`, `2025-04-22`, `2025-04-27`, `2025-06-27`,
`2025-07-06`, `2025-07-13`, `2025-07-26`, `2025-07-27`, `2025-07-31`.

Longest gap: 2 days (2025-07-26 → 2025-07-27).

### GENM — 328 of 365 days active (37 zero days)

`2024-11-03`, `2024-11-24`, `2025-01-26`, `2025-01-30`, `2025-02-02`,
`2025-02-07`, `2025-02-08`, `2025-02-09`, `2025-04-20`, `2025-05-01`,
`2025-05-17`, `2025-05-18`, `2025-05-25`, `2025-05-31`, `2025-06-07`,
`2025-06-14`, `2025-06-19`, `2025-06-21`, `2025-06-22`, `2025-06-26`,
`2025-06-27`, `2025-07-05`, `2025-07-06`, `2025-07-12`, `2025-07-16`,
`2025-07-19`, `2025-07-20`, `2025-07-27`, `2025-08-02`, `2025-08-03`,
`2025-08-23`, `2025-08-24`, `2025-09-16`, `2025-09-21`, `2025-09-27`,
`2025-09-28`, `2025-10-05`.

Longest gap: 3 days (2025-02-07 → 2025-02-09). Seven other gaps are 2 days;
the rest are single quiet days.

Monthly reply counts:

| Month | GENTING | GENM |
|---|---:|---:|
| 2024-11 | 820 | 644 |
| 2024-12 | 1,933 | 595 |
| 2025-01 | 576 | 319 |
| 2025-02 | 1,079 | 862 |
| 2025-03 | 1,174 | 1,134 |
| 2025-04 | 771 | 504 |
| 2025-05 | 953 | 251 |
| 2025-06 | 918 | 274 |
| 2025-07 | 281 | 189 |
| 2025-08 | 1,830 | 182 |
| 2025-09 | 803 | 174 |
| 2025-10 | 1,611 | 1,247 |
| 2025-11 (1 day) | 9 | 4 |

## Timestamps

The site renders `data-datetime="YYYY-MM-DD HH:MM:SS +0800"`. All values are
Asia/Kuala_Lumpur time and were converted to integer UTC epoch seconds. The
synthetic post is anchored at `2024-11-02 00:00 MYT` = `1730476800`
(2024-11-01 16:00 UTC). Actual comment timestamps are unchanged.

## Known gaps / caveats

- **Login-gated detail pages.** Two GENTING comments (`8014569`, `8050163`) and
  eleven GENM comments (`7531185`, `7543895`, `7544847`, `7546289`, `7585759`,
  `7871645`, `7877543`, `7904909`, `7917873`, `7965221`, `7966617`) returned
  the login wall instead of a detail page. Their replies were recovered through
  the public `view_replies` endpoint. All of these threads had
  `replies_left_count: 0` after the first batch, i.e. no hidden older replies.
- **`replies_left_count` is not a reliable remaining count.** For `386764` it
  still reported 33,777 after the oldest direct reply (2024-11-22), but the
  endpoint then returned `count: 0`. The empty response is the authoritative
  end-of-list signal; the recovered 8,764 + existing 3,336 = 12,100
  reconciliation above confirms nothing was lost.
- **Flat reply model.** The detail page exposes a flat list of replies to the
  top-level card. `parent_native_id` is therefore the top-level comment id and
  `depth` is 1 for every reply; reply-to-reply parent ids are not exposed by the
  site, so they are not invented. This matches the existing 2025-2026 files.
- **Duplicate body texts** (18 repeated texts / 20 extra GENTING records; 6
  repeated texts / 6 extra GENM records) are short repeated reactions, quoted
  news paragraphs and near-identical one-liners. They have distinct
  `native_id`s and were not deduplicated.
- **No empty or deleted bodies**, no null authors and no null like counts in
  either file. Comments with zero likes are stored as `0`.
- **Language** is left `null` for mixed English/Chinese/Malay/Manglish text
  rather than guessed.
- The two files do not overlap at the reply level: this backfill ends at
  2025-11-01 21:52:59 MYT; the existing files start at 2025-11-02 00:00 MYT.
  Each yearly file necessarily carries its own synthetic stock `post` with the
  stable Bursa code (`3182` / `4715`); the store upserts those by
  `(source, native_id)`.
- `num_comments` on each synthetic post is the number of in-window reply
  records in that file, matching the existing convention.

## Validation

```bash
python3 -m genting.validate \
  data/raw/klse_screener_GENTING_2024-2025.jsonl \
  data/raw/klse_screener_GENM_2024-2025.jsonl
# OK: 0 errors
```
