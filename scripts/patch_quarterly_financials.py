#!/usr/bin/env python3
"""Patch EPS / net-profit / segment-residual fields in the quarterly panel.

This is deliberately separate from scripts/build_financials.py, which belongs to
another collector.  It reads the table CSVs produced by extract_quarterly.py and
fills only fields that the main panel builder left blank or mis-selected.
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QDIR = ROOT / "data" / "company_docs" / "quarterly"
FIN = ROOT / "data" / "raw" / "quarterly_financials.csv"


def read_text(stem: str) -> dict[int, str]:
    raw = (QDIR / "text" / f"{stem}.txt").read_text(encoding="utf-8", errors="replace")
    parts = re.split(r"\n===== PAGE (\d+) =====\n", raw)
    return {int(parts[i]): parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def read_groups(stem: str):
    path = QDIR / "tables" / f"{stem}.csv"
    if not path.exists():
        return []
    by_row = defaultdict(list)
    for r in csv.DictReader(path.open(newline="", encoding="utf-8")):
        by_row[(int(r["page"]), int(r["table_index"]), int(r["row"]))].append(r)
    groups = []
    for key, cells in by_row.items():
        cells.sort(key=lambda c: int(c["col"]))
        nums = [c for c in cells if c["value_number"] != ""]
        if not nums:
            continue
        label = nums[0].get("row_label") or ""
        if not label:
            texts = [c["value_text"] for c in cells if c["value_number"] == ""]
            label = " ".join(t for t in texts if t)
        groups.append({"page": key[0], "table": key[1], "row": key[2],
                       "label": label.strip(), "cells": nums})
    groups.sort(key=lambda g: (g["page"], g["table"], g["row"]))
    return groups


def main():
    rows = list(csv.DictReader(FIN.open(newline="", encoding="utf-8")))
    fields = list(rows[0].keys())
    by_key = {(r["ticker"], int(r["year"]), int(r["quarter"])): r for r in rows}
    for r in rows:
        stem = Path(r["source"]).stem
        texts = read_text(stem)
        groups = read_groups(stem)
        income_page = None
        for p, t in texts.items():
            if re.search(r"income statement|loss per share \(sen\)|earnings per share \(sen\)", t, re.I):
                income_page = p
                break
        eps_start = -1
        if income_page:
            tpath = QDIR / "tables" / f"{stem}.csv"
            if tpath.exists():
                for rr in csv.DictReader(tpath.open(newline="", encoding="utf-8")):
                    if int(rr["page"]) == income_page and rr["value_number"] == "" and re.search(r"per share", rr["value_text"], re.I):
                        eps_start = max(eps_start, int(rr["row"]))
        eps_cands = [g for g in groups if income_page and g["page"] == income_page and g["row"] > eps_start]

        def small(g):
            try:
                return abs(float(g["cells"][0]["value_number"])) < 200
            except (ValueError, TypeError):
                return False

        eps = None
        for g in eps_cands:
            if re.match(r"^\s*-?\s*Basic\b", g["label"], re.I) and small(g):
                eps = g["cells"][0]
                break
        if eps is None:
            for g in eps_cands:
                if re.search(r"\bBasic\b", g["label"], re.I) and "per share" in g["label"].lower() and small(g):
                    eps = g["cells"][0]
                    break
        if eps is None:
            for g in eps_cands:
                if re.search(r"(holders of )?the company:?$", g["label"], re.I) and small(g):
                    eps = g["cells"][0]
                    break
        if eps is None:
            for g in eps_cands:
                if re.search(r"\bDiluted\b", g["label"], re.I) and small(g):
                    eps = g["cells"][0]
                    break
        if eps is not None:
            try:
                r["eps_sen"] = str(float(eps["value_number"]))
            except ValueError:
                pass

        try:
            if r.get("net_profit") and abs(float(r["net_profit"])) > 50000:
                r["net_profit"] = str(round(float(r["net_profit"]) / 1000.0, 6))
        except ValueError:
            pass
        if not r.get("net_profit"):
            cands = [
                g for g in groups
                if g["page"] in {p for p, t in texts.items() if re.search(r"income statement", t, re.I)}
                and (re.search(r"(profit|loss).*for the (financial )?(period|year)", g["label"], re.I)
                     or re.search(r"for the financial$", g["label"], re.I))
                and not re.search(r"attributable|comprehensive|continuing", g["label"], re.I)
            ]
            if cands:
                g = cands[-1]
                v = float(g["cells"][0]["value_number"])
                pg = texts.get(g["page"], "")
                if re.search(r"RM[’']?\s?000", pg):
                    v *= 0.001
                r["net_profit"] = str(round(v, 6))

        # Old reports sometimes put the net profit value in the perpetual row.
        if r.get("perpetual_securities") and r.get("net_profit") and r["perpetual_securities"] == r["net_profit"]:
            r["perpetual_securities"] = ""

        # Dividends: add special dividends and explicit zero declarations.
        if not r.get("dividend_sen"):
            for p, t in texts.items():
                m = re.search(r"(?:declared|proposed|announced)\s+(?:a|an)\s+(special)\s+(?:single[- ]tier\s+)?dividend\s+of\s+([\d.]+)\s*sen", t, re.I)
                if m:
                    r["dividend_sen"] = m.group(2)
                    r["dividend_type"] = "special"
                    r["dividend_page"] = str(p)
                    break

        # Fallback for a missing segment note: read the current-quarter rows of
        # the results summary table (e.g. "- Malaysia 1,529.3 2Q23").
        if not r.get("segment_revenue_total_q"):
            qtoken = f"{r['quarter']}Q{str(r['year'])[-2:]}".lower()
            got = {}
            for g in groups:
                lab = g["label"].lower().strip()
                cl = (g["cells"][0].get("col_label") or "").lower()
                if qtoken not in cl:
                    continue
                for key, pat in (("malaysia", r"^- malaysia"), ("singapore", r"^- singapore"),
                                 ("uk", r"^- uk"), ("us", r"^- us")):
                    if re.search(pat, lab) and key not in got:
                        got[key] = float(g["cells"][0]["value_number"])
            if len(got) >= 3 and r.get("revenue"):
                total = float(r["revenue"])
                for k in ("malaysia", "singapore", "uk", "us"):
                    r[f"segment_revenue_{k}_q"] = str(got.get(k, "")) if k in got else ""
                r["segment_revenue_total_q"] = str(total)
                present = [v for v in got.values()]
                r["segment_revenue_others_q"] = str(round(total - sum(present), 6))
                r["segment_basis"] = "summary table current-quarter column"

        # Segment residual: allow GENM's absent Singapore column.
        total = r.get("segment_revenue_total_q")
        regions = [r.get("segment_revenue_malaysia_q"), r.get("segment_revenue_singapore_q"),
                   r.get("segment_revenue_uk_q"), r.get("segment_revenue_us_q")]
        present = [float(x) for x in regions if x not in ("", None)]
        if total not in ("", None) and len(present) >= 3:
            r["segment_revenue_others_q"] = str(round(float(total) - sum(present), 6))

    # Unit sanity: a handful of pre-2016 rows were extracted in RM'000 while
    # the panel is RM million.  Values above RM100bn are certainly still in thousands.
    monetary = ["revenue", "ebitda", "pbt", "net_profit", "net_profit_attributable",
                "minority_interest", "finance_cost", "total_debt", "long_term_borrowings",
                "short_term_borrowings", "lease_liabilities", "cash",
                "segment_revenue_malaysia_q", "segment_revenue_singapore_q",
                "segment_revenue_uk_q", "segment_revenue_us_q", "segment_revenue_others_q",
                "segment_revenue_total_q"]
    for r in rows:
        for f in monetary:
            try:
                if r.get(f) and abs(float(r[f])) > 100000:
                    r[f] = str(round(float(r[f]) / 1000.0, 6))
            except ValueError:
                pass
        try:
            if r.get("total_debt") and r.get("cash"):
                r["net_debt"] = str(round(float(r["total_debt"]) - float(r["cash"]), 6))
        except ValueError:
            pass
        # total assets/equity are informational; restore the two 2026 GENT rows
        # that the earlier broad >100,000 sanity rule over-divided.
        try:
            if r.get("total_assets") and float(r["total_assets"]) < 10000 and float(r.get("revenue") or 0) > 5000:
                r["total_assets"] = str(round(float(r["total_assets"]) * 1000, 6))
            if r.get("total_equity") and float(r["total_equity"]) < 10000 and float(r.get("revenue") or 0) > 5000:
                r["total_equity"] = str(round(float(r["total_equity"]) * 1000, 6))
        except ValueError:
            pass

    tmp = FIN.with_suffix(".csv.tmp")
    with tmp.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    tmp.replace(FIN)
    print(f"patched {FIN} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
