"""Language-aware first-pass sentiment: VADER (English), lexicons (Malay/Chinese)."""

from __future__ import annotations

import csv
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "genting.db"
OUT = ROOT / "analysis"

MONTHS = [
    "2024-11", "2024-12", "2025-01", "2025-02", "2025-03", "2025-04",
    "2025-05", "2025-06", "2025-07", "2025-08", "2025-09", "2025-10",
    "2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04",
    "2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10",
    "2026-11",
]

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
MALAY_RE = re.compile(
    r"\b(yang|tak|tidak|dan|untuk|dengan|ini|itu|saya|kami|kau|dia|untung|rugi|"
    r"saham|harga|beli|jual|boleh|dah|je|lah|memang|kena|lagi|sudah|akan)\b",
    re.I,
)

ZH_POS = [
    "买", "买入", "加仓", "便宜", "股息", "派息", "复苏", "盈利", "上涨", "涨",
    "升级", "目标价", "反弹", "价值", "看涨", "支撑", "底部", "好", "强", "赚",
    "成功", "机会", "持有", "长期", "低估", "合理", "不错", "利好", "牛",
]
ZH_NEG = [
    "卖", "卖出", "抛", "债务", "负债", "利息", "附加股", "稀释", "降级", "亏损",
    "下跌", "跌", "崩", "破产", "除牌", "停牌", "风险", "弱", "失败", "骗",
    "贵", "看跌", "阻力", "违约", "罚款", "烂", "差", "亏", "套", "割",
    "恐慌", "抛售", "减仓", "坏消息", "高估", "泡沫", "危险", "惨", "垃圾",
]
MS_POS = [
    "beli", "tambah", "murah", "dividen", "pulih", "untung", "naik", "kukuh",
    "positif", "peluang", "sokong", "nilai", "baik", "bagus", "untung", "bawah",
]
MS_NEG = [
    "jual", "hutang", "faedah", "cair", "turun", "jatuh", "rugi", "lemah",
    "risiko", "gagal", "tipu", "mahal", "saman", "muflis", "salah", "buruk",
    "panik", "tekanan", "beban", "parah", "susah", "takut", "kerugian", "mampus",
]

analyzer = SentimentIntensityAnalyzer()


def language(text: str) -> str:
    if CJK_RE.search(text):
        return "zh"
    if len(MALAY_RE.findall(text)) >= 2:
        return "ms"
    return "en"


def score(text: str) -> tuple[float, str]:
    lang = language(text)
    if lang == "en":
        return analyzer.polarity_scores(text)["compound"], lang
    low = text.lower()
    if lang == "zh":
        pos = sum(low.count(w) for w in ZH_POS)
        neg = sum(low.count(w) for w in ZH_NEG)
    else:
        pos = sum(len(re.findall(rf"\b{re.escape(w)}\b", low)) for w in MS_POS)
        neg = sum(len(re.findall(rf"\b{re.escape(w)}\b", low)) for w in MS_NEG)
    if pos + neg == 0:
        return 0.0, lang
    return max(-1.0, min(1.0, (pos - neg) / (pos + neg))), lang


conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

monthly = defaultdict(list)
by_source = defaultdict(list)
by_lang = Counter()
samples = []
rows = conn.execute(
    "SELECT source, author, score, created_utc, body, time_confidence FROM replies "
    "WHERE body IS NOT NULL AND length(body) > 8"
).fetchall()

for r in rows:
    body = r["body"]
    s, lang = score(body)
    m = datetime.fromtimestamp(r["created_utc"], timezone.utc).strftime("%Y-%m")
    monthly[m].append(s)
    by_source[r["source"]].append(s)
    by_lang[lang] += 1
    if len(samples) < 40000:
        samples.append((s, lang, r))

with (OUT / "07_sentiment_monthly.csv").open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["month", "mean_sentiment", "scored", "bullish_share", "bearish_share", "neutral_share"])
    for m in MONTHS:
        vals = monthly.get(m, [])
        if not vals:
            w.writerow([m, "", 0, "", "", ""])
            continue
        bull = sum(1 for v in vals if v > 0.05) / len(vals)
        bear = sum(1 for v in vals if v < -0.05) / len(vals)
        w.writerow([
            m, round(sum(vals) / len(vals), 3), len(vals),
            round(bull, 3), round(bear, 3), round(1 - bull - bear, 3),
        ])

with (OUT / "08_sentiment_by_source.csv").open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["source", "mean_sentiment", "scored"])
    for source, vals in sorted(by_source.items(), key=lambda kv: -len(kv[1])):
        w.writerow([source, round(sum(vals) / len(vals), 3), len(vals)])

# high / low examples per event window
windows = {
    "Oct 2025 offer": ("2025-10-01", "2025-11-05"),
    "Dec 2025 failure": ("2025-12-01", "2025-12-31"),
    "Oct 2026 rights issue": ("2026-10-01", "2026-11-02"),
    "2026 debt / ratings": ("2026-08-01", "2026-10-01"),
}


def ts(date: str) -> int:
    return int(datetime.fromisoformat(date).replace(tzinfo=timezone.utc).timestamp())


with (OUT / "09_sentiment_examples.md").open("w") as fh:
    fh.write("# Sentiment examples\n\n")
    for label, (start, end) in windows.items():
        fh.write(f"## {label}\n\n")
        subset = [
            (s, lang, r) for s, lang, r in samples
            if ts(start) <= r["created_utc"] <= ts(end)
        ]
        subset.sort(key=lambda x: x[0])
        for title, part in [("Most negative", subset[:3]), ("Most positive", subset[-3:])]:
            fh.write(f"**{title}**\n\n")
            for s, lang, r in part:
                body = re.sub(r"\s+", " ", r["body"])[:260]
                date = datetime.fromtimestamp(r["created_utc"], timezone.utc).strftime("%Y-%m-%d")
                fh.write(f"- `{s:+.2f}` ({lang}) {date} {r['source']}/{r['author']}: {body}\n")
            fh.write("\n")

print("languages", by_lang)
print("scored", sum(len(v) for v in monthly.values()))
for m in ["2024-11", "2025-10", "2025-12", "2026-08", "2026-10"]:
    vals = monthly.get(m, [])
    print(m, round(sum(vals) / len(vals), 3) if vals else None, len(vals))
print("source means")
for source, vals in sorted(by_source.items(), key=lambda kv: -len(kv[1])):
    print(f"  {source:<14} {sum(vals)/len(vals):+.3f}  n={len(vals):,}")
