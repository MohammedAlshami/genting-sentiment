#!/usr/bin/env python3
"""Sentiment classification through the OpenCode Go subscription.

This is the same task and prompt as llm_classify.py, but calls the local
OpenCode CLI (`opencode run --format json --model opencode-go/deepseek-v4.1-flash`)
instead of OpenRouter. The OpenRouter key is out of account credits; the Go
subscription still works.

Resumable through the sentiment_llm table. Each batch is written to
data/llm_sentiment/ as JSONL for audit.

Usage:
    python3 scripts/llm_classify_cli.py --limit 120 --workers 2
    python3 scripts/llm_classify_cli.py --workers 8 --batch-size 60
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import llm_classify as base  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "llm_sentiment"
CWD = Path("/tmp/opencode/classify_cwd")
MODEL = "opencode-go/deepseek-v4.1-flash#low"
PROMPT_VERSION = "v3-cli"


def run_cli(prompt: str) -> tuple[str, str]:
    cmd = [
        "opencode",
        "run",
        "--format",
        "json",
        "--model",
        MODEL,
        prompt,
    ]
    proc = subprocess.run(
        cmd,
        cwd=CWD,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"cli exit {proc.returncode}: {proc.stderr[-300:]}")
    texts = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "text":
            text = (event.get("part") or {}).get("text") or ""
            if text:
                texts.append(text)
    if not texts:
        raise RuntimeError(f"no text event: {proc.stdout[-300:]}")
    return texts[-1], proc.stdout


def classify_batch(rows: list[dict]) -> list[dict]:
    prompt = base.SYSTEM + "\n\nItems:\n" + base.build_prompt(rows)
    last_error = ""
    for attempt in range(3):
        try:
            content, _ = run_cli(prompt)
            parsed = base.parse_scores(content, len(rows))
            if parsed is not None:
                results = []
                for idx, level, conf in parsed:
                    row = rows[idx - 1]
                    results.append(
                        {
                            "reply_id": row["id"],
                            "score": level / 10,
                            "label": base.label_for(level),
                            "confidence": conf,
                            "ticker": row["channel"]
                            if row["channel"] in ("GENTING", "GENM")
                            else row["thread_ticker"],
                            "context_used": 1
                            if row["parent_body"] or row["thread_title"]
                            else 0,
                            "raw_json": json.dumps({"i": idx, "l": level, "c": conf}),
                        }
                    )
                return results
            last_error = f"parse incomplete ({len(rows)} items)"
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)[:300]
            time.sleep(2 + attempt * 3)
        if attempt == 1 and len(rows) > 1:
            mid = len(rows) // 2
            return classify_batch(rows[:mid]) + classify_batch(rows[mid:])
    raise RuntimeError(f"batch failed ({len(rows)}): {last_error}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--batch-size", type=int, default=60)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--max-minutes", type=float, default=0)
    ap.add_argument("--queue", default="")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    CWD.mkdir(parents=True, exist_ok=True)
    conn = base.connect()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()
    state = {"done": 0, "failed": 0, "batches": 0}
    started = time.time()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    remaining = args.limit or 10**9
    batch_no = 0

    while remaining > 0:
        if args.max_minutes and (time.time() - started) / 60 > args.max_minutes:
            break
        rows = base.fetch_rows(
            conn,
            min(args.batch_size * args.workers, remaining),
            args.shard,
            args.shards,
            args.queue or None,
        )
        if not rows:
            break
        chunks = [rows[i : i + args.batch_size] for i in range(0, len(rows), args.batch_size)]
        if args.dry_run:
            print(base.SYSTEM + "\n\nItems:\n" + base.build_prompt(chunks[0])[:3000])
            return 0

        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(classify_batch, chunk) for chunk in chunks]
            for future in futures:
                try:
                    results = future.result()
                except Exception as exc:  # noqa: BLE001
                    with lock:
                        state["failed"] += 1
                    print(f"batch error: {exc}", file=sys.stderr, flush=True)
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
                path = OUT_DIR / f"{run_id}_cli{args.shard}_{batch_no:05d}.jsonl"
                with path.open("w", encoding="utf-8") as fh:
                    for item in results:
                        fh.write(json.dumps(item, ensure_ascii=False) + "\n")

                with lock:
                    state["done"] += len(results)
                    state["batches"] += 1
                remaining -= len(results)

        elapsed = max(1e-6, time.time() - started)
        print(
            f"classified {state['done']:,} | batches {state['batches']} | "
            f"failed {state['failed']} | {state['done'] / elapsed:.1f}/s",
            flush=True,
        )
        if state["failed"] >= 20:
            print("too many failures; stopping", file=sys.stderr)
            break

    print(
        json.dumps(
            {
                "run_id": run_id,
                "done": state["done"],
                "failed": state["failed"],
                "minutes": round((time.time() - started) / 60, 1),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
