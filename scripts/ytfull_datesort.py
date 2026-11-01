#!/usr/bin/env python3
"""Harvest YouTube search results sorted by upload date (sp=CAI) for core queries."""

from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path("/tmp/opencode/ytfull/discovery")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
QUERIES = [
    "genting stock", "genting malaysia", "genting berhad", "GENM 4715",
    "GENTING 3182", "genting rights issue", "genting debt", "genting analysis",
    "genting privatization", "saham genting", "云顶 股票", "云顶大马",
    "云顶 附加股", "云顶 私有化", "云顶 股价", "genting results",
    "genting crash", "genting New York casino", "genting dividend", "analisa genting",
]


def walk_videos(o, out):
    if isinstance(o, dict):
        v = o.get("videoRenderer")
        if isinstance(v, dict) and v.get("videoId"):
            title = "".join(r.get("text", "") for r in v.get("title", {}).get("runs", []))
            channel = "".join(r.get("text", "") for r in
                              v.get("longBylineText", {}).get("runs", [])[:1])
            desc = "".join(r.get("text", "") for r in
                           v.get("detailedMetadataSnippets", [{}])[0]
                           .get("snippetText", {}).get("runs", [])) if v.get("detailedMetadataSnippets") else ""
            out.append({"id": v["videoId"], "title": title, "channel": channel, "description": desc})
            return
        for x in o.values():
            walk_videos(x, out)
    elif isinstance(o, list):
        for x in o:
            walk_videos(x, out)


def main() -> int:
    cands = {c["id"]: c for c in json.loads(
        (BASE / "candidates_all.json").read_text(encoding="utf-8"))}
    added = 0
    for q in QUERIES:
        url = ("https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(q)
               + "&sp=CAI%253D")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                       "Accept-Language": "en-US,en;q=0.9"})
            html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
            m = re.search(r"var ytInitialData = (\{.*?\});</script>", html, re.S)
            if not m:
                print(f"{q!r}: no initial data")
                continue
            vids: list[dict] = []
            walk_videos(json.loads(m.group(1)), vids)
        except Exception as exc:  # noqa: BLE001
            print(f"{q!r}: {exc}")
            continue
        new = 0
        for e in vids:
            vid = e["id"]
            if vid in cands:
                tag = f"date-sorted:{q}"
                if tag not in cands[vid]["queries"]:
                    cands[vid]["queries"].append(tag)
                continue
            cands[vid] = {
                "id": vid, "title": e.get("title"), "description": e.get("description"),
                "channel": e.get("channel"), "channel_id": None,
                "duration": None, "view_count": None,
                "url": f"https://www.youtube.com/watch?v={vid}",
                "queries": [f"date-sorted:{q}"],
            }
            new += 1
            added += 1
        print(f"{q!r}: {len(vids)} videos, {new} new")
        time.sleep(1.2)
    (BASE / "candidates_all.json").write_text(
        json.dumps(list(cands.values()), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"added {added}; total {len(cands)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
