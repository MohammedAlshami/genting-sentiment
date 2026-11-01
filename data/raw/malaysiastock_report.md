# MalaysiaStock.Biz forum — collection report

**Source:** `malaysiastock`
**Window:** 2025-11-02 00:00 MYT → 2026-11-02 23:59 MYT

## Result

**No `data/raw/malaysiastock.jsonl` was produced: there is no Genting/GENM
post in the window.** The forum's Genting threads exist but have been dormant
since 2024.

## What was checked

- `https://www.malaysiastock.biz/Forum/Main.aspx` (Latest Discussion), pages
  1–43. These pages contain 1,190 unique topics.
- `https://www.malaysiastock.biz/Forum/Latest-Topic.aspx`.
- Every topic title in the 1,190-topic listing was scanned for
  `genting`, `genm`, `3182` or `4715`. Three stock-specific threads were found:

| Topic id | Title | Pages | Posts | Last post (MYT) | In window? |
|---|---|---:|---:|---|---|
| 119 | GENTING (3182) : GENTING BERHAD | 3 | 46 | 2024-07-07 14:59 | No |
| 166 | GENM (4715) : GENTING MALAYSIA BERHAD | 2 | 22 | 2024-06-01 09:17 | No |
| 23836 | GENM (4715) - 技术分析 | 1 | 1 | 2020-06-21 03:32 | No |

- All pages of topics 119 and 166 and the single page of 23836 were fetched to
  confirm the last-post dates; the pages are chronological, so no earlier page
  can contain a later post.
- No other Genting/GENM-titled thread exists in the 1,190-topic listing.

## Access notes

- The forum pages were readable as a guest. A site-wide banner says public
  content is being restricted to subscribers, but the Latest Discussion list and
  the topic pages above returned HTTP 200 without login.
- Timestamps on the topic pages are Malaysian time in the form
  `DD Mon YYYY, HH:MM AM/PM`. No records were written, so no timestamps were
  converted.
- No JSONL file is written for this source; an empty file would create a false
  impression that the source was collected but returned nothing.

## Conclusion

MalaysiaStock.Biz has no Genting discussion in the collection window. The
relevant stock topics stopped in mid-2024, so this source contributes zero
records to the dataset.
