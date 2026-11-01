#!/usr/bin/env python3
"""Deep search: re-run core queries with 100 results and merge new candidates."""

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path

BASE = Path("/tmp/opencode/ytfull/discovery")
YTDLP = Path.home() / ".local/bin/yt-dlp"
QUERIES = [
    "genting stock", "genting malaysia", "genting berhad", "GENM 4715",
    "GENTING 3182", "genting rights issue", "genting debt", "genting analysis",
    "genting dividend", "genting privatization", "saham genting", "analisa genting",
    "云顶 股票", "云顶大马", "云顶 附加股", "云顶 私有化", "云顶 股价",
    "genting crash", "genting results", "genting New York casino",
]


def main() -> int:
    cands = {c["id"]: c for c in json.loads(
        (BASE / "candidates_all.json").read_text(encoding="utf-8"))}
    before = len(cands)
    outdir = BASE / "q100"
    outdir.mkdir(exist_ok=True)
    for i, q in enumerate(QUERIES, 1):
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", q)[:80]
        out = outdir / f"{i:02d}_{safe}.jsonl"
        if out.exists():
            entries = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
        else:
            cmd = [str(YTDLP), "--flat-playlist", "--dump-json", "--no-warnings",
                   "--socket-timeout", "30", "--retries", "3", f"ytsearch100:{q}"]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
            entries = []
            for line in proc.stdout.splitlines():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
            out.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n", encoding="utf-8")
            print(f"{q!r}: {len(entries)}", flush=True)
            time.sleep(1.2)
        for e in entries:
            vid = e.get("id")
            if not vid:
                continue
            rec = cands.setdefault(vid, {
                "id": vid, "title": e.get("title"), "description": e.get("description"),
                "channel": e.get("channel") or e.get("uploader"),
                "channel_id": e.get("channel_id"), "duration": e.get("duration"),
                "view_count": e.get("view_count"),
                "url": e.get("url") or f"https://www.youtube.com/watch?v={vid}",
                "queries": [],
            })
            tag = f"ytsearch100:{q}"
            if tag not in rec["queries"]:
                rec["queries"].append(tag)
    (BASE / "candidates_all.json").write_text(
        json.dumps(list(cands.values()), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"candidates {before} -> {len(cands)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
