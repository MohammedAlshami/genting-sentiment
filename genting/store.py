"""Generic storage for multi-source Genting data (v2).

Kept alongside the original Reddit-specific `threads`/`comments` tables so the
existing CLI keeps working while the broader corpus is imported here.
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "genting.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id           TEXT PRIMARY KEY,
    source       TEXT NOT NULL,
    channel      TEXT,
    native_id    TEXT NOT NULL,
    ticker       TEXT,
    title        TEXT,
    author       TEXT,
    author_id    TEXT,
    created_utc  INTEGER,
    url          TEXT,
    body         TEXT,
    score        INTEGER,
    num_comments INTEGER,
    lang         TEXT,
    time_confidence TEXT,
    collected_at TEXT NOT NULL,
    raw_json     TEXT,
    UNIQUE (source, native_id)
);

CREATE TABLE IF NOT EXISTS replies (
    id                TEXT PRIMARY KEY,
    source            TEXT NOT NULL,
    channel           TEXT,
    native_id         TEXT NOT NULL,
    post_native_id    TEXT NOT NULL,
    parent_native_id  TEXT,
    depth             INTEGER,
    author            TEXT,
    author_id         TEXT,
    created_utc       INTEGER,
    body              TEXT,
    score             INTEGER,
    url               TEXT,
    lang              TEXT,
    time_confidence   TEXT,
    collected_at      TEXT NOT NULL,
    raw_json          TEXT,
    UNIQUE (source, native_id)
);

CREATE INDEX IF NOT EXISTS idx_replies_post    ON replies(source, post_native_id);
CREATE INDEX IF NOT EXISTS idx_replies_created ON replies(created_utc);
CREATE INDEX IF NOT EXISTS idx_posts_created   ON posts(created_utc);

CREATE TABLE IF NOT EXISTS articles (
    id            TEXT PRIMARY KEY,
    source        TEXT NOT NULL,
    channel       TEXT,
    url           TEXT UNIQUE,
    title         TEXT,
    author        TEXT,
    published_utc INTEGER,
    body          TEXT,
    summary       TEXT,
    tickers       TEXT,
    lang          TEXT,
    collected_at  TEXT NOT NULL,
    raw_json      TEXT
);

CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_utc);

CREATE TABLE IF NOT EXISTS prices (
    symbol       TEXT NOT NULL,
    date         TEXT NOT NULL,
    open         REAL,
    high         REAL,
    low          REAL,
    close        REAL,
    adj_close    REAL,
    volume       INTEGER,
    source       TEXT,
    collected_at TEXT,
    PRIMARY KEY (symbol, date)
);

CREATE TABLE IF NOT EXISTS attention (
    source       TEXT NOT NULL,
    key          TEXT NOT NULL,
    date         TEXT NOT NULL,
    value        INTEGER,
    collected_at TEXT,
    PRIMARY KEY (source, key, date)
);

CREATE TABLE IF NOT EXISTS ownership (
    id            TEXT PRIMARY KEY,
    ticker        TEXT,
    holder        TEXT,
    role          TEXT,
    stake_pct     REAL,
    shares        INTEGER,
    as_of         TEXT,
    basis         TEXT,
    source_url    TEXT,
    source_detail TEXT,
    notes         TEXT,
    collected_at  TEXT,
    raw_json      TEXT
);

CREATE TABLE IF NOT EXISTS financials (
    id         TEXT PRIMARY KEY,
    ticker     TEXT,
    period     TEXT,
    period_end TEXT,
    statement  TEXT,
    metric     TEXT,
    value      REAL,
    unit       TEXT,
    source     TEXT,
    page       TEXT,
    raw_json   TEXT
);

CREATE TABLE IF NOT EXISTS company_actions (
    id                  TEXT PRIMARY KEY,
    company             TEXT,
    action_type         TEXT,
    announcement_date   TEXT,
    effective_date      TEXT,
    status              TEXT,
    title               TEXT,
    terms               TEXT,
    amount_rm           REAL,
    amount_usd          REAL,
    per_share_sen       REAL,
    price_per_share_rm  REAL,
    ratio               TEXT,
    subscription_price_rm REAL,
    dilution_pct        REAL,
    proceeds_use        TEXT,
    counterparty        TEXT,
    stake_before_pct    REAL,
    stake_after_pct     REAL,
    source_url          TEXT,
    raw_json            TEXT
);

CREATE INDEX IF NOT EXISTS idx_financials_ticker ON financials(ticker, period);
"""


def connect(path: str | os.PathLike[str] | None = None) -> sqlite3.Connection:
    db_path = Path(path or os.environ.get("GENTING_DB") or DEFAULT_DB)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    _ensure_columns(conn)
    return conn


def _ensure_columns(conn: sqlite3.Connection) -> None:
    """Additive migrations for databases created before a column existed."""
    for table in ("posts", "replies"):
        cols = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
        if "time_confidence" not in cols:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN time_confidence TEXT")
    conn.commit()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def make_id(source: str, native_id: str) -> str:
    return f"{source}:{native_id}"


def import_jsonl(conn: sqlite3.Connection, path: Path, source: str | None = None) -> dict:
    """Import one contract-compliant JSONL file. Returns counts."""
    stats = {"post": 0, "reply": 0, "article": 0, "skipped": 0}
    now = utcnow()

    with path.open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            kind = rec.get("record_type")
            src = source or rec.get("source")
            if not src:
                raise ValueError(f"{path}:{line_no}: missing source")

            if kind == "post":
                native = str(rec["native_id"])
                conn.execute(
                    """
                    INSERT INTO posts (id, source, channel, native_id, ticker, title,
                                       author, author_id, created_utc, url, body, score,
                                       num_comments, lang, time_confidence,
                                       collected_at, raw_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(source, native_id) DO UPDATE SET
                        channel=excluded.channel, ticker=excluded.ticker,
                        title=excluded.title, author=excluded.author,
                        author_id=excluded.author_id, created_utc=excluded.created_utc,
                        url=excluded.url, body=excluded.body, score=excluded.score,
                        num_comments=excluded.num_comments, lang=excluded.lang,
                        time_confidence=excluded.time_confidence,
                        collected_at=excluded.collected_at, raw_json=excluded.raw_json
                    """,
                    (
                        make_id(src, native), src, rec.get("channel"), native,
                        rec.get("ticker"), rec.get("title"), rec.get("author"),
                        rec.get("author_id"), rec.get("created_utc"), rec.get("url"),
                        rec.get("body"), rec.get("score"), rec.get("num_comments"),
                        rec.get("lang"),
                        rec.get("time_confidence") or (rec.get("raw") or {}).get("time_confidence"),
                        now, json.dumps(rec.get("raw") or {}),
                    ),
                )
                stats["post"] += 1
            elif kind == "reply":
                native = str(rec["native_id"])
                conn.execute(
                    """
                    INSERT INTO replies (id, source, channel, native_id, post_native_id,
                                         parent_native_id, depth, author, author_id,
                                         created_utc, body, score, url, lang,
                                         time_confidence, collected_at, raw_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(source, native_id) DO UPDATE SET
                        channel=excluded.channel, post_native_id=excluded.post_native_id,
                        parent_native_id=excluded.parent_native_id, depth=excluded.depth,
                        author=excluded.author, author_id=excluded.author_id,
                        created_utc=excluded.created_utc, body=excluded.body,
                        score=excluded.score, url=excluded.url, lang=excluded.lang,
                        time_confidence=excluded.time_confidence,
                        collected_at=excluded.collected_at, raw_json=excluded.raw_json
                    """,
                    (
                        make_id(src, native), src, rec.get("channel"), native,
                        str(rec["post_native_id"]), rec.get("parent_native_id"),
                        rec.get("depth"), rec.get("author"), rec.get("author_id"),
                        rec.get("created_utc"), rec.get("body"), rec.get("score"),
                        rec.get("url"), rec.get("lang"),
                        rec.get("time_confidence") or (rec.get("raw") or {}).get("time_confidence"),
                        now, json.dumps(rec.get("raw") or {}),
                    ),
                )
                stats["reply"] += 1
            elif kind == "article":
                url = rec["url"]
                conn.execute(
                    """
                    INSERT INTO articles (id, source, channel, url, title, author,
                                          published_utc, body, summary, tickers, lang,
                                          collected_at, raw_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(url) DO UPDATE SET
                        source=excluded.source, channel=excluded.channel,
                        title=excluded.title, author=excluded.author,
                        published_utc=excluded.published_utc, body=excluded.body,
                        summary=excluded.summary, tickers=excluded.tickers,
                        lang=excluded.lang, collected_at=excluded.collected_at,
                        raw_json=excluded.raw_json
                    """,
                    (
                        make_id(src, rec.get("native_id") or url), src,
                        rec.get("channel"), url, rec.get("title"), rec.get("author"),
                        rec.get("published_utc"), rec.get("body"), rec.get("summary"),
                        json.dumps(rec.get("tickers") or []), rec.get("lang"), now,
                        json.dumps(rec.get("raw") or {}),
                    ),
                )
                stats["article"] += 1
            else:
                stats["skipped"] += 1
    conn.commit()
    return stats
