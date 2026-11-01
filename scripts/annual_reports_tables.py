#!/usr/bin/env python3
"""Extract all tables from every annual report with pdfplumber.

Two complementary passes per page:
  * ruled  - pdfplumber's line-based table finder (high precision, bordered tables)
  * text   - whitespace/x-position aligned blocks built from pdfplumber words
             (catches financial statements and borderless notes tables)

Every cell is preserved as a string exactly as extracted (None -> "").
Output: data/company_docs/annual/tables/<TICKER>_AR_<YEAR>.json
CSV shards: data/company_docs/annual/tables/.shards/<TICKER>_AR_<YEAR>.csv
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "data" / "company_docs" / "annual"
OUT_DIR = PDF_DIR / "tables"
SHARD_DIR = OUT_DIR / ".shards"
OUT_DIR.mkdir(parents=True, exist_ok=True)
SHARD_DIR.mkdir(parents=True, exist_ok=True)

NUM_RE = re.compile(
    r"^[\(\-\u2212]?\s*(?:RM|MYR|\$)?\s*\d[\d,]*(?:\.\d+)?\s*%?\)?$"
)
YEAR_RE = re.compile(r"^(?:19|20)\d{2}$")
UNIT_RE = re.compile(r"(RM|MYR|US\$|USD|'000|million|billion|sen|%|per share)", re.I)


def clean(v) -> str:
    if v is None:
        return ""
    s = str(v).replace("\x00", " ")
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def is_num(s: str) -> bool:
    s = s.strip()
    if not s or s in {"-", "–", "—", "nil", "N/A", "n/a"}:
        return False
    if not re.search(r"\d", s):
        return False
    return bool(NUM_RE.match(s))


def page_lines(page) -> list[dict]:
    try:
        return page.extract_text_lines(strip=True, return_chars=False)
    except Exception:
        return []


def caption_above(lines: list[dict], top: float, max_lines: int = 2) -> str:
    above = [ln["text"] for ln in lines if ln["bottom"] <= top + 1 and ln["text"].strip()]
    if not above:
        return ""
    return " | ".join(above[-max_lines:])


def num_tokens(s: str) -> int:
    return sum(1 for t in s.split() if is_num(t))


def expand_multiline_row(row: list[str]) -> list[list[str]]:
    """Split a ruled-table row whose cells contain aligned line breaks.

    pdfplumber sometimes returns a whole ruled block as one row, with every
    printed row packed into newline-separated cells.  When numeric columns and
    the label column share the same line count, restore the individual rows.
    """
    parts = [c.split("\n") for c in row]
    counts = [len(p) for p in parts]
    numeric_cols = [i for i, p in enumerate(parts)
                    if counts[i] and sum(1 for x in p if is_num(x)) / counts[i] >= 0.6]
    if not numeric_cols:
        return [row]
    n = max(counts[i] for i in numeric_cols)
    if n < 2:
        return [row]
    if any(c not in (1, n) and not (c > n and i not in numeric_cols)
           for i, c in enumerate(counts)):
        return [row]
    out = []
    for i in range(n):
        newrow = []
        for j, p in enumerate(parts):
            c = counts[j]
            if c == n:
                newrow.append(p[i])
            elif c == 1:
                newrow.append(p[0])
            else:  # c > n on a label column: merge wrapped tail into last line
                newrow.append(p[i] if i < n - 1 else " ".join(p[n - 1:]))
        out.append(newrow)
    return out


def split_cells(words: list[dict], threshold: float) -> list[str]:
    """Split a line's words into cells at horizontal gaps >= threshold."""
    if not words:
        return []
    words = sorted(words, key=lambda w: w["x0"])
    cells: list[str] = []
    cur = [words[0]["text"]]
    prev_x1 = words[0]["x1"]
    for w in words[1:]:
        if w["x0"] - prev_x1 >= threshold:
            cells.append(" ".join(cur))
            cur = [w["text"]]
        else:
            cur.append(w["text"])
        prev_x1 = max(prev_x1, w["x1"])
    cells.append(" ".join(cur))
    return [clean(c) for c in cells]


def text_tables(page, lines: list[dict]) -> list[dict]:
    """Detect borderless table blocks by column alignment of words."""
    try:
        words = page.extract_words(keep_blank_chars=False, use_text_flow=False)
    except Exception:
        return []
    if not words:
        return []
    width = float(page.width)
    gap = max(9.0, width * 0.014)  # ~8.3pt on A4
    # group words into visual lines
    words.sort(key=lambda w: (round(w["top"], 1), w["x0"]))
    groups: list[list[dict]] = []
    for w in words:
        if groups and abs(w["top"] - groups[-1][0]["top"]) <= 2.0:
            groups[-1].append(w)
        else:
            groups.append([w])
    rows = []
    for g in groups:
        cells = split_cells(g, gap)
        if not cells:
            continue
        rows.append({
            "top": min(w["top"] for w in g),
            "bottom": max(w["bottom"] for w in g),
            "cells": cells,
            "ntok": sum(num_tokens(c) for c in cells),
            "ncell": len(cells),
            "nwords": len(g),
        })

    # A row is table-worthy if it has >=2 cells and at least one numeric cell,
    # or is a header row (>=2 cells, contains a year/unit, few words).
    def table_row(r: dict) -> bool:
        txt = " ".join(r["cells"])
        headerish = bool(YEAR_RE.search(txt) or UNIT_RE.search(txt))
        if r["ncell"] < 2:
            return False
        if r["ntok"] >= 1:
            return True
        return headerish and r["nwords"] <= 12

    def prose(r: dict) -> bool:
        return r["nwords"] > 14 and r["ntok"] <= 1

    blocks: list[list[dict]] = []
    cur: list[dict] = []
    for r in rows:
        ok = table_row(r) and not prose(r)
        if ok:
            # don't let a wildly different column count join the block
            if cur and abs(r["ncell"] - cur[-1]["ncell"]) > 3:
                if len(cur) >= 2:
                    blocks.append(cur)
                cur = []
            cur.append(r)
        else:
            if len(cur) >= 2:
                blocks.append(cur)
            cur = []
    if len(cur) >= 2:
        blocks.append(cur)

    out = []
    for b in blocks:
        numeric_cells = sum(1 for r in b for c in r["cells"] if is_num(c))
        if numeric_cells < 2:
            continue
        # Require at least two rows with a number and a reasonably numeric density.
        nrows_num = sum(1 for r in b if r["ntok"] >= 1)
        if nrows_num < 2:
            continue
        cells = [r["cells"] for r in b]
        maxcols = max(len(r) for r in cells)
        # pad ragged rows on the right so the table is rectangular
        cells = [c + [""] * (maxcols - len(c)) for c in cells]
        out.append({
            "method": "text",
            "bbox": [0.0, round(b[0]["top"], 1), round(width, 1), round(b[-1]["bottom"], 1)],
            "rows": cells,
        })
    return out


def process(pdf_path: Path) -> dict:
    m = re.match(r"([A-Z]+)_AR_(\d{4})", pdf_path.name)
    ticker, year = m.group(1), int(m.group(2))
    json_path = OUT_DIR / f"{pdf_path.stem}.json"
    shard_path = SHARD_DIR / f"{pdf_path.stem}.csv"
    all_tables = []
    n_ruled = n_text = n_rows = n_cells = 0
    t0 = time.time()
    with pdfplumber.open(pdf_path) as pdf:
        npages = len(pdf.pages)
        for pno, page in enumerate(pdf.pages, 1):
            lines = page_lines(page)
            page_tables = []
            ruled_boxes = []
            try:
                ruled = page.extract_tables(table_settings={
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                    "snap_tolerance": 3,
                    "join_tolerance": 3,
                    "edge_min_length": 3,
                    "intersection_tolerance": 5,
                })
            except Exception as exc:  # noqa: BLE001
                ruled = []
                print(f"  ruled fail {pdf_path.name} p{pno}: {exc}", file=sys.stderr)
            for tb in ruled:
                rows = []
                for row in tb:
                    rows.extend(expand_multiline_row([clean(c) for c in row]))
                if len(rows) < 2:
                    continue
                if max((len(r) for r in rows), default=0) < 2:
                    continue
                nonempty = sum(1 for r in rows for c in r if c)
                if nonempty < 3:
                    continue
                # A real table has at least two rows with two populated columns;
                # this rejects page borders and decorative rules.
                if sum(1 for r in rows if sum(1 for c in r if c) >= 2) < 2:
                    continue
                # trim fully empty rows/cols at edges
                rows = [r for r in rows if any(c for c in r)]
                maxc = max(len(r) for r in rows)
                rows = [r + [""] * (maxc - len(r)) for r in rows]
                page_tables.append({"method": "ruled", "rows": rows, "bbox": None})
                n_ruled += 1
            if not page_tables:
                for tb in text_tables(page, lines):
                    page_tables.append(tb)
                    n_text += 1
            for k, tb in enumerate(page_tables):
                rows = tb["rows"]
                cap = ""
                if tb.get("bbox"):
                    cap = caption_above(lines, tb["bbox"][1])
                if not cap:
                    # first non-empty row is decent context for ruled tables
                    cap = " | ".join(c for c in rows[0] if c)[:300]
                ctx = caption_above(lines, (tb["bbox"][1] if tb.get("bbox") else 0), 4)
                rec = {
                    "page": pno,
                    "table_index": k,
                    "method": tb["method"],
                    "bbox": tb.get("bbox"),
                    "caption": cap[:400],
                    "context": ctx[:800],
                    "n_rows": len(rows),
                    "n_cols": max((len(r) for r in rows), default=0),
                    "rows": rows,
                }
                all_tables.append(rec)
                n_rows += len(rows)
                n_cells += sum(len(r) for r in rows)
    meta = {
        "ticker": ticker, "year": year, "file": str(pdf_path.relative_to(ROOT)),
        "pages": npages, "n_tables": len(all_tables), "n_ruled": n_ruled,
        "n_text": n_text, "n_rows": n_rows, "n_cells": n_cells,
        "seconds": round(time.time() - t0, 1), "tables": all_tables,
    }
    json_path.write_text(json.dumps(meta, ensure_ascii=False, separators=(",", ":")),
                         encoding="utf-8")
    # CSV shard of numeric cells
    import csv
    with shard_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["page", "table_index", "method", "row_index", "col_index",
                    "value_text", "value_number", "row_label", "col_label", "caption"])
        for tb in all_tables:
            rows = tb["rows"]
            # header labels: rows before first row with any number
            header_end = 0
            for ri, r in enumerate(rows[:8]):
                if any(is_num(c) for c in r):
                    header_end = ri
                    break
            else:
                header_end = min(2, len(rows))
            col_labels = []
            for j in range(tb["n_cols"]):
                lab = ""
                for ri in range(header_end - 1, -1, -1):
                    if j < len(rows[ri]) and rows[ri][j] and not is_num(rows[ri][j]):
                        lab = rows[ri][j]
                        break
                col_labels.append(lab)
            last_label = ""
            for ri, r in enumerate(rows):
                label_cells = [c for c in r if c and not is_num(c)]
                if label_cells:
                    labs = []
                    for c in r:
                        if is_num(c):
                            break
                        if c:
                            labs.append(c)
                    if labs:
                        last_label = " ".join(labs)
                row_label = last_label
                for j, c in enumerate(r):
                    if not is_num(c):
                        continue
                    txt = c.strip()
                    neg = txt.startswith("(") and txt.endswith(")")
                    raw = txt.strip("()").replace(",", "").replace("RM", "").replace("%", "").strip()
                    try:
                        val = float(raw)
                        if neg:
                            val = -val
                    except ValueError:
                        val = ""
                    w.writerow([tb["page"], tb["table_index"], tb["method"], ri, j,
                                txt, val, row_label[:200], col_labels[j][:120],
                                tb["caption"][:300]])
    return {k: meta[k] for k in ("ticker", "year", "pages", "n_tables", "n_ruled",
                                 "n_text", "n_rows", "n_cells", "seconds")}


def main() -> int:
    files = sorted(PDF_DIR.glob("*_AR_*.pdf"))
    if len(sys.argv) > 1:
        wanted = set(sys.argv[1:])
        files = [f for f in files if f.stem in wanted or f.name in wanted]
    from concurrent.futures import ProcessPoolExecutor, as_completed
    results = []
    with ProcessPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(process, f): f for f in files}
        for i, fut in enumerate(as_completed(futs), 1):
            f = futs[fut]
            try:
                r = fut.result()
                results.append(r)
                print(f"[{i:2d}/{len(files)}] {r['ticker']} {r['year']}: "
                      f"{r['n_tables']:4d} tables ({r['n_ruled']} ruled/{r['n_text']} text) "
                      f"{r['n_rows']:6d} rows {r['n_cells']:7d} cells {r['seconds']:6.1f}s")
            except Exception as exc:  # noqa: BLE001
                print(f"FAILED {f.name}: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
