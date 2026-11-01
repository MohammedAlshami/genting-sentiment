# Lowyat.NET — 2024-2025 backfill report

**Source:** `lowyat`
**Window:** 2024-11-02 00:00 MYT → 2025-11-01 23:59:59 MYT
**Collector:** `scripts/backfill_lowyat.py` (copy of `scripts/collect_lowyat.py`)
**Status:** complete; validation passes with 0 errors.

The existing 2025-2026 files were **not** modified:

- `data/raw/lowyat_GENTING.jsonl`
- `data/raw/lowyat_GENM.jsonl`

## Files

| File | Records | Posts | Replies | Threads | Unique authors | Reply range (MYT) |
|---|---:|---:|---:|---:|---:|---|
| `data/raw/lowyat_GENTING_2024-2025.jsonl` | 26 | 1 | 25 | 1 | 7 | 2025-08-20 14:11 → 2025-08-23 19:23 |
| `data/raw/lowyat_GENM_2024-2025.jsonl` | 118 | 4 | 114 | 4 | 51 | 2024-12-05 14:57 → 2025-10-30 18:57 |

Each thread is one synthetic `post` record plus its in-window forum posts as
`reply` records (`depth: 0`, `parent_native_id: null`) because Lowyat threads
are flat. `raw.thread_started_utc` / `raw.thread_started_myt` record the real
thread start. For threads that began before the window the synthetic `post` is
anchored at `2024-11-02 00:00 MYT`; for threads that began inside the window it
uses the first visible opening post's timestamp.

## Threads included

| Thread | Ticker | Forum | Title | Thread started (MYT) | In-window posts | Post range (MYT) |
|---|---|---|---|---|---:|---|
| `662423` | GENM | Stock Exchange | Genting Malaysia | 2008-03-30 00:33 | 4 | 2025-10-13 → 2025-10-21 |
| `5114727` | GENM | Stock Exchange | Sime Darby or Genm? | 2021-03-09 20:42 | 2 | 2025-10-11 → 2025-10-11 |
| `5498125` | GENM | Kopitiam | Genting, Genm to be dropped from FBM KLCI | 2024-12-05 (first visible post) | 14 | 2024-12-05 → 2024-12-05 |
| `5515321` | GENM | Kopitiam | Genting Malaysia have 456 tables and 3012 slots ! | 2025-03-25 16:22 | 94 | 2025-03-25 → 2025-10-30 |
| `5536525` | GENTING | Kopitiam | ✨🌏 Genting Group 2026: Global Challenges | 2025-08-20 14:11 | 25 | 2025-08-20 → 2025-08-23 |

`662423` and `5114727` started before the window; their real start dates are in
`raw.thread_started_utc` and `raw.op_created_utc`. `5515321` and `5536525`
started inside the window. `5498125` is a special case: only posts
#3–#9, #11–#12, #14 and #16–#19 are rendered — #1, #2, #10, #13 and #15 are
absent from the page, so the first visible post is #3
(`raw.first_visible_post_number = 3`, `raw.op_rendered = false`). Its synthetic
`post.author` is therefore `null` rather than the author of reply #3;
`raw.thread_started_utc` is `null` (unknown), while
`raw.first_visible_post_utc` is the first visible timestamp (14:57) and is also
the synthetic post's `created_utc`. A quote inside post #8 references the
unavailable opening post at 14:40.

## Discovery

- Searched Lowyat titles for `genting`, `genm`, `3182` and `4715` across:
  - Stock Exchange (forum 172)
  - Finance, Business and Investment House (forum 153)
  - Kopitiam (forum 23)
  - Serious Kopitiam (forum 175)
- Enumerated 1,065 unique title matches. Threads whose last-post age could fall
  in or after the window, plus the previously known Genting threads, were
  probed at `/topic/<id>/latest` (18 probes in the final discovery pass).
- Included every matching investor-discussion thread with in-window posts.
  Excluded non-investment threads found by the same search:
  - `5581190` “Genting is asking shareholders for RM1.25b.” — created
    2026-10-23; no 2024-2025 posts.
  - `5535462` “Boomers: Best Genting is Old Genting” — nostalgia/travel.
  - `5258297` “Genting Skyworlds outdoor theme park” — travel/attraction.
  - `5518939` “How to go genting downslopes?” — travel.
  - `5527938` “Going to Genting Highland Resort World next month” — travel.
  - `3470389` “GENTING NOW HAS 5 CONDO PROJECT!” — property development.
  - `2728961` “Genting Casino @ Baccarat” and `5561075` “Genting Hotel” —
    casino/travel.
  - Dormant stock threads whose last post predates the window (e.g. `4952702`
    last 2021, `5063606` last 2020, `4897753` last 2020, `5074895` last 2020,
    `610474` last 2017, `3571982` last 2015, `1110023` last 2009).

`5515321` is a Kopitiam operations/hotel thread with mixed relevance. Parts
discuss GENM's gaming positions, share price and “buy the dip”, but much is
Genting Highlands hotel/casino chatter. It is included for consistency with the
existing 2025-2026 collection; downstream scoring may filter it.

## Collection and pages fetched

Pages were walked backwards from `/topic/<id>/latest` until a page's oldest post
predated the window start, then page 1 was fetched when needed for opening-post
metadata. Lowyat pages hold 20 posts.

| Thread | Total pages | Pages fetched for this pull | Coverage |
|---|---:|---:|---|
| `662423` | 59 | 59, 58, 1 | 2025-11-07 back to 2023-02-26, plus OP |
| `5114727` | 1 | 1 | whole thread |
| `5498125` | 1 | 1 | whole thread |
| `5515321` | 7 | 7, 6, 5, 4, 3, 2, 1 | whole thread |
| `5536525` | 2 | 2, 1 | whole thread |

Fourteen thread pages were fetched. The final discovery pass made 79 HTTP
requests (including `/latest` probes); the collector itself reused cached pages
from the same-day 2025-2026 run, so repeated runs made no new page requests.

## Orphan parents

**0.** Lowyat threads are flat: every reply has `parent_native_id: null` and
`depth: 0`, and `post_native_id` always matches a synthetic thread post in the
same file.

## Gaps

The files contain every in-window post from the included threads. Quiet periods
below are real thread dormancy, not skipped pages: each page's oldest post was
checked before the backward walk stopped.

### GENM — 20 active days of 365

Longest gaps:

| Gap | Days |
|---|---:|
| 2024-12-06 → 2025-03-24 | 109 |
| 2025-06-16 → 2025-08-24 | 70 |
| 2025-04-13 → 2025-06-14 | 63 |
| 2024-11-03 → 2024-12-04 | 32 |
| 2025-09-11 → 2025-10-05 | 25 |
| 2025-04-04 → 2025-04-11 | 8 |
| 2025-03-26 → 2025-04-01 | 7 |
| 2025-08-28 → 2025-09-02 | 6 |
| 2025-10-14 → 2025-10-19 | 6 |
| 2025-10-24 → 2025-10-29 | 6 |

`662423`, `5114727` and `5498125` are low-volume/dormant for most of the year;
`5515321` accounts for 94 of the 114 GENM replies and is the main source of
activity from March to October 2025.

### GENTING — 4 active days of 365

| Gap | Days |
|---|---:|
| 2024-11-03 → 2025-08-19 | 290 |
| 2025-08-24 → 2025-11-01 | 70 |

No GENTING-specific Lowyat thread was active between November 2024 and August
2025. `5536525` was created on 2025-08-20 and produced 25 posts over four days;
it then went quiet. This mirrors the existing 2025-2026 GENTING file, which also
has only the group-level `5536525` thread.

## Timestamps

Lowyat renders post times as `Mon DD YYYY, HH:MM AM/PM` in Malaysia time
(UTC+8), e.g. `Oct 13 2025, 05:06 PM`. Values were parsed with
`%b %d %Y, %I:%M %p`, localised to `Asia/Kuala_Lumpur`, and converted to integer
UTC epoch seconds. Every in-window post had an absolute timestamp; the
`Today`/`Yesterday` fallback was not needed. The original string is preserved in
`raw.time_text`.

## Known gaps / caveats

- **Deleted/removed posts are not rendered.** Lowyat keeps post numbers but
  omits deleted posts from the page, leaving numbering gaps. In this pull:
  - `5498125`: #1, #2, #10, #13, #15 absent (14 visible posts of #3–#19).
  - `5515321`: #5, #22, #71, #95 absent (94 visible posts of #1–#98).
  - `662423` and `5114727`: only their in-window tails are visible here;
    missing low numbers are older posts outside the window, not deletions.
  - `5536525`: no numbering gaps.
  No bodies or authors are invented for the absent posts.
- **Quote blocks are retained** in `body`; Lowyat replies often quote an earlier
  post, so some text repeats. `raw.edited` holds edit notices removed from the
  body.
- **One duplicate body text pair** in `lowyat_GENM_2024-2025.jsonl`: two
  image-only posts both have `body: "[image]"`. Their image URLs are in
  `raw.media`. No duplicate `native_id`.
- **No empty/deleted bodies** in either file; all replies have an author,
  author id and like count. Like counts are mostly `0`.
- Threads are flat by design; `parent_native_id` is always `null`.
- `num_comments` on a synthetic post is the number of in-window reply records
  for that thread, matching the existing convention.
- The files do not overlap the 2025-2026 files at the reply level: this
  backfill ends at 2025-10-30 18:57 MYT; the existing files start at
  2025-11-02 00:00 MYT. Threads `662423`, `5515321` and `5536525` also appear
  in the 2025-2026 Lowyat files, so their synthetic thread `post` record uses
  the same stable `native_id` in both years; the store upserts those by
  `(source, native_id)`. Reply records are disjoint.

## Validation

```bash
python3 -m genting.validate \
  data/raw/lowyat_GENTING_2024-2025.jsonl \
  data/raw/lowyat_GENM_2024-2025.jsonl
# OK: 0 errors
```
