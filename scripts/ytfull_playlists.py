#!/usr/bin/env python3
"""Harvest YouTube playlist search results for Genting and expand their videos."""

from __future__ import annotations

import json
import re
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path("/tmp/opencode/ytfull/discovery")
YTDLP = Path.home() / ".local/bin/yt-dlp"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

QUERIES = [
    "genting stock", "genting malaysia", "genting berhad", "GENM 4715",
    "genting rights issue", "saham genting", "云顶 股票", "云顶大马",
]


def playlist_ids(query: str) -> list[tuple[str, str]]:
    url = ("https://www.youtube.com/results?search_query="
           + urllib.parse.quote_plus(query) + "&sp=EgIQAw%253D%253D")
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", html, re.S)
    if not m:
        return []
    data = json.loads(m.group(1))
    found: dict[str, str] = {}

    def walk(o):
        if isinstance(o, dict):
            if o.get("contentType") == "LOCKUP_CONTENT_TYPE_PLAYLIST":
                s = json.dumps(o, ensure_ascii=False)
                for pid in re.findall(r'"playlistId":\s*"(PL[^"]+)"', s):
                    title = None
                    tm = re.search(r'"title":\s*\{"[^"]*":\s*"([^"]{3,200})"', s)
                    if tm:
                        title = tm.group(1)
                    found.setdefault(pid, title or "")
                pe = o.get("contentId")
                if isinstance(pe, str) and pe.startswith("PL"):
                    found.setdefault(pe, "")
                return
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(data)
    # fallback: any watchEndpoint playlistId
    for pid in re.findall(r'"playlistId":\s*"(PL[^"]+)"', json.dumps(data)):
        found.setdefault(pid, "")
    return list(found.items())


def expand(pid: str) -> list[dict]:
    out = BASE / "pl" / f"{pid}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        return [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
    cmd = [str(YTDLP), "--flat-playlist", "--dump-json", "--no-warnings",
           "--playlist-end", "300", "--socket-timeout", "30", "--retries", "3",
           f"https://www.youtube.com/playlist?list={pid}"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    entries = []
    for line in proc.stdout.splitlines():
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    out.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n", encoding="utf-8")
    return entries


def main() -> int:
    playlists: dict[str, str] = {}
    for q in QUERIES:
        try:
            ids = playlist_ids(q)
        except Exception as exc:  # noqa: BLE001
            print(f"playlist search {q!r} failed: {exc}")
            continue
        print(f"playlist search {q!r}: {len(ids)}")
        for pid, title in ids:
            playlists.setdefault(pid, title)
        time.sleep(1.2)
    print(f"unique playlists: {len(playlists)}")
    (BASE / "playlists.json").write_text(
        json.dumps([{"id": k, "title": v} for k, v in playlists.items()], ensure_ascii=False, indent=1),
        encoding="utf-8")

    candidates = {c["id"]: c for c in json.loads((BASE / "candidates.json").read_text(encoding="utf-8"))}
    for pid, title in playlists.items():
        entries = expand(pid)
        print(f"  {pid} {title[:60]!r}: {len(entries)}")
        for e in entries:
            vid = e.get("id")
            if not vid:
                continue
            rec = candidates.setdefault(vid, {
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
            tag = f"playlist:{pid}"
            if tag not in rec["queries"]:
                rec["queries"].append(tag)
        time.sleep(1.0)
    (BASE / "candidates_plus_playlists.json").write_text(
        json.dumps(list(candidates.values()), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"total candidates incl playlists: {len(candidates)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
