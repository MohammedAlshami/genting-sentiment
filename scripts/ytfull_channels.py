#!/usr/bin/env python3
"""Phase 2b: channel-scoped searches for every channel discovered with Genting content."""

from __future__ import annotations

import json
import re
import subprocess
import time
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote

BASE = Path("/tmp/opencode/ytfull/discovery")
YTDLP = Path.home() / ".local/bin/yt-dlp"
PAT = re.compile(r"genting|genm|云顶|3182|4715", re.I)


def main() -> int:
    src = BASE / "candidates_plus_playlists.json"
    if not src.exists():
        src = BASE / "candidates.json"
        if not src.exists():
            src = BASE / "global_index.json"
    candidates = json.loads(src.read_text(encoding="utf-8"))
    by_channel: dict[str, dict] = {}
    counts: Counter = Counter()
    for c in candidates:
        text = (c.get("title") or "") + " " + (c.get("description") or "")
        if not PAT.search(text):
            continue
        cid = c.get("channel_id")
        if not cid:
            continue
        counts[cid] += 1
        by_channel.setdefault(cid, {"channel": c.get("channel"), "titles": []})
        if len(by_channel[cid]["titles"]) < 3:
            by_channel[cid]["titles"].append(c.get("title"))

    # Skip channels that are plainly tourism/hospitality rather than markets.
    skip = re.compile(
        r"resorts world genting|hotel|driving|travel|food|theme park|holiday|vlog|去哪儿|旅游|酒店|"
        r"zzgogo|kenny|skyworlds|casino|amber court|moto", re.I)
    finance = re.compile(
        r"the edge|invest|finance|saham|stock|bursa|market|财经|股市|投资|理财|论股|股票|证券|"
        r"交易所|南洋商报|百格|pocketimes|astro awani|tv3|rtm|八度空间|新闻|capital|business|"
        r"forbes|bloomberg|reuters|nikkei|money|wealth|trade", re.I)
    finterm = re.compile(
        r"stock|share|saham|bursa|klse|klci|ticker|valuation|earning|result|revenue|profit|loss|"
        r"debt|dividend|rights? issue|cash call|bond|credit rating|market cap|analyst|target price|"
        r"invest|ipo|privatis|privatiz|takeover|vgo|offer|minority|shareholder|agm|eps|p/e|"
        r"fundamental|technical|股价|股票|财报|业绩|股息|债务|附加股|私有化|收购|集资|分析|暴跌|"
        r"投资|股东|市值|每股|除牌|上市|季报|年报|亏损|盈利|营收", re.I)
    selected = []
    for cid, n in counts.most_common():
        meta = by_channel[cid]
        if n < 2:
            continue
        if skip.search(meta["channel"] or ""):
            continue
        if not (finance.search(meta["channel"] or "")
                or any(finterm.search(t or "") for t in meta["titles"])):
            continue
        selected.append((cid, meta["channel"], n))
    print(f"channels with >=2 Genting matches: {len(selected)}")
    for cid, name, n in selected[:80]:
        print(f"  {n:3d} {name} ({cid})")

    index = {c["id"]: c for c in candidates}
    for i, (cid, name, n) in enumerate(selected, 1):
        out = BASE / "c2" / f"{cid}.jsonl"
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists():
            entries = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
        else:
            url = f"https://www.youtube.com/channel/{cid}/search?query=genting"
            cmd = [str(YTDLP), "--flat-playlist", "--dump-json", "--no-warnings",
                   "--playlist-end", "100", "--socket-timeout", "30", "--retries", "2", url]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
            entries = []
            for line in proc.stdout.splitlines():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
            out.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n", encoding="utf-8")
            print(f"  [{i}/{len(selected)}] {name}: {len(entries)}", flush=True)
            time.sleep(1.0)
        for e in entries:
            vid = e.get("id")
            if not vid:
                continue
            rec = index.setdefault(vid, {
                "id": vid,
                "title": e.get("title"),
                "description": e.get("description"),
                "channel": e.get("channel") or e.get("uploader"),
                "channel_id": e.get("channel_id"),
                "duration": e.get("duration"),
                "view_count": e.get("view_count"),
                "url": e.get("url") or f"https://www.youtube.com/watch?v={vid}",
                "queries": [],
            })
            tag = f"channel-id:{cid}"
            if tag not in rec["queries"]:
                rec["queries"].append(tag)

    (BASE / "candidates_all.json").write_text(
        json.dumps(list(index.values()), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"total candidates: {len(index)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
