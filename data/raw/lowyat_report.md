# Lowyat.NET — collection report

**Source:** `lowyat`
**Window:** 2025-11-02 00:00 MYT → 2026-11-02 23:59 MYT
**Collector:** `scripts/collect_lowyat.py`

## Files

| File | Records | Posts | Replies | Threads | Reply date range (MYT) |
|---|---:|---:|---:|---:|---|
| `data/raw/lowyat_GENTING.jsonl` | 14 | 1 | 13 | 1 | 2026-05-22 07:13 → 2026-10-28 04:32 |
| `data/raw/lowyat_GENM.jsonl` | 37 | 3 | 34 | 3 | 2025-11-04 11:40 → 2026-10-29 03:40 |

Each file has one synthetic `post` record per thread, anchored at the window
start, followed by every forum post in the window as a `reply` (`depth: 0`,
`parent_native_id: null` — Lowyat threads are flat). The real opening-post
metadata is preserved in `raw.op_native_id`, `raw.op_created_utc`,
`raw.op_author`.

## Threads included

| Thread | Forum | Title | In-window posts | Last activity |
|---|---|---|---:|---|
| 5581190 | Stock Exchange | Genting is asking shareholders for RM1.25b. | 2 | 2026-10-26 |
| 662423 | Stock Exchange | Genting Malaysia | 10 | 2026-04-15 |
| 5515321 | Kopitiam | Genting Malaysia have 456 tables and 3012 slots ! | 22 | 2026-10-29 |
| 5536525 | Kopitiam | ✨🌏 Genting Group 2026: Global Challenges | 13 | 2026-10-28 |

`5581190`, `662423` and `5515321` are tagged **GENM**; `5536525` is a
group-level thread and is tagged **GENTING**. `5515321` is a Kopitiam
operations/hotel thread with mixed relevance: several posts discuss GENM's
gaming positions, 52-week lows and "buy the dip", but much of it is Genting
Highlands hotel/casino chatter. It is included because the task asked for
Kopitiam Genting threads; downstream scoring may want to filter it.

## Discovery

- `https://forum.lowyat.net/` was reachable as a guest; no login was needed.
- The forum search form was used with title-only queries for `genting`, `genm`,
  `3182` and `4715`, restricted to:
  - Stock Exchange (forum 172)
  - Finance, Business and Investment House (forum 153)
  - Kopitiam (forum 23)
  - Serious Kopitiam (forum 175)
- All matching stock threads were probed from their `/topic/<id>/latest` page.
  Only the four threads above had posts on or after 2025-11-02.
- Other Genting stock threads found but dormant before the window include
  `4952702` (Genting: Hope or False hope?, last 2021), `5114727` (Sime Darby or
  Genm?, last 2025-10-11), `5498125` (Genting, Genm to be dropped from FBM KLCI,
  Dec 2024), `5063606` (Genting vs Genm, 2020), `4897753`, `5074895`, `610474`,
  `3571982` and `1110023`.
- Travel/casino threads (e.g. "Genting Casino @ Baccarat", "Boomers: Best
  Genting is Old Genting", hotel/transport threads) were excluded as not
  investor discussion. The large general thread "STOCK MARKET DISCUSSION V150"
  was excluded because it is not Genting-specific.

## Pages fetched

- `5581190`: 1 page (the whole thread).
- `662423`: 59 pages total; pages 58–59 fetched for window posts, plus page 1
  for opening-post metadata. The fetched range covers 2008-03-30 → 2026-04-15;
  only the in-window posts from pages 58–59 were kept.
- `5515321`: 7 pages total; pages 5–7 fetched for window posts, plus page 1 for
  opening-post metadata. The fetched range covers 2025-03-25 → 2026-10-29.
- `5536525`: 2 pages total; page 2 fetched for window posts, plus page 1 for
  opening-post metadata. The fetched range covers 2025-08-20 → 2026-10-28.

Pages were walked backwards from the last page until a page's oldest post
predated the window, because Lowyat pages are chronological.

## Timestamps

Post dates are rendered as `Mon DD YYYY, HH:MM AM/PM` in Malaysia time
(UTC+8). This was cross-checked against the page's JSON-LD
`datePublished` (e.g. `Oct 23 2026, 10:54 PM` = `2026-10-23T14:54:30+00:00`).
Values were converted to UTC epoch seconds. The collector also handles
`Today`/`Yesterday` relative labels, though none were needed for these pages.

## Gaps and caveats

- **No dedicated GENTING (3182) thread was active in the window.** The only
  GENTING-tagged file is the group-level Kopitiam thread `5536525`. The
  GENTING-specific Lowyat threads found by search were all dormant.
- **Quote blocks are retained** in `body`; Lowyat replies often quote an earlier
  post, so some text repeats. `raw.edited` holds edit notices, which were
  removed from the body.
- **Image-only posts (2, both in `5536525`)** have `body: "[image]"` and the
  image URLs in `raw.media`; they are not invented text.
- **No empty/deleted bodies.** Like/reaction counts are stored in `score`;
  Lowyat shows few likes, so most are `0`.
- Duplicate body text (1 pair) comes from the two image-only posts.
- Validation passes with 0 errors.

## Validation

```bash
python3 -m genting.validate data/raw/lowyat_GENTING.jsonl data/raw/lowyat_GENM.jsonl
# OK: 0 errors
```
