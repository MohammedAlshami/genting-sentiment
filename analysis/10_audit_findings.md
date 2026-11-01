# Audit findings — what the data actually says

## Coverage

- **75,641 replies** across 11 sources, 2 Nov 2024 → 1 Nov 2026.
- **6,360 posts**, **386 full news articles**, **980 daily price bars**, **3,499 pageview days**.
- News is **year two only** (3 Nov 2025 → 29 Oct 2026). Year one is being backfilled.
- i3investor has a source-side gap from **30 Nov 2024 → 3 Mar 2025**.
- YouTube timestamps are month-level estimates; Facebook public pages are partial.
- Company documents: 482 PDFs, filings 1998–2026, quarterly reports 2005–2026.

## Price

- **GENTING**: 3.95 → 1.54, **−61.0%**. Peak 4.02 (6 Nov 2024), trough 1.35 (22 Oct 2026).
- **GENM**: 2.25 → 1.25, **−44.4%**. Peak 2.44 (17 Feb 2025), trough 1.12 (23 Oct 2026).

## Event reactions

| Event | GENTING 5d / 20d | GENM 5d / 20d |
|---|---:|---:|
| RM2.35 offer (13 Oct 2025) | +17.8% / +21.0% | +9.4% / +9.8% |
| Offer fails (1 Dec 2025) | −0.6% / −8.3% | −6.4% / −12.3% |
| NY licence (16 Dec 2025) | 0.0% / −2.0% | +1.5% / +1.0% |
| NY casino opens (1 May 2026) | −2.0% / −10.5% | +0.5% / −3.0% |
| Rights issue (9 Oct 2026) | −21.2% / −16.3% | −12.3% / −14.4% |
| 22.87% fall (12 Oct 2026) | −22.9% / −18.1% | −14.8% / −16.1% |

## Sentiment — the surprise

A language-aware first pass (VADER for English; curated Malay/Chinese lexicons) scored **72,702** replies. English 42,484, Chinese 27,914, Malay 2,304.

- Mean sentiment was **never negative** on a monthly basis in the two-year window.
- It **peaked around July 2025 at +0.187**, then eroded: Oct 2025 +0.155, Dec 2025 +0.130, Aug 2026 +0.127, Sep 2026 +0.068, **Oct 2026 +0.051**.
- **Bearish share** rose from ~16% in Dec 2025 to **27.5% in Oct 2026** — the crowd did not turn, it lost conviction.
- Same-month correlation with price: **0.50 (GENTING), 0.62 (GENM)**.
- Sentiment change → next-month return: **0.15 (GENTING), 0.32 (GENM)**.

**Conclusion: sentiment followed the price more than it led it.** The current website line “the mood broke first” is not supported by the monthly data. The honest line is: **the crowd stayed positive too long.**

Caveat: this is a lexicon-based first pass. Negation and sarcasm are only partially handled. It is directionally useful, not a trained model.

## Topic intensity

- **Privatisation**: 9.1% of replies in Oct 2025, 14.6% in Nov 2025, 6.7% in Dec 2025.
- **Debt**: 8.3% in Sep 2026, 6.4% in Aug 2026, 6.0% in Oct 2026.
- **Rights issue**: 5.3% in Oct 2026.
- **New York**: 11.7% in Dec 2025, 10.3% Jan 2026, 10.2% May 2026, 12.0% Aug 2026.
- **Management/ownership**: 7.2% Nov 2025, 7.6% Jun 2026.

## Financials

- GENTING quarterly revenue ~RM6.5–7.7b; net profit swung from RM277m (1Q25) to **−RM194m (4Q25)**, then RM217m / RM198m.
- GENM net profit: RM123m (4Q25), **−RM25m (1Q26)**, RM27m (2Q26).
- Total debt: GENTING **RM39.0b → 45.3b**; GENM **RM12.7b → 15.7b**.
- Annual interest bill ~RM2.1b; 2027 maturities US$617.5m + RM2.35b.

## Fixed during the audit

- Quarterly financials were being scaled twice (2025 rows off by 1,000×). Fixed and re-imported; values now match the PDFs.

## Gaps that matter for the report

1. News year one (2 Nov 2024 → 1 Nov 2025) — collector running.
2. YouTube exact timestamps — need a free YouTube Data API key.
3. Trained multilingual sentiment — current pass is lexicon-based.
4. X/RED/Facebook groups remain inaccessible.
