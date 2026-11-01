# TradingView ideas — collection report

Source: TradingView public trade ideas API (`https://www.tradingview.com/api/v1/ideas/`).
Symbols: `MYX:GENM` (Genting Malaysia) and `MYX:GENTING` (Genting Berhad).
Window: 2025-11-02 → 2026-11-02 inclusive, interpreted in Malaysia time (UTC+8), i.e. 2025-11-01 16:00 UTC → 2026-11-02 15:59:59 UTC.

## Requests and pages

| Ticker | API reported total | Pages fetched | API page_size |
| --- | ---: | ---: | ---: |
| GENM | 53 | 3 | 20 |
| GENTING | 29 | 2 | 20 |

Total API calls made: 5 (page 1 requested once per ticker; pages cached under `data/raw/cache/tradingview/`). At least 1.1 s between calls.

## Records written

- Total ideas in window: **0**
- GENM: **0**
- GENTING: **0**

**No idea was created inside the window, so the JSONL is intentionally empty (0 records).** The API was fully paginated; this is not a fetch failure.

## Coverage check against the source

| Ticker | Ideas fetched (all time) | Oldest idea created | Newest idea created |
| --- | ---: | --- | --- |
| GENM | 53 | 2018-12-19 07:19 UTC | 2024-12-20 12:42 UTC |
| GENTING | 29 | 2018-11-05 08:48 UTC | 2025-04-10 02:18 UTC |

Every idea returned by the API is older than the window start (2025-11-01 16:00 UTC / 2025-11-02 00:00 MYT). Consequently there is no in-window idea to collect for either counter.


## Fields and timestamps

- `created_utc` is derived from the API `created_at` ISO 8601 timestamp (UTC offset included) converted to integer epoch seconds UTC.
- `body` is the full idea `description` with HTML stripped to readable text; line/paragraph breaks preserved, entities decoded, whitespace normalised. Empty descriptions become `null`.
- `score` = `likes_count`, `num_comments` = `comments_count`; `views` = `views_count` (also present in `raw`).
- `url` = `chart_url`; `raw` holds the complete API idea object.
- Deduplication by `(source, native_id)`; native_id is the TradingView idea id.

## Known gaps

- **Comments on ideas are not public.** TradingView's idea-comment endpoints return 404 without authentication, so this file contains ideas (posts) only; `num_comments` records the reported count but the reply text is unavailable.
- Ideas are all-time paginated at 20 per page; the API caps page_size at 20. All pages were fetched before filtering by date, so ideas outside the window were downloaded but excluded from the JSONL.
- TradingView also has a separate **Minds** tab (short stock-forum posts). It is not the trade-ideas API requested here and was not collected.
- View counts are as reported at collection time and may be 0 for ideas whose view counter is not exposed.

## Validation

`python3 -m genting.validate data/raw/tradingview.jsonl` → **OK, 0 errors** (0 records, so no ids, bodies or timestamps to check).
