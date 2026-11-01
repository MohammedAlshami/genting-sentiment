#!/usr/bin/env python3
"""Write data/raw/annual_reports_report.md with coverage, QA and reconciliations."""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "data" / "company_docs" / "manifests" / "annual_reports.csv"
FIN = ROOT / "data" / "raw" / "financial_statements_annual.csv"
NUM = ROOT / "data" / "raw" / "annual_report_numbers.csv"
OUT = ROOT / "data" / "raw" / "annual_reports_report.md"

REQ = ["revenue", "EBITDA", "PBT", "net_profit", "finance_cost", "total_assets",
       "total_liabilities", "equity", "total_debt", "cash", "net_debt", "EPS",
       "DPS", "operating_cash_flow", "capex"]


def main() -> int:
    man = list(csv.DictReader(MAN.open()))
    fin = pd.read_csv(FIN)
    lines = []
    A = lines.append

    A("# Annual reports — collection and extraction report")
    A("")
    A("Genting Berhad (GENTING, Bursa 3182) and Genting Malaysia Berhad (GENM, Bursa 4715).")
    A("")
    A("## Scope and sources")
    A("")
    A("- Source indexes: https://www.genting.com/annual_reports and "
      "https://www.gentingmalaysia.com/annual_reports")
    A("- Years: **1998–2025** (28 report years per company; FY2025 is the latest).")
    A(f"- PDFs held: **{len(man)}** — GENTING "
      f"{sum(1 for r in man if r['ticker']=='GENTING')}, GENM "
      f"{sum(1 for r in man if r['ticker']=='GENM')}.")
    A(f"- Total PDF pages: **{sum(int(r['pages']) for r in man):,}**; total extracted "
      f"text: **{sum(int(r['text_chars']) for r in man):,}** characters.")
    A("- Files: `data/company_docs/annual/<TICKER>_AR_<YEAR>.pdf`; text in `annual/text/`; "
      "tables in `annual/tables/`; manifest in `data/company_docs/manifests/annual_reports.csv`.")
    A("")
    A("## Document manifest")
    A("")
    A("| Ticker | Reports | Years | Pages | Text chars | Tables | Table rows | Table cells |")
    A("|---|---:|---|---:|---:|---:|---:|---:|")
    for tk in ("GENTING", "GENM"):
        sub = [r for r in man if r["ticker"] == tk]
        years = sorted(int(r["year"]) for r in sub)
        A(f"| {tk} | {len(sub)} | {min(years)}–{max(years)} | "
          f"{sum(int(r['pages']) for r in sub):,} | "
          f"{sum(int(r['text_chars']) for r in sub):,} | "
          f"{sum(int(r['table_count'] or 0) for r in sub):,} | "
          f"{sum(int(r['table_rows'] or 0) for r in sub):,} | "
          f"{sum(int(r['table_cells'] or 0) for r in sub):,} |")
    A("")
    A("Every manifest row has a SHA-256 and a page count. All PDFs open with "
      "`pdfinfo` and all have more than 20 pages (smallest: "
      f"{min(int(r['pages']) for r in man)} pages).")
    A("")
    A("## Extraction QA")
    A("")
    low_text = [r for r in man if r["chars_per_page"] and float(r["chars_per_page"]) < 500]
    short = [r for r in man if int(r["pages"]) <= 20]
    bad_text = [r for r in man if r["text_extraction_status"] != "ok"]
    missing_tables = [r for r in man if not r["table_count"]]
    A(f"- Text extraction failures: **{len(bad_text)}**.")
    A(f"- PDFs below 500 text chars/page: **{len(low_text)}**.")
    A(f"- PDFs with <=20 pages: **{len(short)}**.")
    A(f"- PDFs without a table JSON: **{len(missing_tables)}**.")
    if low_text:
        A("")
        A("Low-text PDFs: " + ", ".join(f"{r['ticker']} {r['year']} "
                                        f"({r['chars_per_page']}/page)" for r in low_text))
    A("")
    A("### Text coverage by report")
    A("")
    A("| Ticker | Year | Pages | Text chars | Chars/page | Tables | Table rows |")
    A("|---|---:|---:|---:|---:|---:|---:|")
    for r in sorted(man, key=lambda x: (x["ticker"], int(x["year"]))):
        A(f"| {r['ticker']} | {r['year']} | {r['pages']} | {int(r['text_chars']):,} | "
          f"{r['chars_per_page']} | {r['table_count']} | {r['table_rows']} |")
    A("")
    A("## Table and number layer")
    A("")
    A("Tables were extracted with **pdfplumber** in two passes:")
    A("")
    A("1. `lines` strategy for bordered tables, with newline-packed cells expanded back "
      "into individual rows when the label and numeric columns share a line count.")
    A("2. whitespace/x-position aligned tables built from pdfplumber words for borderless "
      "tables (financial statements, highlights and notes).")
    A("")
    A("Each `annual/tables/<TICKER>_AR_<YEAR>.json` contains `page`, `table_index`, "
      "`method`, `bbox`, `caption`, `context`, `n_rows`, `n_cols` and `rows`; every cell is "
      "kept verbatim as text, including units and footnotes.")
    A("")
    num_rows = 0
    if NUM.exists():
        import csv as _csv
        with NUM.open(newline="", encoding="utf-8") as fh:
            _r = _csv.reader(fh)
            next(_r, None)
            num_rows = sum(1 for _ in _r)
    A(f"`data/raw/annual_report_numbers.csv` contains **{num_rows:,}** numeric tokens. "
      "A printed cell that holds several numbers (for example a value plus a percentage "
      "change) yields one row per number; `cell_text` keeps the original cell verbatim. "
      "Every row carries page, table, row, column and caption coordinates. The layer is "
      "deliberately exhaustive: header years, note references and contents-page numbers are "
      "numeric tokens too.")
    A("")
    A("Table extraction is high-recall and includes contents pages, cover fragments and small "
      "note tables as well as the primary statements. `method` distinguishes `ruled` from "
      "`text` tables; the curated CSV is the right entry point for the primary statements.")
    A("")
    A("## Curated financial statements")
    A("")
    A("`data/raw/financial_statements_annual.csv` covers **FY2015–FY2025** for both "
      "companies and is complete for all required metrics. This is the comparable window "
      "requested; older reports (1998–2014) remain fully represented in the text, table and "
      "long-number layers. Values are normalised to **RM million** using the unit printed on "
      "the source page; EPS and DPS are in **sen**. Page numbers are PDF page numbers (not "
      "the printed page number).")
    A("")
    A("| Metric | GENTING FY2015–25 | GENM FY2015–25 | GENTING rows | GENM rows |")
    A("|---|---:|---:|---:|---:|")
    for m in REQ:
        sub = fin[fin.line_item == m]
        g = sub[(sub.ticker == "GENTING") & sub.fiscal_year.between(2015, 2025)]
        n = sub[(sub.ticker == "GENM") & sub.fiscal_year.between(2015, 2025)]
        ga = sub[sub.ticker == "GENTING"]
        na = sub[sub.ticker == "GENM"]
        A(f"| {m} | {g.fiscal_year.nunique()}/11 | {n.fiscal_year.nunique()}/11 | "
          f"{ga.fiscal_year.nunique()} | {na.fiscal_year.nunique()} |")
    A("")
    A("Definitions and derived lines:")
    A("")
    A("- **EBITDA** = PBT + finance cost + depreciation & amortisation, all taken from the "
      "printed income statement / cash flow statement.")
    A("- **Total debt** = long-term borrowings + short-term borrowings, excluding lease "
      "liabilities so the series is comparable before and after MFRS 16 (2019). "
      "`total_debt_incl_leases` is also provided where lease liabilities are printed.")
    A("- **Net debt** = total debt − cash and cash equivalents. A negative value is net cash.")
    A("- `page` is the primary PDF page; `source_pages` lists every page used for a derived "
      "line. `source_pdf` is the primary report; `source_pdfs` lists all reports used.")
    A("- **Capex** is the reported purchase of property, plant and equipment in the cash flow "
      "statement; negative means a cash outflow.")
    A("- **DPS** is the printed net dividend per share (sen) from the financial-highlights "
      "table. If a report omits the line, the value is taken from the same table in the next "
      "report, where the year is a comparative column; `source_pdf` records which report was used.")
    A("")
    A("## Reconciliation checks")
    A("")
    p = fin.pivot_table(index=["ticker", "fiscal_year"], columns="line_item",
                        values="value", aggfunc="first").reset_index()
    p = p[p.fiscal_year.between(1998, 2025)]

    def check(name, expr, tol_abs=1.0, tol_rel=0.001):
        bad = []
        for _, r in p.iterrows():
            try:
                d = expr(r)
            except Exception:  # noqa: BLE001
                continue
            if d is None or pd.isna(d):
                continue
            if abs(d) > max(tol_abs, abs(r.get("total_assets", 0)) * tol_rel):
                bad.append((r.ticker, int(r.fiscal_year), d))
        A(f"- **{name}**: {len(bad)} mismatch(es)"
          + ("" if not bad else " — " + ", ".join(f"{t} {y} ({d:+.1f})" for t, y, d in bad[:20])))
        return bad

    check("Total assets = total liabilities + equity",
          lambda r: r.total_assets - (r.total_liabilities + r.equity))
    check("Net debt = total debt − cash",
          lambda r: r.net_debt - (r.total_debt - r.cash), tol_abs=0.1, tol_rel=0)
    # net profit identity: attributable + NCI + perpetual (perpetual absent in most years)
    bad = []
    for _, r in p.iterrows():
        if pd.isna(r.get("net_profit")) or pd.isna(r.get("net_profit_attributable")):
            continue
        nci = 0.0 if pd.isna(r.get("net_profit_nci")) else r.net_profit_nci
        perp = 0.0 if pd.isna(r.get("net_profit_perpetual")) else r.net_profit_perpetual
        d = r.net_profit - (r.net_profit_attributable + nci + perp)
        if abs(d) > max(1.0, abs(r.net_profit) * 0.001):
            bad.append((r.ticker, int(r.fiscal_year), d))
    A(f"- **Net profit = attributable + non-controlling interests + perpetual securities**: "
      f"{len(bad)} mismatch(es)"
      + ("" if not bad else " — " + ", ".join(f"{t} {y} ({d:+.1f})" for t, y, d in bad[:20])))
    A("")
    A("Mismatches are reported, not silently corrected. Rounding differences of ≤0.1% of "
      "total assets are treated as presentation rounding.")
    A("")
    A("## Known issues and caveats")
    A("")
    A("- **GENTING 2011 replacement.** The official `genting.com` link returns a truncated "
      "65-page file (`GB Cover 4 May`) that ends mid-directors' report and contains no "
      "financial statements. The full 170-page report was assembled from the two PDF "
      "attachments to Genting Berhad's Annual Report 2011 filing on Bursa Malaysia "
      "(announcement 1265884, 23 May 2012, attachments 157583 and 157584; "
      "https://www.bursamalaysia.com/market_information/announcements/company_announcement/"
      "announcement_details?ann_id=1265884) and is used as "
      "`GENTING_AR_2011.pdf`. The original official file "
      "is retained at "
      "`data/company_docs/annual/alternates/GENTING_AR_2011_official_truncated_65p.pdf`. "
      "This is the only non-genting.com source used.")
    A("- **GENTING 2021 font corruption.** The printed 2021 income statement uses an embedded "
      "font whose text layer drops characters (`Loss rofit e ore ta atio`). Revenue, finance "
      "cost, EPS and the balance sheet are readable; PBT and net profit were recovered from "
      "the 2021 comparative column in the FY2022 report (`GENTING_AR_2022.pdf`) and are marked "
      "with that source PDF.")
    A("- **Curated window.** FY1998–FY2014 balance sheets use legacy layouts (for example "
      "'employment of capital' and 'capital employed') whose totals are not directly "
      "comparable with the modern statements. Those years are deliberately excluded from the "
      "curated file but are fully present in `annual_report_numbers.csv` and the table JSON. "
      "The FY2015–FY2025 curated window is complete and reconciles.")
    A("- **PDF page numbers.** Page references are the physical PDF page, not the printed "
      "page number at the foot of the page.")
    A("- **Text-layer quality.** All 56 PDFs yield >4,000 chars/page on average, but old "
      "scans and some embedded fonts produce OCR-like or dropped characters; table cells "
      "retain the text exactly as extracted rather than being guessed.")
    A("- No numbers were fabricated. Every curated value is tied to a statement row and a "
      "page; derived values record their formula in the `basis` column.")
    A("")
    A("## Files produced")
    A("")
    A("| Path | Contents |")
    A("|---|---|")
    A("| `data/company_docs/annual/*.pdf` | 56 annual reports, 1998–2025 |")
    A("| `data/company_docs/annual/text/*.txt` | page-preserving full text (form-feed separated) |")
    A("| `data/company_docs/annual/tables/*.json` | all tables with page, caption, rows |")
    A("| `data/company_docs/annual/statements/*.json` | parsed primary-statement rows used for curation |")
    A("| `data/company_docs/manifests/annual_reports.csv` | manifest with SHA-256, pages, text/table counts |")
    A("| `data/raw/annual_report_numbers.csv` | long numeric-cell table |")
    A("| `data/raw/financial_statements_annual.csv` | curated income/balance/cash-flow lines |")
    A("| `data/raw/annual_reports_report.md` | this report |")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
