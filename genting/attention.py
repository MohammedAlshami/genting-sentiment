"""Free attention proxies: Wikipedia daily pageviews for Genting entities."""

from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone

from curl_cffi import requests as cr

from . import store

ARTICLES = {
    "Genting_Malaysia": "GENM",
    "Genting_Berhad": "GENTING",
    "Genting_Group": "GROUP",
    "Resorts_World_Genting": "RWG",
    "Lim_Kok_Thay": "CHAIRMAN",
}
BASE = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article"
HEADERS = {"User-Agent": "genting-sentiment-research/1.0 (public pageview analysis)"}


def fetch(article: str, start: str, end: str) -> list[dict]:
    url = f"{BASE}/en.wikipedia/all-access/user/{article}/daily/{start}/{end}"
    for attempt in range(4):
        resp = cr.get(url, impersonate="chrome", headers=HEADERS, timeout=40)
        if resp.status_code == 200:
            return resp.json().get("items", [])
        if resp.status_code == 404:
            return []
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"pageviews failed for {article}: {resp.status_code} {resp.text[:120]}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start", default="20241101")
    ap.add_argument("--end", default=datetime.now(timezone.utc).strftime("%Y%m%d"))
    ap.add_argument("--db")
    args = ap.parse_args(argv)

    conn = store.connect(args.db)
    total = 0
    for article, ticker in ARTICLES.items():
        items = fetch(article, args.start, args.end)
        for item in items:
            date = item["timestamp"][:4] + "-" + item["timestamp"][4:6] + "-" + item["timestamp"][6:8]
            conn.execute(
                """
                INSERT INTO attention (source, key, date, value, collected_at)
                VALUES ('wikipedia', ?, ?, ?, ?)
                ON CONFLICT(source, key, date) DO UPDATE SET
                    value=excluded.value, collected_at=excluded.collected_at
                """,
                (ticker, date, item.get("views", 0), store.utcnow()),
            )
            total += 1
        conn.commit()
        print(f"{article:<28} {ticker:<9} {len(items):>5} days")
        time.sleep(1)

    print(f"stored {total} pageview rows")
    # validation
    for ticker in ARTICLES.values():
        row = conn.execute(
            "SELECT COUNT(*) n, MIN(date) a, MAX(date) b, SUM(value) s FROM attention WHERE key=?",
            (ticker,),
        ).fetchone()
        print(f"  {ticker:<9} {row['n']:>4} days {row['a']} → {row['b']} total={row['s']:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
