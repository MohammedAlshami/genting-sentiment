#!/usr/bin/env python3
"""Parse collected quarterly reports and press releases into candidate rows.

Output is for verification; values are normalised to RM million.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QDIR = ROOT / "data" / "company_docs" / "quarterly"
MANIFEST = json.loads((ROOT / "data" / "company_docs" / "pdf_manifest.json").read_text())

NUM = r"\(?-?[\d,]+(?:\.\d+)?\)?"


def txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def nums(line: str) -> list[float]:
    out = []
    for s in re.findall(NUM, line):
        s2 = s.replace(",", "")
        neg = s2.startswith("(") and s2.endswith(")")
        v = float(s2.strip("()"))
        out.append(-v if neg else v)
    return out


def unit_scale(text: str) -> float:
    head = text[:4000]
    if "RM’000" in head or "RM'000" in head:
        return 0.001
    if re.search(r"RM[’']?(Mil|million|Mil\.)", head, re.I):
        return 1.0
    return 1.0


def find_line(text: str, pattern: str) -> str | None:
    for line in text.splitlines():
        if re.search(pattern, line, re.I):
            return line
    return None


def income_statement(text: str) -> dict:
    scale = unit_scale(text)
    out = {}
    line = find_line(text, r"^\s*Revenue\b")
    out["revenue"] = (nums(line)[0] * scale) if line and nums(line) else None

    line = find_line(text, r"^\s*Finance costs?\b")
    out["finance_cost"] = abs(nums(line)[0] * scale) if line and nums(line) else None

    pbt_line = None
    for cand in text.splitlines():
        low = cand.lower()
        if "before taxation" in low and ("profit" in low or "loss" in low) \
                and "share of" not in low:
            pbt_line = cand
            break
    out["pbt"] = (nums(pbt_line)[0] * scale) if pbt_line and nums(pbt_line) else None

    np_line = None
    for cand in text.splitlines():
        low = cand.lower()
        if ("for the period" in low or "for the financial period" in low
                or "for the financial year" in low or "for the year" in low):
            if ("profit" in low or "loss" in low) and "attributable" not in low \
                    and "comprehensive" not in low and "before taxation" not in low \
                    and "taxation" not in low:
                np_line = cand
                break
    out["net_profit"] = (nums(np_line)[0] * scale) if np_line and nums(np_line) else None

    # EPS: the standalone "Basic" line after the earnings-per-share heading
    eps = None
    lines = text.splitlines()
    for i, cand in enumerate(lines):
        if re.search(r"Basic\b", cand) and re.search(r"\d", cand) and "diluted" not in cand.lower():
            vals = nums(cand)
            if vals:
                eps = vals[0]
                break
        if re.search(r"Earnings.*per share", cand, re.I):
            for nxt in lines[i + 1:i + 6]:
                if re.search(r"Basic\b", nxt) and nums(nxt):
                    eps = nums(nxt)[0]
                    break
            if eps is not None:
                break
    out["eps"] = eps

    lt = find_line(text, r"^\s*Long term borrowings\b")
    st = find_line(text, r"^\s*Short term borrowings\b")
    out["_lt"] = nums(lt)[0] * scale if lt and nums(lt) else None
    out["_st"] = nums(st)[0] * scale if st and nums(st) else None
    out["total_debt"] = (out["_lt"] + out["_st"]) if out["_lt"] is not None and out["_st"] is not None else None

    cash = find_line(text, r"^\s*Cash and cash equivalents\b")
    # balance sheet line has two numbers (current, prior); cash-flow line also matches but has one
    out["cash"] = nums(cash)[0] * scale if cash and nums(cash) else None
    out["_scale"] = scale
    return out


def ebitda_from_pr(text: str) -> float | None:
    scale = 1.0
    m = re.search(r"Adjusted EBITDA(?:/\(LBITDA\))?\s+([\(\-\d,\.]+)", text)
    if m:
        vals = nums(m.group(1))
        return vals[0] if vals else None
    return None


def pairs(ticker: str):
    groups: dict[str, list[Path]] = {}
    for p in sorted((QDIR / ticker).glob("*.txt")):
        key = p.name.split("_")[1]
        groups.setdefault(key, []).append(p)
    for key, files in groups.items():
        report = next((f for f in files if "Press" not in f.name and "press" not in f.name), None)
        press = next((f for f in files if "Press" in f.name or "press" in f.name), None)
        if report and press:
            yield key, report, press


def main() -> int:
    rows = []
    for ticker in ("GENTING", "GENM"):
        for key, report, press in pairs(ticker):
            t = txt(report)
            inc = income_statement(t)
            pr = txt(press)
            rec = MANIFEST.get(f"klse_screener:{key}:1", {})
            rows.append({
                "company": ticker,
                "period_end": None,
                "date": report.name[:10],
                "announcement_id": key,
                "title": rec.get("title"),
                "url": f"https://www.klsescreener.com/v2/announcements/view/{key}",
                **inc,
                "ebitda": ebitda_from_pr(pr),
            })
    print(json.dumps(rows, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
