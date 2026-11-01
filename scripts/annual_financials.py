#!/usr/bin/env python3
"""Build curated annual financial statements (FY2015-FY2025, plus clean earlier years).

Every value is traced to a statement row and PDF page. Monetary values are
normalised to RM million using the unit printed on the source page; EPS/DPS stay
in sen. Derived lines (EBITDA, total debt, net debt, totals summed from printed
subtotals) are flagged in `basis`.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STMT_DIR = ROOT / "data" / "company_docs" / "annual" / "statements"
TXT_DIR = ROOT / "data" / "company_docs" / "annual" / "text"
OUT = ROOT / "data" / "raw" / "financial_statements_annual.csv"
OUT.parent.mkdir(parents=True, exist_ok=True)

COMPANY = {"GENTING": "Genting Berhad", "GENM": "Genting Malaysia Berhad"}


def norm(s: str) -> str:
    s = (s or "").upper().replace("\u2019", "'").replace("\u2013", "-")
    s = re.sub(r"\s+", " ", s).strip(" :")
    # strip trailing note refs: "5, 8, 9 &", "3 & 4", "13", "5 &"
    s = re.sub(r"\s+(?:\d{1,2}[a-z]?\s*(?:[,&]\s*)?)+&?\s*$", "", s).strip()
    s = re.sub(r"\s*\*+\s*$", "", s)
    s = re.sub(r"\s+#\s*$", "", s)
    return s.strip(" :")


def find(rows, patterns, exclude=()):
    for pat in patterns:
        rx = re.compile(pat)
        for r in rows:
            lab = norm(r["label"])
            if not lab:
                continue
            if any(re.search(e, lab) for e in exclude):
                continue
            if rx.search(lab):
                return r
    return None


def num(r):
    if r is None:
        return None
    return r.get("value")


def add(*vals):
    if any(v is None for v in vals):
        return None
    return sum(vals)


def page_of(*rows):
    pages = []
    for r in rows:
        if r and r.get("_page") and r["_page"] not in pages:
            pages.append(r["_page"])
    return ";".join(str(p) for p in pages)


def _dps_candidate(ticker: str, report_year: int):
    path = TXT_DIR / f"{ticker}_AR_{report_year}.txt"
    if not path.exists():
        return None
    pages = path.read_text(encoding="utf-8", errors="replace").split("\f")
    best = None
    for pno, page in enumerate(pages, 1):
        for line in page.splitlines():
            u = line.upper().strip()
            if "DIVIDEND" not in u or "PER SHARE" not in u:
                continue
            if any(x in u for x in ("YIELD", "PAYOUT", "WOULD AMOUNT", "APPROVAL",
                                    "PAYABLE", "ENTITLED", "COMPRISED", "DECLARED",
                                    "BILLION", "MILLION", "REVENUE", "PROJECTED",
                                    "INTERIM DIVIDEND OF", "FINAL DIVIDEND OF")):
                continue
            if not re.match(r"^(?:NET |GROSS )?DIVIDENDS? PER SHARE", u):
                continue
            line2 = re.sub(r"(\d)\.\s+(\d)", r"\1.\2", line)
            nums = re.findall(r"\(?\d[\d,]*(?:\.\d+)?\)?", line2)
            vals = []
            for n in nums:
                try:
                    v = float(n.replace(",", "").strip("()"))
                except ValueError:
                    continue
                if -200 <= v <= 200:
                    vals.append(v)
            if not vals:
                continue
            score = 3 if len(vals) >= 4 else (2 if len(vals) >= 2 else 1)
            if "SEN" in u:
                score += 1
            cand = {"values": vals, "page": pno, "text": line.strip(),
                    "score": score, "report_year": report_year}
            if best is None or cand["score"] > best["score"]:
                best = cand
    return best


def dps_for_year(ticker: str, year: int):
    """Return (value, page, source_report_year, text) for a fiscal year.

    Prefer the report for that year; if its highlights line is absent, use the
    same line in a later report, where the year appears as a comparative column.
    """
    for report_year in range(year, min(year + 3, 2026)):
        cand = _dps_candidate(ticker, report_year)
        if not cand:
            continue
        idx = report_year - year
        if idx < len(cand["values"]):
            return cand["values"][idx], cand["page"], report_year, cand["text"]
    return None


MIN_YEAR = 2015


def extract_one(path: Path) -> list[dict]:
    d = json.loads(path.read_text(encoding="utf-8"))
    ticker, year = d["ticker"], int(d["year"])
    out: list[dict] = []
    if year < MIN_YEAR:
        return out

    def prior_lookup(kind, patterns, exclude=()):
        """Fallback: take the prior-year column of the following year's report."""
        nxt = STMT_DIR / f"{ticker}_AR_{year + 1}.json"
        if not nxt.exists():
            return None
        nd = json.loads(nxt.read_text(encoding="utf-8"))
        for p in nd["statements"].get(kind, []):
            for r in p["rows"]:
                if r.get("prior") is None:
                    continue
                lab = norm(r["label"])
                if any(re.search(e, lab) for e in exclude):
                    continue
                if any(re.search(pat, lab) for pat in patterns):
                    rr = dict(r)
                    rr["value"] = r["prior"]
                    rr["value_text"] = r.get("prior_text") or ""
                    rr["_page"] = p["page"]
                    rr["_unit"] = p.get("unit", "")
                    rr["_scale"] = p.get("scale", 1.0) or 1.0
                    rr["_source_pdf"] = f"{ticker}_AR_{year + 1}.pdf"
                    return rr
        return None

    def rows_for(kind):
        rows = []
        for p in d["statements"][kind]:
            scale = p.get("scale", 1.0) or 1.0
            for r in p["rows"]:
                r = dict(r)
                r["_page"] = p["page"]
                r["_unit"] = p.get("unit", "")
                r["_scale"] = scale
                rows.append(r)
        return rows

    inc = rows_for("income")
    bal = rows_for("balance")
    cfs = rows_for("cashflow")

    def emit(metric, statement, row, basis="reported", value=None, page=None,
             line_item=None, unit="RM million", source_text=None, source_pdf=None):
        if value is None and row is not None and row.get("value") is not None:
            value = row["value"] * row.get("_scale", 1.0)
        if value is None:
            return
        pages = str(page if page is not None else page_of(row))
        pdfs = (source_pdf
                or (row.get("_source_pdf") if row is not None else None)
                or f"{ticker}_AR_{year}.pdf")
        out.append({
            "company": COMPANY[ticker], "ticker": ticker, "fiscal_year": year,
            "statement": statement, "line_item": metric, "value": round(value, 4),
            "unit": unit,
            "page": pages.split(";")[0],
            "source_pages": pages,
            "source_pdf": pdfs.split(";")[0],
            "source_pdfs": pdfs,
            "basis": basis,
            "source_line_item": line_item if line_item is not None else (row["label"] if row else ""),
            "source_value_text": source_text if source_text is not None else (row["value_text"] if row else ""),
            "source_unit": row.get("_unit", "") if row else "",
        })

    # ---------- income statement ----------
    revenue = find(inc, [r"^(?:OPERATING )?REVENUE$", r"^TURNOVER$",
                         r"^REVENUE FROM (?:CONTINUING )?OPERATIONS$"])
    if revenue is None:
        revenue = prior_lookup("income", [r"^(?:OPERATING )?REVENUE$", r"^TURNOVER$"])
    emit("revenue", "income", revenue)

    pbt = find(inc, [r"^(?:PROFIT|LOSS)(?:/\(LOSS\))?(?:/\(PROFIT\))? BEFORE TAXATION$",
                     r"^\(LOSS\)/PROFIT BEFORE TAXATION$",
                     r"^LOSS BEFORE TAXATION$",
                     r"^PROFIT BEFORE TAX$",
                     r"^(?:PROFIT|LOSS) FROM ORDINARY ACTIVITIES BEFORE TAXATION$",
                     r"^PROFIT BEFORE SHARE IN RESULTS OF ASSOCIATED COMPAN"],
               exclude=[r"SHARE IN", r"MINORITY"])
    if pbt is None:
        pbt = prior_lookup("income", [r"BEFORE TAXATION$"], exclude=[r"SHARE IN", r"MINORITY"])
    emit("PBT", "income", pbt)

    net = find(inc, [r"^(?:NET )?(?:PROFIT|LOSS)(?:/\(LOSS\))?(?:/\(PROFIT\))? FOR THE (?:FINANCIAL )?YEAR$",
                     r"^\(LOSS\)/PROFIT FOR THE (?:FINANCIAL )?YEAR$",
                     r"^LOSS FOR THE (?:FINANCIAL )?YEAR$",
                     r"^PROFIT AFTER TAXATION$",
                     r"^NET PROFIT FOR THE (?:FINANCIAL )?YEAR$",
                     r"^(?:PROFIT|LOSS) FROM ORDINARY ACTIVITIES AFTER TAXATION$"],
               exclude=[r"CONTINUING", r"DISCONTINUED", r"ATTRIBUTABLE", r"COMPREHENSIVE"])
    if net is None:
        net = prior_lookup("income", [r"FOR THE (?:FINANCIAL )?YEAR$"],
                           exclude=[r"CONTINUING", r"DISCONTINUED", r"ATTRIBUTABLE",
                                    r"COMPREHENSIVE", r"BEFORE TAXATION"])
    emit("net_profit", "income", net)

    attr = find(inc, [r"^EQUITY HOLDERS OF THE COMPANY$",
                       r"^PROFIT(?:/\(LOSS\))? ATTRIBUTABLE TO SHAREHOLDERS$",
                       r"^ATTRIBUTABLE TO EQUITY HOLDERS OF THE COMPANY$",
                       r"^HOLDERS OF THE COMPANY$"],
                exclude=[r"PERPETUAL", r"TOTAL"])
    emit("net_profit_attributable", "income", attr)

    nci = find(inc, [r"^NON-CONTROLLING INTERESTS$", r"^MINORITY INTERESTS$",
                     r"^MINORITY SHAREHOLDERS' INTERESTS$", r"^MINORITYINTERESTS$"])
    emit("net_profit_nci", "income", nci)

    perp = find(inc, [r"^HOLDERS OF PERPETUAL CAPITAL SECURITIES.*$"],
                exclude=[r"^HOLDERS OF PERPETUAL CAPITAL SECURITIES OF A$"])
    emit("net_profit_perpetual", "income", perp)

    fin = find(inc, [r"^FINANCE COSTS?$", r"^INTEREST EXPENSE$"],
               exclude=[r"SUBSIDIAR", r"HOLDING", r"ASSOCIATE"])
    emit("finance_cost", "income", fin)

    eps = find(inc, [r"^BASIC EARNINGS(?:/\(LOSS\))? PER SHARE.*$",
                     r"^BASIC \(LOSS\)/EARNINGS PER SHARE.*$",
                     r"^BASIC LOSS PER SHARE.*$",
                     r"^BASIC \(SEN\)$", r"^EARNINGS PER SHARE$"])
    if eps is not None:
        emit("EPS", "income", eps, unit="sen")

    # ---------- balance sheet ----------
    ta = find(bal, [r"^TOTAL ASSETS$"])
    if ta is None:
        nca = find(bal, [r"^NON-CURRENT ASSETS$", r"^TOTAL NON-CURRENT ASSETS$"])
        ca = find(bal, [r"^CURRENT ASSETS$"])
        if nca and ca:
            emit("total_assets", "balance", None, basis="computed: non-current assets + current assets",
                 value=add(num(nca), num(ca)), page=page_of(nca, ca),
                 line_item="Non-current assets + Current assets")
        else:
            cap = find(bal, [r"^CAPITAL EMPLOYED$"])
            cl = find(bal, [r"^LESS:? CURRENT LIABILITIES$"])
            if cap and cl:
                emit("total_assets", "balance", None,
                     basis="computed: capital employed + current liabilities",
                     value=add(num(cap), num(cl)), page=page_of(cap, cl),
                     line_item="Capital employed + Current liabilities")
    else:
        emit("total_assets", "balance", ta)

    tl = find(bal, [r"^TOTAL LIABILITIES$"])
    if tl is None:
        ncl = find(bal, [r"^NON-CURRENT LIABILITIES$", r"^TOTAL NON-CURRENT LIABILITIES$",
                         r"^LONG TERM LIABILITIES$"])
        cl = find(bal, [r"^CURRENT LIABILITIES$", r"^LESS:? CURRENT LIABILITIES$"])
        if ncl and cl:
            emit("total_liabilities", "balance", None,
                 basis="computed: non-current liabilities + current liabilities",
                 value=add(num(ncl), num(cl)), page=page_of(ncl, cl),
                 line_item="Non-current liabilities + Current liabilities")
    else:
        emit("total_liabilities", "balance", tl)

    eq = find(bal, [r"^TOTAL EQUITY$", r"^SHAREHOLDERS' EQUITY$", r"^SHAREHOLDERS' FUNDS$"])
    if eq is None:
        shf = find(bal, [r"^SHAREHOLDERS' FUNDS$", r"^EQUITY ATTRIBUTABLE TO EQUITY HOLDERS OF THE COMPANY$",
                         r"^SHAREHOLDERS' EQUITY$"])
        mi = find(bal, [r"^MINORITY INTERESTS$", r"^NON-CONTROLLING INTERESTS$"])
        if shf and mi:
            emit("equity", "balance", None,
                 basis="computed: shareholders' equity + minority/non-controlling interests",
                 value=add(num(shf), num(mi)), page=page_of(shf, mi),
                 line_item="Shareholders' equity + Minority interests")
    else:
        emit("equity", "balance", eq)

    def value_of(patterns, exclude=()):
        r = find(bal, patterns, exclude)
        return (num(r), r)

    lt, lt_row = value_of([r"^LONG[ -]TERM BORROWINGS$", r"^LONG[ -]TERM LOANS$",
                            r"^LONG[ -]TERM LIABILITIES$"])
    st, st_row = value_of([r"^SHORT[ -]TERM BORROWINGS$", r"^SHORT[ -]TERM LOANS$",
                            r"^BANK BORROWINGS$"])
    total_borrow, tb_row = value_of([r"^TOTAL BORROWINGS$", r"^BORROWINGS$"])
    if total_borrow is not None:
        emit("total_debt", "balance", tb_row)
    elif lt is not None and st is not None:
        emit("total_debt", "balance", None,
             basis="computed: long-term borrowings + short-term borrowings (excludes lease liabilities)",
             value=lt + st, page=page_of(lt_row, st_row),
             line_item="Long-term borrowings + Short-term borrowings")
    elif lt is not None:
        emit("total_debt", "balance", None,
             basis="computed: long-term borrowings only (no short-term line found)",
             value=lt, page=page_of(lt_row), line_item="Long-term borrowings")

    cash, cash_row = value_of([r"^CASH AND CASH EQUIVALENTS$", r"^CASH AND BANK BALANCES$"])
    if cash is None:
        bank, bank_row = value_of([r"^BANK BALANCES AND DEPOSITS$"])
        sti, sti_row = value_of([r"^SHORT[ -]TERM INVESTMENTS$"])
        if bank is not None and sti is not None:
            emit("cash", "balance", None,
                 basis="computed: bank balances and deposits + short-term investments",
                 value=bank + sti, page=page_of(bank_row, sti_row),
                 line_item="Bank balances and deposits + Short-term investments")
            cash = bank + sti
            cash_page = page_of(bank_row, sti_row)
        elif bank is not None:
            emit("cash", "balance", bank_row)
            cash = bank
            cash_page = page_of(bank_row)
    else:
        emit("cash", "balance", cash_row)
        cash_page = page_of(cash_row)

    # debt incl leases (extra)
    lease, lease_row = value_of([r"^LEASE LIABILITIES$"])
    td = None
    for r in out:
        if r["line_item"] == "total_debt":
            td = r["value"]
    if td is not None and lease is not None:
        emit("total_debt_incl_leases", "balance", None,
             basis="computed: total_debt + lease liabilities",
             value=td + lease, page=page_of(lease_row), line_item="Total debt + Lease liabilities")

    if td is not None and cash is not None:
        emit("net_debt", "balance", None,
             basis="computed: total debt (excluding leases) - cash and cash equivalents",
             value=td - cash, page=f"{page_of(tb_row or lt_row or st_row)};{cash_page}",
             line_item="Total debt - Cash and cash equivalents")

    # ---------- cash flow ----------
    ocf = find(cfs, [r"^NET CASH (?:FLOW |FLOWS )?(?:GENERATED FROM|FROM|INFLOW FROM|USED IN) OPERATING ACTIVITIES$",
                     r"^NET CASH FROM/\(USED IN\) OPERATING ACTIVITIES$",
                     r"^NET CASH FLOW FROM/\(USED IN\) OPERATING ACTIVITIES$",
                     r"^NET CASH (?:FLOW |FLOWS )?\(USED IN\)/FROM OPERATING ACTIVITIES$"],
              exclude=[r"FINANCING", r"INVESTING"])
    if ocf is None:
        ocf = find(cfs, [r"^NET CASH .*OPERATING ACTIVITIES$"],
                   exclude=[r"FINANCING", r"INVESTING", r"CASH FLOWS FROM"])
    emit("operating_cash_flow", "cashflow", ocf)

    capex = find(cfs, [r"^PURCHASE OF PROPERTY, PLANT AND EQUIPMENT(?: \(PPE\)|\ \(\"PPE\"\))?$",
                       r"^PURCHASE OF PPE$",
                       r"^PURCHASE OF FIXED ASSETS$",
                       r"^ACQUISITION OF PROPERTY, PLANT AND EQUIPMENT$",
                       r"^ADDITIONS? TO PROPERTY, PLANT AND EQUIPMENT$",
                       r"^PURCHASE OF/ADDITIONS? TO PROPERTY, PLANT AND EQUIPMENT$",
                       r"^PROPERTY, PLANT AND EQUIPMENT$"],
                  exclude=[r"PROCEEDS", r"DISPOSAL", r"WRITTEN"])
    emit("capex", "cashflow", capex)

    dep = find(cfs, [r"^DEPRECIATION AND AMORTISATION$", r"^DEPRECIATION AND AMORTISATION EXPENSES?$",
                     r"^DEPRECIATION, AMORTISATION AND IMPAIRMENT$"])
    if dep is not None:
        da = num(dep)
        dep_page = page_of(dep)
        dep_basis = "reported: depreciation and amortisation"
    else:
        parts = []
        for pat in [r"^DEPRECIATION OF PROPERTY, PLANT AND EQUIPMENT.*$",
                    r"^DEPRECIATION OF PPE$", r"^DEPRECIATION OF FIXED ASSETS$",
                    r"^DEPRECIATION OF INVESTMENT PROPERT(?:Y|IES)$",
                    r"^DEPRECIATION OF LEASEHOLD LAND USE RIGHTS$",
                    r"^AMORTISATION OF .*$"]:
            rr = find(cfs, [pat])
            if rr and rr not in parts:
                parts.append(rr)
        if parts:
            da = sum(num(r) for r in parts)
            dep_page = page_of(*parts)
            dep_basis = "computed: sum of depreciation/amortisation lines"
        else:
            da = None
            dep_page = ""
            dep_basis = ""
    if da is not None:
        emit("depreciation_amortisation", "cashflow", None, basis=dep_basis,
             value=da, page=dep_page,
             line_item="Depreciation and amortisation")

    # EBITDA = PBT + finance cost + D&A (finance cost sign normalised)
    if pbt is not None and fin is not None and da is not None:
        ebitda = num(pbt) + abs(num(fin)) + abs(da)
        src = []
        for rr in (pbt, fin, dep):
            s = (rr or {}).get("_source_pdf") if rr is not None else None
            src.append(s or f"{ticker}_AR_{year}.pdf")
        src_pdf = ";".join(dict.fromkeys(src))
        emit("EBITDA", "income", None,
             basis="computed: PBT + finance cost + depreciation & amortisation",
             value=ebitda, page=f"{page_of(pbt)};{page_of(fin)};{dep_page}",
             line_item="PBT + Finance cost + D&A", source_pdf=src_pdf)

    dst = dps_for_year(ticker, year)
    if dst:
        val, pg, src_year, txt = dst
        emit("DPS", "income", None, basis="reported: net dividend per share line (financial highlights)",
             value=val, page=pg, line_item="Net dividend per share (sen)",
             unit="sen", source_text=txt[:300],
             source_pdf=f"{ticker}_AR_{src_year}.pdf")
    return out


def main() -> int:
    files = sorted(STMT_DIR.glob("*_AR_*.json"))
    records = []
    for f in files:
        try:
            records.extend(extract_one(f))
        except Exception as exc:  # noqa: BLE001
            print(f"FAILED {f.name}: {exc}")
    fields = ["company", "ticker", "fiscal_year", "statement", "line_item", "value",
              "unit", "page", "source_pages", "source_pdf", "source_pdfs", "basis",
              "source_line_item", "source_value_text", "source_unit"]
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in records:
            w.writerow(r)
    print(f"wrote {len(records)} rows to {OUT}")
    # coverage summary
    from collections import Counter
    c = Counter((r["ticker"], r["line_item"]) for r in records)
    metrics = ["revenue", "EBITDA", "PBT", "net_profit", "net_profit_attributable",
               "finance_cost", "total_assets", "total_liabilities", "equity",
               "total_debt", "cash", "net_debt", "EPS", "DPS",
               "operating_cash_flow", "capex"]
    for m in metrics:
        print(f"{m:28s} GENTING {c[('GENTING',m)]:2d}  GENM {c[('GENM',m)]:2d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
