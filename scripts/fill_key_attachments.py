#!/usr/bin/env python3
"""Fetch Bursa bodies/attachments for a short list of key new records."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect_announcements import (  # noqa: E402
    parse_bursa, polite_get, fetch_attachment, safe_name, PAGEDIR, PDFDIR,
)

ROOT = Path(__file__).resolve().parent.parent
JSONL = ROOT / "data" / "raw" / "company_announcements.jsonl"
WANT = {
    "3504167", "3528971", "3558043", "3586096",   # GENM quarterly results
    "3542611", "3542729",                          # GENM AGM notice + circular
    "3598504", "3600372",                          # GENM takeover notices
    "3616382", "3606961", "3610092", "3612871",    # GENTING MTN
    "3717932",                                      # rights issue listing application
}


def main():
    records = [json.loads(x) for x in JSONL.read_text(encoding="utf-8").splitlines() if x.strip()]
    done = 0
    for r in records:
        if r.get("ann_id") not in WANT:
            continue
        if r.get("attachments"):
            continue
        ann = r["ann_id"]
        html = polite_get(f"https://disclosure.bursamalaysia.com/FileAccess/viewHtml?e={ann}",
                          PAGEDIR / f"bursa_{ann}.html")
        b = parse_bursa(html)
        if b["body"] and len(b["body"]) > len(r.get("body") or ""):
            r["body"] = b["body"]
        for j, att in enumerate(b["attachments"], 1):
            dest = PDFDIR / f"{ann}_{j}_{safe_name(att['name'])}"
            if dest.suffix.lower() != ".pdf":
                dest = dest.with_suffix(".pdf")
            info = fetch_attachment(att["url"], dest)
            if info:
                info["name"] = att["name"]
                info["url"] = att["url"]
                r.setdefault("attachments", []).append(info)
        if r["attachments"]:
            r.setdefault("raw", {})["attachment_url"] = r["attachments"][0]["url"]
            done += 1
        print(r["date"], r["ticker"], r["title"][:70], "att=", len(r["attachments"]), flush=True)
    JSONL.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")
    print("updated", done)


if __name__ == "__main__":
    main()
