#!/usr/bin/env python3
"""Fill empty announcement bodies from the cached KLSE Screener detail pages."""
from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
JSONL = ROOT / "data" / "raw" / "company_announcements.jsonl"
PAGES = ROOT / "data" / "company_docs" / "announcements" / "pages"


def main():
    records = []
    for line in JSONL.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    fixed = 0
    for r in records:
        if (r.get("body") or "").strip():
            continue
        m = re.search(r"/view/(\d+)", r.get("ks_url") or "")
        if not m:
            continue
        path = PAGES / f"ks_detail_{m.group(1)}.html"
        if not path.exists():
            continue
        s = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "lxml")
        d = s.find("div", id="content")
        if not d:
            continue
        text = d.get_text("\n", strip=True)
        # Drop the ad-block notice and the price header.
        text = re.sub(r"^Our website.*?ad blocker\.\n?", "", text, flags=re.S)
        lines = [x.strip() for x in text.splitlines() if x.strip()]
        # Start at the announcement title (or at 'Subject' if the title was rewritten).
        start = 0
        for i, x in enumerate(lines[:8]):
            if x.upper().startswith(r["title"][:25].upper()) or x == "Subject":
                start = i
                break
        body = "\n".join(lines[start:])
        if len(body) > 20:
            r["body"] = body[:20000]
            r.setdefault("raw", {})["body_source"] = "ks_detail_div_content"
            fixed += 1
    JSONL.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")
    print(f"filled {fixed} empty bodies; {len(records)} records")


if __name__ == "__main__":
    main()
