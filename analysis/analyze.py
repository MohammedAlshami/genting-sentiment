"""Stage 1 analysis: audit, event grouping, price reactions, topic mix, keyword polarity."""

from __future__ import annotations

import csv
import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "genting.db"
OUT = ROOT / "analysis"
OUT.mkdir(exist_ok=True)

MONTHS = [
    "2024-11", "2024-12", "2025-01", "2025-02", "2025-03", "2025-04",
    "2025-05", "2025-06", "2025-07", "2025-08", "2025-09", "2025-10",
    "2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04",
    "2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10",
    "2026-11",
]


def month(ts: int | None) -> str:
    if not ts:
        return "unknown"
    return datetime.fromtimestamp(int(ts), timezone.utc).strftime("%Y-%m")


conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# ---------------------------------------------------------------- volume
replies = conn.execute(
    "SELECT source, created_utc, body FROM replies WHERE created_utc IS NOT NULL"
).fetchall()

volume: dict[str, Counter] = defaultdict(Counter)
for r in replies:
    volume[r["source"]][month(r["created_utc"])] += 1

with (OUT / "01_volume_monthly.csv").open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["source"] + MONTHS)
    for source in sorted(volume, key=lambda s: -sum(volume[s].values())):
        w.writerow([source] + [volume[source].get(m, 0) for m in MONTHS])

# ---------------------------------------------------------------- prices
prices = defaultdict(dict)
for r in conn.execute("SELECT symbol, date, close FROM prices ORDER BY date"):
    prices[r["symbol"]][r["date"]] = r["close"]

with (OUT / "02_prices_monthly.csv").open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["symbol", "month", "close"])
    for sym, series in prices.items():
        by_month: dict[str, float] = {}
        for d, c in series.items():
            by_month[d[:7]] = c
        for m in MONTHS:
            if m in by_month:
                w.writerow([sym, m, round(by_month[m], 3)])

# event reactions
ev = [
    ("2025-10-13", "RM2.35 privatisation offer"),
    ("2025-12-01", "Offer closes below 75%"),
    ("2025-12-16", "RWNYC licence awarded"),
    ("2026-05-01", "RWNYC opens as full casino"),
    ("2026-10-09", "RM1.25b rights issue announced"),
    ("2026-10-12", "22.87% single-day fall"),
]
event_rows = []
for sym, series in prices.items():
    dates = sorted(series)
    for date, label in ev:
        idx = next((i for i, d in enumerate(dates) if d >= date), None)
        if idx is None:
            continue
        base = series[dates[idx - 1]] if idx > 0 else series[dates[idx]]
        for horizon, days in [("1d", 1), ("5d", 5), ("20d", 20)]:
            j = min(idx + days - 1, len(dates) - 1)
            ret = (series[dates[j]] / base - 1) * 100
            event_rows.append([sym, date, label, horizon, dates[j], round(ret, 2)])

with (OUT / "03_event_reactions.csv").open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["symbol", "event_date", "event", "horizon", "end_date", "return_pct"])
    w.writerows(event_rows)

# ---------------------------------------------------------------- news grouping
NEWS_RULES = {
    "Privatisation / takeover": r"privatis|take-?over|take private|delist|75%|offer document|voluntary offer",
    "Rights issue / dilution": r"rights issue|cash call|renounceable|dilut|RM1\.25|fundrais",
    "Results / earnings": r"earnings|results|profit|revenue|q[1-4]|1h|fy|quarter",
    "Debt / ratings": r"debt|bond|rating|fitch|moody|s&p|downgrade|interest|refinanc|fallen angel|leverage",
    "New York / licence": r"new york|rwnyc|rwlv|downstate|licen[cs]e|casino",
    "Dividends": r"dividend|yield|payout",
    "Legal / regulatory": r"lawsuit|sue|fine|rav |rico|tax dispute|whistleblower|nevmada|attorney",
    "Management / ownership": r"ceo|chairman|board|director|lim kok thay|kien huat|stake",
    "Share price": r"shares? (fall|drop|plunge|slump|rise|jump|rally)|stock (fall|drop|plunge|rise)|lowest|record low",
    "Operations / resorts": r"resorts world|genting highlands|theme park|hotel|tourism|visitor",
}
news_rows = conn.execute(
    "SELECT published_utc, title, source, url FROM articles ORDER BY published_utc"
).fetchall()
news_by_cat: dict[str, Counter] = defaultdict(Counter)
news_examples: dict[str, list[tuple[str, str]]] = defaultdict(list)
for r in news_rows:
    text = (r["title"] or "").lower()
    for cat, pat in NEWS_RULES.items():
        if re.search(pat, text):
            news_by_cat[cat][month(r["published_utc"])] += 1
            if len(news_examples[cat]) < 6:
                news_examples[cat].append(
                    (datetime.fromtimestamp(r["published_utc"], timezone.utc).strftime("%Y-%m-%d"), r["title"])
                )

with (OUT / "04_news_events.csv").open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["category"] + MONTHS + ["total"])
    for cat in NEWS_RULES:
        row = [news_by_cat[cat].get(m, 0) for m in MONTHS]
        w.writerow([cat] + row + [sum(row)])

# ---------------------------------------------------------------- topics
TOPIC_RULES = {
    "debt": r"\bdebt\b|\bhutang\b|债务|负债|\binterest\b|\bfaedah\b|利息|\bloan\b|\bpinjaman\b",
    "rights_issue": r"rights issue|附加股|terbitan hak|cash call|dilut|\bcair\b|稀释|renounceable",
    "privatisation": r"privatis|take private|take-?over|delist|75%|私有化|收购|除牌",
    "new_york": r"new york|rwnyc|rwlv|resorts world new york|licen[cs]e|赌场|kasino|casino",
    "dividend": r"dividend|dividen|股息|yield|payout",
    "management": r"lim kok thay|\blkt\b|chairman|\bceo\b|\bboard\b|director|林国泰|管理层",
    "valuation": r"cheap|undervalu|book value|\bp/b\b|\bpb\b|murah|便宜|估值|价值",
    "politics_licence": r"pahang|\bpas\b|election|politic|政治|彭亨|licen[cs]e",
}
topic_counts: dict[str, Counter] = defaultdict(Counter)
total_by_month = Counter()
for r in replies:
    body = (r["body"] or "").lower()
    if not body:
        continue
    m = month(r["created_utc"])
    total_by_month[m] += 1
    for topic, pat in TOPIC_RULES.items():
        if re.search(pat, body):
            topic_counts[topic][m] += 1

with (OUT / "05_topic_share_monthly.csv").open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["topic"] + MONTHS)
    for topic in TOPIC_RULES:
        w.writerow([topic] + [round(topic_counts[topic].get(m, 0) / max(total_by_month[m], 1) * 100, 1) for m in MONTHS])

# ---------------------------------------------------------------- keyword polarity
BULL = [
    r"\bbuy\b", r"\bbuying\b", r"\baccumulat", r"\bundervalu", r"\bcheap\b", r"\bbargain\b",
    r"\bdividend", r"\byield\b", r"\brecover", r"\bturnaround\b", r"\bprofit", r"\bgrowth\b",
    r"\bstrong\b", r"\bbeat\b", r"\bupgrade", r"\brally\b", r"\brebound\b", r"\bbounce\b",
    r"\bupside\b", r"\bprivatis", r"\btake-?over", r"\boffer\b", r"\bnew york\b", r"\blicen[cs]e\b",
    r"\bexpansion\b", r"\bvalue\b", r"\bbullish\b", r"\bpositive\b", r"\bsupport\b", r"\bbottom\b",
    r"\bbeli\b", r"\btambah\b", r"\bmurah\b", r"\bdividen\b", r"\bpulih\b", r"\buntung\b", r"\bnaik\b",
    r"\bkukuh\b", r"\bpositif\b", r"\bpeluang\b", r"\btawaran\b", r"\blesen\b", r"\bkasino\b",
    r"买", r"加仓", r"便宜", r"股息", r"复苏", r"盈利", r"上涨", r"涨", r"升级", r"目标价",
    r"反弹", r"私有化", r"收购", r"赌场", r"牌照", r"价值", r"看涨", r"支撑", r"底部",
]
BEAR = [
    r"\bsell\b", r"\bselling\b", r"\bdump\b", r"\bdebt\b", r"\binterest\b", r"rights issue",
    r"\bdilut", r"\bdowngrade", r"\bcut\b", r"\bloss\b", r"\blosing\b", r"\bfall", r"\bdrop\b",
    r"\bplunge", r"\bslump", r"\bcrash\b", r"\blow\b", r"\bbankrupt\b", r"\bdelist\b", r"\bsuspend\b",
    r"\brisk\b", r"\bweak\b", r"\bmiss\b", r"\bscam\b", r"\bgambl", r"\bovervalu", r"\bexpensive\b",
    r"\bbearish\b", r"\bresistance\b", r"\bdefault\b", r"\blawsuit\b", r"\bfine\b", r"\btax\b",
    r"\bjual\b", r"\bhutang\b", r"\bfaedah\b", r"\bcair\b", r"\bturun\b", r"\bjatuh\b", r"\brugi\b",
    r"\blemah\b", r"\brisiko\b", r"\bgagal\b", r"\btipu\b", r"\bjud[i]?\b", r"\bmahal\b", r"\bsaman\b",
    r"\bcukai\b", r"\bmuflis\b",
    r"卖", r"抛", r"债务", r"利息", r"附加股", r"稀释", r"降级", r"亏损", r"下跌", r"跌", r"崩",
    r"破产", r"除牌", r"停牌", r"风险", r"弱", r"失败", r"骗", r"赌", r"贵", r"看跌", r"阻力",
    r"违约", r"罚款", r"税",
]
BULL_RE = re.compile("|".join(BULL), re.IGNORECASE)
BEAR_RE = re.compile("|".join(BEAR), re.IGNORECASE)

sent_sum: dict[str, float] = defaultdict(float)
sent_n: dict[str, int] = defaultdict(int)
sent_bull: dict[str, int] = defaultdict(int)
sent_bear: dict[str, int] = defaultdict(int)
for r in replies:
    body = r["body"] or ""
    if not body:
        continue
    m = month(r["created_utc"])
    b = len(BULL_RE.findall(body))
    s = len(BEAR_RE.findall(body))
    if b + s == 0:
        continue
    score = (b - s) / (b + s)
    sent_sum[m] += score
    sent_n[m] += 1
    sent_bull[m] += b
    sent_bear[m] += s

with (OUT / "06_keyword_polarity_monthly.csv").open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["month", "polarity", "scored_replies", "bull_terms", "bear_terms"])
    for m in MONTHS:
        w.writerow([
            m,
            round(sent_sum[m] / sent_n[m], 3) if sent_n[m] else "",
            sent_n[m],
            sent_bull[m],
            sent_bear[m],
        ])

# ---------------------------------------------------------------- company events
with (OUT / "07_company_events.csv").open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["date", "ticker", "title", "body"])
    for r in conn.execute(
        "SELECT created_utc, ticker, title, body FROM posts WHERE source='company_event' ORDER BY created_utc"
    ):
        w.writerow([
            datetime.fromtimestamp(r["created_utc"], timezone.utc).strftime("%Y-%m-%d"),
            r["ticker"],
            r["title"],
            (r["body"] or "")[:500],
        ])

# ---------------------------------------------------------------- report
def fmt_pct(x):
    return f"{x:+.2f}%"

lines = ["# Stage 1 audit — Genting sentiment corpus", ""]
lines.append(f"Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}")
lines.append("")
lines.append("## Volume")
lines.append("")
lines.append("| Source | Replies | First | Last |")
lines.append("|---|---:|---|---|")
for r in conn.execute(
    "SELECT source, COUNT(*) n, MIN(created_utc) a, MAX(created_utc) b FROM replies GROUP BY source ORDER BY n DESC"
):
    lines.append(
        f"| {r['source']} | {r['n']:,} | {datetime.fromtimestamp(r['a'], timezone.utc):%Y-%m-%d} | "
        f"{datetime.fromtimestamp(r['b'], timezone.utc):%Y-%m-%d} |"
    )
lines.append("")
lines.append("## Price")
lines.append("")
for sym, series in prices.items():
    ds = sorted(series)
    first, last = series[ds[0]], series[ds[-1]]
    peak = max(series.items(), key=lambda kv: kv[1])
    trough = min(series.items(), key=lambda kv: kv[1])
    lines.append(
        f"- **{sym}**: {first:.2f} ({ds[0]}) → {last:.2f} ({ds[-1]}), "
        f"{fmt_pct((last / first - 1) * 100)}. Peak {peak[1]:.2f} on {peak[0]}; "
        f"trough {trough[1]:.2f} on {trough[0]}."
    )
lines.append("")
lines.append("## Event reactions")
lines.append("")
lines.append("| Event | Ticker | 1d | 5d | 20d |")
lines.append("|---|---|---:|---:|---:|")
for e in ev:
    for sym in ["GENTING", "GENM"]:
        vals = {r[3]: r[5] for r in event_rows if r[1] == e[0] and r[0] == sym}
        if vals:
            lines.append(
                f"| {e[1]} | {sym} | {vals.get('1d', 0):+.2f}% | {vals.get('5d', 0):+.2f}% | {vals.get('20d', 0):+.2f}% |"
            )
lines.append("")
lines.append("## News categories")
lines.append("")
lines.append("| Category | Articles |")
lines.append("|---|---:|")
for cat in NEWS_RULES:
    lines.append(f"| {cat} | {sum(news_by_cat[cat].values())} |")
lines.append("")
lines.append("## Keyword polarity by month")
lines.append("")
lines.append("| Month | Polarity | Scored replies |")
lines.append("|---|---:|---:|")
for m in MONTHS:
    if sent_n[m]:
        lines.append(f"| {m} | {sent_sum[m]/sent_n[m]:+.3f} | {sent_n[m]:,} |")
lines.append("")
lines.append("> Keyword polarity is a crude first pass, not a trained sentiment model. It counts bullish/bearish terms in English, Malay and Chinese; negations and sarcasm are not handled.")
(OUT / "00_audit.md").write_text("\n".join(lines))

# ---------------------------------------------------------------- examples
with (OUT / "08_news_examples.md").open("w") as fh:
    for cat, examples in news_examples.items():
        fh.write(f"## {cat}\n\n")
        for date, title in examples:
            fh.write(f"- {date} — {title}\n")
        fh.write("\n")

print("wrote analysis files")
print("volume rows", len(replies))
print("news", len(news_rows), "articles")
print("keyword scored", sum(sent_n.values()), "replies")
for m in ["2024-11", "2025-10", "2025-12", "2026-10"]:
    print(m, "polarity", round(sent_sum[m]/sent_n[m], 3) if sent_n[m] else None, "n", sent_n[m])
print("\nTop news:")
for cat, c in sorted(news_by_cat.items(), key=lambda kv: -sum(kv[1].values())):
    print(cat, sum(c.values()))
