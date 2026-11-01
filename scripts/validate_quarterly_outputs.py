#!/usr/bin/env python3
"""Validate the quarterly PDF corpus and the derived financial panel."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QDIR = ROOT / "data" / "company_docs" / "quarterly"
MANIFEST = ROOT / "data" / "company_docs" / "manifests" / "quarterly_reports.csv"
FIN = ROOT / "data" / "raw" / "quarterly_financials.csv"
NUM = ROOT / "data" / "raw" / "quarterly_numbers.csv"
OUT = ROOT / "data" / "raw" / "quarterly_validation.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    man = list(csv.DictReader(MANIFEST.open(newline="", encoding="utf-8")))
    pdf_checks = []
    for r in man:
        p = ROOT / r["file"]
        item = {
            "ticker": r["ticker"], "year": int(r["year"]), "quarter": int(r["quarter"]),
            "status": r["status"], "file": r["file"],
        }
        if p.exists():
            item["bytes_on_disk"] = p.stat().st_size
            item["bytes_match"] = str(p.stat().st_size) == r["bytes"]
            item["sha256_match"] = sha256(p) == r["sha256"] if r["sha256"] else None
            try:
                from pypdf import PdfReader
                item["pages_open"] = len(PdfReader(str(p)).pages)
            except Exception as exc:  # noqa: BLE001
                item["pages_open"] = 0
                item["open_error"] = repr(exc)
        else:
            item["bytes_on_disk"] = 0
            item["bytes_match"] = False
            item["sha256_match"] = False
        item["pages_manifest"] = int(r["pages"] or 0)
        item["text_chars"] = int(r["text_chars"] or 0)
        item["pages_gt_5"] = item["pages_manifest"] > 5
        item["ok"] = (
            r["status"] == "ok" and item.get("bytes_match") and item.get("sha256_match")
            and item.get("pages_open", 0) > 5 and item.get("pages_open") == item["pages_manifest"]
        )
        pdf_checks.append(item)

    fin = list(csv.DictReader(FIN.open(newline="", encoding="utf-8")))
    recon = []
    for r in fin:
        if int(r["year"]) < 2020:
            continue
        np_ = fnum(r["net_profit"])
        attr = fnum(r["net_profit_attributable"])
        mino = fnum(r["minority_interest"])
        perp = fnum(r["perpetual_securities"]) or 0.0
        if None not in (np_, attr, mino):
            recon.append({
                "ticker": r["ticker"], "year": r["year"], "quarter": r["quarter"],
                "check": "net_profit = attributable + minority + perpetual",
                "left": np_, "right": round(attr + mino + perp, 6),
                "diff": round(np_ - (attr + mino + perp), 6),
            })
        td, cash, nd = fnum(r["total_debt"]), fnum(r["cash"]), fnum(r["net_debt"])
        if None not in (td, cash, nd):
            recon.append({
                "ticker": r["ticker"], "year": r["year"], "quarter": r["quarter"],
                "check": "net_debt = total_debt - cash",
                "left": nd, "right": round(td - cash, 6), "diff": round(nd - (td - cash), 6),
            })
        rev, seg = fnum(r["revenue"]), fnum(r["segment_revenue_total_q"])
        if rev is not None and seg is not None:
            recon.append({
                "ticker": r["ticker"], "year": r["year"], "quarter": r["quarter"],
                "check": "revenue = segment_total",
                "left": rev, "right": seg, "diff": round(rev - seg, 6),
            })
    bad_recon = [x for x in recon if abs(x["diff"]) > 0.2]

    nums = list(csv.DictReader(NUM.open(newline="", encoding="utf-8")))
    keys = Counter((r["ticker"], r["year"], r["quarter"], r["page"], r["table_index"],
                    r["row"], r["col"]) for r in nums)
    dup_keys = sum(1 for k, v in keys.items() if v > 1)
    num_by_report = Counter((r["ticker"], r["year"], r["quarter"]) for r in nums)

    missing_fields = {}
    for field in ["revenue", "ebitda", "pbt", "net_profit", "net_profit_attributable",
                  "minority_interest", "finance_cost", "total_debt", "cash", "net_debt",
                  "eps_sen", "naps_rm", "dividend_sen", "segment_revenue_total_q"]:
        missing_fields[field] = [
            f"{r['ticker']} {r['year']}Q{r['quarter']}" for r in fin if r[field] in ("", None)
        ]

    out = {
        "pdfs": {
            "rows": len(pdf_checks),
            "ok": sum(1 for x in pdf_checks if x["ok"]),
            "failed": [x for x in pdf_checks if not x["ok"]],
            "total_pages": sum(x["pages_manifest"] for x in pdf_checks),
            "total_bytes": sum(x.get("bytes_on_disk", 0) for x in pdf_checks),
            "total_text_chars": sum(x["text_chars"] for x in pdf_checks),
            "zero_text": [x for x in pdf_checks if x["text_chars"] == 0],
        },
        "panel": {
            "rows": len(fin),
            "by_ticker": dict(Counter(r["ticker"] for r in fin)),
            "missing_fields": missing_fields,
        },
        "numbers": {
            "rows": len(nums),
            "reports": len(num_by_report),
            "duplicate_cell_keys": dup_keys,
        },
        "reconciliation": {
            "checks": len(recon),
            "mismatches": bad_recon,
            "mismatch_count": len(bad_recon),
        },
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: (v if k != "pdfs" else {kk: vv for kk, vv in v.items() if kk != "failed"}) for k, v in out.items()}, indent=2)[:4000])
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
