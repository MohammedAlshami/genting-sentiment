#!/usr/bin/env python3
"""Build data/raw/company_financials.csv (quarterly) and the annual companion CSV.

Values are RM million except EPS and dividend, which are sen per share.
EBITDA is the company-reported "adjusted EBITDA" from the results press release.
Total debt = long-term borrowings + short-term borrowings (excluding lease liabilities).
Net profit = profit for the period (including non-controlling interests).
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_quarterly import pairs, income_statement, ebitda_from_pr, txt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw"
MANIFEST = json.loads((ROOT / "data" / "company_docs" / "pdf_manifest.json").read_text())
HEADER = ["company", "period", "period_end", "revenue", "ebitda", "pbt", "net_profit",
          "finance_cost", "total_debt", "cash", "net_debt", "eps", "dividend", "source_url"]

# Dividends declared with the results for that quarter (sen per share).
DIVIDENDS = {
    ("GENTING", "4Q24"): 5.0,
    ("GENTING", "4Q25"): 5.0,
    ("GENM", "4Q24"): 4.0,
    ("GENM", "4Q25"): 7.0,
}

ANNUAL = [
    # company, period, period_end, revenue, ebitda, pbt, net_profit, finance_cost,
    # total_debt, cash, eps, dividend, source_url
    ("GENTING", "FY2024", "2024-12-31", 27717.0, 8781.8, 3300.3, 2021.3, 2099.6,
     39228.6, 22403.6, 22.93, 11.0,
     "https://www.genting.com/wp-content/uploads/2025/05/GENTING_IAR24v3.pdf"),
    ("GENTING", "FY2025", "2025-12-31", 27711.9, 7990.1, 2198.9, 1023.8, 2104.2,
     40806.7, 17996.1, -0.30, 5.0,
     "https://www.genting.com/wp-content/uploads/2026/07/GENTING-BERHAD_IAR2025v2.pdf"),
    ("GENM", "FY2024", "2024-12-31", 10911.8, 2910.4, 486.7, 162.1, 691.0,
     12220.8, 3536.6, 4.43, 10.0,
     "https://www.gentingmalaysia.com/wp-content/uploads/2025/04/GENTING_IAR2024_v2.pdf"),
    ("GENM", "FY2025", "2025-12-31", 11884.3, 3297.6, 985.0, 670.7, 828.2,
     12716.0, 2847.2, 13.32, 7.0,
     "https://www.gentingmalaysia.com/wp-content/uploads/2026/06/GENM_IAR_2025_v2.pdf"),
]


def period_from_title(title: str) -> tuple[str, str]:
    m = re.search(r"ended\s+(\d{2})/(\d{2})/(\d{4})", title or "")
    if not m:
        raise ValueError(f"no period in {title!r}")
    day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
    q = (month - 1) // 3 + 1
    return f"{q}Q{str(year)[-2:]}", f"{year:04d}-{month:02d}-{day:02d}"


def pdf_url_for(local_name: str) -> str:
    for rec in MANIFEST.values():
        if rec["local"].endswith(local_name):
            return rec["url"]
    raise KeyError(local_name)


def rows() -> list[dict]:
    out = []
    for ticker in ("GENTING", "GENM"):
        for key, report, press in pairs(ticker):
            title = next(v["title"] for v in MANIFEST.values()
                         if v["local"].endswith(report.stem + ".pdf"))
            period, period_end = period_from_title(title)
            inc = income_statement(txt(report))
            ebitda = ebitda_from_pr(txt(press))
            debt = round(inc["total_debt"], 1)
            cash = round(inc["cash"], 1)
            out.append({
                "company": ticker,
                "period": period,
                "period_end": period_end,
                "revenue": round(inc["revenue"], 1),
                "ebitda": round(ebitda, 1) if ebitda is not None else None,
                "pbt": round(inc["pbt"], 1),
                "net_profit": round(inc["net_profit"], 1),
                "finance_cost": round(inc["finance_cost"], 1),
                "total_debt": round(debt, 1),
                "cash": round(cash, 1),
                "net_debt": round(debt - cash, 1),
                "eps": inc["eps"],
                "dividend": DIVIDENDS.get((ticker, period), 0.0),
                "source_url": pdf_url_for(report.stem + ".pdf"),
            })
    out = [r for r in out if r["period_end"] >= "2024-11-02"]
    out.sort(key=lambda r: (r["company"], r["period_end"]))
    return out


def write_csv(path: Path, data: list[dict], header: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        for r in data:
            w.writerow({k: r[k] for k in header})


def main() -> int:
    q = rows()
    write_csv(OUT / "company_financials.csv", q, HEADER)
    annual = [dict(zip(HEADER, [
        c, p, pe, rev, eb, pbt, np, fc, td, cash, round(td - cash, 1), eps, div, url
    ])) for c, p, pe, rev, eb, pbt, np, fc, td, cash, eps, div, url in ANNUAL]
    write_csv(OUT / "company_financials_annual.csv", annual, HEADER)
    print(f"wrote {len(q)} quarterly rows and {len(annual)} annual rows")
    for r in q:
        print(r["company"], r["period"], r["revenue"], r["ebitda"], r["pbt"], r["net_profit"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
