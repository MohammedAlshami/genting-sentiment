#!/usr/bin/env python3
"""Fetch full metadata (no comments) for every discovery candidate."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

BASE = Path("/tmp/opencode/ytfull")
META = BASE / "meta"
YTDLP = Path.home() / ".local/bin/yt-dlp"


def main() -> int:
    src = BASE / "discovery" / "prefilter.json"
    if not src.exists():
        src = BASE / "discovery" / "candidates_all.json"
    if not src.exists():
        src = BASE / "discovery" / "candidates_plus_playlists.json"
    if not src.exists():
        src = BASE / "discovery" / "candidates.json"
    candidates = json.loads(src.read_text(encoding="utf-8"))
    META.mkdir(parents=True, exist_ok=True)
    todo = [c for c in candidates if not (META / f"{c['id']}.json").exists()
            and not (META / f"{c['id']}.error.json").exists()]
    print(f"candidates={len(candidates)} todo={len(todo)}", flush=True)
    for i, c in enumerate(todo, 1):
        vid = c["id"]
        cmd = [str(YTDLP), "--skip-download", "--dump-json", "--no-warnings",
               "--socket-timeout", "30", "--retries", "2",
               f"https://www.youtube.com/watch?v={vid}"]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        except subprocess.TimeoutExpired:
            (META / f"{vid}.error.json").write_text(json.dumps(
                {"id": vid, "error": "timeout", "stderr": ""}), encoding="utf-8")
            continue
        if proc.returncode == 0 and proc.stdout.strip():
            try:
                info = json.loads(proc.stdout.splitlines()[0])
                (META / f"{vid}.json").write_text(json.dumps(info, ensure_ascii=False), encoding="utf-8")
            except json.JSONDecodeError as exc:
                (META / f"{vid}.error.json").write_text(json.dumps(
                    {"id": vid, "error": f"json: {exc}", "stderr": proc.stderr[-2000:]}), encoding="utf-8")
        else:
            (META / f"{vid}.error.json").write_text(json.dumps(
                {"id": vid, "error": f"exit {proc.returncode}", "stderr": proc.stderr[-2000:]}), encoding="utf-8")
        if i % 50 == 0:
            done = len(list(META.glob("*.json")))
            print(f"  {i}/{len(todo)} (files={done})", flush=True)
        time.sleep(0.8)
    print("metadata fetch complete", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
