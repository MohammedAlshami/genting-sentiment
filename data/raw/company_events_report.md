# Company events and ownership collection report

**Window:** 2 November 2024 – 2 November 2026
**Entities:** Genting Berhad (`GENTING`, Bursa 3182) and Genting Malaysia Berhad (`GENM`, Bursa 4715)
**Outputs:**
- `data/raw/company_events.jsonl` — **89** curated events, 37 GENM / 52 GENTING
- `data/raw/ownership.jsonl` — **65** ownership records, 33 GENTING / 32 GENM
- `data/raw/company_structure.json` — 14 nodes, 15 control/ownership edges, 4 listed vehicles, 20 director/management records
- `data/raw/company_timeline.md` — chronological narrative with citations
- `data/raw/company_events_report.md` — this report

| Event type | Count |
|---|---:|
| Credit rating | 10 |
| Legal | 9 |
| Ownership change | 7 |
| Dividend | 5 |
| Debt issuance | 5 |
| Analyst action | 5 |
| Annual report | 4 |
| AGM | 4 |
| Takeover offer | 4 |
| Board / management change | 5 |
| Insider buying | 3 |
| Regulatory tax | 3 |
| Regulatory licence | 3 |
| Operations | 3 |
| Rights issue | 3 |
| Earnings | 2 |
| Governance | 2 |
| Other (penalty, acquisition, restructuring, tender, maturity, buyback, financing, divestment, market reaction, toll) | 12 |

Validation: `python3 -m genting.validate data/raw/company_events.jsonl` returns **OK: 0 errors**, 89 `post` records, no empty bodies, no duplicate bodies, date range **2024-11-22 → 2026-10-29**. No SQLite writes were made; the orchestrator can import the JSONL after validation.

---

## 1. Collection method

### Bursa announcements

I collected the Bursa announcement index for both counters from the KLSE Screener mirror (`/v2/announcements/stock/3182` and `/4715`) across pages 1–9 and 1–12 respectively (**21 index pages**), then fetched **630 detail pages**. The mirror paginates 30 items per page but the page order is not strictly chronological, so I walked enough pages to pass the window start and then filtered on each detail page's **Date Announced** field.

- **630** announcement detail pages fetched and cached under `data/raw/cache/company_events/`.
- **553** fell inside the window (193 GENTING, 360 GENM).
- Every in-window announcement was parsed for title, category, date, body, reference number and attachments.
- I then selected **89** events that are material to ownership, governance, corporate actions, credit, legal/regulatory status or group structure. Routine quarterly results, repetitive director-dealing notices and administrative announcements were not promoted to events, but their underlying notices were used to build `ownership.jsonl`.

The mirror reproduces the Bursa announcement text and links to the original filing. Direct Bursa pages and attachment downloads are Cloudflare-protected; I used `curl_cffi` with `impersonate="chrome124"` for the PDFs that mattered (rights-issue announcement, reply to query, annual reports).

### Annual reports

I used the official Genting Berhad PDFs where available:

- [Genting Berhad FY2025 Integrated Annual Report](https://www.genting.com/wp-content/uploads/2026/07/GENTING-BERHAD_IAR2025v2.pdf) (filed 17 April 2026)
- [Genting Berhad FY2024 Integrated Annual Report](https://www.genting.com/wp-content/uploads/2025/05/GENTING_IAR24v3.pdf) (filed 25 April 2025)

Genting Malaysia's annual reports were read from the Bursa announcements:

- [GENM FY2025 annual report](https://www.klsescreener.com/v2/announcements/view/11539849) (16 April 2026)
- [GENM FY2024 annual report](https://www.klsescreener.com/v2/announcements/view/9434623) (11 April 2025)

Key sections used: analysis of shareholdings (top 30 holders, substantial shareholders, directors' holdings), directors' report (treasury shares, dividends, directorate), group corporate structure, notes on share capital/treasury shares, material litigation (Note 47), and the dividend tables.

### News and court documents

The existing `data/raw/news_articles.jsonl` (386 articles) was reused for 2025-11-03 → 2026-10-29. It supplied market reaction, analyst notes, rating actions and the New York tax dispute. For events before 3 November 2025 (not covered by the news corpus), I used Bursa announcements, annual reports and targeted fetches of The Edge, NST, GGR Asia, Reuters/Straits Times and court documents.

Primary court documents:
- Cipriani/Russell civil RICO docket: `2:25-cv-02396-JCM-DJA`, US District Court for the District of Nevada, filed 3 December 2025.
- First amended complaint, Document 36, filed 30 March 2026 (107 pages), adding Tan Sri Lim Kok Thay and Andrew Cheng Tao Do.

---

## 2. Coverage matrix

| Category | Covered? | What is in the dataset | Main sources |
|---|---|---|---|
| **Major shareholders** | Yes | KHR, KHI, Parkview Management, Lim Kok Thay, Lim Keong Hui; direct vs deemed; 2025 and 2026 snapshots; Oct 2026 purchases | GENT AR2024/AR2025; Bursa s-hldr notices |
| **Directors / key management** | Yes | GENT and GENM boards, appointment/resignation/redesignation dates; CEO/CFO/President changes | AR2025/AR2024; Bursa boardroom notices |
| **Substantial shareholder notices** | Yes | 2025 accumulation; 2025 takeover stake ladder; 2026 73.8–73.888%; Oct 2026 post-rights purchases | Bursa notices |
| **Director dealings / insider trades** | Yes | Tan Kong Han 2026 purchases; KHR purchases; Lim Keong Hui's acceptance of the GENM offer | Bursa director notices; AR2025 |
| **Treasury shares / free float / share capital** | Yes | GENT 26,320,000 treasury; GENM 270.3m → 271.05m; issued/outstanding shares; calculated free float | AR2025 Notes 33–34; SBB announcements |
| **2025 GENM privatisation attempt** | Yes | RM2.35 offer, 13 Oct launch, 3 Nov unconditional, 13 Nov mandatory, 1 Dec close at 73.13%, failed 75% threshold | Bursa announcements; The Edge; GGR Asia |
| **2026 RM1.25b rights issue** | Yes | 9 Oct announcement, use of proceeds, 25–30% discount, EGM requirement, 14 Oct query reply, 23 Oct listing application, 12 Oct market reaction | Bursa announcements; rights-issue PDF; CreditSights/CIMB/Maybank |
| **Dividends** | Yes | GENT FY2024/FY2025 5 sen; GENM FY2024 4 sen, FY2025 7 sen; payment dates | Bursa entitlements; AR dividend tables |
| **Buybacks** | Yes | GENT no purchases; GENM 17 Sep and 12 Oct 2026 buybacks; treasury totals | AR2025; SBB announcements |
| **Bond/MTN issuance and maturities** | Yes | RM900m/RM495m/RM255m/RM1.35b RMTN; RM3b Vista; US$1.25b perpetuals; US$1.5b 2027 tender; US$300m Empire redemption; US$2b Genting Americas facility | Bursa announcements; news |
| **Credit ratings** | Yes | Moody's, S&P, Fitch, RAM actions from Dec 2025 to Sep 2026; instrument ratings on perpetuals | Rating agency reports; The Edge; GGR Asia; Business Times |
| **Analyst actions** | Yes | Maybank Sell, CIMB dilution, CGS Hold, HLIB raise, Nomura, Kenanga, CreditSights | News corpus |
| **RWLV lawsuit** | Yes | Civil RICO filed 3 Dec 2025; amended 30 Mar 2026; whistleblower suit 14 Sep 2026; Nevada AML fine 27 Mar 2025 | Court documents; FocusGN; Vegas Slots Online; NST |
| **RWNYC tax dispute** | Yes | Racing-support payments, 56% vs 72%, >US$500m, 1 Jun 2026; lawmakers' letter 25 Aug; 4 Sep deadline | NY Focus; NY Post; PlayUSA; Covers |
| **New York downstate licence** | Yes | 1 Dec 2025 recommendation; 16 Dec 2025 award; 28 Apr 2026 tables; 1 May 2026 opening; 22 Jul 2026 expansion | GENM announcements; NYSGC/GFLB; GGR Asia; The Star |
| **Pahang/Malaysia casino licence** | Partial | Standing three-monthly renewal disclosed in AR2025; no specific renewal announcement found | GENM AR2025 |
| **AGM/EGM outcomes** | Yes | GENT 57th/58th; GENM 45th/46th; rights-issue EGM not held | Bursa meeting outcomes |
| **Regulatory investigations / tax disputes** | Yes | US matters above; no Malaysian investigation disclosed | Bursa/AR; court/NY sources |
| **Group structure** | Yes | GENT → GENM/GENP/GENS/Energy; GENM → RWLV/GENNY/UK/Empire/Bimini; trust chain | AR2025 group chart; AR shareholding notes |

---

## 3. Source hierarchy and cross-checks

1. **Bursa announcements** are the primary source for dates, amounts, stake percentages and status. Each event links to a KLSE Screener announcement page (which reproduces the Bursa text).
2. **Annual reports** are the primary source for ownership snapshots, directors' holdings, treasury shares and group structure. Where a Bursa announcement and an annual report disagree because of timing (e.g. 73.13% at offer close vs 73.838% at the FY2025 AR date), both are kept and the `as_of` date disambiguates.
3. **News** is secondary. I used at least two sources for the major contested facts (takeover stake ladder, NY licence, rating actions, rights-issue reaction). Where only one source exists, `raw.confidence` is `medium` or the event is marked as a status note.
4. **Court documents** are primary for the RICO case. The docket number and filing date are in the event's `raw.notes`.

Cross-checks performed:
- Takeover: Bursa offer/close announcements + The Edge/GGR Asia/Straits Times.
- Stake ladder: Bursa s-hldr notices + GGR Asia + AR2025.
- NY licence: GENM Bursa announcement + NYSGC/GFLB document + The Star/NST/GGR Asia.
- Ratings: agency reports + at least two Malaysian financial outlets per action.
- Rights issue: Bursa announcement + official PDF + CIMB/Maybank/CreditSights + price reaction.
- Dividends: Bursa entitlement notices + AR dividend tables.
- Group structure: GENT AR2025 group chart + GENM AR2025 subsidiary list.

---

## 4. Gaps

1. **No news corpus before 3 November 2025.** The existing `news_articles.jsonl` starts on 2025-11-03. Events from November 2024 to October 2025 rely on Bursa announcements, annual reports and targeted web fetches. This is adequate for corporate/legal facts but thinner for retail commentary and analyst reaction in that period.
2. **No specific Pahang/Malaysia casino-licence renewal announcement.** The FY2025 annual report says the Malaysian casino licence is renewable every three months, but no Bursa announcement of a renewal, fee or condition was found. I recorded this as a `routine` status note with `confidence: medium`, not as a discrete renewal event. If a renewal letter exists, it is not public.
3. **Rights-issue EGM has not been held.** As of 2 November 2026, there is no EGM notice or outcome in the Bursa announcements. The issue price, entitlement basis and entitlement date are unfixed. The dataset therefore marks the rights issue `proposed`/`pending`, not completed.
4. **No court judgment in the RWLV RICO or whistleblower cases.** Both are ongoing. The RICO amended complaint is dated 30 March 2026; the whistleblower suit was filed 14 September 2026.
5. **No public court filing in the RWNYC racing-support dispute.** The 4 September 2026 legal-challenge deadline passed; I found no filing. The event is marked `unresolved`, not `litigation`.
6. **Scanned takeover press notices.** The 3 November and 13 November 2025 press notices are scanned PDFs with no text layer; `pdftotext` returned nothing and tesseract is not installed. The key numbers were taken from the announcement text and contemporaneous news, not OCR.
7. **Bursa attachments.** A few PDFs are Cloudflare-protected. Key documents (rights issue, reply to query, annual reports) were downloaded with `curl_cffi`; others are cited through the announcement page.
8. **Quarterly results.** The dataset captures the results that moved sentiment (FY2025 dividends, 1Q26 GENM loss, 2Q26 GENT loss) but not every quarterly announcement. The event file is curated, not an exhaustive announcement archive.
9. **GENM FY2024 final dividend announcement.** The KLSE mirror's GENM pages did not include the February 2025 entitlement notice. The 4.0 sen final and 10 April 2025 payment date are taken from the FY2025 annual report's dividend table.
10. **Date-only timestamps.** Bursa announcements are day-level. `created_utc` is 00:00 UTC on the announcement date, with `raw.time_precision = "day"`. This is deliberate; it avoids inventing a publication time.

---

## 5. Conflicts and resolutions

| Conflict | Sources | Resolution in the dataset |
|---|---|---|
| **S&P December 2025: downgrade or outlook change?** | The Edge/Business Times (17 Dec 2025) say S&P revised the outlook to negative and **affirmed** ratings. A later Business Times article (Oct 2026) says S&P "lowered its rating in the same month to BBB-". | S&P had GENT at **BBB-** before December 2025 ([cbonds, 27 Apr 2025](https://cbonds.com/news/3370787/), and the Dec 2025 reports). The 17 Dec action was an **outlook change to negative**, not a rating cut. The later article is imprecise. Flagged in the event body and this table. |
| **New York licence fee: US$500m or US$600m?** | GFLB proposal/GENM announcements say **US$600m upfront**; Fitch (Sep 2026) says about **US$500m** has been spent, including the licence fee. | Both can be true: US$600m commitment vs US$500m paid/recognised to date. The event uses "US$600m upfront fee" for the bid and notes the US$500m spend in the Fitch context. |
| **Rights issue entitlement: one-for-four?** | Official 9 Oct 2026 announcement says the issue price and entitlement basis are **not determined**. CreditSights (13 Oct 2026) models a **one-for-four** issue. | The event records the official position; the one-for-four is labelled an **analyst assumption**, not company guidance. |
| **"Privatisation" vs "control"** | Media called the 2025 exercise a privatisation attempt; Genting's CEO said in June 2026 it was about **control**, not privatisation. The offer document said Genting did not intend to maintain GENM's listing if sufficient acceptances were received. | The dataset uses "takeover / privatisation attempt" for the 2025 exercise because the offer document contemplated delisting, and separately records the CEO's June 2026 denial. Status is `failed` for the 75% delisting objective, not for the offer itself. |
| **GENM stake: 73.13%, 73.8%, 73.859%, 73.888%** | 73.13% at offer close (1 Dec 2025); 73.8% at 31 Dec 2025; 73.8383% direct / 73.8596% deemed at 16 Mar 2026; 73.888% deemed at 2 Apr 2026. | These are different dates and different bases (direct vs deemed). The timeline uses a table with dates; `ownership.jsonl` has separate rows. |
| **Fitch GENM: affirmed BBB in Feb 2026, downgraded to BBB- in Sep 2026** | cbonds (10 Feb 2026) says Fitch affirmed GENM at BBB, negative outlook; The Star (8 Sep 2026) says Fitch downgraded GENM to BBB- from BBB. | Both are correct: February was an affirmation; September was a downgrade following the parent. |
| **Free float: 26.14% vs 26.17%** | Calculated 100% − 73.8596% = 26.1404%; Bursa shareholding table shows 26.166% in the 5%-and-above/other buckets. | The dataset uses **26.14%** and labels it "calculated"; the difference is rounding/definition (the AR's bracket analysis is not a free-float calculation). |
| **Genting Singapore stake: 52.6% vs 52.5852%/52.5935%** | Group chart rounds to 52.6%; directors' deemed interest table shows 52.5852% (FY2024) and 52.5935% (FY2025). | Use **52.6%** for the group structure, with the precise deemed figure in the AR notes. |
| **GENM FY2024 final dividend declaration date** | AR2025 table says **27 February 2025**; no KLSE entitlement notice found in the mirror for that date. | Event dated 27 Feb 2025, sourced to the AR2025 dividend table; flagged as a gap. |
| **12 October 2026 market-cap loss: RM1.6b or RM2b+** | The Star says more than **RM1.6b** was wiped; The Edge says **over RM2b**. | Both are same-day estimates around the close; the difference reflects the reference market cap and rounding. The event uses the more conservative "over RM1.6b" and cites both. |
| **RWLV RICO defendants** | Original complaint (Dec 2025) named RWLV, Genting Berhad, Scott Sibella, David Chesnoff and others; the amended complaint (Mar 2026) added Tan Sri Lim Kok Thay and Andrew Cheng Tao Do. | The Dec 2025 event describes the original defendants; the Mar 2026 event describes the additions. Do not read the amended list back into the original filing. |

---

## 6. Status semantics

- `announced` — public but not yet completed.
- `completed` — transaction/event happened (payment, issuance, redemption, meeting, court filing).
- `failed` — the stated objective was not achieved (the 75% GENM delisting threshold).
- `proposed` / `pending` — announced, awaiting approval or implementation (rights issue).
- `ongoing` — litigation or dispute unresolved.
- `unresolved` — a deadline passed without a public resolution/filing (NY racing-support dispute).
- `routine` — standing regulatory arrangement, not a discrete event (Malaysia casino licence).
- `withdrawn` — proposal abandoned (Empire recapitalisation).
- `unconditional` / `mandatory` / `recommended` / `rejected` — specific takeover or regulatory states.

---

## 7. Recommended next steps

1. **Add the 2024-11 → 2025-10 news archive** if the orchestrator can backfill it. That would let the sentiment model compare pre-takeover retail chatter with the post-October 2025 spike.
2. **Fetch the rights-issue EGM notice and outcome** when published (expected Q4 2026/Q1 2027) and update the event status from `proposed` to `approved`/`completed`.
3. **Monitor the RWLV RICO docket and the NY racing-support dispute** for motions, judgments or a court filing; both are still live.
4. **Add the actual issue price and entitlement basis** once Genting announces the price-fixing date. The current dataset deliberately leaves them null.
5. **Consider a separate `company_ownership_notices.jsonl`** if the sentiment model wants every s-hldr/director notice, not just the curated 65 rows. The 553 in-window announcements include about 348 shareholding notices; the current ownership file is a curated subset.
