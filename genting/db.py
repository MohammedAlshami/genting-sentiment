"""SQLite storage for collected threads and comments."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "genting.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS threads (
    id            TEXT PRIMARY KEY,
    subreddit     TEXT,
    title         TEXT,
    author        TEXT,
    created_utc   INTEGER,
    score         INTEGER,
    upvote_ratio  REAL,
    num_comments  INTEGER,
    permalink     TEXT,
    url           TEXT,
    selftext      TEXT,
    flair         TEXT,
    fetched_at    TEXT NOT NULL,
    raw_json      TEXT
);

CREATE TABLE IF NOT EXISTS comments (
    id                TEXT PRIMARY KEY,
    thread_id         TEXT NOT NULL REFERENCES threads(id),
    parent_id         TEXT,
    depth             INTEGER,
    author            TEXT,
    created_utc       INTEGER,
    score             INTEGER,
    body              TEXT,
    permalink         TEXT,
    is_submitter      INTEGER,
    controversiality  INTEGER,
    fetched_at        TEXT NOT NULL,
    raw_json          TEXT
);

CREATE INDEX IF NOT EXISTS idx_comments_thread  ON comments(thread_id);
CREATE INDEX IF NOT EXISTS idx_comments_created ON comments(created_utc);
CREATE INDEX IF NOT EXISTS idx_threads_created  ON threads(created_utc);

CREATE TABLE IF NOT EXISTS collection_runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source      TEXT NOT NULL,
    kind        TEXT NOT NULL,
    target      TEXT,
    started_at  TEXT NOT NULL,
    finished_at TEXT,
    items       INTEGER DEFAULT 0,
    notes       TEXT
);
"""


def connect(path: str | os.PathLike[str] | None = None) -> sqlite3.Connection:
    db_path = Path(path or os.environ.get("GENTING_DB") or DEFAULT_DB)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def upsert_thread(conn: sqlite3.Connection, post: dict) -> None:
    conn.execute(
        """
        INSERT INTO threads (id, subreddit, title, author, created_utc, score,
                             upvote_ratio, num_comments, permalink, url, selftext,
                             flair, fetched_at, raw_json)
        VALUES (:id, :subreddit, :title, :author, :created_utc, :score,
                :upvote_ratio, :num_comments, :permalink, :url, :selftext,
                :flair, :fetched_at, :raw_json)
        ON CONFLICT(id) DO UPDATE SET
            score        = excluded.score,
            upvote_ratio = excluded.upvote_ratio,
            num_comments = excluded.num_comments,
            selftext     = excluded.selftext,
            fetched_at   = excluded.fetched_at,
            raw_json     = excluded.raw_json
        """,
        {
            "id": post["id"],
            "subreddit": post.get("subreddit"),
            "title": post.get("title"),
            "author": post.get("author"),
            "created_utc": post.get("created_utc"),
            "score": post.get("score"),
            "upvote_ratio": post.get("upvote_ratio"),
            "num_comments": post.get("num_comments"),
            "permalink": post.get("permalink"),
            "url": post.get("url"),
            "selftext": post.get("selftext"),
            "flair": post.get("link_flair_text"),
            "fetched_at": utcnow(),
            "raw_json": json.dumps(post),
        },
    )


def upsert_comment(conn: sqlite3.Connection, thread_id: str, comment: dict) -> None:
    conn.execute(
        """
        INSERT INTO comments (id, thread_id, parent_id, depth, author, created_utc,
                              score, body, permalink, is_submitter,
                              controversiality, fetched_at, raw_json)
        VALUES (:id, :thread_id, :parent_id, :depth, :author, :created_utc,
                :score, :body, :permalink, :is_submitter,
                :controversiality, :fetched_at, :raw_json)
        ON CONFLICT(id) DO UPDATE SET
            score        = excluded.score,
            body         = excluded.body,
            fetched_at   = excluded.fetched_at,
            raw_json     = excluded.raw_json
        """,
        {
            "id": comment["id"],
            "thread_id": thread_id,
            "parent_id": comment.get("parent_id"),
            "depth": comment.get("depth"),
            "author": comment.get("author"),
            "created_utc": comment.get("created_utc"),
            "score": comment.get("score"),
            "body": comment.get("body"),
            "permalink": comment.get("permalink"),
            "is_submitter": int(bool(comment.get("is_submitter"))),
            "controversiality": comment.get("controversiality"),
            "fetched_at": utcnow(),
            "raw_json": json.dumps(comment),
        },
    )


def start_run(conn: sqlite3.Connection, source: str, kind: str, target: str) -> int:
    cur = conn.execute(
        "INSERT INTO collection_runs (source, kind, target, started_at) VALUES (?, ?, ?, ?)",
        (source, kind, target, utcnow()),
    )
    conn.commit()
    return int(cur.lastrowid)


def finish_run(conn: sqlite3.Connection, run_id: int, items: int, notes: str = "") -> None:
    conn.execute(
        "UPDATE collection_runs SET finished_at = ?, items = ?, notes = ? WHERE id = ?",
        (utcnow(), items, notes, run_id),
    )
    conn.commit()


def get_thread(conn: sqlite3.Connection, thread_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM threads WHERE id = ?", (thread_id,)).fetchone()


def get_comments(conn: sqlite3.Connection, thread_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM comments WHERE thread_id = ? ORDER BY created_utc, id",
        (thread_id,),
    ).fetchall()
