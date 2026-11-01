# Extra sweep — Reddit and Malaysian forums

**Sweep date:** 2 Nov 2026
**Window:** 2 Nov 2024 00:00 MYT → 2 Nov 2026 23:59 MYT (inclusive)
**Scope:** Genting Berhad (`GENTING`, Bursa 3182) and Genting Malaysia (`GENM`, Bursa 4715)

This sweep was run independently of the existing collectors. It deliberately does
**not** duplicate records already written by them. Two files were produced:

| File | Source | Records | Posts | Replies | Ticker mix (posts) | Date range |
|---|---|---:|---:|---:|---|---|
| `data/raw/reddit_extra.jsonl` | reddit (Arctic Shift) | 39 | 8 | 31 | 4 GENM, 4 GENTING | 2024-12-01 → 2026-08-23 |
| `data/raw/forum_extra.jsonl` | cari (Cforum stock forum) | 25 | 4 | 21 | 2 GENM, 2 GENTING | container 2024-11-02; content 2025-03-05 → 2026-10-26 |

Validation:

```bash
python3 -m genting.validate data/raw/reddit_extra.jsonl data/raw/forum_extra.jsonl
```

Both files pass with **0 errors**. Each has one warning for a deleted/removed
reply body (Reddit `mrel4us`, Cari `152006483`). Those rows are kept for
completeness and are identifiable so sentiment scoring can drop them.

---

## 1. Reddit

### Method

Reddit's own search/JSON endpoints return 403 from this machine, so no request
was made to reddit.com. Post/comment data came from the
[Arctic Shift](https://arctic-shift.photon-reddit.com) archive API.

Discovery used:

- `GET /api/posts/search` for `genting` across r/MalaysiaPF, r/malaysia,
  r/BursaMalaysia, r/MalaysianPF, r/bursabets, r/investing,
  r/MalaysiaPersonalFinance and r/MalaysiaStock, oldest-first, full window.
  The r/malaysia sweep was stopped at 2025-11-27 because the existing
  `reddit_threads.jsonl` already covers 2025-11 onward.
- A full-post scan of r/MalaysianPF (6,000 posts, 60 pages) because the
  `query=genting` search for that subreddit repeatedly returned HTTP 422.
  Only six posts contained Genting/GENM/3182/4715; two were relevant.
- Web search (`site:reddit.com ...`) for “Genting Malaysia”, “Genting Berhad”,
  “GENM”, “genting rights issue”, privatisation and takeover phrases. This
  recovered `1ki9l9c` (May 2025) and `1o63n1w` (Oct 2025), which predate the
  existing Reddit collector's window.
- `GET /api/posts/ids` for every selected thread and
  `GET /api/comments/search?link_id=...&limit=100&sort=asc` with `after`
  pagination for every comment and sub-comment.
- 422 responses were retried with exponential backoff (up to 180 s). Several
  keyword attempts (`genm`, `3182`, `4715`, `genting` in r/MalaysianPF) never
  succeeded; the full-subreddit scan and web search were used as fallbacks.

### Threads collected (8)

| Reddit id | Subreddit | Ticker | Post date (UTC) | In-window replies | Title |
|---|---|---|---|---:|---|
| `1h3rrgq` | r/malaysia | GENM | 2024-12-01 | 0 | Genting says no immediate plans to reopen shuttered Malaysian casino floors |
| `1husrkh` | r/malaysia | GENM | 2025-01-06 | 0 | Genting opens new mass casino at Malaysia's Resorts World Genting |
| `1ki9l9c` | r/malaysia | GENM | 2025-05-09 | 15 | Genting's RM3.1bil bet on New York gaming may backfire |
| `1l7ho70` | r/malaysia | GENTING | 2025-06-09 | 5 | How the Lim family built Genting's global empire from Malaysia |
| `1mzlqz1` | r/bursabets | GENTING | 2025-08-25 | 2 | GENTING (RM2.95) Testing Critical Support |
| `1ohaj6s` | r/MalaysianPF | GENM | 2025-10-27 | 4 | What will happen to GENM stock after privatisation? |
| `1o63n1w` | r/malaysia | GENTING | 2025-10-14 | 1 | Genting to privatise Genting Malaysia in RM2.35-per-share buyout |
| `1vw3r3t` | r/bursabets | GENTING | 2026-08-23 | 0 | 开赌场的都会亏钱？云顶发生什么事！ (2Q2026 results) |

All replies to replies were fetched; maximum depth in this set is 4. Three
threads have zero archived comments; they are retained as relevant company-news
posts and can be filtered by `num_comments`/reply count.

### What was excluded and why

- **Already collected by `reddit_threads.jsonl` (not duplicated):** `1opmo58`,
  `1opou5j`, `1owh1lr`, `1pbvq10`, `1t00g2r`, `1tm1dpb`, `1vo3uee`, `1w0fd3h`,
  `1wb90ta`, `1x4lwlt`, `1x4rj3v`, `1xdgakx`, `1xdgbx3`.
- **Travel / consumer / casino-visit threads:** the r/malaysia `genting` result
  set is dominated by Genting Highlands tourism, hotels, tolls, SkyWorlds,
  jackpots and casino rules. These were reviewed by title and excluded because
  they do not discuss GENTING/GENM as companies or securities. Examples:
  `1hb0uzw` (“Future of Genting”, a Genting Highlands property/urbanisation
  question), `1hq1v3e` (fake snow), `1tnu4do` (toll), `1tl9oh1` (jackpot),
  `1mj0px0` (casino chip theft), `1kztnt2` (anti-casino petition).
- **Family/estate stories:** `1rd2x35`, `1u0he23`, `1re53ch` concern the Lim
  family inheritance dispute, not the listed companies' shares or financials.
  The existing Reddit report excluded the same class of thread.
- **Employment/consumer questions:** `1ihbd5t` (working at Genting),
  `1i4u4zn` (casino e-cash), `1rfxwq6` (baccarat minimums).
- **General market threads:** `1pdrbei` (“Anyone into Malaysian stock lately”)
  mentions GENTING as one of several examples. It is not a Genting thread and
  its 109 comments are mostly about other counters, so it was not included.

### Gaps and caveats

- **Arctic Shift 422s:** the archive repeatedly returned “Timeout. Maybe slow
  down a bit” on some keyword/subreddit combinations. Successful pages were
  cached; failed combinations are listed in the method above. The full-post
  scan of r/MalaysianPF mitigates the worst gap.
- **Late-window coverage:** our r/malaysia keyword sweep stops at 2025-11-27
  because `reddit_threads.jsonl` already contains the 2025-11 → 2026-11
  threads. This file therefore complements, rather than repeats, that file.
- **Archive lag:** the latest comment in this file is 2026-08-23. Comments
  posted after the archive's last mirror are not present.
- **Scores** are Arctic Shift snapshot values, not live Reddit scores.
- **`lang` is null** for every Reddit record; no language detector was run.
  `1vw3r3t` is Chinese-language, but that is not encoded as a guess.
- **Raw payloads** contain the original API fields (ids, author, timestamps,
  score, title/selftext or body, permalink, subreddit, retrieval time). Large
  award/report blobs were omitted to stay under the 20 KB contract limit.

---

## 2. Lowyat.NET

An independent search was run across Stock Exchange (172), Finance/Business
(153), Kopitiam (23) and Serious Kopitiam (175) for `genting`, `genm`, `3182`
and `4715`, title-only, sorted by last post. It made **105 requests**, returned
**89 title matches**, and **12 threads had a last post inside the window**.
`5536525` (Genting Group 2026) was already known from the existing GENTING
file and is listed for completeness, giving 13 relevant rows in the table:

| Thread | Title | Last post | Relevance | New records? |
|---|---|---|---|---|
| `5498125` | Genting, Genm to be dropped from FBM KLCI | 2024-12-05 | stock | no — in `lowyat_GENM_2024-2025.jsonl` |
| `662423` | Genting Malaysia | 2026-04-15 | stock | no — in both `lowyat_GENM_*` files |
| `5114727` | Sime Darby or Genm? | 2026-10-10 | stock | no — in `lowyat_GENM_2024-2025.jsonl` |
| `5515321` | Genting Malaysia have 456 tables and 3012 slots! | 2026-10-29 | operations/investor mix | no — in both `lowyat_GENM_*` files |
| `5536525` | Genting Group 2026: Global Challenges | 2026-10-28 | group | no — in both `lowyat_GENTING_*` files |
| `5535462` | Boomers: Best Genting is Old Genting | 2025-08-12 | nostalgia/travel | excluded |
| `5527938` | Going to Genting Highland Resort World next month | 2025-06-18 | travel | excluded |
| `5518939` | How to go genting downslopes? | 2025-04-21 | travel | excluded |
| `5258297` | Genting Skyworlds outdoor theme park | 2025-03-29 | travel | excluded |
| `3470389` | GENTING NOW HAS 5 CONDO PROJECT! | 2024-12-13 | property launches | excluded |
| `2728961` | Genting Casino @ Baccarat | 2026-10-19 | casino tips | excluded |
| `5561075` | Genting Hotel | 2026-06-09 | hotel/travel | excluded |
| `3033206` | Genting Plantation Bhd (2291) | 2026-11-01 | different company (GENP) | excluded |

While this sweep was running, concurrent collectors produced
`lowyat_GENM_2024-2025.jsonl`, `lowyat_GENTING_2024-2025.jsonl` and the
late-window `lowyat_*.jsonl` files. They already contain all four in-window
stock threads (and the group thread), including 118 early-window records. To
honour “only new records”, **no Lowyat rows were written to
`forum_extra.jsonl`**; writing them would duplicate `(source, native_id)` pairs
already in the repository. The independent discovery agrees with the existing
Lowyat coverage.

---

## 3. KLSE Screener — “Ideas” / posts

**Blocked by login.** `https://www.klsescreener.com/v2/posts/all` redirects
(302) to `/v2/users/login?url=posts%2Fall`. Requesting it with an
`X-Requested-With: XMLHttpRequest` header returns the sign-in card instead of
posts; paginated `/v2/posts/all/1` behaves the same. No anonymous JSON endpoint
for Ideas was found. The public `/v2/discussion` page exposes stock comments
only, and those are already covered by the concurrent `klse_screener_*` files
(early and late window). **No KLSE Ideas records were written.**

---

## 4. JBTalks (jbtalks.cc)

- Scanned the stock forum (`forum-1315`) pages 1–12 and the finance forum
  (`forum-1313`); 584 thread titles reviewed.
- The only Genting thread is `thread-1549919`, “云顶 (Genting) 风险”, a single
  post dated **2014-07-03**. No in-window content.
- JBTalks search is disabled for guests (“搜索功能已关闭”), so browsing the
  forum index was the only discovery method.
- **No records written.**

---

## 5. MalaysiaStock.Biz

- Checked the forum index and the three Genting/GENM topics:
  - `tid=119` — GENTING (3182): last post **2024-07-07**.
  - `tid=166` — GENM (4715): last post **2024-06-01**.
  - `tid=23836` — GENM technical analysis: last post **2020-06-21**.
- All are dormant before 2 Nov 2024. **No records written.**

---

## 6. ShareInvestor Malaysia

- `shareinvestor.com/my` is a news, research and investor-relations portal.
  `/my/forum`, `/forum/` and stock pages return 404; no public discussion
  forum was found.
- **No records written.**

---

## 7. Cari / Cforum (cforum.cari.com.my) — other Malaysian investing forum

Cari's `股票，期货、外汇` forum (fid 537) is an active Malaysian Chinese
stock forum not covered by the existing collectors. Search was title-only for
`云顶`, `GENTING`, `GENM`, `3182` and `4715`, restricted to fid 537.

Four threads had in-window posts:

| Thread | Ticker | Title | Pages | In-window posts |
|---|---|---|---:|---:|
| `1519333` | GENTING | 【GENTING 3182 交流专区 2】云顶 | 82 | 7 |
| `1567826` | GENM | 【GENM 4715 交流专区】云顶马来西亚 | 131 | 9 |
| `5156218` | GENM | 云顶大马（GENM,4715,主板消费产品服务组） | 1 | 3 |
| `5178457` | GENTING | 云顶跟股东拿 12.5 亿 Right Issue，你们的决定是什么？ | 1 | 2 |

Threads `2184817` (HWGB 9601, Ho Wah Genting) and `3186997` (GENP 2291,
Genting Plantations) are different listed companies and were excluded.

Collection walked backwards from the last page until a page's oldest post
predated the window, so no page was truncated. The two long threads are sparse
near the end: their in-window content is mostly Bursa announcements, results
and dividend notices rather than day-to-day chat. The October 2026 rights-issue
thread is the only substantial retail discussion.

**Timestamps:** Cari shows Malaysian time as `DD-MM-YYYY HH:MM AM/PM`; values
were parsed as MYT and converted to UTC epoch. The thread container posts for
`1519333` and `1567826` are synthetic, anchored at the window start
(2024-11-02 00:00 MYT = 2024-11-01 16:00 UTC) because the
real opening posts are from 2009; the real OP timestamp is preserved in
`raw.op_created_utc`. All reply timestamps are direct from the page.

**Bodies:** HTML stripped, entities decoded, quoted blocks removed, Discuz
attachment boilerplate removed, whitespace normalised. One deleted reply is
kept as `[deleted]`. The two 2009 opening posts are synthetic containers: their
top-level `body` is `null` and the original 2009 text is preserved in
`raw.op_body`, so out-of-window text is not presented as window content.

---

## 8. Sites checked but not used

| Site | Result |
|---|---|
| reddit.com search/JSON | 403 from this machine; used Arctic Shift instead |
| KLSE Screener Ideas | login wall (302 → `/v2/users/login`) |
| ShareInvestor MY forum | no public forum (404) |
| JBTalks search | disabled for guests |
| MalaysiaStock.Biz | dormant since mid-2024 |
| Facebook / X / Telegram | out of scope (other collectors) |
| i3investor, moomoo, TradingView | already covered by existing collectors; not duplicated |

---

## Deduplication and data handling

- Every record is unique on `(source, native_id)` within its file.
- Reddit ids already present in `reddit_threads*.jsonl` were removed before
  writing (0 overlaps at final check).
- Lowyat ids already present in `lowyat_*.jsonl` were not written.
- Missing values are `null`; no authors, timestamps or text were invented.
- The two deleted bodies are preserved, not replaced with guessed text.
- Raw payloads are JSON-serialisable and well under 20 KB per record.

## Known gaps

1. **Arctic Shift instability** blocked some keyword searches (`genm`, `3182`,
   `4715`) in several subreddits. r/MalaysianPF was fully scanned as a
   workaround; r/malaysia and r/bursabets rely on the `genting` search plus web
   search, so a post that says only “GENM” and never “Genting” could be missed.
2. **Late-window Reddit** is intentionally delegated to `reddit_threads.jsonl`;
   this sweep only adds pre-Nov-2025 threads and a few late threads that the
   existing file did not contain.
3. **KLSE Ideas** could not be read without an account.
4. **Cari** coverage is limited to the four active threads found by title
   search; a Genting mention buried inside an unrelated thread would not be
   found because Cari's search is title-only for guests.
5. **Forum posts after the archive/page snapshot** (2 Nov 2026) are not present.
