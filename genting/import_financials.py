"""Import structured annual, quarterly and segment financials into SQLite."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from . import store

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

QUARTER_MONEY = [
    "revenue", "ebitda", "pbt", "net_profit", "net_profit_attributable",
    "minority_interest", "perpetual_securities", "finance_cost", "total_debt",
    "cash", "net_debt", "long_term_borrowings", "short_term_borrowings",
    "lease_liabilities", "total_assets", "total_equity",
]
QUARTER_PER_SHARE = ["eps_sen", "naps_rm", "dividend_sen"]


def _id(*parts: object) -> str:
    return "fin:" + hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:16]


def _upsert(conn, ticker, period, period_end, statement, metric, value, unit, source, page, raw):
    try:
        val = float(value) if value not in (None, "", "n/a", "-") else None
    except (TypeError, ValueError):
        val = None
    conn.execute(
        """
        INSERT INTO financials (id, ticker, period, period_end, statement, metric,
                                value, unit, source, page, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            value=excluded.value, period_end=excluded.period_end,
            unit=excluded.unit, source=excluded.source,
            page=excluded.page, raw_json=excluded.raw_json
        """,
        (_id("a", ticker, period, statement, metric), ticker, period, period_end,
         statement, metric, val, unit, source, page, json.dumps(raw)),
    )


def import_annual(conn) -> int:
    path = RAW / "financial_statements_annual.csv"
    n = 0
    for row in csv.DictReader(path.open()):
        _upsert(
            conn, row["ticker"], row["fiscal_year"], None, row["statement"],
            row["line_item"], row["value"], row["unit"], row["source_pdf"],
            row["page"], row,
        )
        n += 1
    conn.commit()
    return n


def import_quarterly(conn) -> int:
    path = RAW / "quarterly_financials.csv"
    n = 0
    for row in csv.DictReader(path.open()):
        period = f"{row['year']}Q{row['quarter']}"
        # The quarterly CSV is already normalised to RM million; its unit/scale columns are inconsistent.
        for metric in QUARTER_MONEY:
            if row.get(metric) not in (None, ""):
                _upsert(
                    conn, row["ticker"], period, None, "quarterly", metric,
                    float(row[metric]), "RM million",
                    row.get("source"), f"p{row.get('page')}", row,
                )
                n += 1
        for metric in QUARTER_PER_SHARE:
            if row.get(metric) not in (None, ""):
                unit = "RM" if metric == "naps_rm" else "sen"
                _upsert(
                    conn, row["ticker"], period, None, "quarterly", metric,
                    row[metric], unit, row.get("source"),
                    f"p{row.get('page')}", row,
                )
                n += 1
    conn.commit()
    return n


def import_segments(conn) -> int:
    path = RAW / "company_segments.csv"
    if not path.exists():
        return 0
    n = 0
    for row in csv.DictReader(path.open()):
        _upsert(
            conn, row["company"], row["period"], row.get("period_end"),
            "segment", f"segment:{row['segment']}:revenue", row["revenue"],
            "RM million", row.get("source_url"), None, row,
        )
        n += 1
    conn.commit()
    return n


def main() -> int:
    conn = store.connect()
    print("annual rows:", import_annual(conn))
    print("quarterly rows:", import_quarterly(conn))
    print("segment rows:", import_segments(conn))
    for row in conn.execute(
        "SELECT ticker, COUNT(*) n, MIN(period) a, MAX(period) b FROM financials GROUP BY ticker"
    ):
        print(f"  {row[0]}: {row[1]} rows ({row[2]} → {row[3]})")
    print("total financials:", conn.execute("SELECT COUNT(*) FROM financials").fetchone()[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
