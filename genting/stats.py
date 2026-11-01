"""Coverage report for the collected corpus."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from . import store


def month(ts: int | None) -> str:
    if not ts:
        return "unknown"
    return datetime.fromtimestamp(int(ts), timezone.utc).strftime("%Y-%m")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db")
    args = ap.parse_args(argv)
    conn = store.connect(args.db)

    print("== posts by source / ticker ==")
    for row in conn.execute(
        """SELECT source, ticker, COUNT(*) n, MIN(created_utc) first, MAX(created_utc) last
           FROM posts GROUP BY source, ticker ORDER BY n DESC"""
    ):
        print(
            f"{row['source']:<16} {str(row['ticker']):<8} {row['n']:>7}  "
            f"{month(row['first'])} → {month(row['last'])}"
        )

    print("\n== replies by source ==")
    for row in conn.execute(
        """SELECT source, COUNT(*) n, MIN(created_utc) first, MAX(created_utc) last,
                  SUM(CASE WHEN body IS NULL OR body IN ('','[deleted]','[removed]') THEN 1 ELSE 0 END) empty
           FROM replies GROUP BY source ORDER BY n DESC"""
    ):
        print(
            f"{row['source']:<16} {row['n']:>8}  {month(row['first'])} → {month(row['last'])}  "
            f"empty={row['empty']}"
        )

    print("\n== monthly reply volume (2-year grid; · = no data) ==")
    per_month: dict[str, Counter] = defaultdict(Counter)
    for row in conn.execute("SELECT source, created_utc FROM replies WHERE created_utc IS NOT NULL"):
        per_month[row["source"]][month(row["created_utc"])] += 1
    months = sorted({m for c in per_month.values() for m in c})
    header = "source".ljust(16) + "".join(m[-2:].rjust(6) for m in months)
    print(f"months {months[0]} → {months[-1]}" if months else "no replies")
    print(header)
    for source, counts in sorted(per_month.items(), key=lambda kv: -sum(kv[1].values())):
        cells = "".join((str(counts[m]) if counts.get(m) else "·").rjust(6) for m in months)
        print(source.ljust(16) + cells)

    print("\n== timestamp confidence ==")
    for row in conn.execute(
        """SELECT source, COALESCE(time_confidence,'exact') conf, COUNT(*) n
           FROM replies GROUP BY source, conf ORDER BY source, n DESC"""
    ):
        print(f"{row['source']:<16} {row['conf']:<14} {row['n']:>8}")

    print("\n== articles by publisher ==")
    for row in conn.execute(
        """SELECT source, COUNT(*) n, MIN(published_utc) first, MAX(published_utc) last
           FROM articles GROUP BY source ORDER BY n DESC"""
    ):
        print(f"{row['source']:<22} {row['n']:>5}  {month(row['first'])} → {month(row['last'])}")

    print("\n== prices ==")
    for row in conn.execute(
        """SELECT symbol, COUNT(*) n, MIN(date) first, MAX(date) last,
                  SUM(CASE WHEN close IS NULL THEN 1 ELSE 0 END) nulls
           FROM prices GROUP BY symbol ORDER BY symbol"""
    ):
        print(
            f"{row['symbol']:<10} {row['n']:>4} bars  {row['first']} → {row['last']}  "
            f"nulls={row['nulls']}"
        )

    print("\n== totals ==")
    for table in ("posts", "replies", "articles", "prices"):
        n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table:<10} {n:>8}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
