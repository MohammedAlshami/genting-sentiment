# Annual reports — collection and extraction report

Genting Berhad (GENTING, Bursa 3182) and Genting Malaysia Berhad (GENM, Bursa 4715).

## Scope and sources

- Source indexes: https://www.genting.com/annual_reports and https://www.gentingmalaysia.com/annual_reports
- Years: **1998–2025** (28 report years per company; FY2025 is the latest).
- PDFs held: **56** — GENTING 28, GENM 28.
- Total PDF pages: **8,491**; total extracted text: **42,455,347** characters.
- Files: `data/company_docs/annual/<TICKER>_AR_<YEAR>.pdf`; text in `annual/text/`; tables in `annual/tables/`; manifest in `data/company_docs/manifests/annual_reports.csv`.

## Document manifest

| Ticker | Reports | Years | Pages | Text chars | Tables | Table rows | Table cells |
|---|---:|---|---:|---:|---:|---:|---:|
| GENTING | 28 | 1998–2025 | 4,780 | 24,289,625 | 7,009 | 47,716 | 253,430 |
| GENM | 28 | 1998–2025 | 3,711 | 18,165,722 | 5,885 | 34,249 | 179,179 |

Every manifest row has a SHA-256 and a page count. All PDFs open with `pdfinfo` and all have more than 20 pages (smallest: 47 pages).

## Extraction QA

- Text extraction failures: **0**.
- PDFs below 500 text chars/page: **0**.
- PDFs with <=20 pages: **0**.
- PDFs without a table JSON: **0**.

### Text coverage by report

| Ticker | Year | Pages | Text chars | Chars/page | Tables | Table rows |
|---|---:|---:|---:|---:|---:|---:|
| GENM | 1998 | 80 | 419,283 | 5241.0 | 140 | 1019 |
| GENM | 1999 | 47 | 194,522 | 4138.8 | 76 | 515 |
| GENM | 2000 | 56 | 250,824 | 4479.0 | 125 | 668 |
| GENM | 2001 | 68 | 321,740 | 4731.5 | 116 | 644 |
| GENM | 2002 | 80 | 389,346 | 4866.8 | 139 | 738 |
| GENM | 2003 | 96 | 533,536 | 5557.7 | 134 | 667 |
| GENM | 2004 | 86 | 370,543 | 4308.6 | 149 | 786 |
| GENM | 2005 | 104 | 463,971 | 4461.3 | 226 | 1047 |
| GENM | 2006 | 107 | 480,503 | 4490.7 | 190 | 999 |
| GENM | 2007 | 85 | 487,472 | 5735.0 | 177 | 988 |
| GENM | 2008 | 81 | 433,495 | 5351.8 | 154 | 904 |
| GENM | 2009 | 96 | 540,467 | 5629.9 | 153 | 1000 |
| GENM | 2010 | 128 | 692,222 | 5408.0 | 228 | 1483 |
| GENM | 2011 | 114 | 595,184 | 5220.9 | 225 | 1298 |
| GENM | 2012 | 134 | 718,022 | 5358.4 | 240 | 1593 |
| GENM | 2013 | 131 | 680,086 | 5191.5 | 213 | 1436 |
| GENM | 2014 | 137 | 643,897 | 4700.0 | 192 | 1314 |
| GENM | 2015 | 213 | 1,084,965 | 5093.7 | 374 | 2320 |
| GENM | 2016 | 142 | 697,236 | 4910.1 | 213 | 1384 |
| GENM | 2017 | 170 | 821,238 | 4830.8 | 223 | 1370 |
| GENM | 2018 | 186 | 879,935 | 4730.8 | 251 | 1487 |
| GENM | 2019 | 178 | 826,730 | 4644.6 | 267 | 1582 |
| GENM | 2020 | 186 | 841,517 | 4524.3 | 272 | 1609 |
| GENM | 2021 | 200 | 912,394 | 4562.0 | 250 | 1581 |
| GENM | 2022 | 204 | 1,063,104 | 5211.3 | 297 | 1511 |
| GENM | 2023 | 196 | 926,949 | 4729.3 | 279 | 1425 |
| GENM | 2024 | 198 | 923,132 | 4662.3 | 289 | 1395 |
| GENM | 2025 | 208 | 973,409 | 4679.9 | 293 | 1486 |
| GENTING | 1998 | 109 | 578,888 | 5310.9 | 194 | 1557 |
| GENTING | 1999 | 56 | 315,428 | 5632.6 | 111 | 725 |
| GENTING | 2000 | 64 | 312,390 | 4881.1 | 146 | 682 |
| GENTING | 2001 | 79 | 395,169 | 5002.1 | 158 | 1034 |
| GENTING | 2002 | 92 | 446,655 | 4854.9 | 170 | 1074 |
| GENTING | 2003 | 116 | 622,151 | 5363.4 | 179 | 1059 |
| GENTING | 2004 | 123 | 583,884 | 4747.0 | 202 | 1264 |
| GENTING | 2005 | 135 | 608,740 | 4509.2 | 203 | 1360 |
| GENTING | 2006 | 141 | 688,762 | 4884.8 | 258 | 1800 |
| GENTING | 2007 | 134 | 811,722 | 6057.6 | 251 | 1675 |
| GENTING | 2008 | 135 | 793,756 | 5879.7 | 234 | 1690 |
| GENTING | 2009 | 140 | 815,146 | 5822.5 | 237 | 1651 |
| GENTING | 2010 | 140 | 770,867 | 5506.2 | 216 | 1536 |
| GENTING | 2011 | 170 | 873,328 | 5137.2 | 276 | 1808 |
| GENTING | 2012 | 172 | 899,943 | 5232.2 | 260 | 1905 |
| GENTING | 2013 | 180 | 981,186 | 5451.0 | 282 | 1998 |
| GENTING | 2014 | 195 | 972,916 | 4989.3 | 249 | 1920 |
| GENTING | 2015 | 211 | 1,065,113 | 5047.9 | 276 | 2083 |
| GENTING | 2016 | 194 | 987,879 | 5092.2 | 262 | 1969 |
| GENTING | 2017 | 230 | 1,159,388 | 5040.8 | 316 | 2146 |
| GENTING | 2018 | 246 | 1,244,946 | 5060.8 | 338 | 2180 |
| GENTING | 2019 | 224 | 1,131,161 | 5049.8 | 299 | 2093 |
| GENTING | 2020 | 232 | 1,194,023 | 5146.7 | 289 | 2045 |
| GENTING | 2021 | 242 | 1,198,715 | 4953.4 | 295 | 2106 |
| GENTING | 2022 | 246 | 1,191,634 | 4844.0 | 302 | 1980 |
| GENTING | 2023 | 242 | 1,156,124 | 4777.4 | 301 | 1971 |
| GENTING | 2024 | 250 | 1,186,130 | 4744.5 | 320 | 2028 |
| GENTING | 2025 | 282 | 1,303,581 | 4622.6 | 385 | 2377 |

## Table and number layer

Tables were extracted with **pdfplumber** in two passes:

1. `lines` strategy for bordered tables, with newline-packed cells expanded back into individual rows when the label and numeric columns share a line count.
2. whitespace/x-position aligned tables built from pdfplumber words for borderless tables (financial statements, highlights and notes).

Each `annual/tables/<TICKER>_AR_<YEAR>.json` contains `page`, `table_index`, `method`, `bbox`, `caption`, `context`, `n_rows`, `n_cols` and `rows`; every cell is kept verbatim as text, including units and footnotes.

`data/raw/annual_report_numbers.csv` contains **231,379** numeric tokens. A printed cell that holds several numbers (for example a value plus a percentage change) yields one row per number; `cell_text` keeps the original cell verbatim. Every row carries page, table, row, column and caption coordinates. The layer is deliberately exhaustive: header years, note references and contents-page numbers are numeric tokens too.

Table extraction is high-recall and includes contents pages, cover fragments and small note tables as well as the primary statements. `method` distinguishes `ruled` from `text` tables; the curated CSV is the right entry point for the primary statements.

## Curated financial statements

`data/raw/financial_statements_annual.csv` covers **FY2015–FY2025** for both companies and is complete for all required metrics. This is the comparable window requested; older reports (1998–2014) remain fully represented in the text, table and long-number layers. Values are normalised to **RM million** using the unit printed on the source page; EPS and DPS are in **sen**. Page numbers are PDF page numbers (not the printed page number).

| Metric | GENTING FY2015–25 | GENM FY2015–25 | GENTING rows | GENM rows |
|---|---:|---:|---:|---:|
| revenue | 11/11 | 11/11 | 11 | 11 |
| EBITDA | 11/11 | 11/11 | 11 | 11 |
| PBT | 11/11 | 11/11 | 11 | 11 |
| net_profit | 11/11 | 11/11 | 11 | 11 |
| finance_cost | 11/11 | 11/11 | 11 | 11 |
| total_assets | 11/11 | 11/11 | 11 | 11 |
| total_liabilities | 11/11 | 11/11 | 11 | 11 |
| equity | 11/11 | 11/11 | 11 | 11 |
| total_debt | 11/11 | 11/11 | 11 | 11 |
| cash | 11/11 | 11/11 | 11 | 11 |
| net_debt | 11/11 | 11/11 | 11 | 11 |
| EPS | 11/11 | 11/11 | 11 | 11 |
| DPS | 11/11 | 11/11 | 11 | 11 |
| operating_cash_flow | 11/11 | 11/11 | 11 | 11 |
| capex | 11/11 | 11/11 | 11 | 11 |

Definitions and derived lines:

- **EBITDA** = PBT + finance cost + depreciation & amortisation, all taken from the printed income statement / cash flow statement.
- **Total debt** = long-term borrowings + short-term borrowings, excluding lease liabilities so the series is comparable before and after MFRS 16 (2019). `total_debt_incl_leases` is also provided where lease liabilities are printed.
- **Net debt** = total debt − cash and cash equivalents. A negative value is net cash.
- `page` is the primary PDF page; `source_pages` lists every page used for a derived line. `source_pdf` is the primary report; `source_pdfs` lists all reports used.
- **Capex** is the reported purchase of property, plant and equipment in the cash flow statement; negative means a cash outflow.
- **DPS** is the printed net dividend per share (sen) from the financial-highlights table. If a report omits the line, the value is taken from the same table in the next report, where the year is a comparative column; `source_pdf` records which report was used.

## Reconciliation checks

- **Total assets = total liabilities + equity**: 0 mismatch(es)
- **Net debt = total debt − cash**: 0 mismatch(es)
- **Net profit = attributable + non-controlling interests + perpetual securities**: 0 mismatch(es)

Mismatches are reported, not silently corrected. Rounding differences of ≤0.1% of total assets are treated as presentation rounding.

## Known issues and caveats

- **GENTING 2011 replacement.** The official `genting.com` link returns a truncated 65-page file (`GB Cover 4 May`) that ends mid-directors' report and contains no financial statements. The full 170-page report was assembled from the two PDF attachments to Genting Berhad's Annual Report 2011 filing on Bursa Malaysia (announcement 1265884, 23 May 2012, attachments 157583 and 157584; https://www.bursamalaysia.com/market_information/announcements/company_announcement/announcement_details?ann_id=1265884) and is used as `GENTING_AR_2011.pdf`. The original official file is retained at `data/company_docs/annual/alternates/GENTING_AR_2011_official_truncated_65p.pdf`. This is the only non-genting.com source used.
- **GENTING 2021 font corruption.** The printed 2021 income statement uses an embedded font whose text layer drops characters (`Loss rofit e ore ta atio`). Revenue, finance cost, EPS and the balance sheet are readable; PBT and net profit were recovered from the 2021 comparative column in the FY2022 report (`GENTING_AR_2022.pdf`) and are marked with that source PDF.
- **Curated window.** FY1998–FY2014 balance sheets use legacy layouts (for example 'employment of capital' and 'capital employed') whose totals are not directly comparable with the modern statements. Those years are deliberately excluded from the curated file but are fully present in `annual_report_numbers.csv` and the table JSON. The FY2015–FY2025 curated window is complete and reconciles.
- **PDF page numbers.** Page references are the physical PDF page, not the printed page number at the foot of the page.
- **Text-layer quality.** All 56 PDFs yield >4,000 chars/page on average, but old scans and some embedded fonts produce OCR-like or dropped characters; table cells retain the text exactly as extracted rather than being guessed.
- No numbers were fabricated. Every curated value is tied to a statement row and a page; derived values record their formula in the `basis` column.

## Files produced

| Path | Contents |
|---|---|
| `data/company_docs/annual/*.pdf` | 56 annual reports, 1998–2025 |
| `data/company_docs/annual/text/*.txt` | page-preserving full text (form-feed separated) |
| `data/company_docs/annual/tables/*.json` | all tables with page, caption, rows |
| `data/company_docs/annual/statements/*.json` | parsed primary-statement rows used for curation |
| `data/company_docs/manifests/annual_reports.csv` | manifest with SHA-256, pages, text/table counts |
| `data/raw/annual_report_numbers.csv` | long numeric-cell table |
| `data/raw/financial_statements_annual.csv` | curated income/balance/cash-flow lines |
| `data/raw/annual_reports_report.md` | this report |
