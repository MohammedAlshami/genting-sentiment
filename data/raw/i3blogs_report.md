# i3investor blog collection report — GENTING and GENM

**Source:** i3investor blog (`klse.i3investor.com/web/blog/detail/...`)  
**Source id:** `i3blog` (separate from the `i3investor` forum source)  
**Window:** 2 November 2024 00:00 MYT → 2 November 2026 23:59 MYT  
**Output:** `data/raw/i3blogs.jsonl` — **216 records** (155 articles + 61 comments)

| Metric | Value |
| --- | --- |
| Articles | 155 |
| Comments | 61 |
| Articles with ≥1 comment | 19 |
| Articles with 0 comments (no replies or comments disabled) | 136 |
| GENTING articles | 69 |
| GENM articles | 86 |
| UNKNOWN ticker | 0 |
| First article (UTC) | 2024-11-06 02:42 |
| Last article (UTC) | 2026-10-19 04:18 |
| First comment (UTC) | 2024-12-05 09:50 |
| Last comment (UTC) | 2025-12-08 09:36 |

## 1. How the blogs were found

1. **Per-stock News & Blogs pages** — `/web/stock/news-blogs/3182` and `/4715`. These list the last 12 months (2025-11-04 → 2026-11-01) and supplied the current-year core.
2. **Wayback Machine snapshots** of the two stock pages, the stock overview pages, and the blog headline feed (2024-12-08, 2024-12-12, 2025-01-24, 2025-06-20, 2025-08-14, 2025-11-04). These supplied late-2024 / early-2025 articles and spot coverage of mid-2025.
3. **Author blog archives** — every author with a Genting article in the seed set was followed through `/web/cube/blog/blposts/<blog>/<user>?p=N` (50 posts per page). Low-volume blogs were paged back to 2024-11-02; high-volume research-house blogs were paged through the 2024-11-02 → 2025-11-03 gap (209 pages for CEO Morning Brief, 28 for TA Research, 25 for PublicInvest, 18 for Mercury, 10 for M+ Online, 9 for HL Research, 4 for STR, etc.).
4. **Targeted search results** for gap months (Feb–Oct 2025) were added manually where the archive crawl did not reach (e.g. the 2025-01-13 CGS-CIMB report, 2025-06-02 kltrader, 2025-10-13 trading-halt posts).

Discovery produced 22,993 candidate blog posts from the stock/Wayback seeds, plus 1,193 from a second pass over five one-off trading blogs (CGS-CIMB, kltrader, CP Teh, NagaWarrants, cp22). After title filtering and de-duplication, 239 Genting-titled articles were fetched and reviewed; 155 are in the final in-scope set.

## 2. Coverage by month

| Month | Articles | | Month | Articles |
| --- | ---: | --- | --- | ---: |
| 2024-11 | 8 | | 2025-10 | 17 |
| 2024-12 | 8 | | 2025-11 | 16 |
| 2025-01 | 3 | | 2025-12 | 13 |
| 2025-02 | 12 | | 2026-02 | 7 |
| 2025-03 | 9 | | 2026-03 | 1 |
| 2025-04 | 3 | | 2026-04 | 1 |
| 2025-05 | 13 | | 2026-05 | 8 |
| 2025-06 | 3 | | 2026-07 | 1 |
| 2025-07 | 4 | | 2026-08 | 9 |
| 2025-08 | 10 | | 2026-09 | 1 |
| 2025-09 | 4 | | 2026-10 | 4 |

## 3. Articles by author / blog

| Author | Articles |
| --- | ---: |
| edgeinvest | 49 |
| PublicInvest | 23 |
| PhillipCapital | 20 |
| sectoranalyst | 20 |
| BLee | 10 |
| StockTipRatings | 8 |
| CP Teh | 6 |
| NagaWarrants | 5 |
| HLInvest | 5 |
| MercurySec | 4 |
| savemalaysia | 3 |
| kltrader | 2 |

## 4. Articles with comments

| Date (UTC) | Ticker | Author | Title | Comments |
| --- | --- | --- | --- | ---: |
| 2024-12-05 | GENTING | edgeinvest | [Genting, Genting Malaysia to be Dropped From FBM KLCI — Sources](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2024-12-05-story-h475736792-Genting_Genting_Malaysia_to_be_Dropped_From_FBM_KLCI_8212_Sources) | 1 |
| 2024-12-18 | GENTING | edgeinvest | [Genting, GenM Skid to Four-year Lows as Investors Look Past Analysts' 'buy' Calls](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2024-12-18-story-h476691999-Genting_GenM_Skid_to_Four_year_Lows_as_Investors_Look_Past_Analysts_39_3) | 3 |
| 2024-12-27 | GENTING | MercurySec | [Genting (3182) - Breaking Free From Consolidation Mode?](https://klse.i3investor.com/web/blog/detail/mercurysec/2024-12-27-story-h496895164-Genting_3182_Breaking_Free_From_Consolidation_Mode) | 2 |
| 2025-02-14 | GENM | MercurySec | [Genting Malaysia (4715) - Inverse Head and Shoulder Breakout](https://klse.i3investor.com/web/blog/detail/mercurysec/2025-02-14-story-h498615227-Genting_Malaysia_4715_Inverse_Head_and_Shoulder_Breakout) | 1 |
| 2025-02-28 | GENTING | PublicInvest | [Genting Berhad - Weaker Contribution From The US & Singapore](https://klse.i3investor.com/web/blog/detail/PublicInvest/2025-02-28-story-h498647843-Genting_Berhad_Weaker_Contribution_From_The_US_amp_Singapore) | 1 |
| 2025-02-28 | GENM | PhillipCapital | [Genting Malaysia (GENM MK) - Just as we thought things were better](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2025-02-28-story-h498648053-Genting_Malaysia_GENM_MK_Just_as_we_thought_things_were_better) | 2 |
| 2025-02-28 | GENTING | edgeinvest | [Lim Kok Thay to Relinquish CEO Post at Genting, Remain as Executive Chairman](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-02-28-story-h498648832-Lim_Kok_Thay_to_Relinquish_CEO_Post_at_Genting_Remain_as_Executive_Chair) | 2 |
| 2025-03-01 | GENM | BLee | [GenM: A Billion $ Questions? **(Updated with Detail 9)**](https://klse.i3investor.com/web/blog/detail/BLeeGenting/2025-03-01-story-h498649855-GenM_A_Billion_Questions) | 24 |
| 2025-03-13 | GENTING | edgeinvest | [Lim Family Scoops Up Battered Genting Shares](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-03-13-story-h498679553-Lim_Family_Scoops_Up_Battered_Genting_Shares) | 2 |
| 2025-03-27 | GENM | CP Teh | [New 52W low : GenM](https://klse.i3investor.com/web/blog/detail/cpteh25/2025-03-27-story-h498708568-New_52W_low_GenM) | 1 |
| 2025-08-18 | GENM | sectoranalyst | [Genting Malaysia Berhad - Disposals of Non-Gaming Assets in RWC](https://klse.i3investor.com/web/blog/detail/taresearch/2025-08-18-story-h499694341-Genting_Malaysia_Berhad_Disposals_of_Non_Gaming_Assets_in_RWC) | 2 |
| 2025-09-11 | GENTING | edgeinvest | [Sluggish Ops Weigh on Genting, Watch Out for New York Licence Bid, S&P Flags](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-09-11-story-h499776117-Sluggish_Ops_Weigh_on_Genting_Watch_Out_for_New_York_Licence_Bid_S_amp_P) | 1 |
| 2025-10-14 | GENTING | sectoranalyst | [Gaming Sector - Unattractive VGO to Privatise Genting Malaysia](https://klse.i3investor.com/web/blog/detail/taresearch/2025-10-14-story-h500462269-Gaming_Sector_Unattractive_VGO_to_Privatise_Genting_Malaysia) | 1 |
| 2025-10-15 | GENM | BLee | [GenM: The Options..](https://klse.i3investor.com/web/blog/detail/BLeeGenting/2025-10-15-story-h500464099-GenM_The_Options) | 2 |
| 2025-10-29 | GENM | StockTipRatings | [Top Analyst Says GENM’s New York Casino License Bid Is the Strongest, Sees Earnings Boom Ahead](https://klse.i3investor.com/web/blog/detail/strblog/2025-10-29-story-h500492094-Top_Analyst_Says_GENM_s_New_York_Casino_License_Bid_Is_the_Strongest_See) | 1 |
| 2025-11-04 | GENTING | edgeinvest | [Genting’s Takeover Offer for GENM Turns Unconditional After Crossing 50% Threshold](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-11-04-story-h500495780-Genting_8217_s_Takeover_Offer_for_GENM_Turns_Unconditional_After_Crossin) | 1 |
| 2025-11-08 | GENM | BLee | [GenM: How is the take-up rate of Voluntary Take-over Offer by GenT?](https://klse.i3investor.com/web/blog/detail/BLeeGenting/2025-11-08-story-h500498756-GenM_How_is_the_take_up_rate_of_Voluntary_Take_over_Offer_by_GenT) | 3 |
| 2025-11-14 | GENTING | edgeinvest | [Genting Extends Takeover Offer for Genting Malaysia to Dec 1](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-11-14-story-h500522963-Genting_Extends_Takeover_Offer_for_Genting_Malaysia_to_Dec_1) | 1 |
| 2025-12-07 | GENM | BLee | [GenM: What will happen when GenT ‘Burst’ through 75% of GenM shareholdings?](https://klse.i3investor.com/web/blog/detail/BLeeGenting/2025-12-07-story-h500581403-GenM_What_will_happen_when_GenT_Burst_through_75_of_GenM_shareholdings) | 10 |

## 5. All collected articles

| Date (UTC) | Ticker | Author | Title | Comments |
| --- | --- | --- | --- | ---: |
| 2024-11-06 | GENTING | savemalaysia | [“Genting, Genting M’sia risk exit from FBM KLCI; Gamuda and 99 Speedmart may gain entry”](https://klse.i3investor.com/web/blog/detail/savemalaysia/2024-11-06-story-h473653278-_Genting_Genting_M_sia_risk_exit_from_FBM_KLCI_Gamuda_and_99_Speedmart_m) | 0 |
| 2024-11-29 | GENTING | edgeinvest | [Genting's 3Q Net Profit More Than Halves on Higher Write-off](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2024-11-29-story-h475561892-Genting_39_s_3Q_Net_Profit_More_Than_Halves_on_Higher_Write_off) | 0 |
| 2024-11-29 | GENTING | PublicInvest | [Genting Berhad - Weaker Contribution From Singapore](https://klse.i3investor.com/web/blog/detail/PublicInvest/2024-11-29-story-h475562668-Genting_Berhad_Weaker_Contribution_From_Singapore) | 0 |
| 2024-11-29 | GENM | PublicInvest | [Genting Malaysia Berhad - Higher Operating Expenses](https://klse.i3investor.com/web/blog/detail/PublicInvest/2024-11-29-story-h475562669-Genting_Malaysia_Berhad_Higher_Operating_Expenses) | 0 |
| 2024-11-29 | GENM | PhillipCapital | [Genting Malaysia (GENM MK) - Finally, a Decent Quarter](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2024-11-29-story-h475562819-Genting_Malaysia_GENM_MK_Finally_a_Decent_Quarter) | 0 |
| 2024-11-29 | GENTING | PhillipCapital | [Genting Berhad (GENT MK) - Drag From Genting Singapore](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2024-11-29-story-h475562820-Genting_Berhad_GENT_MK_Drag_From_Genting_Singapore) | 0 |
| 2024-11-29 | GENTING | sectoranalyst | [Genting Berhad - Lacklustre Singapore Operations](https://klse.i3investor.com/web/blog/detail/taresearch/2024-11-29-story-h475563754-Genting_Berhad_Lacklustre_Singapore_Operations) | 0 |
| 2024-11-29 | GENM | sectoranalyst | [Genting Malaysia Berhad - Increase in Foreign VIPs in 3Q24](https://klse.i3investor.com/web/blog/detail/taresearch/2024-11-29-story-h475563778-Genting_Malaysia_Berhad_Increase_in_Foreign_VIPs_in_3Q24) | 0 |
| 2024-12-03 | GENM | savemalaysia | [Genting Malaysia delays reopening of two casino floors at Resorts World Genting](https://klse.i3investor.com/web/blog/detail/savemalaysia/2024-12-03-story-h475652253-Genting_Malaysia_delays_reopening_of_two_casino_floors_at_Resorts_World_) | 0 |
| 2024-12-04 | GENM | CP Teh | [Stock Watch : Genting](https://klse.i3investor.com/web/blog/detail/cp22/2024-12-04-story-h475706785-Stock_Watch_Genting) | 0 |
| 2024-12-05 | GENTING | edgeinvest | [Genting, Genting Malaysia to be Dropped From FBM KLCI — Sources](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2024-12-05-story-h475736792-Genting_Genting_Malaysia_to_be_Dropped_From_FBM_KLCI_8212_Sources) | 1 |
| 2024-12-06 | GENTING | edgeinvest | [FBM KLCI Review: Gamuda and 99 Speed Mart In, Genting and Genting Malaysia Out](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2024-12-06-story-h475767544-FBM_KLCI_Review_Gamuda_and_99_Speed_Mart_In_Genting_and_Genting_Malaysia) | 0 |
| 2024-12-17 | GENTING | savemalaysia | [Genting, Genting Malaysia shares hit four-year lows; analysts say negatives priced in](https://klse.i3investor.com/web/blog/detail/savemalaysia/2024-12-17-story-h476665951-Genting_Genting_Malaysia_shares_hit_four_year_lows_analysts_say_negative) | 0 |
| 2024-12-18 | GENTING | edgeinvest | [Genting, GenM Skid to Four-year Lows as Investors Look Past Analysts' 'buy' Calls](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2024-12-18-story-h476691999-Genting_GenM_Skid_to_Four_year_Lows_as_Investors_Look_Past_Analysts_39_3) | 3 |
| 2024-12-24 | GENM | MercurySec | [Genting Malaysia (4715) - Breakout Above 20-day EMA](https://klse.i3investor.com/web/blog/detail/mercurysec/2024-12-24-story-h496856720-Genting_Malaysia_4715_Breakout_Above_20_day_EMA) | 0 |
| 2024-12-27 | GENTING | MercurySec | [Genting (3182) - Breaking Free From Consolidation Mode?](https://klse.i3investor.com/web/blog/detail/mercurysec/2024-12-27-story-h496895164-Genting_3182_Breaking_Free_From_Consolidation_Mode) | 2 |
| 2025-01-13 | GENM | sectoranalyst | [Genting Malaysia - Key beneficiary of robust tourism recovery](https://klse.i3investor.com/web/blog/detail/cgscimbresearch/2025-01-13-story-h497899193-Genting_Malaysia_Key_beneficiary_of_robust_tourism_recovery) | 0 |
| 2025-01-20 | GENM | NagaWarrants | [Trading Idea - Genting Malaysia Berhad](https://klse.i3investor.com/web/blog/detail/kenangawarrants/2025-01-20-story-h497931983-Trading_Idea_Genting_Malaysia_Berhad) | 0 |
| 2025-01-21 | GENM | PhillipCapital | [Genting Malaysia (GENM MK) - Expedited Full Re-opening of Genting Casino?](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2025-01-21-story-h497933750-Genting_Malaysia_GENM_MK_Expedited_Full_Re_opening_of_Genting_Casino) | 0 |
| 2025-02-02 | GENTING | BLee | [Facts and Figures on GenT/GenM](https://klse.i3investor.com/web/blog/detail/BLeeGenting/2025-02-02-story-h498587292-Facts_and_Figures_on_GenT_GenM) | 0 |
| 2025-02-14 | GENM | MercurySec | [Genting Malaysia (4715) - Inverse Head and Shoulder Breakout](https://klse.i3investor.com/web/blog/detail/mercurysec/2025-02-14-story-h498615227-Genting_Malaysia_4715_Inverse_Head_and_Shoulder_Breakout) | 1 |
| 2025-02-21 | GENTING | PublicInvest | [Genting Berhad - GENS: Dragged By Higher Operating Cost & Impairment](https://klse.i3investor.com/web/blog/detail/PublicInvest/2025-02-21-story-h498620866-Genting_Berhad_GENS_Dragged_By_Higher_Operating_Cost_amp_Impairment) | 0 |
| 2025-02-21 | GENTING | edgeinvest | [Genting to Add 100 Megawatts in Second Phase of Aquaculture Solar Farm in China](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-02-21-story-h498620962-Genting_to_Add_100_Megawatts_in_Second_Phase_of_Aquaculture_Solar_Farm_i) | 0 |
| 2025-02-28 | GENM | PublicInvest | [Genting Malaysia Berhad - Dragged By Higher Costs](https://klse.i3investor.com/web/blog/detail/PublicInvest/2025-02-28-story-h498647836-Genting_Malaysia_Berhad_Dragged_By_Higher_Costs) | 0 |
| 2025-02-28 | GENTING | PublicInvest | [Genting Berhad - Weaker Contribution From The US & Singapore](https://klse.i3investor.com/web/blog/detail/PublicInvest/2025-02-28-story-h498647843-Genting_Berhad_Weaker_Contribution_From_The_US_amp_Singapore) | 1 |
| 2025-02-28 | GENM | CP Teh | [52w low : Genting Malaysia](https://klse.i3investor.com/web/blog/detail/cpteh25/2025-02-28-story-h498647871-52w_low_Genting_Malaysia) | 0 |
| 2025-02-28 | GENTING | sectoranalyst | [Genting Berhad - A Surprised Quarterly Loss in 4Q24](https://klse.i3investor.com/web/blog/detail/taresearch/2025-02-28-story-h498647932-Genting_Berhad_A_Surprised_Quarterly_Loss_in_4Q24) | 0 |
| 2025-02-28 | GENM | sectoranalyst | [Genting Malaysia Berhad - Close With a Whimper](https://klse.i3investor.com/web/blog/detail/taresearch/2025-02-28-story-h498647933-Genting_Malaysia_Berhad_Close_With_a_Whimper) | 0 |
| 2025-02-28 | GENM | PhillipCapital | [Genting Berhad (GENT MK) - Expect further margin compression](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2025-02-28-story-h498648052-Genting_Berhad_GENT_MK_Expect_further_margin_compression) | 0 |
| 2025-02-28 | GENM | PhillipCapital | [Genting Malaysia (GENM MK) - Just as we thought things were better](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2025-02-28-story-h498648053-Genting_Malaysia_GENM_MK_Just_as_we_thought_things_were_better) | 2 |
| 2025-02-28 | GENTING | edgeinvest | [Lim Kok Thay to Relinquish CEO Post at Genting, Remain as Executive Chairman](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-02-28-story-h498648832-Lim_Kok_Thay_to_Relinquish_CEO_Post_at_Genting_Remain_as_Executive_Chair) | 2 |
| 2025-03-01 | GENM | BLee | [GenM: A Billion $ Questions? **(Updated with Detail 9)**](https://klse.i3investor.com/web/blog/detail/BLeeGenting/2025-03-01-story-h498649855-GenM_A_Billion_Questions) | 24 |
| 2025-03-03 | GENTING | NagaWarrants | [Weekly Trading Idea - Genting Bhd](https://klse.i3investor.com/web/blog/detail/kenangawarrants/2025-03-03-story-h498649979-Weekly_Trading_Idea_Genting_Bhd) | 0 |
| 2025-03-04 | GENM | CP Teh | [SELLDOWN : GenM](https://klse.i3investor.com/web/blog/detail/cpteh25/2025-03-04-story-h498652615-SELLDOWN_GenM) | 0 |
| 2025-03-06 | GENM | kltrader | [Genting Malaysia - Hard Decisions to be Made](https://klse.i3investor.com/web/blog/detail/kltrader/2025-03-06-story-h498679680-Genting_Malaysia_Hard_Decisions_to_be_Made) | 0 |
| 2025-03-13 | GENTING | edgeinvest | [Lim Family Scoops Up Battered Genting Shares](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-03-13-story-h498679553-Lim_Family_Scoops_Up_Battered_Genting_Shares) | 2 |
| 2025-03-20 | GENM | PhillipCapital | [Genting Malaysia (GENM MK) - Losing its shine; downgrade to HOLD](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2025-03-20-story-h498703576-Genting_Malaysia_GENM_MK_Losing_its_shine_downgrade_to_HOLD) | 0 |
| 2025-03-25 | GENTING | edgeinvest | [Analysts Positive on Resorts World Las Vegas Retaining Licence Despite Hefty Nevada Fine](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-03-25-story-h498706457-Analysts_Positive_on_Resorts_World_Las_Vegas_Retaining_Licence_Despite_H) | 0 |
| 2025-03-27 | GENM | CP Teh | [New 52W low : GenM](https://klse.i3investor.com/web/blog/detail/cpteh25/2025-03-27-story-h498708568-New_52W_low_GenM) | 1 |
| 2025-03-28 | GENM | CP Teh | [GenM : New 52W low](https://klse.i3investor.com/web/blog/detail/cpteh25/2025-03-28-story-h498709532-GenM_New_52W_low) | 0 |
| 2025-04-07 | GENTING | PhillipCapital | [Genting Berhad (GENT MK) - At a crossroads](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2025-04-07-story-h498763317-Genting_Berhad_GENT_MK_At_a_crossroads) | 0 |
| 2025-04-09 | GENM | PublicInvest | [Technical Buy - GENM (4715)](https://klse.i3investor.com/web/blog/detail/PublicInvest/2025-04-09-story-h498766973-Technical_Buy_GENM_4715) | 0 |
| 2025-04-21 | GENM | PublicInvest | [TECHNICAL BUY: GENM (4715)](https://klse.i3investor.com/web/blog/detail/PublicInvest/2025-04-21-story-h498795988-TECHNICAL_BUY_GENM_4715) | 0 |
| 2025-05-05 | GENM | PublicInvest | [Genting Malaysia Berhad - Unfavourable Related Party Transaction](https://klse.i3investor.com/web/blog/detail/PublicInvest/2025-05-05-story-h498825656-Genting_Malaysia_Berhad_Unfavourable_Related_Party_Transaction) | 0 |
| 2025-05-06 | GENM | edgeinvest | [‘Pricey’ Deal for Empire Resorts to Drag Genting Malaysia’s Earnings — Analysts](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-05-06-story-h498826708-_8216_Pricey_8217_Deal_for_Empire_Resorts_to_Drag_Genting_Malaysia_8217_) | 0 |
| 2025-05-08 | GENTING | edgeinvest | [CreditSights Flags Genting Malaysia's Takeover of Empire Resorts as Credit Negative Amid Debt, ](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-05-08-story-h498829436-CreditSights_Flags_Genting_Malaysia_39_s_Takeover_of_Empire_Resorts_as_C) | 0 |
| 2025-05-09 | GENM | edgeinvest | [Bursa Grills Genting Malaysia Over US$41m Empire Resorts Buyout](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-05-09-story-h498830526-Bursa_Grills_Genting_Malaysia_Over_US_41m_Empire_Resorts_Buyout) | 0 |
| 2025-05-30 | GENTING | PublicInvest | [Genting Berhad - Disappointing Results](https://klse.i3investor.com/web/blog/detail/PublicInvest/2025-05-30-story-h499513852-Genting_Berhad_Disappointing_Results) | 0 |
| 2025-05-30 | GENM | PublicInvest | [Genting Malaysia Berhad - Earnings Recovery Remained Weak](https://klse.i3investor.com/web/blog/detail/PublicInvest/2025-05-30-story-h499513858-Genting_Malaysia_Berhad_Earnings_Recovery_Remained_Weak) | 0 |
| 2025-05-30 | GENM | HLInvest | [Genting Malaysia - Registered a mild profit](https://klse.i3investor.com/web/blog/detail/hleresearch/2025-05-30-story-h499513884-Genting_Malaysia_Registered_a_mild_profit) | 0 |
| 2025-05-30 | GENTING | HLInvest | [Genting - Dragged by GenM and GenS](https://klse.i3investor.com/web/blog/detail/hleresearch/2025-05-30-story-h499513885-Genting_Dragged_by_GenM_and_GenS) | 0 |
| 2025-05-30 | GENM | PhillipCapital | [Genting Malaysia (GENM MK) - Missed expectations](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2025-05-30-story-h499513916-Genting_Malaysia_GENM_MK_Missed_expectations) | 0 |
| 2025-05-30 | GENM | sectoranalyst | [Genting Malaysia Berhad - Challenging Outlook](https://klse.i3investor.com/web/blog/detail/taresearch/2025-05-30-story-h499514689-Genting_Malaysia_Berhad_Challenging_Outlook) | 0 |
| 2025-05-30 | GENTING | sectoranalyst | [Genting Berhad - Simultaneous Setbacks](https://klse.i3investor.com/web/blog/detail/taresearch/2025-05-30-story-h499514694-Genting_Berhad_Simultaneous_Setbacks) | 0 |
| 2025-05-30 | GENM | edgeinvest | [Forex Gain Lifts Genting Malaysia's 1Q Profit Despite Revenue Slip](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-05-30-story-h499514845-Forex_Gain_Lifts_Genting_Malaysia_39_s_1Q_Profit_Despite_Revenue_Slip) | 0 |
| 2025-05-30 | GENTING | edgeinvest | [Genting's 1Q Net Profit Down Sharply Amid Lower Revenues From Casinos and Higher Taxation](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-05-30-story-h499514846-Genting_39_s_1Q_Net_Profit_Down_Sharply_Amid_Lower_Revenues_From_Casinos) | 0 |
| 2025-06-02 | GENM | kltrader | [Genting Malaysia - Bringing a Painful Chapter to a Close](https://klse.i3investor.com/web/blog/detail/kltrader/2025-06-02-story-h499537788-Genting_Malaysia_Bringing_a_Painful_Chapter_to_a_Close) | 0 |
| 2025-06-02 | GENM | BLee | [GenM Resort World Empire Inc: Fiction to Reality..](https://klse.i3investor.com/web/blog/detail/BLeeGenting/2025-06-03-story-h499515839-GenM_Resort_World_Empire_Inc_Fiction_to_Reality) | 0 |
| 2025-06-30 | GENM | NagaWarrants | [Weekly Trading Idea - Genting Malaysia Bhd](https://klse.i3investor.com/web/blog/detail/kenangawarrants/2025-06-30-story-h499576354-Weekly_Trading_Idea_Genting_Malaysia_Bhd) | 0 |
| 2025-07-01 | GENM | edgeinvest | [Genting Malaysia Submits Bid for New York Casino Licence](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-07-01-story-h499599194-Genting_Malaysia_Submits_Bid_for_New_York_Casino_Licence) | 0 |
| 2025-07-02 | GENTING | edgeinvest | [Genting Hands Over Coal Plant in China After PPA Expiry, Pivots to Clean Energy](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-07-02-story-h499600190-Genting_Hands_Over_Coal_Plant_in_China_After_PPA_Expiry_Pivots_to_Clean_) | 0 |
| 2025-07-08 | GENM | edgeinvest | [US Court Dismisses Initial Suit by Genting Malaysia's Business Partner, Allows Amended Complain](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-07-08-story-h499603287-US_Court_Dismisses_Initial_Suit_by_Genting_Malaysia_39_s_Business_Partne) | 0 |
| 2025-07-10 | GENTING | edgeinvest | [New York City Casinos Could Become World’s Biggest, Genting Sees Jump in Revenue](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-07-10-story-h499605957-New_York_City_Casinos_Could_Become_World_8217_s_Biggest_Genting_Sees_Jum) | 0 |
| 2025-08-18 | GENM | PublicInvest | [Genting Malaysia Berhad - Restructuring of Loss-Making Unit](https://klse.i3investor.com/web/blog/detail/PublicInvest/2025-08-18-story-h499693595-Genting_Malaysia_Berhad_Restructuring_of_Loss_Making_Unit) | 0 |
| 2025-08-18 | GENM | sectoranalyst | [Genting Malaysia Berhad - Disposals of Non-Gaming Assets in RWC](https://klse.i3investor.com/web/blog/detail/taresearch/2025-08-18-story-h499694341-Genting_Malaysia_Berhad_Disposals_of_Non_Gaming_Assets_in_RWC) | 2 |
| 2025-08-28 | GENM | edgeinvest | [Bond Issue to Fund Purchase of Genting’s Casino in Upstate New York Delayed, Bloomberg Reports](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-08-28-story-h499725310-Bond_Issue_to_Fund_Purchase_of_Genting_8217_s_Casino_in_Upstate_New_York) | 0 |
| 2025-08-29 | GENM | PublicInvest | [Genting Malaysia Berhad - Higher Gaming Profit & Forex Gains](https://klse.i3investor.com/web/blog/detail/PublicInvest/2025-08-29-story-h499746418-Genting_Malaysia_Berhad_Higher_Gaming_Profit_amp_Forex_Gains) | 0 |
| 2025-08-29 | GENTING | PublicInvest | [Genting Berhad - Weaker Contribution From The US](https://klse.i3investor.com/web/blog/detail/PublicInvest/2025-08-29-story-h499746419-Genting_Berhad_Weaker_Contribution_From_The_US) | 0 |
| 2025-08-29 | GENTING | sectoranalyst | [Genting Berhad - Dragged by GENS and RWLV](https://klse.i3investor.com/web/blog/detail/taresearch/2025-08-29-story-h499747160-Genting_Berhad_Dragged_by_GENS_and_RWLV) | 0 |
| 2025-08-29 | GENM | sectoranalyst | [Genting Malaysia Berhad - Recovery in Sight](https://klse.i3investor.com/web/blog/detail/taresearch/2025-08-29-story-h499747161-Genting_Malaysia_Berhad_Recovery_in_Sight) | 0 |
| 2025-08-29 | GENM | PhillipCapital | [Genting Malaysia (GENM MK) - Earnings beat expectations](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2025-08-29-story-h499747258-Genting_Malaysia_GENM_MK_Earnings_beat_expectations) | 0 |
| 2025-08-29 | GENTING | edgeinvest | [Genting's 2Q Profit Edges Up 1.6% to RM244 Mil on Asset Disposals, Turnaround in JVs](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-08-29-story-h499748179-Genting_39_s_2Q_Profit_Edges_Up_1_6_to_RM244_Mil_on_Asset_Disposals_Turn) | 0 |
| 2025-08-29 | GENM | edgeinvest | [Genting Malaysia’s 2Q Profit Jumps Fivefold as Quarterly Revenue Hits Record High](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-08-29-story-h499748181-Genting_Malaysia_8217_s_2Q_Profit_Jumps_Fivefold_as_Quarterly_Revenue_Hi) | 0 |
| 2025-09-02 | GENM | NagaWarrants | [‼️GENM-C3O & GENM-C3E‼️](https://klse.i3investor.com/web/blog/detail/kenangawarrants/2025-09-02-story-h499749140-_GENM_C3O_GENM_C3E) | 0 |
| 2025-09-02 | GENTING | PhillipCapital | [Genting Berhad (GENT MK) - Missing expectations](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2025-09-02-story-h499749240-Genting_Berhad_GENT_MK_Missing_expectations) | 0 |
| 2025-09-11 | GENTING | edgeinvest | [Sluggish Ops Weigh on Genting, Watch Out for New York Licence Bid, S&P Flags](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-09-11-story-h499776117-Sluggish_Ops_Weigh_on_Genting_Watch_Out_for_New_York_Licence_Bid_S_amp_P) | 1 |
| 2025-09-18 | GENM | edgeinvest | [Genting Malaysia's US Unit to Contest Amended US$600 Mil Lawsuit Filed by Business Partner](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-09-18-story-h499779898-Genting_Malaysia_39_s_US_Unit_to_Contest_Amended_US_600_Mil_Lawsuit_File) | 0 |
| 2025-10-13 | GENM | NagaWarrants | [Trading Halt of Trading on GENTING & GENM](https://klse.i3investor.com/web/blog/detail/kenangawarrants/2025-10-13-story-h500461433-Trading_Halt_of_Trading_on_GENTING_GENM) | 0 |
| 2025-10-13 | GENM | CP Teh | [Stock Watch : GenM](https://klse.i3investor.com/web/blog/detail/cpteh25/2025-10-13-story-h500462180-Stock_Watch_GenM) | 0 |
| 2025-10-14 | GENM | PublicInvest | [GAMING - Proposed Privatisation of GENM](https://klse.i3investor.com/web/blog/detail/PublicInvest/2025-10-14-story-h500462208-GAMING_Proposed_Privatisation_of_GENM) | 0 |
| 2025-10-14 | GENM | StockTipRatings | [Top Analyst Urges Shareholders to Reject Takeover Offer for GENM, Citing Potential Casino Licen](https://klse.i3investor.com/web/blog/detail/strblog/2025-10-14-story-h500462237-Top_Analyst_Urges_Shareholders_to_Reject_Takeover_Offer_for_GENM_Citing_) | 0 |
| 2025-10-14 | GENTING | sectoranalyst | [Gaming Sector - Unattractive VGO to Privatise Genting Malaysia](https://klse.i3investor.com/web/blog/detail/taresearch/2025-10-14-story-h500462269-Gaming_Sector_Unattractive_VGO_to_Privatise_Genting_Malaysia) | 1 |
| 2025-10-14 | GENM | PhillipCapital | [Genting Malaysia (GENM MK) - Conditional voluntary take-over offer at RM2.35](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2025-10-14-story-h500462271-Genting_Malaysia_GENM_MK_Conditional_voluntary_take_over_offer_at_RM2_35) | 0 |
| 2025-10-14 | GENTING | edgeinvest | [Genting to Privatise Genting Malaysia in RM2.35-per-share Buyout](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-10-14-story-h500462427-Genting_to_Privatise_Genting_Malaysia_in_RM2_35_per_share_Buyout) | 0 |
| 2025-10-14 | GENTING | StockTipRatings | [Top Analyst Says GENTING Unlikely to Privatise GENM as Shareholders Still Face Losses](https://klse.i3investor.com/web/blog/detail/strblog/2025-10-14-story-h500463132-Top_Analyst_Says_GENTING_Unlikely_to_Privatise_GENM_as_Shareholders_Stil) | 0 |
| 2025-10-15 | GENTING | edgeinvest | [Genting Malaysia Takeover Splits Analysts Amid Valuation Debate, New York Casino Bid](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-10-15-story-h500463386-Genting_Malaysia_Takeover_Splits_Analysts_Amid_Valuation_Debate_New_York) | 0 |
| 2025-10-15 | GENM | BLee | [GenM: The Options..](https://klse.i3investor.com/web/blog/detail/BLeeGenting/2025-10-15-story-h500464099-GenM_The_Options) | 2 |
| 2025-10-16 | GENTING | edgeinvest | [MGM's Withdrawal From NY Casino Project leaves Genting, Two Other bidders in the Race](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-10-16-story-h500464341-MGM_39_s_Withdrawal_From_NY_Casino_Project_nbsp_leaves_Genting_Two_Other) | 0 |
| 2025-10-17 | GENTING | edgeinvest | [Moody's Places Genting on Downgrade Watch Over Debt-funded Acquisition of Genting Malaysia](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-10-17-story-h500465305-Moody_39_s_Places_Genting_on_Downgrade_Watch_Over_Debt_funded_Acquisitio) | 0 |
| 2025-10-17 | GENTING | edgeinvest | [Genting Climbs to Seven-month High on GenM New York Licence Bid Optimism](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-10-17-story-h500465306-Genting_Climbs_to_Seven_month_High_on_GenM_New_York_Licence_Bid_Optimism) | 0 |
| 2025-10-20 | GENM | StockTipRatings | [Is Genting Malaysia’s Privatization Offer a Fair Deal? Here’s What Expects Say](https://klse.i3investor.com/web/blog/detail/strblog/2025-10-20-story-h500466047-Is_Genting_Malaysia_s_Privatization_Offer_a_Fair_Deal_Here_s_What_Expect) | 0 |
| 2025-10-24 | GENTING | edgeinvest | [Genting Resorts World Catskills Hotel’s US$561 Mil municipal Bond Sale Delayed Over Merger](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-10-24-story-h500469085-Genting_Resorts_World_Catskills_Hotel_8217_s_US_561_Mil_nbsp_municipal_B) | 0 |
| 2025-10-25 | GENM | BLee | [GenM: Why complicate the Offer with Two easy Options?](https://klse.i3investor.com/web/blog/detail/BLeeGenting/2025-10-25-story-h500469859-GenM_Why_complicate_the_Offer_with_Two_easy_Options) | 0 |
| 2025-10-29 | GENM | StockTipRatings | [Top Analyst Says GENM’s New York Casino License Bid Is the Strongest, Sees Earnings Boom Ahead](https://klse.i3investor.com/web/blog/detail/strblog/2025-10-29-story-h500492094-Top_Analyst_Says_GENM_s_New_York_Casino_License_Bid_Is_the_Strongest_See) | 1 |
| 2025-11-04 | GENTING | edgeinvest | [Genting’s Takeover Offer for GENM Turns Unconditional After Crossing 50% Threshold](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-11-04-story-h500495780-Genting_8217_s_Takeover_Offer_for_GENM_Turns_Unconditional_After_Crossin) | 1 |
| 2025-11-06 | GENM | edgeinvest | [Bakri MP Flags Potentially Suspicious Genting Malaysia Stock Movements; Govt Says Trading Appea](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-11-06-story-h500496959-Bakri_MP_Flags_Potentially_Suspicious_Genting_Malaysia_Stock_Movements_G) | 0 |
| 2025-11-08 | GENM | BLee | [GenM: How is the take-up rate of Voluntary Take-over Offer by GenT?](https://klse.i3investor.com/web/blog/detail/BLeeGenting/2025-11-08-story-h500498756-GenM_How_is_the_take_up_rate_of_Voluntary_Take_over_Offer_by_GenT) | 3 |
| 2025-11-11 | GENTING | edgeinvest | [Genting Taps Bond Market for RM900m to Finance Genting Malaysia Acquisition](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-11-11-story-h500499836-Genting_Taps_Bond_Market_for_RM900m_to_Finance_Genting_Malaysia_Acquisit) | 0 |
| 2025-11-14 | GENTING | edgeinvest | [Independent Adviser Tells Genting Malaysia Shareholders to Reject Genting’s RM2.35 a Share Offe](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-11-14-story-h500522962-Independent_Adviser_Tells_Genting_Malaysia_Shareholders_to_Reject_Gentin) | 0 |
| 2025-11-14 | GENTING | edgeinvest | [Genting Extends Takeover Offer for Genting Malaysia to Dec 1](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-11-14-story-h500522963-Genting_Extends_Takeover_Offer_for_Genting_Malaysia_to_Dec_1) | 1 |
| 2025-11-15 | GENM | BLee | [GenM: The ‘Offer’ gets a bit Complicated!](https://klse.i3investor.com/web/blog/detail/BLeeGenting/2025-11-16-story-h500523676-GenM_The_Offer_gets_a_bit_Complicated) | 0 |
| 2025-11-23 | GENM | BLee | [GenM: The True or False?](https://klse.i3investor.com/web/blog/detail/BLeeGenting/2025-11-23-story-h500528700-GenM_The_True_or_False) | 0 |
| 2025-11-28 | GENM | PublicInvest | [Genting Malaysia Berhad - Dragged By Higher Costs & Lower Forex Gains](https://klse.i3investor.com/web/blog/detail/PublicInvest/2025-11-28-story-h500554458-Genting_Malaysia_Berhad_Dragged_By_Higher_Costs_amp_Lower_Forex_Gains) | 0 |
| 2025-11-28 | GENTING | PublicInvest | [Genting Berhad - Results Below Our Expectations](https://klse.i3investor.com/web/blog/detail/PublicInvest/2025-11-28-story-h500554464-Genting_Berhad_Results_Below_Our_Expectations) | 0 |
| 2025-11-28 | GENTING | sectoranalyst | [Genting Berhad - Recovery in Progress](https://klse.i3investor.com/web/blog/detail/taresearch/2025-11-28-story-h500554520-Genting_Berhad_Recovery_in_Progress) | 0 |
| 2025-11-28 | GENM | sectoranalyst | [Genting Malaysia Berhad - No Signs of VIP Volume Slowing Down](https://klse.i3investor.com/web/blog/detail/taresearch/2025-11-28-story-h500554521-Genting_Malaysia_Berhad_No_Signs_of_VIP_Volume_Slowing_Down) | 0 |
| 2025-11-28 | GENM | PhillipCapital | [Genting Malaysia (GENM MK) - Above expectations](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2025-11-28-story-h500554647-Genting_Malaysia_GENM_MK_Above_expectations) | 0 |
| 2025-11-28 | GENTING | PhillipCapital | [Genting Berhad (GENT MK) - Above expectation](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2025-11-28-story-h500554648-Genting_Berhad_GENT_MK_Above_expectation) | 0 |
| 2025-11-28 | GENM | edgeinvest | [Genting Malaysia’s 3Q Net Profit Slumps 79% on Lower Forex Gains](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-11-28-story-h500555548-Genting_Malaysia_8217_s_3Q_Net_Profit_Slumps_79_on_Lower_Forex_Gains) | 0 |
| 2025-11-28 | GENTING | edgeinvest | [Genting Posts Steep Drop in 3Q Net Profit, Hit by Forex and Interest-income Headwinds](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-11-28-story-h500555552-Genting_Posts_Steep_Drop_in_3Q_Net_Profit_Hit_by_Forex_and_Interest_inco) | 0 |
| 2025-12-02 | GENTING | edgeinvest | [Genting Malaysia to Remain Listed After Genting Falls Short of 75% Ownership Threshold](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-12-02-story-h500558244-Genting_Malaysia_to_Remain_Listed_After_Genting_Falls_Short_of_75_Owners) | 0 |
| 2025-12-02 | GENM | StockTipRatings | [GENM New York Casino License Is One Step Away, One of the Best Consumer Analysts Sees RM1.9b Pr](https://klse.i3investor.com/web/blog/detail/strblog/2025-12-02-story-h500558247-GENM_New_York_Casino_License_Is_One_Step_Away_One_of_the_Best_Consumer_A) | 0 |
| 2025-12-03 | GENM | PhillipCapital | [Genting Malaysia (GENM MK) - Shortlisted for downstate casino license](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2025-12-03-story-h500558369-Genting_Malaysia_GENM_MK_Shortlisted_for_downstate_casino_license) | 0 |
| 2025-12-03 | GENM | sectoranalyst | [Genting Malaysia Berhad - Winning of Casino License in Downstate New York](https://klse.i3investor.com/web/blog/detail/taresearch/2025-12-03-story-h500558432-Genting_Malaysia_Berhad_Winning_of_Casino_License_in_Downstate_New_York) | 0 |
| 2025-12-03 | GENTING | edgeinvest | [Genting Malaysia Wins New York Casino Licence; Shares Slip](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-12-03-story-h500558465-Genting_Malaysia_Wins_New_York_Casino_Licence_Shares_Slip) | 0 |
| 2025-12-03 | GENM | BLee | [GenM: What is Known and Unknown?](https://klse.i3investor.com/web/blog/detail/BLeeGenting/2025-12-03-story-h500559234-GenM_What_is_Known_and_Unknown) | 0 |
| 2025-12-04 | GENTING | edgeinvest | [Genting Malaysia’s Shares Continue to Fall as Ratings Worries Overshadow New York Casino Progre](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-12-04-story-h500580374-Genting_Malaysia_8217_s_Shares_Continue_to_Fall_as_Ratings_Worries_Overs) | 0 |
| 2025-12-04 | GENTING | edgeinvest | [CreditSights: High Debt, Weak Cash Flow Put Genting, Genting Malaysia at Downgrade Risk](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-12-04-story-h500580375-CreditSights_High_Debt_Weak_Cash_Flow_Put_Genting_Genting_Malaysia_at_Do) | 0 |
| 2025-12-07 | GENM | BLee | [GenM: What will happen when GenT ‘Burst’ through 75% of GenM shareholdings?](https://klse.i3investor.com/web/blog/detail/BLeeGenting/2025-12-07-story-h500581403-GenM_What_will_happen_when_GenT_Burst_through_75_of_GenM_shareholdings) | 10 |
| 2025-12-09 | GENTING | edgeinvest | [Moody’s Downgrades Genting, Genting Singapore and Genting Overseas on Increased Debt, Slower Ea](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-12-09-story-h500582394-Moody_8217_s_Downgrades_Genting_Genting_Singapore_and_Genting_Overseas_o) | 0 |
| 2025-12-10 | GENM | StockTipRatings | [One of Malaysia Top Analyst Successfully Predicted GENTING Failed to Privatize GENM — Now He Pr](https://klse.i3investor.com/web/blog/detail/strblog/2025-12-10-story-h500583416-One_of_Malaysia_Top_Analyst_Successfully_Predicted_GENTING_Failed_to_Pri) | 0 |
| 2025-12-17 | GENM | edgeinvest | [New York Votes to Formally Approve Casino Licences for Genting, Two Other Winners](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-12-17-story-h500587231-New_York_Votes_to_Formally_Approve_Casino_Licences_for_Genting_Two_Other) | 0 |
| 2025-12-31 | GENTING | edgeinvest | [Genting Issues RM3 Bil Notes Under New RM5 Bil Debt Programme](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2025-12-31-story-h500614133-Genting_Issues_RM3_Bil_Notes_Under_New_RM5_Bil_Debt_Programme) | 0 |
| 2026-02-27 | GENTING | PublicInvest | [Genting Berhad - Lower Contribution From Malaysia & Singapore](https://klse.i3investor.com/web/blog/detail/PublicInvest/2026-02-27-story-h501355904-Genting_Berhad_Lower_Contribution_From_Malaysia_amp_Singapore) | 0 |
| 2026-02-27 | GENM | PublicInvest | [Genting Malaysia Berhad - Lifted By Forex Gains](https://klse.i3investor.com/web/blog/detail/PublicInvest/2026-02-27-story-h501355909-Genting_Malaysia_Berhad_Lifted_By_Forex_Gains) | 0 |
| 2026-02-27 | GENM | PhillipCapital | [Genting Malaysia (GENM MK) - Dragged by high costs, largely within expectations](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2026-02-27-story-h501355970-Genting_Malaysia_GENM_MK_Dragged_by_high_costs_largely_within_expectatio) | 0 |
| 2026-02-27 | GENM | PhillipCapital | [Genting Berhad (GENT MK) - Muted Genting Singapore and O&G contributions](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2026-02-27-story-h501355972-Genting_Berhad_GENT_MK_Muted_Genting_Singapore_and_O_amp_G_contributions) | 0 |
| 2026-02-27 | GENTING | edgeinvest | [Genting Falls Into the Red on Impairment Hit; GenM Swings to Profit on Forex Gains](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2026-02-27-story-h501356091-Genting_Falls_Into_the_Red_on_Impairment_Hit_GenM_Swings_to_Profit_on_Fo) | 0 |
| 2026-02-27 | GENM | sectoranalyst | [Genting Malaysia Berhad - Surprisingly Low VIPs in 4Q25](https://klse.i3investor.com/web/blog/detail/taresearch/2026-02-27-story-h501356988-Genting_Malaysia_Berhad_Surprisingly_Low_VIPs_in_4Q25) | 0 |
| 2026-02-27 | GENTING | sectoranalyst | [Genting Berhad - Dwindling VIP Volume in Malaysia and Singapore](https://klse.i3investor.com/web/blog/detail/taresearch/2026-02-27-story-h501356989-Genting_Berhad_Dwindling_VIP_Volume_in_Malaysia_and_Singapore) | 0 |
| 2026-03-03 | GENM | edgeinvest | [GenM President Lee Choong Yan Now Senior Adviser, to be Redesignated as Non-executive Director ](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2026-03-03-story-h501359843-GenM_President_Lee_Choong_Yan_Now_Senior_Adviser_to_be_Redesignated_as_N) | 0 |
| 2026-04-27 | GENM | MercurySec | [Genting Malaysia Berhad (4715) - Breakout of 5-Month Downtrend Line Signals Trend Reversal](https://klse.i3investor.com/web/blog/detail/mercurysec/2026-04-27-story-h501453186-Genting_Malaysia_Berhad_4715_Breakout_of_5_Month_Downtrend_Line_Signals_) | 0 |
| 2026-05-22 | GENM | HLInvest | [Genting Malaysia (RM1.98) - Shortfall Start](https://klse.i3investor.com/web/blog/detail/hleresearch/2026-05-22-story-h501533750-Genting_Malaysia_RM1_98_Shortfall_Start) | 0 |
| 2026-05-22 | GENM | PublicInvest | [Genting Malaysia Berhad - Higher Operating & Finance Costs](https://klse.i3investor.com/web/blog/detail/PublicInvest/2026-05-22-story-h501533780-Genting_Malaysia_Berhad_Higher_Operating_amp_Finance_Costs) | 0 |
| 2026-05-22 | GENTING | PublicInvest | [Genting Berhad - Within Expectations](https://klse.i3investor.com/web/blog/detail/PublicInvest/2026-05-22-story-h501533782-Genting_Berhad_Within_Expectations) | 0 |
| 2026-05-22 | GENM | sectoranalyst | [Genting Malaysia Berhad - Looking Forward to RWNYC Full-Scale Casino](https://klse.i3investor.com/web/blog/detail/taresearch/2026-05-22-story-h501533842-Genting_Malaysia_Berhad_Looking_Forward_to_RWNYC_Full_Scale_Casino) | 0 |
| 2026-05-22 | GENTING | sectoranalyst | [Genting Berhad - Support from Las Vegas](https://klse.i3investor.com/web/blog/detail/taresearch/2026-05-22-story-h501533847-Genting_Berhad_Support_from_Las_Vegas) | 0 |
| 2026-05-22 | GENTING | edgeinvest | [Genting 1Q Profit Surges Over 20-fold on JV Gains, Lower Impairments; Genting Malaysia Slips In](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2026-05-22-story-h501534622-Genting_1Q_Profit_Surges_Over_20_fold_on_JV_Gains_Lower_Impairments_Gent) | 0 |
| 2026-05-22 | GENTING | PhillipCapital | [Genting Berhad (GENT MK) - Results below expectations](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2026-05-22-story-h501535706-Genting_Berhad_GENT_MK_Results_below_expectations) | 0 |
| 2026-05-22 | GENM | PhillipCapital | [Genting Malaysia (GENM MK) - 1Q26: Luck runs dry](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2026-05-22-story-h501534716-Genting_Malaysia_GENM_MK_1Q26_Luck_runs_dry) | 0 |
| 2026-07-31 | GENM | edgeinvest | [Genting Malaysia May Report Loss in 2Q, Analyst Warns](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2026-07-31-story-h502287234-Genting_Malaysia_May_Report_Loss_in_2Q_Analyst_Warns) | 0 |
| 2026-08-21 | GENTING | sectoranalyst | [Genting Berhad - GENS Struggled in 1H26](https://klse.i3investor.com/web/blog/detail/taresearch/2026-08-21-story-h502342044-Genting_Berhad_GENS_Struggled_in_1H26) | 0 |
| 2026-08-21 | GENM | PhillipCapital | [Genting Malaysia (GENM MK) - Result below expectations](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2026-08-21-story-h502342078-Genting_Malaysia_GENM_MK_Result_below_expectations) | 0 |
| 2026-08-21 | GENTING | PhillipCapital | [Genting Berhad (GENT MK) - Results missed expectations](https://klse.i3investor.com/web/blog/detail/PhillipCapitalResearchReports/2026-08-21-story-h502342080-Genting_Berhad_GENT_MK_Results_missed_expectations) | 0 |
| 2026-08-21 | GENM | sectoranalyst | [Genting Malaysia Berhad - Strong Headstart from Casino Operations in New York City](https://klse.i3investor.com/web/blog/detail/taresearch/2026-08-21-story-h502342111-Genting_Malaysia_Berhad_Strong_Headstart_from_Casino_Operations_in_New_Y) | 0 |
| 2026-08-21 | GENM | PublicInvest | [Genting Malaysia Berhad - Dragged By Higher Operating Cost](https://klse.i3investor.com/web/blog/detail/PublicInvest/2026-08-21-story-h502342113-Genting_Malaysia_Berhad_Dragged_By_Higher_Operating_Cost) | 0 |
| 2026-08-21 | GENTING | PublicInvest | [Genting Berhad - Hit By Higher Finance Cost And Forex Losses](https://klse.i3investor.com/web/blog/detail/PublicInvest/2026-08-21-story-h502342135-Genting_Berhad_Hit_By_Higher_Finance_Cost_And_Forex_Losses) | 0 |
| 2026-08-21 | GENM | HLInvest | [GENM (HOLD) - Uncertainties Remain](https://klse.i3investor.com/web/blog/detail/hleresearch/2026-08-21-story-h502342942-GENM_HOLD_Uncertainties_Remain) | 0 |
| 2026-08-21 | GENTING | edgeinvest | [Genting Swings Into 2Q Loss as Higher Finance Costs, Absence of One-off Gain Weigh](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2026-08-21-story-h502342948-Genting_Swings_Into_2Q_Loss_as_Higher_Finance_Costs_Absence_of_One_off_G) | 0 |
| 2026-08-21 | GENTING | HLInvest | [3182 GENTING (HOLD) - Missed Expectations](https://klse.i3investor.com/web/blog/detail/hleresearch/2026-08-21-story-h502342980-3182_GENTING_HOLD_Missed_Expectations) | 0 |
| 2026-09-23 | GENM | PublicInvest | [Technical Buy - GENM (4715)](https://klse.i3investor.com/web/blog/detail/PublicInvest/2026-09-23-story-h502427544-Technical_Buy_GENM_4715) | 0 |
| 2026-10-13 | GENTING | edgeinvest | [Genting Falls 23% to 2007 Lows After Over RM1 Bil Cash Call](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2026-10-13-story-h502463133-Genting_Falls_23_to_2007_Lows_After_Over_RM1_Bil_Cash_Call) | 0 |
| 2026-10-13 | GENTING | StockTipRatings | [Affin Cuts GENTING & GENM to Sell as Rights Issue Offers Little Debt Relief and New York Costs ](https://klse.i3investor.com/web/blog/detail/strblog/2026-10-13-story-h502463910-Affin_Cuts_GENTING_GENM_to_Sell_as_Rights_Issue_Offers_Little_Debt_Relie) | 0 |
| 2026-10-14 | GENTING | edgeinvest | [Genting May Need to Sell Non-core Assets to Avert a Credit-rating Downgrade — CreditSights](https://klse.i3investor.com/web/blog/detail/ceomorningbrief/2026-10-14-story-h502464129-Genting_May_Need_to_Sell_Non_core_Assets_to_Avert_a_Credit_rating_Downgr) | 0 |
| 2026-10-19 | GENM | StockTipRatings | [GENM Plunges 46% Below Offer Price, Vindicating This Analyst’s Exit Call Last Year—Which Stocks](https://klse.i3investor.com/web/blog/detail/strblog/2026-10-19-story-h502487216-GENM_Plunges_46_Below_Offer_Price_Vindicating_This_Analyst_s_Exit_Call_L) | 0 |

## 6. Timestamps

- Article publish times are absolute: `Publish date: Sun, 07 Dec 2025, 08:31 AM` (Asia/Kuala_Lumpur, UTC+8), converted to epoch seconds UTC. Every article has `raw.time_confidence = "exact"`; none needed the URL-date fallback.
- Comment times come from three absolute sources, in priority order: the article page (`YYYY-MM-DD HH:MM`), the `comservlet.jsp` fragment (`DD/MM/YYYY h:mm AM/PM`), and the forum thread page (`YYYY-MM-DD HH:MM`). All are MYT and converted to UTC.
- No relative comment labels were used. Comments with no parseable absolute timestamp were dropped rather than guessed (none were needed for the comments written).

## 7. Comments: completeness and shape

- `comservlet.jsp` returns the latest comments for the article's discussion page with exact timestamps; the article page itself renders the same newest comments. Both are merged by comment id. If the article reports more comments than `comservlet` returned, forum-thread pages (`/web/forum/forum-thread/<page_id>?p=N`) are walked until no new ids appear.
- Blog comments are **flat**: no parent/child links are rendered, so every reply has `parent_native_id = null` and `depth = 0`.
- No per-comment like/score counter is displayed on blog pages, so `score` is `null`.
- Comments collected: **61**. Articles with comments disabled or no comments: **136**.
- Reconciliation: the article counters (`Showing X of Y comments`) sum to **61**, exactly the 61 comments written. No visible comment was skipped.

## 8. Exclusions and known gaps

The review stage dropped candidates that were not substantively about Genting Berhad / Genting Malaysia. Counts by reason:

| Reason | Candidates |
| --- | ---: |
| video_link_stub | 44 |
| empty_or_stub | 22 |
| out_of_scope_genting_plantations | 13 |
| genting_highlands_not_company | 2 |
| different_stock | 1 |
| out_of_scope_genting_singapore | 1 |
| multi_stock_roundup | 1 |

- **Genting Plantations (GENP, 2291)** articles were excluded: a different listed company, even though it shares the Genting name.
- **Genting Singapore-only (GENS)** articles were excluded to keep the corpus on the two Malaysian counters; articles that discuss Genting Berhad's group results (including GENS contributions) were kept.
- **Video-link posts** from DoubleSwords / 双剑论股 whose body is only a YouTube link and a title were excluded as stubs, not full article text. Their genuine text posts (if any) were kept.
- **Genting Highlands road-charge / property** stories that are not about the listed companies were excluded.
- The stock News & Blogs page only exposes one year. For 2024-11-02 → 2025-11-03 the archive is reconstructed from Wayback snapshots plus author-page backfill. The research-house and news coverage for that year is complete for the 20 authors crawled, but one-off user blogs that never appeared in a Wayback snapshot and are not in the seed set may still be missing; the thinnest months are 2025-04 (3 articles), 2025-06 (3) and 2025-09 (4).
- One manually seeded article (`2025-02-28-story-h498648831`, “Genting Posts First Quarterly Loss…”) now returns an empty/deleted page and was skipped; the same 4Q24 result is covered by the TA/PublicInvest/Phillip reports and the CEO Morning Brief CEO-change story.
- No comments were lost to pagination failures; any `comservlet`/forum error is listed below.

## 9. Requests, pages, failures

- Articles fetched: 239; included 155; excluded 84; fetch failures 0.
- HTTP requests during article/comment fetch: 368 (209 on the first full pass, 9 for the extra author-pass articles, 150 for a corrected `comservlet.jsp` re-read; cached article pages were not re-requested). Minimum interval 1.35 s, retries with backoff.
- Pages: 2 stock News & Blogs pages, 6 Wayback stock/headline snapshots (plus 16 stock overview snapshots), ~506 author archive pages (50 posts/page), 239 article pages and 239 `comservlet.jsp` fragments.
- HTTP requests during discovery: 541 (stock pages, Wayback snapshots downloaded separately, and author archive pages), plus ~55 for the extra author pass.
- Cloudflare: plain `curl_cffi` requests were challenged; the collector used a real Chrome/undetected-chromedriver session to obtain `cf_clearance` cookies, then `curl_cffi` with the matching User-Agent. No SQLite writes were made.
- Fetch failures: none.

## 10. Validation

Command run:

```bash
python3 -m genting.validate data/raw/i3blogs.jsonl
```

Result:

```
records=216 {'post': 155, 'reply': 61} tickers={'GENTING': 69, 'GENM': 86} | 2024-11-06 → 2026-10-19
empty_or_deleted=0 duplicate_body_texts=1
OK: 0 errors
```

The single duplicate body is a genuine double-post of the same one-line comment by user `Income` on 2025-03-13 (ids 9587778 and 9587779), not a collector duplication.
