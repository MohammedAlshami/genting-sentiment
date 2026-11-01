# YouTube collection report — Malaysian Genting, 2016–2024

- **Collected:** 2 Nov 2026
- **Video window:** 2 Nov 2016 00:00 MYT → 1 Nov 2024 23:59:59 MYT (1 Nov 2016 16:00 UTC → 1 Nov 2024 16:00 UTC)
- **Output:** `data/raw/youtube_2016-2024.jsonl`
- **Collector:** `scripts/collect_youtube_2016_2024.py` (caches in `/tmp/opencode/yt10`)
- **Videos:** 625 passed the automatic relevance/date filter; manual review removed 152 false positives and added 76 relevant videos the title heuristic missed, leaving 549 fetched (473 automatic + 76 manual); 534 posts written, 15 already posts in `youtube_full.jsonl` (no duplicate post records)
- **Records:** 4682 — 534 posts, 4148 comments
- **Posts by ticker:** GENM × 114, GENTING × 166, UNKNOWN × 254
- **Comments by post ticker:** GENM × 767, GENTING × 1036, UNKNOWN × 2345
- **Comment threads:** 2428 top-level comments, 1720 replies, 1752 distinct authors
- **Post date range:** 2016-11-04 → 2024-10-30
- **Comment date range (estimated):** 2017-05-17 → 2026-09-17; comments on these videos run through the collection date, not only to 1 Nov 2024
- **Validation:** `python3 -m genting.validate data/raw/youtube_2016-2024.jsonl` → **OK, 0 errors, 4585 warnings**. Every warning is the same expected one: the record timestamp is before the validator's fixed 2024-10-01 floor, because this file deliberately covers 2016–2024. No schema, duplicate-id or missing-field errors.

## API / quota

No YouTube Data API key is configured anywhere in the repository (`YOUTUBE_API_KEY` is absent and no key is read by the existing collectors). This collector therefore uses **yt-dlp 2026.10.21.202512**, exactly like `collect_youtube.py` and `collect_youtube_backfill.py`. There is **no Data API quota** and therefore no quota-exhaustion error to report. The relevant limits are YouTube's scraping rate limits; each request is spaced (1.2 s between searches, 2 s between comment extractions) and every non-200 / bot-check / 429 outcome is recorded per video in the failures section.

**Access result:** the platform did allow the 2016–2024 period. The earliest post written is **3 Nov 2016** and the latest is **28 Oct 2024**; no API/key blocker was hit. The only access limits were videos whose comments are disabled and videos that were deleted/private (counts below).

## Method

Discovery ran 20 queries × 8 one-year windows (2016-11-02→2017-11-01 … 2023-11-02→2024-11-01), `ytsearch40` each, using YouTube's `after:`/`before:` operators. The union pool was **3,752 unique video ids**; a cheap title/description filter for a Genting mention plus a finance signal left **630** candidates, whose full metadata was fetched (625 ok, 5 unavailable/deleted). Metadata was used to verify the upload date and subject; videos outside the window, Genting Singapore-only content, Genting Plantations/Hong Kong, travel/theme-park/car videos and unrelated `GenM`/Generation Mining results were dropped. **625** videos passed the automatic filter; a manual review removed 152 travel/car, student-assignment, unrelated-company and generic-roundup false positives and added 76 relevant videos whose titles the heuristic missed, leaving **549** videos. Each was fetched with `yt-dlp --write-comments --skip-download`; yt-dlp paginates the comment continuations and retrieves every comment and reply it is allowed to see.

The searches were (each run once per one-year window):

- `ytsearch40:genting malaysia stock after:YYYY-11-01 before:YYYY+1-11-02`
- `ytsearch40:genting berhad stock after:YYYY-11-01 before:YYYY+1-11-02`
- `ytsearch40:genting share price after:YYYY-11-01 before:YYYY+1-11-02`
- `ytsearch40:GENM 4715 after:YYYY-11-01 before:YYYY+1-11-02`
- `ytsearch40:GENTING 3182 after:YYYY-11-01 before:YYYY+1-11-02`
- `ytsearch40:genting stock analysis after:YYYY-11-01 before:YYYY+1-11-02`
- `ytsearch40:genting results dividend after:YYYY-11-01 before:YYYY+1-11-02`
- `ytsearch40:genting rights issue privatisation after:YYYY-11-01 before:YYYY+1-11-02`
- `ytsearch40:genting malaysia news after:YYYY-11-01 before:YYYY+1-11-02`
- `ytsearch40:genting takeover after:YYYY-11-01 before:YYYY+1-11-02`
- `ytsearch40:saham genting after:YYYY-11-01 before:YYYY+1-11-02`
- `ytsearch40:harga saham genting after:YYYY-11-01 before:YYYY+1-11-02`
- `ytsearch40:analisis saham genting after:YYYY-11-01 before:YYYY+1-11-02`
- `ytsearch40:berita genting after:YYYY-11-01 before:YYYY+1-11-02`
- `ytsearch40:genting untung rugi after:YYYY-11-01 before:YYYY+1-11-02`
- `ytsearch40:云顶 股票 after:YYYY-11-01 before:YYYY+1-11-02`
- `ytsearch40:云顶大马 after:YYYY-11-01 before:YYYY+1-11-02`
- `ytsearch40:云顶 股价 分析 after:YYYY-11-01 before:YYYY+1-11-02`
- `ytsearch40:云顶 业绩 股息 after:YYYY-11-01 before:YYYY+1-11-02`
- `ytsearch40:云顶 附加股 私有化 after:YYYY-11-01 before:YYYY+1-11-02`

## Comment timestamps and `time_confidence`

YouTube's public comment API exposes **only a relative age** (`3 years ago`, `11 months ago`), not an absolute publication time. For every comment this collector:

1. keeps the original label in `raw.time_text` and yt-dlp's resolved value in `raw.timestamp`;
2. computes the label's feasible interval at collection time (for `N years ago`, `[now − (N+1) years, now − N years]`), clips it to the video's upload time and the collection time;
3. sets `created_utc` to the **midpoint** of that interval and `raw.timestamp_estimate_method` to the method used;
4. sets top-level `time_confidence` to **`"relative"`** on every comment. The interval bounds are in `raw.time_text_interval_start` / `raw.time_text_interval_end`; `raw.time_text_bucket` records whether the label was year-, month-, week-, day-, hour- or minute-grained.

This means a `5 years ago` comment is only known to fall somewhere in a 12-month window; the midpoint is a defensible point estimate, **not an observed date**. No comment timestamp or text was invented. Sub-year timing within a year label cannot be recovered from YouTube's public comment API.

**Post timestamps** are different: `created_utc` is YouTube's exact upload timestamp when the metadata exposes it (`time_confidence="exact"`), otherwise the upload date at 00:00 UTC (`time_confidence="date"`). Post timestamps are not estimates from a relative label.

The earliest comment estimate is **May 2017**, not 2016, because a comment posted in late 2016 carries the label `9 years ago` at collection; that label covers Nov 2016 → Nov 2017 and its midpoint is May 2017. The comments exist, but the label cannot place them inside 2016. The year-by-year comment counts below are therefore label-driven and should not be read as a precise activity timeline.

Label precision of the comments written: year × 4147, month × 1.

Because labels are coarse, many comments share an estimated day: the largest cluster is **161 comments at 2021-06-25**. This is an artefact of the relative label, not evidence of a one-day burst.

## Coverage by upload year

| Upload year | Posts | Comments written |
| --- | ---: | ---: |
| 2016 | 3 | 7 |
| 2017 | 13 | 6 |
| 2018 | 16 | 201 |
| 2019 | 47 | 313 |
| 2020 | 61 | 1129 |
| 2021 | 98 | 1335 |
| 2022 | 118 | 296 |
| 2023 | 105 | 347 |
| 2024 | 73 | 514 |

## Videos collected

| Video | Channel | Ticker | Uploaded | Views | Comments (metadata) | Fetched | Written | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| [yK7y0qq4umU](https://www.youtube.com/watch?v=yK7y0qq4umU) GENTING 只能等第2支脚 | Double Swords Investing | GENTING | 2024-10-30 | 2382 | 3 | 3 | 3 | ok |
| [z1CSwnDajnA](https://www.youtube.com/watch?v=z1CSwnDajnA) EVENING 5: Genting awards RM1.36 bil contracts for its FLNG project | The Edge TV | GENTING | 2024-10-28 | 7470 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [4Zs4_WN5tTk](https://www.youtube.com/watch?v=4Zs4_WN5tTk) GENTING 这个支撑不可以跌破 | Double Swords Investing | GENTING | 2024-10-26 | 3416 | 1 | 1 | 1 | ok |
| [VX1_tBVB6_o](https://www.youtube.com/watch?v=VX1_tBVB6_o) GENTING 云顶 - 反弹而上 Bounce up | Double Swords Investing | GENTING | 2024-10-20 | 4541 | 5 | 5 | 5 | ok |
| [-2FBltuW8z4](https://www.youtube.com/watch?v=-2FBltuW8z4) Daily #KLSE #BURSA UPDATE - 18-10-2024 💥GENM SAYS US$600m BIMINI LAWSUIT WON’T IMPACT FINANCIAL💥💥 | Trading with KS | GENM | 2024-10-18 | 769 | 0 | 0 | 0 | ok |
| [BayVUdHeRVQ](https://www.youtube.com/watch?v=BayVUdHeRVQ) GENTING 云顶 - 今早跌破4.00! 可以去捞便宜吗？分享捞的技巧. [CC ENG 中英文字幕］ | Double Swords Investing | GENTING | 2024-10-15 | 5390 | 5 | 5 | 5 | ok |
| [xJRGwjAurrw](https://www.youtube.com/watch?v=xJRGwjAurrw) 15 10 2024 第552期：GENTING 是时候捞了吗？ | 我是雷公 | GENTING | 2024-10-15 | 2057 | 4 | 4 | 4 | ok |
| [UCCEudWGYnA](https://www.youtube.com/watch?v=UCCEudWGYnA) EVENING 5: GenM unit named in US$600 mil lawsuit | The Edge TV | UNKNOWN | 2024-10-14 | 11360 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [rsEAl1YOFuM](https://www.youtube.com/watch?v=rsEAl1YOFuM) Daily #KLSE #BURSA UPDATE - 14-10-2024 💥GENM UNIT SUED FOR US$600m💥CAPITALA SHAREHOLDERS APPROVE 💥 | Trading with KS | GENM | 2024-10-14 | 1044 | 0 | 0 | 0 | ok |
| [yBiajoacPqA](https://www.youtube.com/watch?v=yBiajoacPqA) GENTING｜ 转型之路有没有机会成功？ | 大老板投资记录本 | GENTING | 2024-09-28 | 14940 | 30 | 30 | 30 | ok |
| [vIk9DGLUJoU](https://www.youtube.com/watch?v=vIk9DGLUJoU) 彭伊党扬言关赌场　云顶股价开盘走跌 【东方头条】2024-9-17 | Oriental Daily News Malaysia 马来西亚东方日报  | GENTING | 2024-09-17 | 3908 | 11 | 11 | 11 | ok |
| [I5maCzNzZp8](https://www.youtube.com/watch?v=I5maCzNzZp8) GENTING GENM 云顶双雄- 图表分析很难看.看基本面分析可以在什么价位捞？［CC 中英文字幕］ | Double Swords Investing | UNKNOWN | 2024-09-10 | 5063 | 13 | 13 | 13 | ok |
| [ob3B8tOscIU](https://www.youtube.com/watch?v=ob3B8tOscIU) Daily KLSE BURSA UPDATE - 30-8-2024💥KLCI CONTINUE UP 25 POINTS💥GENTING GENM 盈利上升💥 YTLPOWR YTL SAM | Trading with KS | UNKNOWN | 2024-08-30 | 1187 | 2 | 2 | 2 | ok |
| [BIjv1I7F-W8](https://www.youtube.com/watch?v=BIjv1I7F-W8) KS看股 - 马股 KLSE BURSA 分享 - 30-8-2024 💥综指继续涨25点!!💥GENTING GENM 盈利上升💥 YTLPOWR YTL MPI SAM HTPADU | Trading with KS | UNKNOWN | 2024-08-30 | 4037 | 8 | 8 | 8 | ok |
| [4d9UuLJ0eQo](https://www.youtube.com/watch?v=4d9UuLJ0eQo) GENM Q2 2024 Financial Summary: Key Insights and Analysis \| Investment Haus | Investment Haus | UNKNOWN | 2024-08-30 | 6 | 1 | 1 | 1 | ok |
| [0HxTaoBJXz4](https://www.youtube.com/watch?v=0HxTaoBJXz4) Untung bersih suku kedua Genting Malaysia naik 8 0 peratus, RM82 24 juta | Berita Harian Online | UNKNOWN | 2024-08-30 | 72 | 0 | 0 | 0 | ok |
| [EPNgSws_HC4](https://www.youtube.com/watch?v=EPNgSws_HC4) 28-8-2024 浅谈 #BAHVEST 0098 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2024-08-28 | 150 | 0 | 0 | 0 | ok |
| [mfBjZXrzhi8](https://www.youtube.com/watch?v=mfBjZXrzhi8) Understanding Genting's Cash Flows: Q1 2024 Financial Analysis \| Investment Haus | Investment Haus | UNKNOWN | 2024-08-18 | 7 | 1 | 1 | 1 | ok |
| [dyTQOqJdqfg](https://www.youtube.com/watch?v=dyTQOqJdqfg) Genting Malaysia: Q1 2023 Changes in Equity Explained \| Investment Haus | Investment Haus | UNKNOWN | 2024-08-17 | 16 | 1 | 1 | 1 | ok |
| [HG3Kpbk8rlg](https://www.youtube.com/watch?v=HG3Kpbk8rlg) Exploring Changes in Equity: Genting's Financial Strategy \| Investment Haus | Investment Haus | UNKNOWN | 2024-08-13 | 1 | 1 | 1 | 1 | ok |
| [WHAJqlyIckM](https://www.youtube.com/watch?v=WHAJqlyIckM) How Genting Utilizes Debt for Strategic Growth \| Q1 Financial Analysis \| Investment Haus | Investment Haus | UNKNOWN | 2024-08-12 | 9 | 1 | 1 | 1 | ok |
| [SiFscI1DFKE](https://www.youtube.com/watch?v=SiFscI1DFKE) Deep Dive: Analyzing Assets & Liabilities in Genting's Q1 Financials \| Investment Haus | Investment Haus | UNKNOWN | 2024-08-11 | 2 | 1 | 1 | 1 | ok |
| [CQqEMx6Vzeo](https://www.youtube.com/watch?v=CQqEMx6Vzeo) [Short] Deep Dive: Genting Malaysia's Q1 Financial Statements \| Investment Haus | Investment Haus | UNKNOWN | 2024-07-30 | 13 | 1 | 1 | 1 | ok |
| [n2A3_Uq6kCk](https://www.youtube.com/watch?v=n2A3_Uq6kCk) 17-7-2024 浅谈 #AGX 0299 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2024-07-17 | 125 | 0 | 0 | 0 | ok |
| [v2AzAE1YmlE](https://www.youtube.com/watch?v=v2AzAE1YmlE) GENTING 终于止跌了.即时点评未来的走势. 午盘筹码峰技术分析![中文字幕］ | Double Swords Investing | GENTING | 2024-07-12 | 4769 | 30 | 30 | 30 | ok |
| [CKD0Rf92bgM](https://www.youtube.com/watch?v=CKD0Rf92bgM) 【马股分析】大马蓝筹股哪个是冠军?🔥 #TENAGA #GAMUDA 云顶值得关注吗？#马股 #BURSA #KLCI｜#技术分析 | Andy Yew | GENTING | 2024-07-05 | 9249 | 2 | 2 | 2 | ok |
| [z6pvju9ts5w](https://www.youtube.com/watch?v=z6pvju9ts5w) 21-6-2024 盘中浅谈 #GENTING 3182 \| 马股 | 股市先锋队 | GENTING | 2024-06-21 | 206 | 0 | 0 | 0 | ok |
| [oe8gTgTgInM](https://www.youtube.com/watch?v=oe8gTgTgInM) GENTING 云顶: 突破筹码主力线是买入讯号! [CC 中英文 ENG SUB] | Double Swords Investing | GENTING | 2024-06-21 | 4061 | 10 | 10 | 10 | ok |
| [Koz1Gq6g73M](https://www.youtube.com/watch?v=Koz1Gq6g73M) NEWS: Genting gives update on Alzheimer drug | The Edge TV | GENTING | 2024-06-20 | 15422 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [Wu5UZyX1LT4](https://www.youtube.com/watch?v=Wu5UZyX1LT4) NEWS: ‘Transformation of Genting is just starting’ | The Edge TV | GENTING | 2024-06-20 | 20427 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [CAGeXL00Re0](https://www.youtube.com/watch?v=CAGeXL00Re0) NEWS: Genting to invest RM277 mil for another China power plant | The Edge TV | GENTING | 2024-06-20 | 917 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [TS8hZ3O5ba8](https://www.youtube.com/watch?v=TS8hZ3O5ba8) NEWS: Genting’s energy division could contribute US$1.3 bil in revenue | The Edge TV | GENTING | 2024-06-20 | 3117 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [dnrdMZaJE_M](https://www.youtube.com/watch?v=dnrdMZaJE_M) EVENING 5: Genting bets big on overseas energy projects | The Edge TV | GENTING | 2024-06-20 | 6441 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [cSCwVjgjLEU](https://www.youtube.com/watch?v=cSCwVjgjLEU) 14 June Genting On Fire Why the Stock Price still Bull? #Fire breaks out in Genting Highlands | 双阳倍量 Double Volume Bullish Channel  | GENTING | 2024-06-18 | 88 | 2 | 2 | 2 | ok |
| [X4IrLxL4sQU](https://www.youtube.com/watch?v=X4IrLxL4sQU) 云顶火灾GENM 股会怎么走？#技术分析 #trading #双阳倍量 #gentinghighland #云顶 #云顶之弈 #trending #股市 #赌博 #stockmarket | 双阳倍量 Double Volume Bullish Channel  | GENTING | 2024-06-14 | 654 | 1 | 1 | 1 | ok |
| [ZH92nfa3GRg](https://www.youtube.com/watch?v=ZH92nfa3GRg) AI革命即将引发大马第一中文媒体大裁员？谁是FBMKLCI新贵？云顶股价为何不会起？【谈股论今 180】 | 陈剑老师投资教育频道 | GENTING | 2024-06-04 | 62892 | 50 | 50 | 50 | ok |
| [GKeYngfFUdE](https://www.youtube.com/watch?v=GKeYngfFUdE) GENTING 云顶:股价被拖累,不升反跌! 支撑价位在那里？ | Double Swords Investing | GENTING | 2024-06-01 | 3788 | 9 | 9 | 9 | ok |
| [LduBZ0xVAwQ](https://www.youtube.com/watch?v=LduBZ0xVAwQ) KS看股 - 马股 KLSE BURSA 分享 - 31-5-2024 💥云顶首季净利飙5倍 💥DSONIC盈利创纪录 💥 PTT NOTION HTPADU LAGENDA HUPSENG | Trading with KS | UNKNOWN | 2024-05-31 | 4775 | 13 | 13 | 13 | ok |
| [Dk3dmeOoUD0](https://www.youtube.com/watch?v=Dk3dmeOoUD0) GENTING 云顶:今天突破了所有的筹码主力线! | Double Swords Investing | GENTING | 2024-05-28 | 2825 | 9 | 9 | 9 | ok |
| [PkSIxKuBuRc](https://www.youtube.com/watch?v=PkSIxKuBuRc) GENM GENTING MALAYSIA 云顶大马 - 猜测即将公布的业绩,也聊聊技术图表. | Double Swords Investing | UNKNOWN | 2024-05-25 | 4579 | 8 | 8 | 8 | ok |
| [MsdEK-Yn8HE](https://www.youtube.com/watch?v=MsdEK-Yn8HE) GENTING 云顶- 我猜测, 即将公布的盈利是..... | Double Swords Investing | GENTING | 2024-05-20 | 6097 | 18 | 18 | 18 | ok |
| [KPNvs2Vg1rs](https://www.youtube.com/watch?v=KPNvs2Vg1rs) GENM 4715 你会投资老牌王国吗？ | Explore busking 街道 | UNKNOWN | 2024-05-17 | 1347 | 0 | 0 | 0 | ok |
| [sOS2EDE11HY](https://www.youtube.com/watch?v=sOS2EDE11HY) 14 05 2024 第460期：GENM 终于反弹了！买吗？ | 我是雷公 | GENM | 2024-05-14 | 1776 | 6 | 6 | 6 | ok |
| [OOWNVngpk4k](https://www.youtube.com/watch?v=OOWNVngpk4k) GENM GENTING MALAYSIA 云顶大马 ： 看好业绩会带动股价.下一个阻力线在那里？ | Double Swords Investing | UNKNOWN | 2024-05-13 | 5271 | 20 | 20 | 20 | ok |
| [sgjtMwHCaW0](https://www.youtube.com/watch?v=sgjtMwHCaW0) GENTING 云顶 -出现了牛指标!![CC 中英字幕 ENG SUB] | Double Swords Investing | GENTING | 2024-05-12 | 7701 | 15 | 15 | 15 | ok |
| [6RCeaJvsTuQ](https://www.youtube.com/watch?v=6RCeaJvsTuQ) GENM GENTING MALAYSIA - RSI 底背离,提前预示趋势反转？CC 中英字幕 ENG SUB | Double Swords Investing | UNKNOWN | 2024-04-22 | 4358 | 6 | 6 | 6 | ok |
| [4IG04K2NUlI](https://www.youtube.com/watch?v=4IG04K2NUlI) GENTING 云顶 - 现在可以去捞底了吗？ [CC 中英文 ENG SUB] | Double Swords Investing | GENTING | 2024-04-21 | 5064 | 11 | 11 | 11 | ok |
| [SAPkWbafLWM](https://www.youtube.com/watch?v=SAPkWbafLWM) 2024's Cash Kings: Genting & Yangzijiang's Big Win! 🚀\| 🦖 #TheInvestingIguana EP331 | Iggy the Investing Iguana | GENTING | 2024-04-14 | 350 | 2 | 2 | 2 | ok |
| [RwzJ0ewp-Qg](https://www.youtube.com/watch?v=RwzJ0ewp-Qg) 12-4-2024 浅谈 #GENTING 3182 #PGF 8117 \| 马股 | 股市先锋队 | GENTING | 2024-04-13 | 176 | 0 | 0 | 0 | ok |
| [fCotTtPDPtM](https://www.youtube.com/watch?v=fCotTtPDPtM) GENTING 云顶: 价跌量缩，支撑显现，期待止跌回升讯号!.[CC 中英文字幕 ENG SUB]. | Double Swords Investing | GENTING | 2024-04-09 | 3717 | 6 | 6 | 6 | ok |
| [fkgYrwTdB9k](https://www.youtube.com/watch?v=fkgYrwTdB9k) GENM HARTA VS CTOS SNS  云顶大马 GENTING MALAYSIA 盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB].01042024 | Double Swords Investing | UNKNOWN | 2024-04-01 | 4795 | 13 | 13 | 13 | ok |
| [8BeDrtWa7po](https://www.youtube.com/watch?v=8BeDrtWa7po) Daily KLSE BURSA UPDATE - 20-3-2024💥TOPGLOV 2Q NET LOSS NARROWS💥MBB IB CUT GENM FY2024 ESTIMATES💥 | Trading with KS | GENM | 2024-03-20 | 1088 | 2 | 2 | 2 | ok |
| [aZZKycFZnbs](https://www.youtube.com/watch?v=aZZKycFZnbs) GENM GENTING MALAYSIA 云顶大马 - 出现了牛指标,也突破了筹码主力线. 盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB].09032024 | Double Swords Investing | UNKNOWN | 2024-03-09 | 4748 | 18 | 18 | 18 | ok |
| [cN__h5l2nA4](https://www.youtube.com/watch?v=cN__h5l2nA4) GENM GENTING MALAYSIA 云顶大马 -TauRx 不关事. 之前出现了熊指标! 午盘筹码峰技术分析.[CC 中英文字幕 ENG SUB].07032024 | Double Swords Investing | UNKNOWN | 2024-03-07 | 4012 | 19 | 19 | 19 | ok |
| [Jh-A83zQrzY](https://www.youtube.com/watch?v=Jh-A83zQrzY) 云顶人山人海，股价也来突破？Ep 550 \| BURSA MARKET 第五百五十集Market 开箱 | EL StockTrooper | UNKNOWN | 2024-03-06 | 15 | 0 | 0 | 0 | ok |
| [lbtyTR7H0Ko](https://www.youtube.com/watch?v=lbtyTR7H0Ko) Daily KLSE BURSA UPDATE - 5-3-2024💥CRESBLD WINS RM448.5mil CONTRACT💥GENTING TARGET COULD INCREASE?💥 | Trading with KS | GENTING | 2024-03-05 | 1068 | 4 | 4 | 4 | ok |
| [RKGSJ2v066U](https://www.youtube.com/watch?v=RKGSJ2v066U) GENTING - 有跌有机会.但是,如何去捉住机会？ [CC 中英文字幕 ENG SUB].03032024 | Double Swords Investing | GENTING | 2024-03-03 | 4235 | 18 | 18 | 18 | ok |
| [vbfz3Ondz0w](https://www.youtube.com/watch?v=vbfz3Ondz0w) Daily KLSE BURSA UPDATE - 1-3-2024💥AAX BIG DROP 11% ! 💥GENTING FY2023 TURN PROFIT ! 💥 UTDPLT JTIASA | Trading with KS | GENTING | 2024-03-01 | 1129 | 0 | 0 | 0 | ok |
| [i8yOyzmBfKw](https://www.youtube.com/watch?v=i8yOyzmBfKw) KS看股 - 马股 KLSE BURSA 分享 - 1-3-2024 💥AAX 大跌 11% ! 💥云顶 4 年首获利! 💥 AAX HIBISCS GENTING KGB ICON SPSETIA | Trading with KS | GENTING | 2024-03-01 | 4812 | 13 | 13 | 13 | ok |
| [hb603vtiPbM](https://www.youtube.com/watch?v=hb603vtiPbM) GENTING 云顶 - 有雄厚筹码峰支撑住! 午盘筹码峰技术分析.[CC 中英文字幕 ENG SUB].23022024 | Double Swords Investing | GENTING | 2024-02-23 | 3802 | 7 | 7 | 7 | ok |
| [aIhdYLeBBTI](https://www.youtube.com/watch?v=aIhdYLeBBTI) GENTING  云顶- 突破顶部筹码峰. 盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB].20022024 | Double Swords Investing | GENTING | 2024-02-20 | 3104 | 7 | 7 | 7 | ok |
| [h5R4FCRxSG8](https://www.youtube.com/watch?v=h5R4FCRxSG8) GENM GENTING MALAYSIA 云顶大马- 把策略预备好等业绩! 午盘筹码峰技术分析.[CC 中英文字幕 ENG SUB].19022024 | Double Swords Investing | UNKNOWN | 2024-02-19 | 3715 | 7 | 7 | 7 | ok |
| [cxF02aSYxhs](https://www.youtube.com/watch?v=cxF02aSYxhs) GENTING 云顶 - 洗盘把不稳定的筹码洗掉,是为了后来的拉升. 盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB].16022024 | Double Swords Investing | GENTING | 2024-02-16 | 3833 | 4 | 4 | 4 | ok |
| [UOn_uXXRfX4](https://www.youtube.com/watch?v=UOn_uXXRfX4) GENM GENTING MALAYSIA  云顶大马- 万事俱备,只欠东风! 午盘筹码峰技术分析.[CC 中英文字幕 ENG SUB].13022024 | Double Swords Investing | UNKNOWN | 2024-02-13 | 3259 | 6 | 6 | 6 | ok |
| [WYeXLxdJK2s](https://www.youtube.com/watch?v=WYeXLxdJK2s) GENTING -  云顶新加坡的市值比母公司更高! 云顶值得RM8.77? [CC 中英文字幕 ENG SUB].12022024 | Double Swords Investing | GENTING | 2024-02-12 | 6312 | 12 | 12 | 12 | ok |
| [PCjWW_cxP1g](https://www.youtube.com/watch?v=PCjWW_cxP1g) 2-2-2024 浅谈 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2024-02-04 | 154 | 2 | 2 | 2 | ok |
| [pyglBSM7ME8](https://www.youtube.com/watch?v=pyglBSM7ME8) 02 01 2024 第395期：GENM 启动新年前的涨势！追吗？ | 我是雷公 | GENM | 2024-02-02 | 1844 | 9 | 9 | 9 | ok |
| [_TnqgFCfsDE](https://www.youtube.com/watch?v=_TnqgFCfsDE) GENTING 云顶- 再次突破筹码主力线. 盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB].28012024 | Double Swords Investing | GENTING | 2024-01-28 | 3018 | 20 | 20 | 20 | ok |
| [95RFM5Y0ZPY](https://www.youtube.com/watch?v=95RFM5Y0ZPY) GENM GENTING MALAYSIA 云顶大马 -又有机会加仓了. 盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB].14012024 | Double Swords Investing | UNKNOWN | 2024-01-14 | 5309 | 6 | 6 | 6 | ok |
| [vkj5drIdQ2Y](https://www.youtube.com/watch?v=vkj5drIdQ2Y) GENTING 云顶 - 可以进场了吗？午盘筹码峰技术分析.[CC 中英文字幕 ENG SUB].12012024 | Double Swords Investing | GENTING | 2024-01-12 | 4864 | 15 | 15 | 15 | ok |
| [gpi9H8wEk1Y](https://www.youtube.com/watch?v=gpi9H8wEk1Y) 11 01 2024 第378期：GENM 大跌4 6%！哪里能上车？ | 我是雷公 | GENM | 2024-01-11 | 3569 | 13 | 13 | 13 | ok |
| [slcXrUoSGhY](https://www.youtube.com/watch?v=slcXrUoSGhY) 8-1-2024 浅谈 #GENTING 3182 \| 马股 | 股市先锋队 | GENTING | 2024-01-08 | 103 | 2 | 2 | 2 | ok |
| [-gL2x4ZwEY4](https://www.youtube.com/watch?v=-gL2x4ZwEY4) GENTING 云顶 - 突破阻力线是买入讯号! 盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB].06012024 | Double Swords Investing | GENTING | 2024-01-06 | 3493 | 10 | 10 | 10 | ok |
| [yld2-l6roCk](https://www.youtube.com/watch?v=yld2-l6roCk) GENTING 云顶 - 要有耐心的运用技术分析去收票.盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB].28122023. | Double Swords Investing | GENTING | 2023-12-28 | 2692 | 14 | 14 | 14 | ok |
| [ZnN6Y0v3u4c](https://www.youtube.com/watch?v=ZnN6Y0v3u4c) GENM GENTING MALAYSIA 云顶大马- 上攻乏力,幸好有筹码峰强支撑! 盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB].22122023. | Double Swords Investing | UNKNOWN | 2023-12-22 | 1930 | 9 | 9 | 9 | ok |
| [rg18rNHzc4o](https://www.youtube.com/watch?v=rg18rNHzc4o) 15-12-2023 浅谈 #GENM 4715 #SMRT 0117 #RANHILL 5272 \| 马股 | 股市先锋队 | GENM | 2023-12-17 | 128 | 2 | 2 | 2 | ok |
| [Gp42gDXbBM0](https://www.youtube.com/watch?v=Gp42gDXbBM0) GENTING 和 GENM 业绩好转！已经成功突破主力筹码峰！入场前一定要知道的一个隐患！TENAGA有望冲破RM10？！ | SK 投资空间 | UNKNOWN | 2023-12-15 | 980 | 1 | 1 | 1 | ok |
| [kXk-zoNQhW8](https://www.youtube.com/watch?v=kXk-zoNQhW8) GENM GENTING MALAYSIA 云顶大马 - 连蓝线也跌破了! 盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB].10122023. | Double Swords Investing | UNKNOWN | 2023-12-10 | 2905 | 3 | 3 | 3 | ok |
| [7k6bffRwr9g](https://www.youtube.com/watch?v=7k6bffRwr9g) GENTING - 回调买上涨的机会! 盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB].09122023. | Double Swords Investing | GENTING | 2023-12-09 | 3076 | 10 | 10 | 10 | ok |
| [E01Y6oqmXA4](https://www.youtube.com/watch?v=E01Y6oqmXA4) GENTING - 隨便买,随便收! 午盘筹码峰技术分析.[CC 中英文字幕 ENG SUB] 28112023. | Double Swords Investing | GENTING | 2023-11-28 | 5627 | 7 | 7 | 7 | ok |
| [D0FCUkg6BTo](https://www.youtube.com/watch?v=D0FCUkg6BTo) 27-11-2023 浅谈 #GENTING 3182 \| 马股 | 股市先锋队 | GENTING | 2023-11-27 | 89 | 0 | 0 | 0 | ok |
| [ZoDXwF6XVS4](https://www.youtube.com/watch?v=ZoDXwF6XVS4) GENM GENTING MALAYSIA 云顶大马 -  中国旅客免签证30天与业绩大好, 股价要突破阻力不是难事! 盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB] 25112023. | Double Swords Investing | UNKNOWN | 2023-11-25 | 4747 | 8 | 8 | 8 | ok |
| [GHC13PbfeXo](https://www.youtube.com/watch?v=GHC13PbfeXo) 24-11-2023 浅谈 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2023-11-24 | 256 | 0 | 0 | 0 | ok |
| [euV78K4Sbhs](https://www.youtube.com/watch?v=euV78K4Sbhs) Daily KLSE BURSA UPDATE - 24-11-2023💥GENTING 3Q PROFIT UP 3 FOLD💥KGB 3Q PROFIT UP DOUBLE 💥GENTING | Trading with KS | UNKNOWN | 2023-11-24 | 890 | 2 | 2 | 2 | ok |
| [jl1plZ2pWCY](https://www.youtube.com/watch?v=jl1plZ2pWCY) KS看股 - 马股 KLSE BURSA 分享 - 24-11-2023 💥云顶 3Q 多赚逾3倍!💥KGB 3Q 净利倍增!💥 GENTING GENM RAPID ALLIANZ PCHEM | Trading with KS | UNKNOWN | 2023-11-24 | 3322 | 1 | 1 | 1 | ok |
| [By5kMfIedCE](https://www.youtube.com/watch?v=By5kMfIedCE) GENTING 云顶 -  6块以上是迟早的事. 盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB] 24112023. | Double Swords Investing | GENTING | 2023-11-24 | 6901 | 16 | 16 | 16 | ok |
| [y8wkNHNUoOQ](https://www.youtube.com/watch?v=y8wkNHNUoOQ) EVENING 5: Genting Group earnings jump on post-pandemic recovery momentum | The Edge TV | GENTING | 2023-11-23 | 5336 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [Lyel2j0Jcyk](https://www.youtube.com/watch?v=Lyel2j0Jcyk) GENM GENTING MALAYSIA 云顶大马 - 聊聊买入信号! 盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB] 18112023. | Double Swords Investing | UNKNOWN | 2023-11-18 | 3541 | 4 | 4 | 4 | ok |
| [B1RbwsYNYhI](https://www.youtube.com/watch?v=B1RbwsYNYhI) GENM GENTING MALAYSIA 云顶大马- 阻力重重! 盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB] 12112023. | Double Swords Investing | UNKNOWN | 2023-11-12 | 2481 | 1 | 1 | 1 | ok |
| [NALKAK1hQZo](https://www.youtube.com/watch?v=NALKAK1hQZo) GENTING -.云顶新加坡净利大涨60%, 对云顶集团会有什么影响？ 盘后技术分析.[CC 中英文字幕 ENG SUB] 12112023. | Double Swords Investing | GENTING | 2023-11-12 | 4380 | 3 | 3 | 3 | ok |
| [kOYAFG5S_yY](https://www.youtube.com/watch?v=kOYAFG5S_yY) GENM GENTING MALAYSIA 云顶 - 止跌了,可以去捞吗？ 盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB] 29102023. | Double Swords Investing | UNKNOWN | 2023-10-29 | 3308 | 10 | 10 | 10 | ok |
| [Ki05Jw7h5LE](https://www.youtube.com/watch?v=Ki05Jw7h5LE) GENM GENTING MALAYSIA 云顶大马 -  聊聊止损策略. 盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB] 21102023. | Double Swords Investing | UNKNOWN | 2023-10-21 | 3044 | 4 | 4 | 4 | ok |
| [RkavhlHQV6g](https://www.youtube.com/watch?v=RkavhlHQV6g) Genting Malaysia 难复疫前之勇, 下砍云顶大马营业额预测 Lower GenM revenue estimates #klse #malaysia #stockmarket #大马股市 | Newbie Invest | UNKNOWN | 2023-10-02 | 99 | 0 | 0 | 0 | ok |
| [ikucLpZAzLw](https://www.youtube.com/watch?v=ikucLpZAzLw) 买GENTING比较好？GENM只要做对任何一件事股价都能涨！ | 大老板投资记录本 | UNKNOWN | 2023-09-29 | 14880 | 31 | 31 | 31 | ok |
| [zWh3cavlYAU](https://www.youtube.com/watch?v=zWh3cavlYAU) 云顶大马RM3 - RM3.50指日可待？连续3年业绩进步，股价却保持！ | 大老板投资记录本 | GENM | 2023-09-29 | 12130 | 15 | 15 | 15 | ok |
| [hSTUSeW4zrU](https://www.youtube.com/watch?v=hSTUSeW4zrU) GENM 云顶大马- 等待止跌回升弹上去的讯号. 盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB] 27092023. | Double Swords Investing | GENM | 2023-09-27 | 3778 | 8 | 8 | 8 | ok |
| [ImJHncjTCWg](https://www.youtube.com/watch?v=ImJHncjTCWg) Genting的投资机会浮现？为什么投行那么看好！ | 大老板投资记录本 | UNKNOWN | 2023-09-25 | 19284 | 17 | 17 | 17 | ok |
| [-boDJUb8X1o](https://www.youtube.com/watch?v=-boDJUb8X1o) TA Securities `bertaruh' tiada kenaikan cukai judi dalam Bajet 2024, pilih saham Genting | DagangNews | GENTING | 2023-09-20 | 93 | 0 | 0 | 0 | ok |
| [gAEne-LxQ8s](https://www.youtube.com/watch?v=gAEne-LxQ8s) 6-9-2023 浅谈 #GENTING 3182 \| 马股 | 股市先锋队 | GENTING | 2023-09-06 | 210 | 0 | 0 | 0 | ok |
| [k-PF8mj9Y44](https://www.youtube.com/watch?v=k-PF8mj9Y44) GENTING 云顶 - 逃顶后，要耐心等待止跌回升讯号..盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB] 03092023. | Double Swords Investing | GENTING | 2023-09-02 | 3660 | 14 | 14 | 14 | ok |
| [bbK6CTbz1AY](https://www.youtube.com/watch?v=bbK6CTbz1AY) PCHEM即将要反弹了！GENTING形成黄金交叉！主力筹码峰均价在这里！ HAPSENG的RSI已经超买了！ | SK 投资空间 | UNKNOWN | 2023-08-26 | 1945 | 2 | 2 | 2 | ok |
| [caScL1O6-f4](https://www.youtube.com/watch?v=caScL1O6-f4) GENTING - 突破这个价位是买入讯号.盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB] 26082023. | Double Swords Investing | GENTING | 2023-08-26 | 2684 | 1 | 1 | 1 | ok |
| [q3O8y7v-mOM](https://www.youtube.com/watch?v=q3O8y7v-mOM) TENAGA有入场机会！GENM大选后蓄势待发！已经来到了主力筹码峰！PHARMA有反弹讯号！ | SK 投资空间 | UNKNOWN | 2023-08-19 | 2169 | 3 | 3 | 3 | ok |
| [uBLVuuYGV7I](https://www.youtube.com/watch?v=uBLVuuYGV7I) GENM GENTING MALAYSIA- 今天跌破MA200.YT会员问股福利.午盘筹码峰技术分析.18082023. | Double Swords Investing | UNKNOWN | 2023-08-18 | 3570 | 1 | 1 | 1 | ok |
| [dkpMUwVv1Vo](https://www.youtube.com/watch?v=dkpMUwVv1Vo) GENTING - RSI 超买区.[CC 中英文 ENG SUB].YT会员问福利.午盘筹码峰技术分析.16082023. | Double Swords Investing | GENTING | 2023-08-16 | 3198 | 2 | 2 | 2 | ok |
| [fkfcK99uVOc](https://www.youtube.com/watch?v=fkfcK99uVOc) GENM GENTING MALAYSIA- 今天冲高回落，接下来如何操作? [CC 中英文 ENG SUB].盘后筹码峰技术分析.14082023. | Double Swords Investing | UNKNOWN | 2023-08-14 | 2826 | 2 | 2 | 2 | ok |
| [6gSPDAwl78M](https://www.youtube.com/watch?v=6gSPDAwl78M) 【热股追踪】 GENTING  在6 州选过后技术形势分析，能否继续上吗 ？挑战价位在哪里 ？   20230813（中英文CC 字幕）@mytraderview | MYtraderview 大马股市技术分析交易 + 生活日志 | UNKNOWN | 2023-08-13 | 1389 | 2 | 2 | 2 | ok |
| [IZBJhfD7Tlk](https://www.youtube.com/watch?v=IZBJhfD7Tlk) Daily KLSE BURSA UPDATE - 11-8-2023💥SPTOTO MAGNUM GENTING CAN REBOUND?💥PHARMA 2Q PROFIT UP ! 💥SPTOTO | Trading with KS | UNKNOWN | 2023-08-11 | 895 | 0 | 0 | 0 | ok |
| [YaoMMGXHjCk](https://www.youtube.com/watch?v=YaoMMGXHjCk) Daily KLSE BURSA UPDATE - 4-8-2023💥GENTING GOING TO REBOUND?💥VOLCANO UP 18% 💥 VOLCANO HENGYUAN NAIM | Trading with KS | UNKNOWN | 2023-08-04 | 954 | 0 | 0 | 0 | ok |
| [S9kn9K2bBbs](https://www.youtube.com/watch?v=S9kn9K2bBbs) KS看股- 马股 KLSE BURSA 分享 - 4-8-2023 💥云顶 要反弹了吗?💥VOLCANO 涨 18%💥 VOLCANO HENGYUAN NAIM GENM GENTING TAS | Trading with KS | UNKNOWN | 2023-08-04 | 3345 | 4 | 4 | 4 | ok |
| [t2lHObx24LU](https://www.youtube.com/watch?v=t2lHObx24LU) GENM GENTING MALAYSIA - 现在可以average down 吗？[CC 中英文字幕 ENG SUB]. YT 会员问股福利.午盘筹码峰技术分析.04082023. | Double Swords Investing | UNKNOWN | 2023-08-04 | 2996 | 1 | 1 | 1 | ok |
| [FgErFGVZ4eU](https://www.youtube.com/watch?v=FgErFGVZ4eU) 31-7-2023 浅谈 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2023-07-31 | 109 | 0 | 0 | 0 | ok |
| [stJR3SnbtK0](https://www.youtube.com/watch?v=stJR3SnbtK0) GENM GENTING MALAYSIA  - 现在可以买吗？？[CC 中英文字幕 ENG SUB]. YT会员问股福利.午盘筹码峰技术分析.28072023. | Double Swords Investing | UNKNOWN | 2023-07-28 | 2903 | 2 | 2 | 2 | ok |
| [cfBQH2nGUO0](https://www.youtube.com/watch?v=cfBQH2nGUO0) NEWS: King’s Park in Genting Highlands officially launched | The Edge TV | GENTING | 2023-07-25 | 7637 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [DRmRYiRhgwo](https://www.youtube.com/watch?v=DRmRYiRhgwo) GENTING 云顶- 前方有套牢盘挡路.[CC 中英文字幕 ENG SUB]. 盘后筹码峰技术分析.23072023. | Double Swords Investing | GENTING | 2023-07-23 | 1812 | 1 | 1 | 1 | ok |
| [Fd6vpzrNgdE](https://www.youtube.com/watch?v=Fd6vpzrNgdE) GENM GENTING MALAYSIA - 有套牢盘挡路.[CC 中英文字幕 ENG SUB]. YT会员问股福利.午盘筹码峰技术分析.20072023. | Double Swords Investing | UNKNOWN | 2023-07-20 | 1796 | 1 | 1 | 1 | ok |
| [glCjosRmTYE](https://www.youtube.com/watch?v=glCjosRmTYE) GENM GENTING MALAYSIA 云顶大马 - 突破筹码峰的POC. [CC 中英文字幕 ENG SUB]. 盘后筹码峰技术分析.16072023. | Double Swords Investing | UNKNOWN | 2023-07-16 | 2578 | 2 | 2 | 2 | ok |
| [Em21mJdHpjY](https://www.youtube.com/watch?v=Em21mJdHpjY) GENM GENTING MALAYSIA 云顶大马 - 是不是止跌回升了?[CC 中英文字幕 ENG SUB]. YT会员问股福利.午时筹码峰技术分析.13072023. | Double Swords Investing | UNKNOWN | 2023-07-13 | 3270 | 5 | 5 | 5 | ok |
| [x5ONf5fsk4Y](https://www.youtube.com/watch?v=x5ONf5fsk4Y) GENTING 已经止跌，等待突破筹码主力线. [CC 中英文字幕 ENG SUB]. 午时筹码峰技术分析.07072023. | Double Swords Investing | GENTING | 2023-07-07 | 1792 | 1 | 1 | 1 | ok |
| [i6gU2KeonmY](https://www.youtube.com/watch?v=i6gU2KeonmY) GENM GENTING MALAYSIA- 今早跌破筹码主力线的紫线.[CC 中英文字幕 ENG SUB].YT会员问股福利.午时筹码主力线技术分析.30062023. | Double Swords Investing | UNKNOWN | 2023-06-30 | 3039 | 9 | 9 | 9 | ok |
| [Axnmq70pTXo](https://www.youtube.com/watch?v=Axnmq70pTXo) GENTING- 股价只有更低，惨![CC 中英文字幕 ENG SUB]. 盘后筹码峰技术分析.23062023. | Double Swords Investing | GENTING | 2023-06-23 | 3083 | 5 | 5 | 5 | ok |
| [inCYOCw2U_U](https://www.youtube.com/watch?v=inCYOCw2U_U) EVENING 5: Genting Malaysia’s Miami land sale falls through | The Edge TV | UNKNOWN | 2023-06-22 | 11620 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [ZoztbB458po](https://www.youtube.com/watch?v=ZoztbB458po) 【财经最热NOW】6月22日｜云顶大马 迈阿密57亿售地计划破灭 | 南洋商报eNanyang | UNKNOWN | 2023-06-22 | 6002 | 2 | 2 | 2 | ok |
| [JkDwUunwQjM](https://www.youtube.com/watch?v=JkDwUunwQjM) GENM GENTING MALAYSIA 图表太难看了. [CC 中英文字幕 ENG SUB].YT会员问股福利. 午时筹码峰技术分析.22062023. | Double Swords Investing | UNKNOWN | 2023-06-22 | 2489 | 3 | 3 | 3 | ok |
| [1Bt_HE0HrOQ](https://www.youtube.com/watch?v=1Bt_HE0HrOQ) GENTING 云顶 - 強势突破底部筹码峰和所有主力线. 是机会吗？[中英文字幕 ENG SUB]. 盘后筹码峰主力线技术分析.17062023. | Double Swords Investing | GENTING | 2023-06-17 | 3355 | 9 | 9 | 9 | ok |
| [nOLUBhsJw1E](https://www.youtube.com/watch?v=nOLUBhsJw1E) GENTING GENM 云顶双雄 出现了RSI 底背离的迹象,要反转而上了吗？[CC 中英文字幕 ENG SUB] 盘后筹码峰技术分析.10062023. | Double Swords Investing | UNKNOWN | 2023-06-10 | 4316 | 5 | 5 | 5 | ok |
| [bUnjSt8cBa4](https://www.youtube.com/watch?v=bUnjSt8cBa4) 【热股追踪】云顶双雄 GENM 和 GENTING 还没有 6 州选已大跌 ! 几时才可捞便宜票 ？20230608@mytraderview | MYtraderview 大马股市技术分析交易 + 生活日志 | UNKNOWN | 2023-06-08 | 1058 | 5 | 5 | 5 | ok |
| [iumwY-73TsY](https://www.youtube.com/watch?v=iumwY-73TsY) Investment Analysis Series - GENM (KLSE: 4715) | Harlem Tan | GENM | 2023-06-06 | 29 | 0 | 0 | 0 | ok |
| [n5h_ZEs5rMA](https://www.youtube.com/watch?v=n5h_ZEs5rMA) Investment Analysis Series - GENTING (KLSE: 3182) | Harlem Tan | GENTING | 2023-06-05 | 19 | 0 | 0 | 0 | ok |
| [G5j0Bwscv9c](https://www.youtube.com/watch?v=G5j0Bwscv9c) GENTING GENM GENTING MALAYSIA 云顶双雄 一周回顾. 六州选举影响大.[CC 中英文字幕 ENG SUB].03062023. | Double Swords Investing | UNKNOWN | 2023-06-03 | 3575 | 1 | 1 | 1 | ok |
| [Y8j1K4WXSqc](https://www.youtube.com/watch?v=Y8j1K4WXSqc) 财经Espresso \| 云顶大马差劲 小股东喊董事降薪 | 百格 Pocketimes | GENM | 2023-05-31 | 9337 | 6 | 6 | 6 | ok |
| [bi-scgh1ANI](https://www.youtube.com/watch?v=bi-scgh1ANI) 26-5-2023 浅谈 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2023-05-27 | 246 | 0 | 0 | 0 | ok |
| [efKLXxhdAwo](https://www.youtube.com/watch?v=efKLXxhdAwo) GENTING GENM 云顶双雄 一周回顾 QR公布后，股价继续低迷. 看看支撑线在那里?有没有机会趁低买入?盘后筹码主力线技术分析.27052023. | Double Swords Investing | UNKNOWN | 2023-05-27 | 3840 | 1 | 1 | 1 | ok |
| [VKAhEB83E3w](https://www.youtube.com/watch?v=VKAhEB83E3w) GENTING GENM 云顶双雄 一周回顾.盘后筹码峰技术分析.21052023. | Double Swords Investing | UNKNOWN | 2023-05-21 | 6803 | 3 | 3 | 3 | ok |
| [sAGn9gfBp14](https://www.youtube.com/watch?v=sAGn9gfBp14) 财经Espresso｜云顶大马选董事 重量级股东反对 | 百格 Pocketimes | UNKNOWN | 2023-05-18 | 16308 | 4 | 4 | 4 | ok |
| [bQ6nhcoLdfE](https://www.youtube.com/watch?v=bQ6nhcoLdfE) 15-5-2023 盘中浅谈 #GENM 4715 \| 马股【电话版】 | 股市先锋队 | GENM | 2023-05-15 | 141 | 0 | 0 | 0 | ok |
| [5k5-QKYgj84](https://www.youtube.com/watch?v=5k5-QKYgj84) 2-5-2023 浅谈 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2023-05-02 | 225 | 0 | 0 | 0 | ok |
| [ULzRApic9-s](https://www.youtube.com/watch?v=ULzRApic9-s) GENM直接获利RM0.91！PAVREIT爆发了！科技股新兴玩家？ | 大老板投资记录本 | UNKNOWN | 2023-04-28 | 8384 | 32 | 32 | 32 | ok |
| [6T1RTQ20pYw](https://www.youtube.com/watch?v=6T1RTQ20pYw) EVENING 5: Genting Malaysia expects RM4.29b from Miami deal | The Edge TV | UNKNOWN | 2023-04-27 | 9669 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [S4IaLrf-jh0](https://www.youtube.com/watch?v=S4IaLrf-jh0) 【财经最热NOW】4月27日\|云顶大马脱售迈阿密资产 不打算派息？ | 南洋商报eNanyang | UNKNOWN | 2023-04-27 | 3685 | 2 | 2 | 2 | ok |
| [FZHcLpe0vGg](https://www.youtube.com/watch?v=FZHcLpe0vGg) GENM GENTING MALAYSIA 站上MA200后,再形成底底高头头高的上升趋势型态.午时筹码峰技术分析.27042023. | Double Swords Investing | UNKNOWN | 2023-04-27 | 4558 | 1 | 1 | 1 | ok |
| [qEYT3hQhMT4](https://www.youtube.com/watch?v=qEYT3hQhMT4) StubWorld: Genting Berhad Is Cheap | Smartkarma | GENTING | 2023-04-18 | 61 | 0 | 0 | 0 | ok |
| [UciTcvgjlzw](https://www.youtube.com/watch?v=UciTcvgjlzw) 财经Espresso｜云顶高原人流 受土崩大雨拖累？ | 百格 Pocketimes | UNKNOWN | 2023-04-13 | 14147 | 1 | 1 | 1 | ok |
| [GGZ8j04bZVA](https://www.youtube.com/watch?v=GGZ8j04bZVA) 财经Espresso｜云顶4公司发威 林国泰去年薪资破2亿 | 百格 Pocketimes | GENTING | 2023-04-07 | 8675 | 1 | 1 | 1 | ok |
| [ghP7tDnBxCQ](https://www.youtube.com/watch?v=ghP7tDnBxCQ) 【财经最热NOW】4月7日｜云顶去年续亏钱 林国泰薪酬却破2亿！ | 南洋商报eNanyang | UNKNOWN | 2023-04-07 | 2265 | 4 | 4 | 4 | ok |
| [KwH7A2O5jIs](https://www.youtube.com/watch?v=KwH7A2O5jIs) 【2023】云顶旗下三家公司，哪一家最值得投资？\| 十年趋势财报分析 | 大马股市分析 | UNKNOWN | 2023-04-01 | 2520 | 1 | 1 | 1 | ok |
| [nHvlagUKUZ4](https://www.youtube.com/watch?v=nHvlagUKUZ4) GENTING MALAYSIA ：大马首屈一指的度假村集团，值得投资吗？\| 十年趋势财报分析 | 大马股市分析 | UNKNOWN | 2023-03-30 | 1546 | 1 | 1 | 1 | ok |
| [OYYV61dYOWQ](https://www.youtube.com/watch?v=OYYV61dYOWQ) GENTING BERHAD：大马最多元化的企业之一，值得投资吗？\| 十年趋势财报分析 | 大马股市分析 | GENTING | 2023-03-29 | 964 | 0 | 0 | 0 | ok |
| [eW_e4_ne3Gc](https://www.youtube.com/watch?v=eW_e4_ne3Gc) 财经Espresso｜传售迈阿密产业 云顶瞄准下一张赌牌？ | 百格 Pocketimes | GENM | 2023-03-27 | 9362 | 2 | 2 | 2 | ok |
| [9dQhgkXDp40](https://www.youtube.com/watch?v=9dQhgkXDp40) GENM GENTING MALAYSIA 突破POC止跌回升，但是。。。。盘后筹码峰技术分析.19032023. | Double Swords Investing | UNKNOWN | 2023-03-19 | 2663 | 2 | 2 | 2 | ok |
| [jdv1xEXMZgE](https://www.youtube.com/watch?v=jdv1xEXMZgE) GENM GENTING 股价低迷. 支撑阻力线在那里?也聊聊六州选举对股价的影响.盘后筹码峰技术分析.11032023. | Double Swords Investing | UNKNOWN | 2023-03-11 | 3009 | 2 | 2 | 2 | ok |
| [pTN46Rvr4S4](https://www.youtube.com/watch?v=pTN46Rvr4S4) 3-3-2023 浅谈 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2023-03-04 | 168 | 0 | 0 | 0 | ok |
| [pT58gNa8Tss](https://www.youtube.com/watch?v=pT58gNa8Tss) GENM GENTING MALAYSIA 继续等待买入讯号. YT会员问股福利.盘后筹码峰技术分析.03022023. | Double Swords Investing | UNKNOWN | 2023-03-03 | 2796 | 1 | 1 | 1 | ok |
| [72HBsYcTunw](https://www.youtube.com/watch?v=72HBsYcTunw) 谈双云顶FY2022Q4业绩 \| 为何仍然亏损？细比2022vs2021表现 【剪去更多空气+调高音量版】 | TCYap马股投资 | UNKNOWN | 2023-02-28 | 1482 | 1 | 1 | 1 | ok |
| [GrNAZS1sw5g](https://www.youtube.com/watch?v=GrNAZS1sw5g) GENTING 底部筹码峰雄厚!YT会员问股福利.盘后技术分析.27022023. | Double Swords Investing | GENTING | 2023-02-27 | 2568 | 2 | 2 | 2 | ok |
| [K5kpzYi7F0A](https://www.youtube.com/watch?v=K5kpzYi7F0A) 谈双云顶2022末季业绩 \| 做么还是亏损？ 【剪去空气版】 | TCYap马股投资 | UNKNOWN | 2023-02-26 | 5113 | 12 | 12 | 12 | ok |
| [-1CqpUicLVQ](https://www.youtube.com/watch?v=-1CqpUicLVQ) GENM GENTING MALAYSIA 没有新赌博税!利空出尽，股价会反弹吗？看看筹码峰技术分析怎么说!25022023. | Double Swords Investing | UNKNOWN | 2023-02-25 | 5924 | 0 | 0 | 0 | ok |
| [VA26_yTW7fE](https://www.youtube.com/watch?v=VA26_yTW7fE) Daily KLSE BURSA Update - 24-2-2023 💥GENTING GENM 4Q LOSES💥ARMADA 4Q PROFIT UP 79%💥 CHINHIN DUFU | Trading with KS | UNKNOWN | 2023-02-24 | 957 | 0 | 0 | 0 | ok |
| [PqS47cIou-k](https://www.youtube.com/watch?v=PqS47cIou-k) 【热股追踪】  GENTING 近期大跌谜底终于解开！下个支撑将在哪里？20230223（中英文CC字幕） | MYtraderview 大马股市技术分析交易 + 生活日志 | GENTING | 2023-02-23 | 1103 | 1 | 1 | 1 | ok |
| [xiRbqW9rBAU](https://www.youtube.com/watch?v=xiRbqW9rBAU) GENM GENTING MALAYSIA Q4大亏393M!技术分析怎么看? 盘后筹码峰技术分析.23022023. | Double Swords Investing | UNKNOWN | 2023-02-23 | 5528 | 2 | 2 | 2 | ok |
| [6SVMdeKYva4](https://www.youtube.com/watch?v=6SVMdeKYva4) GENTING 命运会在这兩天揭晓!筹码峰也分析不到!盘后技术分析.22022023. | Double Swords Investing | GENTING | 2023-02-22 | 2601 | 0 | 0 | 0 | ok |
| [Iie6BjH1GGw](https://www.youtube.com/watch?v=Iie6BjH1GGw) GENM GENTING MALAYSIA 跌破MA200再跌破筹码POC.难道QR/财政预算案有负面消息?盘后技术分析.20022023. | Double Swords Investing | UNKNOWN | 2023-02-20 | 3546 | 1 | 1 | 1 | ok |
| [0jXiO6jxZFM](https://www.youtube.com/watch?v=0jXiO6jxZFM) 【热股追踪】GENTING 周五突然大跌！发生了什么事？ 20230218（中英文CC字幕） | MYtraderview 大马股市技术分析交易 + 生活日志 | GENTING | 2023-02-18 | 2370 | 0 | 0 | 0 | ok |
| [rb23LRDSasQ](https://www.youtube.com/watch?v=rb23LRDSasQ) GENTING 云顶 MOMEMTUM 已经慢下來. 那么要如何技术操作?盘后筹码主力线技术分析.14022023. | Double Swords Investing | GENTING | 2023-02-14 | 1800 | 0 | 0 | 0 | ok |
| [f5-s71_oJ94](https://www.youtube.com/watch?v=f5-s71_oJ94) GENTING 区间盘整等方向.[中英文字幕ENG SUB][CC].盘后筹码主力线技术分析.06022023. | Double Swords Investing | GENTING | 2023-02-06 | 1866 | 0 | 0 | 0 | ok |
| [k0sjJogTf_M](https://www.youtube.com/watch?v=k0sjJogTf_M) GENM GENTING MALAYSIA 止跌回升了吗？[中英文字幕ENG SUB][CC].YT会员问股福利.盘后筹码峰技术分析.03022023. | Double Swords Investing | UNKNOWN | 2023-02-03 | 3099 | 1 | 1 | 1 | ok |
| [YLx31FXEM7k](https://www.youtube.com/watch?v=YLx31FXEM7k) GENM GENTING MALAYSIA 如果跌破这条线是卖出讯号. [中英文字幕ENG SUB][CC].YT会员问股福利.盘后技术分析.31012023. | Double Swords Investing | UNKNOWN | 2023-01-31 | 3642 | 0 | 0 | 0 | ok |
| [d6bsMSu1hlw](https://www.youtube.com/watch?v=d6bsMSu1hlw) GENM GENTING MALAYSIA 股价刚好碰到阻力线, 没有突破.[中英文字幕ENG SUB][CC].YT会员问股福利.盘后筹码主力线技术分析.28012023. | Double Swords Investing | UNKNOWN | 2023-01-28 | 3030 | 4 | 4 | 4 | ok |
| [eia3qw3jcgI](https://www.youtube.com/watch?v=eia3qw3jcgI) GENM GENTING MALAYSIA 套牢盘正挡路. [中英文字幕ENG SUB][CC].YT会员问股福利.盘后技术分析.26012023. | Double Swords Investing | UNKNOWN | 2023-01-26 | 2701 | 2 | 2 | 2 | ok |
| [uZynj4DQpwM](https://www.youtube.com/watch?v=uZynj4DQpwM) Kajian Saham Genting Bhd (FBMKLCI) 25 Januari 2023 | Kelas Saham Percuma | GENTING | 2023-01-25 | 36 | 0 | 0 | 0 | ok |
| [-es5eyGDxSE](https://www.youtube.com/watch?v=-es5eyGDxSE) GENTING 今早突破5.00,短期目标价是多少钱?[中英文字幕ENG SUB][CC].早盘观股筹码峰技术分析.25012023. | Double Swords Investing | GENTING | 2023-01-25 | 2116 | 0 | 0 | 0 | ok |
| [iKGvsnH9eOo](https://www.youtube.com/watch?v=iKGvsnH9eOo) GENM GENTING MALAYSIA 站上MA200是买入讯号.[中英文字幕ENG SUB][CC].YT会员问股福利.午时技术分析.19012023. | Double Swords Investing | UNKNOWN | 2023-01-19 | 3329 | 2 | 2 | 2 | ok |
| [gkUhnAlnrHA](https://www.youtube.com/watch?v=gkUhnAlnrHA) GENTING 继续上升，下一个阻力线在那里?盘后筹码主力线技术分析.12012023. | Double Swords Investing | GENTING | 2023-01-12 | 1694 | 0 | 0 | 0 | ok |
| [84ljhk3w3mQ](https://www.youtube.com/watch?v=84ljhk3w3mQ) GENM GENTING MALAYSIA 站稳MA200了吗？盘前筹码峰技术分析.12012022. | Double Swords Investing | UNKNOWN | 2023-01-11 | 2139 | 0 | 0 | 0 | ok |
| [sb7ICFCFTfY](https://www.youtube.com/watch?v=sb7ICFCFTfY) GENM 用筹码峰分析为什么上升速度比GENTING 慢?盘前技术分析.11012023. | Double Swords Investing | GENM | 2023-01-10 | 2479 | 3 | 3 | 3 | ok |
| [JkUWEb18DUE](https://www.youtube.com/watch?v=JkUWEb18DUE) GENTING 底部筹码雄厚，顶部套牢盘稀少.盘前技术分析.11012023. | Double Swords Investing | GENTING | 2023-01-10 | 2443 | 1 | 1 | 1 | ok |
| [0s97ka5ECvM](https://www.youtube.com/watch?v=0s97ka5ECvM) GENM GENTING MALAYSIA 如果能够突破这条线是买入讯号. 中英文字幕ENG SUB][CC].YT会员问股福利.盘后筹码峰技术分析.07012023. | Double Swords Investing | UNKNOWN | 2023-01-07 | 2899 | 1 | 1 | 1 | ok |
| [4G4HltzNwag](https://www.youtube.com/watch?v=4G4HltzNwag) GENM GENTING MALAYSIA 如果能够突破站稳在MA200是买入讯号.[中英文字幕][CC].YT会员问股福利.盘后技术分析.03012023. | Double Swords Investing | UNKNOWN | 2023-01-03 | 2561 | 1 | 1 | 1 | ok |
| [I51YCoWEG50](https://www.youtube.com/watch?v=I51YCoWEG50) GENM GENTING MALAYSIA 如果能够突破站稳在这条线上，是买入信号. [中英文字幕ENG SUB][CC].YT会员问股福利.早盘筹码峰技术分析.30122022. | Double Swords Investing | UNKNOWN | 2022-12-30 | 3235 | 3 | 3 | 3 | ok |
| [1usQRjiBwgk](https://www.youtube.com/watch?v=1usQRjiBwgk) Daily KLSE BURSA Update - 20-12-2022 💥GAMING SECTORS CAN REBOUND?💥HEALTHCARE SECTOR CAN REBOUND? 💥 | Trading with KS | GENM | 2022-12-20 | 794 | 4 | 4 | 4 | ok |
| [j8bQJ8Ch2JA](https://www.youtube.com/watch?v=j8bQJ8Ch2JA) Daily KLSE BURSA Update - 13-12-2022 💥ITMAX IPO DEBUT UP 45% 💥GENM FY23 GETTING BETTER? 💥ITMAX | Trading with KS | GENM | 2022-12-13 | 906 | 0 | 0 | 0 | ok |
| [Nt7rGHoG64w](https://www.youtube.com/watch?v=Nt7rGHoG64w) GENM GENTING 云顶双雄 的合理价是多少?介绍简单估值的方法.心中有价，买的开心，睡得安心.[中英文字幕ENG SUB][CC].基本面分析.13122022. | Double Swords Investing | UNKNOWN | 2022-12-13 | 9246 | 2 | 2 | 2 | ok |
| [h33UYORB0Ms](https://www.youtube.com/watch?v=h33UYORB0Ms) 【业绩点评】Genm 4715 再次转亏为盈，明年有望突破低迷状态？ | VYCONCHONG理财点滴 | GENM | 2022-12-09 | 3470 | 4 | 4 | 4 | ok |
| [wJWypNFuh3U](https://www.youtube.com/watch?v=wJWypNFuh3U) The Return Of Genting Berhad (What You Should Know) | FIRL | UNKNOWN | 2022-12-03 | 4025 | 3 | 3 | 3 | ok |
| [UD55z_AkHJo](https://www.youtube.com/watch?v=UD55z_AkHJo) GENTING 已经站上所有的筹码主力线.现在只差两个条件.盘后技术分析.03122022.【中文字幕】【CC] | Double Swords Investing | GENTING | 2022-12-03 | 2203 | 5 | 5 | 5 | ok |
| [D16tKEq8cxI](https://www.youtube.com/watch?v=D16tKEq8cxI) 云顶和云顶大马转亏为盈了，股价是否要开始上涨了？ | 投资与财务 | UNKNOWN | 2022-11-27 | 7488 | 15 | 15 | 15 | ok |
| [rakk0ftQmqE](https://www.youtube.com/watch?v=rakk0ftQmqE) 【热股追踪】云顶双雄  GENTING 和 GENM  周一被吓到暴跌后大反弹回来， 现在该怎样看 ？20221126 ( 中文 CC 字幕 ） | MYtraderview 大马股市技术分析交易 + 生活日志 | UNKNOWN | 2022-11-26 | 1229 | 0 | 0 | 0 | ok |
| [lBzoDMfJh7o](https://www.youtube.com/watch?v=lBzoDMfJh7o) GENM GENTING MALAYSIA 市场打臉QR. 估计短期会在区间盘整.YT 会员问股福利. 午时技术分析. | Double Swords Investing | UNKNOWN | 2022-11-25 | 2839 | 4 | 4 | 4 | ok |
| [GcEAi7m_SJY](https://www.youtube.com/watch?v=GcEAi7m_SJY) GENM GENTING MALAYSIA ANWAR 安华做首相 PM10,效应之下，股价回到原来的位置.QR没有亏钱，可否继续往上推?吹水马后炮. 盘后技术分析.24112022. | Double Swords Investing | UNKNOWN | 2022-11-24 | 3083 | 3 | 3 | 3 | ok |
| [fTi_25VLc_U](https://www.youtube.com/watch?v=fTi_25VLc_U) 成功转亏为盈！云顶双雄GENM & GENTING FY2022Q3季报分享 （剪去空气版） | TCYap马股投资 | UNKNOWN | 2022-11-24 | 975 | 0 | 0 | 0 | ok |
| [RGlYlK421vE](https://www.youtube.com/watch?v=RGlYlK421vE) 成功转亏为盈！浅谈云顶双雄GENM & GENTING FY2022Q3季报🎰🎢 | TCYap马股投资 | UNKNOWN | 2022-11-24 | 591 | 0 | 0 | 0 | ok |
| [hf-rClHzSU8](https://www.youtube.com/watch?v=hf-rClHzSU8) 23-11-2022 浅谈 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2022-11-23 | 106 | 0 | 0 | 0 | ok |
| [GjfzrBbDQjw](https://www.youtube.com/watch?v=GjfzrBbDQjw) GENM GENTING MALAYSIA 今早股价随着PRU15政局波动. 谁可以成为首相?PAHANG 政府没有回教党有利云顶大马.午时技术分析.21112022. | Double Swords Investing | UNKNOWN | 2022-11-21 | 2986 | 1 | 1 | 1 | ok |
| [_7ggMWMKHIc](https://www.youtube.com/watch?v=_7ggMWMKHIc) GENM GENTING MALAYSIA 如果云顶大马的股价大跌，支撑线会在那里?聊聊如何操作.盘后技术分析.20112022. | Double Swords Investing | UNKNOWN | 2022-11-20 | 4721 | 6 | 6 | 6 | ok |
| [-ILaqWVfesU](https://www.youtube.com/watch?v=-ILaqWVfesU) GENM 4715 ｜疫情都没了，你还不起吗？ | 大老板投资记录本 | GENM | 2022-11-15 | 6866 | 22 | 22 | 22 | ok |
| [I_bsDUAVi5U](https://www.youtube.com/watch?v=I_bsDUAVi5U) GENTING 盘中突破MA200!即时点评!午时技术分析.11112022. | Double Swords Investing | GENTING | 2022-11-11 | 1514 | 0 | 0 | 0 | ok |
| [SAMP57Inka4](https://www.youtube.com/watch?v=SAMP57Inka4) GENM GENTING MALAYSIA 套牢盘是強大的阻力线，除非有这个加持。。。。盘后技术分析. 06112022..[中文字幕][CC] | Double Swords Investing | UNKNOWN | 2022-11-06 | 2643 | 1 | 1 | 1 | ok |
| [4UiMFb5pgQc](https://www.youtube.com/watch?v=4UiMFb5pgQc) 大马股票 \| 云顶集团 3182 \| GENTING 你可能不知道的10件事 | 少爷兵 | GENTING | 2022-11-04 | 18254 | 8 | 8 | 8 | ok |
| [bvcGApziQ9k](https://www.youtube.com/watch?v=bvcGApziQ9k) 【财经最热NOW】11月2日｜开业不到1年 云顶Skyworlds调整票价 | 南洋商报eNanyang | UNKNOWN | 2022-11-02 | 2694 | 0 | 0 | 0 | ok |
| [Ho-b-9ALxu0](https://www.youtube.com/watch?v=Ho-b-9ALxu0) GENM GENTING MALAYSIA 分析员与专家的澳门赌牌报道自相矛盾，只好看看筹码峰分析.盘后技术分析.28102022. | Double Swords Investing | UNKNOWN | 2022-10-28 | 2976 | 1 | 1 | 1 | ok |
| [GlQ9yvgpETM](https://www.youtube.com/watch?v=GlQ9yvgpETM) 21-10-2022 盘中浅谈 #GENTING 3182 \| 马股 | 股市先锋队 | GENTING | 2022-10-21 | 73 | 0 | 0 | 0 | ok |
| [eQjaQqIOrLk](https://www.youtube.com/watch?v=eQjaQqIOrLk) GENM GENTING MALAYSIA 继续等待不用急.盘后技术分析.20102022. | Double Swords Investing | UNKNOWN | 2022-10-20 | 2534 | 1 | 1 | 1 | ok |
| [OxpmRQ-dtzU](https://www.youtube.com/watch?v=OxpmRQ-dtzU) GENM GENTING MALAYSIA 跌跌不休不急捞. 午时技术分析.18102022. | Double Swords Investing | UNKNOWN | 2022-10-18 | 3431 | 0 | 0 | 0 | ok |
| [RgAQHtjXLiA](https://www.youtube.com/watch?v=RgAQHtjXLiA) GENTING 分析员"看好"特效药call buy.但是股价却不给力. 盘后技术分析.17102022. | Double Swords Investing | GENTING | 2022-10-17 | 2889 | 0 | 0 | 0 | ok |
| [bt-9hQKl7rE](https://www.youtube.com/watch?v=bt-9hQKl7rE) 14-10-2022 浅谈 #GENTING 3182 \| 马股【电话版】 | 股市先锋队 | GENTING | 2022-10-15 | 67 | 0 | 0 | 0 | ok |
| [zgpO2dmmrTg](https://www.youtube.com/watch?v=zgpO2dmmrTg) 【热股追踪】GENTING  周五开盘突然开高高，收盘反跌低！你知道为什么会这样吗？20221010 | MYtraderview 大马股市技术分析交易 + 生活日志 | GENTING | 2022-10-10 | 781 | 0 | 0 | 0 | ok |
| [f4CfmYGRi-0](https://www.youtube.com/watch?v=f4CfmYGRi-0) 7-10-2022 浅谈 #GENTING 3182 \| 马股【电话版】 | 股市先锋队 | GENTING | 2022-10-08 | 98 | 1 | 1 | 1 | ok |
| [acSoct_1FVc](https://www.youtube.com/watch?v=acSoct_1FVc) GENM GENTING MALAYSIA 正在筹码峰区内盘整. 聊聊要如何操作. 会员问股福利.盘后技术分析. 08102022. | Double Swords Investing | UNKNOWN | 2022-10-08 | 2327 | 2 | 2 | 2 | ok |
| [spXKKY7ESFg](https://www.youtube.com/watch?v=spXKKY7ESFg) 【热股追踪】GENTING 相隔 21年再竞标澳门赌牌成焦点！技术破底后反弹，要怎样看？20221003 | MYtraderview 大马股市技术分析交易 + 生活日志 | GENTING | 2022-10-03 | 450 | 0 | 0 | 0 | ok |
| [EkstG3_0oGQ](https://www.youtube.com/watch?v=EkstG3_0oGQ) GENM GENTING MALAYSIA 股价在支撑线寻得支撑. 下一步就要看MA200. 会员问股福利.盘后筹码峰技术分析.01102022. | Double Swords Investing | UNKNOWN | 2022-10-01 | 2830 | 3 | 3 | 3 | ok |
| [6k3ggsA7Vyg](https://www.youtube.com/watch?v=6k3ggsA7Vyg) 之前投行分析员看好的GENTING ,跌破前低支撑线.分析员是叫你接票吗？盘后技术分析. 25092022. | Double Swords Investing | UNKNOWN | 2022-09-25 | 3660 | 1 | 1 | 1 | ok |
| [iiLBggZ-QqQ](https://www.youtube.com/watch?v=iiLBggZ-QqQ) GENM GENTING MALAYSIA 跌破MA200 是危险信号.  盘后技术分析. 23092022. | Double Swords Investing | UNKNOWN | 2022-09-23 | 4148 | 1 | 1 | 1 | ok |
| [6kaENqEVE9c](https://www.youtube.com/watch?v=6kaENqEVE9c) 6张赌牌，云顶成老7？云顶进军澳门搅局！【谈股论今 30】【中字】 | 陈剑老师投资教育频道 | UNKNOWN | 2022-09-19 | 36801 | 33 | 33 | 33 | ok |
| [vDNrNypJU7w](https://www.youtube.com/watch?v=vDNrNypJU7w) GENTING GENM 云顶双雄的合理价是多少? 心中有价，交易不会慌. 配合技术分析买在好价钱. 基本面分析. 马股. 06092022. | Double Swords Investing | UNKNOWN | 2022-09-06 | 4522 | 1 | 1 | 1 | ok |
| [kOGjH5JNgOM](https://www.youtube.com/watch?v=kOGjH5JNgOM) GENTING MALAYSIA GENM 云顶双雄. 筹码峰技术图显得弱势. 盘后技术分析. 03092022. | Double Swords Investing | UNKNOWN | 2022-09-03 | 2294 | 2 | 2 | 2 | ok |
| [B_NygGnxZN0](https://www.youtube.com/watch?v=B_NygGnxZN0) GENTING 云顶 股价区间盘整等出方向，继续观察. 会员问股福利. 盘后技术分析. 28082022. | Double Swords Investing | GENTING | 2022-08-28 | 1223 | 0 | 0 | 0 | ok |
| [U_8ZDLA9a30](https://www.youtube.com/watch?v=U_8ZDLA9a30) GENTING MALAYSIA GENM QR比预期差，但是股价+筹码稳住了. 会员问股福利. 盘后技术分析.27082022. | Double Swords Investing | UNKNOWN | 2022-08-27 | 3128 | 1 | 1 | 1 | ok |
| [IfwhetOAzwA](https://www.youtube.com/watch?v=IfwhetOAzwA) 浅谈双云顶UCHITEC CORAZA等9份业绩 \| 6家营业额创新高！ | TCYap马股投资 | UNKNOWN | 2022-08-25 | 2683 | 9 | 9 | 9 | ok |
| [EVJcjXpoqRI](https://www.youtube.com/watch?v=EVJcjXpoqRI) GENTING MALAYSIA GENM 云顶双雄业绩不给力，会对股价有什么影响? 筹码峰分析!盘后技术分析. 25082022. | Double Swords Investing | UNKNOWN | 2022-08-25 | 3109 | 0 | 0 | 0 | ok |
| [-H1EQ1ggvZI](https://www.youtube.com/watch?v=-H1EQ1ggvZI) GENTING MALAYSIA GENM 云顶大马 底部筹码雄厚是强支撑!会员问股福利. 也聊聊下个QR. 午时技术分析. 17082022. | Double Swords Investing | UNKNOWN | 2022-08-17 | 3736 | 2 | 2 | 2 | ok |
| [kQkJN6B6q20](https://www.youtube.com/watch?v=kQkJN6B6q20) GENTING MALAYSIA GENM 今天'突破关键阻力线. 留意可否站稳! 筹码峰分析告诉你未来的走势! 盘后技术分析. 11082022. | Double Swords Investing | UNKNOWN | 2022-08-11 | 2682 | 3 | 3 | 3 | ok |
| [wBq_g0qPcm0](https://www.youtube.com/watch?v=wBq_g0qPcm0) WHICH GENTING COUNTER IS MOST WORTHY TO BE INVESTED? | Malaysia Stock Investment Analysis | GENTING | 2022-07-30 | 619 | 0 | 0 | 0 | ok |
| [70EHi6zIyBs](https://www.youtube.com/watch?v=70EHi6zIyBs) 【热股追踪】传言云顶新加坡被收购，激励子母公司股价急涨！GENTING 是否要回来了？ 20220715 | MYtraderview 大马股市技术分析交易 + 生活日志 | GENTING | 2022-07-15 | 634 | 0 | 0 | 0 | ok |
| [N8xhuJc9-ns](https://www.youtube.com/watch?v=N8xhuJc9-ns) 【行家论股】云顶 美赌城环路引人流 | 南洋商报eNanyang | GENTING | 2022-07-08 | 519 | 0 | 0 | 0 | ok |
| [w9aprhwM9xg](https://www.youtube.com/watch?v=w9aprhwM9xg) 【行家论股】云顶大马 赌客回流复苏在望 | 南洋商报eNanyang | GENM | 2022-07-07 | 612 | 2 | 2 | 2 | ok |
| [XaV2BYHJhGw](https://www.youtube.com/watch?v=XaV2BYHJhGw) 06072022 #GENTING #GENM 云顶双雄，难兄难弟，都是要看MA200的脸色. 盘后技术分析. | Double Swords Investing | UNKNOWN | 2022-07-06 | 3048 | 2 | 2 | 2 | ok |
| [Z2Na-bKfFd0](https://www.youtube.com/watch?v=Z2Na-bKfFd0) GENTING MALAYSIA: ONE OF THE LEADING RESORTS OPERATOR IN MALAYSIA, IS IT WORTHY TO BE INVESTED? | Malaysia Stock Investment Analysis | UNKNOWN | 2022-07-04 | 245 | 1 | 1 | 1 | ok |
| [GEJo7av1WwQ](https://www.youtube.com/watch?v=GEJo7av1WwQ) GENTING BERHAD: ONE OF THE MOST DIVERSIFIED COMPANIES IN MALAYSIA, IS IT WORTHY TO BE INVESTED? | Malaysia Stock Investment Analysis | GENTING | 2022-07-02 | 666 | 0 | 0 | 0 | ok |
| [3Km3JGjk21k](https://www.youtube.com/watch?v=3Km3JGjk21k) 26062022 #GENTING 区间盘整等出方向!MA200是关键. 盘后技术分析. | Double Swords Investing | GENTING | 2022-06-26 | 1582 | 0 | 0 | 0 | ok |
| [w2yHDErox6s](https://www.youtube.com/watch?v=w2yHDErox6s) 19062022 #GENM 跌破MA200后，持续往南下，不要随便去接刀! 等待这个确认讯号出现后再考虑要不要介入. 盘后技术分析. | Double Swords Investing | GENM | 2022-06-19 | 2273 | 0 | 0 | 0 | ok |
| [T5LjqkUzJgI](https://www.youtube.com/watch?v=T5LjqkUzJgI) 17-6-2022 浅谈 #GENTING 3182 \| 马股 | 股市先锋队 | GENTING | 2022-06-19 | 85 | 0 | 0 | 0 | ok |
| [e0qf3QYrgUk](https://www.youtube.com/watch?v=e0qf3QYrgUk) 14062022 ＃GENTING 热情过后，股价回到MA200,可以守住吗？底部筹码雄厚是强支撑. 午时技术分析. | Double Swords Investing | GENTING | 2022-06-14 | 1829 | 1 | 1 | 1 | ok |
| [hqfoGLwhHDg](https://www.youtube.com/watch?v=hqfoGLwhHDg) 【热股追踪】GENTING 攻打关键阻力惊闻老板卖票 ！多军士气涣散 溃败而逃 20220611 | MYtraderview 大马股市技术分析交易 + 生活日志 | GENTING | 2022-06-11 | 635 | 2 | 2 | 2 | ok |
| [uuprUPZafwU](https://www.youtube.com/watch?v=uuprUPZafwU) 10062022 #GENTING 今天大跌近7％，跌破MA20. 底部筹码雄厚，估计MA200可以守住. 盘后技术分析. | Double Swords Investing | GENTING | 2022-06-10 | 2681 | 3 | 3 | 3 | ok |
| [lNmbMBxfjPo](https://www.youtube.com/watch?v=lNmbMBxfjPo) 8-6-2022 浅谈 #GENTING 3182 \| 马股 | 股市先锋队 | GENTING | 2022-06-08 | 148 | 0 | 0 | 0 | ok |
| [51p6kWgxfqk](https://www.youtube.com/watch?v=51p6kWgxfqk) 04062022 ＃GENTING  1hr, 短线分析之前追高的投机者的买入价是多少? 止损价又是多少? 阻力线又是多少? 盘后技术分析. | Double Swords Investing | GENTING | 2022-06-04 | 1839 | 0 | 0 | 0 | ok |
| [J23Cn_63_8w](https://www.youtube.com/watch?v=J23Cn_63_8w) 财经Espresso ｜ 新金鹅有望下蛋？云顶价量齐升 | 百格 Pocketimes | UNKNOWN | 2022-06-01 | 9060 | 5 | 5 | 5 | ok |
| [RxBXYTjSqF0](https://www.youtube.com/watch?v=RxBXYTjSqF0) 1-6-2022 浅谈 #GENTING 3182 \| 马股 | 股市先锋队 | GENTING | 2022-06-01 | 171 | 0 | 0 | 0 | ok |
| [QnTVm0q5T48](https://www.youtube.com/watch?v=QnTVm0q5T48) 【热股追踪】GENTING 今天开盘就一飞冲天，要起始终都要起的！！20220601 | MYtraderview 大马股市技术分析交易 + 生活日志 | GENTING | 2022-06-01 | 467 | 0 | 0 | 0 | ok |
| [JrTthsAxaPw](https://www.youtube.com/watch?v=JrTthsAxaPw) Daily KLSE BURSA Update - 1-6-2022 💥GENTING BIG SPIKE 10%💥DATASONIC BACK TO PROFIT!💥 ARMADA PETRONM | Trading with KS | GENTING | 2022-06-01 | 1158 | 8 | 8 | 8 | ok |
| [99Yy7c_p6Bw](https://www.youtube.com/watch?v=99Yy7c_p6Bw) KS看股- 马股 KLSE BURSA 分享 - 1-6-2022 💥云顶大涨 10% !💥DATASONIC 转亏为盈!💥ARMADA PETRONM HENGYUAN GENTING SAPNRG | Trading with KS | GENTING | 2022-06-01 | 3063 | 10 | 10 | 10 | ok |
| [5uHdaD_DteE](https://www.youtube.com/watch?v=5uHdaD_DteE) 27-5-2022 浅谈 #GENM 4715 \| 马股【电话版】 | 股市先锋队 | GENM | 2022-05-27 | 140 | 0 | 0 | 0 | ok |
| [1-K5G7lZIDY](https://www.youtube.com/watch?v=1-K5G7lZIDY) 【行家论股】云顶大马 次季业绩料续改善 | 南洋商报eNanyang | GENM | 2022-05-27 | 569 | 0 | 0 | 0 | ok |
| [zSwzq6xGHvE](https://www.youtube.com/watch?v=zSwzq6xGHvE) 财经Espresso｜开山了 云顶双雄照亏不误 | 百格 Pocketimes | GENM | 2022-05-26 | 14202 | 8 | 8 | 8 | ok |
| [AfjRN-sPmsc](https://www.youtube.com/watch?v=AfjRN-sPmsc) 20-5-2022 浅谈 #GENTING 3182 \| 马股 | 股市先锋队 | GENTING | 2022-05-22 | 59 | 0 | 0 | 0 | ok |
| [0XRBrN1CUPo](https://www.youtube.com/watch?v=0XRBrN1CUPo) Why Genting is on an uptrend movement ? Top 3 Reasons to Monitor using Volume Spread Analysis | Footprints of Smart Money | GENTING | 2022-05-19 | 430 | 0 | 0 | 0 | ok |
| [4D-egLpCg4E](https://www.youtube.com/watch?v=4D-egLpCg4E) 19052022 #GENTING 帶量突破 MA200+前高+筹码峰. 底部筹码雄厚是強支撑.  暴量会不会是主力出货? 下个阻力线在那里? 教你如何去判断. 午时技术分析. | Double Swords Investing | GENTING | 2022-05-19 | 2534 | 1 | 1 | 1 | ok |
| [qSxHO1XxBDI](https://www.youtube.com/watch?v=qSxHO1XxBDI) Daily KLSE BURSA Update - 18-5-2022 💥GENTING DREAM SHIP 💥SERBADK FACING WINDING-UP PETITIONS💥 | Trading with KS | GENTING | 2022-05-18 | 1265 | 5 | 5 | 5 | ok |
| [C1lTQHiZfy8](https://www.youtube.com/watch?v=C1lTQHiZfy8) 12052022 #GENM 跌破3.00后，再破箱子. 下一个关键支撑是MA200. 盘后技术分析. | Double Swords Investing | GENM | 2022-05-12 | 1819 | 1 | 1 | 1 | ok |
| [xes4_V2dnLM](https://www.youtube.com/watch?v=xes4_V2dnLM) 09052022 #GENTING 没有能力站回MA200,但是底部筹码雄厚有支撑,估计可以守住. 午时技术分析. | Double Swords Investing | GENTING | 2022-05-09 | 1105 | 0 | 0 | 0 | ok |
| [TgSR2HTlZOM](https://www.youtube.com/watch?v=TgSR2HTlZOM) 云顶大马重回大家的视线?! 下一个超级复苏股?! 【乐学成长空间】 | 乐学成长空间 - LXInvest | UNKNOWN | 2022-05-07 | 11698 | 20 | 20 | 20 | ok |
| [gc1byvvwDts](https://www.youtube.com/watch?v=gc1byvvwDts) EVENING 5: Omicron to weigh on Genting Malaysia — Maybank IB | The Edge TV | UNKNOWN | 2022-05-06 | 11081 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [bvTFK-k74Ac](https://www.youtube.com/watch?v=bvTFK-k74Ac) 06052022 #GENTING 今早跌破MA200, 底部有強大筹码峰支撑住. 继续等待下一个买入信号. 午时技术分析. | Double Swords Investing | GENTING | 2022-05-06 | 1667 | 4 | 4 | 4 | ok |
| [rP4gNcigfcY](https://www.youtube.com/watch?v=rP4gNcigfcY) 云顶人山人海，股价也来突破？Ep 550 \| BURSA MARKET 第五百五十集Market 开箱 | EL StockTrooper | UNKNOWN | 2022-05-05 | 634 | 0 | 0 | 0 | ok |
| [bWmOywehnpQ](https://www.youtube.com/watch?v=bWmOywehnpQ) 5-5-2022 浅谈 #GENTING 3182 \| 马股 | 股市先锋队 | GENTING | 2022-05-05 | 60 | 0 | 0 | 0 | ok |
| [BeW-rM0q9hU](https://www.youtube.com/watch?v=BeW-rM0q9hU) 05052022 #GENTING 今早终于站上MA200. 那么是确认买入信号吗？要留意收盘价可否持续站稳在MA200之上，或突破前高阻力? 早上实时观股技术分析. | Double Swords Investing | GENTING | 2022-05-05 | 1918 | 2 | 2 | 2 | ok |
| [x7tVlaeGdlk](https://www.youtube.com/watch?v=x7tVlaeGdlk) 【热股追踪】旅游业迎来强劲复苏，云顶双雄渐入佳境 ？！20220503 | MYtraderview 大马股市技术分析交易 + 生活日志 | UNKNOWN | 2022-05-03 | 531 | 0 | 0 | 0 | ok |
| [R5Kd1fAEjFs](https://www.youtube.com/watch?v=R5Kd1fAEjFs) 03052022 #GENTING 突破筹码峰，准备再次挑战MA200. 这次会不会成功呢? 盘后技术分析. | Double Swords Investing | GENTING | 2022-05-03 | 2716 | 0 | 0 | 0 | ok |
| [zCB2XNWzt60](https://www.youtube.com/watch?v=zCB2XNWzt60) 01052022 #GENM 终于成功突破3.00， 准备挑战52周新高. 盘后技术分析. | Double Swords Investing | GENM | 2022-05-01 | 2185 | 0 | 0 | 0 | ok |
| [zw_96JqON-c](https://www.youtube.com/watch?v=zw_96JqON-c) 29042022 #GENM 今早突破箱子站上3.00. 留意可否维持到收盘. 聊聊交易策略. 午时技术分析. | Double Swords Investing | GENM | 2022-04-29 | 2162 | 3 | 3 | 3 | ok |
| [t8lUQu58hMc](https://www.youtube.com/watch?v=t8lUQu58hMc) 24042022 #GENTING 底部筹码雄厚有支撑.  继续等待突破MA200. 盘后技术分析. | Double Swords Investing | GENTING | 2022-04-24 | 795 | 0 | 0 | 0 | ok |
| [E8sQxgWPFt8](https://www.youtube.com/watch?v=E8sQxgWPFt8) 22042022 #GENM 区间盘整，继续旁边看戏. 盘后技术分析. | Double Swords Investing | GENM | 2022-04-22 | 1374 | 0 | 0 | 0 | ok |
| [GtQ7WUCU8O8](https://www.youtube.com/watch?v=GtQ7WUCU8O8) 17042022 GENTING 继续在MA200之下徘徊. 盘后技术分析. | Double Swords Investing | GENTING | 2022-04-17 | 899 | 3 | 3 | 3 | ok |
| [DPx1QLm_YuM](https://www.youtube.com/watch?v=DPx1QLm_YuM) EVENING 5: Genting M’sia tipped to win full casino licence in New York | The Edge TV | UNKNOWN | 2022-04-13 | 6711 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [CuHeYpmIxDM](https://www.youtube.com/watch?v=CuHeYpmIxDM) 09042022 #GENM 要继续等待突破3.00心理阻力价位. MA20是支撑线. 盘后技术分析. | Double Swords Investing | GENM | 2022-04-09 | 1100 | 0 | 0 | 0 | ok |
| [Da4ryrU7mls](https://www.youtube.com/watch?v=Da4ryrU7mls) 09042022 #GENTING 要继续等待，看看有没有机会突破MA200. 盘后技术分析. | Double Swords Investing | GENTING | 2022-04-09 | 620 | 0 | 0 | 0 | ok |
| [zRqjbK_NxSM](https://www.youtube.com/watch?v=zRqjbK_NxSM) 一次过看清云顶集团Genting和大马云顶Genting Malaysia \| 个别业务、股权&估值 | TCYap马股投资 | UNKNOWN | 2022-04-08 | 13362 | 10 | 10 | 10 | ok |
| [2OY9K7e63pM](https://www.youtube.com/watch?v=2OY9K7e63pM) 云顶 Genting Malaysia \|  疫情复苏股的首选股？\| 马来西亚蓝筹股的翻身仗？\|  数据证明才是最重要的！【马股投资】 | 大老板投资记录本 | UNKNOWN | 2022-04-08 | 13116 | 10 | 10 | 10 | ok |
| [4xM9qDubrEY](https://www.youtube.com/watch?v=4xM9qDubrEY) 04042022 #GENTING MA200近在眼前，就是没有能力突破! 盘后技术分析. | Double Swords Investing | GENTING | 2022-04-04 | 1714 | 1 | 1 | 1 | ok |
| [3r3DT7Ym_DE](https://www.youtube.com/watch?v=3r3DT7Ym_DE) 02042022 #GENTING MA200是强大阻力线. 量价背离，欲冲无力. 看看下个支撑线阻力线在那里? 盘后技术分析. | Double Swords Investing | GENTING | 2022-04-02 | 918 | 0 | 0 | 0 | ok |
| [JDXyTD8o6Bw](https://www.youtube.com/watch?v=JDXyTD8o6Bw) 31032022 #GENM 3.00是关键阻力线. 也聊聊马新开放边界对GENM的看法. 新加坡人会不会來大马报复性消费? 实时观股技术分析. | Double Swords Investing | GENM | 2022-03-31 | 1722 | 3 | 3 | 3 | ok |
| [qUg2j__Q5-Q](https://www.youtube.com/watch?v=qUg2j__Q5-Q) 29032022 #GENTING 无力突破MA200. #GENM 回归筹码峰. 盘后技术分析. | Double Swords Investing | UNKNOWN | 2022-03-29 | 2085 | 5 | 5 | 5 | ok |
| [RGMXYYSDCBQ](https://www.youtube.com/watch?v=RGMXYYSDCBQ) 25032022 #GENM GENTING MA200 是分水岭. 实时观股技术分析. | Double Swords Investing | UNKNOWN | 2022-03-25 | 1902 | 4 | 4 | 4 | ok |
| [2OTD48tA1xo](https://www.youtube.com/watch?v=2OTD48tA1xo) GENTING MALAYSIA #genm #4715 今天turbo, 很像要rocket了。可以买了没有？CAN BUY ORNOT. | Trade Kao Kao | UNKNOWN | 2022-03-24 | 132 | 0 | 0 | 0 | ok |
| [V5WZhNG8Axo](https://www.youtube.com/watch?v=V5WZhNG8Axo) 23032022 #GENTING #GENM  如何分辨筹码峰是"支撑筹码"? "套利筹码"? 盘后技术分析. | Double Swords Investing | UNKNOWN | 2022-03-23 | 2290 | 3 | 3 | 3 | ok |
| [GPlmBFPG1m0](https://www.youtube.com/watch?v=GPlmBFPG1m0) 21032022 #GENTING #GENM 云顶双雄的盘后技术分析. 正处于弱势. | Double Swords Investing | UNKNOWN | 2022-03-21 | 1514 | 0 | 0 | 0 | ok |
| [7DaX_Qcuits](https://www.youtube.com/watch?v=7DaX_Qcuits) 15-3-2022 盘中浅谈 #GENTING 3182 \| 马股 | 股市先锋队 | GENTING | 2022-03-15 | 85 | 0 | 0 | 0 | ok |
| [diH21ZRUKRY](https://www.youtube.com/watch?v=diH21ZRUKRY) 10032022 #GENTING #GENM 云顶双雄，一强一弱. 盘后技术分析. | Double Swords Investing | UNKNOWN | 2022-03-10 | 2696 | 2 | 2 | 2 | ok |
| [WggFobv72l0](https://www.youtube.com/watch?v=WggFobv72l0) 02032022 #GENM 股价回测颈线，雄厚筹码峰支撑住. 实时观股技术分析. | Double Swords Investing | GENM | 2022-03-02 | 1589 | 5 | 5 | 5 | ok |
| [vLU9xpahdL8](https://www.youtube.com/watch?v=vLU9xpahdL8) 24022022 #GENM 最新QR 反亏为盈，营业额接近疫情前. 聊聊我的看法. | Double Swords Investing | GENM | 2022-02-24 | 2017 | 2 | 2 | 2 | ok |
| [eN9-o2R_W74](https://www.youtube.com/watch?v=eN9-o2R_W74) 20022022 GENM 再次跌破MA200,显得乏力. GENTING MA20向上扬，短期上升趋势. 盘后技术分析. | Double Swords Investing | UNKNOWN | 2022-02-20 | 1138 | 0 | 0 | 0 | ok |
| [pu1_L9ExnYE](https://www.youtube.com/watch?v=pu1_L9ExnYE) 16022022 #GENM 破底翻后站上MA200, 要留意可否站稳? 盘后技术分析. | Double Swords Investing | GENM | 2022-02-16 | 1580 | 3 | 3 | 3 | ok |
| [Oe2N5q5RHVM](https://www.youtube.com/watch?v=Oe2N5q5RHVM) GENM-Positive on Tourism; HEVEA-Ride on Bullish Wood \| EP. M26 \| Technical Analysis \| TA_BULLPLAY | Ryan Trader's Hub | GENM | 2022-02-15 | 150 | 0 | 0 | 0 | ok |
| [xViJayfbsW0](https://www.youtube.com/watch?v=xViJayfbsW0) 13022022 #GENM 合理价是多少? 为什么上次突破阻力线后站不稳? 为什么这次突破我会认为可以站稳? 聊聊均线助涨/助跌的原因. 价值投资配合技术分析大道至简. | Double Swords Investing | GENM | 2022-02-13 | 2200 | 1 | 1 | 1 | ok |
| [YchQAdDbT4M](https://www.youtube.com/watch?v=YchQAdDbT4M) Daily KLSE BURSA Update - 8-2-2022 💥GENM SKYWORLD OPEN !!💥AIRSIA AIRPORT PMBTECH UP !! 💥 | Trading with KS | GENM | 2022-02-08 | 1226 | 3 | 3 | 3 | ok |
| [6CV42uWJfpU](https://www.youtube.com/watch?v=6CV42uWJfpU) 08022022 #GENM  下午大涨5%， 可否更上一层楼要看MA200. 实时观股技术分析简评. | Double Swords Investing | GENM | 2022-02-08 | 1315 | 1 | 1 | 1 | ok |
| [RgNXGTo1l08](https://www.youtube.com/watch?v=RgNXGTo1l08) 06022022 #GENM 投行报告说2023财政年可以赚14.7亿，那么今天的合理价是多少? 心中有价，交易不会慌张! 基本面分析估值. | Double Swords Investing | GENM | 2022-02-06 | 2051 | 1 | 1 | 1 | ok |
| [dbInXmejxPE](https://www.youtube.com/watch?v=dbInXmejxPE) Daily KLSE BURSA Update - 4-2-2022 💥 ENERGY STOCKS CONTINUE SPIKE! 💥GENTING SKYWORLD OPENING SOON 💥 | Trading with KS | UNKNOWN | 2022-02-04 | 1289 | 8 | 8 | 8 | ok |
| [VbEOJKC34cc](https://www.youtube.com/watch?v=VbEOJKC34cc) 【行家论股】云顶大马 复苏势头更强劲 | 南洋商报eNanyang | GENM | 2022-02-04 | 694 | 0 | 0 | 0 | ok |
| [tRvso3Pvkgs](https://www.youtube.com/watch?v=tRvso3Pvkgs) 财经Espresso \| 乐园开业日期 云顶大马松口 | 百格 Pocketimes | UNKNOWN | 2022-01-28 | 12139 | 4 | 4 | 4 | ok |
| [OENKDDuiWf4](https://www.youtube.com/watch?v=OENKDDuiWf4) EVENING 5: Genting Skyworlds to open next month | The Edge TV | UNKNOWN | 2022-01-28 | 8788 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [PO9wqqbFnbM](https://www.youtube.com/watch?v=PO9wqqbFnbM) 财经Espresso ｜ 云顶乐园开幕"筹备中"? | 百格 Pocketimes | UNKNOWN | 2022-01-25 | 11890 | 4 | 4 | 4 | ok |
| [JE5wdzwuAV4](https://www.youtube.com/watch?v=JE5wdzwuAV4) 25012022 #GENTING 早上跌破前低支撑线，看看下个支撑会在那里? 午盘技术分析简评. | Double Swords Investing | GENTING | 2022-01-25 | 1149 | 1 | 1 | 1 | ok |
| [7Epg1Lx6b_s](https://www.youtube.com/watch?v=7Epg1Lx6b_s) 浅谈 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2022-01-24 | 64 | 0 | 0 | 0 | ok |
| [dKlHDKAV_XA](https://www.youtube.com/watch?v=dKlHDKAV_XA) 15012022 #GENTING #GENM 一周回顾，盘后个股技术分析简评. | Double Swords Investing | UNKNOWN | 2022-01-15 | 1329 | 1 | 1 | 1 | ok |
| [s9Nyy0m1PFc](https://www.youtube.com/watch?v=s9Nyy0m1PFc) 03012022 #GENTING 再次补缺口.  看看可否维持到收盘? 早上实时观股技术分析简评. | Double Swords Investing | GENTING | 2022-01-03 | 692 | 1 | 1 | 1 | ok |
| [-Qz5vEQol-A](https://www.youtube.com/watch?v=-Qz5vEQol-A) 31122021 #GENTING 出现了类似3只乌鸦型态.  盘后技术分析简评. | Double Swords Investing | GENTING | 2021-12-31 | 1235 | 1 | 1 | 1 | ok |
| [8F5j-QrO_cE](https://www.youtube.com/watch?v=8F5j-QrO_cE) 财经Espresso \| 日本梦碎  云顶清算业务 | 百格 Pocketimes | GENTING | 2021-12-30 | 19375 | 7 | 7 | 7 | ok |
| [08-mBhpfAKo](https://www.youtube.com/watch?v=08-mBhpfAKo) KS看股- 每天 马股 KLSE BURSA 分享 - 30-12-2021 - GENETEC能继续反弹吗? 云顶 可以捞底了吗? GENTING GENM MAGNUM AIRPORT | Trading with KS | UNKNOWN | 2021-12-30 | 4195 | 14 | 14 | 14 | ok |
| [9B9aahP4xaQ](https://www.youtube.com/watch?v=9B9aahP4xaQ) Daily KLSE BURSA Update - 30-12-2021 - GENETEC REBOUND STARTED?  GENTING & GENM PICK BOTTOM? | Trading with KS | UNKNOWN | 2021-12-30 | 1088 | 8 | 8 | 8 | ok |
| [ahkaW9Js37w](https://www.youtube.com/watch?v=ahkaW9Js37w) 28122021 #GENTING  #GENM 今天双双补缺口 gap closed, 但是是有分別的.  筹码分布图VOLUME PROFILE 就可以看到那里不同了. 盘后技术分析简评. | Double Swords Investing | UNKNOWN | 2021-12-28 | 1231 | 0 | 0 | 0 | ok |
| [yw1dtJ6-rXo](https://www.youtube.com/watch?v=yw1dtJ6-rXo) 26122021 #GENM  留意可否站稳在阻力线上. 盘后技术分析简评. | Double Swords Investing | GENM | 2021-12-26 | 566 | 0 | 0 | 0 | ok |
| [DBVAdz7HAUU](https://www.youtube.com/watch?v=DBVAdz7HAUU) 24122021 #GENTING 今早跳空开盘，准备补缺口.  盘后技术分析简评. | Double Swords Investing | GENTING | 2021-12-24 | 749 | 0 | 0 | 0 | ok |
| [QRIZzndcvUQ](https://www.youtube.com/watch?v=QRIZzndcvUQ) 24122021 #GENTING 简单粗暴估值法 #agak. 教学. | Double Swords Investing | GENTING | 2021-12-24 | 1081 | 5 | 5 | 5 | ok |
| [jEBXnbtepuA](https://www.youtube.com/watch?v=jEBXnbtepuA) 财经Espresso ｜ 对林国泰有信心  分析员喊买云顶 | 百格 Pocketimes | UNKNOWN | 2021-12-23 | 9602 | 10 | 10 | 10 | ok |
| [oUhylXly1KQ](https://www.youtube.com/watch?v=oUhylXly1KQ) Morning KLSE BURSA Update - 23-12-2021 - GENTING REBOUND? MPI PMETAL GENTING EPMB KGB GENETEC | Trading with KS | GENTING | 2021-12-23 | 641 | 8 | 8 | 8 | ok |
| [dV89z8uFJFk](https://www.youtube.com/watch?v=dV89z8uFJFk) 21122021 #GENTING 三重顶型态? 早上实时观股技术分析简评. | Double Swords Investing | GENTING | 2021-12-21 | 958 | 1 | 1 | 1 | ok |
| [umbeQfo4K0c](https://www.youtube.com/watch?v=umbeQfo4K0c) 16122021 #GENM  盘后技术分析简评. | Double Swords Investing | GENM | 2021-12-16 | 608 | 0 | 0 | 0 | ok |
| [zvo7hly8xxo](https://www.youtube.com/watch?v=zvo7hly8xxo) 16122021 #GENTING 午盘技术分析简评. | Double Swords Investing | GENTING | 2021-12-16 | 698 | 0 | 0 | 0 | ok |
| [2krXv3aTLMs](https://www.youtube.com/watch?v=2krXv3aTLMs) (马股)浅谈GENTING BERHAD 云顶BHD | 严谈股市 | UNKNOWN | 2021-12-16 | 1114 | 4 | 4 | 4 | ok |
| [JrI85h__LIQ](https://www.youtube.com/watch?v=JrI85h__LIQ) 【马股分析】云顶大马股价起落原来“有迹可循？”！！别让到口的肉飞了！！ | 牛转钱坤 Superbull | GENM | 2021-12-14 | 17589 | 14 | 14 | 14 | ok |
| [HHN0Sf7S2DI](https://www.youtube.com/watch?v=HHN0Sf7S2DI) 13122021 #GENM 午盘技术分析 Technical Analysis [Eng Sub Title] | Double Swords Investing | GENM | 2021-12-13 | 1119 | 1 | 1 | 1 | ok |
| [0NgTP2GRiFs](https://www.youtube.com/watch?v=0NgTP2GRiFs) 11122021 #GENTING  的关键价位和操作策略. 个股盘后技术分析 。 | Double Swords Investing | GENTING | 2021-12-11 | 1399 | 1 | 1 | 1 | ok |
| [B7pJnNpQN3M](https://www.youtube.com/watch?v=B7pJnNpQN3M) 第 M18 期 \| 20211209 \| GENTING 酝酿着反弹，阻力位是 ？ \| GENTING & INNO 马股 \| 交易投资 \| 股票技术分析【每日分析】 | Ryan Trader's Hub | GENTING | 2021-12-10 | 314 | 0 | 0 | 0 | ok |
| [sMD0jMM96zU](https://www.youtube.com/watch?v=sMD0jMM96zU) EP. M18 \| 20211209 \| GENTING Potential Reversal \| GENTING & INNO Stock Technical Analysis | Ryan Trader's Hub | GENTING | 2021-12-10 | 165 | 0 | 0 | 0 | ok |
| [zdSa0xf8qU4](https://www.youtube.com/watch?v=zdSa0xf8qU4) Daily KLSE BURSA Update - 9-12-2021  - KLCI CLOSING PUSHED TO 1501 ! GENTING & GENM CAN PICK BOTTOM? | Trading with KS | UNKNOWN | 2021-12-09 | 2245 | 12 | 12 | 12 | ok |
| [CvxUaHepjbw](https://www.youtube.com/watch?v=CvxUaHepjbw) KS看股- 每天马股 KLSE BURSA 分享 - 9-12-2021 - KLCI 收市推上1501点! GENTING 和 GENM能捞底吗? | Trading with KS | UNKNOWN | 2021-12-09 | 4307 | 23 | 23 | 23 | ok |
| [iW6xlyKdhBg](https://www.youtube.com/watch?v=iW6xlyKdhBg) 大马股票 \| 云顶大马 \| GENM \| 从零开始了解云顶大马EP.02 | 少爷兵 | UNKNOWN | 2021-12-09 | 4138 | 3 | 3 | 3 | ok |
| [Jz0O875Vmzk](https://www.youtube.com/watch?v=Jz0O875Vmzk) 09122021 #GENTING 今早突破阻力线, 早盘后个股技术分析. | Double Swords Investing | GENTING | 2021-12-09 | 1156 | 0 | 0 | 0 | ok |
| [iOzbobwkAEk](https://www.youtube.com/watch?v=iOzbobwkAEk) 02122021 #GENTING 没有出现破底翻型态.  盘后个股技术分析. | Double Swords Investing | GENTING | 2021-12-02 | 1195 | 0 | 0 | 0 | ok |
| [VCxzDHItc7I](https://www.youtube.com/watch?v=VCxzDHItc7I) 02122021 #GENM 在支撑线上出现了 定海神针. 盘后个股技术分析. | Double Swords Investing | GENM | 2021-12-02 | 1138 | 2 | 2 | 2 | ok |
| [yGSqBuM210Q](https://www.youtube.com/watch?v=yGSqBuM210Q) 第九十三期：市场太烂，等机会吧！GENM, GENTING | 我是雷公 | UNKNOWN | 2021-12-01 | 8447 | 57 | 57 | 57 | ok |
| [CcBzrGjdjZI](https://www.youtube.com/watch?v=CcBzrGjdjZI) 29112021 云顶双雄 #GENTING #GENM 的支撑线在那里? 买入讯号? 早盘后个股技术分析. | Double Swords Investing | UNKNOWN | 2021-11-29 | 1897 | 1 | 1 | 1 | ok |
| [KYLp1wKISrU](https://www.youtube.com/watch?v=KYLp1wKISrU) 浅谈 #GENTING 3182 \| 马股 | 股市先锋队 | GENTING | 2021-11-28 | 66 | 0 | 0 | 0 | ok |
| [npYPfUCL2z4](https://www.youtube.com/watch?v=npYPfUCL2z4) 27112021 #GENTING  可以捞了吗? 聊聊技术分析操作策略! | Double Swords Investing | GENTING | 2021-11-27 | 1584 | 0 | 0 | 0 | ok |
| [PQtTYg83CQM](https://www.youtube.com/watch?v=PQtTYg83CQM) 【行家论股】云顶大马 末季有望强势反弹 | 南洋商报eNanyang | GENM | 2021-11-26 | 633 | 2 | 2 | 2 | ok |
| [Oyx671hQ2b8](https://www.youtube.com/watch?v=Oyx671hQ2b8) 26112021 实时观股 #GENM 跌破 RM3.00. 机会吗？ 如何运用 移动平均线 MA200天操作? | Double Swords Investing | GENM | 2021-11-26 | 1501 | 2 | 2 | 2 | ok |
| [6xxGqJ4Y_Y4](https://www.youtube.com/watch?v=6xxGqJ4Y_Y4) 财经Espresso \| 云顶赤字恶化 云顶大马亏损缩减 | 百格 Pocketimes | UNKNOWN | 2021-11-25 | 9424 | 2 | 2 | 2 | ok |
| [dGLidW5vsMQ](https://www.youtube.com/watch?v=dGLidW5vsMQ) 【行家论股】云顶 经济重启喜迎复苏 | 南洋商报eNanyang | UNKNOWN | 2021-11-10 | 1018 | 0 | 0 | 0 | ok |
| [2YFhsZvuUkc](https://www.youtube.com/watch?v=2YFhsZvuUkc) 财经 Espresso｜云顶户外乐园 传下月开张 | 百格 Pocketimes | GENTING | 2021-10-27 | 12208 | 7 | 7 | 7 | ok |
| [7LCPHRdi_uk](https://www.youtube.com/watch?v=7LCPHRdi_uk) 财经 Espresso｜云顶半年亏18亿 有望躲过博彩税 | 百格 Pocketimes | GENTING | 2021-10-21 | 11778 | 1 | 1 | 1 | ok |
| [CPnnsddGmZY](https://www.youtube.com/watch?v=CPnnsddGmZY) 天哥受访于INVESTING NOTE~云顶重开是否一个投资机会？十多年投资领悟最大的投资道理？ | 第一天投资理财研究所 | GENM | 2021-10-14 | 4869 | 2 | 2 | 2 | ok |
| [Xc2gmEp8SVw](https://www.youtube.com/watch?v=Xc2gmEp8SVw) 财经Espresso \| 云顶大马加码6亿 帝国5年难赚钱 | 百格 Pocketimes | UNKNOWN | 2021-10-13 | 16242 | 9 | 9 | 9 | ok |
| [HFADA245lvY](https://www.youtube.com/watch?v=HFADA245lvY) 【行家论股】云顶大马 经济重开亏损料收窄 | 南洋商报eNanyang | GENM | 2021-10-13 | 875 | 0 | 0 | 0 | ok |
| [thCW1c2Ymr4](https://www.youtube.com/watch?v=thCW1c2Ymr4) Genting 2021 10 11 韩巍博士股票分析 | Robin Han | GENTING | 2021-10-12 | 15 | 0 | 0 | 0 | ok |
| [5c7V3lHXoi8](https://www.youtube.com/watch?v=5c7V3lHXoi8) GENTING 2021 10 08 韩巍博士股票分析 | Robin Han | GENTING | 2021-10-10 | 51 | 0 | 0 | 0 | ok |
| [BqSVNY837nQ](https://www.youtube.com/watch?v=BqSVNY837nQ) （40/2021）云顶是否朝着复苏大道前进？  Is Genting heading towards recovery? | Gtc Resources | GENTING | 2021-09-27 | 110 | 0 | 0 | 0 | ok |
| [96r4lMapep0](https://www.youtube.com/watch?v=96r4lMapep0) #HARTA和 #GENM 的有趣现象.  股价已经回到疫情前2019年的价位，但是公司盈利并还没有回到去。。。 | Double Swords Investing | GENM | 2021-09-12 | 2074 | 16 | 16 | 16 | ok |
| [XS2srl3GpZc](https://www.youtube.com/watch?v=XS2srl3GpZc) 网友尖锐提问：云顶重开在即，会带动股价回来吗？Buy on Rumor Sell on News?! | 陈剑老师投资教育频道 | UNKNOWN | 2021-09-08 | 15291 | 25 | 25 | 25 | ok |
| [NFF5rtszCQU](https://www.youtube.com/watch?v=NFF5rtszCQU) GENTING COMEBACK? KNM TROUBLES, FOREIGN INVESTOR CONFIDENCE IN BURSA REVIVED? | FIRL | UNKNOWN | 2021-09-07 | 8155 | 34 | 34 | 34 | ok |
| [43w5vcldp28](https://www.youtube.com/watch?v=43w5vcldp28) EDGE WEEKLY: Genting’s big bet on Vegas | The Edge TV | GENTING | 2021-09-06 | 603 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [1pSrEWfRceA](https://www.youtube.com/watch?v=1pSrEWfRceA) 财经Espresso｜云顶2021：亏9亿vs赚3亿 | 百格 Pocketimes | GENTING | 2021-08-30 | 15143 | 4 | 4 | 4 | ok |
| [u0xHMU6eaWM](https://www.youtube.com/watch?v=u0xHMU6eaWM) 【行家论股】云顶 美业务支撑收入 | 南洋商报eNanyang | GENTING | 2021-08-30 | 1236 | 0 | 0 | 0 | ok |
| [IAHJQEkIzbg](https://www.youtube.com/watch?v=IAHJQEkIzbg) 29082021 复苏股 #GENM #AIRPORT #AIRASIA 个股技术分析. | Double Swords Investing | GENM | 2021-08-29 | 758 | 1 | 1 | 1 | ok |
| [Y9Z1jX_wVok](https://www.youtube.com/watch?v=Y9Z1jX_wVok) 财经Espresso｜“封山”冲击 云顶次季亏5.6亿 | 百格 Pocketimes | GENTING | 2021-08-27 | 16143 | 5 | 5 | 5 | ok |
| [5vTTYXhEfNY](https://www.youtube.com/watch?v=5vTTYXhEfNY) 财经Espresso ｜ 开拓网上市场  云顶找Amazon帮忙 | 百格 Pocketimes | GENTING | 2021-08-25 | 15397 | 1 | 1 | 1 | ok |
| [Eg4D1avlYvo](https://www.youtube.com/watch?v=Eg4D1avlYvo) 22082021 复苏股 #GENM #AIRPORT #AIRASIA 盘后个股技术分析. 运用Volume Profile 筹码峰分析套牢盘和阻力区. | Double Swords Investing | GENM | 2021-08-22 | 512 | 3 | 3 | 3 | ok |
| [DOErGnkuj4Q](https://www.youtube.com/watch?v=DOErGnkuj4Q) EVENING 5: Maybank sees wider loss for Genting Malaysia | The Edge TV | UNKNOWN | 2021-08-17 | 3793 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [pvOvlmwDImc](https://www.youtube.com/watch?v=pvOvlmwDImc) KS看股- 每天马股KLSE分享 - 17-8-2021 - Revenue 扩展到保险行业 ! GenM 竞标体育博彩牌照 ! 0200 4715 9679 7034 0215 5657 0143 | Trading with KS | GENM | 2021-08-17 | 2050 | 17 | 17 | 17 | ok |
| [hvMehC8nwp8](https://www.youtube.com/watch?v=hvMehC8nwp8) KS看股- 每天马股KLSE分享 - 13-8-2021 - 云顶能反弹吗? AEMULUS 获330万新订单 ! GENTING DPHARMA MISC IJM AEMULUS OPCOM | Trading with KS | GENTING | 2021-08-13 | 3627 | 16 | 16 | 16 | ok |
| [Aus3jdwDSuY](https://www.youtube.com/watch?v=Aus3jdwDSuY) 【行家论股/视频】云顶 边境封锁阻碍复苏 | 南洋商报eNanyang | GENTING | 2021-08-13 | 652 | 0 | 0 | 0 | ok |
| [1JbUsyj_dA8](https://www.youtube.com/watch?v=1JbUsyj_dA8) Daily KLSE Update - 13-8-2021 - CAN GENTING REBOUND? AEMULUS GET 3.3m ORDER ! GENTING DPHARMA MISC | Trading with KS | GENTING | 2021-08-13 | 1166 | 12 | 12 | 12 | ok |
| [2hbKqQIMJL4](https://www.youtube.com/watch?v=2hbKqQIMJL4) 股票投资 \| 大马股票 \| 疫情后三大复苏股 #Genting#Carlsberg#Tenaga [马股分析]  [Bursa Malaysia] | BullStar 理財投資 | UNKNOWN | 2021-08-13 | 2217 | 5 | 5 | 5 | ok |
| [wlA1skSD_P8](https://www.youtube.com/watch?v=wlA1skSD_P8) 马来西亚政府要开放了 复苏股会起嘛？\| GENTING \| AIRASIA | Andy Yew | UNKNOWN | 2021-08-12 | 4790 | 3 | 3 | 3 | ok |
| [wMSm_xN0kv8](https://www.youtube.com/watch?v=wMSm_xN0kv8) 第四十六期：GENM & GENTING  买入时机 ？ | 我是雷公 | UNKNOWN | 2021-08-09 | 9637 | 16 | 16 | 16 | ok |
| [NfFILi-n_M4](https://www.youtube.com/watch?v=NfFILi-n_M4) 09082021 #GENM 云顶大马 早盘后个股技术分析. 也谈谈追高的 intraday 策略. | Double Swords Investing | GENM | 2021-08-09 | 487 | 1 | 1 | 1 | ok |
| [W7OAi39zo2o](https://www.youtube.com/watch?v=W7OAi39zo2o) GENTING Still can invest? \| Tan Sri Lim Kok Thay \| The FAQ Show | FAQ Show | UNKNOWN | 2021-08-08 | 14614 | 25 | 25 | 25 | ok |
| [80WLIWyiQYg](https://www.youtube.com/watch?v=80WLIWyiQYg) 01082021 #GENM 云顶大马 盘后个股技术分析! | Double Swords Investing | GENM | 2021-08-01 | 226 | 1 | 1 | 1 | ok |
| [jci5fO79rlI](https://www.youtube.com/watch?v=jci5fO79rlI) 30072021 #GENM 云顶大马 早盘后个股技术分析. | Double Swords Investing | GENM | 2021-07-30 | 209 | 2 | 2 | 2 | ok |
| [nI7mOU5Jga8](https://www.youtube.com/watch?v=nI7mOU5Jga8) 25072021 #GENM 云顶大马 盘后个股技术分析. | Double Swords Investing | GENM | 2021-07-25 | 417 | 3 | 3 | 3 | ok |
| [hle2IKbEhR4](https://www.youtube.com/watch?v=hle2IKbEhR4) Technical Analysis in 3 minutes: Genting Malaysia (GENM 4715) 210723 | Money Steps 金钱脚步 | UNKNOWN | 2021-07-23 | 288 | 0 | 0 | 0 | ok |
| [17tys8Q5G0E](https://www.youtube.com/watch?v=17tys8Q5G0E) 粗暴简单的 agak-agak 股价估值法.懂得这个就不会买贵了!PE vs Present value vs Future Value.用 Google Sheets 估算! #GENM 示范讲解. | Double Swords Investing | GENM | 2021-07-18 | 1963 | 15 | 15 | 15 | ok |
| [tvBObU3P8DQ](https://www.youtube.com/watch?v=tvBObU3P8DQ) #GENM 云顶大马 : 一周走势的技术分析. 短期支撑阻力价位. 是不是止跌回升了? 另外再分析明天的走势和操作策略. | Double Swords Investing | GENM | 2021-07-18 | 450 | 3 | 3 | 3 | ok |
| [eO8yZJyoNvM](https://www.youtube.com/watch?v=eO8yZJyoNvM) 15072021  #GENM 大马云顶 ，即时分析接下来的走势. 示范如何运用 Session Volume Profile 筹码分布 和 VWAP 短线分析. | Double Swords Investing | GENM | 2021-07-15 | 308 | 2 | 2 | 2 | ok |
| [sRB9arN6lRA](https://www.youtube.com/watch?v=sRB9arN6lRA) MALAYSIA = FAILED STATE?, GENTING, SCIB \| FIRL Quick Dive | FIRL | GENTING | 2021-07-13 | 10759 | 85 | 85 | 85 | ok |
| [NXj3itfmHK8](https://www.youtube.com/watch?v=NXj3itfmHK8) 11072021 #GENM 大马云顶 技术分析点评. 运用 Volume Profile Fixed Range 筹码分布分析未来的走势. VP Fixed Range 运用技巧. | Double Swords Investing | GENM | 2021-07-11 | 496 | 1 | 1 | 1 | ok |
| [2rBbi_2F8CY](https://www.youtube.com/watch?v=2rBbi_2F8CY) 财经Espresso｜核心业务惨淡 云顶“副业”大好 | 百格 Pocketimes | GENTING | 2021-07-09 | 17128 | 10 | 10 | 10 | ok |
| [IPBq4Zg_eqg](https://www.youtube.com/watch?v=IPBq4Zg_eqg) 【行家论股】云顶 横滨赌牌成最强激素 | 南洋商报eNanyang | GENTING | 2021-06-22 | 939 | 0 | 0 | 0 | ok |
| [dOADROsOJ2o](https://www.youtube.com/watch?v=dOADROsOJ2o) 【马股分析】面对FMCO 云顶大马是否还能稳如泰山？GENM \| 4715 [ENGLISH CC] | 牛转钱坤 Superbull | GENM | 2021-05-29 | 36137 | 102 | 102 | 102 | ok |
| [VybliJQ2v_E](https://www.youtube.com/watch?v=VybliJQ2v_E) 【行家论股】云顶大马 未来季度有望改善 | 南洋商报eNanyang | GENM | 2021-05-27 | 1005 | 0 | 0 | 0 | ok |
| [Hdt1jg7Kj9g](https://www.youtube.com/watch?v=Hdt1jg7Kj9g) 财经Espresso｜“开山”失灵？ 云顶双雄再亏损 | 百格 Pocketimes | GENM | 2021-05-25 | 10475 | 3 | 3 | 3 | ok |
| [Z0p0hB8daJE](https://www.youtube.com/watch?v=Z0p0hB8daJE) 【行家论股】云顶 短期盈利靠狮城 | 南洋商报eNanyang | GENTING | 2021-05-10 | 368 | 0 | 0 | 0 | ok |
| [0rJS90OkeYQ](https://www.youtube.com/watch?v=0rJS90OkeYQ) 3128.KL: Genting Berhad- Breaking out of a trendline | Share and Stocks | GENTING | 2021-04-29 | 22 | 0 | 0 | 0 | ok |
| [1Ar2vqCidvw](https://www.youtube.com/watch?v=1Ar2vqCidvw) 【行家论股】云顶大马 2022财年料V型复苏 | 南洋商报eNanyang | GENM | 2021-04-14 | 858 | 0 | 0 | 0 | ok |
| [OsM6uo8nli0](https://www.youtube.com/watch?v=OsM6uo8nli0) 10 Years Financial Analysis #8: Genting Malaysia Berhad | Jonathan San | UNKNOWN | 2021-03-30 | 713 | 5 | 5 | 5 | ok |
| [f2Ok3l4HMgQ](https://www.youtube.com/watch?v=f2Ok3l4HMgQ) Genting Malaysia Stock Analysis (GENM) - A dividend stock? | Jessica Sin | UNKNOWN | 2021-03-28 | 4074 | 17 | 17 | 17 | ok |
| [8VNwoHt_WNY](https://www.youtube.com/watch?v=8VNwoHt_WNY) 财经Espresso｜卖资产 云顶联号转亏为盈 | 百格 Pocketimes | UNKNOWN | 2021-03-23 | 13678 | 10 | 10 | 10 | ok |
| [VPD2GG2f56M](https://www.youtube.com/watch?v=VPD2GG2f56M) 财经Espresso｜刚花8千万 云顶大马配发470万股 | 百格 Pocketimes | GENM | 2021-03-22 | 23043 | 8 | 8 | 8 | ok |
| [gbtc87z6R6M](https://www.youtube.com/watch?v=gbtc87z6R6M) 2021马股投资 \| 云顶大马GentingM价值股强势回归的最佳买入时机 | JC聊股势 | GENM | 2021-03-20 | 3062 | 24 | 24 | 24 | ok |
| [Hzxf9wf3fGk](https://www.youtube.com/watch?v=Hzxf9wf3fGk) 3 Stocks to Ride the Recovery Theme in Malaysia - AIRASIA, GENM, GENTING | Ming Jong Tey - Wyckoff Method | UNKNOWN | 2021-03-14 | 1348 | 14 | 14 | 14 | ok |
| [6A7wr7K9eXI](https://www.youtube.com/watch?v=6A7wr7K9eXI) 财经ESPRESSO｜复苏主题发酵 云顶三雄轮流上涨 | 百格 Pocketimes | GENM | 2021-03-11 | 11910 | 9 | 9 | 9 | ok |
| [V7TOABCAp7M](https://www.youtube.com/watch?v=V7TOABCAp7M) 【马股分析】云顶大马最新财报速看！万众瞩目复苏股中的领头羊！？GENM \| 4715 [English CC] | 牛转钱坤 Superbull | UNKNOWN | 2021-03-10 | 30299 | 56 | 56 | 56 | ok |
| [eGmteThVVYY](https://www.youtube.com/watch?v=eGmteThVVYY) 【马股分析】云顶 GENTING BERHAD  GENTINGGENTING 3182 | Joseph Kelly | UNKNOWN | 2021-03-02 | 1831 | 9 | 9 | 9 | ok |
| [F5ZxQ1fT8zE](https://www.youtube.com/watch?v=F5ZxQ1fT8zE) 【行家论股】云顶 疫苗护航反弹可期 | 南洋商报eNanyang | GENTING | 2021-02-26 | 418 | 0 | 0 | 0 | ok |
| [Hph363QHTJM](https://www.youtube.com/watch?v=Hph363QHTJM) 财经Espresso \| 云顶双雄2020年亏损32.88亿 | 百格 Pocketimes | GENTING | 2021-02-25 | 12597 | 130 | 130 | 130 | ok |
| [mEgyJkb-kFU](https://www.youtube.com/watch?v=mEgyJkb-kFU) 财经Espresso \| 新年开门  云顶多多万能"股涨" | 百格 Pocketimes | GENTING | 2021-02-16 | 15399 | 161 | 161 | 161 | ok |
| [cwohb8w_-G4](https://www.youtube.com/watch?v=cwohb8w_-G4) 老李祝大家新年发财，万事如意。Genting 未来可能有不错的回报。适合长期投资！ | 老李讲股 | GENTING | 2021-02-11 | 8039 | 46 | 46 | 46 | ok |
| [6trBSvwu8fI](https://www.youtube.com/watch?v=6trBSvwu8fI) 财经Espresso \| "封山"到218  云顶失新年旺季 | 百格 Pocketimes | UNKNOWN | 2021-02-05 | 24704 | 26 | 26 | 26 | ok |
| [DZ4SWfEiOXo](https://www.youtube.com/watch?v=DZ4SWfEiOXo) 财经Espresso \| 云顶爱尔兰公司清盘 | 百格 Pocketimes | UNKNOWN | 2021-02-02 | 33165 | 132 | 132 | 132 | ok |
| [nmsYJLp0Xro](https://www.youtube.com/watch?v=nmsYJLp0Xro) 【讲股吹水03】2021/22 最有潜能复苏的股票 \| 我如何部署 \| #GENM #GENTING #AIRASIA | HY Investment | UNKNOWN | 2021-01-30 | 377 | 2 | 2 | 2 | ok |
| [aps3z6CFQqU](https://www.youtube.com/watch?v=aps3z6CFQqU) 最适合中长期投资的马来西亚股票 \| 云顶大马 \| GENTING MALAYSIA BERHAD #小编谈马股 | WCT Worldwide Training - Wealth Creation | UNKNOWN | 2021-01-27 | 1479 | 0 | 0 | 0 | ok |
| [pgYiXkVIrqs](https://www.youtube.com/watch?v=pgYiXkVIrqs) 财经Espresso｜新年旺季可开门？ 云顶“股涨” | 百格 Pocketimes | UNKNOWN | 2021-01-26 | 35028 | 41 | 41 | 41 | ok |
| [7lbG8pDnRIY](https://www.youtube.com/watch?v=7lbG8pDnRIY) 财经Espresso｜今年倒第一家 云顶英国会更惨？ | 百格 Pocketimes | UNKNOWN | 2021-01-15 | 36461 | 5 | 5 | 5 | ok |
| [g8WUeInngsg](https://www.youtube.com/watch?v=g8WUeInngsg) 财经Espresso｜坐拥37亿 云顶大马料派高息 | 百格 Pocketimes | UNKNOWN | 2021-01-05 | 17974 | 32 | 32 | 32 | ok |
| [DwZhSVEFTCI](https://www.youtube.com/watch?v=DwZhSVEFTCI) 云顶集团(Genting Berhad)这只股票未来还有竞争优势吗？ | 投资与财务 | UNKNOWN | 2020-12-21 | 13547 | 17 | 17 | 17 | ok |
| [6S8Nx1pwGRU](https://www.youtube.com/watch?v=6S8Nx1pwGRU) GENTING 3182 & AIR ASIA 5099 - BIG GAIN STOCK - KLSE 17th December 2020 | Trading with KS | GENTING | 2020-12-17 | 739 | 4 | 4 | 4 | ok |
| [bG2DF8Mfsio](https://www.youtube.com/watch?v=bG2DF8Mfsio) 【马股分析】云顶大马最详细分析！疫情后王者归来？GENM \| 4715 [English CC] | 牛转钱坤 Superbull | UNKNOWN | 2020-12-15 | 57847 | 110 | 110 | 110 | ok |
| [_IqnMuBnU48](https://www.youtube.com/watch?v=_IqnMuBnU48) 【马股分析】全马最强现金流的公司？2021最有潜能复苏的公司？云顶集团最详细分析！GENTING \| 3182 [English CC] | 牛转钱坤 Superbull | UNKNOWN | 2020-12-12 | 66155 | 124 | 124 | 124 | ok |
| [OURzkWY3t54](https://www.youtube.com/watch?v=OURzkWY3t54) 疫苗出现后，#GENM #GENTING 可以怎么操作？技术走势如何？【5分钟个股技术分析】（CC字幕） | Jack Investment | UNKNOWN | 2020-12-01 | 18089 | 14 | 14 | 14 | ok |
| [e0V-JsJlu-M](https://www.youtube.com/watch?v=e0V-JsJlu-M) 财经Espresso｜云顶百亿项目 明年夏天开张 | 百格 Pocketimes | GENTING | 2020-11-27 | 19720 | 10 | 10 | 10 | ok |
| [Z9hYs3GcKAM](https://www.youtube.com/watch?v=Z9hYs3GcKAM) 云顶大马 全年亏损料达16亿 | 南洋商报eNanyang | GENM | 2020-11-27 | 808 | 0 | 0 | 0 | ok |
| [4w9Y7sUCqFM](https://www.youtube.com/watch?v=4w9Y7sUCqFM) 财经Espresso \|  第二季亏7.9亿   云顶第三季仍丢1.3亿 | 百格 Pocketimes | GENTING | 2020-11-26 | 13572 | 4 | 4 | 4 | ok |
| [qQbUy0yP4T4](https://www.youtube.com/watch?v=qQbUy0yP4T4) 【南视界】云顶人气“好冷”! | 南洋商报eNanyang | UNKNOWN | 2020-11-20 | 4035 | 1 | 1 | 1 | ok |
| [5zuOW_i_Kbo](https://www.youtube.com/watch?v=5zuOW_i_Kbo) Genting起飞了吗?-Queenie股票教室 | Queenie Homily | UNKNOWN | 2020-11-18 | 130 | 0 | 0 | 0 | ok |
| [BaxN6jAdVeE](https://www.youtube.com/watch?v=BaxN6jAdVeE) 财经Espresso \| 狮城转盈 云顶“股涨”35仙 | 百格 Pocketimes | GENM | 2020-11-16 | 15033 | 5 | 5 | 5 | ok |
| [3Vs827Wkxrw](https://www.youtube.com/watch?v=3Vs827Wkxrw) 市场动荡多 惠誉：打乱云顶减债 | 百格 Pocketimes | UNKNOWN | 2020-11-06 | 17595 | 3 | 3 | 3 | ok |
| [_EpQTBDVvRo](https://www.youtube.com/watch?v=_EpQTBDVvRo) 3月2.91令吉 云顶随时改写新低｜财经Espresso | 百格 Pocketimes | GENTING | 2020-10-30 | 14587 | 21 | 21 | 21 | ok |
| [WP_W1o9_p70](https://www.youtube.com/watch?v=WP_W1o9_p70) 美国单轨项目  云顶获准探讨    \| 财经Espresso | 百格 Pocketimes | GENTING | 2020-10-21 | 11945 | 9 | 9 | 9 | ok |
| [8G1k5lAXALs](https://www.youtube.com/watch?v=8G1k5lAXALs) 云顶大马展望胜母公司｜财经espresso | 百格 Pocketimes | GENM | 2020-10-05 | 12055 | 21 | 21 | 21 | ok |
| [jW7AApGG4vc](https://www.youtube.com/watch?v=jW7AApGG4vc) 云顶高原 人龙车龙重现｜财经ESPRESSO | 百格 Pocketimes | GENM | 2020-09-22 | 29146 | 16 | 16 | 16 | ok |
| [_vSeDZvhk2U](https://www.youtube.com/watch?v=_vSeDZvhk2U) EVENING 5: Worst over for GenM, says RHB | The Edge TV | UNKNOWN | 2020-09-22 | 3149 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [ziL_dhKUejs](https://www.youtube.com/watch?v=ziL_dhKUejs) 云顶酒店入住率达90% ｜财经Espresso | 百格 Pocketimes | GENM | 2020-09-18 | 17857 | 20 | 20 | 20 | ok |
| [mGxrQ01ULr4](https://www.youtube.com/watch?v=mGxrQ01ULr4) Genting 2020 \|云顶大马\|Genm\|4715\|云顶破产了 ？林国泰辞职? \|叉烧理财笔记\| | Khong Seng Chong | UNKNOWN | 2020-09-14 | 91219 | 52 | 52 | 52 | ok |
| [yuEPA8n65Vs](https://www.youtube.com/watch?v=yuEPA8n65Vs) 6亿注资帝国  分析员唱衰云顶大马    \| 财经Espresso | 百格 Pocketimes | GENM | 2020-09-14 | 17973 | 10 | 10 | 10 | ok |
| [K9f3m-IFS-M](https://www.youtube.com/watch?v=K9f3m-IFS-M) EVENING 5: Analysts wary of GenM and Empire’s stock subscription | The Edge TV | UNKNOWN | 2020-09-14 | 3391 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [ra6QDHKHOJU](https://www.youtube.com/watch?v=ra6QDHKHOJU) 云顶大马 注资帝国不意外 | 南洋商报eNanyang | GENM | 2020-09-14 | 1658 | 0 | 0 | 0 | ok |
| [fhyaYYAOh6A](https://www.youtube.com/watch?v=fhyaYYAOh6A) 云顶大马 Genting Malaysia \| 大马股票 \| 云顶大马现在很便宜？但是你敢买吗？\| 【乐学成长空间】 | 乐学成长空间 - LXInvest | UNKNOWN | 2020-09-11 | 253771 | 180 | 180 | 180 | ok |
| [mMjDBdFW-bw](https://www.youtube.com/watch?v=mMjDBdFW-bw) 云顶系派18.5仙  林国泰获3.1亿 ｜财经Espresso | 百格 Pocketimes | UNKNOWN | 2020-08-28 | 25539 | 14 | 14 | 14 | ok |
| [Jm8ZL1hKj6U](https://www.youtube.com/watch?v=Jm8ZL1hKj6U) 云顶大马 6仙股息是惊喜 | 南洋商报eNanyang | GENM | 2020-08-28 | 1480 | 1 | 1 | 1 | ok |
| [K8U-7V8VADM](https://www.youtube.com/watch?v=K8U-7V8VADM) EVENING 5: Genting falls on knee-jerk reaction | The Edge TV | UNKNOWN | 2020-08-21 | 6326 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [Unzy-7F0bT8](https://www.youtube.com/watch?v=Unzy-7F0bT8) 云顶 次季盈利料重挫 | 南洋商报eNanyang | GENTING | 2020-08-07 | 829 | 0 | 0 | 0 | ok |
| [Ra8lvqiM6iY](https://www.youtube.com/watch?v=Ra8lvqiM6iY) 赌场泄气/云顶油棕业务“争气” ｜ 财经Espresso | 百格 Pocketimes | GENM | 2020-07-30 | 12037 | 5 | 5 | 5 | ok |
| [eltGJsaUzKc](https://www.youtube.com/watch?v=eltGJsaUzKc) 云顶集团的投资价值 vs 20年前的名胜世界，已今非昔比，而很多投资者仍蒙在鼓里... | 陈剑老师投资教育频道 | UNKNOWN | 2020-07-27 | 106790 | 94 | 94 | 94 | ok |
| [lgm1ydNcHhE](https://www.youtube.com/watch?v=lgm1ydNcHhE) 云顶纽约联号公司  发行20亿债券｜财经espresso | 百格 Pocketimes | UNKNOWN | 2020-07-20 | 10321 | 11 | 11 | 11 | ok |
| [itG3DUdF-Gc](https://www.youtube.com/watch?v=itG3DUdF-Gc) 大马15% 云顶狮城纽约裁多少？｜ 财经Espresso | 百格 Pocketimes | UNKNOWN | 2020-07-15 | 12989 | 4 | 4 | 4 | ok |
| [MI-jcP8eHWM](https://www.youtube.com/watch?v=MI-jcP8eHWM) 发仔和你解释云顶大马股价走势，分享云顶大马是否值得考虑买进？ | exceller plus | UNKNOWN | 2020-07-08 | 8963 | 3 | 3 | 3 | ok |
| [QzCNZZx0WnU](https://www.youtube.com/watch?v=QzCNZZx0WnU) GENM (4715) | Big Wallet | GENM | 2020-06-28 | 787 | 2 | 2 | 2 | ok |
| [GI61tO2-3ws](https://www.youtube.com/watch?v=GI61tO2-3ws) 全年恐转亏/云顶大马派息不乐观 \| 财经ESPRESSO | 百格 Pocketimes | GENM | 2020-06-22 | 12804 | 13 | 13 | 13 | ok |
| [oNog951VNPI](https://www.youtube.com/watch?v=oNog951VNPI) EVENING 5: Dividends still on the cards for Genting Malaysia | The Edge TV | UNKNOWN | 2020-06-22 | 4020 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [feIro_R-97g](https://www.youtube.com/watch?v=feIro_R-97g) 619重开？云顶双雄股价飙高 | 百格 Pocketimes | UNKNOWN | 2020-06-17 | 17661 | 11 | 11 | 11 | ok |
| [RaqWP74WLPU](https://www.youtube.com/watch?v=RaqWP74WLPU) 登吉度假村 云顶：618复工｜财经Espresso | 百格 Pocketimes | GENM | 2020-06-16 | 19951 | 18 | 18 | 18 | ok |
| [xOfWkHEbWPs](https://www.youtube.com/watch?v=xOfWkHEbWPs) Genting Malaysia: off its game | Edward Wong | UNKNOWN | 2020-05-31 | 3618 | 0 | 0 | 0 | ok |
| [SQUzz6fOyE0](https://www.youtube.com/watch?v=SQUzz6fOyE0) Neil Foo 【How Resort World Genting still announce share dividend ?】 | Dr Neil Foo | GENTING | 2020-05-29 | 113 | 0 | 0 | 0 | ok |
| [VepWueat9F4](https://www.youtube.com/watch?v=VepWueat9F4) 云顶“封山”冲击 大于市场预期｜财经Espresso | 百格 Pocketimes | GENM | 2020-05-22 | 44428 | 28 | 28 | 28 | ok |
| [CoQ4IAjg7ms](https://www.youtube.com/watch?v=CoQ4IAjg7ms) #stockGenm #stockKlci stock #malaysia stock GENM (4715) technical analysis | Peter blogger | UNKNOWN | 2020-05-22 | 504 | 4 | 4 | 4 | ok |
| [rQk9YfjzmPM](https://www.youtube.com/watch?v=rQk9YfjzmPM) EVENING 5: Genting Malaysia to shed jobs | The Edge TV | UNKNOWN | 2020-05-21 | 10405 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [RLwPQUQJW6A](https://www.youtube.com/watch?v=RLwPQUQJW6A) 云顶亏1.3亿 云顶大马亏4.2亿 \| 财经Espresso | 百格 Pocketimes | UNKNOWN | 2020-05-21 | 16952 | 24 | 24 | 24 | ok |
| [azQlCKF7gEM](https://www.youtube.com/watch?v=azQlCKF7gEM) 业务陆续发布  云顶喜忧参半｜财经Espresso | 百格 Pocketimes | UNKNOWN | 2020-05-20 | 16570 | 10 | 10 | 10 | ok |
| [CJJ2e_UUnZ8](https://www.youtube.com/watch?v=CJJ2e_UUnZ8) CMCO让云顶赌场无法营业，GENM股票继续“大平卖”？ | 陈剑老师投资教育频道 | UNKNOWN | 2020-05-12 | 50185 | 61 | 61 | 61 | ok |
| [9cCJB_bNMZ8](https://www.youtube.com/watch?v=9cCJB_bNMZ8) 云顶大马想“翻身” 要等2022年 \| 财经Espresso | 百格 Pocketimes | UNKNOWN | 2020-04-23 | 19526 | 21 | 21 | 21 | ok |
| [hP4YlM0n52o](https://www.youtube.com/watch?v=hP4YlM0n52o) 云顶大马 下半年可收复失地 | 南洋商报eNanyang | GENM | 2020-04-23 | 3753 | 1 | 1 | 1 | ok |
| [EQyySrx2ChE](https://www.youtube.com/watch?v=EQyySrx2ChE) 云顶大马员工 减薪放假二选一？ | 百格 Pocketimes | GENM | 2020-04-20 | 18946 | 35 | 35 | 35 | ok |
| [tTtQ-DWDAn0](https://www.youtube.com/watch?v=tTtQ-DWDAn0) GENM 4715 加油！ | 股灵精探 | UNKNOWN | 2020-04-10 | 44 | 0 | 0 | 0 | ok |
| [3KDnEeT5-BE](https://www.youtube.com/watch?v=3KDnEeT5-BE) Genting Malaysia, too cheap to ignore | Edward Wong | UNKNOWN | 2020-04-05 | 4302 | 0 | 0 | 0 | ok |
| [fSefdu62x6E](https://www.youtube.com/watch?v=fSefdu62x6E) "熊市定投计划"如何执行？云顶集团便宜过云顶大马？！【直播互动】【问答精华】 | 陈剑老师投资教育频道 | UNKNOWN | 2020-04-04 | 62035 | 70 | 70 | 70 | ok |
| [AUkn9tv-TCE](https://www.youtube.com/watch?v=AUkn9tv-TCE) 【行家论股】云顶 入场价3.20元 | 南洋商报eNanyang | UNKNOWN | 2020-03-27 | 1495 | 0 | 0 | 0 | ok |
| [qN3Xkod37TI](https://www.youtube.com/watch?v=qN3Xkod37TI) 云顶 上涨空间逾70% | 南洋商报eNanyang | UNKNOWN | 2020-03-25 | 1513 | 2 | 2 | 2 | ok |
| [s4GrqyZK7Zg](https://www.youtube.com/watch?v=s4GrqyZK7Zg) 【行家论股】云顶大马  9.4%周息率诱人 | 南洋商报eNanyang | GENM | 2020-03-20 | 454 | 0 | 0 | 0 | ok |
| [5bT9xW5Zpwc](https://www.youtube.com/watch?v=5bT9xW5Zpwc) 高原封山 云顶至少丢2.5亿 \| 财经Espresso | 百格 Pocketimes | UNKNOWN | 2020-03-18 | 41466 | 26 | 26 | 26 | ok |
| [x_J5v_vZxy0](https://www.youtube.com/watch?v=x_J5v_vZxy0) Genting Malaysia Bhd (GENM) Latest News by Greentrades | Raymond | UNKNOWN | 2020-03-07 | 277 | 1 | 1 | 1 | ok |
| [r8YI-cbtHDU](https://www.youtube.com/watch?v=r8YI-cbtHDU) 【行家论股】云顶大马 全年财测大砍29% | 南洋商报eNanyang | GENM | 2020-02-28 | 834 | 0 | 0 | 0 | ok |
| [KcqN-IV_JKQ](https://www.youtube.com/watch?v=KcqN-IV_JKQ) 新冠肺炎 I 马来西亚云顶 GENTING 买云顶股票的好机会？马来西亚股票技术分析 20 FEB 2020 | FuturesMalaysia | UNKNOWN | 2020-02-19 | 1428 | 2 | 2 | 2 | ok |
| [LUfg2jAHBjU](https://www.youtube.com/watch?v=LUfg2jAHBjU) 云顶潜在风险恐酿“毁灭性冲击” \| 财经espresso | 百格 Pocketimes | UNKNOWN | 2020-02-13 | 133004 | 27 | 27 | 27 | ok |
| [Sh6uKqvAq0Q](https://www.youtube.com/watch?v=Sh6uKqvAq0Q) 【行家论股】云顶大马 股价重挫可买入 | 南洋商报eNanyang | GENM | 2020-02-10 | 3312 | 0 | 0 | 0 | ok |
| [r1pWg4N2eLY](https://www.youtube.com/watch?v=r1pWg4N2eLY) 对抗肺炎：云顶高原酒店降价75% \| 财经Espresso | 百格 Pocketimes | UNKNOWN | 2020-02-07 | 28451 | 20 | 20 | 20 | ok |
| [i4VXDtQQkKE](https://www.youtube.com/watch?v=i4VXDtQQkKE) Genting Malaysia - Quarter Review | Edward Wong | UNKNOWN | 2019-12-21 | 1836 | 0 | 0 | 0 | ok |
| [YO6DnablsN8](https://www.youtube.com/watch?v=YO6DnablsN8) 帝国赌场快到手 林国泰大计已成 \| 财经Espresso | 百格 Pocketimes | GENM | 2019-11-14 | 9085 | 8 | 8 | 8 | ok |
| [7_-h3OFFS7U](https://www.youtube.com/watch?v=7_-h3OFFS7U) EVENING 5: Genting gets OK from Empire shareholders | The Edge TV | UNKNOWN | 2019-11-14 | 3043 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [JBhTrAherjA](https://www.youtube.com/watch?v=JBhTrAherjA) 斥资7千万 云顶购网路博彩公司\|财经Espresso | 百格 Pocketimes | UNKNOWN | 2019-11-01 | 7797 | 5 | 5 | 5 | ok |
| [617nmFnXMJk](https://www.youtube.com/watch?v=617nmFnXMJk) Genting Berhad: Opportunities and Threat Analysis | Chris Lau | GENTING | 2019-10-28 | 668 | 1 | 1 | 1 | ok |
| [PB5oWS_tWjw](https://www.youtube.com/watch?v=PB5oWS_tWjw) 云顶主题乐园要开了 考察团透露重点 \| 财经Espresso | 百格 Pocketimes | UNKNOWN | 2019-10-21 | 12468 | 18 | 18 | 18 | ok |
| [NoGfUUJft3U](https://www.youtube.com/watch?v=NoGfUUJft3U) 收购赌场风波未平 林国泰公司被小股东起诉 \| 财经espresso | 百格 Pocketimes | GENM | 2019-10-16 | 8410 | 7 | 7 | 7 | ok |
| [LSf0YG93daM](https://www.youtube.com/watch?v=LSf0YG93daM) 预算案炸弹：云顶忧彩票业怕 \| 财经Espresso | 百格 Pocketimes | UNKNOWN | 2019-10-02 | 10275 | 11 | 11 | 11 | ok |
| [UsQZ_EUjHJ4](https://www.youtube.com/watch?v=UsQZ_EUjHJ4) 大马股票 \| 云顶大马 \| GENM \| 从零开始了解云顶大马EP.01 | 少爷兵 | UNKNOWN | 2019-09-26 | 50228 | 26 | 26 | 26 | ok |
| [Ngl8vF9kHAs](https://www.youtube.com/watch?v=Ngl8vF9kHAs) 云顶大整顿业务 部署美国上市？\| 财经Espresso | 百格 Pocketimes | GENM | 2019-09-24 | 9058 | 4 | 4 | 4 | ok |
| [XMioN_2rZgI](https://www.youtube.com/watch?v=XMioN_2rZgI) 设新业务：云顶帝国赌场恐难止血 \| 财经Espresso | 百格 Pocketimes | GENM | 2019-09-20 | 8953 | 2 | 2 | 2 | ok |
| [iKVimmJX1qU](https://www.youtube.com/watch?v=iKVimmJX1qU) 大马股票 \| 云顶大马 \| 令云顶大马股价暴跌的5大事件 | 少爷兵 | UNKNOWN | 2019-09-14 | 118671 | 27 | 27 | 27 | ok |
| [eNc0UoCTEtk](https://www.youtube.com/watch?v=eNc0UoCTEtk) 云顶大马 核心净利上修33% | 南洋商报eNanyang | GENM | 2019-08-30 | 3552 | 0 | 0 | 0 | ok |
| [Sx7afdkz5ZY](https://www.youtube.com/watch?v=Sx7afdkz5ZY) EVENING 5: GenM seals RPT buy of Empire Resorts | The Edge TV | UNKNOWN | 2019-08-20 | 5174 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [ZZSuElk3etU](https://www.youtube.com/watch?v=ZZSuElk3etU) 每日一股One share one day(Genm 4715)8 月18日 | 股哥说股@jeff | GENM | 2019-08-19 | 942 | 0 | 0 | 0 | ok |
| [NTv1Z9I2_sI](https://www.youtube.com/watch?v=NTv1Z9I2_sI) 股价减15% 云顶大马还跌得不够？\| 财经Espresso | 百格 Pocketimes | GENM | 2019-08-16 | 15010 | 13 | 13 | 13 | ok |
| [lEHTLmv-ihY](https://www.youtube.com/watch?v=lEHTLmv-ihY) 云顶：帝国度假村能解决资金问题 \| 财经Espresso | 百格 Pocketimes | GENM | 2019-08-15 | 8924 | 4 | 4 | 4 | ok |
| [NMD_ao5TICk](https://www.youtube.com/watch?v=NMD_ao5TICk) Genting and its Empire | Edward Wong | UNKNOWN | 2019-08-14 | 530 | 0 | 0 | 0 | ok |
| [j4GMBxyO6-A](https://www.youtube.com/watch?v=j4GMBxyO6-A) Genting, conquering a losing Empire? | Edward Wong | UNKNOWN | 2019-08-09 | 1255 | 1 | 1 | 1 | ok |
| [GQokdpJ16mE](https://www.youtube.com/watch?v=GQokdpJ16mE) 乐园利多消散 云顶大马打回原形 \| 财经Espresso | 百格 Pocketimes | GENM | 2019-08-07 | 27849 | 8 | 8 | 8 | ok |
| [lA9oUUtW-po](https://www.youtube.com/watch?v=lA9oUUtW-po) EVENING 5: Genting M’sia sees RM2.6 bil wiped off in market cap | The Edge TV | UNKNOWN | 2019-08-07 | 11001 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [6-Th7mJLPc0](https://www.youtube.com/watch?v=6-Th7mJLPc0) 云顶 外资持股过高 | 南洋商报eNanyang | UNKNOWN | 2019-08-06 | 1090 | 0 | 0 | 0 | ok |
| [6BIK-MQO-gk](https://www.youtube.com/watch?v=6BIK-MQO-gk) 每日一股 one share one day（4715 GEM）8月4号 | 股哥说股@jeff | GENM | 2019-08-05 | 498 | 1 | 1 | 1 | ok |
| [fY7ZKLqjMAg](https://www.youtube.com/watch?v=fY7ZKLqjMAg) Genting, the Empire strikes back? | Edward Wong | UNKNOWN | 2019-07-28 | 604 | 0 | 0 | 0 | ok |
| [DZu45wHylnw](https://www.youtube.com/watch?v=DZu45wHylnw) 20190726  主题乐园准运营 云顶大马股价水涨船高 | 马新社电视华语新闻 Bernama TV Chinese | UNKNOWN | 2019-07-26 | 135 | 0 | 0 | 0 | ok |
| [EBlYo1nFJi4](https://www.youtube.com/watch?v=EBlYo1nFJi4) 霍士不玩 云顶乐园最快明年开张？\|Espresso | 百格 Pocketimes | GENM | 2019-07-24 | 17630 | 2 | 2 | 2 | ok |
| [0xGwBLJtKWI](https://www.youtube.com/watch?v=0xGwBLJtKWI) #股票投资理财 每日一股one share one day(Genm 4715)7月3日 | 股哥说股@jeff | GENM | 2019-07-03 | 470 | 0 | 0 | 0 | ok |
| [OaQEEiCLCp8](https://www.youtube.com/watch?v=OaQEEiCLCp8) 政府官司撤 云顶股价跌 \| 财经Espresso | 百格 Pocketimes | UNKNOWN | 2019-06-21 | 14785 | 7 | 7 | 7 | ok |
| [rC0_TpD6rtA](https://www.youtube.com/watch?v=rC0_TpD6rtA) 昨天第一轮 林国泰又减薪20% \| 财经Espresso | 百格 Pocketimes | UNKNOWN | 2019-06-20 | 12537 | 4 | 4 | 4 | ok |
| [Tn-lC4Gx_4I](https://www.youtube.com/watch?v=Tn-lC4Gx_4I) 股东：林国泰应减薪50% \| 财经Espresso | 百格 Pocketimes | GENM | 2019-06-19 | 15950 | 3 | 3 | 3 | ok |
| [7Pe0MGh3SAI](https://www.youtube.com/watch?v=7Pe0MGh3SAI) 天哥讲股--云顶大马【GENM】 | 全家私房钱 Money Money Home | GENM | 2019-05-02 | 42362 | 62 | 62 | 62 | ok |
| [ajeq4WmbET8](https://www.youtube.com/watch?v=ajeq4WmbET8) #JUSTSAYING: Why did Genting buy the Equanimity? | The Edge TV | UNKNOWN | 2019-04-10 | 36404 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [DJyoiYsyxrE](https://www.youtube.com/watch?v=DJyoiYsyxrE) EVENING 5: Genting folds hand on capex plans | The Edge TV | UNKNOWN | 2019-04-08 | 6045 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [CGi_egWYB4c](https://www.youtube.com/watch?v=CGi_egWYB4c) Malaysia 1MDB: Genting reportedly buys Jho Low's Equanimity yacht | YT Night News | UNKNOWN | 2019-04-07 | 44 | 0 | 0 | 0 | ok |
| [syVz56V2FME](https://www.youtube.com/watch?v=syVz56V2FME) Equanimity: Harga ditawar Genting terbaik | Astro AWANI | UNKNOWN | 2019-04-03 | 876 | 9 | 9 | 9 | ok |
| [D07Mcr_maKA](https://www.youtube.com/watch?v=D07Mcr_maKA) 云顶惨：新加坡赌场税将上调 \| 财经espresso | 百格 Pocketimes | GENM | 2019-04-03 | 16895 | 11 | 11 | 11 | ok |
| [X4rC4HcH_hs](https://www.youtube.com/watch?v=X4rC4HcH_hs) Kapal Equanimity Lonjak Saham Genting | Buletin TV3 | UNKNOWN | 2019-04-03 | 5688 | 8 | 8 | 8 | ok |
| [GhRO_dYBj6E](https://www.youtube.com/watch?v=GhRO_dYBj6E) Malaysia to sell 1MDB-linked superyacht to casino operator Genting for $170 million | Canada News | UNKNOWN | 2019-04-03 | 25 | 0 | 0 | 0 | ok |
| [4PsKXbqKrP8](https://www.youtube.com/watch?v=4PsKXbqKrP8) Genting buys Equanimity for US$126mil | The Star | UNKNOWN | 2019-04-03 | 5035 | 11 | 11 | 11 | ok |
| [KnlwpjHBC_I](https://www.youtube.com/watch?v=KnlwpjHBC_I) Genting Malaysia Bhd Beli Equanimity | Buletin TV3 | UNKNOWN | 2019-04-03 | 2961 | 16 | 16 | 16 | ok |
| [dzZY_IAf-xY](https://www.youtube.com/watch?v=dzZY_IAf-xY) 卖英国赌场 云顶套现1.9亿 \| 财经Espresso | 百格 Pocketimes | UNKNOWN | 2019-03-22 | 17966 | 10 | 10 | 10 | ok |
| [CB38-KfB_hs](https://www.youtube.com/watch?v=CB38-KfB_hs) 林国泰：爸爸说缴税好 \| 财经Espresso | 百格 Pocketimes | UNKNOWN | 2019-02-28 | 13738 | 14 | 14 | 14 | ok |
| [IVjZhDS4wOw](https://www.youtube.com/watch?v=IVjZhDS4wOw) 投资生命科学与生物科技已10年 云顶贡献医疗研发 | China Press 中國報 | UNKNOWN | 2019-02-28 | 9667 | 2 | 2 | 2 | ok |
| [OcsJTTdxbqw](https://www.youtube.com/watch?v=OcsJTTdxbqw) 云顶大马年入99亿 竟亏1959万！\| 财经Espresso | 百格 Pocketimes | UNKNOWN | 2019-02-27 | 12860 | 10 | 10 | 10 | ok |
| [zHhJjkc0vHA](https://www.youtube.com/watch?v=zHhJjkc0vHA) 云顶讨40亿 迪士尼只追2亿 \| 财经Espresso | 百格 Pocketimes | UNKNOWN | 2019-01-23 | 11227 | 3 | 3 | 3 | ok |
| [ArjZRhXz5Zc](https://www.youtube.com/watch?v=ArjZRhXz5Zc) Genting Bhd shares RISE within hours of my BUY call! =) | domperrier | GENTING | 2019-01-08 | 206 | 2 | 2 | 2 | ok |
| [DEge3h3WB9o](https://www.youtube.com/watch?v=DEge3h3WB9o) 雲頂 Genting Bhd(3182) BUY Call January 2019 (Technical Analysis) | domperrier | GENTING | 2019-01-07 | 1265 | 3 | 3 | 3 | ok |
| [DLW3HovRLm8](https://www.youtube.com/watch?v=DLW3HovRLm8) 美国结怨 永利赌场要拆云顶赌场 \| 财经Espresso | 百格 Pocketimes | UNKNOWN | 2018-12-26 | 32245 | 7 | 7 | 7 | ok |
| [Fbt-VR_j_x8](https://www.youtube.com/watch?v=Fbt-VR_j_x8) 不理米老鼠 云顶乐园明年初完工 \| 财经Espresso | 百格 Pocketimes | UNKNOWN | 2018-12-18 | 15925 | 9 | 9 | 9 | ok |
| [B6VjBb-SSVs](https://www.youtube.com/watch?v=B6VjBb-SSVs) GENM(4715)要等还是不要等?浅谈云顶大马 | Price Investment (Price投资研究) | UNKNOWN | 2018-12-09 | 5716 | 6 | 6 | 6 | ok |
| [EtggFauH0eE](https://www.youtube.com/watch?v=EtggFauH0eE) FRIDAY TAKEAWAY: Can Genting take on Disney? | The Edge TV | UNKNOWN | 2018-11-30 | 2326 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [cc2aDt_39EE](https://www.youtube.com/watch?v=cc2aDt_39EE) 市值单月蒸发逾83亿 云顶大马暴跌止血 | Few Hand新闻 | UNKNOWN | 2018-11-28 | 7 | 0 | 0 | 0 | ok |
| [kM6rAGZu5ww](https://www.youtube.com/watch?v=kM6rAGZu5ww) FOX：指控毫无根据 云顶股民没在怕 \| 财经Espresso | 百格 Pocketimes | UNKNOWN | 2018-11-28 | 31501 | 12 | 12 | 12 | ok |
| [7H7ryH39zzE](https://www.youtube.com/watch?v=7H7ryH39zzE) EVENING 5: Genting sues Fox, Disney for over US$1b | The Edge TV | GENTING | 2018-11-27 | 32072 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [e9QvFLCKFZo](https://www.youtube.com/watch?v=e9QvFLCKFZo) FOX主题乐园生变 云顶雪上加霜 \| 财经Espresso | 百格 Pocketimes | GENM | 2018-11-27 | 23232 | 15 | 15 | 15 | ok |
| [T4crUrIKT5M](https://www.youtube.com/watch?v=T4crUrIKT5M) 不收入场费 云顶：减行销费 | 百格 Pocketimes | UNKNOWN | 2018-11-07 | 25371 | 25 | 25 | 25 | ok |
| [MYZj0YCP-zk](https://www.youtube.com/watch?v=MYZj0YCP-zk) EVENING 5: Genting Malaysia hits limit down on Budget woes | The Edge TV | UNKNOWN | 2018-11-05 | 22674 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [-OAt6Wff8tw](https://www.youtube.com/watch?v=-OAt6Wff8tw) “贡献”不够？云顶预算案双重打击 \| 财经Espresso | 百格 Pocketimes | UNKNOWN | 2018-11-05 | 41545 | 43 | 43 | 43 | ok |
| [QqA1LQxZ4sY](https://www.youtube.com/watch?v=QqA1LQxZ4sY) Why Are Rating Agencies so Optimistic about Genting Berhad? Case Study Solution & Analysis | CaseAnalysisTeam com | GENTING | 2018-08-04 | 35 | — | 0 | 0 | comments_disabled: comment section unavailable (no comments or count; likely disabled) |
| [Kvn-U7z-ozA](https://www.youtube.com/watch?v=Kvn-U7z-ozA) Why invest in Genting?? | GUMINHO PRODUCTION | GENTING | 2018-07-08 | 23 | 0 | 0 | 0 | ok |
| [QESF1_1hSSg](https://www.youtube.com/watch?v=QESF1_1hSSg) 小股东：云顶年年赚钱应捐献国家 | 百格 Pocketimes | GENM | 2018-06-05 | 91838 | 83 | 83 | 83 | ok |
| [ZYZETxiuuq0](https://www.youtube.com/watch?v=ZYZETxiuuq0) 心碎澳门 林国泰一线梦难圆 | 百格 Pocketimes | UNKNOWN | 2018-03-23 | 14875 | 0 | 0 | 0 | ok |
| [ZxgyTSYfSCo](https://www.youtube.com/watch?v=ZxgyTSYfSCo) 林国泰云顶净利明跌暗升 | 百格 Pocketimes | UNKNOWN | 2018-02-27 | 11396 | 1 | 1 | 1 | ok |
| [Nl3AHQE-rH0](https://www.youtube.com/watch?v=Nl3AHQE-rH0) 缺钱？  传云顶卖英国赌场 | 百格 Pocketimes | GENM | 2017-09-26 | 10315 | 1 | 1 | 1 | ok |
| [hmmAsN6Ev_A](https://www.youtube.com/watch?v=hmmAsN6Ev_A) 林梧桐遗孀逝世 云顶股价下跌 | 百格 Pocketimes | UNKNOWN | 2017-08-25 | 24830 | 0 | 0 | 0 | ok |
| [7TJP2-qX07Q](https://www.youtube.com/watch?v=7TJP2-qX07Q) 林国泰当不成加拿大赌王 | 百格 Pocketimes | UNKNOWN | 2017-08-11 | 5702 | 0 | 0 | 0 | ok |
| [UyHYiinSH5Q](https://www.youtube.com/watch?v=UyHYiinSH5Q) 前进加拿大 林国泰放眼世界赌王 | 百格 Pocketimes | UNKNOWN | 2017-07-25 | 6511 | 0 | 0 | 0 | ok |
| [pSu388JHDMM](https://www.youtube.com/watch?v=pSu388JHDMM) 林国泰卖了地再卖股 | 百格 Pocketimes | GENTING | 2017-07-14 | 21248 | 0 | 0 | 0 | ok |
| [GNQclqfeDy0](https://www.youtube.com/watch?v=GNQclqfeDy0) 等转运  云顶印尼美国有麻烦 | 百格 Pocketimes | GENM | 2017-07-10 | 20056 | 1 | 1 | 1 | ok |
| [7lwefDkdetU](https://www.youtube.com/watch?v=7lwefDkdetU) 林国泰发功  云顶多赚3.6倍 | 百格 Pocketimes | UNKNOWN | 2017-05-29 | 11075 | 0 | 0 | 0 | ok |
| [MoDYXbdzDNs](https://www.youtube.com/watch?v=MoDYXbdzDNs) AEON不跟云顶买地！ | 百格 Pocketimes | GENTING | 2017-04-05 | 9873 | 0 | 0 | 0 | ok |
| [hDLHypgoZAY](https://www.youtube.com/watch?v=hDLHypgoZAY) 屡败屡战 云顶再进军医疗业 | 百格 Pocketimes | GENTING | 2017-04-04 | 5829 | 0 | 0 | 0 | ok |
| [TYjufaALK2o](https://www.youtube.com/watch?v=TYjufaALK2o) 云顶去年告美国政府 今年有望建酒店 | 百格 Pocketimes | UNKNOWN | 2017-03-20 | 6117 | 0 | 0 | 0 | ok |
| [AX95GDzg4wk](https://www.youtube.com/watch?v=AX95GDzg4wk) 云顶发债券筹44.6亿 | 百格 Pocketimes | GENTING | 2017-01-18 | 3838 | 1 | 1 | 1 | ok |
| [ZkZ0jn2bM1g](https://www.youtube.com/watch?v=ZkZ0jn2bM1g) 2019开张  云顶拉斯维加斯赌场将动工 | 百格 Pocketimes | UNKNOWN | 2017-01-11 | 7958 | 1 | 1 | 1 | ok |
| [esbDR9sV-ZY](https://www.youtube.com/watch?v=esbDR9sV-ZY) 云顶新赌场首季开张 | 百格 Pocketimes | GENM | 2017-01-04 | 52279 | 2 | 2 | 2 | ok |
| [_8954vYbiFg](https://www.youtube.com/watch?v=_8954vYbiFg) 云顶日本赌场梦碎？ | 百格 Pocketimes | UNKNOWN | 2016-12-07 | 9472 | 3 | 3 | 3 | ok |
| [_ZdsY9qyWLQ](https://www.youtube.com/watch?v=_ZdsY9qyWLQ) 陈志远暗批云顶 | 百格 Pocketimes | UNKNOWN | 2016-11-29 | 43241 | 4 | 4 | 4 | ok |
| [8bROaXauUjY](https://www.youtube.com/watch?v=8bROaXauUjY) Weekly iVSAChart Clinic – Be a Better Trader Campaign #2 (GDEX, Genting Malaysia and etc) | VSA Chart | UNKNOWN | 2016-11-04 | 209 | 0 | 0 | 0 | ok |

## Videos checked but not written as posts

| Video | Uploaded | Fetched comments | Reason |
| --- | --- | ---: | --- |
| [uTgj8qV7EcM](https://www.youtube.com/watch?v=uTgj8qV7EcM) 被美国合伙人索偿， 云顶大马股价创今年新低？ | 2024-10-16 | 14 | post already in `youtube_full.jsonl`; all fetched comments were already present there, so nothing was duplicated |
| [gnl60BjiWM4](https://www.youtube.com/watch?v=gnl60BjiWM4) GENTING 云顶: 业绩无力,股价疲弱!! [CC 中英文字幕 ENG SUB] | 2024-09-01 | 10 | post already in `youtube_full.jsonl`; all fetched comments were already present there, so nothing was duplicated |
| [OZ7mJgQK7Bs](https://www.youtube.com/watch?v=OZ7mJgQK7Bs) 【投资必知】看这三个数据就可以选到又快又稳的股票？！云顶股并没有想象中那么好？#SUNCON #GAMUDA #IJM #TENAGA #CIMB #GENTING #技术分析 | 2024-07-15 | 4 | post already in `youtube_full.jsonl`; all fetched comments were already present there, so nothing was duplicated |
| [lyn7g936dtI](https://www.youtube.com/watch?v=lyn7g936dtI) GENTING GENM 云顶傻傻分不清楚｜了解云顶的结构｜八卦大小文｜投资分享 | 2024-06-23 | 7 | post already in `youtube_full.jsonl`; all fetched comments were already present there, so nothing was duplicated |
| [bNaMnuWwTYY](https://www.youtube.com/watch?v=bNaMnuWwTYY) 云顶双雄股价下跌!?  最新的业绩到底说了什么？机会还是陷阱？10分钟带你了解你该不该投资! 【乐学成长空间 - LXInvest】 | 2024-06-07 | 25 | post already in `youtube_full.jsonl`; all fetched comments were already present there, so nothing was duplicated |
| [TMWFee7Lzh8](https://www.youtube.com/watch?v=TMWFee7Lzh8) GENTING 云顶: 业绩大好,应该可以带动股价! 阻力在那里？ | 2024-05-30 | 7 | post already in `youtube_full.jsonl`; all fetched comments were already present there, so nothing was duplicated |
| [fvqMRUrwwYc](https://www.youtube.com/watch?v=fvqMRUrwwYc) 旅游业大复苏，GENS大赚！云顶Genting Berhad要飞了？GENM & GENP也一起分析【理财投资】 ｜阿布abu | 2024-05-24 | 25 | post already in `youtube_full.jsonl`; all fetched comments were already present there, so nothing was duplicated |
| [a4cgwF3B3mU](https://www.youtube.com/watch?v=a4cgwF3B3mU) 【马股分析】云顶反弹7%，要进场吗？现在最赚钱的股票是什么？#马股 #GENTING #PBBANK #CAPITALA #BURSA | 2024-05-24 | 12 | post already in `youtube_full.jsonl`; all fetched comments were already present there, so nothing was duplicated |
| [z-ouqUfSzI0](https://www.youtube.com/watch?v=z-ouqUfSzI0) 【马股分析】为什么云顶股票表现不佳？哪些更好的股票选择？📊✅ #马股 #GENTING #RCL #LVS #AirBNB | 2024-05-06 | 8 | post already in `youtube_full.jsonl`; all fetched comments were already present there, so nothing was duplicated |
| [vQVnkeMgXFI](https://www.youtube.com/watch?v=vQVnkeMgXFI) GENTING 云顶 ： 股价跌跌不休,可否逢低买入长期持有？[CC 中英文字幕 ENG SUB]. | 2024-04-14 | 8 | post already in `youtube_full.jsonl`; all fetched comments were already present there, so nothing was duplicated |
| [ffuR_j3QswI](https://www.youtube.com/watch?v=ffuR_j3QswI) GENTING 云顶 RM0.09 股息 ex-date 之前,出现了熊指标. 午盘筹码峰技术分析.[CC 中英文字幕 ENG SUB].19032024 | 2024-03-19 | 6 | post already in `youtube_full.jsonl`; all fetched comments were already present there, so nothing was duplicated |
| [1l8b5-SJL_U](https://www.youtube.com/watch?v=1l8b5-SJL_U) 给我17分钟带你了解云顶集团 Genting Group 背后所有的上市公司 \| 股票投资 中文字幕 | 2024-02-27 | 18 | post already in `youtube_full.jsonl`; all fetched comments were already present there, so nothing was duplicated |
| [GY_TyCgLBnQ](https://www.youtube.com/watch?v=GY_TyCgLBnQ) 2024年最值得投资的2支股票！｜GENM 和 SIME 谁与争锋 ｜云顶大马｜Genting Malaysia 【理财投资】​⁠ ｜阿布 abu | 2024-02-24 | 68 | post already in `youtube_full.jsonl`; all fetched comments were already present there, so nothing was duplicated |
| [NIyv37O3KnE](https://www.youtube.com/watch?v=NIyv37O3KnE) GENM 子债母还!!?? 股价下跌背后的原因详细分析！机会还是陷阱!?! \| 【乐学成长空间 - LXInvest】 | 2024-01-19 | 29 | post already in `youtube_full.jsonl`; all fetched comments were already present there, so nothing was duplicated |
| [FiN-q0Se1xE](https://www.youtube.com/watch?v=FiN-q0Se1xE) GENM GENTING MALAYSIA 云顶大马-今年站上3块钱不是问题. 盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB]..07012024 | 2024-01-07 | 10 | post already in `youtube_full.jsonl`; all fetched comments were already present there, so nothing was duplicated |

## Largest comment threads

| Video | Ticker | Comments written |
| --- | --- | ---: |
| [fhyaYYAOh6A](https://www.youtube.com/watch?v=fhyaYYAOh6A) 云顶大马 Genting Malaysia \| 大马股票 \| 云顶大马现在很便宜？但是你敢买吗？\| 【乐学成长空间】 | UNKNOWN | 180 |
| [mEgyJkb-kFU](https://www.youtube.com/watch?v=mEgyJkb-kFU) 财经Espresso \| 新年开门  云顶多多万能"股涨" | GENTING | 161 |
| [DZ4SWfEiOXo](https://www.youtube.com/watch?v=DZ4SWfEiOXo) 财经Espresso \| 云顶爱尔兰公司清盘 | UNKNOWN | 132 |
| [Hph363QHTJM](https://www.youtube.com/watch?v=Hph363QHTJM) 财经Espresso \| 云顶双雄2020年亏损32.88亿 | GENTING | 130 |
| [_IqnMuBnU48](https://www.youtube.com/watch?v=_IqnMuBnU48) 【马股分析】全马最强现金流的公司？2021最有潜能复苏的公司？云顶集团最详细分析！GENTING \| 3182 [English CC] | UNKNOWN | 124 |
| [bG2DF8Mfsio](https://www.youtube.com/watch?v=bG2DF8Mfsio) 【马股分析】云顶大马最详细分析！疫情后王者归来？GENM \| 4715 [English CC] | UNKNOWN | 110 |
| [dOADROsOJ2o](https://www.youtube.com/watch?v=dOADROsOJ2o) 【马股分析】面对FMCO 云顶大马是否还能稳如泰山？GENM \| 4715 [ENGLISH CC] | GENM | 102 |
| [eltGJsaUzKc](https://www.youtube.com/watch?v=eltGJsaUzKc) 云顶集团的投资价值 vs 20年前的名胜世界，已今非昔比，而很多投资者仍蒙在鼓里... | UNKNOWN | 94 |
| [sRB9arN6lRA](https://www.youtube.com/watch?v=sRB9arN6lRA) MALAYSIA = FAILED STATE?, GENTING, SCIB \| FIRL Quick Dive | GENTING | 85 |
| [QESF1_1hSSg](https://www.youtube.com/watch?v=QESF1_1hSSg) 小股东：云顶年年赚钱应捐献国家 | GENM | 83 |
| [fSefdu62x6E](https://www.youtube.com/watch?v=fSefdu62x6E) "熊市定投计划"如何执行？云顶集团便宜过云顶大马？！【直播互动】【问答精华】 | UNKNOWN | 70 |
| [7Pe0MGh3SAI](https://www.youtube.com/watch?v=7Pe0MGh3SAI) 天哥讲股--云顶大马【GENM】 | GENM | 62 |
| [CJJ2e_UUnZ8](https://www.youtube.com/watch?v=CJJ2e_UUnZ8) CMCO让云顶赌场无法营业，GENM股票继续“大平卖”？ | UNKNOWN | 61 |
| [yGSqBuM210Q](https://www.youtube.com/watch?v=yGSqBuM210Q) 第九十三期：市场太烂，等机会吧！GENM, GENTING | UNKNOWN | 57 |
| [V7TOABCAp7M](https://www.youtube.com/watch?v=V7TOABCAp7M) 【马股分析】云顶大马最新财报速看！万众瞩目复苏股中的领头羊！？GENM \| 4715 [English CC] | UNKNOWN | 56 |

## Failures, quota errors and gaps

- **Quota errors:** none. No Data API key is configured, so no quota was consumed; the collector used yt-dlp scraping.
- **HTTP 429 / bot checks:** none recorded in the search or comment logs.
- **Unavailable/deleted candidates:** 5 of 630 metadata fetches returned no metadata (`BlxP_c69dso`, `m62nPMYhHrY`, `wVNY7bKPWa4`, `1NyBTyzMnV8`, `TqqQLMTqQL4`). They could not be included.
- **Zero comments fetched:** 175 of 549 selected videos. Of these, 30 explicitly returned no comment section/comment count (usually comments disabled); the rest legitimately have no comments. Posts are still written for all of them.
- `QqA1LQxZ4sY` (Why Are Rating Agencies so Optimistic about Genting Berhad? Case Study Solution & Analysis) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `MYZj0YCP-zk` (EVENING 5: Genting Malaysia hits limit down on Budget woes) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `7H7ryH39zzE` (EVENING 5: Genting sues Fox, Disney for over US$1b) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `EtggFauH0eE` (FRIDAY TAKEAWAY: Can Genting take on Disney?) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `DJyoiYsyxrE` (EVENING 5: Genting folds hand on capex plans) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `ajeq4WmbET8` (#JUSTSAYING: Why did Genting buy the Equanimity?) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `lA9oUUtW-po` (EVENING 5: Genting M’sia sees RM2.6 bil wiped off in market cap) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `Sx7afdkz5ZY` (EVENING 5: GenM seals RPT buy of Empire Resorts) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `7_-h3OFFS7U` (EVENING 5: Genting gets OK from Empire shareholders) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `rQk9YfjzmPM` (EVENING 5: Genting Malaysia to shed jobs) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `oNog951VNPI` (EVENING 5: Dividends still on the cards for Genting Malaysia) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `K8U-7V8VADM` (EVENING 5: Genting falls on knee-jerk reaction) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `K9f3m-IFS-M` (EVENING 5: Analysts wary of GenM and Empire’s stock subscription) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `_vSeDZvhk2U` (EVENING 5: Worst over for GenM, says RHB) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `DOErGnkuj4Q` (EVENING 5: Maybank sees wider loss for Genting Malaysia) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `43w5vcldp28` (EDGE WEEKLY: Genting’s big bet on Vegas) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `OENKDDuiWf4` (EVENING 5: Genting Skyworlds to open next month) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `DPx1QLm_YuM` (EVENING 5: Genting M’sia tipped to win full casino licence in New York) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `gc1byvvwDts` (EVENING 5: Omicron to weigh on Genting Malaysia — Maybank IB) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `6T1RTQ20pYw` (EVENING 5: Genting Malaysia expects RM4.29b from Miami deal) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `inCYOCw2U_U` (EVENING 5: Genting Malaysia’s Miami land sale falls through) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `cfBQH2nGUO0` (NEWS: King’s Park in Genting Highlands officially launched) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `y8wkNHNUoOQ` (EVENING 5: Genting Group earnings jump on post-pandemic recovery momentum) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `dnrdMZaJE_M` (EVENING 5: Genting bets big on overseas energy projects) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `TS8hZ3O5ba8` (NEWS: Genting’s energy division could contribute US$1.3 bil in revenue) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `CAGeXL00Re0` (NEWS: Genting to invest RM277 mil for another China power plant) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `Wu5UZyX1LT4` (NEWS: ‘Transformation of Genting is just starting’) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `Koz1Gq6g73M` (NEWS: Genting gives update on Alzheimer drug) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `UCCEudWGYnA` (EVENING 5: GenM unit named in US$600 mil lawsuit) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.
- `z1CSwnDajnA` (EVENING 5: Genting awards RM1.36 bil contracts for its FLNG project) — comment section unavailable (no comments or count; likely disabled); fetched 0 comments, 0 written; post written.

### Discovery gaps

YouTube search is relevance-ranked and caps a query at the requested result count (`ytsearch40` here), so it is a sample, not an exhaustive index. Old Malaysian retail stock videos are often unlisted, deleted, or titled only with Chinese characters and no Romanised company name; those cannot be recovered by keyword search. The pool was built from the queries above and their one-year windows; videos whose titles/descriptions do not mention Genting or a finance term were not fetched. Channel-scoped archive sweeps (as used for the 2024–2026 file) were not repeated for all 2016–2024 channels because the candidate pool already spans the window. Comment counts in video metadata are approximate and can lag; the fetched total is the authoritative count.

## Exclusions

Genting Highlands travel/theme-park/hotel/driving videos, casino-consumer and gambling vlogs, Kamen Rider `GenM`, Generation Mining (TSX:GENM), Genting Plantations (GENP), Genting Hong Kong and Genting Singapore-only (SGX:G13) analysis were excluded. Multi-stock market roundups were kept only when Genting was a named subject in the title or description. Videos about the Malaysian counters that also discuss Genting Singapore as a subsidiary/sister listing were kept when GENTING or GENM was the subject.

## Deduplication

The collector read the three existing YouTube files (never wrote them) and skipped any comment id already present there. 15 selected videos were already posts in `youtube_full.jsonl`; every comment fetched for them was already present in that file, so no record was duplicated. Records are deduplicated by `(source, native_id)` inside this file. Because comments were fetched for the whole thread, the comment date range can extend past 1 Nov 2024; those are comments on the 2016–2024 videos, not videos published after the window. They are labelled with `time_confidence="relative"` like every other comment.

