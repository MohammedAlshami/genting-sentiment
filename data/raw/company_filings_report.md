# Company filings & financials — collection report

**Scope:** Genting Berhad (`GENTING`, Bursa 3182) and Genting Malaysia Berhad (`GENM`,
Bursa 4715), 2 Nov 2024 → 2 Nov 2026.
**Collected:** 2 Nov 2026.
**Outputs:** `data/raw/company_filings.jsonl`, `data/raw/company_financials.csv`,
`data/raw/company_financials_annual.csv`, `data/raw/company_segments.csv`,
`data/raw/company_actions.jsonl`, `data/company_docs/`.


## Headline facts

- **GENTING FY2025:** revenue RM27,711.9m (FY2024: RM27,717.0m), adjusted EBITDA
  RM7,990.1m (RM8,781.8m), net profit RM1,023.8m (RM2,021.3m), loss attributable to
  shareholders RM11.6m, EPS -0.30 sen (22.93 sen), DPS 5.0 sen (11.0 sen). Net debt
  RM22,810.6m at end-2025 vs RM16,825.0m at end-2024.
- **GENM FY2025:** revenue RM11,884.3m (FY2024: RM10,911.8m), adjusted EBITDA
  RM3,297.6m (RM2,910.4m), net profit RM670.7m (RM162.1m), EPS 13.32 sen (4.43 sen),
  DPS 7.0 sen (10.0 sen). Net debt RM9,868.8m vs RM8,684.2m.
- **Latest quarter (2Q26):** GENTING revenue RM7,746.1m / net profit RM197.6m / net debt
  RM27,608.8m; GENM revenue RM3,853.3m / net profit RM27.0m / net debt RM13,029.1m.
- **Ownership:** GENT's stake in GENM rose from 49.36% at the 13 Oct 2025 offer
  announcement to 73.13% at the 1 Dec 2025 close and 73.867% by 2 Apr 2026.
- **Funding:** GENT raised RM3.0b of 1-year MTNs in Nov–Dec 2025 to part-fund the GENM
  take-over, then issued RM3.0b of 1–5 year MTNs via Genting Vista to redeem them; a
  RM1.25b rights issue was proposed in Oct 2026 but was not priced by the window end.
- **Growth:** GENM was awarded a downstate New York commercial casino licence on
  15 Dec 2025 and began full commercial casino operations at RWNYC on 28 Apr 2026.

## 1. Source and method

Bursa Malaysia's own announcement pages return HTTP 403 from this network. The primary
source is therefore the **KLSE Screener mirror** of Bursa announcements:

- listing: `https://www.klsescreener.com/v2/announcements/stock/<code>?category=&page=N`
  (30 items/page, reverse chronological)
- detail: `https://www.klsescreener.com/v2/announcements/view/<id>` — contains the full
  Bursa announcement body, the announcement-info table (date, category, reference number)
  and links to the original PDF attachments
- attachments: `https://disclosure.bursamalaysia.com/FileAccess/apbursaweb/download?...`
  (the Bursa disclosure host; PDFs download normally)

Requests used `curl_cffi` with `impersonate="chrome"`, ≥1.05 s between requests, and
exponential backoff on 429/5xx. The initial crawl made 20 listing-page requests and 560 detail-page requests
(580 requests in total); 115 announcement attachments and 4 annual reports were then downloaded. All
HTML and PDFs are cached under `/tmp/opencode/gent/cache` and `data/company_docs/`, so a
full re-run of the collector from cache completed with `requests=0`.

The collector is `scripts/collect_filings.py`; PDF download and text extraction are
`scripts/download_filing_pdfs.py` and `scripts/extract_company_docs.py`.

**i3investor cross-check.** `https://klse.i3investor.com/web/stock/announcement/3182`
(and `/4715`) were fetched and parsed. The page exposes only the latest **99** (3182) /
**96** (4715) announcements and ignores `?page=` / `?p=` pagination, so it cannot
enumerate the full two years. On every date where its list overlaps our data, our record
count is equal or larger (i3investor is a strict subset). It was therefore used only as a
sanity check, not as the enumeration source.

## 2. Announcement coverage

| Metric | Value |
| --- | ---: |
| Announcements in `company_filings.jsonl` | **563** |
| GENTING (3182) | 193 |
| GENM (4715) | 370 |
| First announcement date | 2024-11-25 |
| Last announcement date | 2026-10-26 |
| Announcements with PDF attachments | 85 |
| Attachment links captured / downloaded | 115 / 115 |
| Records with a non-empty body | 563 (100%) |
| Duplicate `native_id` | 0 |

No announcements were filed between 2 Nov 2024 and 24 Nov 2024 (first record is
25 Nov 2024); the window start is 2 Nov 2024, so this appears to be a genuine quiet
period rather than a pagination gap. The crawler walked back to April 2024 and stopped
only after passing the window start.

### Counts by category

| Category | GENTING | GENM |
| --- | ---: | ---: |
| Change in substantial shareholder interest (s.138) | 75 | 174 |
| Changes in director's interest (s.219) | 41 | 58 |
| General announcement (PLC) | 33 | 58 |
| Financial results | 8 | 8 |
| Dealings in listed securities (Chapter 14) | 3 | 40 |
| Document submission (annual report, circular) | 6 | 7 |
| Listing circular | 5 | 5 |
| General meeting (notice/outcome) | 4 | 4 |
| Board / committee changes (incl. principal officer) | 16 | 9 |
| Entitlement / book closure | 2 | 2 |
| Share buy-back (immediate + s.127 notice) | 0 | 4 |
| Take-over offer | 0 | 1 |
| **Total** | **193** | **370** |

`raw.normalized_type` adds a research-friendly label on top of the Bursa category:
substantial shareholder 249, director dealing 142, take-over 43, other 33, governance 25,
financial results 16, bond/MTN 15, dividend 8, AGM/EGM 8, listing circular 8, buy-back 6,
annual report 4, rights issue 3, litigation 3.

### Counts by month

| Month | GENTING | GENM | Total |
| --- | ---: | ---: | ---: |
| 2024-11 | 5 | 2 | 7 |
| 2024-12 | 1 | 1 | 2 |
| 2025-02 | 10 | 3 | 13 |
| 2025-03 | 60 | 2 | 62 |
| 2025-04 | 19 | 5 | 24 |
| 2025-05 | 1 | 3 | 4 |
| 2025-06 | 1 | 4 | 5 |
| 2025-07 | 1 | 1 | 2 |
| 2025-08 | 1 | 2 | 3 |
| 2025-09 | 0 | 1 | 1 |
| 2025-10 | 29 | 35 | 64 |
| 2025-11 | 8 | 217 | 225 |
| 2025-12 | 5 | 41 | 46 |
| 2026-02 | 7 | 3 | 10 |
| 2026-03 | 0 | 17 | 17 |
| 2026-04 | 12 | 14 | 26 |
| 2026-05 | 2 | 2 | 4 |
| 2026-06 | 1 | 7 | 8 |
| 2026-07 | 0 | 1 | 1 |
| 2026-08 | 1 | 2 | 3 |
| 2026-09 | 5 | 4 | 9 |
| 2026-10 | 24 | 3 | 27 |

The March 2025 GENTING burst (60 filings) and the October–December 2025 GENM burst
(293 filings) are predominantly substantial-shareholder and director-interest disclosures, including
the daily take-over acceptances. They are genuine repeat filings, not duplicates: every
record has a distinct Bursa reference number.

## 3. Date/time derivation

- `created_utc` is the Bursa **Date Announced** (from the detail page) combined with the
  wall-clock time shown on the listing page ("6:22 pm"), interpreted as
  **Asia/Kuala_Lumpur (UTC+8)** and converted to UTC epoch seconds.
- All 563 records have both a date and a time on the source page; none fell back to
  midnight.
- The date is authoritative from the detail page, not inferred from pagination. An
  earlier pass inferred years from the listing order; the final pass re-reads every
  detail page, so year boundaries (Jan→Dec) are exact.
- `raw.date_announced` preserves the original "26 Oct 2026" string and `raw.time_text`
  the original "6:22 pm" string.

## 4. Financial results and quarterly dataset

All 16 financial-results announcements in the window were found (8 per company), each
with two PDFs: the Bursa quarterly report and the results press release. Both were
downloaded to `data/company_docs/quarterly/<TICKER>/` and converted to `.txt`.

| Quarter | Period end | GENTING announcement | GENM announcement |
| --- | --- | --- | --- |
| 3Q24 | 2024-09-30 | 2024-11-28 | 2024-11-28 |
| 4Q24 | 2024-12-31 | 2025-02-27 | 2025-02-27 |
| 1Q25 | 2025-03-31 | 2025-05-29 | 2025-05-29 |
| 2Q25 | 2025-06-30 | 2025-08-28 | 2025-08-28 |
| 3Q25 | 2025-09-30 | 2025-11-27 | 2025-11-27 |
| 4Q25 | 2025-12-31 | 2026-02-26 | 2026-02-26 |
| 1Q26 | 2026-03-31 | 2026-05-21 | 2026-05-21 |
| 2Q26 | 2026-06-30 | 2026-08-20 | 2026-08-20 |
| 3Q26 | 2026-09-30 | **not announced by 2 Nov 2026** | **not announced by 2 Nov 2026** |

`company_financials.csv` contains the seven quarters **4Q24 → 2Q26** for each company
(14 rows). 3Q24 was extracted for completeness but excluded from the CSV because its
period end (30 Sep 2024) falls before the collection window. 3Q26 is a genuine gap: Bursa
requires the report within two months of quarter end, i.e. by 30 Nov 2026, after the
window closes.

CSV conventions:

- amounts in **RM million**; EPS and dividend in **sen per share**; `eps` is basic
  EPS attributable to equity holders as reported (it can diverge from `net_profit`,
  which includes non-controlling interests);
- `net_profit` = profit for the period, including non-controlling interests (not
  "attributable to equity holders");
- `total_debt` = long-term + short-term borrowings, **excluding lease liabilities**;
- `cash` = cash and cash equivalents (balance-sheet line);
- `net_debt` = `total_debt − cash`;
- `ebitda` = the company-reported **adjusted EBITDA** for the individual quarter, taken
  from the "Summary of Results" table in the press release (not a PBT+D&A calculation);
- `dividend` = dividend declared with that quarter's results (5.0/5.0 sen for GENTING
  4Q24/4Q25; 4.0/7.0 sen for GENM 4Q24/4Q25; 0.0 in other quarters). The FY2024 interim
  dividends were declared before the window (Aug 2024), so the quarterly column sums to
  the final dividend only; the FY2024 total DPS in the annual CSV (11.0 sen GENTING /
  10.0 sen GENM) includes that earlier interim;
- `source_url` is the direct PDF attachment URL for that quarter's report; the press
  release and page-level provenance are in `company_financials_provenance.csv`.

Anomaly worth flagging: GENTING 1Q25 EPS is **0.12 sen** although net profit is
RM277.6m, because only RM4.6m was attributable to equity holders and RM273.1m to
non-controlling interests. Both figures are in the Bursa summary table and the quarterly
report; the low EPS is real, not a parsing error. The same applies to GENTING 2Q26:
net profit RM197.6m but EPS -0.70 sen (loss attributable RM27.1m, NCI RM224.7m).

Rounding: GENTING's FY2025 annual report shows total borrowings of RM40,806.7m and net
debt of RM22,810.6m, while the 4Q25 quarterly report's components round to RM40,806.6m
and RM22,810.5m. The difference is RM0.1m of component rounding; each CSV row agrees
with its own source.

Each number was cross-checked against the Bursa summary table in the announcement body and
the press-release summary table, which print the same quarter in RM'000 / RM million; this caught the RM'000 → RM million change that GENTING and
GENM made in 1Q26 (earlier reports are in thousands).

`company_financials_annual.csv` holds FY2024 and FY2025 for both companies, sourced from
the annual reports (income statement and balance sheet) and the 4Q press releases
(adjusted EBITDA). `company_segments.csv` holds 105 quarterly segment-revenue rows
(10 segments per GENTING quarter, 5 per GENM quarter). GENM's leaf segments sum to group revenue within 0.1m rounding; GENTING's leaf segments
sum to group revenue plus the intra-plantation elimination that the press release reports
separately (e.g. RM211.2m in 4Q24).

## 5. Annual reports

| Company | Year | File | Pages | Text |
| --- | --- | --- | ---: | --- |
| GENTING | FY2024 | `GENTING_IAR2024.pdf` | 250 | `GENTING_IAR2024.txt` |
| GENTING | FY2025 | `GENTING_IAR2025.pdf` | 282 | `GENTING_IAR2025.txt` |
| GENM | FY2024 | `GENM_IAR2024.pdf` | 198 | `GENM_IAR2024.txt` |
| GENM | FY2025 | `GENM_IAR2025.pdf` | 208 | `GENM_IAR2025.txt` |

Downloaded from <https://www.genting.com/annual_reports> and
<https://www.gentingmalaysia.com/annual_reports>; the direct PDF URLs are in
`annual_facts.md` and the local copies are also in `data/company_docs/announcements/`
from the Bursa filings.

Text is page-delimited (`=== PAGE n ===`), with `<stem>.pages.json` (page count and
character offsets) and `<stem>.index.json` (pages where key statement headings occur).
`data/company_docs/annual_facts.md` summarises the income statement, balance sheet, cash
flow, segment results, borrowings maturity, dividend history, major shareholders,
directors and related-party notes, with PDF page references and source URLs.

Note: the FY2025 GENM substantial-shareholder register table (p194) is image-based and
did not extract as text. The 73.84% GENT stake is instead corroborated by the FY2025
review narrative (p12) and the Bursa substantial-shareholder announcements (73.798% on
4 Dec 2025, 73.867% by 2 Apr 2026).

## 6. Corporate actions (`company_actions.jsonl`) and other material disclosures

40 records covering:

- **Rights issue (GENTING, Oct 2026):** RM1,250m gross, renounceable, full subscription;
  RM800m debt repayment, RM429.5m working capital, RM20.5m expenses; 25–30% TERP
  discount intended; KHR/KHIL/DILKH undertakings for 45.10%; issue price, entitlement
  ratio and dilution **not fixed by 2 Nov 2026**; expected completion 1Q2027.
- **GENM take-over (Oct–Dec 2025):** RM2.35 cash per share for the 50.64% not held;
  unconditional 3 Nov 2025; closed 1 Dec 2025 at 73.13%; post-offer purchases to 73.798%
  (4 Dec 2025) and 73.867% (2 Apr 2026). This is the exercise often described as the
  "2025 GENM privatisation attempt"; legally it was a conditional voluntary take-over
  that lifted GENT's stake to ~73.8%, not a delisting or 100% privatisation.
- **Dividends:** four final single-tier dividends (GENTING 5.0 sen for FY2024 and FY2025;
  GENM 4.0 sen FY2024, 7.0 sen FY2025) with ex/payment dates.
- **Buy-backs:** GENTING and GENM annual mandate renewals; two actual GENM buy-backs in
  Sep/Oct 2026 (200,000 and 550,000 shares).
- **MTNs/bonds:** GENTING RMTN tranches 5–8 (RM900m + RM495m + RM255m + RM1,350m =
  RM3.0b), the RM5.0b Genting Vista programme, the RM3.0b Series 1 issuance that
  is to redeem the RMTN paper, GENM's RM75m MTN, the US$1.5b 4.25% 2027 note tender
  (US$882.462m accepted, US$617.538m outstanding), and the subordinated perpetual
  securities (Ba2/BB+, NC5.5 and NC10).
- **AGMs:** GENTING 57th (12 Jun 2025) and 58th (11 Jun 2026); GENM 45th (11 Jun 2025)
  and 46th (10 Jun 2026).
- **Acquisition:** GENM's purchase of the remaining 51% of Genting Empire Resorts LLC
  from Kien Huat Realty III for USD41.7m, completed 31 May 2025.
- **New York licence:** Genting New York LLC's bid was selected on 1 Dec 2025 and awarded a
  downstate commercial casino licence on 15 Dec 2025; RWNYC began full commercial casino
  operations on 28 Apr 2026.
- **Empire restructuring:** the Aug 2025 proposal to sell non-gaming assets for USD525m,
  buy land for USD201.3m and redeem USD300m notes did not proceed; Empire redeemed the
  USD300m 7.75% notes in full on 2 Jul 2026.
- **RWLV settlement:** the Nevada Gaming Control Board stipulation was approved by the
  Nevada Gaming Commission on 27 Mar 2025 (no monetary penalty stated).
- **Meizhou Wan handover:** the 2 x 393MW Phase I power plant was handed over on BOT
  expiry at 23:59 on 30 Jun 2025.
- **GENM litigation:** RAV Bahamas Ltd v Genting Americas Inc. in the US District Court,
  Southern District of Florida; updates on 25 Nov 2024, 7 Jul 2025 and 17 Sep 2025
  (dismissal granted 1 Jul 2025, amended complaint 29 Jul 2025, new motion to dismiss
  12 Sep 2025). No amount claimed or provision disclosed.

Where the announcement does not state a number (e.g. the principal amount of the
perpetual securities, the rights-issue price), the field is `null`; nothing was inferred.

Other material disclosure kept in the filings file (not promoted to an action):

- **Credit ratings** — no standalone corporate rating announcement was filed in the
  window. The only rating disclosure is the Ba2 (Moody's) / BB+ (Fitch) instrument rating
  on the April 2026 subordinated perpetual securities.

## 7. Validation

```
python3 -m genting.validate data/raw/company_filings.jsonl
  records=563 {'post': 563} tickers={'GENTING': 193, 'GENM': 370}
  2024-11-25 → 2026-10-26
  OK: 0 errors

python3 scripts/validate_company_data.py data/raw/company_financials.csv
  14 rows, 7 periods per company, OK: 0 errors

python3 scripts/validate_company_data.py data/raw/company_financials_annual.csv
  4 rows, OK: 0 errors

python3 scripts/crosscheck_financials.py
  checked 14 result announcements; mismatches=0
```

`crosscheck_financials.py` re-reads the Bursa "Summary of Key Financial Information"
from each results announcement and compares revenue, PBT, net profit, EPS and declared
dividend with the CSV; all 14 rows match after normalising RM'000 to RM million.

The CSV validator checks: exact header, duplicate `(company, period)`, numeric fields,
`revenue > 0`, `net_debt == total_debt − cash` (±0.5), `period_end` inside the window,
and a non-empty http source URL.

## 8. Extraction issues and known gaps

1. **Empty announcement bodies (fixed).** 281 records initially had an empty body because
   the shareholding/listing templates do not use the `#D_GA_Content` container that
   financial-result pages use. The parser now takes the whole `div.bursa-ann` panel
   whenever it is longer and cuts at "Announcement Info"; all 563 records have body text,
   including the detail tables (date of change, number of securities, consideration,
   resulting interest) that the partial container omitted.
2. **Short records.** The shortest bodies (roughly 300–380 characters) are book-closure
   notices, annual-report cover announcements, suspension/resumption circulars and a
   principal-officer change. Their announcement pages contain only the metadata shown;
   where a PDF is attached it was downloaded. These are complete bodies, not truncations.
3. **Financial-result bodies carry the Bursa summary table, not the full statements.**
   All 16 bodies include the official "Summary of Key Financial Information" (revenue,
   PBT, profit for the period, attributable profit, EPS, declared dividend and net assets
   per share, in RM'000). The full income statement, balance sheet, cash flow and segment
   note are in the attached quarterly report, while adjusted EBITDA and the segment table
   are in the press release. Both PDFs were downloaded and parsed for all 16 results.
4. **Units changed in 1Q26.** GENTING and GENM reported in RM'000 through 4Q25 and in
   RM million from 1Q26. The parser detects the unit header and normalises to RM million;
   without this, 1Q26 revenue would have been 1,000× too large.
5. **PDF text extraction.** All 4 annual reports, all 32 quarterly PDFs and all 83
   announcement PDFs were converted to page-delimited text with pypdf; every PDF has a
   sibling `.txt`. Some annual-report registers are images (noted above). pypdf also emits
   warnings about a few embedded fonts ("fontTools is required…"); extracted text for the
   primary statements is clean and was manually read against the PDF page images for the
   numbers used in the CSVs.
6. **3Q26 results** do not exist in the window (due by 30 Nov 2026). Genuine gap.
7. **Rights-issue pricing** is not yet fixed; the corporate-action record therefore has
   null subscription price, ratio and dilution.
8. **Bursa direct** is 403 from this network. The KLSE Screener mirror reproduces the
   Bursa announcement body, the reference number and the attachment links, and links the
   original `announcement_details?ann_id=…` page; `raw.bursa_original_url` is present on
   all 563 records. i3investor was used only as a recent-items subset check.
9. **Shares/turnover announcements** filed by stockbrokers (disclosure of dealings during
   the take-over) are included as general announcements; they are not trades by the
   companies themselves.
10. **Company IR pages** list the same annual reports that are filed with Bursa. The IR
    copies were used for text extraction; the Bursa copies are also stored under
    `data/company_docs/announcements/` for provenance.
11. **Stratford acquisition.** GENM's April 2025 acquisition of Genting Casino Stratford
    for GBP27.8m is disclosed in the FY2025 annual report (p23) but has no Bursa
    announcement in the window and the annual report gives only the month, not the exact
    completion date. It is recorded in `annual_facts.md`, not dated in
    `company_actions.jsonl`.

## 9. Files

| Path | Contents |
| --- | --- |
| `data/raw/company_filings.jsonl` | 563 announcement records (`record_type=post`, `source=bursa_filing`) |
| `data/raw/company_financials.csv` | 14 quarterly rows (4Q24–2Q26, both companies) |
| `data/raw/company_financials_annual.csv` | FY2024/FY2025 rows |
| `data/raw/company_segments.csv` | 105 quarterly segment-revenue rows |
| `data/raw/company_financials_meta.json` | units, definitions, coverage |
| `data/raw/company_financials_provenance.csv` | per-period report / press-release PDFs and page hints |
| `data/raw/company_actions.jsonl` | 40 corporate-action records |
| `data/company_docs/*.pdf` | FY2024/FY2025 annual reports |
| `data/company_docs/*.txt` | page-delimited annual-report text |
| `data/company_docs/quarterly/<TICKER>/` | 32 quarterly report + press-release PDFs and text |
| `data/company_docs/quarterly/manifest.csv` | period → report / press-release PDF / announcement URL |
| `data/company_docs/announcements/` | 83 announcement PDFs + extracted text (offer document, circulars, AGM notices, IAC, rights issue, MTNs, annual reports) |
| `data/company_docs/annual_manifest.csv` | company / year → PDF, text, pages, source URL |
| `data/company_docs/annual_facts.md` | structured summary of the four annual reports |
| `data/company_docs/pdf_manifest.json` | URL → local file manifest for every downloaded PDF |

## 10. Reproduction

```bash
# 1. enumerate announcements + detail pages (cached)
python3 scripts/collect_filings.py

# 2. download announcement PDFs
python3 scripts/download_filing_pdfs.py --filter financial
python3 scripts/download_filing_pdfs.py --filter corporate

# 3. extract text from annual + quarterly PDFs
python3 scripts/extract_company_docs.py data/company_docs/GENTING_IAR2024.pdf data/company_docs/GENTING_IAR2025.pdf \
    data/company_docs/GENM_IAR2024.pdf data/company_docs/GENM_IAR2025.pdf
python3 scripts/extract_company_docs.py $(find data/company_docs/quarterly/GENTING data/company_docs/quarterly/GENM -maxdepth 1 -name '*.pdf')

# 4. build the datasets
python3 scripts/build_financials.py
python3 scripts/build_segments.py
python3 scripts/build_company_actions.py

# 5. validate
python3 -m genting.validate data/raw/company_filings.jsonl
python3 scripts/validate_company_data.py data/raw/company_financials.csv
python3 scripts/validate_company_data.py data/raw/company_financials_annual.csv
python3 scripts/crosscheck_financials.py
```
