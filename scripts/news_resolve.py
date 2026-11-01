#!/usr/bin/env python3
"""Stage 2: resolve Google News redirect links to publisher URLs."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

from curl_cffi import requests as cffi_requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from news_lib import CACHE, http_get  # noqa: E402

STATE = CACHE / "resolved.json"


def resolve_one(session: cffi_requests.Session, google_url: str) -> str | None:
    base = google_url.split("?")[0]
    r = http_get(base, session=session, timeout=30, tries=2)
    if r is None:
        return None
    if "news.google.com" not in r.url:
        return r.url
    h = r.text
    sg = re.search(r'data-n-a-sg="([^"]+)"', h)
    ts = re.search(r'data-n-a-ts="([^"]+)"', h)
    aid = re.search(r'data-n-a-id="([^"]+)"', h)
    if not (sg and ts and aid):
        return None
    payload = [
        "garturlreq",
        [
            ["X", "X", ["X", "X"], None, None, 1, 1, "US:en", None, 1, None, None, None, None, None, 0, 1],
            "X",
            "X",
            1,
            [1, 1, 1],
            1,
            1,
            None,
            0,
            0,
            None,
            0,
        ],
        aid.group(1),
        int(ts.group(1)),
        sg.group(1),
    ]
    f_req = [[["Fbv4je", json.dumps(payload, separators=(",", ":"))]]]
    data = "f.req=" + urllib.parse.quote(json.dumps(f_req, separators=(",", ":")))
    try:
        r2 = session.post(
            "https://news.google.com/_/DotsSplashUi/data/batchexecute",
            data=data,
            headers={
                "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            },
            impersonate="chrome",
            timeout=30,
        )
    except Exception:
        return None
    if r2.status_code != 200:
        return None
    m = re.search(r'\[\\"garturlres\\",\\"(.*?)\\"', r2.text)
    if not m:
        return None
    url = m.group(1).replace("\\\\u003d", "=").replace("\\\\u0026", "&")
    url = url.replace("\\u003d", "=").replace("\\u0026", "&")
    if not url.startswith("http"):
        return None
    return url


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--discovery", type=Path, default=CACHE / "discovery.json")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    items = json.loads(args.discovery.read_text())
    state: dict[str, str | None] = {}
    if STATE.exists():
        state = json.loads(STATE.read_text())
    todo = [
        it for it in items
        if it["google_url"] not in state
        and re.search(r"genting|genm|3182|4715|云顶|resorts world|rwg|rwnyc", it["title"], re.I)
    ]
    if args.limit:
        todo = todo[: args.limit]
    print(f"{len(state)} cached, {len(todo)} to resolve")
    session = cffi_requests.Session()
    t0 = time.time()
    for i, it in enumerate(todo, 1):
        url = resolve_one(session, it["google_url"])
        state[it["google_url"]] = url
        if i % 25 == 0 or i == len(todo):
            STATE.write_text(json.dumps(state, ensure_ascii=False, indent=0))
            ok = sum(1 for v in state.values() if v)
            print(f"  [{i}/{len(todo)}] resolved={ok} elapsed={time.time()-t0:.0f}s", flush=True)
        time.sleep(0.35)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=0))
    good = sum(1 for v in state.values() if v)
    print(f"done: {good}/{len(state)} resolved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
