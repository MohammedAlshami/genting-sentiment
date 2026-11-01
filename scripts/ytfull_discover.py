#!/usr/bin/env python3
"""Exhaustive YouTube discovery for Malaysian Genting (2 Nov 2024 - 2 Nov 2026).

Phase 1: global ytsearch queries (English / Malay / Chinese).
Phase 2: channel-scoped searches for channels known to cover Bursa stocks.
Phase 3: playlist search-results surfaced by YouTube.

Writes every raw flat result to /tmp/opencode/ytfull/discovery/ and a combined
candidate index with query provenance. No filtering here: phase 4 fetches full
metadata for each candidate and decides relevance from title/description.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import quote

YTDLP = Path.home() / ".local/bin/yt-dlp"
BASE = Path("/tmp/opencode/ytfull/discovery")
BASE.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- queries ---
GLOBAL_QUERIES = [
    # English - company / ticker / market
    "genting stock",
    "genting share price",
    "genting berhad",
    "genting malaysia",
    "genting berhad stock analysis",
    "genting malaysia stock analysis",
    "GENM 4715",
    "GENTING 3182",
    "genting rights issue",
    "genting debt",
    "genting analysis",
    "genting dividend",
    "genting privatization",
    "genting privatisation",
    "genting New York casino",
    "genting results",
    "genting Q1 2025",
    "genting Q2 2025",
    "genting Q3 2025",
    "genting Q4 2025",
    "genting Q1 2026",
    "genting Q2 2026",
    "genting Q3 2026",
    "genting annual report",
    "genting share price crash",
    "genting stock drop",
    "genting buy or sell",
    "genting valuation",
    "genting cash call",
    "genting Miami land sale",
    "genting Empire Resorts",
    "genting Resorts World Las Vegas",
    "genting Malaysia casino licence",
    "genting Singapore stake",
    "genting Lim Kok Thay",
    "genting bond",
    "genting credit rating",
    "genting Moody's",
    "genting Fitch",
    "genting stock 2024",
    "genting stock 2025",
    "genting stock 2026",
    "GENM stock",
    "GENTING share",
    "genting group",
    "genting theme park",
    "genting casino Malaysia",
    "genting earnings",
    "genting revenue",
    "genting net loss",
    "genting restructuring",
    "genting sell-off",
    "genting shareholders",
    "genting AGM",
    "genting takeover",
    "genting offer",
    "genting minority shareholders",
    # Malay
    "saham genting",
    "analisa genting",
    "genting untung",
    "genting rugi",
    "genting jatuh",
    "genting naik",
    "harga saham genting",
    "genting berhad saham",
    "genting malaysia berhad",
    "genm saham",
    "genting beli atau jual",
    "genting dividen",
    "genting hak isu",
    "genting ambil alih",
    "genting berita",
    "saham genm jatuh",
    "analisis saham genting",
    "genting kongsi",
    "saham genting 2025",
    "saham genting 2026",
    "genting modal",
    "genting hutang",
    "genting untung 2025",
    "genting jual",
    # Chinese
    "云顶 股票",
    "云顶大马",
    "云顶 分析",
    "云顶 债务",
    "云顶 附加股",
    "云顶 私有化",
    "云顶 财报",
    "云顶 业绩",
    "云顶 股息",
    "云顶 股价",
    "云顶 暴跌",
    "云顶 3182",
    "云顶大马 4715",
    "GENM 云顶",
    "GENTING 云顶",
    "云顶 纽约 赌场",
    "云顶 迈阿密",
    "林国泰 云顶",
    "云顶 债务危机",
    "云顶 集资",
    "云顶 附加股 2026",
    "云顶 私有化 2025",
    "云顶 大马",
    "云顶 集团",
    "云顶 股价 新低",
    "云顶 财报 2025",
    "云顶 业绩 2026",
    "云顶 分析 2025",
    "云顶 股票 分析",
    "云顶 还能买吗",
    "云顶 值得买吗",
    "云顶 反弹",
    "云顶 套牢",
    "云顶 附加股 2025",
]

# Channels that cover Bursa Malaysia / corporate news. Handles are resolved by
# YouTube when the @handle exists; channel ids are used for the rest.
CHANNELS = [
    ("The Edge TV", "@TheEdgeTV"),
    ("The Edge Malaysia", "@theedgemalaysia"),
    ("InvestDummies", "@InvestDummies"),
    ("Y-Z Finance MY", "@YZFinanceMY"),
    ("Asri Ahmad Academy", "@AsriAhmadAcademy"),
    ("Maher Saham", "@MaherSaham"),
    ("CGS International", "@CGSInternational"),
    ("UOB Kay Hian Malaysia", "@UOBKayHianMalaysia"),
    ("Maybank Investment Bank", "@MaybankIB"),
    ("Bursa Malaysia", "@BursaMalaysia"),
    ("TI 懂一点", "@TIknowsomething"),
    ("Double Swords Investing", "@DoubleSwordsInvesting"),
    ("大老板投资记录本", "@bigbossinvestment"),
    ("八卦大小文的闲聊股市", "@baguadaxiaowen"),
    ("第一天投资理财研究所", "@firstdayinvestment"),
    ("阿布的鸟公司", "@abucompany"),
    ("股市先锋队", "@stockpioneer"),
    ("Nighteyes08", "@Nighteyes08"),
    ("FIRL", "@FIRL"),
    ("AF's Notes", "@AFsNotes"),
    ("我是雷公", "@leigong"),
    ("Neo, Biz Editor", "@neobizeditor"),
    ("大马财富故事", "@malaysiawealthstories"),
    ("Ziet Invests", "@ZietInvests"),
    ("八度空间华语新闻", "@8tvchinesenews"),
    ("MYtraderview", "@mytraderview"),
    ("One Minute Finance", "@oneminutefinance"),
    ("PERSENAN", "@PERSENAN"),
    ("Learn Gambling", "@learngambling"),
    ("Smartkarma", "@smartkarma"),
    ("StubWorld", "@StubWorld"),
]

CHANNEL_TERMS = ["genting", "genm", "云顶", "3182", "4715"]


def run_search(target: str, limit: int, out: Path) -> list[dict]:
    if out.exists():
        return [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
    cmd = [
        str(YTDLP), "--flat-playlist", "--dump-json", "--no-warnings",
        "--socket-timeout", "30", "--retries", "3",
        f"ytsearch{limit}:{target}",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    entries: list[dict] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    out.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n", encoding="utf-8")
    err = (proc.stderr or "").strip().splitlines()
    print(f"  search {target!r}: {len(entries)} results" + (f" | {err[-1]}" if err and not entries else ""), flush=True)
    return entries


def run_channel_search(channel: str, term: str, limit: int, out: Path) -> list[dict]:
    if out.exists():
        return [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
    if channel.startswith("@"):
        url = f"https://www.youtube.com/{channel}/search?query={quote(term)}"
    else:
        url = f"https://www.youtube.com/channel/{channel}/search?query={quote(term)}"
    cmd = [
        str(YTDLP), "--flat-playlist", "--dump-json", "--no-warnings",
        "--playlist-end", str(limit), "--socket-timeout", "30", "--retries", "3", url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    entries: list[dict] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    out.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n", encoding="utf-8")
    if entries:
        print(f"  channel {channel} / {term}: {len(entries)}", flush=True)
    else:
        print(f"  channel {channel} / {term}: 0", flush=True)
    return entries


def main() -> int:
    index: dict[str, dict] = {}

    def add(entry: dict, query: str) -> None:
        vid = entry.get("id")
        if not vid:
            return
        rec = index.setdefault(vid, {
            "id": vid,
            "title": entry.get("title"),
            "description": entry.get("description"),
            "channel": entry.get("channel") or entry.get("uploader"),
            "channel_id": entry.get("channel_id"),
            "duration": entry.get("duration"),
            "view_count": entry.get("view_count"),
            "url": entry.get("url") or f"https://www.youtube.com/watch?v={vid}",
            "queries": [],
        })
        if query not in rec["queries"]:
            rec["queries"].append(query)

    # Phase 1 -----------------------------------------------------------------
    print("PHASE 1: global searches", flush=True)
    for i, q in enumerate(GLOBAL_QUERIES, 1):
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", q)[:80]
        out = BASE / "q" / f"{i:03d}_{safe}.jsonl"
        out.parent.mkdir(parents=True, exist_ok=True)
        entries = run_search(q, 50, out)
        for e in entries:
            add(e, f"ytsearch50:{q}")
        if not out.exists() or not entries:
            time.sleep(1.5)
    (BASE / "global_index.json").write_text(
        json.dumps(list(index.values()), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"global unique candidates: {len(index)}", flush=True)

    # Phase 2 -----------------------------------------------------------------
    print("PHASE 2: channel scoped searches", flush=True)
    for channel, handle in CHANNELS:
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", channel)[:40]
        for term in CHANNEL_TERMS:
            out = BASE / "c" / f"{safe}__{re.sub(r'[^A-Za-z0-9]+', '_', term)}.jsonl"
            out.parent.mkdir(parents=True, exist_ok=True)
            entries = run_channel_search(handle, term, 100, out)
            for e in entries:
                add(e, f"channel:{channel}:{term}")
            time.sleep(1.0)
    (BASE / "candidates.json").write_text(
        json.dumps(list(index.values()), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"total unique candidates: {len(index)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
