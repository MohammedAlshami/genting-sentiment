# Genting sentiment — 10 years of Malaysian retail opinion

Public data + code behind **https://genting-sentiment.mshami2021.workers.dev**.

A ten-year study of what Malaysian retail investors said about **Genting Berhad (GENTING, Bursa 3182)** and **Genting Malaysia (GENM, Bursa 4715)**, compared with the share price. Scope is Malaysia only; Genting Singapore is excluded.

The website is the story. This repository is the evidence: every collector, every raw record, the SQLite database, the analysis tables, and the exact sentiment rubric used to score the replies.

## Dataset at a glance

| Item | Value |
|---|---:|
| Replies / comments | **217,451** |
| Full news articles | **864** |
| Company documents archived | **2,972** (482 PDFs) |
| Daily price bars | **2,459** GENTING / **2,458** GENM (2016-10-31 → 2026-10-30) |
| LLM-classified replies | **9,015** |
| Months with measured sentiment | **118 / 120** |
| Same-month sentiment / GENM correlation | **0.22** |

Sources: i3investor, KLSE Screener, Moomoo Malaysia, YouTube, TikTok, Lowyat.NET, Cari, Reddit, Facebook public pages, Instagram, LinkedIn, i3 blogs, TradingView, and Malaysian news outlets.

Full per-source counts, date ranges and usability notes: **[DATA_INVENTORY.md](DATA_INVENTORY.md)**.

## What is in the repository

```
analysis/                 derived CSVs and reports (prices, events, topics, sentiment)
data/raw/                 collector JSONL, one record per line
data/llm_sentiment/       per-batch LLM classification audit files
data/genting.sql.gz       compressed SQLite dump — the full database
genting/                  Python package: schema, importer, validator, price loader
scripts/                  collectors + LLM classifier + site data builder
site/                     TanStack Start / React site (source only)
docs/                     collector contract and notes
```

Raw data is JSONL. The importer validates every record before inserting it, so malformed or out-of-scope rows cannot silently land in SQLite.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# restore the database (25 MB compressed, ~165 MB on disk)
gunzip -c data/genting.sql.gz | sqlite3 data/genting.db

# coverage report
python3 -m genting.stats

# re-import raw JSONL from scratch (optional)
python3 -m genting.import_raw
```

Website:

```bash
cd site
npm install
npm run dev        # http://localhost:3000
npm run build
```

Regenerate the website's 10-year series from the database:

```bash
python3 scripts/build_site_history.py
```

## Sentiment method

Every reply is scored with the rubric in [`scripts/llm_classify.py`](scripts/llm_classify.py), using DeepSeek V4.1 Flash through the OpenCode Go subscription.

The model assigns an integer **level 0–10**:

| Level | Meaning |
|---|---|
| 0 | Total collapse / zero |
| 1–2 | Very strong / strong bearish |
| 3–4 | Moderate / mild bearish |
| 5 | Neutral — no directional view |
| 6 | Mild bullish (hold, cheap) |
| 7 | Moderate bullish (buy/add, undervalued) |
| 8 | Strong bullish (catalyst, target) |
| 9–10 | Very strong / certain rally |

Stored score = `level / 10`, so **0 = maximally bearish, 0.5 = neutral, 1 = maximally bullish**. Labels: 0–4 bearish, 5 neutral, 6–10 bullish.

Each request includes the ticker, date, thread title, parent comment and the comment itself, so short replies (“agree”, “sell”, “2.35 lowball”) are scored in context. Full rubric, special cases and confidence scale are in the prompt.

The site uses a **stratified sample of 9,015 replies** across every month and source. The data appendix on the website shows the sample size `n` for each month; months without a sample are interpolated and marked `*`. The full 217k corpus has not been LLM-scored yet.

## Price and event data

- Daily OHLCV for 3182.KL and 4715.KL from Yahoo Finance, 2016-10-31 → 2026-10-30.
- Monthly closes in `analysis/02_prices_monthly_10y.csv`.
- Event reactions in `analysis/03_event_reactions.csv`.
- Corporate actions, ownership, financials and annual-report extracts in `data/genting.db`.

Key events used in the story:

| Date | Event |
|---|---|
| 13 Oct 2025 | Genting offers RM2.35/share for GENM |
| 1 Dec 2025 | Offer closes at 73.13% — below the 75% threshold |
| 16 Dec 2025 | Resorts World NYC licence awarded |
| 1 May 2026 | NYC casino opens |
| 9 Oct 2026 | RM1.25b rights issue |
| 12 Oct 2026 | GENTING falls 22.87% to RM1.45 |

## Database

`data/genting.db` (restore from `data/genting.sql.gz`):

| Table | Contents |
|---|---|
| `posts` | threads, videos, feed items |
| `replies` | comments and nested replies |
| `articles` | full news text |
| `prices` | daily OHLCV |
| `sentiment_llm` | LLM level, score, confidence, ticker, prompt version |
| `ownership`, `financials`, `company_actions` | company facts |
| `collection_runs` | audit log |

Every row keeps `raw_json` for reproducibility.

## Large files

The 482 company PDFs and their extracted text (848 MB) are attached to the **`data-v1` release** rather than committed to git:

**https://github.com/MohammedAlshami/genting-sentiment/releases/tag/data-v1**

The repository keeps the annual-report manifest, facts and index files needed to map them.

## Known gaps

- KLSE Screener’s public archive starts March 2018, so 2016–2018 has no KLSE records.
- The full i3investor 2016–2024 crawl is still proxy-limited; the cached partial (47,912 replies) is in the database and covers the window.
- YouTube comments use relative timestamps; `time_confidence="relative"` and the original interval are preserved.
- Facebook groups, X/Twitter search and Xiaohongshu are login-walled and not included.
- Full-corpus LLM scoring is incomplete by design; the site uses the sample and reports `n`.

## License

- Code: MIT.
- Derived analysis and aggregate series: CC BY 4.0.
- Raw posts and comments remain the property of their authors; they are reproduced here for research and criticism. Company filings are public disclosures.

Not investment advice.
