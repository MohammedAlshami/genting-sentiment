# Collector output contract

Every collector writes **JSONL** to `data/raw/<source>_<channel>.jsonl`, one JSON object
per line. Do not write to the SQLite database directly — the orchestrator imports and
validates after collection.

Scope: **Malaysian Genting** — Genting Berhad (`GENTING`, Bursa 3182) and Genting
Malaysia (`GENM`, Bursa 4715). Window: **2 Nov 2024 → 2 Nov 2026** inclusive.

## Record types

### post

```json
{
  "record_type": "post",
  "source": "i3investor",
  "channel": "GENM",
  "native_id": "800000712",
  "ticker": "GENM",
  "title": "Stock: [GENM]: GENTING MALAYSIA BERHAD",
  "author": null,
  "author_id": null,
  "created_utc": 1730000000,
  "url": "https://klse.i3investor.com/web/forum/forum-thread/800000712",
  "body": "optional opening text",
  "score": null,
  "num_comments": 46482,
  "lang": null,
  "raw": {}
}
```

- `source` — stable snake_case id: `i3investor`, `moomoo_my`, `klse_screener`, `lowyat`,
  `malaysiastock`, `reddit`, `news_<publisher>`.
- `channel` — where it lives: subreddit, stock code, forum board, publisher.
- `native_id` — id used by the source; must be stable across re-runs.
- `ticker` — `GENTING`, `GENM`, or `UNKNOWN`.
- `created_utc` — **integer epoch seconds, UTC**. Mandatory. If the source only shows a
  relative time ("2 weeks ago"), resolve it to the most defensible absolute timestamp and
  put the original string in `raw.time_text`; never invent precision you don't have.

### reply

```json
{
  "record_type": "reply",
  "source": "i3investor",
  "channel": "GENM",
  "native_id": "9960136",
  "post_native_id": "800000712",
  "parent_native_id": null,
  "depth": 0,
  "author": "Loh Kok Wai W",
  "author_id": "100001767519849",
  "created_utc": 1730000000,
  "body": "yes....more investor sideway Malaysia Share Market...",
  "score": null,
  "url": "https://klse.i3investor.com/web/forum/forum-thread/800000712?p=930",
  "lang": null,
  "raw": {}
}
```

- `post_native_id` must match a `post.native_id` from the same source.
- `parent_native_id` is the native id of the replied-to reply, or null for top level.
- `depth` is 0 for top level.
- `body` is the raw text as shown, HTML stripped, entities decoded, whitespace normalised.

### article

```json
{
  "record_type": "article",
  "source": "news_theedge",
  "channel": "The Edge Malaysia",
  "url": "https://theedgemalaysia.com/node/822639",
  "title": "Cover Story: Debt repayment looms for Genting",
  "author": null,
  "published_utc": 1730000000,
  "body": "full article text...",
  "summary": null,
  "tickers": ["GENTING"],
  "lang": "en",
  "raw": {}
}
```

- `body` must be the **full article text**, not a teaser. If the article is paywalled and
  only a stub is available, set `body` to what is public and `raw.paywalled = true`.

## Hard requirements

1. **Completeness beats speed.** Every post/reply in the window, including replies to
   replies. Do not truncate a thread because it is long.
2. **Never fabricate.** Missing values are `null`, not guesses. Do not invent authors,
   timestamps or text.
3. **Idempotent.** Re-running a collector must not duplicate records. Deduplicate by
   `(source, native_id)`.
4. **Raw payloads.** Put the original API/HTML-derived object in `raw` so anything can be
   re-derived. Keep it JSON-serialisable and under ~20 KB per record.
5. **Politeness.** ≥1 second between requests; back off on 429/5xx. Use a browser-like
   User-Agent, and `curl_cffi` with `impersonate="chrome"` where Cloudflare blocks plain
   requests.
6. **Report.** Write `data/raw/<source>_report.md` with: pages/requests made, records
   written, date range covered, counts by ticker, known gaps, and how timestamps were
   derived.

## Validation

Run before declaring done:

```bash
python3 -m genting.validate data/raw/<file>.jsonl
```

Fix every error it reports. Warnings (empty/deleted bodies, missing scores) are acceptable
but must be explained in the report.
