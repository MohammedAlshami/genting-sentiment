#!/usr/bin/env python3
"""Validate data/raw/company_announcements.jsonl."""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IN = ROOT / "data" / "raw" / "company_announcements.jsonl"
OUT = ROOT / "data" / "raw" / "announcements_validation.json"
# Window is 2 Nov 2024 00:00 MYT (UTC+8) to 2 Nov 2026 23:59 MYT.
START = int(datetime(2024, 11, 1, 16, 0, tzinfo=timezone.utc).timestamp())
END = int(datetime(2026, 11, 2, 15, 59, tzinfo=timezone.utc).timestamp())


def main():
    records = []
    errors = []
    for i, line in enumerate(IN.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception as exc:  # noqa: BLE001
            errors.append({"line": i, "error": f"bad json: {exc}"})
            continue
        records.append(r)
        for f in ("source", "ticker", "native_id", "created_utc", "url", "title"):
            if not r.get(f):
                errors.append({"line": i, "native_id": r.get("native_id"), "error": f"missing {f}"})
        if r.get("ticker") not in ("GENTING", "GENM", "UNKNOWN"):
            errors.append({"line": i, "native_id": r.get("native_id"), "error": "bad ticker"})
        ts = r.get("created_utc")
        if not isinstance(ts, int) or not (START <= ts <= END):
            errors.append({"line": i, "native_id": r.get("native_id"), "error": f"outside window: {ts}"})
    ids = Counter(r.get("native_id") for r in records)
    dups = {k: v for k, v in ids.items() if v > 1}
    out = {
        "records": len(records),
        "by_ticker": dict(Counter(r.get("ticker") for r in records)),
        "by_source": dict(Counter(r.get("source") for r in records)),
        "by_category": dict(Counter(r.get("category") or "" for r in records).most_common()),
        "with_attachments": sum(1 for r in records if r.get("attachments")),
        "attachment_count": sum(len(r.get("attachments", [])) for r in records),
        "duplicate_native_ids": dups,
        "errors": errors,
        "date_min": min((r.get("date") for r in records), default=None),
        "date_max": max((r.get("date") for r in records), default=None),
        "body_chars": sum(len(r.get("body") or "") for r in records),
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "by_category"}, indent=2)[:3000])
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
