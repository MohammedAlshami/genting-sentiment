# YouTube collection report — Malaysian Genting

- **Collected:** 2 Nov 2026
- **Window:** 2 Nov 2025 → 2 Nov 2026 (inclusive; cutoff 3 Nov 2026 00:00 UTC)
- **Output:** `data/raw/youtube.jsonl`
- **Records:** 1199 — 55 posts, 1144 comments
- **Posts by ticker:** GENM × 21, GENTING × 30, UNKNOWN × 4
- **Comments by post ticker:** GENM × 909, GENTING × 212, UNKNOWN × 23
- **Comment threads:** 749 top-level comments, 395 replies, 794 distinct authors
- **Date range in file:** 2025-07-08 → 2026-11-01
- **Comment date range:** 2025-11-02 → 2026-11-01
- **Validation:** `python3 -m genting.validate data/raw/youtube.jsonl` → **OK, 0 errors, 1 warning** (pre-window upload with in-window comments; explained below)

## Method

Discovery used `yt-dlp --flat-playlist --dump-json` against these YouTube searches (30 results each for the first eight, 25 for the last four):

- `ytsearch30:genting malaysia stock`
- `ytsearch30:genting berhad stock analysis`
- `ytsearch30:GENM 4715`
- `ytsearch30:genting rights issue`
- `ytsearch30:genting share price`
- `ytsearch30:saham genting`
- `ytsearch30:云顶 股票`
- `ytsearch30:云顶大马`
- `ytsearch25:Genting 3182`
- `ytsearch25:genting crash`
- `ytsearch25:GENM share price`
- `ytsearch25:云顶 附加股`

Requests: 12 search calls (25–30 results each) plus 78 per-video metadata/comment extractions, run sequentially with a 2-second gap. No HTTP 429 or sign-in challenge was hit.

The 198 unique results were filtered to videos whose subject is Genting Berhad (GENTING, 3182) or Genting Malaysia (GENM, 4715) as listed companies/securities. Tourism/theme-park vlogs, casino-consumer content, Genting Singapore and generic market roundups were dropped. Each shortlisted video was then fetched one at a time with `yt-dlp --write-comments --skip-download` (78 videos, 2-second gap); yt-dlp paginates the comment continuations and retrieves every comment, not only the top ones. Comments are filtered to the window by their own `timestamp`.

`created_utc` for a post is the exact upload timestamp where YouTube exposes it, otherwise the upload date at 00:00 UTC. `score` is `view_count` for posts and `like_count` for comments. `num_comments` is the `comment_count` reported in the video metadata (null where YouTube did not expose it). Records are deduplicated by `(source, native_id)`.

### Comment timestamp precision

YouTube's comment API exposes only a **relative** age (`2 weeks ago`, `1 year ago`), not an absolute publication time. yt-dlp resolves each label to an estimated date at 00:00 UTC; the original label is preserved in every reply's `raw.time_text`. These timestamps are therefore day-level estimates, not exact times, and labels such as `1 year ago` are coarse (YouTube uses them for a range of months). This is the most defensible timestamp publicly available; no precision beyond the date was invented. The window filter uses these estimates, so comments dated exactly 2 Nov 2025 are boundary cases (the label `1 year ago` on collection day resolves there).

Because the labels are coarse, replies cluster on the same estimated day: the largest cluster is **621 replies at 2026-02-02**, all carrying the same relative label. Sub-month timing within a label bucket cannot be recovered from YouTube's public comment API; use `raw.time_text` for the original label.

## Videos collected

| Video | Channel | Ticker | Uploaded | Views | Comments (metadata) | Fetched | In window | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| [eMldGrhWukM](https://www.youtube.com/watch?v=eMldGrhWukM) 云顶要跟股东拿 12.5 亿，为什么？｜你的 1,000 股会怎样? | 棋有此理 | GENTING | 2026-10-24 | 97 | 0 | 0 | 0 | ok |
| [zb4XUj4ptf0](https://www.youtube.com/watch?v=zb4XUj4ptf0) Why Genting Crashed 50% This Year | FIRL | GENTING | 2026-10-22 | 2542 | 4 | 4 | 4 | ok |
| [5MkxlZtt2_E](https://www.youtube.com/watch?v=5MkxlZtt2_E) Genting Plunged 21% In 1 Day. What Happened? | FIRL | GENTING | 2026-10-20 | 19729 | 17 | 17 | 17 | ok |
| [KUkInDEtthM](https://www.youtube.com/watch?v=KUkInDEtthM) 云顶股价跌回1998年水平，股东为什么还要再掏钱？ | AF's Notes | GENTING | 2026-10-17 | 5400 | 18 | 18 | 18 | ok |
| [ASM3jGhjjv4](https://www.youtube.com/watch?v=ASM3jGhjjv4) GENM 高峰跌80%，来到了RM1.28，接下来怎么看？#马股 #GenM #genting #云顶 | TI 懂一点 | GENM | 2026-10-15 | 4720 | 3 | 3 | 3 | ok |
| [7Mx1GOyFU2w](https://www.youtube.com/watch?v=7Mx1GOyFU2w) Analysts vs. Rating Agencies: The Truth Behind Genting’s Rights Issue @YZFinanceMY | Y-Z Finance MY | GENTING | 2026-10-13 | 202 | 0 | 0 | 0 | ok |
| [b96x4D-t_-4](https://www.youtube.com/watch?v=b96x4D-t_-4) 13 10 2026 第825期：GENM 烂泥扶不上墙！ | 我是雷公 | GENM | 2026-10-13 | 4127 | 6 | 6 | 6 | ok |
| [bWyCSIb1kek](https://www.youtube.com/watch?v=bWyCSIb1kek) 【暴跌应变策略】GENTING 昨天暴跌22.9%！RM1.45近二十年低位，附加股风暴后该如何应变？@mytraderview | MYtraderview 大马股市技术分析交易 + 生活日志 | GENTING | 2026-10-13 | 310 | 2 | 2 | 2 | ok |
| [a7v1yQuvRdU](https://www.youtube.com/watch?v=a7v1yQuvRdU) Genting’s $306M Cash Call: Why the Stock Crashed 17% in One Day | One Minute Finance | GENTING | 2026-10-13 | 141 | 1 | 1 | 1 | ok |
| [9sGjLgbY1kY](https://www.youtube.com/watch?v=9sGjLgbY1kY) Genting Berhad暴跌23%！现在可以上车吗？#Genting #GentingBerhad #马股 #马来西亚股票 #股票投资 #Genting暴跌 #股票大跌 #3182  #双阳倍量 | 双阳倍量 Double Volume Bullish Channel  | GENTING | 2026-10-12 | 107 | 0 | 0 | 0 | ok |
| [23YnMF041Dk](https://www.youtube.com/watch?v=23YnMF041Dk) 云顶拟发附加股筹12.5亿 恐稀释每股盈利股息约20%【2026.10.12 八度空间华语新闻】 | 八度空间华语新闻 | GENTING | 2026-10-12 | 11042 | 9 | 9 | 9 | ok |
| [4NMqS8088mw](https://www.youtube.com/watch?v=4NMqS8088mw) GENTING 今天大跌23%，来到了RM1.45?为什么会暴跌？接下来怎么看？#马股 #云顶 #genting #genm | TI 懂一点 | GENTING | 2026-10-12 | 13059 | 14 | 14 | 14 | ok |
| [TFuermAvqYA](https://www.youtube.com/watch?v=TFuermAvqYA) Limit down of Genting | InvestDummies | GENTING | 2026-10-12 | 57 | 0 | 0 | 0 | ok |
| [RgglDDKT-qE](https://www.youtube.com/watch?v=RgglDDKT-qE) Maybank cuts Genting to sell, Ethiopia's betting shutdown \| Gambling news 12 Oct 2026 | Learn Gambling | GENTING | 2026-10-12 | 43 | 0 | 0 | 0 | ok |
| [FBQwVVixcrk](https://www.youtube.com/watch?v=FBQwVVixcrk) Genting RM1.25B Rights Issue: Red Flag or Golden Opportunity? @YZFinanceMY | Y-Z Finance MY | GENTING | 2026-10-11 | 188 | 0 | 0 | 0 | ok |
| [C8M7S7lqzGQ](https://www.youtube.com/watch?v=C8M7S7lqzGQ) 【技术形态解读】GENTING 拟发附加股集资12.5亿还债！股价能否守住历史新低 ？接下来怎么看？@mytraderview | MYtraderview 大马股市技术分析交易 + 生活日志 | GENTING | 2026-10-11 | 498 | 2 | 2 | 2 | ok |
| [zlQhl78ZzKg](https://www.youtube.com/watch?v=zlQhl78ZzKg) GENTING 云顶 刷新的52周新低！现在怎么办? 中英字幕 ENG SUB | Double Swords Investing | GENTING | 2026-10-03 | 3850 | 7 | 7 | 7 | ok |
| [n0VA3V5HeT4](https://www.youtube.com/watch?v=n0VA3V5HeT4) The Genting Situation - current and its forecast into 27/28 payout | InvestDummies | GENTING | 2026-09-10 | 126 | 0 | 0 | 0 | ok |
| [VvGLSkUIesM](https://www.youtube.com/watch?v=VvGLSkUIesM) Genting跌回近25年低位，市场到底在怕什么？ | AF's Notes | UNKNOWN | 2026-08-29 | 6053 | 18 | 18 | 18 | ok |
| [8IUZC7XdCqs](https://www.youtube.com/watch?v=8IUZC7XdCqs) 聊一聊4支云顶股 | 大老板投资记录本 | UNKNOWN | 2026-08-22 | 4618 | 3 | 3 | 3 | ok |
| [auwV0rb5VzQ](https://www.youtube.com/watch?v=auwV0rb5VzQ) Genting Malaysia (4715) Q2 2026: RM3.85B Revenue 📈, 89% Profit Drop! (NY Casino, Privatization) | Nighteyes08 | GENM | 2026-08-22 | 981 | 1 | 1 | 1 | ok |
| [e-vof7U496w](https://www.youtube.com/watch?v=e-vof7U496w) GENTING 云顶 可以去捞便宜吗? 双剑筹码峰分析告诉你！中幸英字幕 ENG SUB | Double Swords Investing | GENTING | 2026-08-21 | 3450 | 2 | 2 | 2 | ok |
| [IRYyHe16OZY](https://www.youtube.com/watch?v=IRYyHe16OZY) GENM Paradox: Market is ignoring RWNYC expansion 🎰 @YZFinanceMY | Y-Z Finance MY | GENM | 2026-08-20 | 181 | 0 | 0 | 0 | ok |
| [CjVr62Y9w28](https://www.youtube.com/watch?v=CjVr62Y9w28) GENM 云顶大马 GENTING MALAYSIA 预测未来的走势！季度财报公布前, 要如何去操作？中英字幕 ENG SUB | Double Swords Investing | GENM | 2026-08-14 | 3292 | 0 | 0 | 0 | ok |
| [Uokye1GSu84](https://www.youtube.com/watch?v=Uokye1GSu84) 云顶股价20年来历史新低，Genting 彻底玩完了？#genting  #genm #gens | 阿布的鸟公司 | GENTING | 2026-08-07 | 58848 | 64 | 64 | 64 | ok |
| [C60JnI65NLQ](https://www.youtube.com/watch?v=C60JnI65NLQ) GENM暴跌到RM1.7,股价便宜了？投资接下来该怎么应对？庄家价格在哪里？#马股 #genm #genting #云顶股票 | TI 懂一点 | GENM | 2026-08-05 | 2347 | 3 | 3 | 3 | ok |
| [eK3bsSe5pbc](https://www.youtube.com/watch?v=eK3bsSe5pbc) GENM GENTING 云顶大马 现在要如何去抓反弹？目标价？识别 3个危险的信号！逃生门 筹码峰技术分析 中英字幕 ENG SUB. | Double Swords Investing | UNKNOWN | 2026-07-28 | 1736 | 0 | 0 | 0 | ok |
| [WV-1meK6d60](https://www.youtube.com/watch?v=WV-1meK6d60) GENTING 云顶 - 下跌中的刀！如何去操作？中英字幕 ENG SUB. | Double Swords Investing | GENTING | 2026-07-24 | 1576 | 1 | 1 | 1 | ok |
| [wuVPgdar6xw](https://www.youtube.com/watch?v=wuVPgdar6xw) GENTING｜未来3年的看点是什么？ | 大老板投资记录本 | GENTING | 2026-07-17 | 13480 | 26 | 26 | 26 | ok |
| [W0kCTXMa-U0](https://www.youtube.com/watch?v=W0kCTXMa-U0) 马股 GENTING 可以看吗？股价趋势分析，庄家价位在哪里？#马股 #科技股  #genting #genm #云顶 #马来西亚股票 | TI 懂一点 | GENTING | 2026-06-21 | 1659 | 0 | 0 | 0 | ok |
| [WJ3wY3kBRyY](https://www.youtube.com/watch?v=WJ3wY3kBRyY) Why Is Everyone Suddenly Worried About Genting Berhad? | FIRL | GENTING | 2026-05-21 | 10356 | 14 | 14 | 14 | ok |
| [9bGkeKa6GY8](https://www.youtube.com/watch?v=9bGkeKa6GY8) 🔥 24 Apr 2026｜GENM (4715) & GENTING (3182) 起涨买点讯号！目前关键价位与走势解析｜射箭指标 | 股市先锋队 | UNKNOWN | 2026-04-24 | 496 | 2 | 2 | 2 | ok |
| [B7sBgzhz5RQ](https://www.youtube.com/watch?v=B7sBgzhz5RQ) GENTING云顶私有化失败后续,接下来怎么看？庄家价位在哪里？#马股 #genting  #云顶 #庄家 #私有化 | TI 懂一点 | GENTING | 2026-04-10 | 1520 | 5 | 5 | 5 | ok |
| [DCofWXNk_5k](https://www.youtube.com/watch?v=DCofWXNk_5k) 庄家布局GENTING? 最近跌破3块，接下来看这些关键价位 #genting #云顶 #马股 #genm #3182 | TI 懂一点 | GENTING | 2026-03-15 | 2369 | 2 | 2 | 2 | ok |
| [qE71UOfGwFM](https://www.youtube.com/watch?v=qE71UOfGwFM) GENTING 3182 股价下跌真正原因, 跌破庄家价位是机会吗？#3182 #genm #genting #云顶 #马股 #庄家 #私有化 | TI 懂一点 | GENTING | 2026-02-27 | 1864 | 6 | 6 | 6 | ok |
| [MfMTFU2z0t0](https://www.youtube.com/watch?v=MfMTFU2z0t0) Genting Berhad (GENT 3182) Q4 2025 Results: Net Loss – Deep Value or Empire Under Pressure? | Nighteyes08 | GENTING | 2026-02-27 | 174 | 0 | 0 | 0 | ok |
| [GS3C-kVfaAo](https://www.youtube.com/watch?v=GS3C-kVfaAo) Genting Malaysia (GENM 4715) Q4 2025 Results: New York Casino Win, RM2.6B Lawsuit & Rising Debt Risk | Nighteyes08 | GENM | 2026-02-27 | 101 | 0 | 0 | 0 | ok |
| [uiGZ7zLiw0g](https://www.youtube.com/watch?v=uiGZ7zLiw0g) GENTING 云顶 ！什么时候可以去捞？强支撑在什么位置？套牢盘在哪里？关键技巧揭露! 中英字幕ENG SUB | Double Swords Investing | GENTING | 2026-02-05 | 2241 | 2 | 2 | 2 | ok |
| [7qlVD50_g8o](https://www.youtube.com/watch?v=7qlVD50_g8o) GENTING 3182 私有化GENM失败后 ,发生什么事？目前股价怎么看？#马股 #genting #genm #云顶股票 #庄家 #资金 | TI 懂一点 | GENTING | 2026-01-20 | 2726 | 2 | 2 | 2 | ok |
| [BgyQDJkYtDo](https://www.youtube.com/watch?v=BgyQDJkYtDo) Saham Genting Malaysia Jatuh, Rahasia Besar Indonesia Terbongkar! | PERSENAN | GENM | 2026-01-12 | 21768 | 142 | 142 | 142 | ok |
| [5xbcnlCy-7k](https://www.youtube.com/watch?v=5xbcnlCy-7k) Is this the End for Genting Malaysia? | Ziet Invests | GENM | 2026-01-05 | 596152 | 632 | 632 | 632 | ok |
| [YV7wPHl55UU](https://www.youtube.com/watch?v=YV7wPHl55UU) GENTING 3182股价来到了关键价位吗？接下来筑底反弹？投资者可以看？#马股 #genting #3182 #云顶 | TI 懂一点 | GENTING | 2025-12-28 | 2030 | 8 | 8 | 8 | ok |
| [ospEUOdSv3E](https://www.youtube.com/watch?v=ospEUOdSv3E) GENM 4715 现在怎么看？私有化失败后为什么股价下跌？#马股 #genm #4715 #genting #云顶 | TI 懂一点 | GENM | 2025-12-18 | 1751 | 1 | 1 | 1 | ok |
| [J_2z7rBsNLg](https://www.youtube.com/watch?v=J_2z7rBsNLg) GENM 4715 私有化失败,但是股价下跌了,投资者要小心？#马股 #genm #4715 #genting #云顶 | TI 懂一点 | GENM | 2025-12-02 | 4461 | 3 | 3 | 3 | ok |
| [8APxvQ015fA](https://www.youtube.com/watch?v=8APxvQ015fA) Genting Malaysia (GENM) Q3 2025: Revenue +22%, Profit –79% (Forex Shock & RM2.35 Takeover Battle) | Nighteyes08 | GENM | 2025-11-28 | 100 | 5 | 5 | 5 | ok |
| [dh6kHyS_JL8](https://www.youtube.com/watch?v=dh6kHyS_JL8) EDGE WEEKLY: Should Genting Malaysia shareholders stay or fold? | The Edge TV | GENM | 2025-11-26 | 5125 | — | 0 | 0 | comments_disabled: comment section unavailable (YouTube returned no comments or count; likely disabled) |
| [nQdJp0DTKus](https://www.youtube.com/watch?v=nQdJp0DTKus) GENM 4715 股价突破 RM2.35，私有化失败？#马股分析 #genm #genting #云顶 #云顶大马 #4715 #私有化 | TI 懂一点 | GENM | 2025-11-18 | 2211 | 3 | 3 | 3 | ok |
| [5htUkKiu9X8](https://www.youtube.com/watch?v=5htUkKiu9X8) GENM 4715,云顶无条件全购云顶大马,什么意思？#股票投資 #马股 #genm #genting #云顶 #私有化 #全面收购 | TI 懂一点 | GENM | 2025-11-04 | 3637 | 3 | 3 | 3 | ok |
| [8RPViwkuzFQ](https://www.youtube.com/watch?v=8RPViwkuzFQ) 云顶大马GENM私有化，该卖？该接受？还能做什么？｜八卦大小文 | 八卦大小文的闲聊股市 | GENM | 2025-11-02 | 11299 | 52 | 52 | 52 | ok |
| [SAXnfqtbvOU](https://www.youtube.com/watch?v=SAXnfqtbvOU) GENTING 3182私有化GENM后的价格技术分析 #股票投資 #马股 #云顶 #genm #genting | TI 懂一点 | GENTING | 2025-10-22 | 1969 | 6 | 6 | 6 | ok |
| [6Tp_HHbypSQ](https://www.youtube.com/watch?v=6Tp_HHbypSQ) 云顶大马的最后一页… | Neo, Biz Editor  | GENM | 2025-10-22 | 2300 | 3 | 3 | 3 | ok |
| [6wqA59uSSlY](https://www.youtube.com/watch?v=6wqA59uSSlY) 林国泰的豪赌：67亿私有化云顶大马，背后的棋局与信号 | 大马财富故事Wealth Stories | GENM | 2025-10-20 | 5863 | 16 | 16 | 16 | ok |
| [ltChQ03z2Gg](https://www.youtube.com/watch?v=ltChQ03z2Gg) 林国泰出手私有化云顶大马！2.35令吉收购价合理吗？｜2026财政预算案赢家输家诞生，99超市股价和创办人身家暴涨！｜马币势如破竹升破4在望，亚航或成大赢家？｜财经祥谈（17/10/25） | Neo, Biz Editor  | GENM | 2025-10-17 | 2408 | 2 | 2 | 2 | ok |
| [kX2YXGLlygc](https://www.youtube.com/watch?v=kX2YXGLlygc) 云顶大动作！GENM 私有化计划全解析 ｜第一天乡下茶话会 | 第一天投资理财研究所 | GENM | 2025-10-16 | 15740 | 33 | 33 | 33 | ok |
| [gESZSALUDJE](https://www.youtube.com/watch?v=gESZSALUDJE) GENTING MALAYSIA BERHAD@SUPER STOCK | I AM LEGEND | GENM | 2025-07-08 | 147 | 1 | 1 | 1 | ok |

## Videos checked but not written

| Video | Uploaded | Fetched comments | Reason |
| --- | --- | ---: | --- |
| [EwKoGKRLIEY](https://www.youtube.com/watch?v=EwKoGKRLIEY) Genting Malaysia (GENM MK): Genting (GENT MK)'s Curious Offer | 2025-10-15 | 0 | no in-window comments |
| [Wvv6M6Sgs7M](https://www.youtube.com/watch?v=Wvv6M6Sgs7M) 云顶拟私有化云顶大马 献购每股2.35令吉【2025.10.13 八度空间华语新闻】 | 2025-10-13 | 0 | no in-window comments |
| [hi6z7UTSRLs](https://www.youtube.com/watch?v=hi6z7UTSRLs) Genting (3182) Stock Drops Big! Is It Time to Buy or Will It Fall Further? | 2025-03-03 | 0 | no in-window comments |
| [iumwY-73TsY](https://www.youtube.com/watch?v=iumwY-73TsY) Investment Analysis Series - GENM (KLSE: 4715) | 2023-06-06 | 0 | no in-window comments |
| [n5h_ZEs5rMA](https://www.youtube.com/watch?v=n5h_ZEs5rMA) Investment Analysis Series - GENTING (KLSE: 3182) | 2023-06-05 | 0 | no in-window comments |
| [qEYT3hQhMT4](https://www.youtube.com/watch?v=qEYT3hQhMT4) StubWorld: Genting Berhad Is Cheap | 2023-04-18 | 0 | no in-window comments |
| [wBq_g0qPcm0](https://www.youtube.com/watch?v=wBq_g0qPcm0) WHICH GENTING COUNTER IS MOST WORTHY TO BE INVESTED? | 2022-07-30 | 0 | no in-window comments |
| [Z2Na-bKfFd0](https://www.youtube.com/watch?v=Z2Na-bKfFd0) GENTING MALAYSIA: ONE OF THE LEADING RESORTS OPERATOR IN MALAYSIA, IS IT WORTHY TO BE INVESTED? | 2022-07-04 | 1 | no in-window comments |
| [GEJo7av1WwQ](https://www.youtube.com/watch?v=GEJo7av1WwQ) GENTING BERHAD: ONE OF THE MOST DIVERSIFIED COMPANIES IN MALAYSIA, IS IT WORTHY TO BE INVESTED? | 2022-07-02 | 0 | no in-window comments |
| [TgSR2HTlZOM](https://www.youtube.com/watch?v=TgSR2HTlZOM) 云顶大马重回大家的视线?! 下一个超级复苏股?! 【乐学成长空间】 | 2022-05-07 | 20 | no in-window comments |
| [7Epg1Lx6b_s](https://www.youtube.com/watch?v=7Epg1Lx6b_s) 浅谈 #GENM 4715 \| 马股 | 2022-01-24 | 0 | no in-window comments |
| [iW6xlyKdhBg](https://www.youtube.com/watch?v=iW6xlyKdhBg) 大马股票 \| 云顶大马 \| GENM \| 从零开始了解云顶大马EP.02 | 2021-12-09 | 3 | no in-window comments |
| [zu8Gz6Mhk6s](https://www.youtube.com/watch?v=zu8Gz6Mhk6s) Re-Accumulation with Potential VCP Setup - GENTING & GENM | 2021-09-14 | 3 | no in-window comments |
| [hle2IKbEhR4](https://www.youtube.com/watch?v=hle2IKbEhR4) Technical Analysis in 3 minutes: Genting Malaysia (GENM 4715) 210723 | 2021-07-23 | 0 | no in-window comments |
| [fhyaYYAOh6A](https://www.youtube.com/watch?v=fhyaYYAOh6A) 云顶大马 Genting Malaysia \| 大马股票 \| 云顶大马现在很便宜？但是你敢买吗？\| 【乐学成长空间】 | 2020-09-11 | 180 | no in-window comments |
| [lgm1ydNcHhE](https://www.youtube.com/watch?v=lgm1ydNcHhE) 云顶纽约联号公司  发行20亿债券｜财经espresso | 2020-07-20 | 11 | no in-window comments |
| [QzCNZZx0WnU](https://www.youtube.com/watch?v=QzCNZZx0WnU) GENM (4715) | 2020-06-28 | 2 | no in-window comments |
| [CoQ4IAjg7ms](https://www.youtube.com/watch?v=CoQ4IAjg7ms) #stockGenm #stockKlci stock #malaysia stock GENM (4715) technical analysis | 2020-05-22 | 4 | no in-window comments |
| [tTtQ-DWDAn0](https://www.youtube.com/watch?v=tTtQ-DWDAn0) GENM 4715 加油！ | 2020-04-10 | 0 | no in-window comments |
| [x_J5v_vZxy0](https://www.youtube.com/watch?v=x_J5v_vZxy0) Genting Malaysia Bhd (GENM) Latest News by Greentrades | 2020-03-07 | 1 | no in-window comments |
| [617nmFnXMJk](https://www.youtube.com/watch?v=617nmFnXMJk) Genting Berhad: Opportunities and Threat Analysis | 2019-10-28 | 1 | no in-window comments |
| [BlxP_c69dso](https://www.youtube.com/watch?v=BlxP_c69dso)  | — | 0 | video unavailable (deleted/private) |
| [wVNY7bKPWa4](https://www.youtube.com/watch?v=wVNY7bKPWa4)  | — | 0 | video unavailable (deleted/private) |

## Largest comment threads

| Video | Ticker | Comments in window |
| --- | --- | ---: |
| [5xbcnlCy-7k](https://www.youtube.com/watch?v=5xbcnlCy-7k) Is this the End for Genting Malaysia? | GENM | 632 |
| [BgyQDJkYtDo](https://www.youtube.com/watch?v=BgyQDJkYtDo) Saham Genting Malaysia Jatuh, Rahasia Besar Indonesia Terbongkar! | GENM | 142 |
| [Uokye1GSu84](https://www.youtube.com/watch?v=Uokye1GSu84) 云顶股价20年来历史新低，Genting 彻底玩完了？#genting  #genm #gens | GENTING | 64 |
| [8RPViwkuzFQ](https://www.youtube.com/watch?v=8RPViwkuzFQ) 云顶大马GENM私有化，该卖？该接受？还能做什么？｜八卦大小文 | GENM | 52 |
| [kX2YXGLlygc](https://www.youtube.com/watch?v=kX2YXGLlygc) 云顶大动作！GENM 私有化计划全解析 ｜第一天乡下茶话会 | GENM | 33 |
| [wuVPgdar6xw](https://www.youtube.com/watch?v=wuVPgdar6xw) GENTING｜未来3年的看点是什么？ | GENTING | 26 |
| [VvGLSkUIesM](https://www.youtube.com/watch?v=VvGLSkUIesM) Genting跌回近25年低位，市场到底在怕什么？ | UNKNOWN | 18 |
| [KUkInDEtthM](https://www.youtube.com/watch?v=KUkInDEtthM) 云顶股价跌回1998年水平，股东为什么还要再掏钱？ | GENTING | 18 |
| [5MkxlZtt2_E](https://www.youtube.com/watch?v=5MkxlZtt2_E) Genting Plunged 21% In 1 Day. What Happened? | GENTING | 17 |
| [6wqA59uSSlY](https://www.youtube.com/watch?v=6wqA59uSSlY) 林国泰的豪赌：67亿私有化云顶大马，背后的棋局与信号 | GENM | 16 |

## Failures and gaps

- `dh6kHyS_JL8` (EDGE WEEKLY: Should Genting Malaysia shareholders stay or fold?) — comment section unavailable (YouTube returned no comments or count; likely disabled); fetched 0 comments, 0 in window; post written.
- `BlxP_c69dso` (title unavailable) — video unavailable (deleted/private); fetched 0 comments, 0 in window; no post written.
- `wVNY7bKPWa4` (title unavailable) — video unavailable (deleted/private); fetched 0 comments, 0 in window; no post written.

`dh6kHyS_JL8` (The Edge TV) returned no comment section or comment count at all, so no comments exist to collect; the post itself is included. Videos with zero comments are kept as posts because they are part of the in-window Genting coverage. Comment counts on YouTube are approximate (the counter includes replies and can lag), so the fetched totals are the authoritative measure of what was retrievable; no comment was invented or padded.

Creator participation is retained: 102 replies are by the video uploader and 13 are pinned. 19 reply bodies repeat another reply's exact text (short reactions such as emoji/thanks, plus creators' boilerplate replies); they are distinct comment ids and are kept.

## Exclusions

The discovery pool also contained Genting Highlands travel/theme-park videos, casino/gambling vlogs, Indonesian political commentary about gambling money, Genting Singapore (SGX:G13) analysis, and multi-stock market roundups. Those were excluded because they are not about GENTING/GENM as Malaysian listed securities. Videos that mentioned Genting only in passing (for example weekly Bursa recaps) were also dropped.

Pre-window videos were fetched only to test whether they were still receiving comments in the window. Six did and are included with their original upload dates: `gESZSALUDJE` (8 Jul 2025), `kX2YXGLlygc` (16 Oct 2025), `ltChQ03z2Gg` (17 Oct 2025), `6wqA59uSSlY` (20 Oct 2025), `6Tp_HHbypSQ` and `SAXnfqtbvOU` (22 Oct 2025). `gESZSALUDJE` is the single validator warning (upload date before the validator's 1 Oct 2025 floor); it is kept because its comment is in the window. Older videos with no in-window comments are listed in the checked-but-not-written table above. `Riu1JRlvlrI` was checked and excluded as Genting Singapore (SGX:G13), not a Malaysian counter. `BlxP_c69dso` and `wVNY7bKPWa4` were unavailable (deleted/private).

