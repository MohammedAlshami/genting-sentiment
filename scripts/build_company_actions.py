#!/usr/bin/env python3
"""Build data/raw/company_actions.jsonl from the collected Bursa announcements.

Every record is transcribed from an announcement body or its attached PDF; the
source_url points at the KLSE Screener mirror page (the PDF itself is linked
there and stored under data/company_docs/announcements/).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "company_actions.jsonl"
BASE = "https://www.klsescreener.com/v2/announcements/view/"

FIELDS = [
    "company", "action_type", "announcement_date", "effective_date", "status", "title",
    "terms", "amount_rm", "amount_usd", "per_share_sen", "price_per_share_rm",
    "ratio", "subscription_price_rm", "dilution_pct", "proceeds_use", "counterparty",
    "stake_before_pct", "stake_after_pct", "source_url", "source_title", "notes",
]


def rec(company, action_type, date, title, nid, **kw):
    r = {k: None for k in FIELDS}
    r.update({
        "company": company,
        "action_type": action_type,
        "announcement_date": date,
        "title": title,
        "source_url": BASE + nid,
        "source_title": title,
    })
    r.update(kw)
    return r


def main() -> int:
    rows = [
        # ---------------- GENTING: dividends ----------------
        rec("GENTING", "dividend", "2025-02-27",
            "Final Single-Tier Dividend of 5.0 sen per ordinary share", "9161089",
            effective_date="2025-04-16", status="paid",
            terms="Final single-tier dividend of 5.0 sen per ordinary share for FY2024; ex-date 14 Mar 2025, payment 16 Apr 2025.",
            per_share_sen=5.0,
            notes="Declared with 4Q24 results. Book closure notice 9161883."),
        rec("GENTING", "dividend", "2026-02-26",
            "Final Single-Tier Dividend of 5.0 sen per ordinary share", "11181555",
            effective_date="2026-04-17", status="paid",
            terms="Final single-tier dividend of 5.0 sen per ordinary share for FY2025; ex-date 17 Mar 2026, payment 17 Apr 2026.",
            per_share_sen=5.0,
            notes="Declared with 4Q25 results. Book closure notice 11181777."),

        # ---------------- GENTING: buy-back authority ----------------
        rec("GENTING", "buyback_mandate", "2025-04-25",
            "Proposed renewal of share buy-back authority", "9562009",
            effective_date="2025-06-12", status="approved",
            terms="Renewal of the authority for the Company to purchase its own shares, tabled at the 57th AGM.",
            notes="Approved with all 8 resolutions at the 57th AGM on 12 Jun 2025 (outcome 9788741). No GENT buy-backs were announced in the window."),
        rec("GENTING", "buyback_mandate", "2026-04-17",
            "Proposed renewal of share buy-back authority", "11547909",
            effective_date="2026-06-11", status="approved",
            terms="Renewal of the share buy-back authority, tabled at the 58th AGM.",
            notes="Approved with all 8 resolutions at the 58th AGM on 11 Jun 2026 (outcome 11612349)."),

        # ---------------- GENTING: AGMs ----------------
        rec("GENTING", "agm", "2025-04-25", "Fifty-Seventh Annual General Meeting", "9561345",
            effective_date="2025-06-12", status="held",
            terms="57th AGM held 12 Jun 2025; all 8 ordinary resolutions approved by poll.",
            source_title="Notice of 57th AGM; outcome announcement 9788741."),
        rec("GENTING", "agm", "2026-04-17", "Fifty-Eighth Annual General Meeting", "11546841",
            effective_date="2026-06-11", status="held",
            terms="58th AGM held 11 Jun 2026; all 8 ordinary resolutions approved by poll.",
            source_title="Notice of 58th AGM; outcome announcement 11612349."),

        # ---------------- GENTING: GENM take-over ----------------
        rec("GENTING", "takeover_offer", "2025-10-13",
            "Conditional voluntary take-over offer for Genting Malaysia Berhad", "10518319",
            effective_date="2025-12-01", status="completed",
            terms=("Cash offer of RM2.35 per GENM share for all 2,870,039,874 GENM shares "
                   "(50.64% of GENM excluding treasury shares) not already held by GENT. "
                   "Conditional on GENT and persons acting in concert holding >50% of GENM. "
                   "First closing date 24 Nov 2025; extended to 1 Dec 2025."),
            price_per_share_rm=2.35, stake_before_pct=49.36, stake_after_pct=73.13,
            counterparty="Genting Malaysia Berhad (4715)",
            notes=("Became unconditional on 3 Nov 2025 after open-market purchases took GENT's "
                   "holding above 50%. At close on 1 Dec 2025 GENT held 4,144,966,481 GENM "
                   "shares = 73.13%. Post-offer purchases raised the stake to 73.798% by "
                   "4 Dec 2025 and 73.867% by 2 Apr 2026 (last SSH notice 11371165).")),
        rec("GENM", "takeover_offer", "2025-10-13",
            "Receipt of notice of conditional voluntary take-over offer from Genting Berhad", "10518317",
            effective_date="2025-12-01", status="completed",
            terms="GENT offered RM2.35 cash per GENM share for all shares not already held.",
            price_per_share_rm=2.35, stake_before_pct=49.36, stake_after_pct=73.13,
            counterparty="Genting Berhad (3182)",
            notes="GENM board appointed an independent adviser; IAC issued 13 Nov 2025 (10694735). Offer closed 1 Dec 2025."),
        rec("GENM", "independent_advice", "2025-11-13",
            "Independent Advice Circular on the unconditional voluntary take-over offer", "10694735",
            status="issued",
            terms="Independent adviser's opinion on the fairness and reasonableness of the RM2.35 offer.",
            counterparty="Genting Berhad (3182)",
            notes="Circular PDF stored at data/company_docs/announcements/2025-11-13_10694735_1_Genting_Malaysia_Berhad_IAC.pdf."),
        rec("GENM", "stake_increase", "2025-12-04",
            "Genting Berhad raises stake in GENM to 73.798%", "10737261",
            effective_date="2025-12-03", status="completed",
            terms=("Post-offer open-market purchases and take-over acceptances: 24,412,000 shares "
                   "acquired on 2 Dec 2025, 2,000,000 on 3 Dec 2025 and 11,322,372 shares via "
                   "take-over acceptance on 3 Dec 2025."),
            stake_before_pct=73.133, stake_after_pct=73.798,
            counterparty="Genting Berhad (3182)",
            notes=("SSH notice by GENT. Further purchases took the stake to 73.834% (5 Dec 2025), "
                   "73.838% (13 Mar 2026), 73.849% (27 Mar 2026) and 73.867% (2 Apr 2026, "
                   "announcement 11371165). GENM IAR2025 states GENT owned 73.84% at 16 Mar 2026.")),

        # ---------------- GENTING: MTNs / bonds ----------------
        rec("GENTING", "mtn_issuance", "2025-11-10",
            "Genting RMTN issues RM900 million MTNs (Tranche 5)", "10681211",
            effective_date="2025-11-10", status="issued",
            terms="RM900m nominal, issued at par, 1-year tenure, 1-month KLIBOR + 1.80% p.a.",
            amount_rm=900_000_000,
            proceeds_use="Part-finance the acquisition of GENM shares under the take-over offer.",
            notes="Issued by Genting RMTN, a wholly-owned subsidiary, under the existing MTN Programme."),
        rec("GENTING", "mtn_issuance", "2025-11-20",
            "Genting RMTN issues RM495 million MTNs (Tranche 6)", "10707633",
            effective_date="2025-11-20", status="issued",
            terms="RM495m nominal, issued at par, 1-year tenure, 1-month KLIBOR + 1.80% p.a.",
            amount_rm=495_000_000,
            proceeds_use="Part-finance the acquisition of GENM shares under the take-over offer."),
        rec("GENTING", "mtn_issuance", "2025-11-27",
            "Genting RMTN issues RM255 million MTNs (Tranche 7)", "10724501",
            effective_date="2025-11-27", status="issued",
            terms="RM255m nominal, issued at par, 1-year tenure, 1-month KLIBOR + 1.80% p.a.",
            amount_rm=255_000_000,
            proceeds_use="Part-finance the acquisition of GENM shares under the take-over offer."),
        rec("GENTING", "mtn_issuance", "2025-12-05",
            "Genting RMTN issues RM1,350 million MTNs (Tranche 8)", "10742285",
            effective_date="2025-12-05", status="issued",
            terms="RM1,350m nominal, issued at par, 1-year tenure, 1-month KLIBOR + 1.80% p.a.",
            amount_rm=1_350_000_000,
            proceeds_use="Part-finance the acquisition of GENM shares under the take-over offer (closed 1 Dec 2025)."),
        rec("GENTING", "mtn_programme", "2025-12-05",
            "Genting Vista establishes RM5.0 billion unrated MTN programme", "10742301",
            effective_date="2025-12-05", status="established",
            terms="RM5.0b nominal unrated MTN programme lodged with the SC under the Lodge and Launch Framework; irrevocably and unconditionally guaranteed by GENT.",
            amount_rm=5_000_000_000,
            notes="Issuer: Genting Vista Berhad, a wholly-owned subsidiary of GENT."),
        rec("GENTING", "mtn_issuance", "2025-12-30",
            "Genting Vista issues RM3.0 billion Series 1 MTN", "10858417",
            effective_date="2025-12-30", status="issued",
            terms="RM3.0b nominal, issued at par, tenure 1 to 5 years, 3-month KLIBOR + 1.80% p.a.",
            amount_rm=3_000_000_000,
            proceeds_use="Redeem the Genting RMTN MTNs used to part-finance the GENM shares acquired under the take-over offer.",
            notes="First issuance under the RM5.0b Genting Vista unrated MTN programme."),
        rec("GENTING", "mtn_redemption", "2025-12-30",
            "Genting RMTN MTNs to be redeemed with Genting Vista Series 1 proceeds", "10858417",
            status="announced",
            terms="The RM3.0b proceeds of the Series 1 MTN are to redeem the Genting RMTN MTNs (tranches 5-8: RM900m + RM495m + RM255m + RM1,350m = RM3.0b).",
            amount_rm=3_000_000_000,
            notes="Redemption is the stated use of proceeds; the exact settlement date is not in the announcement."),
        rec("GENTING", "bond_tender_offer", "2026-04-20",
            "Conditional tender offer for GOHL Capital US$1.5 billion 4.25% notes due 2027", "11549731",
            effective_date="2026-05-04", status="completed",
            terms=("Tender offer by GOHL Capital Limited for its outstanding US$1,500,000,000 "
                   "4.25% guaranteed notes due 2027; maximum purchase amount set at "
                   "US$1,250,000,000 on 23 Apr 2026. US$882,462,000 validly tendered and "
                   "accepted; settlement 4 May 2026; US$617,538,000 remains outstanding."),
            amount_usd=882_462_000,
            proceeds_use="Refinancing to extend the GENT group's debt maturity profile.",
            notes="Notes listed on HKEX. Results announcement 11568689; settlement 11572519."),
        rec("GENTING", "perpetual_securities", "2026-04-23",
            "GOHL Capital Holdings prices US$ subordinated perpetual securities", "11554255",
            effective_date="2026-04-29", status="issued",
            terms=("Subordinated perpetual capital securities, Series 1 perpetual non-call 5.5 "
                   "(first call 29 Oct 2031) and Series 2 perpetual non-call 10 (first call "
                   "29 Apr 2036); fixed rate to first reset, then resets every 5 years; "
                   "25bp step-up at year 10.5/10 and further 75bp at year 25.5/30; "
                   "distributions deferrable and cumulative."),
            proceeds_use="Repay GOHL Capital Limited's US$1.5b notes due Jan 2027 and other refinancing.",
            notes=("Issued by GOHL Capital Holdings Limited, guaranteed subordinated by Genting "
                   "Overseas Holdings Limited, with a subordinated keepwell deed from GENT. "
                   "Listed on SGX-ST 30 Apr 2026. Principal amount not stated in the Bursa "
                   "announcement; do not infer.")),
        rec("GENTING", "credit_rating", "2026-04-23",
            "Ratings assigned to the new subordinated perpetual securities", "11554255",
            status="assigned",
            terms="Moody's Investors Service assigned Ba2; Fitch Ratings assigned BB+ to the Series 1 and Series 2 securities.",
            notes="Instrument ratings, not corporate ratings."),

        # ---------------- GENTING: rights issue ----------------
        rec("GENTING", "rights_issue", "2026-10-09",
            "Proposed renounceable rights issue to raise approximately RM1,250 million", "11682541",
            status="proposed",
            terms=("Renounceable rights issue of new GENT ordinary shares on a full-subscription "
                   "basis to raise gross proceeds of approximately RM1,250m. Issue price and "
                   "entitlement basis not fixed at announcement; Board intends a 25%-30% "
                   "discount to TERP based on the 5-day VWAP before the price-fixing date. "
                   "KHR, KHIL and DILKH irrevocably undertake to subscribe in full for their "
                   "entitlements (45.10% of shares in issue). Remaining open portion to be underwritten."),
            amount_rm=1_250_000_000,
            proceeds_use=("Repayment of borrowings RM800.0m; working capital RM429.5m "
                          "(interest/financing costs RM280.0m + general working capital RM149.5m); "
                          "transaction expenses RM20.5m. All within 12 months of listing (expenses 2 months)."),
            notes=("Based on 3,850,576,099 shares in issue excluding 26,320,000 treasury shares "
                   "at 6 Oct 2026. Expected completion 1Q2027. No subscription price, entitlement "
                   "ratio or dilution percentage was announced by 2 Nov 2026.")),
        rec("GENTING", "rights_issue", "2026-10-14",
            "Reply to Bursa query on the proposed rights issue", "11684683",
            status="proposed",
            terms="Additional information on the 25%-30% TERP discount and the breakdown of the RM429.5m working-capital allocation.",
            amount_rm=1_250_000_000,
            notes="Confirms working capital split: RM280.0m interest/financing costs, RM149.5m general working capital."),
        rec("GENTING", "rights_issue", "2026-10-23",
            "Listing application submitted for the rights shares", "11690197",
            status="pending_listing",
            terms="Application for listing and quotation of the rights shares submitted to Bursa Securities.",
            amount_rm=1_250_000_000,
            notes="Still pending as at 2 Nov 2026."),

        # ---------------- GENM: dividends ----------------
        rec("GENM", "dividend", "2025-02-27",
            "Final Single-Tier Dividend of 4.0 sen per ordinary share", "9161199",
            effective_date="2025-04-10", status="paid",
            terms="Final single-tier dividend of 4.0 sen per ordinary share for FY2024; ex-date 14 Mar 2025, payment 10 Apr 2025.",
            per_share_sen=4.0,
            notes="Declared with 4Q24 results. Book closure notice 9161965."),
        rec("GENM", "dividend", "2026-02-26",
            "Final Single-Tier Dividend of 7.0 sen per ordinary share", "11181513",
            effective_date="2026-04-10", status="paid",
            terms="Final single-tier dividend of 7.0 sen per ordinary share for FY2025; ex-date 13 Mar 2026, payment 10 Apr 2026.",
            per_share_sen=7.0,
            notes="Declared with 4Q25 results. Book closure notice 11181783."),

        # ---------------- GENM: buy-backs / AGMs ----------------
        rec("GENM", "buyback_mandate", "2025-04-11",
            "Proposed renewal of share buy-back authority", "9433665",
            effective_date="2025-06-11", status="approved",
            terms="Renewal of the share buy-back authority, tabled at the 45th AGM.",
            notes="Approved with all 9 ordinary resolutions at the 45th AGM on 11 Jun 2025 (outcome 9784091)."),
        rec("GENM", "buyback_mandate", "2026-04-16",
            "Proposed renewal of share buy-back authority", "11537975",
            effective_date="2026-06-10", status="approved",
            terms="Renewal of the share buy-back authority, tabled at the 46th AGM.",
            notes="Approved with all 8 ordinary resolutions at the 46th AGM on 10 Jun 2026 (outcome 11611215)."),
        rec("GENM", "agm", "2025-04-11", "Forty-Fifth Annual General Meeting", "9426719",
            effective_date="2025-06-11", status="held",
            terms="45th AGM held 11 Jun 2025; 9 ordinary resolutions approved.",
            source_title="Notice of 45th AGM; outcome announcement 9784091."),
        rec("GENM", "agm", "2026-04-16", "Forty-Sixth Annual General Meeting", "11534697",
            effective_date="2026-06-10", status="held",
            terms="46th AGM held 10 Jun 2026; all 8 ordinary resolutions approved.",
            source_title="Notice of 46th AGM; outcome announcement 11611215."),
        rec("GENM", "buyback", "2026-09-17",
            "Share buy-back: 200,000 shares at RM1.50", "11669007",
            effective_date="2026-09-17", status="completed",
            terms="200,000 ordinary shares bought back at RM1.500 each; total consideration RM300,630.00; retained as treasury.",
            amount_rm=300_630.00, price_per_share_rm=1.50,
            notes="Cumulative treasury after buy-back: 270,502,915 shares (4.55542% of issued shares)."),
        rec("GENM", "buyback", "2026-10-12",
            "Share buy-back: 550,000 shares at RM1.26-1.27", "11683189",
            effective_date="2026-10-12", status="completed",
            terms="550,000 ordinary shares bought back at RM1.260-1.270 each; total consideration RM699,465.30; retained as treasury.",
            amount_rm=699_465.30,
            notes="Cumulative treasury after buy-back: 271,052,915 shares (4.56468% of issued shares)."),

        rec("GENM", "stake_increase", "2026-04-02",
            "Genting Berhad stake in GENM reaches 73.867%", "11371165",
            effective_date="2026-04-02", status="completed",
            terms="Further open-market purchases by GENT; latest substantial-shareholder notice in the window.",
            stake_before_pct=73.849, stake_after_pct=73.867,
            counterparty="Genting Berhad (3182)",
            notes=("GENT held 4,186,582,953 GENM shares after the change. Intermediate steps: "
                   "73.834% (5 Dec 2025), 73.838% (13 Mar 2026), 73.849% (27 Mar 2026). "
                   "GENM IAR2025 states 73.84% at 16 Mar 2026.")),
        rec("GENM", "litigation", "2024-11-25",
            "RAV Bahamas litigation against Genting Americas Inc.", "8510103",
            status="ongoing",
            terms=("RAV Bahamas Ltd filed a complaint in the US District Court, Southern "
                   "District of Florida against Genting Americas Inc. (indirect wholly-owned "
                   "GENM subsidiary). GAI filed a motion to dismiss on 22 Nov 2024; the court "
                   "granted dismissal of the complaint in its current form on 1 Jul 2025; RAV "
                   "filed an amended complaint on 29 Jul 2025; GAI moved to dismiss the amended "
                   "complaint on 12 Sep 2025."),
            notes="Updates: 25 Nov 2024 (8510103), 7 Jul 2025 (9926289), 17 Sep 2025 (10372693). No amount claimed or provision disclosed in the announcements."),
        # ---------------- GENM: MTN / acquisition ----------------
        rec("GENM", "mtn_issuance", "2024-12-05",
            "GENM Capital issues RM75 million MTNs", "8552587",
            effective_date="2024-12-05", status="issued",
            terms="RM75m nominal, issued at par, 1-year tenure, 3.90% p.a. payable semi-annually (Tranche 1 of the sixth issuance under the RM5.0b MTN Programme).",
            amount_rm=75_000_000,
            proceeds_use="Operating expenses, capex, investment, refinancing and working capital of GENM group."),
        rec("GENM", "acquisition", "2025-05-02",
            "Acquisition of remaining 51% of Genting Empire Resorts LLC", "9594817",
            effective_date="2025-05-31", status="completed",
            terms=("Genting ER Limited (indirect wholly-owned GENM subsidiary) acquired the "
                   "remaining 51% membership interest in GERL from Kien Huat Realty III Limited "
                   "and accepted assignment of intercompany loans, for total cash consideration "
                   "of USD41.7 million (including accrued interest)."),
            amount_usd=41_700_000,
            counterparty="Kien Huat Realty III Limited",
            notes="Related-party transaction. Completed 31 May 2025 (announcement 9724705)."),

        # ---------------- Other material corporate / regulatory events ----------------
        rec("GENTING", "litigation_settlement", "2025-03-21",
            "Stipulation for settlement with the Nevada Gaming Control Board (RWLV)", "9244767",
            effective_date="2025-03-27", status="approved",
            terms=("Resorts World Las Vegas LLC and its holding companies signed a Stipulation "
                   "for Settlement and Order dated 20 March 2025 with the Nevada Gaming Control "
                   "Board; the Nevada Gaming Commission approved it at its 27 March 2025 hearing. "
                   "The announcement does not state a monetary penalty."),
            notes="Relates to the NGCB complaint dated 15 Aug 2024. Approval announcement 9278925."),
        rec("GENTING", "asset_handover", "2025-07-01",
            "Handover of Meizhou Wan Phase I power plant (BOT expiry)", "9880573",
            effective_date="2025-06-30", status="completed",
            terms=("SDIC Genting Meizhou Wan Electric Power Company Limited (49%-owned indirect "
                   "joint venture) handed over its 2 x 393MW Meizhou Wan Phase I coal-fired power "
                   "plant to Fujian Investment & Development Group at 23:59 on 30 June 2025, on "
                   "expiry of the 21.5-year build-operate-transfer power purchase agreement."),
            notes="No consideration stated in the announcement."),
        rec("GENM", "licence_award", "2025-12-16",
            "New York commercial casino licence awarded to Genting New York LLC", "10813373",
            effective_date="2025-12-15", status="awarded",
            terms=("Genting New York LLC's bid for a downstate New York commercial casino licence "
                   "was selected by the New York Gaming Facility Location Board on 1 Dec 2025 and "
                   "awarded by the New York State Gaming Commission on 15 Dec 2025. RWNYC was "
                   "expected to open the first phase in 2Q2026; full commercial casino operations "
                   "began on 28 April 2026."),
            notes=("Bid submitted 27 Jun 2025 (announcement 9877997); selection 2 Dec 2025 "
                   "(10730039); award 16 Dec 2025. The bid described a proposed multi-billion-"
                   "dollar investment but no exact amount was stated.")),
        rec("GENM", "asset_disposal", "2025-08-15",
            "Proposed sale of Empire Resorts' non-gaming assets and related refinancing", "10196205",
            status="not_proceeding",
            terms=("Proposal by Empire Resorts Inc. to sell its non-gaming assets (RWC hotel, "
                   "Alder Hotel, Monster Golf Course, Epicenter and restaurants) to Sullivan County "
                   "Resort Facilities Local Development Corporation for USD525.0m; purchase 1,554.6 "
                   "acres from EPR Properties for USD201.3m; redeem the USD300m 7.75% senior notes "
                   "due 1 Nov 2026; and enter into a long-term land lease and management agreement."),
            amount_usd=525_000_000,
            notes=("On 3 Jul 2026 Empire redeemed the USD300m notes in full and the parties agreed "
                   "the Proposal would not proceed (announcement 11625481).")),
        rec("GENM", "bond_redemption", "2026-07-03",
            "Empire Resorts redeems USD300 million 7.75% senior notes due 2026", "11625481",
            effective_date="2026-07-02", status="completed",
            terms="Empire Resorts Inc. redeemed in full the USD300.0m 7.75% senior secured notes due 1 November 2026.",
            amount_usd=300_000_000,
            notes="With the redemption, the parties agreed the 15 Aug 2025 asset-sale/refinancing proposal would not proceed."),
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps({k: r[k] for k in FIELDS}, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} corporate actions -> {OUT}")
    for r in rows:
        print(f"  {r['company']:8} {r['announcement_date']} {r['action_type']:18} {r['title'][:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
