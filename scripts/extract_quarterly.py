#!/usr/bin/env python3
"""Extract full text and every numeric-bearing table from the quarterly PDFs.

For each PDF we write:
  data/company_docs/quarterly/text/<TICKER>_<YEAR>Q<Q>.txt
  data/company_docs/quarterly/tables/<TICKER>_<YEAR>Q<Q>.csv

The table CSV is long-form and keeps every cell (text and numeric) with page,
table index, row, column and coordinates.  Two pdfplumber strategies are used:
  * "lines"  - ruled tables via page.extract_tables()
  * "words"  - borderless numeric tables reconstructed from pdfplumber word
               coordinates (many Bursa quarterly reports have no ruling lines)

Usage:
  python scripts/extract_quarterly.py --workers 4
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
QDIR = ROOT / "data" / "company_docs" / "quarterly"
TEXTDIR = QDIR / "text"
TABLEDIR = QDIR / "tables"
MANIFEST = ROOT / "data" / "company_docs" / "manifests" / "quarterly_reports.csv"

NUM_RE = re.compile(r"^\(?[-+\u2013]?[\d,]+(?:\.\d+)?\)?%?$")
DATE_RE = re.compile(r"^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$")


def is_number(text: str) -> bool:
    if text is None:
        return False
    t = text.strip().replace(" ", "")
    if not t or not any(ch.isdigit() for ch in t):
        return False
    if DATE_RE.match(t):
        return False
    if not NUM_RE.match(t):
        return False
    # reject things like "2026" alone? No: years can be legitimate table cells.
    return True


def number_value(text: str):
    if text is None:
        return None
    t = text.strip().replace(" ", "").replace(",", "")
    if not t or not is_number(t):
        return None
    pct = t.endswith("%")
    t = t.rstrip("%")
    neg = t.startswith("(") and t.endswith(")")
    t = t.strip("()")
    if t in ("-", "\u2013", "+", ""):
        return None
    try:
        v = float(t)
    except ValueError:
        return None
    if neg:
        v = -v
    return v


def group_lines(page):
    words = page.extract_words(
        x_tolerance=1.2, y_tolerance=2.2, keep_blank_chars=False, use_text_flow=False
    )
    words.sort(key=lambda w: (round(w["top"], 1), w["x0"]))
    lines = []
    for w in words:
        if lines and abs(w["top"] - lines[-1]["top"]) < 3.0:
            lines[-1]["words"].append(w)
        else:
            lines.append({"top": w["top"], "bottom": w["bottom"], "words": [w]})
    for line in lines:
        line["words"].sort(key=lambda w: w["x0"])
    return lines


def split_cells(line, gap: float = 10.0):
    cells = []
    cur = None
    for w in line["words"]:
        if cur is None:
            cur = {"x0": w["x0"], "x1": w["x1"], "text": w["text"]}
        elif w["x0"] - cur["x1"] >= gap:
            cells.append(cur)
            cur = {"x0": w["x0"], "x1": w["x1"], "text": w["text"]}
        else:
            cur["text"] = cur["text"] + " " + w["text"]
            cur["x1"] = w["x1"]
    if cur:
        cells.append(cur)
    return cells


def numeric_cells(cells):
    return [c for c in cells if is_number(c["text"])]


def word_tables(page):
    """Reconstruct borderless numeric tables from word coordinates."""
    lines = group_lines(page)
    if not lines:
        return []
    heights = [max(1.0, l["bottom"] - l["top"]) for l in lines]
    med_h = sorted(heights)[len(heights) // 2]
    candidates = []
    for idx, line in enumerate(lines):
        cells = split_cells(line)
        nums = numeric_cells(cells)
        if len(nums) < 2:
            continue
        gaps = [nums[j + 1]["x0"] - nums[j]["x1"] for j in range(len(nums) - 1)]
        if not gaps or max(gaps) < 16:
            continue
        candidates.append((idx, line, cells, nums))

    # Group candidate rows into contiguous blocks.
    blocks = []
    cur = []
    for item in candidates:
        idx, line, cells, nums = item
        if not cur:
            cur = [item]
            continue
        prev_idx = cur[-1][0]
        gap = line["top"] - lines[prev_idx]["bottom"]
        # allow one intervening text line, but not a large vertical gap
        if idx - prev_idx <= 4 and gap <= max(med_h * 4.0, 75):
            cur.append(item)
        else:
            blocks.append(cur)
            cur = [item]
    if cur:
        blocks.append(cur)

    tables = []
    for block in blocks:
        if len(block) < 2:
            continue
        n_nums = sum(len(b[3]) for b in block)
        if n_nums < 4:
            continue
        first_idx = block[0][0]
        last_idx = block[-1][0]
        # Header = up to 6 immediately preceding text lines that are close enough.
        header = []
        j = first_idx - 1
        while j >= 0 and len(header) < 6:
            top_gap = lines[first_idx]["top"] - lines[j]["bottom"]
            if top_gap > med_h * 6.0:
                break
            header.insert(0, lines[j])
            j -= 1
        # Keep intervening label lines (0 numeric cells) so two-line row labels
        # and section headings are not lost; drop rows without any text.
        block_idxs = {b[0] for b in block}
        rows = []
        for idx in range(first_idx, last_idx + 1):
            cells = split_cells(lines[idx])
            if not cells:
                continue
            if idx in block_idxs or not any(is_number(c["text"]) for c in cells):
                rows.append(cells)
        if sum(1 for r in rows if any(is_number(c["text"]) for c in r)) < 2:
            continue
        tables.append({"header": header, "rows": rows, "strategy": "words"})
    return tables


def line_tables(page):
    """Ruled tables as detected by pdfplumber's default strategy."""
    try:
        raw = page.extract_tables()
    except Exception:
        return []
    out = []
    for tbl in raw:
        if not tbl or len(tbl) < 2:
            continue
        ncols = max(len(r) for r in tbl)
        if ncols < 2:
            continue
        n_nums = sum(1 for r in tbl for c in r if c and is_number(str(c)))
        if n_nums < 2:
            continue
        rows = [[("" if c is None else str(c).replace("\n", " ").strip()) for c in r] for r in tbl]
        # Treat the first row as header if it has no numeric cells.
        out.append({"header": [], "rows": rows, "strategy": "lines"})
    return out


def cell_label(header_rows, cells, col_idx):
    """Best-effort column label for a cell, from header rows overlapping its x-range."""
    if not header_rows:
        return ""
    cell = cells[col_idx]
    labels = []
    for hline in header_rows:
        hcells = split_cells(hline)
        best = None
        best_overlap = 0.0
        for hc in hcells:
            ov = min(cell["x1"], hc["x1"]) - max(cell["x0"], hc["x0"])
            if ov > best_overlap:
                best_overlap = ov
                best = hc
        if best and best_overlap > 1.0:
            labels.append(best["text"])
    return " / ".join(dict.fromkeys(labels))[-200:]


def row_label(cells, nums, prev_text=""):
    first_num_idx = None
    for i, c in enumerate(cells):
        if is_number(c["text"]):
            first_num_idx = i
            break
    label = ""
    if first_num_idx is not None and first_num_idx > 0:
        label = " ".join(c["text"] for c in cells[:first_num_idx]).strip()
    if not label:
        label = prev_text.strip()
    return label[:300]


def extract_one(pdf_path: Path) -> dict:
    stem = pdf_path.stem
    text_out = TEXTDIR / f"{stem}.txt"
    table_out = TABLEDIR / f"{stem}.csv"
    t0 = time.time()
    pages = 0
    text_chars = 0
    n_tables = 0
    n_cells = 0
    n_numeric = 0
    errors = []
    table_rows = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        pages = len(pdf.pages)
        with text_out.open("w", encoding="utf-8") as tf:
            for pno, page in enumerate(pdf.pages, 1):
                try:
                    txt = page.extract_text(x_tolerance=1.5, y_tolerance=3) or ""
                except Exception as exc:  # noqa: BLE001
                    txt = ""
                    errors.append(f"p{pno} text: {exc}")
                text_chars += len(txt)
                tf.write(f"\n===== PAGE {pno} =====\n")
                tf.write(txt)
                tf.write("\n")

                try:
                    tables = line_tables(page)
                    if not tables:
                        tables = word_tables(page)
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"p{pno} tables: {exc}")
                    tables = []

                for ti, table in enumerate(tables, 1):
                    n_tables += 1
                    header = table.get("header") or []
                    rows = table["rows"]
                    strategy = table["strategy"]
                    prev_text = ""
                    for ri, row in enumerate(rows, 1):
                        # normalise: rows may be list[str] or list[dict]
                        if row and isinstance(row[0], dict):
                            cells = row
                            cell_texts = [c["text"] for c in cells]
                        else:
                            cell_texts = [str(c) for c in row]
                            # synthesise coordinates from cell order for labels
                            cells = [
                                {"x0": 0.0, "x1": 0.0, "text": t} for t in cell_texts
                            ]
                        rlabel = row_label(cells, numeric_cells(cells), prev_text)
                        if cell_texts and not any(is_number(t) for t in cell_texts):
                            prev_text = " ".join(t for t in cell_texts if t).strip()[:300]
                        for ci, val in enumerate(cell_texts, 1):
                            if ci > len(cells):
                                cell = {"x0": 0.0, "x1": 0.0, "text": val}
                            else:
                                cell = cells[ci - 1]
                            clabel = cell_label(header, cells, ci - 1) if strategy == "words" else ""
                            if strategy == "lines" and ri == 1:
                                clabel = ""
                            num = number_value(val)
                            table_rows.append(
                                {
                                    "page": pno,
                                    "table_index": ti,
                                    "row": ri,
                                    "col": ci,
                                    "value_text": val,
                                    "value_number": "" if num is None else repr(num),
                                    "row_label": rlabel if num is not None else "",
                                    "col_label": clabel if num is not None else "",
                                    "strategy": strategy,
                                }
                            )
                            n_cells += 1
                            if num is not None:
                                n_numeric += 1
                tf.flush()
    tmp = table_out.with_suffix(".csv.part")
    with tmp.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(
            fh,
            fieldnames=[
                "page", "table_index", "row", "col", "value_text",
                "value_number", "row_label", "col_label", "strategy",
            ],
        )
        w.writeheader()
        w.writerows(table_rows)
    tmp.replace(table_out)
    return {
        "stem": stem,
        "pages": pages,
        "text_chars": text_chars,
        "tables": n_tables,
        "cells": n_cells,
        "numeric_cells": n_numeric,
        "seconds": round(time.time() - t0, 1),
        "errors": errors[:20],
        "text_file": str(text_out.relative_to(ROOT)),
        "table_file": str(table_out.relative_to(ROOT)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=max(1, min(4, os.cpu_count() or 1)))
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    TEXTDIR.mkdir(parents=True, exist_ok=True)
    TABLEDIR.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(QDIR.glob("*.pdf"))
    if args.limit:
        pdfs = pdfs[: args.limit]
    print(f"extracting {len(pdfs)} PDFs with {args.workers} workers", flush=True)
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(extract_one, p): p for p in pdfs}
        for i, fut in enumerate(as_completed(futs), 1):
            p = futs[fut]
            try:
                r = fut.result()
                results.append(r)
                print(
                    f"[{i}/{len(pdfs)}] {r['stem']}: {r['pages']}p, "
                    f"{r['text_chars']} chars, {r['tables']} tables, "
                    f"{r['numeric_cells']} numeric cells, {r['seconds']}s",
                    flush=True,
                )
                if r["errors"]:
                    print("   errors:", r["errors"][:3], flush=True)
            except Exception as exc:  # noqa: BLE001
                print(f"[{i}/{len(pdfs)}] {p.name} FAILED: {exc}", flush=True)

    with (ROOT / "data/company_docs/manifests/quarterly_extraction.json").open("w") as fh:
        json.dump(results, fh, indent=2)

    # Update manifest text_chars (and pages, in case pypdf mis-read).
    idx = {r["stem"]: r for r in results}
    with MANIFEST.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
        fields = rows[0].keys() if rows else []
    for row in rows:
        stem = Path(row["file"]).stem
        if stem in idx:
            row["text_chars"] = str(idx[stem]["text_chars"])
            row["pages"] = str(idx[stem]["pages"])
    tmp = MANIFEST.with_suffix(".csv.tmp")
    with tmp.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(fields))
        w.writeheader()
        w.writerows(rows)
    tmp.replace(MANIFEST)
    total_pages = sum(r["pages"] for r in results)
    total_chars = sum(r["text_chars"] for r in results)
    total_nums = sum(r["numeric_cells"] for r in results)
    print(f"done: {len(results)} PDFs, {total_pages} pages, {total_chars:,} chars, {total_nums:,} numeric cells", flush=True)
    bad = [r for r in results if r["pages"] < 5 or r["text_chars"] < 100]
    for r in bad:
        print("  LOW:", r["stem"], r["pages"], "pages", r["text_chars"], "chars", flush=True)


if __name__ == "__main__":
    main()
