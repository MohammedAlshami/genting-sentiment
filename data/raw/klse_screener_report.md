# KLSE Screener comments — collection report

**Source:** `klse_screener` (per-stock comment stream)
**Window:** 2025-11-02 00:00 MYT → 2026-11-02 23:59 MYT
(2025-11-01 16:00 UTC → 2026-11-02 15:59 UTC, inclusive)
**Collector:** `scripts/collect_klse.py`

## Files

| File | Records | Posts | Replies | Top-level comments | Replies to comments | Unique authors | Reply date range (MYT) |
|---|---:|---:|---:|---:|---:|---:|---|
| `data/raw/klse_screener_GENTING.jsonl` | 8,275 | 1 | 8,274 | 909 | 7,365 | 555 | 2025-11-02 07:10 → 2026-11-01 23:03 |
| `data/raw/klse_screener_GENM.jsonl` | 3,137 | 1 | 3,136 | 746 | 2,390 | 579 | 2025-11-03 09:22 → 2026-10-30 15:26 |

Each file starts with one synthetic `post` record for the stock
(`native_id` = Bursa code, title `GENTING (3182) comments` / `GENM (4715) comments`).
Every comment is a `reply` record: `depth: 0` for a top-level stock comment,
`depth: 1` for a reply to a comment. `post_native_id` is the stock code.

## Collection method

- Endpoint: `GET https://www.klsescreener.com/v2/comments/all/stock/<code>/<page>`
  with `X-Requested-With: XMLHttpRequest`. It returns JSON
  `{"count": 10, "html": "..."}` and is the "Load More" endpoint used by the site.
- Ten top-level cards per page. Pages are ordered by latest activity
  (newest reply, not newest comment), which was verified to be monotonic
  across every page fetched for both stocks.
- **GENTING (3182):** 94 listing pages, 940 top-level cards, 173 comment-detail
  pages, 56 reply-pagination calls.
- **GENM (4715):** 78 listing pages, 780 top-level cards, 224 comment-detail
  pages, 6 reply-pagination calls.
- A listing card shows only the last two replies. Cards with earlier replies carry
  `Previous replies (N)`; their detail page `/v2/comment/<id>` was fetched.
- Detail pages render at most the latest **100** replies. Earlier replies were
  fetched backwards with
  `GET /v2/comments/view_replies/<comment_id>?last_id=<oldest_id>`, 100 at a time,
  until a batch's newest timestamp fell before the window start or the reply
  counter reached zero. This was essential for GENTING: comment `386764` alone
  has 3,336 in-window replies.
- Pagination stopped after the first page whose newest timestamp was before
  the window start, plus two extra look-back pages as a guard.

## Timestamps

The site renders `data-datetime="YYYY-MM-DD HH:MM:SS +0800"`. All values are
Asia/Kuala_Lumpur time and were converted to integer UTC epoch seconds.
The synthetic post is anchored at `2025-11-02 00:00 MYT` = `1762012800`
(2025-11-01 16:00 UTC); actual reply timestamps are unchanged.

## Gaps and caveats

- **Login-gated detail pages (6).** These returned HTTP 401 with
  "You need to login to view this page": GENM `7904909`, `7917873`, `7965221`,
  `7966617`; GENTING `8014569`, `8050163`. Their replies were recovered through
  the public reply endpoint (`view_replies/<id>?last_id=0`). Parent bodies,
  authors and dates came from the listing card. One parent had 57 earlier replies,
  all recovered.
- **Parents outside the file (3,500 GENTING / 34 GENM).** Replies can belong to a
  top-level comment created before 2025-11-02 that was bumped by in-window
  replies. The reply is kept (it is in the window), but the parent comment is
  not, so `parent_native_id` points outside the file. For GENTING, 3,336 of these
  are the long-running comment `386764`.
- **Duplicate body texts (19 GENTING / 4 GENM).** Short repeated reactions such
  as "Hahahahaha", "+1..........." and quoted statutory text. They are distinct
  native comment ids and were not deduplicated.
- **No empty or deleted bodies** in either file.
- A handful of comments are written in Chinese, Malay, Manglish or mixed
  English/Chinese; `lang` is left `null` rather than guessed.
- `num_comments` on the synthetic post equals the number of in-window reply
  records in that file.
- Scores are the site's "Like" counts; comments with no likes are stored as `0`.
