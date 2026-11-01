# Reddit collection report — Malaysian Genting, earlier year

- **Collected:** 2 Nov 2026
- **Window:** 2 Nov 2024 00:00 MYT → 1 Nov 2025 23:59:59 MYT (1 Nov 2024 16:00 UTC → 1 Nov 2025 16:00 UTC)
- **Source:** Reddit, read through the Arctic Shift archive API
- **Output:** `data/raw/reddit_threads_2024-2025.jsonl`
- **Records:** 37 — 7 posts, 30 replies
- **Post tickers:** GENM × 5, GENTING × 2
- **Date range in file:** 2024-12-01 → 2025-11-01
- **Comment date range:** 2025-05-09 → 2025-11-01
- **Comment threads:** 19 top-level comments, 11 replies, 27 distinct authors
- **Validation:** `python3 -m genting.validate data/raw/reddit_threads_2024-2025.jsonl` → **OK, 0 errors, 1 warning** (one removed/deleted comment body; kept for completeness)

## Method

Reddit's own search and anonymous JSON endpoints return 403 from this machine. Threads were discovered with (a) Reddit's public Atom search feed (`/r/<sub>/search.rss?q=genting&restrict_sr=1&sort=new&t=all`), paged backwards to 2 Nov 2024, and (b) Arctic Shift `/api/posts/search` title searches for `genting`, `GENM`, `4715`, `3182` and `云顶` across r/MalaysiaPF, r/MalaysianPF, r/malaysia, r/BursaMalaysia and r/bursabets.  Arctic Shift's full-text `query` search timed out repeatedly, so the lighter title search plus the RSS full-text feed were used together; the RSS feed catches possessives such as "Genting's" that the title tokenizer misses.

Content was fetched only through Arctic Shift: `/api/posts/ids` for the posts, then `/api/comments/search?link_id=<id>&limit=100&sort=asc` for every comment page. Pagination uses `after=<created_utc>`; the cursor is set to `newest-1` so comments that share a second are not skipped (duplicates are removed by id).  Comments are filtered to the window by their exact `created_utc`.  No selected post was missing from the archive.

## Threads collected

| Reddit id | Subreddit | Ticker | Post date (UTC) | Replies in file | Comments fetched | `num_comments` | Title |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| `1h3rrgq` | r/malaysia | GENM | 2024-12-01 | 0 | 0 | 0 | Genting says no immediate plans to reopen shuttered Malaysian casino floors |
| `1husrkh` | r/malaysia | GENM | 2025-01-06 | 0 | 0 | 0 | Genting opens new mass casino at Malaysia’s Resorts World Genting |
| `1ki9l9c` | r/malaysia | GENM | 2025-05-09 | 15 | 15 | 15 | Genting’s RM3.1bil bet on New York gaming may backfire |
| `1l7ho70` | r/malaysia | GENTING | 2025-06-09 | 5 | 5 | 4 | How the Lim family built Genting’s global empire from Malaysia |
| `1mzlqz1` | r/bursabets | GENTING | 2025-08-25 | 2 | 2 | 2 | GENTING (RM2.95) Testing Critical Support ⚠️ Will It Rebound From Oversold Levels? |
| `1o63n1w` | r/malaysia | GENM | 2025-10-14 | 1 | 1 | 1 | Genting to privatise Genting Malaysia in RM2.35-per-share buyout |
| `1ohaj6s` | r/MalaysianPF | GENM | 2025-10-27 | 7 | 8 | 4 | What will happen to GENM stock after privatisation? |

## Discovery and exclusions

The r/malaysia full-text feed returned 82 posts for `genting` in the window, but almost all were Genting Highlands travel, hotel, theme-park, crime or consumer threads; only the company-news and market threads were kept.  r/MalaysianPF produced the privatisation thread; r/MalaysiaPF produced no relevant in-window thread; r/bursabets produced one technical thread; r/BursaMalaysia had no in-window Genting thread.  Excluded examples: `1hb0uzw` (Genting Highlands development/real estate), `1heu0yb` (KWSP portfolio list), `1l2rlu9` (Daim's empire), `1nti3p1` (removed body), and the many travel/consumer threads.  The `1l7ho70` company-history feature is included because it is about how Genting Berhad was built, not a family-estate dispute.

## Known gaps and caveats

- `num_comments` is an archive snapshot and can be lower or higher than the number of archived comments (Arctic Shift updates comments separately from the post row). The reply rows are the authoritative measure of what was retrievable.
- Removed/deleted comment bodies are kept as `[deleted]`/`[removed]` for completeness; they produce validator warnings and will be skipped by any sentiment scorer.
- Scores are archive-snapshot values, not live Reddit scores. `lang` is `null` for every record because no language detector was run.
- Post `url` is the Reddit permalink; the outbound article URL is in `raw.url`. Reply URLs are comment permalinks.
- Depth is computed from the `parent_id` chain (`t3_` = top level, `t1_` = reply to a comment). Every selected thread's parents were present, so no depth was inferred.

## Timestamps

All `created_utc` values are integer epoch seconds taken directly from Arctic Shift's `created_utc`, which is UTC. No relative-time strings were parsed and no timestamps were estimated for Reddit.

## Deduplication

Records are unique on `(source, native_id)` within this file.  The 2025-2026 file `data/raw/reddit_threads.jsonl` starts on 6 Nov 2025, so no post or comment in this earlier-year file overlaps it.

