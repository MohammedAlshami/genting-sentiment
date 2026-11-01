#!/usr/bin/env python3
"""Parse cached KLSE Screener announcement pages into a structured JSON file."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data/raw/cache/company_events"


def text(html: str) -> str:
    s = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</(p|tr|div|h\d|li|table)>", "\n", s, flags=re.I)
    s = re.sub(r"</t[dh]>", " | ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = (
        s.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&#39;", "'")
        .replace("&quot;", '"')
    )
    s = s.replace(" | ", " ").replace("|", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


def field(t: str, label: str) -> str | None:
    m = re.search(rf"(?:^|\n)\s*{re.escape(label)}\s*\n([^\n]+)", t)
    return m.group(1).strip() if m else None


def parse(path: Path) -> dict | None:
    h = path.read_text(encoding="utf-8", errors="replace")
    title = re.search(r"<title>(.*?)</title>", h, re.S)
    t = text(h)
    date = re.search(r"Date Announced\s+([0-9]{1,2} \w{3} \d{4})", t)
    if not date:
        return None
    rec = {
        "id": path.stem.split("_")[-1],
        "date_announced": date.group(1),
        "title": (title.group(1).split("|")[0].strip() if title else ""),
        "company": field(t, "Company Name"),
        "category": field(t, "Category"),
        "reference": field(t, "Reference Number"),
        "body": t,
        "url": f"https://www.klsescreener.com/v2/announcements/view/{path.stem.split('_')[-1]}",
    }
    # Director / substantial shareholder structured fields
    if "Particulars of Director" in t or "Particulars of substantial" in t:
        rec["kind"] = "ownership_notice"
        rec["person"] = field(t, "Name")
        rec["direct_units"] = field(t, "Direct (units)")
        rec["direct_pct"] = field(t, "Direct (%)")
        rec["deemed_units"] = field(t, "Indirect/deemed interest (units)")
        rec["deemed_pct"] = field(t, "Indirect/deemed interest (%)")
        rec["total_after"] = field(t, "Total no of securities after change")
        rec["date_notice"] = field(t, "Date of notice")
        changes = []
        for m in re.finditer(
            r"\n(\d{2}/\d{2}/\d{4})\s*\n([\d,]+)\s*\n(Acquired|Disposed|Transferred|Others)\s*\n([^\n]+)",
            t,
        ):
            changes.append(
                {
                    "date": m.group(1),
                    "shares": int(m.group(2).replace(",", "")),
                    "type": m.group(3),
                    "interest": m.group(4).strip(),
                }
            )
        rec["changes"] = changes
        cons = re.findall(r"Consideration \(if any\)\s*\n(RM[\d.,]+)", t)
        rec["considerations"] = cons
    return rec


def main() -> None:
    recs = []
    for p in sorted(CACHE.glob("detail_*.html")):
        r = parse(p)
        if r:
            recs.append(r)
    out = CACHE / "parsed.json"
    out.write_text(json.dumps(recs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(recs)} parsed -> {out}")


if __name__ == "__main__":
    main()
