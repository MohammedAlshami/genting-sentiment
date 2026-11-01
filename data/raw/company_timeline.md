# Genting: ownership, governance, corporate events and legal timeline

**Scope:** Genting Berhad (`GENTING`, Bursa 3182) and Genting Malaysia Berhad (`GENM`, Bursa 4715), 2 November 2024 to 2 November 2026. This is a source-backed event timeline, not a sentiment score. Each fact carries a date and a link; where sources conflict, the conflict is flagged in [`company_events_report.md`](company_events_report.md).

**Primary sources:** Bursa Malaysia announcements via the KLSE Screener mirror; Genting Berhad's [FY2025](https://www.genting.com/wp-content/uploads/2026/07/GENTING-BERHAD_IAR2025v2.pdf) and [FY2024](https://www.genting.com/wp-content/uploads/2025/05/GENTING_IAR24v3.pdf) Integrated Annual Reports; Genting Malaysia's FY2025 and FY2024 annual reports (Bursa links in the report); US court filings; contemporaneous news. Full details are in `data/raw/company_events.jsonl`, `data/raw/ownership.jsonl` and `data/raw/company_structure.json`.

---

## 1. Ownership snapshot: the Lim family controls Genting, Genting controls GENM

The control chain is a discretionary trust, not a single family block:

```
Parkview Management Sdn Bhd (trustee)
        │ 100% of voting shares
        ▼
Kien Huat International Limited (KHI)
        │ 100% of voting shares
        ▼
Kien Huat Realty Sdn Berhad (KHR)
        │ 43.822% direct  ┐
        │                  ├── 45.072% deemed Lim-family interest in GENT
KHI ────┘ 1.250% direct  ┘
        │
        ▼
Genting Berhad (GENTING, 3182)
        │ 73.838% direct
        ▼
Genting Malaysia Berhad (GENM, 4715)
```

Genting Berhad also owns **55.4% of Genting Plantations Berhad** and **52.6% of Genting Singapore Limited**; those are siblings of GENM, not GENM subsidiaries. The structure is set out in the FY2025 annual report's group corporate structure ([GENT AR2025, p. 20](https://www.genting.com/wp-content/uploads/2026/07/GENTING-BERHAD_IAR2025v2.pdf#page=28)) and the shareholding sections ([pp. 257–259](https://www.genting.com/wp-content/uploads/2026/07/GENTING-BERHAD_IAR2025v2.pdf#page=265)).

| Holder | Basis | 15 Apr 2025 | 18 Mar 2026 | 16 Oct 2026 |
|---|---|---:|---:|---:|
| Kien Huat Realty Sdn Berhad | direct GENT | 43.587% | 43.822% | 43.989% |
| Kien Huat International Limited | direct GENT | 1.250% | 1.250% | 1.250% |
| Parkview Management Sdn Bhd (trustee) | deemed GENT | 44.837% | 45.072% | 45.239% |
| Tan Sri Lim Kok Thay | deemed GENT | 44.837% | 45.072% | 45.239% |
| Dato' Indera Lim Keong Hui | direct / deemed GENT | 0.033% / 44.837% | 0.033% / 45.072% | 0.033% / 45.239% |

Sources: [GENT FY2024 AR pp. 227–228](https://www.genting.com/wp-content/uploads/2025/05/GENTING_IAR24v3.pdf); [GENT FY2025 AR p. 258](https://www.genting.com/wp-content/uploads/2026/07/GENTING-BERHAD_IAR2025v2.pdf#page=266); Bursa notices dated [14 October 2026](https://www.klsescreener.com/v2/announcements/view/11684741) and [16 October 2026](https://www.klsescreener.com/v2/announcements/view/11686057).

The family's GENT stake rose from **44.84% in April 2025 to 45.24% in October 2026**. That is a small percentage move but a large share purchase: KHR bought about **47.2 million GENT shares** from January 2025 to October 2026. The most visible purchases were:

- **16 October 2025:** 3,000,000 shares at **RM3.48112**.
- **17 October 2025:** 3,421,200 shares at **RM3.37029**.
- **27–28 October 2025:** 628,500 + 2,000,000 shares, taking the family to 45.072% ([notice](https://www.klsescreener.com/v2/announcements/view/10579497)).
- **12 October 2026:** 6,000,000 shares at **RM1.494**, on the day of the rights-issue crash, plus 270,000 at **RM1.39185** and 152,500 at **RM1.45** on 14–15 October 2026 ([notice](https://www.klsescreener.com/v2/announcements/view/11684741); [director notice](https://www.klsescreener.com/v2/announcements/view/11684749)).

At GENM, Genting Berhad's direct stake moved from **49.33%** at the FY2024 annual-report date ([GENM FY2024 AR p. 180](https://www.klsescreener.com/v2/announcements/view/9434623)) to **73.8383%** at the FY2025 date ([GENM FY2025 AR p. 186](https://www.klsescreener.com/v2/announcements/view/11539849)), then **73.867% direct / 73.888% deemed** after the last purchase on 2 April 2026 ([notice](https://www.klsescreener.com/v2/announcements/view/11371165)).

| GENM ownership | 17 Mar 2025 | 1 Dec 2025 | 16 Mar 2026 | 2 Apr 2026 |
|---|---:|---:|---:|---:|
| Genting Berhad direct | 49.33% | 73.13% | 73.8383% | 73.867% |
| KHR direct | 0.0212% | 0.0212% | 0.0212% | 0.0212% |
| KHI / PMSB deemed | 49.35% | 73.86% | 73.8595% | 73.888% |
| Lim Kok Thay / Lim Keong Hui deemed | 49.3493% | 73.86% | 73.8596% | 73.888% |

**Treasury and free float.** GENT had **3,876,896,099** issued shares, **26,320,000** treasury shares and **3,850,576,099** shares outstanding at 31 December 2025. It bought no treasury shares in FY2024 or FY2025 ([GENT AR2025 Note 34](https://www.genting.com/wp-content/uploads/2026/07/GENTING-BERHAD_IAR2025v2.pdf)). GENM had **5,938,044,648** issued shares, **270,302,915** treasury shares and **5,667,741,733** shares outstanding at 31 December 2025 ([GENM AR2025 Note 34](https://www.klsescreener.com/v2/announcements/view/11539849)). GENM resumed buybacks in September 2026, taking treasury to **271,052,915** shares (4.56468%) by 12 October 2026 ([announcement](https://www.klsescreener.com/v2/announcements/view/11683189)).

Calculated free float at the FY2025 annual-report date was approximately **54.93% for GENT** and **26.14% for GENM**. GENM is therefore close to the 25% Bursa public-spread floor, which matters for any further parent buying or a renewed privatisation attempt.

---

## 2. November 2024 – April 2025: quiet accumulation, a Nevada fine and a management succession

**22 November 2024 — Genting Americas moves to dismiss a US$600m Bahamas claim.** RAV Bahamas Ltd, owner of 22% of RW Bimini operator BB Entertainment Ltd, sued Genting Americas Inc in the Southern District of Florida over the operations of RW Bimini, seeking more than **US$600m**. Genting Americas filed a motion to dismiss, arguing the dispute belonged in arbitration and the claims were time-barred. Mediation in May 2025 failed; the court dismissed the complaint with leave to amend on 1 July 2025, and RAV filed an amended complaint on 29 July 2025 ([GENT AR2025, Note 47, pp. 218–219](https://www.genting.com/wp-content/uploads/2026/07/GENTING-BERHAD_IAR2025v2.pdf#page=226)). The case remained pending at the annual-report date.

**27 February 2025 — Genting cuts its FY2024 dividend.** GENT declared a **5.0 sen** final single-tier dividend for FY2024, paid 16 April 2025. Together with the 6.0 sen interim, the FY2024 total was **11.0 sen**, down from **15.0 sen** in 2023 and far below the **22.0 sen** paid in 2019; the bigger halving came with FY2025's **5.0 sen** total ([announcement](https://www.klsescreener.com/v2/announcements/view/9161089); [GENT AR2025](https://www.genting.com/wp-content/uploads/2026/07/GENTING-BERHAD_IAR2025v2.pdf); [The Edge](https://theedgemalaysia.com/node/822639)). GENM declared a **4.0 sen** final for FY2024, paid 10 April 2025, for a FY2024 total of **10.0 sen** ([GENM AR2025 dividend table](https://www.klsescreener.com/v2/announcements/view/11539849)). The payout cut is an important background variable for retail sentiment: Genting had long been held as an income stock, and the FY2024–FY2025 reductions broke that pattern.

**27 February 2025 — Lim Kok Thay hands the CEO role to Tan Kong Han.** Effective 1 March 2025, Tan Sri Lim Kok Thay was redesignated **Executive Chairman** from Chief Executive Officer, and Dato' Sri Tan Kong Han became **Chief Executive Officer** from Executive Director ([Lim notice](https://www.klsescreener.com/v2/announcements/view/9161073); [Tan notice](https://www.klsescreener.com/v2/announcements/view/9161079)). Independent director **Eric Ooi Lip Aun** resigned the same day for personal reasons ([notice](https://www.klsescreener.com/v2/announcements/view/9161103)). The split separated the family's chairman role from day-to-day management for the first time in decades.

**7 March – 10 April 2025 — Kien Huat's GENT buying becomes visible.** A substantial-shareholder notice showed KHR at **42.816%** on 7 March 2025 ([notice](https://www.klsescreener.com/v2/announcements/view/9186625)); by 10 April 2025 it held **43.587%**, or 1,678,348,910 shares, and the Lim family's deemed interest was **44.837%** ([notice](https://www.klsescreener.com/v2/announcements/view/9412051)). This was the opening leg of the accumulation that preceded the GENM takeover.

**27 March 2025 — Nevada approves a US$10.5m fine against Resorts World Las Vegas.** The Nevada Gaming Commission approved a stipulated settlement and **US$10.5m** fine against RWLV and parent Genting Berhad over anti-money-laundering failures and dealings with illegal bookmakers. It was the second-largest fine in Nevada gaming history at the time ([NST](https://www.nst.com.my/business/corporate/2025/03/1191412/genting-paying-nevada-gaming-commission-us105mil-settle-las-vegas); [iGaming Business](https://igamingbusiness.com/casino/land-based-casino-regulation/resorts-world-nevada-fine-approved/)). The penalty became a reference point for the later civil RICO and whistleblower suits.

---

## 3. May – September 2025: buying Empire Resorts from the family, and the RAV litigation

**31 May 2025 — GENM completes the Empire Resorts buyout.** Genting Malaysia bought the remaining **51%** of Genting Empire Resorts LLC from **Kien Huat Realty III Limited**, a Lim-family vehicle, for **US$41m cash plus about US$40m of assumed debt**. Empire Resorts Inc became an indirect wholly owned subsidiary ([The Edge](https://theedgemalaysia.com/node/753817); [ASGAM](https://asgam.com/2025/06/04/genting-malaysia-completes-full-acquisition-of-troubled-us-entity-empire-resorts/); [GENM AR2025 Note 44(b)(vii)](https://www.klsescreener.com/v2/announcements/view/11539849)). Bursa Malaysia queried the related-party deal, and the group replied on 8 May 2025 ([reply](https://www.klsescreener.com/v2/announcements/view/9663623)). The transaction is a governance marker: it bought a loss-making US business from the controlling family, and it preceded the New York casino licence win that made Empire strategically more valuable.

**11–12 June 2025 — AGMs approve the usual mandates.** GENM's 45th AGM approved **nine** ordinary resolutions, including directors' fees of **RM1,904,098** for FY2024 and renewal of the buy-back authority ([announcement](https://www.klsescreener.com/v2/announcements/view/9784091)). GENT's 57th AGM approved **eight** resolutions, including directors' fees of **RM1,636,290**, re-election of Lim Kok Thay and Manharlal Ratilal, and renewal of the buy-back mandate ([announcement](https://www.klsescreener.com/v2/announcements/view/9788741)).

**1 July – 12 September 2025 — RAV Bahamas litigation continues.** The Florida court granted Genting Americas' motion to dismiss RAV's complaint with leave to amend on 1 July 2025. RAV filed an amended complaint on 29 July 2025, and Genting Americas moved to dismiss that on 12 September 2025 ([GENT AR2025, Note 47](https://www.genting.com/wp-content/uploads/2026/07/GENTING-BERHAD_IAR2025v2.pdf#page=226)). The dispute stayed out of the headlines relative to the New York licence, but it remained a contingent US legal risk.

**15 August 2025 — Empire announces a US$525m recapitalisation.** GENM proposed the **US$525m** sale of Empire's non-gaming assets at Resorts World Catskills to Sullivan County Resort Facilities Local Development Corp, with proceeds to redeem Empire's **US$300m 7.75%** notes due 1 November 2026 ([announcement](https://www.klsescreener.com/v2/announcements/view/11625481)). The proposal was later withdrawn after Empire repaid the notes in July 2026.

---

## 4. October – December 2025: the RM2.35 takeover, the New York licence and the rating downgrades

This is the densest period in the dataset and the most likely source of retail-sentiment shocks.

### 4.1 The offer

On **13 October 2025**, Genting Berhad launched a conditional voluntary takeover offer for all **2,870,039,874** GENM shares it did not own — **50.64%** of GENM excluding treasury — at **RM2.35 cash per share**, valuing the minority at about **RM6.745b (US$1.59b)**. Genting said it wanted statutory control and did not intend to maintain GENM's listing if sufficient acceptances were received. Trading in both counters was suspended for the announcement ([announcement](https://www.klsescreener.com/v2/announcements/view/10518319); [offer document](https://www.klsescreener.com/v2/announcements/view/10597715)).

The offer became **unconditional on 3 November 2025** after open-market purchases took Genting above **50.00%** ([announcement](https://www.klsescreener.com/v2/announcements/view/10598787)). The stake then moved quickly:

| Date | GENT stake in GENM | Trigger |
|---|---:|---|
| Pre-offer (3 Nov filing) | 49.36% | starting point |
| 10 Nov 2025 | 52.63% | open-market purchases + acceptances |
| 13 Nov 2025 | ~57.0% | 2.02% open-market purchases triggered mandatory offer; acceptances added |
| 19 Nov 2025 | 60.609% direct | acceptances |
| 1 Dec 2025 | 73.13% | offer close |
| 13 Mar 2026 | 73.838% | post-offer open-market purchases |
| 2 Apr 2026 | 73.867% direct / 73.888% deemed | last purchase before rights issue |

Sources: [52.63%](https://www.ggrasia.com/genting-bhd-crosses-52pct-ownership-mark-in-genting-malaysia); [57%](https://www.ggrasia.com/genting-bhd-takeover-bid-for-genting-malaysia-now-mandatory-stake-rises-to-57pct); [60.609% notice](https://www.klsescreener.com/v2/announcements/view/10706821); [73.13% close](https://www.klsescreener.com/v2/announcements/view/10728467); [73.838% notice](https://www.klsescreener.com/v2/announcements/view/11302411); [73.888% notice](https://www.klsescreener.com/v2/announcements/view/11371165).

**13 November 2025 — mandatory offer and independent advice.** Genting acquired 34,929,300 GENM shares on 13 November, taking total open-market purchases in the six-month period to **114,469,300 shares (2.02%)**. That triggered a mandatory offer and extended the closing date from 24 November to **1 December 2025** ([announcement](https://www.klsescreener.com/v2/announcements/view/10695835)). GENM's independent adviser recommended shareholders **reject** the RM2.35 offer as **"not fair and not reasonable"**, noting they could sell in the open market and that Genting needed 90% to compulsorily acquire ([independent advice circular](https://www.klsescreener.com/v2/announcements/view/10694735); [The Edge](https://theedgemalaysia.com/node/779551)).

**1 December 2025 — the offer closes at 73.13%, short of 75%.** Genting held **4,144,966,481** GENM shares, or **73.13%** excluding treasury. It fell short of the **75%** threshold needed to delist GENM, so **Genting Malaysia remained listed**. The offer itself completed and acceptances were settled; the privatisation attempt failed ([announcement](https://www.klsescreener.com/v2/announcements/view/10728467); [The Edge](https://theedgemalaysia.com/node/784367); [GGR Asia](https://www.ggrasia.com/genting-malaysia-to-stay-listed-as-parents-stake-was-73pct-at-the-close-of-its-offering)).

Fitch later put the cost of the additional **23.8%** stake at **MYR3.1b** ([GGR Asia](https://www.ggrasia.com/fitch-affirms-genting-bhd-at-investment-grade-but-outlook-is-negative-amid-costs-on-genting-malaysia-downstate-ny-licence)). S&P also used the MYR3.1b figure ([S&P research update](https://www.spglobal.com/ratings/en/regulatory/article/-/view/sourceId/101662684)).

### 4.2 The New York licence

**2 December 2025 — the New York Gaming Facility Location Board selects RWNYC.** The board voted **5-0** to send Genting New York LLC's Resorts World New York City bid, Bally's Bronx and Hard Rock Metropolitan Park to the New York State Gaming Commission for licensure. Genting proposed a **US$5.5b** expansion and a **US$600m upfront licence fee** ([GENM announcement](https://www.klsescreener.com/v2/announcements/view/10730039); [GGR Asia](https://www.ggrasia.com/genting-recommended-for-downstate-new-york-full-casino-licence); [GFLB selection document](https://nycasinos.ny.gov/system/files/documents/2026/03/12.01.25.gflbselectiondocument1.pdf)).

**16 December 2025 — the New York State Gaming Commission awards the full licence.** The commission voted unanimously to award a full commercial casino licence to Genting New York LLC for RWNYC at Aqueduct Racetrack in Queens. Genting said the first phase would open by Q2 2026 ([The Star](https://www.thestar.com.my/business/business-news/2025/12/16/genting-malaysia-gets-the-nod-for-new-york-casino-licence); [NST](https://www.nst.com.my/business/corporate/2025/12/1338105/nyc-casino-licence-approvals-open-door-genting-malaysias-us)). The licence allowed live table games, which launched on **28 April 2026**, and the property opened as a full casino on **1 May 2026** ([GGR Asia](https://www.ggrasia.com/gentings-resorts-world-new-york-city-to-launch-table-games-on-april-28); [The Star](https://www.thestar.com.my/business/business-news/2026/05/01/genting-opens-new-york-casino-creates-history)).

The licence was a double-edged event for sentiment. It removed a long-standing catalyst uncertainty and gave GENM the only near-term full casino in New York City, but it also committed the group to **US$5.5b** of capex and a large licence fee, just as it was taking on debt for the GENM stake. The shares initially fell on the news: GENM closed **4.26% lower at RM2.25** and GENT **2.08% lower at RM3.29** on 2 December 2025 ([The Edge](https://theedgemalaysia.com/node/784489)).

**18 November 2025 — Resorts World asks New York to reconsider the tax rate.** Genting had bid the highest slot tax at **56%**, versus 25% for Hard Rock/Mets and 30% for Bally's, and asked the state to lower its rate or raise rivals' levies ([The Star](https://www.thestar.com.my/business/business-news/2025/11/18/gentings-resorts-world-to-ask-new-york-to-reconsider-casino-tax-rates-after-bid)). The Gaming Facility Location Board later rejected any reduction, a decision that fed the 2026 racing-support dispute ([NY Focus](https://nysfocus.com/2026/06/01/nyc-casino-resorts-world-horseracing-support-tax)).

### 4.3 Ratings and debt

The takeover and the New York commitment triggered a wave of rating actions:

| Date | Agency | Action | Detail |
|---|---|---|---|
| 8 Dec 2025 | Moody's | **Downgrade** | GENT and GOHL **Baa2 → Baa3**; Genting Singapore **A3 → Baa1**; stable outlook. Cited takeover debt and New York spending. |
| 13 Dec 2025 | RAM | **Outlook to negative** | GENT and GENM **AA1** maintained; higher-than-expected 73% GENM stake and RWNYC capex. |
| 17 Dec 2025 | S&P | **Outlook to negative** | Affirmed ratings; estimated 2026 capex would double to ~RM12b and FFO/debt fall below 20%. |
| 22 Dec 2025 | Fitch | **Affirm, outlook negative** | GENT **BBB** affirmed, removed from rating watch negative; GENM/GOHL/RWLV/GENNY also off watch. |
| 10 Feb 2026 | Fitch | **Affirm** | GENM **BBB**, outlook negative. |
| 25 Feb 2026 | S&P | **Downgrade** | Empire Resorts **B+ → B** on November 2026 refinancing risk. |
| 20 Apr 2026 | Fitch / Moody's | **Instrument ratings** | New perpetuals **BB+ / Ba2**; limited credit relief. |
| 7 Sep 2026 | Fitch | **Downgrade** | GENT **BBB → BBB-**, GOHL **BBB → BBB-**, RWLV **BBB- → BB+**; stable outlook. |
| 8 Sep 2026 | Fitch | **Downgrade** | GENM **BBB → BBB-**, 2031 notes to BBB-, GENNY affirmed BBB-. |
| 8 Sep 2026 | S&P | **Warning, no action** | GENT/GENM at **BBB-** negative; FFO/debt 15–17% vs 20% trigger; "no more buffer". |

Sources: [Moody's](https://theedgemalaysia.com/node/785277); [RAM](https://www.businesstoday.com.my/2025/12/13/ram-revises-genting-berhad-credit-ratings-to-negative-after-takeover-bid); [S&P December](https://www.businesstimes.com.sg/companies-markets/sp-global-shifts-genting-companies-outlook-negative-weaker-credit-quality-forecasts); [Fitch December](https://www.ggrasia.com/fitch-affirms-genting-bhd-at-investment-grade-but-outlook-is-negative-amid-costs-on-genting-malaysia-downstate-ny-licence); [Fitch GENM February](https://cbonds.com/news/3788399/); [S&P Empire](https://www.ggrasia.com/sp-downgrades-empire-resorts-rating-expects-genting-to-provide-further-support); [Fitch September](https://theedgemalaysia.com/node/817109); [Fitch GENM September](https://www.thestar.com.my/business/business-news/2026/09/08/fitch-downgrades-genting-malaysia-to-039bbb-039); [S&P fallen-angel warning](https://www.ggrasia.com/genting-group-faces-fallen-angel-risk-no-more-buffer-for-earnings-downside-sp).

**Debt issuance for the takeover.** Genting RMTN issued **RM900m** (10 Nov), **RM495m** (20 Nov), **RM255m** (27 Nov) and **RM1.35b** (5 Dec) of one-year MTNs at **1-month KLIBOR + 1.80%**, all to part-finance the GENM acquisition ([RM900m](https://www.klsescreener.com/v2/announcements/view/10681211); [RM495m](https://www.klsescreener.com/v2/announcements/view/10707633); [RM255m](https://www.klsescreener.com/v2/announcements/view/10724501); [RM1.35b](https://www.klsescreener.com/v2/announcements/view/10742285)). On **30 December 2025**, Genting Vista issued **RM3.0b** of 1–5 year unrated MTNs at **3-month KLIBOR + 1.80%** and redeemed the RM3.0b of RMTN paper, extending the maturity profile ([announcement](https://www.klsescreener.com/v2/announcements/view/10858417)).

### 4.4 The first Resorts World Las Vegas RICO suit

On **3 December 2025**, Robert J. Cipriani and James Russell filed a **95-page civil RICO** complaint in the US District Court for the District of Nevada against **Resorts World Las Vegas, Genting Berhad**, former RWLV president **Scott Sibella**, attorney **David Chesnoff** and others. The complaint alleged the casino enabled illegal gambling, money laundering and retaliation against a cooperating witness from 2021–2023, and sought treble damages ([Vegas Slots Online](https://www.vegasslotsonline.com/news/2025/12/05/federal-lawsuit-accuses-resorts-world-of-facilitating-large-scale-organized-crime/); [docket](https://dockets.justia.com/docket/nevada/nvdce/2:2025cv02396/178321)). Genting denied the allegations. On **30 March 2026**, the plaintiffs filed a **107-page first amended complaint** adding Andrew Cheng Tao Do as a plaintiff and **Tan Sri Lim Kok Thay**, among others, as a defendant ([amended complaint](https://www.8newsnow.com/wp-content/uploads/sites/59/2026/03/File-Stamped-First-Amended-Complaint-with-new-parties.pdf)). The case remained pending.

---

## 5. January – June 2026: integration, 73.8%, perpetuals and the New York opening

**30 January 2026 — Lim Kok Thay takes the executive chair at Resorts World at Sentosa.** Genting Singapore's SGX filing appointed Tan Sri Lim Kok Thay as chairman and director of Resorts World at Sentosa Pte Ltd, the operating entity of the Singapore casino, with the role designated executive in nature. Day-to-day management stayed with CEO Lee Shi Ruh. Lim also remained Genting Berhad's Executive Chairman and Genting Malaysia's Deputy Chairman and Chief Executive ([GGR Asia](https://www.ggrasia.com/lim-kok-thay-now-executive-chairman-of-rws-operating-unit)). The appointment concentrated family oversight across the group's three main gaming vehicles.

**26 February 2026 — FY2025 results and another 5 sen dividend.** GENT declared a **5.0 sen** final dividend for FY2025, paid 17 April 2026; FY2025's total was **5.0 sen**, half the FY2024 total ([announcement](https://www.klsescreener.com/v2/announcements/view/11181555)). GENM declared **7.0 sen** for FY2025, down from 10.0 sen, paid 10 April 2026 ([announcement](https://www.klsescreener.com/v2/announcements/view/11181513)). The lower payouts were consistent with the group's debt-reduction and capex priorities, but they undercut the income case for retail holders.

**2 March 2026 — GENM management transition.** Dato' Sri Lee Choong Yan moved from President/Executive Director to **Senior Advisor and Executive Director** effective 1 March 2026; **Lee Thiam Kit** became President. Lee Choong Yan retired as Senior Advisor on 30 April 2026 and became a **Non-Independent Non-Executive Director** on 1 May 2026 ([announcement](https://www.klsescreener.com/v2/announcements/view/11185095); [GENM AR2025](https://www.klsescreener.com/v2/announcements/view/11539849)). Loh Wai Yee had become CFO on 1 April 2025.

**13 March 2026 — GENT's GENM stake reaches 73.838%.** Further open-market purchases took Genting to **4,184,966,253** GENM shares, or **73.838%**, with the Lim family deemed at **73.859%** ([notice](https://www.klsescreener.com/v2/announcements/view/11302411); [GGR Asia](https://www.ggrasia.com/genting-bhd-moves-closer-to-75pct-stake-target-for-taking-genting-malaysia-private)). The group was now within **1.16 percentage points** of the 75% delisting threshold but did not cross it.

**17 April 2026 — GENT files FY2025 annual report.** The report confirmed **26,320,000** treasury shares, **3,850,576,099** shares outstanding, a **45.07%** Lim-family deemed stake, a **73.8%** GENM stake and a **52.6%** Genting Singapore stake ([announcement](https://www.klsescreener.com/v2/announcements/view/11547907); [GENT AR2025](https://www.genting.com/wp-content/uploads/2026/07/GENTING-BERHAD_IAR2025v2.pdf)).

**20–30 April 2026 — the perpetual refinancing.** GOHL Capital Holdings priced **US$1.25b** of subordinated perpetual securities: **US$750m 7.625%** non-callable 5.5 years and **US$500m 8.300%** non-callable 10 years, rated **Ba2/BB+**. The securities were issued on 29 April 2026 and listed on SGX ([pricing announcement](https://www.klsescreener.com/v2/announcements/view/11554255); [issuance](https://www.klsescreener.com/v2/announcements/view/11568687)). In parallel, GOHL Capital ran a tender for its **US$1.5b 4.25% notes due 2027**; it accepted **US$882,462,000**, settled 4 May 2026, leaving about **US$617.5m** outstanding ([results](https://www.klsescreener.com/v2/announcements/view/11568689); [CreditSights](https://theedgemalaysia.com/node/821593)).

**28 April – 1 May 2026 — RWNYC becomes a full casino.** Live table games launched on 28 April 2026, and the property opened as New York City's first full-scale casino on 1 May 2026. The gaming machine tax rate fell to **56% from 68%** as the property converted from video lottery terminals to commercial slots; Maybank estimated this could add up to **US$100m** to GENM's 12-month earnings ([GGR Asia](https://www.ggrasia.com/gentings-resorts-world-new-york-city-to-launch-table-games-on-april-28); [Maybank note](https://www.ggrasia.com/a-lower-gaming-machine-tax-at-rwnyc-could-boost-genting-malaysia-earnings-maybank); [The Star](https://www.thestar.com.my/business/business-news/2026/05/01/genting-opens-new-york-casino-creates-history)).

**21 May 2026 — GENM posts a 1Q26 loss.** GENM reported a **RM25.2m** net loss despite a 10% rise in revenue to **RM2.87b**, as pre-opening costs at RWNYC and higher payroll offset growth. GENT's 1Q26 profit surged more than 20-fold on joint-venture gains and lower impairments ([The Edge](https://theedgemalaysia.com/node/804544); [ASGAM](https://asgam.com/2026/05/22/revenue-rising-but-genting-malaysia-falls-to-us6-million-net-loss-in-1q26-due-to-pre-opening-expenses-at-resorts-world-new-york-city)).

**28 May 2026 — Genting Highlands road charges start.** Genting began charging **RM3.30–RM25** per vehicle on the private access road to Genting Highlands. The Pahang state government and federal ministry said the road was privately owned and the charges were a state matter, not a federal toll ([Says](https://says.com/my/lifestyle/travel-lifestyle/genting-highlands-toll-starts-from-28-may-charges-range-from-rm3-30-to-rm25-per-vehicle-type); [The Edge](https://www.theedgemalaysia.com/node/780833)). A developer's challenge to the road privatisation failed in June 2026 ([NST](https://www.nst.com.my/news/regional/2026/06/1470619/developer-fails-bid-challenge-genting-road-privatisation-watch)). This was a consumer-facing irritant with clear retail-sentiment relevance, separate from the casino licence itself.

**1 June 2026 — the RWNYC racing-support tax dispute emerges.** Resorts World NYC argued that its **56%** slot tax was inclusive of payments to the horseracing industry; the state Gaming Commission said the payments, at least **US$150m a year**, must be paid on top. Genting said that would mean an effective **72%** slot tax and could cost it **over US$500m** before the other downstate casinos open around 2030 ([NY Focus](https://nysfocus.com/2026/06/01/nyc-casino-resorts-world-horseracing-support-tax)). On **25 August 2026**, ten Queens Democratic lawmakers urged Governor Hochul to resolve the dispute; on **4 September 2026**, the deadline for a legal challenge passed with no public filing located ([NY Post](https://nypost.com/2026/08/31/us-news/dems-push-hochul-to-block-staggering-72-tax-rate-slapped-on-nycs-first-full-casino/); [NY Focus](https://nysfocus.com/2026/09/04/resorts-world-nyc-casino-tax-expansion)). The dispute remained unresolved at the end of the window.

**10–11 June 2026 — AGMs.** GENM's 46th AGM approved all **eight** resolutions, including re-election of Lim Kok Thay and Lee Choong Yan and renewal of the buy-back mandate; **Teo Eng Siong** retired as a Non-Independent Non-Executive Director after 16 years ([outcome](https://www.klsescreener.com/v2/announcements/view/11611215); [retirement](https://www.klsescreener.com/v2/announcements/view/11611205)). GENT's 58th AGM approved all **eight** resolutions; the re-election of **Tan Sri Foong Cheng Yuen** drew **9.05%** votes against, the largest dissent of the meeting ([outcome](https://www.klsescreener.com/v2/announcements/view/11612349)).

**12 June 2026 — Genting says it is not privatising GENM.** Speaking at the 11 June AGM, CEO Tan Kong Han said the 2025 takeover was not aimed at privatising GENM but at ensuring Genting had more than 50% control, and that the group was "fortunate" to have raised its stake. The parent remained below 75% ([GGR Asia](https://www.ggrasia.com/genting-bhd-not-privatising-its-global-gaming-unit-genting-malaysia-report); [ASGAM](https://asgam.com/2026/06/15/genting-bhd-ceo-says-balance-sheet-requirements-not-privatization-at-heart-of-genting-malaysia-takeover-bid)). The remarks did not stop speculation about a renewed attempt once RWNYC earnings improve.



---

## 6. July – October 2026: Empire clean-up, downgrades, lawsuits and the rights-issue shock

**2 July 2026 — Empire redeems its US$300m notes; recapitalisation shelved.** Empire Resorts redeemed in full its **US$300m 7.75%** senior secured notes due 1 November 2026. With the debt gone, the parties agreed the **US$525m** asset-sale/recapitalisation proposal would not proceed ([announcement](https://www.klsescreener.com/v2/announcements/view/11625481); [NST](https://www.nst.com.my/business/corporate/2026/07/1479747/genting-malaysia-unit-calls-capital-restructuring-after-settling)). The clean-up removed a near-term maturity but did not fix Empire's operating losses.

**9 July 2026 — Genting Americas secures a US$2b facility.** The facility refinanced debt and funds the second phase of the RWNYC expansion. S&P said it removed Empire's refinancing risk but construction risks remained ([GGR Asia](https://www.ggrasia.com/genting-americas-in-new-us2bln-bank-facility-to-refinance-debt-fund-second-phase-of-n-y-casino); [AGB](https://agbrief.com/news/usa/09/07/2026/genting-americas-2b-facility-eases-empire-refinancing-risk-but-construction-risks-remain-sp)).

**22 July 2026 — RWNYC adds 1,400 slots and breaks ground on phase two.** The new gaming floor took the property closer to its planned scale; the group was on track for **400 table games by January 2027** ([GGR Asia](https://www.ggrasia.com/resorts-world-new-york-city-adds-1400-casino-slots-has-phase-two-ground-breaking); [ASGAM](https://asgam.com/2026/07/22/gentings-resorts-world-new-york-city-opens-new-gaming-floor-adding-another-1400-slot-machines-and-themed-aristocrat-zone)).

**20 August 2026 — GENT swings to a 2Q26 net loss.** GENT reported a **RM27.1m** net loss despite a 14% rise in revenue, as finance costs and forex losses offset New York growth. GENM's borrowings rose **23%** year on year as casino costs squeezed profit ([The Edge](https://theedgemalaysia.com/node/815315); [AGB](https://agbrief.com/news/malaysia/21/08/2026/genting-malaysia-borrowings-rise-23-as-new-york-casino-costs-squeeze-profit)). The result reinforced the market's leverage concerns ahead of the rights issue.

**7–8 September 2026 — Fitch cuts GENT and GENM to BBB-.** Fitch downgraded GENT to **BBB-** from BBB, GOHL to BBB- and RWLV to **BB+** from BBB-, with stable outlooks, citing leverage above **4.0x** for three years and capex in Singapore and New York ([The Edge](https://theedgemalaysia.com/node/817109); [Fitch](https://www.fitchratings.com/research/corporate-finance/fitch-downgrades-genting-berhad-to-bbb-resorts-world-las-vegas-to-bb-outlooks-stable-07-09-2026)). The next day it cut GENM to **BBB-** from BBB and its 2031 notes to BBB-, while affirming Genting New York at BBB- ([The Star](https://www.thestar.com.my/business/business-news/2026/09/08/fitch-downgrades-genting-malaysia-to-039bbb-039)).

**8 September 2026 — S&P warns of fallen-angel risk.** S&P said Genting had **"no more buffer"** for earnings disappointment, with FFO/debt expected at **15–17%** through 2028 versus a 20% downside trigger. GENT and several subsidiaries were at **BBB- negative**, the lowest investment-grade level, leaving a real risk of losing investment grade ([GGR Asia](https://www.ggrasia.com/genting-group-faces-fallen-angel-risk-no-more-buffer-for-earnings-downside-sp); [ASGAM](https://asgam.com/2026/09/08/sp-global-expansion-costs-subdued-operational-performance-place-genting-bhd-at-risk-of-becoming-a-fallen-angel/)). S&P did not change the rating in that report.

**14 September 2026 — RWLV whistleblower suit.** Preston Banks, a former compliance director at Resorts World Las Vegas, sued in US District Court alleging whistleblower retaliation under the Anti-Money Laundering Act and wrongful termination under Nevada law. He claimed he was fired after reporting suspicious activity by a group of foreign patrons and that a report shown to regulators omitted material details. RWLV called the suit frivolous and denied the allegations ([FocusGN](https://focusgn.com/former-resorts-world-las-vegas-compliance-director-sues-over-alleged-whistleblower-firing); [Global Gaming Insider](https://globalgaminginsider.com/news/7272/resorts-world-las-vegas-faces-whistleblower-lawsuit-over-aml-concerns)). This was the second Nevada legal/regulatory thread after the US$10.5m AML settlement and the civil RICO case.

**17 September 2026 — GENM buybacks resume.** GENM bought **200,000** shares at **RM1.50**, its first purchase under the mandate renewed at the 10 June 2026 AGM, taking treasury to **270,502,915** shares (4.55542%). The buyback was small relative to the coming rights issue but signalled that the board saw value near RM1.50 ([17 Sep](https://www.klsescreener.com/v2/announcements/view/11669007)).

### 6.1 The RM1.25b rights issue

**9 October 2026 — Genting proposes its first rights issue since 1973.** GENT announced a renounceable rights issue to raise about **RM1.25b**, with proceeds earmarked for:

| Use | Amount |
|---|---:|
| Repayment of borrowings | **RM800.0m** |
| Working capital (including **RM280m** for interest/financing costs and RM149.5m general working capital) | **RM429.5m** |
| Expenses | **RM20.5m** |
| **Total** | **RM1,250.0m** |

The issue price and entitlement basis were **not fixed**; the board intended a **25–30% discount to TERP** based on the 5-day VWAP before the price-fixing date. KHR, KHI and Dato' Indera Lim Keong Hui gave irrevocable undertakings to subscribe in full for their **45.10%** entitlement, and the remainder was to be underwritten. The exercise required shareholder approval at an **EGM** ([announcement](https://www.klsescreener.com/v2/announcements/view/11682541)).

The balance sheet context was **RM45.25b** of total borrowings at 30 June 2026, of which **RM9.68b** was short-term and **RM35.58b** long-term, at interest rates of **3.88%–8.45%**. Genting estimated the RM800m repayment would save about **RM41.3m** a year based on a **5.16%** weighted average short-term rate ([announcement](https://www.klsescreener.com/v2/announcements/view/11682541)).

**12 October 2026 — the stock crashes.** GENT fell **43 sen, or 22.87%, to RM1.45**, its lowest since April 2007, wiping more than **RM1.6b** of market value; GENM fell **17.45% to RM1.23**. Bursa suspended intraday short selling in both counters. **Maybank Investment Bank downgraded GENT to Sell from Buy** and cut its target price to **RM1.49 from RM2.88**. CIMB Securities flagged up to **18% EPS dilution** in FY2027–FY2028 ([The Edge](https://theedgemalaysia.com/node/821415); [The Star](https://www.thestar.com.my/business/business-news/2026/10/13/genting-loses-rm16bil-in-market-value-after-cash-call); [FMT](https://www.freemalaysiatoday.com/category/business/2026/10/12/genting-shares-tumble-most-since-1998-on-rights-issue-plan); [CIMB note](https://www.businesstoday.com.my/2026/10/12/gentings-rm1-25-billion-rights-issue-could-dilute-earnings-by-18-says-cimb)).

**12 October 2026 — GENM buys 550,000 more shares.** The same day as the crash, GENM bought **550,000** shares at **RM1.26–1.27**, lifting treasury to **271,052,915** shares (4.56468%). The purchase was tiny against the sell-off but reinforced the board's price signal ([announcement](https://www.klsescreener.com/v2/announcements/view/11683189)).

**29 September – 23 October 2026 — insiders buy the dip.** KHR bought **6,000,000** GENT shares at **RM1.494** on 12 October, **270,000** at **RM1.39185** on 14 October and **152,500** at **RM1.45** on 15 October, lifting the family's deemed stake to **45.239%** ([notice](https://www.klsescreener.com/v2/announcements/view/11684741); [director notice](https://www.klsescreener.com/v2/announcements/view/11686075)). CEO **Tan Kong Han** bought **1,250,000** shares between 29 September and 23 October at **RM1.34–1.87**, taking his direct holding to **2,540,000** ([notice](https://www.klsescreener.com/v2/announcements/view/11691613)). The insider buying was the clearest counter-signal to the retail sell-off.

**14 October 2026 — Genting defends the discount.** Replying to Bursa's query, Genting said the 25–30% discount reflected issue size, market conditions, liquidity, comparable rights issues, underwriting appetite and the need to incentivise participation. It confirmed the working-capital split: **RM280m** for interest/financing costs and **RM149.5m** for general working capital ([reply](https://www.klsescreener.com/v2/announcements/view/11684683)).

**23 October 2026 — listing application submitted.** Genting applied to Bursa for the listing and quotation of the rights shares. The issue price, entitlement basis and entitlement date remained unfixed, and no EGM notice or shareholder-approval outcome had been announced ([announcement](https://www.klsescreener.com/v2/announcements/view/11690197)). CreditSights expected completion in **Q1 2027** and modelled the issue as a **one-for-four** exercise, but that entitlement basis is an analyst assumption, not company guidance ([CreditSights](https://www.businesstoday.com.my/2026/10/13/gentings-rm1-25-billion-rights-issue-positive-for-credit-profile-but-downgrade-risks-remain-creditsights)).

**29 October 2026 — Genting says no further equity fundraising is currently planned.** In a reply to The Edge, Genting said **"No further equity fundraising is currently planned by the company"** after the RM1.25b rights issue. The statement followed a **24%** share-price fall over 10 days and analyst concerns about more cash calls and dividend cuts ([The Edge](https://theedgemalaysia.com/node/822667); [BusinessToday](https://www.businesstoday.com.my/2026/10/19/genting-share-price-dives-24-in-last-10-days-as-rights-issue-raises-cash-flow-concerns)).

---

## 7. Legal and regulatory docket

| Matter | Status at 2 Nov 2026 | Key dates | Source |
|---|---|---|---|
| **RAV Bahamas v Genting Americas** (US$600m+ claim over RW Bimini) | Pending; amended complaint filed, second motion to dismiss filed | Filed 7 Oct 2024; motion to dismiss 22 Nov 2024; dismissed with leave 1 Jul 2025; amended complaint 29 Jul 2025; motion to dismiss 12 Sep 2025 | [GENT AR2025 Note 47](https://www.genting.com/wp-content/uploads/2026/07/GENTING-BERHAD_IAR2025v2.pdf#page=226) |
| **Nevada AML fine** (RWLV/Genting) | Completed; US$10.5m paid | Commission approval 27 Mar 2025 | [NST](https://www.nst.com.my/business/corporate/2025/03/1191412/genting-paying-nevada-gaming-commission-us105mil-settle-las-vegas) |
| **Cipriani/Russell civil RICO v RWLV/Genting** | Pending; amended complaint added Lim Kok Thay | Filed 3 Dec 2025; amended 30 Mar 2026 | [Vegas Slots Online](https://www.vegasslotsonline.com/news/2025/12/05/federal-lawsuit-accuses-resorts-world-of-facilitating-large-scale-organized-crime/); [amended complaint](https://www.8newsnow.com/wp-content/uploads/sites/59/2026/03/File-Stamped-First-Amended-Complaint-with-new-parties.pdf) |
| **Preston Banks whistleblower suit v RWLV** | Pending; RWLV denies | Filed 14 Sep 2026 | [FocusGN](https://focusgn.com/former-resorts-world-las-vegas-compliance-director-sues-over-alleged-whistleblower-firing) |
| **RWNYC racing-support tax dispute** | Unresolved; legal-challenge deadline 4 Sep 2026 passed with no public filing located | Dispute public 1 Jun 2026; lawmakers' letter 25 Aug 2026; deadline 4 Sep 2026 | [NY Focus](https://nysfocus.com/2026/06/01/nyc-casino-resorts-world-horseracing-support-tax); [NY Focus](https://nysfocus.com/2026/09/04/resorts-world-nyc-casino-tax-expansion) |
| **New York downstate casino licence** | Completed; RWNYC opened 1 May 2026 | Recommended 1 Dec 2025; awarded 16 Dec 2025; tables 28 Apr 2026; opening 1 May 2026 | [GENM](https://www.klsescreener.com/v2/announcements/view/10730039); [The Star](https://www.thestar.com.my/business/business-news/2025/12/16/genting-malaysia-gets-the-nod-for-new-york-casino-licence) |
| **Genting Highlands road privatisation/toll** | Completed; developer challenge failed | Charges start 28 May 2026; challenge failed 23 Jun 2026 | [Says](https://says.com/my/lifestyle/travel-lifestyle/genting-highlands-toll-starts-from-28-may-charges-range-from-rm3-30-to-rm25-per-vehicle-type); [NST](https://www.nst.com.my/news/regional/2026/06/1470619/developer-fails-bid-challenge-genting-road-privatisation-watch) |
| **Malaysia casino licence** | Routine; renewable every three months; no specific renewal announcement in window | Standing disclosure in FY2025 AR | [GENM AR2025](https://www.klsescreener.com/v2/announcements/view/11539849) |
| **AGMs** | Completed; all resolutions passed | GENM 11 Jun 2025 and 10 Jun 2026; GENT 12 Jun 2025 and 11 Jun 2026 | [GENM 2026](https://www.klsescreener.com/v2/announcements/view/11611215); [GENT 2026](https://www.klsescreener.com/v2/announcements/view/11612349) |
| **Rights issue EGM** | Not held as of 2 Nov 2026; no EGM notice/outcome in Bursa announcements | Announced 9 Oct 2026; listing application 23 Oct 2026 | [announcement](https://www.klsescreener.com/v2/announcements/view/11682541); [listing application](https://www.klsescreener.com/v2/announcements/view/11690197) |

**Regulatory investigations.** No Malaysian regulatory investigation or tax dispute specific to Genting Berhad/GENM was disclosed in the Bursa announcements or annual reports in the window. The material regulatory matters were US-based: the Nevada AML settlement, the RWLV civil RICO/whistleblower litigation and the New York racing-support tax dispute. The Malaysian casino licence is a standing three-monthly renewal, not a contested event in this period.

---

## 8. What this dataset suggests for retail sentiment

These are candidate mechanisms, not proof of causality. The sentiment series should test them event-by-event.

1. **The "privatisation" label was misleading, and the market treated it as a governance event.** Genting framed the RM2.35 offer as a route to statutory control; the independent adviser called it **"not fair and not reasonable"**, and the offer closed at **73.13%**, short of 75%. Minority holders who held for a higher price or a delisting were disappointed, while the parent's subsequent on-market buying signalled that control was the real objective. The distinction between "takeover completed" and "privatisation failed" matters for how retail discussed the stock.

2. **The New York licence was a sell-the-news event.** The licence was the biggest positive catalyst in the window, but GENM fell **4.26%** and GENT **2.08%** on the first trading day after the award. The market had already priced the win, and the licence brought **US$5.5b** of capex, a large fee and a tax dispute rather than near-term free cash flow.

3. **The dividend cut and the rights issue broke the income narrative.** GENT's FY2025 dividend of **5.0 sen** was half FY2024's **11.0 sen**; GENM's fell from **10.0 sen to 7.0 sen**. Then the **RM1.25b** rights issue — the first since 1973 — raised the prospect of dilution and further cash calls. The **22.87%** one-day fall on 12 October 2026 and the **24%** 10-day decline are the clearest sentiment shocks in the window.

4. **Credit downgrades turned a balance-sheet story into a retail story.** Moody's, S&P and Fitch all moved negative or down between December 2025 and September 2026. Fitch's cut to **BBB-** and S&P's **"no more buffer"** warning put Genting one notch above junk, a headline that retail investors could readily understand. The downgrades also raised funding costs, which made the rights issue more defensible and more painful at the same time.

5. **Insider buying was the main counter-signal.** KHR bought **6m** GENT shares at **RM1.494** on the crash day and another **422,500** at **RM1.39–1.45**; CEO Tan Kong Han bought **1.25m** shares at **RM1.34–1.87**. These purchases did not reverse the price trend, but they gave the bulls a concrete "family is buying" argument.

6. **Legal headlines were US-driven and slow-burning.** The Nevada AML fine, the RICO suit, the whistleblower suit and the New York tax dispute were all material but not immediate earnings events. Their sentiment effect is likely to be episodic — around filing dates, amended complaints and regulatory deadlines — rather than a continuous drag.

7. **The free float and overhang matter.** GENM's free float was only about **26.1%**, close to the 25% public-spread floor, and GENT still held **73.888%**. Any further parent buying, a renewed privatisation attempt or a rights-issue dilution could move the small float sharply. This is a structural amplifier for both positive and negative news.

---

## 9. Data notes and caveats

- **Date precision.** Bursa announcements are dated to the day; `created_utc` is set to **00:00 UTC** on that date and `raw.time_precision` is `"day"`. News timestamps in the source corpus were used only where an exact publication time was available; the event file does not invent times.
- **Status semantics.** `completed` means the transaction/event happened; `failed` means the stated objective (75% delisting) was not achieved even though the offer itself closed; `proposed`/`pending` means announced but not completed; `ongoing` means litigation or dispute unresolved; `routine` means a standing regulatory arrangement, not a discrete event.
- **Conflicts.** The main conflicts are the S&P December 2025 "downgrade vs outlook" wording, the New York licence fee (US$500m paid vs US$600m commitment), the rights-issue entitlement basis (company left it open; CreditSights assumed one-for-four), and the "privatisation" framing (company said control, media said privatisation). These are documented in [`company_events_report.md`](company_events_report.md).
- **Source mirror.** Bursa announcements are cited through the KLSE Screener mirror because the Bursa site blocks automated access. Each page reproduces the announcement text and links to the original Bursa filing. Annual-report facts are cited to the official Genting PDF where available, otherwise to the Bursa annual-report announcement.
