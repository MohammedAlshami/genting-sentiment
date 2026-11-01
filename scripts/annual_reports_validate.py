#!/usr/bin/env python3
"""Validate the annual-report collection and print pass/fail checks."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "data" / "company_docs" / "manifests" / "annual_reports.csv"
ANN = ROOT / "data" / "company_docs" / "annual"
FIN = ROOT / "data" / "raw" / "financial_statements_annual.csv"
NUM = ROOT / "data" / "raw" / "annual_report_numbers.csv"

errors = []
warnings = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def pdf_pages(path: Path) -> int:
    out = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True)
    for line in out.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    return 0


def main() -> int:
    man = list(csv.DictReader(MAN.open()))
    if len(man) != 56:
        err(f"manifest has {len(man)} rows, expected 56")
    seen = set()
    for r in man:
        key = (r["ticker"], r["year"])
        if key in seen:
            err(f"duplicate {key}")
        seen.add(key)
        if len(r["sha256"]) != 64:
            err(f"{key}: bad sha256")
        if not r["pages"] or int(r["pages"]) <= 20:
            err(f"{key}: page count {r['pages']}")
        if not r["text_chars"] or int(r["text_chars"]) == 0:
            err(f"{key}: no text")
        if r["chars_per_page"] and float(r["chars_per_page"]) < 500:
            warn(f"{key}: {r['chars_per_page']} chars/page")
        pdf = ROOT / r["file"]
        if not pdf.exists():
            err(f"{key}: missing PDF")
        else:
            actual = pdf_pages(pdf)
            if actual != int(r["pages"]):
                err(f"{key}: pdfinfo {actual} != manifest {r['pages']}")
        tab = ANN / "tables" / f"{r['ticker']}_AR_{r['year']}.json"
        if not tab.exists():
            err(f"{key}: missing table JSON")
        else:
            d = json.loads(tab.read_text())
            if d.get("n_tables", 0) == 0:
                err(f"{key}: zero tables")
            if d.get("n_tables") != int(r["table_count"] or -1):
                warn(f"{key}: table JSON count differs from manifest")
    if not FIN.exists():
        err("missing financial_statements_annual.csv")
    else:
        fin = pd.read_csv(FIN)
        p = fin.pivot_table(index=["ticker", "fiscal_year"], columns="line_item",
                            values="value", aggfunc="first").reset_index()
        p = p[p.fiscal_year.between(2015, 2025)]
        for tk in ("GENTING", "GENM"):
            for y in range(2015, 2026):
                row = p[(p.ticker == tk) & (p.fiscal_year == y)]
                if row.empty:
                    err(f"curated: {tk} {y} absent")
                    continue
                for m in ["revenue", "EBITDA", "PBT", "net_profit", "finance_cost",
                          "total_assets", "total_liabilities", "equity", "total_debt",
                          "cash", "net_debt", "EPS", "DPS", "operating_cash_flow", "capex"]:
                    if pd.isna(row.iloc[0].get(m)):
                        err(f"curated: {tk} {y} missing {m}")
                d = row.iloc[0]
                if abs(d.total_assets - (d.total_liabilities + d.equity)) > max(1, abs(d.total_assets) * 0.001):
                    err(f"recon A=L+E {tk} {y}: {d.total_assets - (d.total_liabilities + d.equity):+.1f}")
                if abs(d.net_debt - (d.total_debt - d.cash)) > 0.1:
                    err(f"recon net debt {tk} {y}")
    if not NUM.exists():
        err("missing annual_report_numbers.csv")
    else:
        import csv as _csv
        with NUM.open(newline="", encoding="utf-8") as fh:
            _r = _csv.reader(fh)
            next(_r, None)
            n = sum(1 for _ in _r)
        if n < 10000:
            warn(f"only {n} numeric tokens")
    print(f"manifest rows: {len(man)}")
    print(f"errors: {len(errors)}; warnings: {len(warnings)}")
    for e in errors:
        print("ERROR", e)
    for w in warnings:
        print("WARN ", w)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
