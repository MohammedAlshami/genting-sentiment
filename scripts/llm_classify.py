#!/usr/bin/env python3
"""LLM sentiment classification for Genting forum replies.

Uses OpenRouter's DeepSeek Flash (cheapest DeepSeek chat model) with reasoning
disabled. Every request gets the ticker, date, thread title, parent comment and
the comment itself, so short replies like "agree" or "sell" are interpretable.

Resumable: results go into the sentiment_llm table; classified replies are
skipped on restart. Also writes per-batch JSONL under data/llm_sentiment/.

Usage:
    python3 scripts/llm_classify.py --limit 100          # pilot
    python3 scripts/llm_classify.py --workers 8
    python3 scripts/llm_classify.py --shard 0 --shards 2  # parallel process
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "genting.db"
OUT_DIR = ROOT / "data" / "llm_sentiment"
AUTH = Path("/home/shami/.local/share/opencode/auth.json")
API = "https://openrouter.ai/api/v1/chat/completions"

MODEL = os.environ.get("GENTING_LLM_MODEL", "~deepseek/deepseek-flash-latest")
FALLBACK = "deepseek/deepseek-v4.1-flash"
PROMPT_VERSION = "v2"
MYT = timezone(timedelta(hours=8))

SYSTEM = """You are a financial sentiment annotator for a Malaysian retail-investor study of Genting Berhad (GENTING, 3182) and Genting Malaysia (GENM, 4715).

TASK
Assign an integer sentiment LEVEL from 0 to 10 for the stock named in the item header.
0 = maximally bearish, 5 = neutral, 10 = maximally bullish.
Judge the author's view over the next 1-3 months unless they state another horizon.

LEVELS
0 Total collapse: expects ruin, delisting or zero; urges exit at any price. "going to zero", "bankrupt", "worthless".
1 Very strong bearish: expects a very large fall or urgent exit; explicit severe downside. "sell before 1.00", "rights issue will crush it".
2 Strong bearish: expects a clear decline and recommends selling or avoiding; cites debt, dilution, weak results or licence risk.
3 Moderate bearish: expects weakness or drift lower; sceptical, no catalyst. "will drift to 1.20", "management has no plan".
4 Mild bearish: leans negative with low conviction; doubt, caution, "wait", "risky", "not yet".
5 Neutral: no directional view. Facts, price quotes without a view, questions, jokes, emoji-only, thanks, spam, off-topic, moral/religious comments with no price implication, balanced bull/bear.
6 Mild bullish: leans positive, low conviction; holding, "looks cheap", "wait for recovery", results okay.
7 Moderate bullish: expects upside and is willing to act; buy/add/average down, undervalued, "buy the dip", "2.35 is too low, don't sell".
8 Strong bullish: high conviction, meaningful upside, explicit catalyst or target. "rally to 2.00", "re-rate".
9 Very strong bullish: extreme conviction or target. "load up", "multi-bagger", "won't see this price again".
10 Maximal bullish: certainty of a rally, all-in, no risk acknowledged, fantastical target.

DECISION PROCEDURE
1 Identify the stock from the header. If the comment discusses only the other Genting entity, score 5.
2 Is there a directional view (price, valuation, buy/sell/hold, expected corporate-action impact)? If no -> 5.
3 Grade the action/expectation: sell/avoid 0-3; hold/wait 6; buy/add 7-9; certainty/extreme 10.
4 Grade conviction: hedges pull toward 5; certainty pushes to the extremes.
5 Use the thread title and parent comment for short replies.
6 Invert sarcasm.
7 Do not use outside facts.

RULES
- Sentiment toward the stock, not tone. Angry criticism of management is bearish only if it implies weaker earnings or price; otherwise 4-5.
- Buy/sell/hold calls, price targets and views on debt, dilution or rights issues are strong signals.
- A question is 5 unless it clearly implies a view.
- English, Malay, Chinese, Manglish: read all.
- Short reply: "agree" inherits the parent level; "wrong" mirrors it (10 - parent level).
- Courtesy/emoji/spam/off-topic -> 5 even with high confidence.
- Do not score an offer price as bearish just because it is low. "2.35 is too low, don't sell" = 6-7. "2.35 is low but I'm selling" = 3-4.
- "Rights issue is dilution, sell" = 2. "Rights issue lets me average down" = 6.
- "Debt is high but cash flow covers it" = 5-6. "Debt is unsustainable" = 2.
- "Management is overpaid" with no earnings/price link = 4-5. "Management is incompetent, earnings will fall" = 3.
- "Casino is haram" = 5 unless demand destruction is argued.
- "1.99 lol" = 5 (price quote), 4 only if mocking a fall.
- "Will gap down tomorrow" = 2. "Limit up tomorrow" = 8.

CONFIDENCE
0.90-1.00 explicit direction/action, no ambiguity.
0.75-0.89 clear, minor ambiguity.
0.60-0.74 implicit but readable.
0.40-0.59 mixed/weak lean.
0.00-0.39 guessing; prefer 5.
Confidence is confidence in the rating, not strength of sentiment. A neutral off-topic comment can be 0.95.

OUTPUT
Return strict JSON, no markdown: {"r":[[i,level,confidence],...]}
i = item number, level = integer 0-10, confidence = 0-1. Include every item exactly once."""

def load_key() -> str:
    data = json.loads(AUTH.read_text())
    return data["openrouter"]["key"]


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB, timeout=60)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=60000")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sentiment_llm (
            reply_id TEXT PRIMARY KEY,
            model TEXT NOT NULL,
            prompt_version TEXT NOT NULL,
            label TEXT NOT NULL,
            score REAL NOT NULL,
            confidence REAL NOT NULL,
            ticker TEXT,
            context_used INTEGER NOT NULL DEFAULT 0,
            classified_at INTEGER NOT NULL,
            raw_json TEXT
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sentiment_llm_label ON sentiment_llm(label)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sentiment_llm_score ON sentiment_llm(score)")
    conn.commit()
    return conn


def clean(text: str | None, limit: int) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def label_for(level: int) -> str:
    if level >= 6:
        return "bullish"
    if level <= 4:
        return "bearish"
    return "neutral"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB, timeout=60)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=60000")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sentiment_llm (
            reply_id TEXT PRIMARY KEY,
            model TEXT NOT NULL,
            prompt_version TEXT NOT NULL,
            label TEXT NOT NULL,
            score REAL NOT NULL,
            confidence REAL NOT NULL,
            ticker TEXT,
            context_used INTEGER NOT NULL DEFAULT 0,
            classified_at INTEGER NOT NULL,
            raw_json TEXT
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sentiment_llm_label ON sentiment_llm(label)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sentiment_llm_score ON sentiment_llm(score)")
    conn.commit()
    return conn


def clean(text: str | None, limit: int) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def fetch_rows(conn: sqlite3.Connection, limit: int, shard: int, shards: int, queue: str | None = None) -> list[dict]:
    where_shard = ""
    params: list[object] = []
    if shards > 1:
        where_shard = " AND (r.rowid % ?) = ?"
        params += [shards, shard]
    queue_join = f"JOIN {queue} q ON q.reply_id = r.id" if queue else ""
    sql = f"""
        SELECT r.id, r.source, r.channel, r.body, r.created_utc,
               r.parent_native_id, r.post_native_id,
               p.body AS parent_body,
               t.title AS thread_title, t.ticker AS thread_ticker
        FROM replies r
        {queue_join}
        LEFT JOIN replies p
          ON p.source = r.source AND p.channel = r.channel
         AND p.native_id = r.parent_native_id
        LEFT JOIN posts t
          ON t.source = r.source AND t.native_id = r.post_native_id
        WHERE NOT EXISTS (SELECT 1 FROM sentiment_llm s WHERE s.reply_id = r.id)
          AND length(trim(r.body)) > 0
          {where_shard}
        ORDER BY {"((r.rowid * 2654435761) % 100003)" if queue else "r.created_utc"}
        LIMIT ?
    """
    params.append(limit)
    cur = conn.execute(sql, params)
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def build_prompt(rows: list[dict]) -> str:
    lines = []
    for i, row in enumerate(rows, 1):
        ts = datetime.fromtimestamp(row["created_utc"], MYT).strftime("%Y-%m-%d")
        ticker = row["channel"] if row["channel"] in ("GENTING", "GENM") else (row["thread_ticker"] or "")
        title = clean(row["thread_title"], 70)
        head = f"#{i} {ticker} {ts}".strip()
        if title and title.lower() not in head.lower():
            head += f" | thread: {title}"
        lines.append(head)
        parent = clean(row["parent_body"], 180)
        if parent:
            lines.append(f"parent: {parent}")
        lines.append(f"text: {clean(row['body'], 500)}")
    return "\n".join(lines)


def call_api(key: str, prompt: str, max_tokens: int) -> tuple[str, dict]:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0,
        "reasoning": {"enabled": False},
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(
        API,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "genting-sentiment",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.load(resp)
    content = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
    return content, data.get("usage") or {}


def parse_scores(content: str, n: int) -> list[tuple[int, int, float]] | None:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        obj = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    raw = obj.get("r")
    if raw is None:
        for value in obj.values():
            if isinstance(value, list):
                raw = value
                break
    if not isinstance(raw, list):
        return None
    out: list[tuple[int, int, float]] = []
    for item in raw:
        if isinstance(item, dict):
            idx = item.get("i") or item.get("id")
            value = item.get("l", item.get("level", item.get("s", item.get("score"))))
            conf = item.get("c", item.get("confidence", 0.6))
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            idx, value = item[0], item[1]
            conf = item[2] if len(item) > 2 else 0.6
        else:
            continue
        try:
            idx = int(idx)
            value = float(value)
            if 0 < value < 1:
                value *= 10
            level = max(0, min(10, int(round(value))))
            conf = max(0.0, min(1.0, float(conf)))
        except (TypeError, ValueError):
            continue
        if 1 <= idx <= n:
            out.append((idx, level, conf))
    seen = {i for i, _, _ in out}
    if len(seen) < n:
        return None
    return sorted(out)


def classify_chunk(key: str, rows: list[dict], cost_lock: threading.Lock, state: dict) -> tuple[list[dict], dict, float]:
    prompt = build_prompt(rows)
    max_tokens = 24 * len(rows) + 40
    last_error = ""
    for attempt in range(4):
        model = MODEL if attempt < 3 else FALLBACK
        try:
            content, usage = call_api(key, prompt, max_tokens)
            parsed = parse_scores(content, len(rows))
            if parsed is not None:
                results = []
                for idx, level, conf in parsed:
                    row = rows[idx - 1]
                    results.append(
                        {
                            "reply_id": row["id"],
                            "score": level / 10,
                            "label": label_for(level),
                            "confidence": conf,
                            "ticker": row["channel"] if row["channel"] in ("GENTING", "GENM") else row["thread_ticker"],
                            "context_used": 1 if row["parent_body"] or row["thread_title"] else 0,
                            "raw_json": json.dumps({"i": idx, "l": level, "c": conf}),
                        }
                    )
                cost = float(usage.get("cost") or 0)
                with cost_lock:
                    state["cost"] += cost
                    state["tokens"] += int(usage.get("total_tokens") or 0)
                return results, usage, cost
            last_error = f"parse failed: {content[:160]}"
        except urllib.error.HTTPError as exc:
            body = exc.read()[:200].decode("utf-8", "ignore")
            last_error = f"HTTP {exc.code}: {body}"
            if exc.code == 401:
                raise SystemExit(f"FATAL {exc.code}: {body}")
            if exc.code == 402:
                time.sleep(6 + attempt * 6)
            else:
                time.sleep(2 + attempt * 3)
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)[:200]
            time.sleep(2 + attempt * 3)
        if attempt == 2 and len(rows) > 1:
            break
    raise RuntimeError(f"chunk failed ({len(rows)} rows): {last_error}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="max replies this run (0 = all)")
    ap.add_argument("--batch-size", type=int, default=20)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--max-cost", type=float, default=3.5)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    key = load_key()
    conn = connect()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cost_lock = threading.Lock()
    state = {"cost": 0.0, "tokens": 0, "done": 0, "failed": 0}
    started = time.time()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    remaining = args.limit or 10**9
    batch_no = 0
    while remaining > 0:
        rows = fetch_rows(conn, min(args.batch_size * args.workers * 2, remaining), args.shard, args.shards)
        if not rows:
            break
        chunks = [rows[i : i + args.batch_size] for i in range(0, len(rows), args.batch_size)]
        if args.dry_run:
            print(build_prompt(chunks[0])[:2000])
            return 0

        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(classify_chunk, key, chunk, cost_lock, state) for chunk in chunks]
            for future in futures:
                try:
                    results, usage, cost = future.result()
                except Exception as exc:  # noqa: BLE001
                    state["failed"] += 1
                    print(f"chunk error: {exc}", file=sys.stderr, flush=True)
                    continue

                now = int(time.time())
                with conn:
                    for item in results:
                        conn.execute(
                            """
                            INSERT OR REPLACE INTO sentiment_llm
                            (reply_id, model, prompt_version, label, score, confidence,
                             ticker, context_used, classified_at, raw_json)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                item["reply_id"], MODEL, PROMPT_VERSION, item["label"],
                                item["score"], item["confidence"], item["ticker"],
                                item["context_used"], now, item["raw_json"],
                            ),
                        )
                batch_no += 1
                path = OUT_DIR / f"{run_id}_shard{args.shard}_{batch_no:05d}.jsonl"
                with path.open("w", encoding="utf-8") as fh:
                    for item in results:
                        fh.write(json.dumps(item, ensure_ascii=False) + "\n")

                state["done"] += len(results)
                remaining -= len(results)
                if state["cost"] > args.max_cost:
                    print(f"cost cap hit: ${state['cost']:.4f}", file=sys.stderr)
                    remaining = 0

        if state["failed"] >= 15:
            print("too many chunk failures; stopping", file=sys.stderr, flush=True)
            break

        elapsed = max(1e-6, time.time() - started)
        print(
            f"classified {state['done']:,} | failed {state['failed']} | "
            f"cost ${state['cost']:.4f} | {state['tokens']:,} tok | "
            f"{state['done'] / elapsed:.1f}/s",
            flush=True,
        )

    print(json.dumps({"run_id": run_id, "done": state["done"], "failed": state["failed"], "cost": round(state["cost"], 6), "tokens": state["tokens"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
