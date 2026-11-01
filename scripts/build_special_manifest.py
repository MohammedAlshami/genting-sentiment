#!/usr/bin/env python3
"""Build data/company_docs/manifests/special_documents.csv.

The PDFs are copied from the announcement attachments into a small, clearly
named special-documents tree.  Credit-rating pages are stored as HTML + text.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPECIAL = ROOT / "data" / "company_docs" / "special"
MAN = ROOT / "data" / "company_docs" / "manifests" / "special_documents.csv"

ROWS = [
    {
        "doc_type": "takeover_offer_document",
        "ticker": "GENTING",
        "date": "2025-11-03",
        "title": "Conditional voluntary take-over offer by Genting Berhad for the remaining shares of Genting Malaysia Berhad — Offer Document",
        "source_url": "https://www.bursamalaysia.com/market_information/announcements/company_announcement/announcement_details?ann_id=3604999",
        "file": "data/company_docs/special/takeover/GENM_takeover_offer_document_2025-11-03.pdf",
        "notes": "65-page offer document; GENM privatisation/consolidation exercise.",
    },
    {
        "doc_type": "takeover_notice",
        "ticker": "GENTING",
        "date": "2025-10-13",
        "title": "Notice of conditional voluntary take-over offer",
        "source_url": "https://www.bursamalaysia.com/market_information/announcements/company_announcement/announcement_details?ann_id=3598505",
        "file": "data/company_docs/special/takeover/GENM_notice_of_conditional_voluntary_takeover_2025-10-13.pdf",
        "notes": "Notice to GENM shareholders.",
    },
    {
        "doc_type": "takeover_notice",
        "ticker": "GENM",
        "date": "2025-11-17",
        "title": "Notice to the shareholders of Genting Malaysia Berhad in relation to the unconditional take-over offer by Genting Berhad",
        "source_url": "https://www.bursamalaysia.com/market_information/announcements/company_announcement/announcement_details?ann_id=3608590",
        "file": "data/company_docs/special/takeover/GENM_notice_to_shareholders_takeover_2025-11-17.pdf",
        "notes": "Notice of VGO-to-MGO and extension of closing date.",
    },
    {
        "doc_type": "rights_issue_announcement",
        "ticker": "GENTING",
        "date": "2026-10-09",
        "title": "Proposed renounceable rights issue of new ordinary shares in GENT to raise gross proceeds of approximately RM1,250 million",
        "source_url": "https://www.bursamalaysia.com/market_information/announcements/company_announcement/announcement_details?ann_id=3713808",
        "file": "data/company_docs/special/rights_issue/GENTING_rights_issue_announcement_2026-10-09.pdf",
        "notes": "22-page announcement. The formal circular/prospectus had not been published by 2 Nov 2026; completion targeted 1Q2027.",
    },
    {
        "doc_type": "agm_circular",
        "ticker": "GENTING",
        "date": "2026-04-17",
        "title": "Circular to shareholders: proposed renewal of share buy-back authority and shareholders' mandate",
        "source_url": "https://www.bursamalaysia.com/market_information/announcements/company_announcement/announcement_details?ann_id=3655946",
        "file": "data/company_docs/special/agm_egm/GENTING_circular_share_buyback_2026-04-17.pdf",
        "notes": "24 pages.",
    },
    {
        "doc_type": "agm_circular",
        "ticker": "GENTING",
        "date": "2025-04-25",
        "title": "Circular to shareholders: proposed renewal of share buy-back authority and shareholders' mandate",
        "source_url": "https://www.bursamalaysia.com/market_information/announcements/company_announcement/announcement_details?ann_id=3547194",
        "file": "data/company_docs/special/agm_egm/GENTING_circular_share_buyback_2025-04-25.pdf",
        "notes": "",
    },
    {
        "doc_type": "agm_circular",
        "ticker": "GENM",
        "date": "2025-04-11",
        "title": "GENM circular to shareholders: proposed renewal of share buy-back authority and shareholders' mandate",
        "source_url": "https://www.bursamalaysia.com/market_information/announcements/company_announcement/announcement_details?ann_id=3542729",
        "file": "data/company_docs/special/agm_egm/GENM_circular_share_buyback_2025-04-11.pdf",
        "notes": "",
    },
    {
        "doc_type": "agm_notice",
        "ticker": "GENM",
        "date": "2025-04-11",
        "title": "Notice of 45th Annual General Meeting, proxy form and personal data notice",
        "source_url": "https://www.bursamalaysia.com/market_information/announcements/company_announcement/announcement_details?ann_id=3542611",
        "file": "data/company_docs/special/agm_egm/GENM_AGM_notice_2025-04-11.pdf",
        "notes": "",
    },
    {
        "doc_type": "agm_circular",
        "ticker": "GENM",
        "date": "2026-04-16",
        "title": "GENM circular to shareholders: proposed renewal of share buy-back authority and shareholders' mandate",
        "source_url": "https://www.bursamalaysia.com/market_information/announcements/company_announcement/announcement_details?ann_id=3655404",
        "file": "data/company_docs/special/agm_egm/GENM_circular_share_buyback_2026-04-16.pdf",
        "notes": "",
    },
    {
        "doc_type": "agm_notice",
        "ticker": "GENM",
        "date": "2026-04-16",
        "title": "Notice of 46th Annual General Meeting, proxy form and personal data notice",
        "source_url": "https://www.bursamalaysia.com/market_information/announcements/company_announcement/announcement_details?ann_id=3655355",
        "file": "data/company_docs/special/agm_egm/GENM_AGM_notice_2026-04-16.pdf",
        "notes": "",
    },
    {
        "doc_type": "agm_notice",
        "ticker": "GENTING",
        "date": "2026-04-17",
        "title": "Notice of 58th Annual General Meeting, proxy form and personal data notice",
        "source_url": "https://www.bursamalaysia.com/market_information/announcements/company_announcement/announcement_details?ann_id=3655791",
        "file": "data/company_docs/special/agm_egm/GENTING_AGM_notice_2026-04-17.pdf",
        "notes": "10 pages.",
    },
    {
        "doc_type": "mtn_programme",
        "ticker": "GENTING",
        "date": "2025-12-05",
        "title": "Unrated Medium Term Notes Programme of RM5.0 billion by Genting Vista Berhad",
        "source_url": "https://www.bursamalaysia.com/market_information/announcements/company_announcement/announcement_details?ann_id=3616383",
        "file": "data/company_docs/special/mtn/GENTING_RM5bn_MTN_programme_Genting_Vista_2025-12-05.pdf",
        "notes": "4-page programme announcement. A separate RM10.0 billion Genting RMTN Berhad programme was also announced; see announcements JSONL.",
    },
    {
        "doc_type": "credit_rating",
        "ticker": "GENTING/GENM",
        "date": "2025-12-12",
        "title": "RAM Ratings: Outlook on Genting Group revised to negative; AA1 long-term ratings maintained",
        "source_url": "https://www.ram.com.my/pressrelease?prviewid=7152",
        "file": "data/company_docs/special/credit_ratings/RAM_2026_outlook_negative.txt",
        "notes": "Full public press release text; HTML also saved.",
    },
    {
        "doc_type": "credit_rating",
        "ticker": "GENTING",
        "date": "2026-09-07",
        "title": "Fitch downgrades Genting Berhad to BBB-; RWLV to BB+; outlooks stable",
        "source_url": "https://www.fitchratings.com/research/corporate-finance/fitch-downgrades-genting-berhad-to-bbb-resorts-world-las-vegas-to-bb-outlooks-stable-07-09-2026",
        "file": "data/company_docs/special/credit_ratings/Fitch_2026-09-07_downgrade_BBB-.html",
        "notes": "Public rating-action page; article body is JS/paywalled. HTML retained; key facts in credit_ratings/README.md.",
    },
    {
        "doc_type": "credit_rating_notes",
        "ticker": "GENTING/GENM",
        "date": "2026-11-02",
        "title": "Collector notes on public credit-rating material and paywall limits",
        "source_url": "https://www.ram.com.my/pressrelease?prviewid=7152",
        "file": "data/company_docs/special/credit_ratings/README.md",
        "notes": "Explains which rating-agency bodies are public, JS-rendered or paywalled.",
    },
    {
        "doc_type": "bond_list",
        "ticker": "GENTING",
        "date": "2026-11-02",
        "title": "Genting Berhad ratings and bonds page (outstanding bonds, coupons, maturities, RAM AA1)",
        "source_url": "https://www.genting.com/ratings-bonds",
        "file": "data/company_docs/special/credit_ratings/Genting_ratings_bonds_page.txt",
        "notes": "Company-published bond list; HTML also saved.",
    },
    {
        "doc_type": "credit_rating",
        "ticker": "GENTING",
        "date": "2026-10-01",
        "title": "S&P Global Ratings: Research Update: Genting Group Companies Outlook Revised To Negative",
        "source_url": "https://www.spglobal.com/ratings/en/regulatory/article/-/view/sourceId/101662684",
        "file": "data/company_docs/special/credit_ratings/SP_Global_2026_research_update.html",
        "notes": "Public page; body is JS-rendered. HTML retained.",
    },
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pages(path: Path) -> int | str:
    if path.suffix.lower() != ".pdf":
        return ""
    try:
        from pypdf import PdfReader
        return len(PdfReader(str(path)).pages)
    except Exception:  # noqa: BLE001
        return ""


def main():
    out = []
    for r in ROWS:
        p = ROOT / r["file"]
        if not p.exists():
            r["bytes"] = 0
            r["sha256"] = ""
            r["pages"] = ""
            r["status"] = "missing"
        else:
            r["bytes"] = p.stat().st_size
            r["sha256"] = sha256(p)
            r["pages"] = pages(p)
            r["status"] = "ok"
        out.append(r)
    fields = ["doc_type", "ticker", "date", "title", "source_url", "file", "bytes",
              "sha256", "pages", "status", "notes"]
    with MAN.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(out)
    print(f"wrote {MAN} ({len(out)} rows)")


if __name__ == "__main__":
    main()
