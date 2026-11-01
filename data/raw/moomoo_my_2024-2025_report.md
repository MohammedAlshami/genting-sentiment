# moomoo Malaysia — Genting community backfill report (2024–2025)

Source id `moomoo_my` · backfill collected 2 Nov 2026 (Asia/Kuala_Lumpur) · boards
[GENTING 3182](https://www.moomoo.com/stock/3182-BMS/community) and
[GENM 4715](https://www.moomoo.com/stock/4715-BMS/community).

Files:

- `data/raw/moomoo_my_GENTING_2024-2025.jsonl`
- `data/raw/moomoo_my_GENM_2024-2025.jsonl`

Script: `scripts/backfill_moomoo_my.py` (copy of `scripts/collect_moomoo_my.py`; only
the window, output filename and summary filename were changed).

Window: **2 Nov 2024 00:00 MYT → 1 Nov 2025 23:59:59 MYT**
(`2024-11-01T16:00:00Z` → `2025-11-01T15:59:59Z`). The window is enforced client-side
because the feed API has no date filter. The collector walked the newest-first feed
backwards until every post on a page predated the window.

The two 2025–2026 files (`moomoo_my_GENTING.jsonl`, `moomoo_my_GENM.jsonl`) and SQLite
were **not written by this job**. Output was restricted to the two new JSONL files and
this report.

## Totals

| Ticker | Posts | Replies | Records | Oldest post (MYT) | Newest post (MYT) |
|---|---:|---:|---:|---|---|
| GENTING | 1,194 | 1,987 | 3,181 | 2024-11-05 15:13:06 | 2025-11-01 13:22:59 |
| GENM | 1,599 | 3,104 | 4,703 | 2024-11-06 17:16:14 | 2025-11-01 20:19:56 |
| **total** | **2,793** | **5,091** | **7,884** | | |

UTC spans: GENTING posts `2024-11-05T07:13:06Z` → `2025-11-01T05:22:59Z`; GENM posts
`2024-11-06T09:16:14Z` → `2025-11-01T12:19:56Z`.

Replies on these older posts continue after the post window, because the comment
endpoint returns the whole thread regardless of comment date:

| Ticker | Replies created in window | Replies created after 2025-11-01 | Latest reply (MYT) |
|---|---:|---:|---|
| GENTING | 1,916 | 71 | 2026-10-30 17:05:13 |
| GENM | 3,091 | 13 | 2026-03-11 14:27:16 |

This is deliberate: those later replies belong to in-window threads and would otherwise
be absent from both the backfill and the 2025–2026 files. Only the *posts* are filtered
to the backfill window.

## Requests and pagination

| Ticker | Feed pages walked | of which cached | Live feed requests | Comment-list calls | Detail-page calls | Live requests |
|---|---:|---:|---:|---:|---:|---:|
| GENTING | 141 | 81 | 60 | 73 | 138 | 271 |
| GENM | 108 | 28 | 80 | 140 | 179 | 399 |
| **total** | **249** | **109** | **140** | **213** | **317** | **670** |

`GET /community/nnq/stock-feedlist2?type=500&load_list_type=1&stock_id=<id>&num=10`
returns 20 posts per request (the server caps `num`) newest-first. The opaque
`more_mark` cursor was followed until `has_more=0`, the cursor stopped advancing, or a
page's **newest** post predated the window.

Feed pages 0–80 (GENTING) and 0–27 (GENM) were already in the shared on-disk response
cache from the 2025–2026 walk and were re-read rather than re-requested. All pages
needed for 2024-11 → 2025-11 (GENTING pages 81–140, GENM pages 28–107) were fetched
live. A 1.05 s delay and 5 retries were used; 429/5xx were backed off.

## Monthly post counts (MYT)

| Month | GENTING | GENM |
|---|---:|---:|
| 2024-11 | 68 | 81 |
| 2024-12 | 99 | 100 |
| 2025-01 | 42 | 46 |
| 2025-02 | 119 | 203 |
| 2025-03 | 83 | 365 |
| 2025-04 | 58 | 179 |
| 2025-05 | 50 | 90 |
| 2025-06 | 51 | 120 |
| 2025-07 | 27 | 41 |
| 2025-08 | 90 | 65 |
| 2025-09 | 90 | 42 |
| 2025-10 | 416 | 265 |
| 2025-11 (1 Nov only) | 1 | 2 |
| **total** | **1,194** | **1,599** |

## Declared vs stored comments

`declared` is the sum of each post's `comments_total_count` from the feed payload;
`stored` is the number of reply records written for those posts.

| Ticker | Declared | Stored | Difference | Posts with a mismatch |
|---|---:|---:|---:|---:|
| GENTING | 1,988 | 1,987 | −1 | 1 |
| GENM | 3,104 | 3,104 | 0 | 0 |
| **total** | **5,092** | **5,091** | **−1** | **1** |

The single mismatch:

- GENTING feed `114308376756230` — `"My Malaysian Stock Lab": 🔥 Alchemy Log 🔥`
  (2025-04-09 22:03 MYT), declared `comments_total_count=145`, stored **144**.
  A fresh re-query of `get-feed-comment-list` also returned 144 unique comments over
  three pages (50 + 50 + 44) and then `has_more=0`. One comment is deleted or hidden
  server-side; it cannot be recovered and was not fabricated.

Every other post reconciles exactly, including posts with zero comments.

## Reply depth

Depth is computed by walking `reply_to_comment_id` chains. `depth=0` is top level.

| Depth | GENTING | GENM |
|---:|---:|---:|
| 0 | 1,495 | 2,224 |
| 1 | 321 | 559 |
| 2 | 111 | 168 |
| 3 | 35 | 79 |
| 4 | 19 | 37 |
| 5 | 5 | 18 |
| 6 | 1 | 13 |
| 7 | 0 | 5 |
| 8 | 0 | 1 |
| **max depth** | **6** | **8** |

Thread shape:

| Ticker | Posts with ≥1 reply | Posts with zero replies | Replies whose parent is absent |
|---|---:|---:|---:|
| GENTING | 643 | 551 | 8 (across 6 posts) |
| GENM | 946 | 653 | 12 (across 9 posts) |

Replies with an absent parent are replies to a deleted/hidden comment. They keep the
real `parent_native_id` (so the edge can be restored if the parent is ever returned) and
are assigned `depth=1` because the true depth is unknowable without the parent. They are
not dropped.

## What a record is

- **Post** — one `comment_feed.feed` item. `native_id` = `feed_comm.feed_id`;
  `created_utc` = `feed_comm.timestamp` (epoch seconds); author from
  `author_info.nick_name` / `user_id`; `url` =
  `https://www.moomoo.com/community/feed/<url_slugname>-<feed_id>`;
  `num_comments` = `comments_total_count`; `score` = `like.liked_num`. `raw` retains
  feed id/type, title, summary rich-text, like/browse counts, author and the
  detail-fetch marker.
- **Reply** — one item from `get-feed-comment-list`, which returns the thread flattened.
  `native_id` = `comment_id`; `post_native_id` = the feed id; `parent_native_id` =
  `reply_to_comment_id` (`"0"` becomes `null`); depth is computed from that chain.
  `raw` retains the parent/user, language flags, emoji ids and rich-text items.
- **Full bodies for truncated posts** — the server-rendered page
  `/community/feed/<feed_id>` was fetched when `summary.is_complete=false` **or** the
  summary ended in an ellipsis (the list payload sometimes truncates while still
  flagging the summary complete). `detail.moduleData` was rendered to plain text (text,
  stock mentions and hyperlinks; images omitted). 138 GENTING and 179 GENM posts were
  expanded this way.
- **Deduplication** — `(source, native_id)` within each file; feed ids across pages and
  comment ids across pages are also deduplicated. Re-running reads the same cache and
  rewrites identical JSONL.
- **Markers** — comments with no text keep an explicit marker: `[emoji]` (custom
  emoticon only), `[image]` (image only) or `[empty]` (blank/deleted). Counts:

| Ticker | `[emoji]` | `[image]` | `[empty]` |
|---|---:|---:|---:|
| GENTING | 36 | 3 | 17 |
| GENM | 68 | 7 | 16 |

These are the only non-verbatim bodies and explain the validator's duplicate-body
counts (131 GENTING, 144 GENM).

## Coverage and gaps

### GENTING

- **1,194 posts / 1,987 replies** from 141 feed pages. 2,820 feed items were walked;
  1,591 newer posts (the 2025–2026 corpus) and 35 posts older than the backfill
  window were discarded; 1,194 were kept. The boundary page straddles the window
  start.
- Boundary check: the newest pre-window post on the feed is
  **2024-11-01 16:16:08 MYT**; the oldest in-window post is
  **2024-11-05 15:13:06 MYT**. The intervening feed items are contiguous on the
  boundary page — there were simply no GENTING posts on 2–5 Nov 2024.
- End boundary: newest in-window post **2025-11-01 13:22:59 MYT**; the existing
  2025–2026 GENTING file starts at **2025-11-02 20:10 MYT**. No overlap and no gap.
- Declared / stored: **1,988 / 1,987**. One deleted/hidden comment as detailed above.
- Empty post bodies (title-only, media-only or link posts): **170**.
- Full-detail fetches: **138**.
- Missing-parent replies: **8** across 6 posts; parents deleted/hidden.
- No pagination cap was hit. The feed stopped on page 140, whose newest post is
  **2024-10-29**.

### GENM

- **1,599 posts / 3,104 replies** from 108 feed pages. 2,160 feed items were walked;
  537 newer posts (the 2025–2026 corpus) and 24 posts older than the backfill window
  were discarded; 1,599 were kept. The boundary page straddles the window start.
- Boundary check: the newest pre-window post is **2024-11-01 14:35:53 MYT**; the
  oldest in-window post is **2024-11-06 17:16:14 MYT**. Contiguous feed, no skipped
  page — there were no GENM posts on 2–6 Nov 2024.
- End boundary: newest in-window post **2025-11-01 20:19:56 MYT**; the existing
  2025–2026 GENM file starts at **2025-11-03 09:16 MYT**. No overlap and no gap.
- Declared / stored: **3,104 / 3,104**. Zero mismatches.
- Empty post bodies: **240**.
- Full-detail fetches: **179**.
- Missing-parent replies: **12** across 9 posts; parents deleted/hidden.
- No pagination cap was hit. The feed stopped on page 107, whose newest post is
  **2024-10-28**.

### Cross-board overlap

**104 feed posts** and **225 replies** appear in both files with the same `native_id`.
These are site-wide news wraps and posts dual-tagged with
`$GENTING(3182.BMS)$` / `$GENM(4715.BMS)$`. They are retained in both channel files
because each is a real appearance on that board's feed. For a single global stream,
deduplicate on `(source, native_id)` after loading; `channel` records which board(s)
carried the item.

### Other notes

- **Language.** `lang` is `null` on every record. moomoo served the English-locale
  rendering; some Chinese text remains untranslated. The corpus is what an
  English-reading visitor sees, not a guaranteed original-language transcript.
- **Titles.** `feed_title` is empty for ordinary forum posts; in that case `title` is
  the first body line with a leading `$STOCK(...)$` tag removed (max 160 chars).
  Media-only posts get `[media post] <date>`. Titles are derived, never invented.
- **Body text.** HTML stripped, entities decoded, whitespace normalised; the
  auto-inserted leading `$STOCK(...)$` tag is removed from `body` but kept in `raw`.
  Embedded images/videos are not transcribed.
- **Site-wide content.** News wraps and warrant-issuer promotions tagged to the stock
  are part of the community feed and were kept; `raw.feed_type` distinguishes them.

## Validation

```
python3 -m genting.validate \
  data/raw/moomoo_my_GENTING_2024-2025.jsonl \
  data/raw/moomoo_my_GENM_2024-2025.jsonl
```

Result: **0 errors**.

```
data/raw/moomoo_my_GENTING_2024-2025.jsonl
  records=3181 {'post': 1194, 'reply': 1987} tickers={'GENTING': 1194} | 2024-11-05 → 2026-10-30
  empty_or_deleted=0 duplicate_body_texts=131

data/raw/moomoo_my_GENM_2024-2025.jsonl
  records=4703 {'post': 1599, 'reply': 3104} tickers={'GENM': 1599} | 2024-11-06 → 2026-03-11
  empty_or_deleted=0 duplicate_body_texts=144

OK: 0 errors
```

No duplicate `(source, native_id)` exists within either file. Remaining warnings are
duplicate body texts, almost entirely the non-verbatim `[emoji]`/`[image]`/`[empty]`
markers documented above. The only content-level gaps are the one GENTING comment the
API no longer returns and the deleted/hidden parent comments listed above; all child
replies are retained with their parent ids.
