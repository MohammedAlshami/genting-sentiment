"""Import company events, filings and ownership records."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from . import store

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"


def import_ownership(conn, path: Path) -> int:
    n = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        key = "|".join(
            str(rec.get(k)) for k in ("ticker", "holder", "as_of", "basis", "role")
        )
        oid = "own:" + hashlib.sha1(key.encode()).hexdigest()[:16]
        conn.execute(
            """
            INSERT INTO ownership (id, ticker, holder, role, stake_pct, shares,
                as_of, basis, source_url, source_detail, notes, collected_at, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                stake_pct=excluded.stake_pct, shares=excluded.shares,
                as_of=excluded.as_of, source_detail=excluded.source_detail,
                notes=excluded.notes, collected_at=excluded.collected_at,
                raw_json=excluded.raw_json
            """,
            (
                oid, rec.get("ticker"), rec.get("holder"), rec.get("role"),
                rec.get("stake_pct"), rec.get("shares"), rec.get("as_of"),
                rec.get("basis"), rec.get("source_url"), rec.get("source_detail"),
                rec.get("notes"), store.utcnow(), json.dumps(rec),
            ),
        )
        n += 1
    conn.commit()
    return n


def main() -> int:
    conn = store.connect()
    for name in ("company_events.jsonl", "company_filings.jsonl"):
        path = RAW / name
        if not path.exists():
            print(f"skip {name} (missing)")
            continue
        stats = store.import_jsonl(conn, path)
        print(f"{name}: {stats}")

    path = RAW / "ownership.jsonl"
    if path.exists():
        print(f"ownership.jsonl: {import_ownership(conn, path)} rows")

    path = RAW / "company_actions.jsonl"
    if path.exists():
        n = 0
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            key = "|".join(str(rec.get(k)) for k in ("company", "action_type", "announcement_date", "title"))
            aid = "act:" + hashlib.sha1(key.encode()).hexdigest()[:16]
            conn.execute(
                """
                INSERT INTO company_actions (id, company, action_type, announcement_date,
                    effective_date, status, title, terms, amount_rm, amount_usd,
                    per_share_sen, price_per_share_rm, ratio, subscription_price_rm,
                    dilution_pct, proceeds_use, counterparty, stake_before_pct,
                    stake_after_pct, source_url, raw_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status=excluded.status, terms=excluded.terms,
                    amount_rm=excluded.amount_rm, amount_usd=excluded.amount_usd,
                    per_share_sen=excluded.per_share_sen,
                    price_per_share_rm=excluded.price_per_share_rm,
                    ratio=excluded.ratio,
                    subscription_price_rm=excluded.subscription_price_rm,
                    dilution_pct=excluded.dilution_pct,
                    proceeds_use=excluded.proceeds_use,
                    counterparty=excluded.counterparty,
                    stake_before_pct=excluded.stake_before_pct,
                    stake_after_pct=excluded.stake_after_pct,
                    source_url=excluded.source_url, raw_json=excluded.raw_json
                """,
                (
                    aid, rec.get("company"), rec.get("action_type"),
                    rec.get("announcement_date"), rec.get("effective_date"),
                    rec.get("status"), rec.get("title"), rec.get("terms"),
                    rec.get("amount_rm"), rec.get("amount_usd"),
                    rec.get("per_share_sen"), rec.get("price_per_share_rm"),
                    rec.get("ratio"), rec.get("subscription_price_rm"),
                    rec.get("dilution_pct"), rec.get("proceeds_use"),
                    rec.get("counterparty"), rec.get("stake_before_pct"),
                    rec.get("stake_after_pct"), rec.get("source_url"),
                    json.dumps(rec),
                ),
            )
            n += 1
        conn.commit()
        print(f"company_actions.jsonl: {n} rows")

    print("\ntotals:")
    for table in ("posts", "replies", "articles", "prices", "attention", "ownership", "financials", "company_actions"):
        print(f"  {table}: {conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
