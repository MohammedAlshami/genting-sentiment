# Small Malaysian forums — 2016-2024 backfill report

**Collected:** 2 Nov 2026.
**Window:** 2 Nov 2016 00:00 MYT → 1 Nov 2024 23:59:59 MYT
(1 Nov 2016 16:00 UTC → 1 Nov 2024 16:00 UTC).
**Scope:** Genting Berhad (`GENTING`, Bursa 3182) and Genting Malaysia (`GENM`,
Bursa 4715). Travel / theme-park / hotel / casino-consumer / family-estate
discussion is excluded; the files are company and market discussion.

**Outputs**

| File | Records | Posts | Replies | First record (UTC) | Last record (UTC) |
| --- | ---: | ---: | ---: | --- | --- |
| `data/raw/lowyat_GENTING_2016-2024.jsonl` | 474 | 14 | 460 | 2016-11-01 16:00 | 2022-01-25 07:47 |
| `data/raw/lowyat_GENM_2016-2024.jsonl` | 214 | 13 | 201 | 2016-11-01 16:00 | 2024-06-13 13:57 |
| `data/raw/cari_2016-2024.jsonl` | 482 | 17 | 465 | 2016-11-01 16:00 | 2024-09-13 17:34 |
| `data/raw/reddit_2016-2024.jsonl` | 341 | 56 | 285 | 2017-06-14 05:32 | 2024-10-16 07:54 |
| **Total** | **1,511** | **100** | **1,411** | | |

In Lowyat and Cari, the earliest `created_utc` is the window anchor for
threads that started before the window; the real opening-post time is kept in
`raw.op_created_utc` / `raw.thread_started_utc` (Lowyat) and
`raw.op_created_utc` (Cari). Reddit timestamps are the real archive
`created_utc`.

Ticker split (posts / replies):

| File | GENTING | GENM |
| --- | ---: | ---: |
| Lowyat GENTING | 14 / 460 | — |
| Lowyat GENM | — | 13 / 201 |
| Cari | 12 / 309 | 5 / 156 |
| Reddit | 22 / 145 | 34 / 140 |

## Discovery and collection

### Lowyat.NET

- **Discovery:** title search for `genting`, `genm`, `3182`, `4715` across Stock
  Exchange (172), Finance / Business (153), Kopitiam (23) and Serious Kopitiam
  (175) — 16 search queries. The existing candidate run produced **182 title
  matches**; 27 company/market threads were selected for this window.
- **Collection:** **27 threads**, **54 pages fetched** (one HTTP GET per page,
  54 requests), walking backwards from each thread's last page until the first
  page older than 2 Nov 2016. `/topic/<id>/latest` + page 1 supplied the title
  and opening post.
- **Notable threads:** `610474` “GENTING” (2008-2017, 34 in-window replies),
  `4699412` “Genting Fox theme park cancelled” (202 replies), `662423`
  “Genting Malaysia” (2008-2026, 91 in-window replies), plus the 2018-2024
  results / Macau / privatisation-era threads.
- **Contract:** flat forum — one synthetic `post` per thread, one `reply` per
  in-window post, `parent_native_id: null`, `depth: 0`,
  `post_native_id` = thread id. Every reply also carries
  `raw.thread_title`.

### Cari (cforum.cari.com.my)

- **Discovery:** five title searches (`云顶`, `GENTING`, `GENM`, `3182`, `4715`)
  in the 股票，期货、外汇 board returned **58 title matches**; 17 company
  threads were selected. Genting Plantation (GENP), Ho Wah Genting, Genting
  Singapore (G13) and Genting Hong Kong (S21) threads were excluded as
  different listed companies.
- **Collection:** **17 threads**, **41 pages parsed**, **44 HTTP requests**
  (page 1 + backward walk from the last page until the first page older than
  the window). The two long `交流专区` threads (`1519333` GENTING, 82 pages;
  `1567826` GENM, 131 pages) account for 366 replies.
- **Contract:** one `post` per thread (opening text only when the OP is inside
  the window) and one `reply` per in-window post; Chinese text, `lang: "zh"`.
  Replies carry `raw.thread_title`.

### Reddit

- **Discovery:** Arctic Shift title search over r/malaysia, r/MalaysianPF,
  r/MalaysiaPF, r/BursaMalaysia, r/bursabets, r/investing, r/stocks,
  r/StockMarket and r/SecurityAnalysis for `genting`, `genm`, `3182`, `4715`:
  **36 queries, 38 result pages, 216 unique posts**. Because long range queries
  frequently returned HTTP 422, the collector walked backwards in 25-row pages.
- **Full-text supplement:** Reddit Atom search (`q=genting`, `q=genm` in
  r/malaysia): **2 queries, 6 pages, 245 rows, 102 in-window posts**.
- **Gap anchors:** 8 `before` anchors (2022-09, 2022-06, 2022-01, 2021-01,
  2020-01, 2019-01, 2018-01, 2017-01); 6 succeeded and produced 147 posts,
  2 failed (2019-01 and 2017-01) with HTTP 422.
- **Company-title probes:** `genm`, `genting malaysia`, `genting berhad`,
  `genting` before 2020 — 4 queries, 48 posts. A second 2016-2017 probe — 4
  queries, 27 posts.
- **Candidate pool:** **414 unique posts**. After the window and relevance
  filter: **56 posts** selected (7 outside window, 351 irrelevant).
- **Collection:** **56 comment pages** (`/api/comments/search?link_id=...`),
  **285 comments fetched**, all inside the window. 33 threads contributed
  comments; 23 posts have an archive `num_comments` of 0 (22 have no reply
  rows and one has later comments).
- **Contract:** post rows have title/body/score/`num_comments`; replies keep
  `parent_native_id`, computed `depth` (0-6), permalink, and
  `raw.thread_title`. All 144 non-null parent ids are present in the file
  (0 missing parents; 141 replies are top-level).

## Validation

`python3 -m genting.validate` was run on each file:

| File | Errors | Warnings | Warning breakdown |
| --- | ---: | ---: | --- |
| Lowyat GENTING | 0 | 474 | 474 timestamp outside validator window |
| Lowyat GENM | 0 | 214 | 214 timestamp outside validator window |
| Cari | 0 | 483 | 482 timestamp outside validator window; 1 empty/deleted body |
| Reddit | 0 | 358 | 340 timestamp outside validator window; 18 empty/deleted bodies |

`genting.validate` has a hard-coded `MIN_TS = 2024-10-01`. Every 2016-2024
record therefore produces a timestamp warning even though it is inside the
requested 2016-11-02 → 2024-11-01 window. The warnings are not data errors; a
custom window check found **0 records outside the requested window** and **0
duplicate `(source, native_id)` keys**.

Duplicate body text stats (validator): Lowyat GENTING 4 (two `PLOUFFLE`
reactions, two `Sad` reactions, three `[image]` placeholders), Lowyat GENM 0,
Cari 3 (two `Loading FB Video...` placeholders, two `RM 2.93......` posts, and
one director-change announcement copied across the two long threads), Reddit 2
(three copies of the same bot removal notice).

## Coverage by year (records, all record types)

| Year | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Records | 24 | 136 | 551 | 217 | 189 | 165 | 85 | 46 | 98 |
| Posts | 5 | 2 | 13 | 8 | 11 | 16 | 23 | 9 | 13 |

## Known gaps and caveats

1. **Lowyat discovery is title-based.** Threads where Genting/GENM appears only
   in a post body are not enumerated. The 182-title candidate set was filtered
   to company/market threads; travel, hotel, theme-park, condo, casino-consumer,
   Kamen Rider, Genting Plantation, Ho Wah Genting and Genting Singapore/Hong
   Kong threads were deliberately left out.
2. **Lowyat GENTING activity ends 25 Jan 2022.** No 2022-11 → 2024-11
   GENTING-titled company threads were found; later GENTING discussion appears
   mostly in the GENM thread or on other platforms. The GENM main thread
   (`662423`) has no posts between 2014-10 and 2018-11 (its page 53 spans that
   gap), so GENM has no 2016-2017 replies.
3. **Cari search returned 58 title matches.** The board's topic search is
   title-only, so body-only mentions are missed. The two long threads dominate;
   activity collapses after 2020 (7 replies in 2021, 7 in 2022, 0 in 2023, 5
   in 2024). The 2022-2023 company-news threads are single-post threads with no
   replies.
4. **Reddit has a 2016 gap.** No qualifying company post was found before
   **14 Jun 2017**; the 2016-11/12 candidates were travel, ESL/Dota or
   pre-window posts. 2017-2020 are sparse (2, 3, 4, 3 posts per year); 2021-
   2024 are much better covered (12, 13, 6, 13).
5. **Reddit API limits.** Arctic Shift range queries frequently returned HTTP
   422; the 2019-01 and 2017-01 gap anchors failed, so parts of 2016 and 2019
   may be under-covered. The Atom full-text feed caps at roughly 245 results,
   so it only reaches mid-2023 for r/malaysia. r/BursaMalaysia and r/investing
   produced no qualifying title matches; the one r/investing `genm` hit was a
   Canadian `GENM.TO` mining company and was excluded. r/MalaysianPF has 3
   qualifying posts.
6. **Comments are complete for the selected threads, not the whole of Reddit.**
   Comments mentioning Genting in unrelated threads were not exhaustively
   mined. 18 archived comment bodies are `[deleted]`/`[removed]`; those rows are
   kept for completeness and produce validator warnings. Scores and `num_comments` are archive
   snapshots, not live Reddit values; 8 of 56 posts have an archive
   `num_comments` that differs from the number of reply rows written.
7. **Timestamps:** Lowyat and Cari dates were parsed from the sites' MYT
   display strings and converted to UTC epoch seconds. Reddit timestamps are
   the archive's `created_utc`. No relative-time strings were guessed.
8. **Tail gaps before 1 Nov 2024:** Reddit 17-31 Oct 2024, Cari 14 Sep-31
   Oct 2024, Lowyat GENM 14 Jun-31 Oct 2024, Lowyat GENTING 26 Jan 2022-31
   Oct 2024. These are periods with no qualifying in-window posts in the
   collected threads, not missing rows inside collected pages.
9. **No SQLite writes, no website changes, no existing data/raw file was
   overwritten.** The new files use `_2016-2024` names; the existing
   2024-11-02 → 2026 files were read only for overlap checks. No
   `data/raw/cari*.jsonl` existed before this run; the only earlier Cari
   artifact was `/tmp/opencode/cari_records.json` (2024-2026), which was not
   modified.
