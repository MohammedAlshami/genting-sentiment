#!/usr/bin/env python3
"""Parse the primary financial statements from each annual report.

Uses pdfplumber word positions so the Group current-year column can be isolated
from the prior-year and Company columns. Dumps parsed rows to
data/company_docs/annual/statements/<TICKER>_AR_<YEAR>.json for audit.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "data" / "company_docs" / "annual"
OUT_DIR = PDF_DIR / "statements"
OUT_DIR.mkdir(parents=True, exist_ok=True)

NUM = re.compile(r"^\(?-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\)?%?$")
YEAR = re.compile(r"^\(?((?:19|20)\d{2})\)?$")
DATEYEAR = re.compile(r"^(?:\d{1,2}[./-]){1,2}((?:19|20)\d{2})$")
UNIT_PATTERNS = [
    (re.compile(r"RM\s*['\u2019]?\s*0{3}|RM\s*thousand", re.I), "RM'000", 0.001),
    (re.compile(r"RM\s*(?:million|mil\b|m\b)", re.I), "RM million", 1.0),
    (re.compile(r"RM\s*billion", re.I), "RM billion", 1000.0),
]


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def is_num(s: str) -> bool:
    s = clean(s)
    if s in {"-", "\u2013", "\u2014"}:
        return True
    return bool(NUM.match(s.replace(" ", "")))


def to_num(s: str):
    s = clean(s)
    if s in {"-", "\u2013", "\u2014"}:
        return 0.0
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()").replace(",", "").replace("%", "")
    try:
        v = float(s)
    except ValueError:
        return None
    return -v if neg else v


def unit_for(text: str):
    head = text[:800]
    for pat, name, scale in UNIT_PATTERNS:
        if pat.search(head):
            return name, scale
    return "", 1.0


def group_lines(words: list[dict]) -> list[dict]:
    words = sorted(words, key=lambda w: (round(w["top"], 1), w["x0"]))
    groups = []
    for w in words:
        if groups and abs(w["top"] - groups[-1][0]["top"]) <= 2.2:
            groups[-1].append(w)
        else:
            groups.append([w])
    out = []
    for g in groups:
        g = sorted(g, key=lambda w: w["x0"])
        out.append({"top": min(w["top"] for w in g), "words": g,
                    "text": " ".join(w["text"] for w in g)})
    return out


def find_year_header(lines: list[dict], report_year: int):
    best = None
    for ln in lines[:80]:
        toks = []
        for w in ln["words"]:
            token = w["text"].strip().strip("()")
            m = YEAR.match(token) or DATEYEAR.match(token)
            if m:
                y = int(m.group(1))
                if abs(y - report_year) <= 2:
                    toks.append((w, y))
        if len(toks) >= 2:
            # prefer header with report year first and max tokens
            score = len(toks) + (2 if toks[0][1] == report_year else 0)
            if best is None or score > best[0]:
                best = (score, toks)
    return best[1] if best else None


def parse_page(page, report_year: int):
    words = page.extract_words(keep_blank_chars=False, use_text_flow=False)
    lines = group_lines(words)
    hdr = find_year_header(lines, report_year)
    if not hdr:
        return None
    # Cluster identical year values by x; first occurrence of report year = Group
    year_positions = []
    for w, y in hdr:
        year_positions.append({"year": y, "center": (w["x0"] + w["x1"]) / 2,
                               "x0": w["x0"], "x1": w["x1"]})
    # exact year columns (only report and report-1 matter)
    cur = [p for p in year_positions if p["year"] == report_year]
    pri = [p for p in year_positions if p["year"] == report_year - 1]
    if not cur:
        return None
    group_cur = cur[0]
    group_pri = pri[0] if pri else None
    left_limit = min(p["x0"] for p in year_positions) - 8
    rows = []
    pending_label = ""
    for ln in lines:
        ws = ln["words"]
        # numeric tokens on the right side
        vals = []
        label_words = []
        for w in ws:
            txt = w["text"].strip()
            center = (w["x0"] + w["x1"]) / 2
            if center >= left_limit and is_num(txt):
                vals.append((w, txt))
            elif w["x1"] < left_limit:
                label_words.append(txt)
        label = clean(" ".join(label_words))
        # drop trailing note numbers / section numbers from label
        label = re.sub(r"\s+(?:\d{1,3}[a-z]?|4\s*&\s*5|5\s*&\s*9|9\s*&\s*4)$", "", label)
        label = clean(label)
        if not vals:
            if label and len(label) > 2 and not label.isdigit():
                pending_label = label
            continue
        if not label and pending_label:
            label = pending_label
        elif label and pending_label:
            # A printed label can wrap onto a second line ("NET CASH FLOW FROM
            # OPERATING" / "ACTIVITIES").  Join only short, upper-case tails.
            if (len(label.split()) <= 2 and label.isupper()
                    and not label.startswith("-")):
                label = clean(pending_label + " " + label)
            elif label[0].islower() or re.fullmatch(r"[\d\s&,()]+", label):
                label = clean(pending_label + " " + label)
        # choose value nearest to group current column, within tolerance
        best = None
        for w, txt in vals:
            center = (w["x0"] + w["x1"]) / 2
            d = abs(center - group_cur["center"])
            if d <= 42:
                if best is None or d < best[0]:
                    best = (d, txt, w)
        if best is None:
            pending_label = label or pending_label
            continue
        val_txt = best[1]
        pri_txt = None
        if group_pri:
            bp = None
            for w, txt in vals:
                center = (w["x0"] + w["x1"]) / 2
                d = abs(center - group_pri["center"])
                if d <= 42 and (bp is None or d < bp[0]):
                    bp = (d, txt)
            pri_txt = bp[1] if bp else None
        rows.append({"label": label, "value_text": val_txt,
                     "value": to_num(val_txt), "prior_text": pri_txt,
                     "prior": to_num(pri_txt) if pri_txt else None,
                     "top": round(ln["top"], 1)})
    return {"rows": rows, "header": [(p["year"], round(p["center"], 1)) for p in year_positions],
            "group_cur_x": round(group_cur["center"], 1)}


def statement_pages(pages_text: list[str], kind: str) -> list[int]:
    """Return 1-based PDF page numbers for a primary statement."""
    starts = {
        "income": [r"income statements?\b", r"consolidated (?:statement of profit or loss|income statement)",
                   r"profit\s*(?:&|and)\s*loss accounts?\b"],
        "balance": [r"statements? of financial position\b", r"balance[\s-]*sheets?\b"],
        "cashflow": [r"statements? of cash flows?\b", r"cash flow statements?\b"],
    }[kind]
    # Headings may sit under a page number/sidebar; scan the first few lines.
    cand = []
    for i, txt in enumerate(pages_text, 1):
        if i < 5:
            continue
        lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
        head = " ".join(lines[:5]).lower()
        if not any(re.search(p, head, re.I) for p in starts):
            continue
        # exclude notes pages and TOC
        if "notes to the financial" in head or "notes to financial" in head:
            continue
        if "notes to consolidated" in head or "notes to statements" in head:
            continue
        if len(lines) < 12:
            continue
        # a primary statement carries a period marker near the heading
        period = ("for the financial year" in head or "as at" in head
                  or "31 december" in head or "year ended" in head)
        if not period:
            continue
        cand.append(i)
    if not cand:
        return []
    # group consecutive pages; choose the first group after page 20
    groups = []
    for p in cand:
        if groups and p - groups[-1][-1] <= 2:
            groups[-1].append(p)
        else:
            groups.append([p])
    groups = [g for g in groups if g[0] > 15]
    if not groups:
        return []
    # statements all live in the same first group or adjacent groups
    first = groups[0]
    out = list(first)
    # include immediate continuation pages if heading carries (cont'd) or same title
    j = out[-1] + 1
    while j <= len(pages_text) and j <= out[-1] + 4:
        lines = [ln.strip() for ln in pages_text[j - 1].splitlines() if ln.strip()]
        head = " ".join(lines[:5]).lower()
        key = {"income": "income statement", "balance": "financial position",
               "cashflow": "cash flow"}[kind]
        if key in head and "notes to" not in head:
            out.append(j)
            j += 1
        else:
            break
    return out


def main() -> int:
    files = sorted(PDF_DIR.glob("*_AR_*.pdf"))
    if len(sys.argv) > 1:
        files = [f for f in files if f.stem in set(sys.argv[1:]) or f.name in set(sys.argv[1:])]
    for pdf_path in files:
        m = re.match(r"([A-Z]+)_AR_(\d{4})", pdf_path.name)
        ticker, year = m.group(1), int(m.group(2))
        text_path = PDF_DIR / "text" / f"{pdf_path.stem}.txt"
        pages_text = text_path.read_text(encoding="utf-8", errors="replace").split("\f")
        if pages_text and not pages_text[-1].strip():
            pages_text.pop()
        result = {"ticker": ticker, "year": year,
                  "file": str(pdf_path.relative_to(ROOT)), "statements": {}}
        with pdfplumber.open(pdf_path) as pdf:
            for kind in ("income", "balance", "cashflow"):
                pnos = statement_pages(pages_text, kind)
                pages = []
                for pno in pnos:
                    if 1 <= pno <= len(pdf.pages):
                        parsed = parse_page(pdf.pages[pno - 1], year)
                        if parsed:
                            u, scale = unit_for(pages_text[pno - 1])
                            parsed.update(page=pno, unit=u, scale=scale)
                            pages.append(parsed)
                result["statements"][kind] = pages
        out = OUT_DIR / f"{pdf_path.stem}.json"
        out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        counts = " ".join(f"{k}:{len(v)}p/{sum(len(p['rows']) for p in v)}r"
                          for k, v in result["statements"].items())
        print(f"{pdf_path.stem}: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
