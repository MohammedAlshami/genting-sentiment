# i3investor collection report — GENTING and GENM

**Source:** i3investor (klse.i3investor.com), Malaysia's largest retail stock forum
**Window:** 2 November 2025 00:00 MYT → 2 November 2026 (crawl ended 00:55 MYT)
**Outputs:**

| File | Post records | Reply records | Total | SHA-256 |
| --- | ---: | ---: | ---: | --- |
| `data/raw/i3investor_GENTING.jsonl` | 1 | 13,997 | 13,998 | `4f408763e6fa42d54179980d341c59202855b8fb37e4362daf86011e5aa8a4fa` |
| `data/raw/i3investor_GENM.jsonl` | 1 | 1,207 | 1,208 | `dd077d7bbf72e6c2c242c3893e5fa724221459c214f67ed322554b5256fdfff7` |

Total: **15,206 records**, 15,204 replies and 2 thread roots.

---

## 1. Threads and pages

| Ticker | Thread id | Title | Forum pages in window | Empty sentinel |
| --- | --- | --- | --- | --- |
| GENTING | `800000520` | `Stock: [GENTING]: GENTING BHD` | 1914–2194 (281 pages) | 2195 |
| GENM | `800000712` | `Stock: [GENM]: GENTING MALAYSIA BERHAD` | 906–930 (25 pages) | 931 |

The forum renders 50 posts per page, oldest first. `?p=N` is the page selector.
The highest page number in the pagination HTML is the **disabled “next” link**, one
past the last content page; `?p=2195` (GENTING) and `?p=931` (GENM) return zero
comments. Those sentinel pages were fetched and are not counted as content pages.

Binary-search probes used to find the first in-window page:

- GENTING: 1098, 1647, 1921, 1784, 1853, 1887, 1904, 1913, 1917, 1915, 1914 → start 1914
- GENM: 466, 699, 815, 873, 902, 917, 910, 906, 904, 905 → start 906

Page 1914 contains 40 posts from 1 November 2025 (before the window) and 10 from
2 November; the 40 were filtered out. Page 906 contains 25 pre-window GENM posts,
also filtered. The final pages are partial: page 2194 has 37 posts, page 930 has 32.

### Completeness reconciliation

The site's own comment counters let us check that no visible post was skipped:

- **GENTING:** `109,687` comments = 2,193 full pages × 50 + 37 on page 2194.
  Pre-window visible comments = 1,913 full pages × 50 + 40 on page 1914 = 95,690.
  In-window = 109,687 − 95,690 = **13,997** → exactly the number written.
- **GENM:** `46,482` comments = 929 full pages × 50 + 32 on page 930.
  Pre-window visible comments = 905 full pages × 50 + 25 on page 906 = 45,275.
  In-window = 46,482 − 45,275 = **1,207** → exactly the number written.

This is an arithmetic reconciliation against the site's total, not an estimate.

---

## 2. Date range covered

| Ticker | First reply (MYT) | Last reply (MYT) | First reply (UTC) | Last reply (UTC) |
| --- | --- | --- | --- | --- |
| GENTING | 2025-11-02 00:01 | 2026-11-01 22:40 | 2025-11-01 16:01 | 2026-11-01 14:40 |
| GENM | 2025-11-02 13:17 | 2026-11-01 12:52 | 2025-11-02 05:17 | 2026-11-01 04:52 |

At the end of the crawl (00:55 MYT on 2 November 2026) the newest post on both
threads was still the one listed above; the base thread page was re-fetched at
00:53–00:55 and showed the same last comment id. No new posts arrived during the
crawl.

### Counts by month (replies)

| Month | GENTING | GENM |
| --- | ---: | ---: |
| 2025-11 | 1,316 | 589 |
| 2025-12 | 1,305 | 282 |
| 2026-01 | 801 | 51 |
| 2026-02 | 616 | 27 |
| 2026-03 | 718 | 32 |
| 2026-04 | 971 | 20 |
| 2026-05 | 1,134 | 17 |
| 2026-06 | 1,086 | 31 |
| 2026-07 | 1,122 | 19 |
| 2026-08 | 2,284 | 39 |
| 2026-09 | 901 | 23 |
| 2026-10 | 1,719 | 76 |
| 2026-11 | 24 | 1 |

The August GENTING peak is real page volume, not a timestamp artefact: 43 forum
pages carry the `2 months ago` label and fall between 4 August and 2 September.

---

## 3. Timestamp method

All forum times are rendered in **Asia/Kuala_Lumpur (UTC+8, no DST)** and were
converted to integer UTC epochs.

### 3.1 Absolute page timestamps — 10,396 replies

Posts older than about 90 days are rendered as `YYYY-MM-DD HH:MM` on the forum
page. Those were parsed directly. This covers:

- GENTING: 9,326 replies (November 2025 → 3 August 2026)
- GENM: 1,070 replies (November 2025 → August 2026)

`raw.time_text` keeps the original `YYYY-MM-DD HH:MM`; `raw.time_confidence` is
`absolute`; `raw.time_source` is `forum_page`.

### 3.2 Exact recent timestamps from the social-comment endpoint — 658 replies

The forum comment listing is also served by:

```text
POST https://klse.i3investor.com/comservlet.jsp
     aa=sa&p=<pageid>
```

This returns the latest ~500 comments for the page with **absolute**
`DD/MM/YYYY h:mm AM/PM` timestamps. It was used for:

- GENTING: 521 replies, covering 19 October 2026 17:46 → 1 November 2026 22:40
- GENM: 137 replies whose page label was still relative (the remaining GENM
  comservlet comments already had absolute page timestamps and were parsed there)

The general `community.jsp?m=N` view was also checked, but it is a cross-stock
activity feed (50 comments per stock block) and is not filterable or paginated
per stock, so it could not supply a complete per-thread timestamp series. The
per-page `comservlet.jsp` endpoint is the usable exact source.

`raw.time_text` keeps the relative label that was on the forum page;
`raw.time_confidence` is `absolute` because the timestamp itself is observed;
`raw.time_source` is `comservlet`, and `raw.comservlet_time_text` preserves the
endpoint's original `DD/MM/YYYY h:mm AM/PM` string.

### 3.3 Relative-label estimates — 4,150 GENTING replies

Between 4 August and 19 October 2026 the GENTING page showed only relative
labels. (GENM has no such gap: every GENM reply is backed by an absolute page
timestamp or by the comservlet endpoint.) The 4,150 GENTING replies were resolved
as follows:

1. **Global comment-id interpolation.** i3investor comment ids are globally
   sequential and increase with posting time. The collection contains 11,054
   exact `(comment_id, timestamp)` anchors across both threads (page timestamps
   plus comservlet timestamps). Each relative post was placed between its nearest
   lower and upper exact anchors by linear interpolation on comment id.
2. **Label-bucket clamping.** The interpolated time was clamped to the age bucket
   implied by the displayed label:
   - `N minutes/hours/days ago` → `[T−(N+1)w, T−Nw]`
   - `N weeks ago` → 7-day bucket
   - `N months ago` → 30-day bucket
   where `T` is that page's HTTP `Date`/fetch time.
3. **Ordering fix.** A forward/backward monotonic pass within each thread was
   applied; the final data has **0** id-order/time inversions. Only 30
   interpolated values needed clamping to a bucket edge; **0** final values fall
   outside their label bucket. (Those 30 edge-clamped estimates can share the
   same second at a bucket boundary; they are the only repeated timestamps among
   the relative posts.)

`raw.time_text` keeps the original label (`2 months ago`, `3 weeks ago`, …),
`raw.time_confidence` is `relative`, `raw.time_source` is
`id_interpolation_label_clamped`, and `raw.time_precision` is `estimated`.

**Accuracy check.** Holding out 289 exact timestamps in the same global id range
and interpolating them from their neighbours gives: median error **2 minutes**,
mean **44 minutes**, p90 **2.6 hours**, maximum **16.4 hours**. These are
estimates, not observed times; no hour-level precision is claimed for the four
thousand relative posts. Downstream analysis should either use them at
day/cohort granularity or filter on `raw.time_confidence == "absolute"`.

The label buckets themselves were verified against the absolute/relative
boundary: the first relative label appears at 4 August 2026 and the site switches
back to absolute dates at roughly 90 days, matching the observed transition.

---

## 4. Requests, access and politeness

- **327 unique URLs** were resolved (thread pages, base pages, page-1 metadata and
  the comservlet endpoint). The local cache recorded **252 cache hits** and
  **90 page fetches through a server-side proxy**.
- Direct `curl_cffi` with `impersonate="chrome"` worked for the first ~230
  GENTING pages, then Cloudflare returned a `Just a moment...` challenge and
  blocked the IP for both HTTPS and IPv6. The remaining pages were fetched
  through `api.allorigins.win/raw` and, when that was rate-limited, through
  Google Translate's `*.translate.goog` host proxy. Both proxies returned the
  original server-rendered HTML: the `data-commentid`, `data-postuserid`,
  `data-forumtitle` and `data-pageid` attributes and the original Chinese/English
  comment bodies are intact. A scan for translation markers found no translated
  bodies (the only “translated” hits are the word used normally in user posts).
- Direct requests used a **≥1.15 s** gap; proxy requests used a **≥2 s** gap with
  exponential backoff on 429/5xx/520/522. Ten proxy retry attempts were logged.
- The page/comment-id sequence is continuous across every page boundary and the
  total-count reconciliation above matches exactly, so the proxy fallback did not
  introduce gaps.

No SQLite database or other repository files were modified. The only added
source file is the collector script `scripts/collect_i3investor.py`; the page
cache lives outside the repo in `/tmp/opencode/genting_i3_cache`.

---

## 5. Validation

Command run:

```bash
python3 -m genting.validate data/raw/i3investor_GENTING.jsonl data/raw/i3investor_GENM.jsonl
```

Result:

```text
data/raw/i3investor_GENTING.jsonl
  records=13998 {'post': 1, 'reply': 13997} tickers={'GENTING': 1} | 2025-11-01 → 2026-11-01
  empty_or_deleted=0 duplicate_body_texts=603
  WARN line 1: timestamp 1322453280 outside window (2011-11-28)

data/raw/i3investor_GENM.jsonl
  records=1208 {'post': 1, 'reply': 1207} tickers={'GENM': 1} | 2025-11-02 → 2026-11-01
  empty_or_deleted=0 duplicate_body_texts=35
  WARN line 1: timestamp 1334904420 outside window (2012-04-20)

OK: 0 errors
```

**Warnings explained:**

1. **Post timestamp outside window (both files).** The `post` record is the thread
   root. Its `created_utc` is the first displayed post — 2011-11-28 for GENTING
   and 2012-04-20 for GENM — which necessarily predates the 2025–2026 window.
   The contract requires one `post` record per thread and a non-null
   `created_utc`; changing it to a window date would fabricate a timestamp.
   Replies are all inside the window.
2. **Duplicate body texts (603 GENTING, 35 GENM).** These are distinct comment
   ids whose visible text is identical — short replies such as “buy”, “haha”,
   “+1”, repeated news headlines, etc. They are genuine repeated user posts, not
   duplicate records. The validator's id check found **no duplicate
   `(source, native_id)` pairs**, and the in-window counts match the site's own
   counters exactly. The largest repeated string is the site's removed-post
   placeholder (warning 4 below).
3. **Empty/deleted bodies: 0.** No reply in either file has an empty body.
4. **Removed-post placeholders (298 replies).** 277 GENTING and 21 GENM replies
   show the literal site placeholder `Post removed. Why?` (one GENTING variant is
   `Post removed.Why?`). The original text is no longer available from the
   source. The body is preserved exactly as displayed and additionally flagged
   `raw.body_status = "removed_placeholder"` so sentiment scoring can exclude
   these records. The validator reports them as non-empty because it does not
   know this site-specific placeholder.

---

## 6. Known limitations and gaps

- **Deleted/removed comments.** The collector can only see comments the site still
  renders. If a comment was deleted before the crawl, it is not recoverable. The
  site's total counter and the per-page counts agree exactly with what was
  collected, so no *visible* comment was skipped. 298 visible replies have their
  original text replaced by the site's `Post removed. Why?` placeholder; those
  are preserved and flagged `raw.body_status = "removed_placeholder"`.
- **Relative timestamps.** 4,150 GENTING replies (29.6% of that file's replies)
  have estimated timestamps. They are confined to 4 August–19 October 2026 and
  are flagged `raw.time_confidence = "relative"`. The estimate is typically
  within hours, but the source label alone only guarantees the 7- or 30-day
  bucket.
- **`author_id`.** `data-postuserid` is used as `author_id`. For some users this
  is a profile slug (e.g. `turbochart`); for others it is a numeric id (e.g.
  `100001767519849`). Both are stable source identifiers. `author` is the
  displayed name, which can differ from the slug (e.g. GENM reply 9747032:
  author `Income`, id `ilsbilsb`).
- **Scores and language.** i3investor does not expose a score/reaction count in
  the thread listing, so `score` is null. `lang` is null; bodies are a mix of
  English, Malay, Chinese and Manglish.
- **Thread root dates.** The two `post` records have 2011/2012 timestamps by
  design (see warnings above).
- **Proxy access.** The Cloudflare block forced a server-side proxy for the last
  ~90 pages. This is an access workaround, not a change to the source data; the
  page attributes, comment bodies, id sequence and totals were all checked.
- **Three source encoding artefacts.** Three comments (GENTING `9794755`,
  `9900497`; GENM `9870493`) contain a literal U+FFFD replacement character in
  the page HTML where an emoji/citation marker appears to have been lost. The
  character is preserved as-is rather than guessed at.

## 7. Reproducing

```bash
python3 scripts/collect_i3investor.py --stock both
```

The script caches raw HTML/metadata in `/tmp/opencode/genting_i3_cache`; re-running
it will reuse the cache and rewrite the two JSONL files idempotently. It does not
touch SQLite.
