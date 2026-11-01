# moomoo Malaysia — Genting community collection report

Source id `moomoo_my` · collected 2 Nov 2026 (Asia/Kuala_Lumpur) · boards [GENTING 3182](https://www.moomoo.com/stock/3182-BMS/community) and [GENM 4715](https://www.moomoo.com/stock/4715-BMS/community).

Files: `data/raw/moomoo_my_GENTING.jsonl`, `data/raw/moomoo_my_GENM.jsonl`.

Window: **2 Nov 2025 00:00 MYT → 2 Nov 2026** inclusive (`2025-11-01T16:00:00Z` → `2026-11-02T16:00:00Z`). The window is enforced client-side because the feed API has no date filter. Collection snapshot: **2 Nov 2026, ~00:40 MYT**; later posts did not exist yet.

## Totals

| Ticker | Posts | Replies | Records | Oldest post | Newest post |
|---|---:|---:|---:|---|---|
| GENTING | 1591 | 2797 | 4388 | 2025-11-02 12:10 UTC / 2025-11-02 20:10 MYT | 2026-10-30 14:51 UTC / 2026-10-30 22:51 MYT |
| GENM | 537 | 1230 | 1767 | 2025-11-03 01:16 UTC / 2025-11-03 09:16 MYT | 2026-11-01 14:08 UTC / 2026-11-01 22:08 MYT |
| **total** | **2128** | **4027** | **6155** | | |

## Requests and pagination

| Ticker | Feed pages | Comment-list calls | Detail-page calls |
|---|---:|---:|---:|
| GENTING | 81 | 116 | 134 |
| GENM | 28 | 57 | 74 |
| **total** | **109** | **173** | **208** |

`GET /community/nnq/stock-feedlist2?type=500&load_list_type=1&stock_id=<id>&num=10` returns **20 posts per request** (the server caps `num`) newest-first. The opaque `more_mark` cursor from each response is fed into the next request until `has_more=0`, the cursor stops advancing, or a page lies wholly before the window. A 1.05 s delay and 5 retries were used; 429/5xx were backed off.

## Monthly post counts (MYT)

| Month | GENTING | GENM |
|---|---:|---:|
| 2025-11 | 79 | 89 |
| 2025-12 | 138 | 163 |
| 2026-01 | 71 | 11 |
| 2026-02 | 39 | 12 |
| 2026-03 | 145 | 12 |
| 2026-04 | 132 | 24 |
| 2026-05 | 65 | 8 |
| 2026-06 | 74 | 5 |
| 2026-07 | 43 | 4 |
| 2026-08 | 125 | 19 |
| 2026-09 | 302 | 84 |
| 2026-10 | 378 | 105 |
| 2026-11 | 0 | 1 |

## What a record is

- **Post** — one `comment_feed.feed` item. `native_id` = `feed_comm.feed_id`; `created_utc` = `feed_comm.timestamp` (epoch seconds); author from `author_info.nick_name`/`user_id`; `url` = `https://www.moomoo.com/community/feed/<url_slugname>-<feed_id>`; `num_comments` = `comments_total_count`; `score` = `like.liked_num`. `raw` keeps the feed id, type, title, summary rich-text, like/browse counts, author and detail-fetch marker.
- **Reply** — one item from `get-feed-comment-list`. The endpoint returns the whole thread **flattened**, not just top-level comments. `native_id` = `comment_id`; `post_native_id` = the feed id; `parent_native_id` = `reply_to_comment_id` (the string `"0"` becomes `null`); `depth` is computed by walking that parent chain, so a reply to a reply has depth ≥ 2. `score` = `like.liked_num`. `raw` keeps the parent/user, language flags, emoji ids and rich-text items.
- **Full bodies for long posts** — the server-rendered page `/community/feed/<feed_id>` was fetched when the list payload said `summary.is_complete=false` **or** the summary ended in an ellipsis (the API sometimes truncates even when it flags the summary complete). `detail.moduleData` was rendered to plain text (text, stock mentions and hyperlinks; images omitted). Their `raw.detail_fetched` is `true`.
- **Deduplication** — `(source, native_id)`; the collector also dedupes feed ids across pages and comment ids across pages. A re-run reads the same on-disk API cache and rewrites identical JSONL.

## Data quality notes

- **Language.** `lang` is `null` on every record. moomoo served the English-locale rendering (`current_lang=2`); the API also exposes `translate_info` and `original_lang` but not the original-language text (`original_rich_text_items` was empty). Some Chinese text remains untranslated. The corpus is therefore what an English-reading visitor sees, not a guaranteed original-language transcript.
- **Titles.** `feed_title` is empty for ordinary forum posts. In that case `title` is the first line of the body with a leading `$STOCK(...)$` tag removed, truncated to 160 characters; media-only posts get `[media post] <date>`. The title is derived, never invented free text.
- **Body text.** HTML is stripped, entities decoded and whitespace normalised. The auto-inserted `$STOCK(...)$` tag at the start of a post is removed from `body` (it remains in `raw.summary.rich_text`); cashtags inside the text are kept. Embedded images/videos are not transcribed. Comments whose payload contains no text are kept with an explicit marker: `[emoji]` (custom emoticon-only), `[image]` (image-only) or `[empty]` (blank/deleted). Those markers are the only non-verbatim bodies and explain the validator's duplicate-body warnings.
- **Site-wide content.** The stock feed also carries moomoo news wraps and warrant-issuer promotions tagged to the stock (e.g. Malaysia Morning Wrap, Macquarie warrant posts). They are part of the community feed and were kept; `raw.feed_type` distinguishes them (5 = short stock comment, 3 = long-form post/article, 4 = news wrap, 8 = blog-style long post).

## Coverage and gaps

### GENTING

- **1591 posts / 2797 replies**, from 81 feed pages (20 posts each). 1620 posts were fetched in total; 29 older than the window were discarded and 1591 were kept. The boundary page straddles the window start.
- Date span: 2025-11-02 12:10 UTC / 2025-11-02 20:10 MYT → 2026-10-30 14:51 UTC / 2026-10-30 22:51 MYT.
- Declared `comments_total_count` over all posts: **2798**; replies stored: **2797**. Posts whose declared count differs from stored replies: **1**.
  - `115880840331270`: `comments_total_count=5` but 4 comment(s) returned (deleted/hidden comment is the likely cause).
- Nested replies whose parent id is absent from the returned thread (parent deleted/hidden): **7**. Their `parent_native_id` is kept and depth is set to 1.
- Maximum computed depth: **13**. Full-detail fetches: **134**; posts with an empty `body` (title-only / media / link posts): **173**.
- Non-verbatim reply markers: `[emoji]` × 125, `[image]` × 10, `[empty]` × 4.
- Boundary: the oldest in-window post is the first post at/after `2025-11-01T16:00Z`; the next older post is outside the window. No posts existed between the window start and that first post for this ticker.

### GENM

- **537 posts / 1230 replies**, from 28 feed pages (20 posts each). 560 posts were fetched in total; 23 older than the window were discarded and 537 were kept. The boundary page straddles the window start.
- Date span: 2025-11-03 01:16 UTC / 2025-11-03 09:16 MYT → 2026-11-01 14:08 UTC / 2026-11-01 22:08 MYT.
- Declared `comments_total_count` over all posts: **1230**; replies stored: **1230**. Posts whose declared count differs from stored replies: **0**.
- Nested replies whose parent id is absent from the returned thread (parent deleted/hidden): **7**. Their `parent_native_id` is kept and depth is set to 1.
- Maximum computed depth: **22**. Full-detail fetches: **74**; posts with an empty `body` (title-only / media / link posts): **53**.
- Non-verbatim reply markers: `[emoji]` × 95, `[image]` × 5, `[empty]` × 4.
- Boundary: the oldest in-window post is the first post at/after `2025-11-01T16:00Z`; the next older post is outside the window. No posts existed between the window start and that first post for this ticker.

**No pagination cap was hit.** Both feeds reached a page whose newest post predated the window, so collection stopped naturally. There is no missing date range inside either file. The only content-level gaps are the one comment the API no longer returns (GENTING) and the replies whose parent comment was deleted/hidden (7 per board); the child replies are kept with their parent ids.

### Cross-board overlap

**35 feed posts** and **236 replies** appear in both files with the same `native_id`. These are site-wide news wraps and posts dual-tagged with `$GENTING(3182.BMS)$`/`$GENM(4715.BMS)$` (privatisation, New York casino, morning wraps). They are retained in both channel files because each is a real appearance on that board's feed; if you need one global event corpus, deduplicate on `(source, native_id)` (or `(native_id)`) after loading. `channel` records which board(s) carried them.

## Validation

```
python3 -m genting.validate data/raw/moomoo_my_GENTING.jsonl
python3 -m genting.validate data/raw/moomoo_my_GENM.jsonl
```

Both runs report **0 errors**. Remaining warnings are duplicate body texts (mostly `[emoji]`); posts with no body text (title-only/media/link) have empty `body` fields but do not trigger a validator warning. No duplicate `(source, native_id)` exists **within either file**; the 35 posts shared across the two board files are documented above.
