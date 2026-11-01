"""Daily OHLCV for the two Malaysian Genting counters, last 12 months."""

from __future__ import annotations

import argparse
import json
import time
from datetime import date, datetime, timezone

from curl_cffi import requests as cr

from . import store

SYMBOLS = {
    "3182.KL": "GENTING",
    "4715.KL": "GENM",
}
HOSTS = [
    "https://query1.finance.yahoo.com",
    "https://query2.finance.yahoo.com",
]
HEADERS = {"Accept": "application/json", "Accept-Language": "en-US,en;q=0.9"}


def fetch_chart(symbol: str, range_: str = "1y", interval: str = "1d", retries: int = 6) -> dict:
    last: Exception | None = None
    for attempt in range(retries):
        host = HOSTS[attempt % len(HOSTS)]
        url = f"{host}/v8/finance/chart/{symbol}"
        try:
            resp = cr.get(
                url,
                params={"range": range_, "interval": interval, "events": "div,splits"},
                impersonate="chrome",
                headers=HEADERS,
                timeout=40,
            )
            if resp.status_code == 200:
                return resp.json()
            last = RuntimeError(f"{symbol}: HTTP {resp.status_code} {resp.text[:120]}")
        except Exception as exc:  # network / TLS
            last = exc
        time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"could not fetch {symbol}: {last}")


def store_chart(conn, symbol: str, payload: dict, ticker: str) -> dict:
    result = payload["chart"]["result"][0]
    meta = result["meta"]
    timestamps = result.get("timestamp") or []
    quote = (result.get("indicators", {}).get("quote") or [{}])[0]
    adj = ((result.get("indicators", {}).get("adjclose") or [{}])[0]).get("adjclose")

    rows = 0
    for i, ts in enumerate(timestamps):
        date = datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d")
        o, h, l, c = (quote.get(k, [None] * len(timestamps))[i] for k in ("open", "high", "low", "close"))
        if c is None:
            continue
        o = round(o, 3) if o is not None else None
        h = round(h, 3) if h is not None else None
        l = round(l, 3) if l is not None else None
        c = round(c, 3)
        adj_close = round(adj[i], 4) if adj and adj[i] is not None else None
        conn.execute(
            """
            INSERT INTO prices (symbol, date, open, high, low, close, adj_close,
                                volume, source, collected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol, date) DO UPDATE SET
                open=excluded.open, high=excluded.high, low=excluded.low,
                close=excluded.close, adj_close=excluded.adj_close,
                volume=excluded.volume, source=excluded.source,
                collected_at=excluded.collected_at
            """,
            (
                ticker, date, o, h, l, c,
                adj_close,
                quote.get("volume", [None] * len(timestamps))[i],
                "yahoo",
                store.utcnow(),
            ),
        )
        rows += 1
    conn.commit()
    return {
        "ticker": ticker,
        "symbol": symbol,
        "rows": rows,
        "first": datetime.fromtimestamp(timestamps[0], timezone.utc).date().isoformat() if timestamps else None,
        "last": datetime.fromtimestamp(timestamps[-1], timezone.utc).date().isoformat() if timestamps else None,
        "currency": meta.get("currency"),
    }


def validate(conn) -> list[str]:
    problems: list[str] = []
    for ticker in SYMBOLS.values():
        rows = conn.execute(
            "SELECT * FROM prices WHERE symbol=? ORDER BY date", (ticker,)
        ).fetchall()
        if len(rows) < 200:
            problems.append(f"{ticker}: only {len(rows)} rows")
            continue
        last = rows[-1]["date"]
        days = (datetime.now(timezone.utc).date() - date.fromisoformat(last)).days
        if days > 7:
            problems.append(f"{ticker}: last price is {days} days old ({last})")
        for r in rows:
            if not (r["low"] <= r["open"] <= r["high"] and r["low"] <= r["close"] <= r["high"]):
                problems.append(f"{ticker} {r['date']}: OHLC out of order")
                break
            if r["close"] <= 0:
                problems.append(f"{ticker} {r['date']}: non-positive close")
                break
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--range", default="1y")
    ap.add_argument("--db")
    args = ap.parse_args(argv)

    conn = store.connect(args.db)
    for symbol, ticker in SYMBOLS.items():
        payload = fetch_chart(symbol, range_=args.range)
        summary = store_chart(conn, symbol, payload, ticker)
        print(json.dumps(summary))
        time.sleep(1.5)

    problems = validate(conn)
    for p in problems:
        print(f"WARN {p}")
    print("OK" if not problems else f"{len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
