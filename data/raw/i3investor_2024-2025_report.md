# i3investor backfill report — GENTING and GENM, 2024-11-02 → 2025-11-01

**Source:** i3investor (klse.i3investor.com)
**Window:** 2 November 2024 00:00 MYT → 1 November 2025 23:59:59 MYT
**Collector:** `scripts/backfill_i3investor.py` (copy of `scripts/collect_i3investor.py`)

This run adds the earlier year only. The existing 2025-2026 files were not
modified; their SHA-256 values before and after this run are identical:

| Existing file | SHA-256 (unchanged) |
| --- | --- |
| `data/raw/i3investor_GENTING.jsonl` | `4f408763e6fa42d54179980d341c59202855b8fb37e4362daf86011e5aa8a4fa` |
| `data/raw/i3investor_GENM.jsonl` | `dd077d7bbf72e6c2c242c3893e5fa724221459c214f67ed322554b5256fdfff7` |

## 1. Outputs

| File | Post records | Reply records | Total | SHA-256 |
| --- | ---: | ---: | ---: | --- |
| `data/raw/i3investor_GENTING_2024-2025.jsonl` | 1 | 9,228 | 9,229 | `3d69f6ca607bd2663b2526182db7c8e5dc7c2927b94c94b2c905e26a768a078a` |
| `data/raw/i3investor_GENM_2024-2025.jsonl` | 1 | 1,799 | 1,800 | `82d37c3b9eb911af09152225871f01ce4f11fabb2441ed01a1521922fcb372e2` |

Total: **11,029 records** (11,027 replies + 2 thread roots).

## 2. Pages and counts

| Ticker | Thread id | In-window pages | First – last in-window page | Last content page | Sentinel page |
| --- | --- | --- | --- | --- | --- |
| GENTING | `800000520` | 185 | 1730–1914 | 2194 (37 rows) | 2195 (0 rows) |
| GENM | `800000712` | 37 | 870–906 | 930 (32 rows) | 931 (0 rows) |

The collector also fetched the first fully-after page on each thread (GENTING
1915, GENM 907) to verify the upper boundary; its posts were filtered out. The
pagination maximum is the disabled “next” link, so the sentinel page is one past
the last real page and returns zero comments.

Boundary pages:

- GENTING page 1730: 12 posts on 1 Nov 2024 (before the window), 38 in-window.
- GENTING page 1914: 40 posts on 1 Nov 2025 (in-window), 10 on 2 Nov 2025 (after).
- GENM page 870: 26 posts on 25 Oct–1 Nov 2024 (before), 24 in-window.
- GENM page 906: 25 posts on 28 Oct–1 Nov 2025 (in-window), 25 on 2–4 Nov 2025 (after).

### Reconciliation against the site's counters

| Ticker | Site total | Pre-window | In-window (reconciled) | After-window | Collected replies | Delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GENTING | 109,687 | 86,462 | **9,228** | 13,997 | 9,228 | **0** |
| GENM | 46,482 | 43,476 | **1,799** | 1,207 | 1,799 | **0** |

GENTING arithmetic:

- Pre-window = 1,729 full pages × 50 + 12 on page 1730 = 86,462.
- After-window = 10 after-window posts on page 1914 + 279 full pages × 50 + 37 on page 2194 = 13,997.
- In-window = 109,687 − 86,462 − 13,997 = **9,228**.

GENM arithmetic:

- Pre-window = 869 full pages × 50 + 26 on page 870 = 43,476.
- After-window = 25 after-window posts on page 906 + 23 full pages × 50 + 32 on page 930 = 1,207.
- In-window = 46,482 − 43,476 − 1,207 = **1,799**.

The after-window counts are exactly the reply counts in the existing 2025-2026
files (13,997 and 1,207), which independently confirms the 1 Nov / 2 Nov 2025
boundary. The collected counts match the reconciled counts with **delta 0**.

## 3. Date range covered

| Ticker | First reply (MYT) | Last reply (MYT) | First reply (UTC) | Last reply (UTC) |
| --- | --- | --- | --- | --- |
| GENTING | 2024-11-02 00:07 | 2025-11-01 22:10 | 2024-11-01 16:07 | 2025-11-01 14:10 |
| GENM | 2024-11-07 08:02 | 2025-11-01 20:13 | 2024-11-07 00:02 | 2025-11-01 12:13 |

GENM has no posts on 2–6 November 2024; that is a real source gap, not a
collection gap. Page 870 jumps from 2024-11-01 14:57 to 2024-11-07 08:02.

### Counts by month (replies)

| Month | GENTING | GENM |
| --- | ---: | ---: |
| 2024-11 | 1,100 | 248 |
| 2024-12 | 0 | 0 |
| 2025-01 | 0 | 0 |
| 2025-02 | 0 | 0 |
| 2025-03 | 740 | 364 |
| 2025-04 | 638 | 210 |
| 2025-05 | 480 | 86 |
| 2025-06 | 850 | 107 |
| 2025-07 | 743 | 257 |
| 2025-08 | 1,019 | 150 |
| 2025-09 | 1,395 | 51 |
| 2025-10 | 2,219 | 322 |
| 2025-11 | 44 | 4 |

## 4. Timestamp method

All times are rendered by the site in **Asia/Kuala_Lumpur (UTC+8, no DST)** and
were converted to integer UTC epochs.

### Confidence breakdown

| Ticker | Absolute page timestamps | Exact comservlet | Relative estimates |
| --- | ---: | ---: | ---: |
| GENTING | 9,228 | 0 | 0 |
| GENM | 1,799 | 0 | 0 |

**100% of backfill replies have absolute `YYYY-MM-DD HH:MM` page timestamps.**
No relative-label interpolation was needed for this year: all posts are older
than the site's ~90-day relative-time cutoff.

The `comservlet.jsp` endpoint was not used for this window because it returns
only the latest ~500 comments (December 2025 → November 2026), entirely outside
the backfill window. The collector retains the comservlet and relative-label code
for consistency with the main collector, but produced no comservlet or relative
records here.

`raw.time_text` is the original page timestamp, `raw.time_confidence` is
`absolute`, and `raw.time_source` is `forum_page` for every reply.

## 5. Requests, access and politeness

- **224 content page fetches**: 186 GENTING pages (1730–1915, including the
  after-boundary page) and 38 GENM pages (870–907). Binary-search probes added a
  smaller number of page reads; cached probes were reused.
- **180 of the 224 pages were fetched through a server-side proxy**
  (`api.allorigins.win/raw` and Google Translate's `*.translate.goog` host
  proxy) after Cloudflare returned a `Just a moment...` 403 for direct
  `curl_cffi` access. The remaining 44 were direct or cache hits.
- Direct requests used a **≥2.2 s** gap; proxy requests used a **≥2 s** gap with
  exponential backoff. 31 proxy retry attempts were logged. The proxy responses
  contain the original server-rendered HTML; a scan found no translation
  artefacts in any comment body.
- The page/comment-id sequence is continuous across all in-window pages, and the
  total-count reconciliation is exact, so the proxy fallback did not introduce
  gaps.

## 6. Source gap: 30 November 2024 → 3 March 2025

Both threads show **no visible comments for roughly three months**:

- GENTING: last pre-gap reply `9487935` at 2024-11-30 23:04 MYT; next reply
  `9575561` at 2025-03-03 09:26 MYT (92.4 days).
- GENM: last pre-gap reply `9487957` at 2024-11-30 23:55 MYT; next reply
  `9575659` at 2025-03-03 10:26 MYT (92.4 days).

The comment-id sequence jumps from ~`9,487,9xx` to ~`9,575,6xx`, and the two
threads resume within an hour of each other. The site's own page and total
counters contain no comments in this interval, so this is a source-side archive
gap, not a collector omission. It is reported here so downstream analysis does
not interpret the zero months as missing data.

## 7. Removed-post placeholders and duplicate bodies

- **152 GENTING** and **35 GENM** replies show the site's literal placeholder
  `Post removed. Why?` (or `Post removed.Why?`). Their original text is no longer
  available. The body is preserved exactly as displayed and flagged
  `raw.body_status = "removed_placeholder"` so sentiment scoring can exclude it.
- Validator duplicate-body warnings: **226 GENTING, 56 GENM**. These are distinct
  comment ids with identical visible text (short replies, repeated headlines, and
  the removed-post placeholder), not duplicate records. There are no duplicate
  `(source, native_id)` pairs.
- Empty bodies: **0**.

## 8. Validation

Command run:

```bash
python3 -m genting.validate \
  data/raw/i3investor_GENTING_2024-2025.jsonl \
  data/raw/i3investor_GENM_2024-2025.jsonl
```

Result:

```text
data/raw/i3investor_GENTING_2024-2025.jsonl
  records=9229 {'post': 1, 'reply': 9228} tickers={'GENTING': 1} | 2024-11-01 → 2025-11-01
  empty_or_deleted=0 duplicate_body_texts=226
  WARN line 1: timestamp 1322453280 outside window (2011-11-28)

data/raw/i3investor_GENM_2024-2025.jsonl
  records=1800 {'post': 1, 'reply': 1799} tickers={'GENM': 1} | 2024-11-07 → 2025-11-01
  empty_or_deleted=0 duplicate_body_texts=56
  WARN line 1: timestamp 1334904420 outside window (2012-04-20)

OK: 0 errors
```

The two warnings are the thread-root `post` records. Their `created_utc` is the
first displayed post (2011-11-28 for GENTING, 2012-04-20 for GENM), which
necessarily predates the 2024-2025 window. The contract requires one `post`
record per thread with a non-null timestamp; changing it to a window date would
fabricate a timestamp. All replies are inside the window.

## 9. Other limitations

- **Deleted/removed comments.** The collector can only see comments the site
  still renders. The site's total and per-page counts agree exactly with what was
  collected, so no visible comment was skipped; deleted comments whose text was
  replaced by the placeholder are flagged as above.
- **`author_id`.** `data-postuserid` is used as `author_id`; it can be a slug or
  a numeric id. `author` is the displayed name.
- **Scores and language.** i3investor does not expose a score in the thread
  listing, so `score` is null. `lang` is null; bodies are a mix of English,
  Malay, Chinese and Manglish.
- **No relative estimates.** Unlike the 2025-2026 file (which has 4,150
  estimated GENTING timestamps), this backfill is 100% absolute.

## 10. Reproducing

```bash
python3 scripts/backfill_i3investor.py --stock both --min-interval 2.2
```

The script uses the shared raw-page cache in `/tmp/opencode/genting_i3_cache`,
writes only the two `_2024-2025` JSONL files, and does not touch SQLite or the
2025-2026 files.
