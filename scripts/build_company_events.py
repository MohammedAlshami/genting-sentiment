#!/usr/bin/env python3
"""Build the curated ownership / corporate-event / legal dataset for GENTING & GENM.

Outputs:
  data/raw/company_events.jsonl
  data/raw/ownership.jsonl
  data/raw/company_structure.json

Facts are drawn from Bursa announcements (KLSE Screener mirror), the FY2024/FY2025
integrated annual reports, court filings and contemporaneous news. Every event
carries at least one source URL and a status (announced / completed / failed /
pending / ongoing / withdrawn / routine).
"""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/raw"

GENT_AR25 = "https://www.genting.com/wp-content/uploads/2026/07/GENTING-BERHAD_IAR2025v2.pdf"
GENT_AR24 = "https://www.genting.com/wp-content/uploads/2025/05/GENTING_IAR24v3.pdf"
GENM_AR25 = "https://www.klsescreener.com/v2/announcements/view/11539849"
GENM_AR24 = "https://www.klsescreener.com/v2/announcements/view/9434623"
KL = "https://www.klsescreener.com/v2/announcements/view/"

EVENTS: list[dict] = []


def ev(
    d: str,
    ticker: str,
    channel: str,
    event_type: str,
    title: str,
    body: str,
    url: str,
    *,
    amount: str | None = None,
    counterparties: list[str] | None = None,
    status: str = "announced",
    sources: list[str] | None = None,
    notes: str | None = None,
    confidence: str = "high",
) -> None:
    EVENTS.append(
        {
            "date": d,
            "ticker": ticker,
            "channel": channel,
            "event_type": event_type,
            "title": title,
            "body": body,
            "url": url,
            "amount": amount,
            "counterparties": counterparties or [],
            "status": status,
            "sources": sources or [url],
            "notes": notes,
            "confidence": confidence,
        }
    )


# ---------------------------------------------------------------------------
# 2024
# ---------------------------------------------------------------------------
ev(
    "2024-11-22",
    "GENM",
    "RWLV",
    "legal",
    "Genting Americas moves to dismiss RAV Bahamas' US$600m claim over RW Bimini",
    "Genting Americas Inc, an indirect wholly owned Genting Malaysia subsidiary, filed a motion to dismiss RAV Bahamas Ltd's complaint in the US District Court for the Southern District of Florida. RAV, which owns 22% of RW Bimini operator BB Entertainment Ltd, sought damages in excess of US$600m; Genting Malaysia called the claim a shareholder dispute that belongs in arbitration. The case remained pending after mediation failed in May 2025.",
    GENT_AR25,
    amount=">US$600m claimed",
    counterparties=["RAV Bahamas Ltd", "BB Entertainment Ltd"],
    status="ongoing",
    notes="GENT FY2025 Integrated Annual Report, Note 47 Material Litigation, pp. 218-219.",
)

# ---------------------------------------------------------------------------
# 2025
# ---------------------------------------------------------------------------
ev(
    "2025-02-27",
    "GENTING",
    "GENTING",
    "dividend",
    "Genting Berhad declares FY2024 final dividend of 5.0 sen",
    "Genting Berhad declared a final single-tier dividend of 5.0 sen per ordinary share for FY2024, with ex-date 14 March 2025 and payment on 16 April 2025. The FY2024 total was 11.0 sen (6.0 sen interim plus 5.0 sen final), the last year before the payout was halved.",
    KL + "9161089",
    amount="RM192.5m (5.0 sen/share)",
    counterparties=["shareholders"],
    status="completed",
    sources=[KL + "9161089", GENT_AR25],
    notes="Payment amount based on 3,850,576,099 shares excluding treasury; AR2025 Directors' Report.",
)

ev(
    "2025-02-27",
    "GENTING",
    "GENTING",
    "board_change",
    "Lim Kok Thay relinquishes CEO role; Tan Kong Han becomes Chief Executive",
    "Effective 1 March 2025, Tan Sri Lim Kok Thay was redesignated Executive Chairman from Chief Executive Officer, and Dato' Sri Tan Kong Han was redesignated Chief Executive Officer from Executive Director. The split separated the Lim family's chairman role from day-to-day management after more than 50 years in which Lim Kok Thay had combined both roles.",
    KL + "9161073",
    counterparties=["Tan Sri Lim Kok Thay", "Dato' Sri Tan Kong Han"],
    status="completed",
    sources=[KL + "9161073", KL + "9161079", GENT_AR25],
)

ev(
    "2025-02-27",
    "GENTING",
    "GENTING",
    "board_change",
    "Independent director Eric Ooi Lip Aun resigns",
    "Eric Ooi Lip Aun resigned as an Independent Non-Executive Director on 27 February 2025 for personal considerations, with no disagreement with the board. The resignation reduced the Genting Berhad board to seven directors.",
    KL + "9161103",
    counterparties=["Eric Ooi Lip Aun"],
    status="completed",
    sources=[KL + "9161103", GENT_AR25],
)

ev(
    "2025-03-27",
    "GENTING",
    "RWLV",
    "regulatory_penalty",
    "Nevada Gaming Commission approves US$10.5m fine against Resorts World Las Vegas",
    "The Nevada Gaming Commission approved a stipulated settlement and US$10.5m fine against Resorts World Las Vegas and parent Genting Berhad over anti-money-laundering failures and dealings with illegal bookmakers. It was the second-largest fine in Nevada gaming history at the time. The penalty pre-dated the separate civil RICO suit filed in December 2025.",
    "https://www.nst.com.my/business/corporate/2025/03/1191412/genting-paying-nevada-gaming-commission-us105mil-settle-las-vegas",
    amount="US$10.5m",
    counterparties=["Nevada Gaming Commission", "Nevada Gaming Control Board", "Resorts World Las Vegas LLC"],
    status="completed",
    sources=[
        "https://www.nst.com.my/business/corporate/2025/03/1191412/genting-paying-nevada-gaming-commission-us105mil-settle-las-vegas",
        "https://igamingbusiness.com/casino/land-based-casino-regulation/resorts-world-nevada-fine-approved/",
    ],
)

ev(
    "2025-03-07",
    "GENTING",
    "GENTING",
    "ownership_change",
    "Kien Huat's 2025 Genting Berhad accumulation becomes visible",
    "A substantial-shareholder notice showed Kien Huat Realty Sdn Berhad holding 1,648,659,110 Genting Berhad shares, or 42.816%, with the Lim family's deemed interest at 44.066%. The disclosure was the first in a run that lifted the family's deemed stake to 45.07% by late October 2025, ahead of the GENM takeover.",
    KL + "9186625",
    amount="42.816% direct (KHR); 44.066% deemed",
    counterparties=["Kien Huat Realty Sdn Berhad", "Parkview Management Sdn Bhd"],
    status="completed",
    sources=[KL + "9186625", GENT_AR24, GENT_AR25],
    notes="Exact notice ID for the 7 March 2025 KHR filing is 9340145; percentages from the notice and AR2025.",
)

ev(
    "2025-04-10",
    "GENTING",
    "GENTING",
    "ownership_change",
    "Kien Huat raises Genting Berhad stake to 43.587%",
    "Kien Huat Realty Sdn Berhad acquired a further 5,000,000 Genting Berhad shares, lifting its direct stake to 1,678,348,910 shares or 43.587%. The Lim family's deemed interest through KHR, KHI and Parkview Management rose to 44.837%, the level reported in the FY2024 annual report five days later.",
    KL + "9412051",
    amount="43.587% direct; 44.837% deemed",
    counterparties=["Kien Huat Realty Sdn Berhad"],
    status="completed",
    sources=[KL + "9412051", GENT_AR24],
)

ev(
    "2025-04-16",
    "GENTING",
    "GENTING",
    "dividend",
    "Genting Berhad pays FY2024 final dividend of 5.0 sen",
    "Genting Berhad paid the FY2024 final single-tier dividend of 5.0 sen per share on 16 April 2025, amounting to about RM192.5m. Combined with the 6.0 sen interim paid in 2024, the FY2024 total was 11.0 sen.",
    KL + "9161089",
    amount="RM192.5m",
    counterparties=["shareholders"],
    status="completed",
    sources=[KL + "9161089", GENT_AR25],
)

ev(
    "2025-05-31",
    "GENM",
    "GENM",
    "acquisition",
    "Genting Malaysia completes buyout of Empire Resorts for US$41m",
    "Genting Malaysia completed the acquisition of the remaining 51% interest in Genting Empire Resorts LLC from Kien Huat Realty III Limited, a Lim-family vehicle, for US$41m cash plus about US$40m of assumed debt. Empire Resorts Inc became an indirect wholly owned subsidiary. The related-party deal was queried by Bursa Malaysia and drew governance scrutiny because it bought a loss-making US business from the controlling family.",
    "https://theedgemalaysia.com/node/753817",
    amount="US$41m cash + ~US$40m debt",
    counterparties=["Kien Huat Realty III Limited", "Genting Empire Resorts LLC", "Empire Resorts Inc"],
    status="completed",
    sources=[
        "https://theedgemalaysia.com/node/753817",
        "https://theedgemalaysia.com/node/754615",
        "https://asgam.com/2025/06/04/genting-malaysia-completes-full-acquisition-of-troubled-us-entity-empire-resorts/",
        KL + "9663623",
        GENM_AR25,
    ],
    notes="Completion 31 May 2025; Bursa query reply 8 May 2025; AR2025 Note 44(b)(vii) records RM174.1m including loan assignment.",
)

ev(
    "2025-06-11",
    "GENM",
    "GENM",
    "agm",
    "Genting Malaysia 45th AGM approves nine resolutions",
    "Genting Malaysia's 45th AGM approved nine ordinary resolutions, including directors' fees of RM1,904,098 for FY2024 and renewal of the share buy-back authority. The meeting was held at Wisma Genting, Kuala Lumpur.",
    KL + "9784091",
    counterparties=["shareholders"],
    status="completed",
    sources=[KL + "9784091", GENM_AR25],
)

ev(
    "2025-06-12",
    "GENTING",
    "GENTING",
    "agm",
    "Genting Berhad 57th AGM approves eight resolutions",
    "Genting Berhad's 57th AGM approved all eight ordinary resolutions, including directors' fees of RM1,636,290 for FY2024, re-election of Tan Sri Lim Kok Thay and Datuk Manharlal Ratilal, and renewal of the share buy-back mandate. The meeting was held at Wisma Genting, Kuala Lumpur.",
    KL + "9788741",
    counterparties=["shareholders"],
    status="completed",
    sources=[KL + "9788741", GENT_AR25],
)

ev(
    "2025-07-01",
    "GENM",
    "RWLV",
    "legal",
    "US court dismisses RAV Bahamas complaint, with leave to amend",
    "The US District Court for the Southern District of Florida granted Genting Americas' motion to dismiss RAV Bahamas' US$600m complaint, giving RAV one last opportunity to amend. Genting said the ruling reinforced its view that the claim was baseless. RAV filed an amended complaint on 29 July 2025.",
    GENT_AR25,
    amount=">US$600m claimed",
    counterparties=["RAV Bahamas Ltd", "Genting Americas Inc"],
    status="ongoing",
    sources=[GENT_AR25],
    notes="AR2025 Note 47, p. 218.",
)

ev(
    "2025-07-29",
    "GENM",
    "RWLV",
    "legal",
    "RAV Bahamas files amended complaint against Genting Americas",
    "RAV Bahamas filed an amended complaint seeking to bring claims derivatively on behalf of BB Entertainment Ltd and adding claims about Genting Americas' business conduct. Genting Americas rejected the claims and filed a further motion to dismiss on 12 September 2025.",
    GENT_AR25,
    amount=">US$600m claimed",
    counterparties=["RAV Bahamas Ltd", "Genting Americas Inc", "BB Entertainment Ltd"],
    status="ongoing",
    sources=[GENT_AR25],
    notes="AR2025 Note 47, pp. 218-219.",
)

ev(
    "2025-08-15",
    "GENM",
    "GENM",
    "debt_restructuring",
    "Empire Resorts announces US$525m asset-sale recapitalisation",
    "Genting Malaysia announced a proposal to strengthen Empire Resorts' capital structure, including the proposed US$525m disposal of non-gaming assets at Resorts World Catskills to Sullivan County Resort Facilities Local Development Corp and redemption of Empire's US$300m 7.75% senior secured notes due November 2026. The proposal was later shelved after Empire repaid the notes.",
    KL + "11625481",
    amount="US$525m asset sale; US$300m notes",
    counterparties=["Empire Resorts Inc", "Sullivan County Resort Facilities Local Development Corp"],
    status="withdrawn",
    sources=[KL + "11625481", "https://www.ggrasia.com/genting-malaysia-shelves-empire-resorts-recapitalisation-after-repayment-of-us300mln-notes"],
)

ev(
    "2025-09-12",
    "GENM",
    "RWLV",
    "legal",
    "Genting Americas moves to dismiss RAV Bahamas' amended complaint",
    "Genting Americas filed a motion to dismiss RAV Bahamas' amended complaint, saying it repeated earlier allegations without new material facts. The litigation remained pending at the FY2025 annual report date.",
    GENT_AR25,
    amount=">US$600m claimed",
    counterparties=["RAV Bahamas Ltd", "Genting Americas Inc"],
    status="ongoing",
    sources=[GENT_AR25],
)

ev(
    "2025-10-13",
    "GENTING",
    "GENTING",
    "takeover_offer",
    "Genting Berhad launches RM2.35/share conditional takeover offer for Genting Malaysia",
    "Genting Berhad served a conditional voluntary takeover notice on Genting Malaysia's board to buy all 2,870,039,874 GENM shares it did not own (50.64% of shares excluding treasury) at RM2.35 cash each, valuing the minority stake at about RM6.745b (US$1.59b). Genting said the offer was to obtain statutory control and did not intend to maintain GENM's listing if sufficient acceptances were received. Trading in both stocks was suspended for the announcement.",
    KL + "10518319",
    amount="RM2.35/share; ~RM6.745b for 50.64%",
    counterparties=["Genting Malaysia Berhad", "AmInvestment Bank Berhad"],
    status="announced",
    sources=[KL + "10518319", KL + "10597715", KL + "10597725", "https://theedgemalaysia.com/node/777354"],
)

ev(
    "2025-10-16",
    "GENTING",
    "GENTING",
    "insider_buying",
    "Kien Huat buys 3m Genting Berhad shares at RM3.48112",
    "Kien Huat Realty Sdn Berhad acquired 3,000,000 Genting Berhad shares on 16 October 2025 at RM3.48112 each, lifting the Lim family's deemed interest to 44.915%. Further purchases on 17 and 27-28 October took the family to 45.072% by 29 October 2025.",
    KL + "10528291",
    amount="3,000,000 shares; RM10.44m",
    counterparties=["Kien Huat Realty Sdn Berhad"],
    status="completed",
    sources=[KL + "10528291", KL + "10557479", KL + "10579599"],
)

ev(
    "2025-10-28",
    "GENTING",
    "GENTING",
    "ownership_change",
    "Lim family stake in Genting Berhad reaches 45.07%",
    "After open-market purchases on 16, 17, 27 and 28 October 2025 totalling 9,049,700 shares, Kien Huat Realty held 1,687,398,610 Genting Berhad shares (43.822%) and the Lim family's deemed interest through KHR, KHI and Parkview Management reached 1,735,518,590 shares (45.072%). This was the stake level reported in the FY2025 annual report.",
    KL + "10579497",
    amount="45.072% deemed",
    counterparties=["Kien Huat Realty Sdn Berhad", "Parkview Management Sdn Bhd", "Tan Sri Lim Kok Thay"],
    status="completed",
    sources=[KL + "10579497", KL + "10579581", GENT_AR25],
)

ev(
    "2025-11-03",
    "GENTING",
    "GENTING",
    "takeover_offer",
    "GENM takeover turns unconditional after Genting crosses 50%",
    "Genting Berhad's offer became unconditional on 3 November 2025 after open-market purchases took its holding, together with shares already acquired or entitled, above 50.00% of GENM shares excluding treasury. The first closing date was 24 November 2025. The offer document was despatched the same day.",
    KL + "10598787",
    amount=">50% of GENM",
    counterparties=["Genting Malaysia Berhad"],
    status="unconditional",
    sources=[KL + "10598787", KL + "10597725"],
)

ev(
    "2025-11-10",
    "GENTING",
    "GENTING",
    "ownership_change",
    "Genting Berhad's GENM stake crosses 52.63%",
    "Genting Berhad's stake in Genting Malaysia rose to 52.63% through on-market purchases and acceptances under the offer, according to Bursa filings reported by GGR Asia. The same day, Genting RMTN issued RM900m of one-year MTNs at 1-month KLIBOR + 1.80% to part-finance the acquisition.",
    "https://www.ggrasia.com/genting-bhd-crosses-52pct-ownership-mark-in-genting-malaysia",
    amount="52.63%; RM900m MTN",
    counterparties=["Genting Malaysia Berhad", "Genting RMTN Berhad"],
    status="completed",
    sources=[
        "https://www.ggrasia.com/genting-bhd-crosses-52pct-ownership-mark-in-genting-malaysia",
        KL + "10681211",
    ],
)

ev(
    "2025-11-13",
    "GENTING",
    "GENTING",
    "takeover_offer",
    "GENM offer becomes mandatory; closing extended to 1 December",
    "Genting acquired 34,929,300 GENM shares on 13 November 2025, taking total open-market purchases in the six-month period to 114,469,300 shares (2.02%). That triggered a mandatory offer under the Malaysian Code, converted the voluntary offer into an unconditional mandatory offer, and extended the closing date from 24 November to 1 December 2025. Genting's stake, including acceptances, was reported at just over 57.0%.",
    KL + "10695835",
    amount="114,469,300 shares acquired (2.02%); offer RM2.35",
    counterparties=["Genting Malaysia Berhad", "Securities Commission Malaysia"],
    status="mandatory",
    sources=[
        KL + "10695835",
        "https://www.ggrasia.com/genting-bhd-takeover-bid-for-genting-malaysia-now-mandatory-stake-rises-to-57pct",
        "https://www.thestar.com.my/business/business-news/2025/11/14/gentings-genm-takeover-bid-becomes-mandatory-as-stake-crosses-2-limit",
    ],
)

ev(
    "2025-11-13",
    "GENM",
    "GENM",
    "independent_advice",
    "Independent adviser says RM2.35 GENM offer is 'not fair and not reasonable'",
    "Genting Malaysia's independent adviser recommended shareholders reject Genting Berhad's RM2.35 cash offer, concluding it was neither fair nor reasonable. The adviser noted shareholders could sell in the open market and that Genting needed 90% to compulsorily acquire. The circular was dated 13 November 2025.",
    KL + "10694735",
    amount="RM2.35/share",
    counterparties=["Genting Malaysia Berhad", "Genting Berhad"],
    status="completed",
    sources=[
        KL + "10694735",
        "https://theedgemalaysia.com/node/779551",
        "https://www.freemalaysiatoday.com/category/highlight/2025/11/13/takeover-offer-for-genting-malaysia-not-fair-and-not-reasonable",
    ],
)

ev(
    "2025-11-18",
    "GENM",
    "RWNYC",
    "regulatory_tax",
    "Resorts World asks New York to reconsider casino tax rates",
    "Resorts World, bidding for a downstate New York licence, asked the state to lower its proposed tax rate or raise the levy on rival bidders. Genting had proposed the highest slot tax at 56%, versus 25% for Hard Rock/Mets and 30% for Bally's. New York's Gaming Facility Location Board later rejected any reduction.",
    "https://www.thestar.com.my/business/business-news/2025/11/18/gentings-resorts-world-to-ask-new-york-to-reconsider-casino-tax-rates-after-bid",
    amount="56% proposed slot tax",
    counterparties=["New York State Gaming Commission", "Genting New York LLC"],
    status="rejected",
    sources=[
        "https://www.thestar.com.my/business/business-news/2025/11/18/gentings-resorts-world-to-ask-new-york-to-reconsider-casino-tax-rates-after-bid",
        "https://nysfocus.com/2026/06/01/nyc-casino-resorts-world-horseracing-support-tax",
    ],
)

ev(
    "2025-11-19",
    "GENTING",
    "GENTING",
    "ownership_change",
    "Genting Berhad's GENM stake passes 60.6%",
    "Bursa substantial-shareholder notices showed Genting Berhad holding 3,435,138,666 GENM shares, or 60.609%, as acceptances under the offer increased. The Lim family's deemed interest was 60.630%.",
    KL + "10706821",
    amount="60.609% direct",
    counterparties=["Genting Malaysia Berhad"],
    status="completed",
    sources=[KL + "10706821", "https://www.ggrasia.com/genting-bhd-now-controls-over-60pct-in-genting-malaysia"],
)

ev(
    "2025-11-20",
    "GENTING",
    "GENTING",
    "debt_issuance",
    "Genting RMTN issues RM495m of one-year MTNs",
    "Genting RMTN Berhad issued RM495m nominal of Tranche 6 one-year MTNs at 1-month KLIBOR + 1.80%, part-financing the GENM takeover. The issuance followed RM900m of Tranche 5 MTNs on 10 November 2025.",
    KL + "10707633",
    amount="RM495m",
    counterparties=["Genting RMTN Berhad", "Affin Hwang Investment Bank", "AmInvestment Bank"],
    status="completed",
    sources=[KL + "10707633", KL + "10681211"],
)

ev(
    "2025-11-27",
    "GENTING",
    "GENTING",
    "debt_issuance",
    "Genting RMTN issues RM255m of one-year MTNs",
    "Genting RMTN Berhad issued RM255m nominal of Tranche 7 one-year MTNs at 1-month KLIBOR + 1.80%, part-financing the GENM takeover. Together with the November tranches, Genting RMTN issued RM1.65b of one-year paper for the offer.",
    KL + "10724501",
    amount="RM255m",
    counterparties=["Genting RMTN Berhad"],
    status="completed",
    sources=[KL + "10724501"],
)

ev(
    "2025-12-01",
    "GENTING",
    "GENTING",
    "takeover_offer",
    "GENM takeover closes at 73.13%, falling short of 75% delisting threshold",
    "Genting Berhad's unconditional offer closed at 5pm on 1 December 2025 with Genting holding 4,144,966,481 GENM shares, or 73.13% excluding treasury. It fell short of the 75% threshold needed to delist GENM, so Genting Malaysia remained listed. The offer had been priced at RM2.35 and became mandatory in November.",
    KL + "10728467",
    amount="73.13%; 4,144,966,481 shares",
    counterparties=["Genting Malaysia Berhad"],
    status="failed",
    notes="Failed to achieve the 75% delisting threshold; offer itself completed and acceptances were settled.",
    sources=[
        KL + "10728467",
        "https://theedgemalaysia.com/node/784367",
        "https://www.ggrasia.com/genting-malaysia-to-stay-listed-as-parents-stake-was-73pct-at-the-close-of-its-offering",
    ],
)

ev(
    "2025-12-02",
    "GENM",
    "RWNYC",
    "regulatory_licence",
    "New York board selects Resorts World New York City for casino licence consideration",
    "The New York Gaming Facility Location Board selected Genting New York LLC's Resorts World New York City bid, along with Bally's Bronx and Hard Rock Metropolitan Park, to proceed to New York State Gaming Commission licensure. The board voted 5-0; final licences were expected by 31 December 2025. Genting proposed a US$5.5b expansion and a US$600m upfront licence fee.",
    KL + "10730039",
    amount="US$5.5b expansion; US$600m upfront fee",
    counterparties=["New York Gaming Facility Location Board", "Genting New York LLC"],
    status="recommended",
    sources=[
        KL + "10730039",
        "https://www.ggrasia.com/genting-recommended-for-downstate-new-york-full-casino-licence",
        "https://nycasinos.ny.gov/system/files/documents/2026/03/12.01.25.gflbselectiondocument1.pdf",
    ],
)

ev(
    "2025-12-03",
    "GENTING",
    "RWLV",
    "legal",
    "Civil RICO lawsuit filed against Resorts World Las Vegas and Genting Berhad",
    "High-stakes gambler Robert J. Cipriani and investor James Russell filed a 95-page civil RICO complaint in the US District Court for the District of Nevada against Resorts World Las Vegas, Genting Berhad, former RWLV president Scott Sibella, attorney David Chesnoff and others. The complaint alleged the casino enabled illegal gambling, money laundering and retaliation against a cooperating witness from 2021-2023. Genting denied the claims.",
    "https://www.vegasslotsonline.com/news/2025/12/05/federal-lawsuit-accuses-resorts-world-of-facilitating-large-scale-organized-crime/",
    amount="treble damages sought (unspecified)",
    counterparties=["Robert J. Cipriani", "James Russell", "Scott Sibella", "David Chesnoff"],
    status="ongoing",
    sources=[
        "https://www.vegasslotsonline.com/news/2025/12/05/federal-lawsuit-accuses-resorts-world-of-facilitating-large-scale-organized-crime/",
        "https://dockets.justia.com/docket/nevada/nvdce/2:2025cv02396/178321",
    ],
    notes="Case No. 2:25-cv-02396-JCM-DJA, filed 3 December 2025.",
)

ev(
    "2025-12-05",
    "GENTING",
    "GENTING",
    "debt_issuance",
    "Genting issues RM1.35b MTN and lodges RM5b unrated programme",
    "Genting RMTN Berhad issued RM1.35b of one-year MTNs at 1-month KLIBOR + 1.80% (Tranche 8) to part-finance the GENM takeover, while Genting Vista Berhad lodged a new RM5b unrated MTN programme with the Securities Commission. The programme was guaranteed by Genting Berhad.",
    KL + "10742285",
    amount="RM1.35b issued; RM5b programme",
    counterparties=["Genting RMTN Berhad", "Genting Vista Berhad", "Securities Commission Malaysia"],
    status="completed",
    sources=[KL + "10742285", KL + "10742301", "https://theedgemalaysia.com/node/785048"],
)

ev(
    "2025-12-08",
    "GENTING",
    "GENTING",
    "credit_rating",
    "Moody's downgrades Genting Berhad to Baa3 and Genting Singapore to Baa1",
    "Moody's Ratings downgraded Genting Berhad and Genting Overseas Holdings Ltd to Baa3 from Baa2, and Genting Singapore Ltd to Baa1 from A3, with stable outlooks. The agency cited increased debt to fund the GENM takeover and expected spending after the New York casino licence, against a slower earnings recovery. It also downgraded GOHL Capital's backed senior unsecured notes to Baa3.",
    "https://theedgemalaysia.com/node/785277",
    amount="GENT Baa2 -> Baa3; GENS A3 -> Baa1",
    counterparties=["Moody's Ratings", "Genting Overseas Holdings Ltd", "Genting Singapore Ltd"],
    status="completed",
    sources=[
        "https://theedgemalaysia.com/node/785277",
        "https://www.businesstimes.com.sg/companies-markets/moodys-downgrades-genting-bhd-and-two-subsidiaries",
        "https://asgam.com/2025/12/09/moodys-downgrades-genting-berhad-on-new-debt-linked-to-genting-malaysia-takeover-new-york-license-win",
    ],
)

ev(
    "2025-12-13",
    "GENTING",
    "GENTING",
    "credit_rating",
    "RAM revises Genting and GENM outlook to negative, keeps AA1",
    "RAM Ratings maintained the AA1 long-term corporate credit ratings of Genting Berhad and Genting Malaysia but revised the outlook to negative from stable. It cited the higher-than-expected 73% GENM stake, reduced debt headroom and capex for the Resorts World New York City full casino, with net debt/OPBDIT potentially rising to about 3.4x in FY2026.",
    "https://www.businesstoday.com.my/2025/12/13/ram-revises-genting-berhad-credit-ratings-to-negative-after-takeover-bid",
    amount="AA1 maintained; outlook negative",
    counterparties=["RAM Ratings", "Genting Malaysia Berhad"],
    status="completed",
    sources=[
        "https://www.businesstoday.com.my/2025/12/13/ram-revises-genting-berhad-credit-ratings-to-negative-after-takeover-bid",
        "https://www.ram.com.my/pressrelease?prviewid=7152",
    ],
)

ev(
    "2025-12-16",
    "GENM",
    "RWNYC",
    "regulatory_licence",
    "New York State Gaming Commission awards full casino licence to Resorts World NYC",
    "The New York State Gaming Commission unanimously awarded a full commercial casino licence to Genting New York LLC for Resorts World New York City at Aqueduct Racetrack in Queens. Genting said the first phase of the expanded integrated resort would open by Q2 2026. The licence allowed live table games, which launched on 28 April 2026.",
    "https://www.thestar.com.my/business/business-news/2025/12/16/genting-malaysia-gets-the-nod-for-new-york-casino-licence",
    amount="US$600m upfront licence fee; US$5.5b expansion",
    counterparties=["New York State Gaming Commission", "Genting New York LLC"],
    status="completed",
    sources=[
        "https://www.thestar.com.my/business/business-news/2025/12/16/genting-malaysia-gets-the-nod-for-new-york-casino-licence",
        "https://www.ggrasia.com/genting-two-other-bidders-approved-for-downstate-new-york-full-casino-licences",
        "https://www.nst.com.my/business/corporate/2025/12/1338105/nyc-casino-licence-approvals-open-door-genting-malaysias-us",
    ],
    notes="Some reports cite a US$500m fee paid versus a US$600m commitment; see report for conflict note.",
)

ev(
    "2025-12-17",
    "GENTING",
    "GENTING",
    "credit_rating",
    "S&P revises Genting group outlook to negative, affirms ratings",
    "S&P Global Ratings revised the outlook on Genting Berhad, Genting Malaysia, Genting New York and Resorts World Las Vegas to negative from stable, while affirming issuer and issue ratings. It estimated group capex would double to about RM12b in 2026 and stay above RM8b annually through 2030, with FFO/debt falling below 20%.",
    "https://www.businesstimes.com.sg/companies-markets/sp-global-shifts-genting-companies-outlook-negative-weaker-credit-quality-forecasts",
    amount="outlook negative; ratings affirmed",
    counterparties=["S&P Global Ratings", "Genting Malaysia Berhad", "Genting New York LLC", "Resorts World Las Vegas LLC"],
    status="completed",
    sources=[
        "https://www.businesstimes.com.sg/companies-markets/sp-global-shifts-genting-companies-outlook-negative-weaker-credit-quality-forecasts",
        "https://www.ggrasia.com/genting-bhd-and-some-gaming-units-are-tagged-outlook-negative-on-elevated-spending-risk-appetite-sp-global",
    ],
    notes="S&P had Genting at BBB- (lowest investment grade) at this point; this was an outlook change, not a rating cut.",
)

ev(
    "2025-12-22",
    "GENTING",
    "GENTING",
    "credit_rating",
    "Fitch affirms Genting at BBB, removes rating watch, outlook negative",
    "Fitch Ratings affirmed Genting Berhad's long-term issuer default rating at BBB and removed it from rating watch negative, assigning a negative outlook. It also removed negative watch from Genting Malaysia, Genting Overseas Holdings, Resorts World Las Vegas and Genting New York. Fitch noted Genting spent MYR3.1b to acquire an additional 23.8% of GENM.",
    "https://www.ggrasia.com/fitch-affirms-genting-bhd-at-investment-grade-but-outlook-is-negative-amid-costs-on-genting-malaysia-downstate-ny-licence",
    amount="BBB affirmed; outlook negative; MYR3.1b takeover cost",
    counterparties=["Fitch Ratings", "Genting Malaysia Berhad", "Genting Overseas Holdings Ltd"],
    status="completed",
    sources=[
        "https://www.ggrasia.com/fitch-affirms-genting-bhd-at-investment-grade-but-outlook-is-negative-amid-costs-on-genting-malaysia-downstate-ny-licence",
        "https://www.fitchratings.com/",
    ],
)

ev(
    "2025-12-30",
    "GENTING",
    "GENTING",
    "debt_refinancing",
    "Genting Vista issues RM3b MTNs to redeem takeover-related RMTN notes",
    "Genting Vista Berhad issued RM3.0b nominal of unrated MTNs under its RM5b programme, with tenors of 1-5 years at 3-month KLIBOR + 1.80%. Proceeds redeemed RM3.0b of Genting RMTN MTNs issued in November-December 2025 to finance the GENM takeover, extending the debt maturity profile.",
    KL + "10858417",
    amount="RM3.0b",
    counterparties=["Genting Vista Berhad", "Genting RMTN Berhad"],
    status="completed",
    sources=[KL + "10858417", "https://www.thestar.com.my/business/business-news/2025/12/30/genting-vista-issues-rm3bil-unrated-medium-term-notes"],
)

# ---------------------------------------------------------------------------
# 2026
# ---------------------------------------------------------------------------
ev(
    "2026-01-30",
    "GENTING",
    "GENS",
    "board_change",
    "Lim Kok Thay appointed executive chairman of Resorts World at Sentosa",
    "Genting Singapore Ltd's SGX filing appointed Tan Sri Lim Kok Thay as chairman and director of Resorts World at Sentosa Pte Ltd, the operating entity of the Singapore casino complex, with the role designated executive in nature. Day-to-day management remained with CEO Lee Shi Ruh. Lim also remained Genting Berhad's Executive Chairman and Genting Malaysia's Deputy Chairman and Chief Executive.",
    "https://www.ggrasia.com/lim-kok-thay-now-executive-chairman-of-rws-operating-unit",
    counterparties=["Tan Sri Lim Kok Thay", "Genting Singapore Ltd", "Resorts World at Sentosa Pte Ltd"],
    status="completed",
    sources=["https://www.ggrasia.com/lim-kok-thay-now-executive-chairman-of-rws-operating-unit"],
)

ev(
    "2026-02-10",
    "GENM",
    "GENM",
    "credit_rating",
    "Fitch affirms Genting Malaysia at BBB with negative outlook",
    "Fitch Ratings affirmed Genting Malaysia's BBB long-term issuer default rating with a negative outlook, following the December 2025 affirmation of parent Genting Berhad. The affirmation preceded Fitch's September 2026 downgrade to BBB-.",
    "https://cbonds.com/news/3788399/",
    amount="BBB affirmed; outlook negative",
    counterparties=["Fitch Ratings"],
    status="completed",
    sources=["https://cbonds.com/news/3788399/", "https://www.fitchratings.com/entity/genting-malaysia-berhad-97128191"],
)

ev(
    "2026-02-25",
    "GENM",
    "RWLV",
    "credit_rating",
    "S&P downgrades Empire Resorts to B on refinancing risk",
    "S&P Global Ratings downgraded Empire Resorts Inc's long-term issuer credit rating to B from B+, with a negative outlook, citing rising refinancing risk on its US$300m bond due November 2026. It also cut the secured debt issue rating to B from B+ and lowered the stand-alone credit profile to ccc from ccc+.",
    "https://www.ggrasia.com/sp-downgrades-empire-resorts-rating-expects-genting-to-provide-further-support",
    amount="B from B+",
    counterparties=["S&P Global Ratings", "Empire Resorts Inc"],
    status="completed",
    sources=["https://www.ggrasia.com/sp-downgrades-empire-resorts-rating-expects-genting-to-provide-further-support"],
)

ev(
    "2026-02-26",
    "GENTING",
    "GENTING",
    "dividend",
    "Genting Berhad declares FY2025 final dividend of 5.0 sen",
    "Genting Berhad declared a final single-tier dividend of 5.0 sen per share for FY2025, with ex-date 17 March 2026 and payment on 17 April 2026. FY2025's total dividend was 5.0 sen, down from 11.0 sen in FY2024, as the group conserved cash for debt and capex.",
    KL + "11181555",
    amount="RM192.5m (5.0 sen/share)",
    counterparties=["shareholders"],
    status="completed",
    sources=[KL + "11181555", GENT_AR25],
)

ev(
    "2026-02-26",
    "GENM",
    "GENM",
    "dividend",
    "Genting Malaysia declares FY2025 final dividend of 7.0 sen",
    "Genting Malaysia declared a final single-tier dividend of 7.0 sen per share for FY2025, with ex-date 13 March 2026 and payment on 10 April 2026. FY2025's total dividend was 7.0 sen, down from 10.0 sen in FY2024 (6.0 sen interim plus 4.0 sen final).",
    KL + "11181513",
    amount="RM396.7m (7.0 sen/share)",
    counterparties=["shareholders"],
    status="completed",
    sources=[KL + "11181513", GENM_AR25],
)

ev(
    "2026-03-02",
    "GENM",
    "GENM",
    "management_change",
    "Lee Choong Yan moves to senior adviser; Lee Thiam Kit appointed President",
    "Effective 1 March 2026, Dato' Sri Lee Choong Yan was redesignated Senior Advisor and Executive Director from President and Executive Director, and Lee Thiam Kit was appointed President. Lee Choong Yan retired as Senior Advisor on 30 April 2026 and became a Non-Independent Non-Executive Director on 1 May 2026. Loh Wai Yee had become CFO on 1 April 2025.",
    KL + "11185095",
    counterparties=["Dato' Sri Lee Choong Yan", "Lee Thiam Kit", "Loh Wai Yee"],
    status="completed",
    sources=[KL + "11185095", GENM_AR25],
)

ev(
    "2026-03-13",
    "GENTING",
    "GENTING",
    "ownership_change",
    "Genting Berhad's GENM stake reaches 73.838%",
    "Bursa filings showed Genting Berhad holding 4,184,966,253 GENM shares, or 73.838%, after further open-market purchases. The Lim family's deemed interest was 73.859%. The purchases narrowed the gap to the 75% delisting threshold but did not reach it.",
    KL + "11302411",
    amount="73.838% direct; 73.859% deemed",
    counterparties=["Genting Malaysia Berhad"],
    status="completed",
    sources=[KL + "11302411", "https://www.ggrasia.com/genting-bhd-moves-closer-to-75pct-stake-target-for-taking-genting-malaysia-private"],
)

ev(
    "2026-03-30",
    "GENTING",
    "RWLV",
    "legal",
    "RWLV RICO plaintiffs file 107-page amended complaint adding Lim Kok Thay",
    "The plaintiffs in the Resorts World Las Vegas civil RICO case filed a first amended complaint adding Andrew Cheng Tao Do as a plaintiff and Tan Sri Lim Kok Thay, among others, as defendants. The amended complaint repeated allegations that Genting Berhad and RWLV tolerated or enabled illegal gambling and money laundering. Genting denied the claims.",
    "https://www.8newsnow.com/wp-content/uploads/sites/59/2026/03/File-Stamped-First-Amended-Complaint-with-new-parties.pdf",
    amount="treble damages sought (unspecified)",
    counterparties=["Robert J. Cipriani", "James Russell", "Andrew Cheng Tao Do", "Tan Sri Lim Kok Thay"],
    status="ongoing",
    sources=[
        "https://www.8newsnow.com/wp-content/uploads/sites/59/2026/03/File-Stamped-First-Amended-Complaint-with-new-parties.pdf",
        "https://dockets.justia.com/docket/nevada/nvdce/2:2025cv02396/178321",
    ],
    notes="Case No. 2:25-cv-02396-JCM-DJA, Document 36, filed 30 March 2026.",
)

ev(
    "2026-04-17",
    "GENTING",
    "GENTING",
    "annual_report",
    "Genting Berhad files FY2025 annual report; 58th AGM notice issued",
    "Genting Berhad submitted its FY2025 Integrated Annual Report and the notice of its 58th AGM. The report disclosed 26,320,000 treasury shares, 3,850,576,099 shares outstanding, a 45.07% Lim-family deemed stake, a 73.8% GENM stake and a 52.6% Genting Singapore stake.",
    KL + "11547907",
    counterparties=["shareholders"],
    status="completed",
    sources=[KL + "11547907", GENT_AR25, KL + "11546841"],
)

ev(
    "2026-04-20",
    "GENTING",
    "GENTING",
    "credit_rating",
    "Fitch assigns BB+ to Genting-linked perpetual securities, warns on leverage",
    "Fitch Ratings assigned a BB+ rating to Genting's proposed US-dollar subordinated perpetual capital securities, two notches below the BBB issuer rating, and said the issuance would provide limited credit relief. Moody's assigned Ba2. Fitch also flagged downgrade risk from the group's leverage and capex.",
    "https://www.businesstoday.com.my/2026/04/20/fitch-assigns-bb-ratings-on-genting-linked-perpetual-securities",
    amount="BB+ / Ba2 instrument ratings",
    counterparties=["Fitch Ratings", "Moody's Ratings", "GOHL Capital Holdings Limited"],
    status="completed",
    sources=[
        "https://www.businesstoday.com.my/2026/04/20/fitch-assigns-bb-ratings-on-genting-linked-perpetual-securities",
        "https://agbrief.com/news/malaysia/20/04/2026/fitch-moodys-see-limited-credit-relief-from-genting-perpetual-issuance",
    ],
)

ev(
    "2026-04-23",
    "GENTING",
    "GENTING",
    "debt_issuance",
    "Genting prices US$1.25b of subordinated perpetual securities",
    "GOHL Capital Holdings Limited priced US$750m of 7.625% Series 1 perpetual securities (non-callable 5.5 years) and US$500m of 8.300% Series 2 perpetual securities (non-callable 10 years), guaranteed on a subordinated basis by Genting Overseas Holdings. The securities were rated Ba2/BB+ and listed on SGX on 30 April 2026. Proceeds were for refinancing.",
    KL + "11554255",
    amount="US$1.25b",
    counterparties=["GOHL Capital Holdings Limited", "Genting Overseas Holdings Limited", "Deutsche Bank", "J.P. Morgan"],
    status="completed",
    sources=[KL + "11554255", KL + "11568687", "https://theedgemalaysia.com/node/801019"],
)

ev(
    "2026-04-28",
    "GENM",
    "RWNYC",
    "operations",
    "Resorts World New York City launches live table games",
    "Resorts World New York City began live table games on 28 April 2026, becoming the first full-scale casino in New York City. The property converted from video lottery terminals to commercial slot machines, and the applicable gaming machine tax rate fell to 56% from 68%, which Maybank estimated could boost Genting Malaysia's 12-month earnings by up to US$100m.",
    "https://www.ggrasia.com/gentings-resorts-world-new-york-city-to-launch-table-games-on-april-28",
    amount="~250 tables initially",
    counterparties=["New York State Gaming Commission", "Genting New York LLC"],
    status="completed",
    sources=[
        "https://www.ggrasia.com/gentings-resorts-world-new-york-city-to-launch-table-games-on-april-28",
        "https://www.ggrasia.com/a-lower-gaming-machine-tax-at-rwnyc-could-boost-genting-malaysia-earnings-maybank",
    ],
)

ev(
    "2026-04-30",
    "GENTING",
    "GENTING",
    "debt_tender",
    "Genting accepts US$882.462m of US$1.5b 2027 notes in tender",
    "GOHL Capital accepted US$882,462,000 principal of its outstanding US$1.5b 4.25% guaranteed notes due 2027 in a conditional tender offer, with settlement on 4 May 2026. About US$617.5m remained outstanding, which CreditSights later described as a US$618m bond maturing in January 2027.",
    KL + "11568689",
    amount="US$882.462m accepted; US$617.538m remaining",
    counterparties=["GOHL Capital Limited", "noteholders"],
    status="completed",
    sources=[KL + "11568689", KL + "11559551"],
)

ev(
    "2026-05-01",
    "GENM",
    "RWNYC",
    "operations",
    "Resorts World New York City opens as a full casino",
    "Genting opened New York City's first full-scale casino at Resorts World New York City in Queens, following the April table-games launch. The group committed US$5.5b to expand the property through 2030, including a 2,000-room hotel, arena, 6,000 slots and 800 tables.",
    "https://www.thestar.com.my/business/business-news/2026/05/01/genting-opens-new-york-casino-creates-history",
    amount="US$5.5b expansion",
    counterparties=["Genting New York LLC", "New York State"],
    status="completed",
    sources=[
        "https://www.thestar.com.my/business/business-news/2026/05/01/genting-opens-new-york-casino-creates-history",
        "https://www.ggrasia.com/gentings-resorts-world-new-york-city-to-launch-table-games-on-april-28",
    ],
)

ev(
    "2026-05-01",
    "GENM",
    "GENM",
    "board_change",
    "Lee Choong Yan becomes Non-Independent Non-Executive Director",
    "Dato' Sri Lee Choong Yan retired as Senior Advisor on 30 April 2026 and was redesignated a Non-Independent Non-Executive Director of Genting Malaysia on 1 May 2026. He remained on the board after stepping back from executive duties.",
    KL + "11185095",
    counterparties=["Dato' Sri Lee Choong Yan"],
    status="completed",
    sources=[KL + "11185095", GENM_AR25],
)

ev(
    "2026-05-21",
    "GENM",
    "GENM",
    "earnings",
    "Genting Malaysia posts 1Q26 net loss on New York pre-opening costs",
    "Genting Malaysia reported a 1Q26 net loss of RM25.2m (about US$6m) despite a 10% rise in revenue to RM2.87b, as pre-opening expenses at Resorts World New York City and higher payroll costs offset growth. Parent Genting Berhad's 1Q26 profit surged more than 20-fold on joint-venture gains and lower impairments.",
    "https://theedgemalaysia.com/node/804544",
    amount="GENM net loss RM25.2m; revenue RM2.87b",
    counterparties=["Genting Malaysia Berhad"],
    status="completed",
    sources=[
        "https://theedgemalaysia.com/node/804544",
        "https://asgam.com/2026/05/22/revenue-rising-but-genting-malaysia-falls-to-us6-million-net-loss-in-1q26-due-to-pre-opening-expenses-at-resorts-world-new-york-city",
    ],
)

ev(
    "2026-05-28",
    "GENM",
    "MALAYSIA",
    "regulatory_toll",
    "Genting Highlands access-road charges start at RM3.30-RM25",
    "Genting Malaysia began charging vehicles using the private access road to Genting Highlands, with rates from RM3.30 to RM25 depending on vehicle type. The Pahang state government and federal ministry said the road was privately owned and the charges were a state matter, not a federal toll. The move drew public criticism and a legal challenge from a developer.",
    "https://says.com/my/lifestyle/travel-lifestyle/genting-highlands-toll-starts-from-28-may-charges-range-from-rm3-30-to-rm25-per-vehicle-type",
    amount="RM3.30-RM25 per vehicle",
    counterparties=["Pahang State Government", "Genting Highlands Berhad"],
    status="completed",
    sources=[
        "https://says.com/my/lifestyle/travel-lifestyle/genting-highlands-toll-starts-from-28-may-charges-range-from-rm3-30-to-rm25-per-vehicle-type",
        "https://www.theedgemalaysia.com/node/780833",
    ],
)

ev(
    "2026-06-01",
    "GENM",
    "RWNYC",
    "regulatory_tax",
    "Resorts World NYC in US$500m+ dispute over racing-support payments",
    "Resorts World New York City became locked in a dispute with New York state over whether its 56% slot tax is inclusive of payments to the horseracing industry. The state Gaming Commission said the racing-support payments, at least US$150m a year, must be paid on top of tax; Genting said that would raise its effective slot tax to 72% and could cost it over US$500m before the other downstate casinos open around 2030.",
    "https://nysfocus.com/2026/06/01/nyc-casino-resorts-world-horseracing-support-tax",
    amount=">US$500m; ~US$150m/year",
    counterparties=["New York State Gaming Commission", "New York Racing Association", "Genting New York LLC"],
    status="ongoing",
    sources=[
        "https://nysfocus.com/2026/06/01/nyc-casino-resorts-world-horseracing-support-tax",
        "https://www.covers.com/industry/resorts-world-new-york-in-legal-dispute-with-the-state-june-2-2026",
    ],
)

ev(
    "2026-06-10",
    "GENM",
    "GENM",
    "agm",
    "Genting Malaysia 46th AGM approves eight resolutions; Teo Eng Siong retires",
    "Genting Malaysia's 46th AGM approved all eight ordinary resolutions, including the re-election of Tan Sri Lim Kok Thay and Dato' Sri Lee Choong Yan and renewal of the share buy-back authority. Non-Independent Non-Executive Director Teo Eng Siong retired at the conclusion of the meeting after 16 years on the board.",
    KL + "11611215",
    counterparties=["shareholders", "Teo Eng Siong"],
    status="completed",
    sources=[KL + "11611215", KL + "11611205", GENM_AR25],
)

ev(
    "2026-06-11",
    "GENTING",
    "GENTING",
    "agm",
    "Genting Berhad 58th AGM approves eight resolutions; Foong re-election draws 9% dissent",
    "Genting Berhad's 58th AGM approved all eight ordinary resolutions, including directors' fees of RM1,572,508 for FY2025 and the re-election of Tan Sri Foong Cheng Yuen and Dato' Sri Tan Kong Han. The re-election of Foong drew 9.05% of votes against, the largest dissent of the meeting; the buy-back mandate passed with 99.91% support.",
    KL + "11612349",
    counterparties=["shareholders"],
    status="completed",
    sources=[KL + "11612349", GENT_AR25],
)

ev(
    "2026-06-12",
    "GENTING",
    "GENTING",
    "governance",
    "Genting CEO says GENM takeover was for control, not privatisation",
    "Speaking at Genting Berhad's 11 June AGM (reported 12 June), CEO Tan Kong Han said the 2025 takeover was not aimed at privatising Genting Malaysia but at ensuring Genting had more than 50% control, and that the group was 'fortunate' to have raised its stake. The parent remained below the 75% delisting threshold. The remarks followed press speculation about a renewed privatisation attempt.",
    "https://www.ggrasia.com/genting-bhd-not-privatising-its-global-gaming-unit-genting-malaysia-report",
    amount="73.8% stake; below 75%",
    counterparties=["Tan Kong Han", "Genting Malaysia Berhad"],
    status="completed",
    sources=[
        "https://www.ggrasia.com/genting-bhd-not-privatising-its-global-gaming-unit-genting-malaysia-report",
        "https://asgam.com/2026/06/15/genting-bhd-ceo-says-balance-sheet-requirements-not-privatization-at-heart-of-genting-malaysia-takeover-bid",
    ],
)

ev(
    "2026-06-23",
    "GENM",
    "MALAYSIA",
    "legal",
    "Developer fails in challenge to Genting Highlands road privatisation",
    "A Malaysian developer failed in its bid to challenge the privatisation of the main access road to Genting Highlands. The dispute concerned eight land parcels alienated by the Pahang State Authority to Genting Highlands Berhad in March 2023 for use as a private road. The court outcome upheld the arrangement, clearing the way for the road charges introduced in May 2026.",
    "https://www.nst.com.my/news/regional/2026/06/1470619/developer-fails-bid-challenge-genting-road-privatisation-watch",
    amount="8 land parcels",
    counterparties=["Genting Highlands Berhad", "Pahang State Authority", "developer"],
    status="completed",
    sources=["https://www.nst.com.my/news/regional/2026/06/1470619/developer-fails-bid-challenge-genting-road-privatisation-watch"],
)

ev(
    "2026-07-02",
    "GENM",
    "GENM",
    "debt_maturity",
    "Empire Resorts redeems US$300m notes; recapitalisation shelved",
    "Empire Resorts redeemed in full its US$300m 7.75% senior secured notes due 1 November 2026 on 2 July 2026 (US Eastern time), removing the debt that underpinned the August 2025 recapitalisation proposal. Genting Malaysia and the other parties agreed the US$525m asset-sale/recapitalisation proposal would not proceed.",
    KL + "11625481",
    amount="US$300m redeemed; US$525m proposal withdrawn",
    counterparties=["Empire Resorts Inc", "Sullivan County Resort Facilities Local Development Corp"],
    status="completed",
    sources=[KL + "11625481", "https://www.nst.com.my/business/corporate/2026/07/1479747/genting-malaysia-unit-calls-capital-restructuring-after-settling"],
)

ev(
    "2026-07-09",
    "GENM",
    "GENM",
    "debt_issuance",
    "Genting Americas secures US$2b bank facility",
    "Genting Americas Inc, a wholly owned Genting Malaysia subsidiary, secured a new US$2b bank facility to refinance debt and fund the second phase of the Resorts World New York City expansion. S&P said the facility removed Empire Resorts' refinancing risk but construction risks remained.",
    "https://www.ggrasia.com/genting-americas-in-new-us2bln-bank-facility-to-refinance-debt-fund-second-phase-of-n-y-casino",
    amount="US$2b",
    counterparties=["Genting Americas Inc", "bank lenders"],
    status="completed",
    sources=[
        "https://www.ggrasia.com/genting-americas-in-new-us2bln-bank-facility-to-refinance-debt-fund-second-phase-of-n-y-casino",
        "https://agbrief.com/news/usa/09/07/2026/genting-americas-2b-facility-eases-empire-refinancing-risk-but-construction-risks-remain-sp",
    ],
)

ev(
    "2026-07-22",
    "GENM",
    "RWNYC",
    "operations",
    "Resorts World NYC adds 1,400 slots and breaks ground on phase two",
    "Resorts World New York City opened a new gaming floor with 1,400 additional slot machines and an Aristocrat-themed zone, and began phase two of its expansion. The property had about 250 table games after the April launch and was on track for 400 tables by January 2027.",
    "https://www.ggrasia.com/resorts-world-new-york-city-adds-1400-casino-slots-has-phase-two-ground-breaking",
    amount="1,400 slots",
    counterparties=["Genting New York LLC"],
    status="completed",
    sources=[
        "https://www.ggrasia.com/resorts-world-new-york-city-adds-1400-casino-slots-has-phase-two-ground-breaking",
        "https://asgam.com/2026/07/22/gentings-resorts-world-new-york-city-opens-new-gaming-floor-adding-another-1400-slot-machines-and-themed-aristocrat-zone",
    ],
)

ev(
    "2026-08-20",
    "GENTING",
    "GENTING",
    "earnings",
    "Genting swings to 2Q26 net loss as finance costs and forex weigh",
    "Genting Berhad reported a 2Q26 net loss of RM27.1m despite a 14% rise in revenue, as higher finance costs and foreign-exchange losses offset New York growth. Genting Malaysia's borrowings rose 23% year on year as New York casino costs squeezed profit.",
    "https://theedgemalaysia.com/node/815315",
    amount="net loss RM27.1m",
    counterparties=["Genting Berhad"],
    status="completed",
    sources=[
        "https://theedgemalaysia.com/node/815315",
        "https://agbrief.com/news/malaysia/21/08/2026/genting-malaysia-borrowings-rise-23-as-new-york-casino-costs-squeeze-profit",
    ],
)

ev(
    "2026-08-25",
    "GENM",
    "RWNYC",
    "regulatory_tax",
    "Queens lawmakers urge Hochul to resolve 72% Resorts World tax dispute",
    "Ten Queens Democratic lawmakers signed a letter asking Governor Kathy Hochul and the New York State Gaming Commission to clarify that Resorts World's 56% tax rate includes racing-support payments, saying the effective 72% rate threatens the expansion. The letter followed reports that the dispute could end up in court.",
    "https://nypost.com/2026/08/31/us-news/dems-push-hochul-to-block-staggering-72-tax-rate-slapped-on-nycs-first-full-casino/",
    amount="56% vs 72% effective tax",
    counterparties=["New York State Gaming Commission", "Kathy Hochul", "Genting New York LLC"],
    status="ongoing",
    sources=[
        "https://nypost.com/2026/08/31/us-news/dems-push-hochul-to-block-staggering-72-tax-rate-slapped-on-nycs-first-full-casino/",
        "https://www.playusa.com/news/queens-dems-push-hochul-resolve-rwnyc-dispute/",
    ],
)

ev(
    "2026-09-04",
    "GENM",
    "RWNYC",
    "legal",
    "Resorts World NYC faces 4 September deadline for legal challenge over tax",
    "New York Focus reported that Resorts World New York City faced a 4 September 2026 deadline to file a legal challenge over whether its 56% tax rate includes racing-support payments. The dispute remained unresolved and Governor Hochul's administration had not budged; no court filing by Resorts World was located in this collection as of 2 November 2026.",
    "https://nysfocus.com/2026/09/04/resorts-world-nyc-casino-tax-expansion",
    amount=">US$500m at stake",
    counterparties=["New York State Gaming Commission", "Genting New York LLC"],
    status="unresolved",
    notes="No public court filing found; status is 'deadline passed, dispute unresolved'.",
    sources=["https://nysfocus.com/2026/09/04/resorts-world-nyc-casino-tax-expansion"],
)

ev(
    "2026-09-07",
    "GENTING",
    "GENTING",
    "credit_rating",
    "Fitch downgrades Genting Berhad to BBB- and RWLV to BB+",
    "Fitch Ratings downgraded Genting Berhad's long-term issuer default rating to BBB- from BBB, Genting Overseas Holdings to BBB- from BBB, and Resorts World Las Vegas to BB+ from BBB-, with stable outlooks. Fitch expected Genting's EBITDA net leverage to stay above 4.0x for three years because of capex in Singapore and New York and a slower New York ramp-up.",
    "https://theedgemalaysia.com/node/817109",
    amount="GENT BBB -> BBB-; RWLV BBB- -> BB+",
    counterparties=["Fitch Ratings", "Genting Overseas Holdings Ltd", "Resorts World Las Vegas LLC"],
    status="completed",
    sources=[
        "https://theedgemalaysia.com/node/817109",
        "https://www.fitchratings.com/research/corporate-finance/fitch-downgrades-genting-berhad-to-bbb-resorts-world-las-vegas-to-bb-outlooks-stable-07-09-2026",
        "https://www.thestar.com.my/business/business-news/2026/09/08/fitch-downgrades-genting-to-bbb-",
    ],
)

ev(
    "2026-09-08",
    "GENM",
    "GENM",
    "credit_rating",
    "Fitch downgrades Genting Malaysia to BBB-",
    "Fitch downgraded Genting Malaysia's long-term issuer default rating to BBB- from BBB, with a stable outlook, following the parent's downgrade. It also cut the rating on GENM's US$1b senior unsecured notes due 2031 to BBB- from BBB and affirmed Genting New York LLC at BBB-.",
    "https://www.thestar.com.my/business/business-news/2026/09/08/fitch-downgrades-genting-malaysia-to-039bbb-039",
    amount="GENM BBB -> BBB-",
    counterparties=["Fitch Ratings", "Genting New York LLC"],
    status="completed",
    sources=[
        "https://www.thestar.com.my/business/business-news/2026/09/08/fitch-downgrades-genting-malaysia-to-039bbb-039",
        "https://www.fitchratings.com/research/corporate-finance/fitch-downgrades-genting-malaysia-to-bbb-affirms-genting-new-york-at-bbb-outlooks-stable-07-09-2026",
    ],
)

ev(
    "2026-09-08",
    "GENTING",
    "GENTING",
    "credit_rating",
    "S&P warns Genting has 'no more buffer' and faces fallen-angel risk",
    "S&P Global Ratings said Genting had no buffer for further earnings disappointment, with FFO/debt expected at 15-17% through 2028 versus a 20% downside trigger. Genting and several subsidiaries were rated BBB- with a negative outlook, the lowest investment-grade level, leaving a real risk of becoming a fallen angel. S&P did not change the rating in this report.",
    "https://www.ggrasia.com/genting-group-faces-fallen-angel-risk-no-more-buffer-for-earnings-downside-sp",
    amount="BBB- negative; FFO/debt 15-17%",
    counterparties=["S&P Global Ratings"],
    status="ongoing",
    sources=[
        "https://www.ggrasia.com/genting-group-faces-fallen-angel-risk-no-more-buffer-for-earnings-downside-sp",
        "https://asgam.com/2026/09/08/sp-global-expansion-costs-subdued-operational-performance-place-genting-bhd-at-risk-of-becoming-a-fallen-angel/",
    ],
)

ev(
    "2026-09-14",
    "GENM",
    "RWLV",
    "legal",
    "Former RWLV compliance director files AML whistleblower lawsuit",
    "Preston Banks, a former compliance director at Resorts World Las Vegas, sued in US District Court on 14 September 2026 alleging whistleblower retaliation under the Anti-Money Laundering Act and wrongful termination under Nevada law. He claimed he was fired after reporting suspicious activity by a group of foreign patrons and that a report shown to regulators omitted material details. RWLV called the suit frivolous and denied the allegations.",
    "https://focusgn.com/former-resorts-world-las-vegas-compliance-director-sues-over-alleged-whistleblower-firing",
    amount="double back pay, compensatory and punitive damages sought",
    counterparties=["Preston Banks", "Resorts World Las Vegas LLC"],
    status="ongoing",
    sources=[
        "https://focusgn.com/former-resorts-world-las-vegas-compliance-director-sues-over-alleged-whistleblower-firing",
        "https://globalgaminginsider.com/news/7272/resorts-world-las-vegas-faces-whistleblower-lawsuit-over-aml-concerns",
    ],
)

ev(
    "2026-09-17",
    "GENM",
    "GENM",
    "buyback",
    "Genting Malaysia resumes share buybacks",
    "Genting Malaysia bought 200,000 shares at RM1.50 on 17 September 2026, its first buyback under the mandate renewed at the 10 June 2026 AGM, lifting treasury shares to 270,502,915 (4.55542% of issued shares). It bought a further 550,000 shares at RM1.26-1.27 on 12 October 2026, taking treasury to 271,052,915 (4.56468%).",
    KL + "11669007",
    amount="750,000 shares; ~RM1.0m",
    counterparties=["shareholders"],
    status="completed",
    sources=[KL + "11669007", KL + "11683189", KL + "11689761"],
)

ev(
    "2026-09-29",
    "GENTING",
    "GENTING",
    "insider_buying",
    "Genting CEO Tan Kong Han starts buying shares after price fall",
    "Dato' Sri Tan Kong Han bought 200,000 Genting Berhad shares at RM1.87 on 29 September 2026, his first purchase in the latest run. He continued buying through October at RM1.34-1.58, taking his direct holding from 1,290,000 at end-2025 to 2,540,000 by 23 October 2026.",
    KL + "11676081",
    amount="1,250,000 shares; ~RM1.9m",
    counterparties=["Dato' Sri Tan Kong Han"],
    status="completed",
    sources=[
        KL + "11676081",
        KL + "11683945",
        KL + "11685125",
        KL + "11687681",
        KL + "11688051",
        KL + "11689045",
        KL + "11691613",
    ],
)

ev(
    "2026-10-09",
    "GENTING",
    "GENTING",
    "rights_issue",
    "Genting proposes RM1.25b renounceable rights issue to repay debt",
    "Genting Berhad proposed a renounceable rights issue to raise about RM1.25b, its first equity fundraising since 1973. The proceeds were earmarked for RM800m of debt repayment (about RM41.3m annual interest savings), RM429.5m of working capital (including RM280m for interest and financing costs) and RM20.5m of expenses. The issue price and entitlement basis were not fixed; the board intended a 25-30% discount to TERP, subject to shareholder approval at an EGM.",
    KL + "11682541",
    amount="RM1.25b gross; RM800m debt repayment",
    counterparties=["shareholders", "AmInvestment Bank", "Kien Huat Realty", "Kien Huat International", "Dato' Indera Lim Keong Hui"],
    status="proposed",
    sources=[
        KL + "11682541",
        "https://theedgemalaysia.com/node/821263",
    ],
    notes="Official PDF saved as data/company_docs/GENT_RightsIssue_2026-10-09.pdf; URL above is the Bursa attachment pattern, verify.",
)

ev(
    "2026-10-12",
    "GENTING",
    "GENTING",
    "market_reaction",
    "Genting shares plunge 23% on rights issue; Maybank cuts to Sell",
    "Genting Berhad shares fell 43 sen, or 22.87%, to RM1.45 on 12 October 2026, the lowest since April 2007, wiping over RM1.6b of market value, after the RM1.25b rights issue was announced. Genting Malaysia fell 17.45% to RM1.23. Bursa suspended intraday short selling in both counters. Maybank Investment Bank downgraded Genting to Sell from Buy and cut its target price to RM1.49 from RM2.88; CIMB Securities flagged up to 18% EPS dilution.",
    "https://theedgemalaysia.com/node/821415",
    amount="-22.87% to RM1.45",
    counterparties=["Maybank Investment Bank", "CIMB Securities"],
    status="completed",
    sources=[
        "https://theedgemalaysia.com/node/821415",
        "https://www.thestar.com.my/business/business-news/2026/10/13/genting-loses-rm16bil-in-market-value-after-cash-call",
        "https://www.freemalaysiatoday.com/category/business/2026/10/12/genting-shares-tumble-most-since-1998-on-rights-issue-plan",
    ],
)

ev(
    "2026-10-12",
    "GENTING",
    "GENTING",
    "insider_buying",
    "Kien Huat buys 6m Genting shares at RM1.494 on crash day",
    "Kien Huat Realty Sdn Berhad bought 6,000,000 Genting Berhad shares at RM1.494 each on 12 October 2026, the day of the 23% rights-issue sell-off. It added 270,000 shares at RM1.39185 on 14 October and 152,500 at RM1.45 on 15 October, lifting the Lim family's deemed stake to 45.239%.",
    KL + "11684741",
    amount="6,422,500 shares; ~RM9.55m",
    counterparties=["Kien Huat Realty Sdn Berhad", "Parkview Management Sdn Bhd"],
    status="completed",
    sources=[KL + "11684741", KL + "11684749", KL + "11686057", KL + "11686075"],
)

ev(
    "2026-10-14",
    "GENTING",
    "GENTING",
    "rights_issue",
    "Genting defends 25-30% rights discount in Bursa query reply",
    "Responding to Bursa Malaysia's query, Genting said the 25-30% discount to TERP was set after considering the issue size, market conditions, liquidity, comparable rights issues, underwriting appetite and the need to incentivise participation. It confirmed the working-capital breakdown: RM280m for interest and financing costs and RM149.5m for general working capital, within the RM429.5m total.",
    KL + "11684683",
    amount="25-30% discount; RM280m interest",
    counterparties=["Bursa Malaysia", "AmInvestment Bank"],
    status="completed",
    sources=[KL + "11684683"],
)

ev(
    "2026-10-23",
    "GENTING",
    "GENTING",
    "rights_issue",
    "Genting submits listing application for RM1.25b rights shares",
    "Genting submitted an application to Bursa Malaysia for the listing and quotation of the rights shares, a procedural step after the 9 and 14 October announcements. The issue price, entitlement basis and entitlement date remained unfixed, and no EGM notice or shareholder-approval outcome had been announced.",
    KL + "11690197",
    amount="RM1.25b",
    counterparties=["Bursa Malaysia", "AmInvestment Bank"],
    status="pending",
    sources=[KL + "11690197", KL + "11682541"],
)

ev(
    "2026-10-29",
    "GENTING",
    "GENTING",
    "governance",
    "Genting says no further equity fundraising currently planned",
    "In a reply to The Edge, Genting Berhad said 'No further equity fundraising is currently planned by the company' after the RM1.25b rights issue. The statement followed a 24% share-price fall over 10 days and analyst concerns about more cash calls and dividend cuts. The company also said RM800m of the proceeds would repay debt and the balance would fund working capital.",
    "https://theedgemalaysia.com/node/822667",
    amount="RM1.25b rights issue",
    counterparties=["The Edge Malaysia"],
    status="announced",
    sources=[
        "https://theedgemalaysia.com/node/822667",
        "https://theedgemalaysia.com/node/822639",
        "https://www.businesstoday.com.my/2026/10/19/genting-share-price-dives-24-in-last-10-days-as-rights-issue-raises-cash-flow-concerns",
    ],
)


ev(
    "2025-02-27",
    "GENM",
    "GENM",
    "dividend",
    "Genting Malaysia declares FY2024 final dividend of 4.0 sen",
    "Genting Malaysia declared a final single-tier dividend of 4.0 sen per share for FY2024, with ex-date 17 March 2025 and payment on 10 April 2025. FY2024's total was 10.0 sen (6.0 sen interim plus 4.0 sen final); The FY2025 final was later set at 7.0 sen.",
    GENM_AR25,
    amount="RM226.7m (4.0 sen/share)",
    counterparties=["shareholders"],
    status="completed",
    sources=[GENM_AR25],
    notes="AR2025 dividend table; exact payment amount based on 5,667,741,733 shares excluding treasury.",
)

ev(
    "2025-04-11",
    "GENM",
    "GENM",
    "annual_report",
    "Genting Malaysia files FY2024 annual report",
    "Genting Malaysia submitted its FY2024 Integrated Annual Report, disclosing a 49.33% Genting Berhad stake, 270,302,915 treasury shares, 5,667,741,733 shares outstanding and a 49.35% Lim-family deemed interest. The report also detailed the 45th AGM notice and the FY2024 dividend.",
    GENM_AR24,
    counterparties=["shareholders"],
    status="completed",
    sources=[GENM_AR24, KL + "9434623"],
)

ev(
    "2025-04-25",
    "GENTING",
    "GENTING",
    "annual_report",
    "Genting Berhad files FY2024 annual report",
    "Genting Berhad submitted its FY2024 Integrated Annual Report, disclosing a 43.587% Kien Huat Realty stake, a 44.837% Lim-family deemed interest, 26,320,000 treasury shares, 3,850,576,099 shares outstanding and a 49.3% Genting Malaysia stake. The report was the last annual snapshot before the GENM takeover.",
    GENT_AR24,
    counterparties=["shareholders"],
    status="completed",
    sources=[GENT_AR24, KL + "9562939"],
)

ev(
    "2025-12-03",
    "GENM",
    "GENM",
    "analyst_action",
    "HLIB raises Genting Malaysia FY26/27 earnings forecasts after NY licence",
    "Hong Leong Investment Bank raised its Genting Malaysia FY2026/FY2027 earnings forecasts by 21.3%/23.7% to reflect expected contributions from Resorts World New York City after the group was selected for a full downstate casino licence. The note was positive on the New York first-mover advantage.",
    "https://www.businesstoday.com.my/2025/12/03/hlib-raises-genms-fy26-27-earnings-forecast",
    amount="FY26/27 forecasts +21.3%/+23.7%",
    counterparties=["Hong Leong Investment Bank", "Genting Malaysia Berhad"],
    status="completed",
    sources=["https://www.businesstoday.com.my/2025/12/03/hlib-raises-genms-fy26-27-earnings-forecast"],
)

ev(
    "2025-12-04",
    "GENTING",
    "GENTING",
    "analyst_action",
    "Nomura says taking Genting Malaysia private remains 'complex'",
    "Nomura said it remained 'complex' for Genting Berhad to take Genting Malaysia private despite on-market share purchases, noting the 75% threshold, the 2% purchase cap after a lapsed offer and the need for a shareholder vote. The note followed the takeover's close at 73.13%.",
    "https://www.ggrasia.com/complex-for-genting-bhd-to-take-gen-malaysia-private-despite-on-market-share-buys-nomura",
    amount="73.13% stake; 75% threshold",
    counterparties=["Nomura", "Genting Malaysia Berhad"],
    status="completed",
    sources=["https://www.ggrasia.com/complex-for-genting-bhd-to-take-gen-malaysia-private-despite-on-market-share-buys-nomura"],
)

ev(
    "2026-03-01",
    "GENTING",
    "GENTING",
    "analyst_action",
    "Kenanga keeps Genting at Outperform on FY26-27 recovery",
    "Kenanga Investment Bank maintained an Outperform call on Genting Berhad, citing the New York casino licence, plantation earnings and a recovery in Malaysian gaming. The note was one of the few positive calls during the post-takeover de-rating.",
    "https://www.businesstoday.com.my/2026/03/01/kenanga-bets-on-genting-to-outperform-in-fy26-27",
    amount="Outperform",
    counterparties=["Kenanga Investment Bank"],
    status="completed",
    sources=["https://www.businesstoday.com.my/2026/03/01/kenanga-bets-on-genting-to-outperform-in-fy26-27"],
)

ev(
    "2026-04-02",
    "GENTING",
    "GENTING",
    "ownership_change",
    "Genting Berhad's GENM stake reaches 73.888%",
    "Genting Berhad bought 1,000,000 GENM shares on 30-31 March 2026, lifting its direct stake to 4,186,582,953 shares or 73.867%; the Lim family's deemed interest reached 4,187,785,983 shares or 73.888%. It was the last open-market GENM purchase disclosed in the window, leaving the group 1.1 percentage points short of 75%.",
    KL + "11371165",
    amount="73.888% deemed",
    counterparties=["Genting Malaysia Berhad"],
    status="completed",
    sources=[KL + "11371165", KL + "11371151", KL + "11371155"],
)

ev(
    "2026-04-16",
    "GENM",
    "GENM",
    "annual_report",
    "Genting Malaysia files FY2025 annual report",
    "Genting Malaysia submitted its FY2025 Integrated Annual Report, disclosing a 73.8383% Genting Berhad stake, 270,302,915 treasury shares, 5,667,741,733 shares outstanding and a 73.8596% Lim-family deemed interest. The report also disclosed the US$300m Empire notes due November 2026 and the US$2b Genting Americas facility.",
    GENM_AR25,
    counterparties=["shareholders"],
    status="completed",
    sources=[GENM_AR25, KL + "11539849"],
)

ev(
    "2026-08-24",
    "GENTING",
    "GENTING",
    "analyst_action",
    "CGS International cuts Genting to Hold, target RM2.45",
    "CGS International Securities Malaysia maintained a Hold on Genting Berhad but cut FY2026-FY2028 earnings forecasts by 9-13% and lowered its sum-of-parts target price to RM2.45, applying a 20% holding-company discount. It said a renewed GENM privatisation would depend on a convincing Resorts World New York turnaround.",
    "https://www.nst.com.my/business/corporate/2026/08/1517573/genting-privatisation-hinges-resorts-world-new-york-turnaround",
    amount="TP RM2.45; FY26-28 cuts 9-13%",
    counterparties=["CGS International Securities Malaysia"],
    status="completed",
    sources=["https://www.nst.com.my/business/corporate/2026/08/1517573/genting-privatisation-hinges-resorts-world-new-york-turnaround"],
)

ev(
    "2026-09-06",
    "GENM",
    "RWNYC",
    "financing",
    "Genting says financing in place for US$5.5b New York expansion",
    "Genting said financing was in place for the US$5.5b Resorts World New York City expansion, including the US$2b Genting Americas facility secured in July 2026. The group had spent about US$700m of the remaining US$4.4b commitment, including the licence fee, and planned to deploy the rest over five years.",
    "https://agbrief.com/news/usa/06/09/2026/genting-says-financing-in-place-for-5-5b-resorts-world-new-york-expansion-report",
    amount="US$5.5b; US$2b facility",
    counterparties=["Genting New York LLC", "Genting Americas Inc", "bank lenders"],
    status="announced",
    sources=["https://agbrief.com/news/usa/06/09/2026/genting-says-financing-in-place-for-5-5b-resorts-world-new-york-expansion-report"],
)

ev(
    "2026-09-08",
    "GENTING",
    "GENTING",
    "divestment",
    "Genting completes 5% PT Layar sale, retains 95% of Indonesian LNG unit",
    "Genting Berhad completed the sale of a 5% stake in PT Layar Nusantara Gas, the operator of its Indonesian floating LNG project, to a Rukun Raharja unit, retaining a 95% stake. The divestment was part of the group's non-core asset sales to support deleveraging.",
    "https://www.theedgemalaysia.com/node/817267",
    amount="5% stake (price not disclosed in headline)",
    counterparties=["PT Layar Nusantara Gas", "Rukun Raharja"],
    status="completed",
    sources=[
        "https://www.theedgemalaysia.com/node/817267",
        "https://www.nst.com.my/business/corporate/2026/09/1528398/genting-completes-pt-layar-divestment-retains-95pct-stake",
    ],
)

ev(
    "2026-10-13",
    "GENTING",
    "GENTING",
    "analyst_action",
    "CreditSights: rights issue positive but asset sales still needed",
    "CreditSights called the RM1.25b rights issue a positive but small step towards deleveraging, estimating it would reduce pro-forma net leverage by only 0.2-0.3x to about 4.3x. It said non-core asset sales, notably unused Miami land, would be the main tool to stave off downgrade risk, and expected no further debt-funded GENM stake purchases for 12-18 months.",
    "https://www.theedgemalaysia.com/node/821593",
    amount="leverage reduction 0.2-0.3x",
    counterparties=["CreditSights", "Genting Berhad"],
    status="completed",
    sources=[
        "https://www.theedgemalaysia.com/node/821593",
        "https://www.ggrasia.com/genting-bhd-asset-sales-key-despite-us306mln-rights-issue-creditsights",
    ],
)

# Add Pahang / Malaysia casino licence status note as a dated regulatory baseline.
ev(
    "2026-04-17",
    "GENM",
    "MALAYSIA",
    "regulatory_licence",
    "Malaysia casino licence remains a three-monthly renewal; no specific renewal announcement in window",
    "Genting Malaysia's FY2025 annual report states that casino licences are renewed periodically under local regulation and that in Malaysia the casino licence is renewable every three months. No specific Bursa announcement of a Malaysian casino-licence renewal, renewal fee or conditions was found in the 2 November 2024-2 November 2026 window; Resorts World Genting continued to operate as Malaysia's sole licensed casino.",
    GENM_AR25,
    amount=None,
    counterparties=["Ministry of Finance Malaysia", "Pahang State Government"],
    status="routine",
    confidence="medium",
    notes="Status is inferred from the absence of a specific announcement plus the AR's standing disclosure; not a renewal event.",
)


def epoch(d: str) -> int:
    y, m, dd = map(int, d.split("-"))
    return int(datetime(y, m, dd, tzinfo=timezone.utc).timestamp())


def native_id(e: dict) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in e["title"])
    slug = "-".join(x for x in slug.split("-") if x)[:60].rstrip("-")
    return f"company_event:{e['date']}:{slug}"


def write_events() -> None:
    path = OUT / "company_events.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for e in sorted(EVENTS, key=lambda x: (x["date"], x["ticker"], x["title"])):
            rec = {
                "record_type": "post",
                "source": "company_event",
                "channel": e["channel"],
                "native_id": native_id(e),
                "ticker": e["ticker"],
                "title": e["title"],
                "author": None,
                "author_id": None,
                "created_utc": epoch(e["date"]),
                "url": e["url"],
                "body": e["body"],
                "score": None,
                "num_comments": None,
                "lang": "en",
                "raw": {
                    "event_type": e["event_type"],
                    "amount": e["amount"],
                    "counterparties": e["counterparties"],
                    "status": e["status"],
                    "date": e["date"],
                    "time_precision": "day",
                    "time_text": e["date"],
                    "sources": e["sources"],
                    "notes": e["notes"],
                    "confidence": e["confidence"],
                },
            }
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"wrote {len(EVENTS)} events -> {path}")


if __name__ == "__main__":
    write_events()
