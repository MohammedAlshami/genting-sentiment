#!/usr/bin/env python3
"""Aggregate LLM sentiment into monthly series and a quality report."""

from __future__ import annotations

import csv
import json
import sqlite3
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "genting.db"
OUT_CSV = ROOT / "analysis" / "12_llm_sentiment_monthly.csv"
OUT_TICKER_CSV = ROOT / "analysis" / "12b_llm_sentiment_monthly_by_ticker.csv"
OUT_SOURCE_CSV = ROOT / "analysis" / "12c_llm_sentiment_by_source.csv"
OUT_REPORT = ROOT / "analysis" / "13_llm_sentiment_report.md"
OUT_EXAMPLES = ROOT / "analysis" / "14_llm_sentiment_examples.md"
MYT = timezone(timedelta(hours=8))


def month_of(ts: int) -> str:
    return datetime.fromtimestamp(ts, MYT).strftime("%Y-%m")


def main() -> None:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    total_replies = conn.execute("SELECT count(*) FROM replies").fetchone()[0]
    total_scored = conn.execute("SELECT count(*) FROM sentiment_llm").fetchone()[0]
    rows = conn.execute(
        """
        SELECT s.reply_id, s.score, s.label, s.confidence, s.model, s.prompt_version,
               COALESCE(s.ticker, r.channel, 'UNKNOWN') AS ticker,
               r.source, r.channel, r.created_utc, r.body
        FROM sentiment_llm s
        JOIN replies r ON r.id = s.reply_id
        ORDER BY r.created_utc
        """
    ).fetchall()
    if not rows:
        raise SystemExit("no classified rows yet")

    monthly: dict[str, list[sqlite3.Row]] = defaultdict(list)
    monthly_ticker: dict[tuple[str, str], list[sqlite3.Row]] = defaultdict(list)
    by_source: dict[str, list[sqlite3.Row]] = defaultdict(list)
    for row in rows:
        month = month_of(row["created_utc"])
        ticker = row["ticker"] if row["ticker"] in ("GENTING", "GENM") else "OTHER"
        monthly[month].append(row)
        monthly_ticker[(month, ticker)].append(row)
        by_source[row["source"]].append(row)

    def summarize(items: list[sqlite3.Row]) -> dict:
        scores = [r["score"] for r in items]
        confs = [r["confidence"] for r in items]
        labels = Counter(r["label"] for r in items)
        n = len(items)
        weighted = (
            sum(r["score"] * r["confidence"] for r in items) / sum(confs) if sum(confs) else 0
        )
        return {
            "n": n,
            "mean": statistics.fmean(scores),
            "weighted": weighted,
            "bull": labels.get("bullish", 0) / n,
            "bear": labels.get("bearish", 0) / n,
            "neutral": labels.get("neutral", 0) / n,
            "conf": statistics.fmean(confs),
        }

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            ["month", "n", "mean_score", "confidence_weighted", "bullish_share",
             "bearish_share", "neutral_share", "mean_confidence"]
        )
        for month in sorted(monthly):
            s = summarize(monthly[month])
            w.writerow(
                [month, s["n"], f"{s['mean']:.4f}", f"{s['weighted']:.4f}",
                 f"{s['bull']:.3f}", f"{s['bear']:.3f}", f"{s['neutral']:.3f}",
                 f"{s['conf']:.3f}"]
            )

    with OUT_TICKER_CSV.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(
            ["month", "ticker", "n", "mean_score", "bullish_share", "bearish_share",
             "neutral_share"]
        )
        for (month, ticker) in sorted(monthly_ticker):
            s = summarize(monthly_ticker[(month, ticker)])
            w.writerow(
                [month, ticker, s["n"], f"{s['mean']:.4f}", f"{s['bull']:.3f}",
                 f"{s['bear']:.3f}", f"{s['neutral']:.3f}"]
            )

    with OUT_SOURCE_CSV.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["source", "n", "mean_score", "bullish_share", "bearish_share",
                    "neutral_share", "mean_confidence"])
        for source in sorted(by_source, key=lambda k: -len(by_source[k])):
            s = summarize(by_source[source])
            w.writerow(
                [source, s["n"], f"{s['mean']:.4f}", f"{s['bull']:.3f}",
                 f"{s['bear']:.3f}", f"{s['neutral']:.3f}", f"{s['conf']:.3f}"]
            )

    # Agreement with the existing VADER/lexicon series, where months overlap.
    vader_path = ROOT / "analysis" / "07_sentiment_monthly.csv"
    agreement_lines = []
    if vader_path.exists():
        vader = {}
        with vader_path.open() as fh:
            for r in csv.DictReader(fh):
                vader[r["month"]] = (float(r["mean_sentiment"]), int(r["scored"]))
        pairs = [
            (month, summarize(monthly[month])["mean"] * 2 - 1, vader[month][0])
            for month in monthly
            if month in vader
        ]
        if len(pairs) >= 3:
            xs = [p[1] for p in pairs]
            ys = [p[2] for p in pairs]
            mx, my = statistics.fmean(xs), statistics.fmean(ys)
            num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
            den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
            corr = num / den if den else 0
            diffs = [a - b for _, a, b in pairs]
            agreement_lines = [
                f"- Overlap months: **{len(pairs)}**",
                f"- Pearson correlation with the lexicon score: **{corr:.3f}**",
                f"- Mean difference (LLM rescaled to −1…+1, minus lexicon): **{statistics.fmean(diffs):+.3f}**",
                f"- Largest gap: **{max(pairs, key=lambda p: abs(p[1] - p[2]))[0]}**",
            ]

    label_counts = Counter(r["label"] for r in rows)
    conf_buckets = Counter(
        "high" if r["confidence"] >= 0.75 else "medium" if r["confidence"] >= 0.5 else "low"
        for r in rows
    )
    model_counts = Counter(r["model"] for r in rows)
    months = sorted(monthly)
    latest = summarize(monthly[months[-1]])

    lines = [
        "# LLM sentiment classification",
        "",
        "## Coverage",
        f"- Replies in the corpus: **{total_replies:,}**",
        f"- Replies classified by the LLM: **{total_scored:,}** "
        f"({total_scored / total_replies * 100:.1f}%)",
        f"- Months covered: **{months[0]} → {months[-1]}** ({len(months)} months)",
        f"- Labels: bullish {label_counts.get('bullish', 0):,}, "
        f"bearish {label_counts.get('bearish', 0):,}, neutral {label_counts.get('neutral', 0):,}",
        f"- Confidence: high {conf_buckets['high']:,}, medium {conf_buckets['medium']:,}, "
        f"low {conf_buckets['low']:,}",
        "",
        "## Model",
        *[f"- `{model}`: {count:,} replies" for model, count in model_counts.most_common()],
        "",
        "Method: each reply was sent with its ticker, date, thread title and parent comment. "
        "The model assigned an integer level 0–10 (0 = maximally bearish, 5 = neutral, "
        "10 = maximally bullish), stored as score/10. Labels: 0–4 bearish, 5 neutral, "
        "6–10 bullish. Full rubric in `scripts/llm_classify.py` (v3).",
        "",
        "## Latest month",
        f"- {months[-1]}: mean {latest['mean']:+.3f}, bullish {latest['bull']:.1%}, "
        f"bearish {latest['bear']:.1%}, neutral {latest['neutral']:.1%} (n={latest['n']:,})",
        "",
        "## Agreement with the lexicon method",
        *(agreement_lines or ["- Not enough overlap to compare."]),
        "",
        "## Caveats",
        "- This is a model annotation, not a human-labelled gold set. A 200-item hand audit is recommended.",
        "- YouTube/TikTok comments are often about the video rather than the stock; the prompt scores those neutral.",
        "- Channel-level ticker is used where a reply does not name a stock.",
        "- Confidence is the model's own; it is not calibrated.",
        "",
        "## Files",
        "- `analysis/12_llm_sentiment_monthly.csv`",
        "- `analysis/12b_llm_sentiment_monthly_by_ticker.csv`",
        "- `analysis/12c_llm_sentiment_by_source.csv`",
        "- `analysis/14_llm_sentiment_examples.md`",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n")

    # Examples: top/bottom score per quarter, one per direction.
    buckets: dict[tuple[str, str], list[sqlite3.Row]] = defaultdict(list)
    for row in rows:
        dt = datetime.fromtimestamp(row["created_utc"], MYT)
        quarter = f"{dt.year}-Q{(dt.month - 1) // 3 + 1}"
        buckets[(quarter, row["label"])].append(row)
    ex = ["# LLM sentiment examples", ""]
    for (quarter, label) in sorted(buckets):
        if label == "neutral":
            continue
        items = sorted(
            buckets[(quarter, label)],
            key=lambda r: (abs(r["score"]), r["confidence"]),
            reverse=True,
        )[:2]
        ex.append(f"## {quarter} · {label}")
        for item in items:
            body = " ".join((item["body"] or "").split())[:260]
            ex.append(
                f"- `{item['score']:+.2f}` ({item['confidence']:.2f}) "
                f"{item['source']}/{item['channel']}: {body}"
            )
        ex.append("")
    OUT_EXAMPLES.write_text("\n".join(ex))

    print(json.dumps({
        "replies": total_replies,
        "classified": total_scored,
        "months": [months[0], months[-1]],
        "labels": dict(label_counts),
        "sources": len(by_source),
        "files": [str(OUT_CSV), str(OUT_REPORT), str(OUT_EXAMPLES)],
    }, indent=2))


if __name__ == "__main__":
    main()
