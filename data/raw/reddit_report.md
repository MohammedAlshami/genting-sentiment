# Reddit collection report — Malaysian Genting

- **Collected:** 2 Nov 2026
- **Window:** 2 Nov 2025 → 2 Nov 2026 (inclusive)
- **Source:** Reddit, read through the [Arctic Shift](https://arctic-shift.photon-reddit.com) archive API
- **Output:** `data/raw/reddit_threads.jsonl`
- **Records:** 119 total — 13 posts, 106 replies
- **Post tickers:** 8 × `GENM`, 5 × `GENTING`
- **Date range in file:** 6 Nov 2025 → 28 Oct 2026
- **Validation:** `python3 -m genting.validate data/raw/reddit_threads.jsonl` → **OK, 0 errors** (3 warnings for removed comment bodies, explained below)

## Method

Reddit's own search and anonymous JSON endpoints return 403 from this machine, so no request was made to reddit.com for discovery or data. Threads were found with:

- Web search queries: `site:reddit.com "Genting" Malaysia stock`, `site:reddit.com r/MalaysiaPF Genting`, `site:reddit.com r/BursaMalaysia Genting`, `reddit GENM 4715`, `reddit "Genting rights issue"`, `reddit Genting Berhad 3182`, plus variations for Fitch/Moody's, privatisation, New York casino and the October 2026 share fall.
- DuckDuckGo HTML results for `site:reddit.com Genting ...` to recover thread URLs that the search tool did not surface.
- As a completeness check, Arctic Shift's `/api/posts/search` **title** keyword search (`genting`, `GENM`, `4715`, `3182`) restricted to 2 Nov 2025 – 3 Nov 2026 across r/MalaysiaPF, r/MalaysianPF, r/malaysia, r/BursaMalaysia, r/bursabets, r/investing, r/stocks and r/StockMarket. This found the same core threads plus additional low-comment news posts; tourism, theme-park, toll, casino-consumer and family/legacy threads were then filtered out.

Content was fetched only through Arctic Shift:

- `GET /api/posts/ids?ids=<comma-separated ids>` — one call for all 13 posts.
- `GET /api/comments/search?link_id=<id>&limit=100&sort=asc` — one page per thread; every selected thread had fewer than 100 archived comments. The collector still implements `&after=<last created_utc>` pagination and deduplicates by comment id, so a long thread would not be truncated.
- **14 successful collection calls** (1 post lookup + 13 comment pages), spaced at least 1.2 seconds apart. Discovery calls were also spaced; 422 "Timeout. Maybe slow down a bit" responses were retried with exponential backoff. No selected thread was missing from the archive.

## Threads collected

| Reddit id | Subreddit | Ticker | Post date (UTC) | Replies fetched | `num_comments` in archive | Title |
| --- | --- | --- | --- | ---: | ---: | --- |
| `1opmo58` | r/malaysia | GENM | 2025-11-06 | 0 | 0 | Bakri MP flags potentially suspicious Genting Malaysia stock movements; govt says trading appears legit |
| `1opou5j` | r/MalaysianPF | GENM | 2025-11-06 | 16 | 9 | Genting stock Take Over Offer |
| `1owh1lr` | r/malaysia | GENM | 2025-11-13 | 0 | 0 | Genting extends takeover offer for Genting Malaysia to Dec 1 |
| `1pbvq10` | r/malaysia | GENM | 2025-12-02 | 1 | 1 | Genting Malaysia to Stay Listed After Privatization Bid Flops |
| `1t00g2r` | r/malaysia | GENM | 2026-04-30 | 0 | 0 | High Court halts Sky City project in Genting Highlands |
| `1tm1dpb` | r/malaysia | GENM | 2026-05-24 | 5 | 5 | Genting Malaysia Faces Unfavourable Conditions |
| `1vo3uee` | r/malaysia | GENTING | 2026-08-14 | 1 | 1 | Genting Singapore net profit drops 34% to $156m in H1 |
| `1w0fd3h` | r/bursabets | GENM | 2026-08-28 | 2 | 1 | 🔥 GENM 4715：营收暴增32%，净利却暴跌! |
| `1wb90ta` | r/malaysia | GENM | 2026-09-09 | 7 | 6 | Fitch Downgrades Genting Malaysia to 'BBB-' |
| `1x4lwlt` | r/malaysia | GENTING | 2026-10-13 | 38 | 38 | Shares in Malaysia's Genting tumble by most in 28 years |
| `1x4rj3v` | r/BursaMalaysia | GENTING | 2026-10-13 | 0 | 0 | Genting Crashes 23%! Buy or Avoid? |
| `1xdgakx` | r/MalaysianPF | GENTING | 2026-10-23 | 30 | 31 | Genting is asking shareholders for RM1.25b. 86% of it goes to old debt and interest. What is your decision? |
| `1xdgbx3` | r/MalaysiaPF | GENTING | 2026-10-23 | 6 | 5 | Genting is asking shareholders for RM1.25b. 86% of it goes to old debt and interest. What is your decision? |

Thread-level totals: 106 replies, maximum nesting depth 4 (`1opou5j`), 92 distinct non-deleted authors. Four selected posts had no archived comments; they are retained as relevant company-news posts and can be filtered out of sentiment scoring by `num_comments`/reply count.

## Threads checked but not included

- `1ki9l9c` — "Genting's RM3.1bil bet on New York gaming may backfire" (r/malaysia, 9 May 2025). Relevant, but all 15 archived comments are dated 9 May 2025 and none fall in the window, so it was not included under the window rule.
- `1079z2g` and `161mdhl` — older Genting investment threads (2023); last comments are from 2023, so they were not active in the window.
- Tourism / consumer threads in r/malaysia such as the Genting Highlands toll posts (`1ovw8x6`, `1ovx6x1`, `1ow1se7`, `1tnu4do`), SkyWorlds/ride posts, jackpot/robbery posts, and travel advice. These discuss visiting Genting Highlands, not GENTING/GENM as companies or securities.
- `1rd2x35` — "Genting inheritance saga" (89 comments). It concerns the Lim family estate, not the listed companies' shares or financials; excluded to keep the sentiment sample company-focused.
- `1w6r5bo` — Disney Adventure / Genting Hong Kong history (16 comments). Genting Hong Kong left the Genting group in 2016 and is not GENTING or GENM; excluded.
- `1vpy71c` — Genting Malaysia Scholarship (not investor/company discussion).
- r/investing, r/stocks and r/StockMarket had no Malaysia-Genting threads in the window; the only `GENM` matches were for Generation Mining Ltd.

## Known gaps and caveats

- **`1xdgakx` comment count:** Arctic Shift reports `num_comments = 31` but returns 30 comments. There is no second page (`len(page) < 100`), so one comment is not present in the archive — most likely removed/deleted before archival or a count discrepancy. It is recorded as a gap, not fabricated.
- **Archive `num_comments` is a snapshot.** `1opou5j` reports 9 but has 16 archived comments; `1wb90ta` reports 6 but has 7; `1w0fd3h` reports 1 but has 2; `1xdgbx3` reports 5 but has 6. Arctic Shift's documentation notes that `score` and `num_comments` can be initial values captured shortly after posting, while the comment archive is updated separately. The `num_comments` field is preserved as returned; the reply records are the more complete measure.
- **Removed comments:** 3 replies in `1opou5j` have body `[removed]` and deleted authors. They are kept for completeness and will be excluded by any sentiment scorer. This accounts for the 3 validator warnings.
- **Archive lag:** the latest comment retrieved is dated 28 Oct 2026. Comments posted after that, or after the archive's last mirror, will not be present. No selected post itself was missing.
- **Scores:** post/reply scores are values from the archive snapshot, not live Reddit scores. They are left as returned and may be stale.
- **Language:** `lang` is `null` for every record. Several threads are English; `1w0fd3h` is Chinese-language. No language detector was run, so no guesses are recorded.
- **URLs:** `url` on a post is the Reddit permalink, not the linked news article. The outbound article URL is preserved in `raw.url`. Reply URLs are comment permalinks.
- **Raw payloads:** `raw` contains the essential original API fields (ids, author, timestamps, score, title/selftext or body, permalink, subreddit, retrieval time). Large award/report blobs were omitted to keep each record well under the 20 KB contract limit; the largest raw record is about 2.5 KB.
- **Depth:** Arctic Shift's flat comment rows do not include `depth`, so depth was computed from the `parent_id` chain (`t3_` = top level, `t1_` = reply to a comment). Every parent was present in the fetched set, so no depth had to be inferred.

## Timestamps

All `created_utc` values are integer epoch seconds taken directly from the Arctic Shift `created_utc` field, which is UTC. No relative-time strings were parsed and no timestamps were estimated.

## Deduplication

Records are unique on `(source, native_id)`. The two rights-issue posts `1xdgakx` and `1xdgbx3` are intentionally separate records: they are the same author's post in two different subreddits, each with its own native id, comments and score.
