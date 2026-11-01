# Genting forum collection — source summary

**Collection window:** 2025-11-02 00:00 MYT → 2026-11-02 23:59 MYT (inclusive)
**Contract:** `docs/collector_contract.md`
**Collectors:** `scripts/collect_klse.py`, `scripts/collect_lowyat.py`

## Summary

| Source | Channel / file | Posts | Replies | Total records | Reply date range (MYT) | Status |
|---|---|---:|---:|---:|---|---|
| KLSE Screener | `klse_screener_GENTING.jsonl` | 1 | 8,274 | 8,275 | 2025-11-02 07:10 → 2026-11-01 23:03 | complete |
| KLSE Screener | `klse_screener_GENM.jsonl` | 1 | 3,136 | 3,137 | 2025-11-03 09:22 → 2026-10-30 15:26 | complete |
| Lowyat.NET | `lowyat_GENTING.jsonl` | 1 | 13 | 14 | 2026-05-22 07:13 → 2026-10-28 04:32 | 1 thread |
| Lowyat.NET | `lowyat_GENM.jsonl` | 3 | 34 | 37 | 2025-11-04 11:40 → 2026-10-29 03:40 | 3 threads |
| MalaysiaStock.Biz | — | 0 | 0 | 0 | — | no in-window content |
| **Total** | | **6** | **11,457** | **11,463** | 2025-11-02 → 2026-11-01 | |

Counts are records written to JSONL. Every `post` is a thread/stock container;
every comment or forum post in the window is a `reply`.

## KLSE Screener (primary)

- **GENTING (3182):** 94 listing pages, 940 top-level comment cards, 173
  comment-detail pages and 56 reply-pagination calls. 8,274 replies, 909
  top-level comments and 7,365 replies-to-comments, from 555 authors.
- **GENM (4715):** 78 listing pages, 780 top-level cards, 224 detail pages and
  6 reply-pagination calls. 3,136 replies, 746 top-level comments and 2,390
  replies-to-comments, from 579 authors.
- Pagination used the site's "Load More" JSON endpoint
  `/v2/comments/all/stock/<code>/<page>` (10 top-level comments per page).
  Pages are ordered by latest activity; the ordering was verified monotonic for
  every page of both stocks.
- Listing cards show only the last two replies, so detail pages were fetched for
  cards with `Previous replies (N)`. Detail pages render at most the latest 100
  replies; older replies were fetched backwards with
  `/v2/comments/view_replies/<id>?last_id=<oldest_id>` until the batch left the
  window. This recovered thousands of replies under GENTING comment `386764`
  (3,336 in-window replies) and 1,015 under `8110033`.
- Timestamps: `data-datetime="YYYY-MM-DD HH:MM:SS +0800"` converted to UTC epoch.
  The synthetic stock post is anchored at `2025-11-02 00:00 MYT`
  (`1762012800` = `2025-11-01 16:00 UTC`).

## Lowyat.NET

- Forum index and topic pages were publicly readable with no login; a guest
  session cookie was used for the search form. Search was done with title-only
  queries for `genting`, `genm`, `3182`, `4715` in Stock Exchange,
  Finance/Business, Kopitiam and Serious Kopitiam.
- Four threads had in-window posts:
  - `5581190` — "Genting is asking shareholders for RM1.25b." (Stock Exchange),
    2 posts, 2026-10-23 → 2026-10-26.
  - `662423` — "Genting Malaysia" (Stock Exchange), 10 posts,
    2025-11-04 → 2026-04-15.
  - `5515321` — "Genting Malaysia have 456 tables and 3012 slots !" (Kopitiam),
    22 posts, 2025-11-04 → 2026-10-29.
  - `5536525` — "✨🌏 Genting Group 2026: Global Challenges" (Kopitiam),
    13 posts, 2026-05-22 → 2026-10-28.
- `5515321` is a Kopitiam operations/hotel thread with mixed relevance; it is
  included because the task asked for Kopitiam Genting threads. It contains some
  clear GENM investor posts ("buy the dip", "52 week lowest") and a lot of
  Genting Highlands hotel/casino chatter.
- `5536525` is a group-level thread (Genting Berhad, GENM, Genting Singapore, UK
  operations) and is tagged GENTING.
- Lowyat timestamps are shown in Malaysia time (`Mon DD YYYY, HH:MM AM/PM`) and
  were cross-checked against the page JSON-LD `datePublished` before conversion
  to UTC.

## MalaysiaStock.Biz

- No JSONL was written. 43 pages of the Latest Discussion listing (1,190 unique
  topics) were scanned; the only Genting stock topics are:
  - `119` GENTING (3182), 3 pages / 46 posts, last post 2024-07-07.
  - `166` GENM (4715), 2 pages / 22 posts, last post 2024-06-01.
  - `23836` GENM technical analysis, 1 page / 1 post, last post 2020-06-21.
- All pages of these topics were checked; none has a post on or after
  2025-11-02. See `data/raw/malaysiastock_report.md`.

## What was unavailable

- **KLSE Screener:** six comment-detail pages returned HTTP 401 ("You need to
  login to view this page") — GENM `7904909`, `7917873`, `7965221`, `7966617`;
  GENTING `8014569`, `8050163`. Their replies were recovered from the public
  reply endpoint, and their parent bodies from the listing cards. No known
  in-window comment is missing.
- **Lowyat:** there is no dedicated GENTING (3182) thread active in the window.
  Several old GENTING threads exist but stopped before 2025-11-02. The only
  GENTING-tagged content is the group-level thread `5536525`. Title searches in
  the four relevant forums were used (results sorted by last post date), and
  travel/casino and general market threads were deliberately excluded.
- **MalaysiaStock.Biz:** no in-window content, so no file.
- **Not attempted / out of scope:** general Lowyat market threads (e.g. "STOCK
  MARKET DISCUSSION V150") where Genting is mentioned only incidentally; they
  are not Genting threads.

## Data handling

- Deduplication key: `(source, native_id)`. Comment/post ids are the source's
  own numeric ids; the synthetic stock/thread records use the stock code or
  thread id.
- Missing values are `null`. No author names, timestamps or text were invented.
- Bodies are HTML-stripped, entity-decoded and whitespace-normalised. Lowyat
  edit notices were moved to `raw.edited`; image-only posts use the marker
  `[image]` with URLs in `raw.media`.
- Request pacing was ≥1.05 s (KLSE) / ≥1.1 s (Lowyat), with backoff on 429/5xx.
- Re-running both collectors produced byte-identical JSONL files (md5-checked),
  so collection is idempotent.

## Validation

```bash
python3 -m genting.validate \
  data/raw/klse_screener_GENTING.jsonl \
  data/raw/klse_screener_GENM.jsonl \
  data/raw/lowyat_GENTING.jsonl \
  data/raw/lowyat_GENM.jsonl
```

Result: **OK: 0 errors** for all four files.

Warnings are limited to duplicate body text (19 GENTING, 4 GENM, 1 Lowyat pair)
from repeated short reactions and two `[image]`-only posts. No empty/deleted
bodies were written.
