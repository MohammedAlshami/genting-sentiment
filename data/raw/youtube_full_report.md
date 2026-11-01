# YouTube full-window collection — Malaysian Genting

- **Collected:** 2 Nov 2026
- **Window:** 2 Nov 2024 → 2 Nov 2026 (inclusive; cutoff 3 Nov 2026 00:00 UTC)
- **Output:** `data/raw/youtube_full.jsonl`
- **Records:** 6013 — 94 posts, 5919 comments
- **Posts by ticker:** GENM × 24, GENTING × 31, UNKNOWN × 39
- **Comments by ticker:** GENM × 353, GENTING × 1352, UNKNOWN × 4214
- **Comment threads:** 3760 top-level comments, 2159 replies, 3849 distinct authors
- **Date range in file:** 2024-01-07 → 2026-11-01
- **Comment date range:** 2024-11-02 → 2026-11-01
- **Validation:** `python3 -m genting.validate data/raw/youtube_full.jsonl` → **OK, 0 errors, 18 warnings** (all warnings are pre-window uploads kept because they received in-window comments; explained below)

## Deduplication and scope

This file is **additive**: it contains only videos that were **not already present** in `data/raw/youtube.jsonl` (55 videos, 2 Nov 2025 → 2 Nov 2026) or `data/raw/youtube_2024-2025.jsonl` (129 videos, 2 Nov 2024 → 2 Nov 2025), both read at write time. 184 video ids were excluded for that reason. Combined, the three files cover 278 distinct videos. Nothing was re-fetched for the 184 existing videos, so this file is not a superset of their comment sections; it adds 94 new posts and their comment threads. Deduplication inside this file is by `(source, native_id)` for posts and comments.

Scope is Genting Berhad (`GENTING`, Bursa 3182) and Genting Malaysia (`GENM`, Bursa 4715) as listed securities. Excluded: Genting Highlands travel/theme-park/hotel/casino vlogs, Genting Singapore (SGX:G13) as the sole subject, Genting Plantations (GENP), Genting Hong Kong, Generation Mining (TSX:GENM, an unrelated ticker collision), student assignments, and generic multi-stock market roundups where Genting was not a leading segment.

## Method and discovery surface

Discovery ran in five passes, all through `yt-dlp`/YouTube search. Every query result was kept in a candidate pool with query provenance; relevance was decided only after full metadata (title, description, tags, upload date) was fetched. The pool is not a random sample: it is the union of 115 global queries, 20 deep queries, 20 upload-date-sorted searches, channel-scoped searches on 31 named market/news channels plus 77 channels that surfaced Genting content, and 138 playlists returned by YouTube's playlist-filtered search.

- Unique candidates in pool: **12,317**
- Passed the cheap title/description prefilter: **1,635**
- Metadata fetched overall: **1,302** (1,274 ok, 28 unavailable); this covers **1,175** of the 1,635 prefiltered candidates
- Prefiltered candidates left without metadata: **460** (mostly 2020–2023 archive videos from channel/playlist expansion; see gaps)
- Comment extractions attempted for this file: **98** videos (91 main + 7 channel-tail)
- Posts written: **94**; videos checked but not written: **4** (no in-window comments)

### Global queries (115 × `ytsearch50`)

```text
ytsearch50:genting stock
ytsearch50:genting share price
ytsearch50:genting berhad
ytsearch50:genting malaysia
ytsearch50:genting berhad stock analysis
ytsearch50:genting malaysia stock analysis
ytsearch50:GENM 4715
ytsearch50:GENTING 3182
ytsearch50:genting rights issue
ytsearch50:genting debt
ytsearch50:genting analysis
ytsearch50:genting dividend
ytsearch50:genting privatization
ytsearch50:genting privatisation
ytsearch50:genting New York casino
ytsearch50:genting results
ytsearch50:genting Q1 2025
ytsearch50:genting Q2 2025
ytsearch50:genting Q3 2025
ytsearch50:genting Q4 2025
ytsearch50:genting Q1 2026
ytsearch50:genting Q2 2026
ytsearch50:genting Q3 2026
ytsearch50:genting annual report
ytsearch50:genting share price crash
ytsearch50:genting stock drop
ytsearch50:genting buy or sell
ytsearch50:genting valuation
ytsearch50:genting cash call
ytsearch50:genting Miami land sale
ytsearch50:genting Empire Resorts
ytsearch50:genting Resorts World Las Vegas
ytsearch50:genting Malaysia casino licence
ytsearch50:genting Singapore stake
ytsearch50:genting Lim Kok Thay
ytsearch50:genting bond
ytsearch50:genting credit rating
ytsearch50:genting Moody's
ytsearch50:genting Fitch
ytsearch50:genting stock 2024
ytsearch50:genting stock 2025
ytsearch50:genting stock 2026
ytsearch50:GENM stock
ytsearch50:GENTING share
ytsearch50:genting group
ytsearch50:genting theme park
ytsearch50:genting casino Malaysia
ytsearch50:genting earnings
ytsearch50:genting revenue
ytsearch50:genting net loss
ytsearch50:genting restructuring
ytsearch50:genting sell-off
ytsearch50:genting shareholders
ytsearch50:genting AGM
ytsearch50:genting takeover
ytsearch50:genting offer
ytsearch50:genting minority shareholders
ytsearch50:saham genting
ytsearch50:analisa genting
ytsearch50:genting untung
ytsearch50:genting rugi
ytsearch50:genting jatuh
ytsearch50:genting naik
ytsearch50:harga saham genting
ytsearch50:genting berhad saham
ytsearch50:genting malaysia berhad
ytsearch50:genm saham
ytsearch50:genting beli atau jual
ytsearch50:genting dividen
ytsearch50:genting hak isu
ytsearch50:genting ambil alih
ytsearch50:genting berita
ytsearch50:saham genm jatuh
ytsearch50:analisis saham genting
ytsearch50:genting kongsi
ytsearch50:saham genting 2025
ytsearch50:saham genting 2026
ytsearch50:genting modal
ytsearch50:genting hutang
ytsearch50:genting untung 2025
ytsearch50:genting jual
ytsearch50:云顶 股票
ytsearch50:云顶大马
ytsearch50:云顶 分析
ytsearch50:云顶 债务
ytsearch50:云顶 附加股
ytsearch50:云顶 私有化
ytsearch50:云顶 财报
ytsearch50:云顶 业绩
ytsearch50:云顶 股息
ytsearch50:云顶 股价
ytsearch50:云顶 暴跌
ytsearch50:云顶 3182
ytsearch50:云顶大马 4715
ytsearch50:GENM 云顶
ytsearch50:GENTING 云顶
ytsearch50:云顶 纽约 赌场
ytsearch50:云顶 迈阿密
ytsearch50:林国泰 云顶
ytsearch50:云顶 债务危机
ytsearch50:云顶 集资
ytsearch50:云顶 附加股 2026
ytsearch50:云顶 私有化 2025
ytsearch50:云顶 大马
ytsearch50:云顶 集团
ytsearch50:云顶 股价 新低
ytsearch50:云顶 财报 2025
ytsearch50:云顶 业绩 2026
ytsearch50:云顶 分析 2025
ytsearch50:云顶 股票 分析
ytsearch50:云顶 还能买吗
ytsearch50:云顶 值得买吗
ytsearch50:云顶 反弹
ytsearch50:云顶 套牢
ytsearch50:云顶 附加股 2025
```

### Deep and date-sorted searches

`ytsearch100:` genting stock, genting malaysia, genting berhad, GENM 4715, GENTING 3182, genting rights issue, genting debt, genting analysis, genting dividend, genting privatization, saham genting, analisa genting, 云顶 股票, 云顶大马, 云顶 附加股, 云顶 私有化, 云顶 股价, genting crash, genting results, genting New York casino

The same 20 queries were also requested through YouTube's upload-date sort (`sp=CAI`) to catch recent low-view uploads that relevance ranking hid.

### Channel-scoped searches

Named channels searched with `genting`, `genm`, `云顶`, `3182` and `4715` (100 results per term): The Edge TV, The Edge Malaysia, InvestDummies, Y-Z Finance MY, Asri Ahmad Academy, Maher Saham, CGS International, UOB Kay Hian Malaysia, Maybank Investment Bank, Bursa Malaysia, TI 懂一点, Double Swords Investing, 大老板投资记录本, 八卦大小文的闲聊股市, 第一天投资理财研究所, 阿布的鸟公司, 股市先锋队, Nighteyes08, FIRL, AF's Notes, 我是雷公, Neo, Biz Editor, 大马财富故事, Ziet Invests, 八度空间华语新闻, MYtraderview, One Minute Finance, PERSENAN, Learn Gambling, Smartkarma, StubWorld.

In addition, every channel in the candidate pool with at least two Genting matches and a markets/news profile was searched for `genting` (100 results): 77 channels, listed below.

```text
百格 Pocketimes
The Edge TV
Double Swords 双剑论股
MYtraderview 大马股市技术分析交易 + 生活日志
Trading with KS
南洋商报eNanyang
股市先锋队
Buletin TV3
TI 懂一点
财经主编Neo
Astro AWANI
Berita RTM
JWen Soo
Nighteyes08
八度空间华语新闻
Bruce Investment
陈剑老师投资教育频道
大老板投资记录本
Investment Haus
Malaysia Money Matters
云顶全知道
SIAS
Business News
nerdbull1669 Trades and Thoughts
Smartkarma
牛转钱坤 Superbull
DagangNews
乐学成长空间 - LXInvest
TCYap马股投资
Ziet Invests
EL StockTrooper
金穗投资于生活
Y-Z Finance MY
阿布的鸟公司
Malaysia Stock Investment Analysis
Footprints of Smart Money
InvestKaki
双阳倍量 Double Volume Bullish Channel
domperrier
少爷兵
Andy Yew
大马股市分析
阿符的投资笔记
The Dividend Uncle
Joey Choy
Trade VSA
Iggy the Investing Iguana
严谈股市
Bloomberg Television
Kyle Livingston
10 Bagger Stocks Canada
CRAZII Market Talk With KEL
投资与财务
Robin Han
NCT Group of Companies 高裕轩集团有限公司
InvestDummies
Josh Tan - TheAstuteParent
Learn With Stanley
Ming Jong Tey - Wyckoff Method
The Business Times
Ryan Trader's Hub
Raymond
Harlem Tan
edgetv1
八卦大小文的闲聊股市
第一天投资理财研究所
WealthHero
GUMINHO PRODUCTION
I AM LEGEND
Crux Investor
Inside Asian Gaming
Zaidan Zainuddin
师奶股师
夜月投资
第一天乡下茶话会
Few Hand新闻
SK 投资空间
```

### Playlists

YouTube's playlist-filtered search (`sp=EgIQAw`) was queried for 8 core phrases; 138 unique playlists were expanded (up to 300 entries each). Most were generic Bursa/Malaysia stock playlists; they contributed long-tail episodes that the normal search ranking did not show.

Requests were sequential with a 1–2 s gap. No HTTP 429 or sign-in challenge was observed. Metadata-only fetches used `yt-dlp --skip-download --dump-json`; comment fetches used `yt-dlp --write-comments --skip-download`, which paginates comment continuations rather than taking only the first page.

## Comment timestamp precision

YouTube exposes comment age only as a relative label (`2 weeks ago`, `1 year ago`), not an absolute time. yt-dlp resolves each label to an estimated date at 00:00 UTC. Every comment keeps the original label in `raw.time_text`, and every reply carries `time_confidence="relative_month"`; the field is on replies as required by the task. These are day-level estimates, not exact publication times, and labels such as `1 year ago` span a range of months. No precision was invented. The window filter uses the estimates, so comments dated exactly 2 Nov 2024/2 Nov 2026 are boundary cases.

Because the labels are coarse, comments cluster on the same estimated day: the largest cluster is **3835 comments at 2025-12-02**, all carrying the same relative label. In particular, 285 comments labelled `2 years ago` resolve to the first day of the window (2 Nov 2024); the true dates could span late 2024 to late 2025. Sub-day timing inside a label bucket cannot be recovered from YouTube's public comment API.

## Videos collected

| Video | Channel | Ticker | Uploaded | Views | Comments (metadata) | In window | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| [e3UZGrF6GZg](https://www.youtube.com/watch?v=e3UZGrF6GZg) GENM GENTING MALAYSIA 云顶大马- 前有套牢盘挡路！ #马来西亚 #投資心法 #投資 #马股 #trading #领涨 #技术分析 | Double Swords Investing | UNKNOWN | 2026-10-31 | 2614 | 1 | 1 | ok |
| [4FuKBVLD4gc](https://www.youtube.com/watch?v=4FuKBVLD4gc) GENTING 云顶！连续上涨5天！要回调了吗? #马来西亚 #投資 #马股 #领涨 #投資心法 #trading #技术分析 | Double Swords Investing | GENTING | 2026-10-29 | 3875 | 1 | 1 | ok |
| [d9aTJ5Gu-7A](https://www.youtube.com/watch?v=d9aTJ5Gu-7A) 云顶向股东拿钱，惨遭市场无情抛售！GENM或有一风险？｜Zetrix危机越演越烈，被反贪会联手警察调查，债券现违约风险！｜华阳咖啡陷菜单风波、森那美被追税、CTOS被网络攻击股价暴跌！｜财经祥谈 | Neo, Biz Editor  | UNKNOWN | 2026-10-17 | 15627 | 12 | 12 | ok |
| [rfWaPFvMtgA](https://www.youtube.com/watch?v=rfWaPFvMtgA) #GENTING #大跌 #比刚才跌更多 #小股东怒了😡 | MYtraderview 大马股市技术分析交易 + 生活日志 | GENTING | 2026-10-12 | 379 | 0 | 0 | ok |
| [Ygjj0I938E8](https://www.youtube.com/watch?v=Ygjj0I938E8) Maybank cuts Genting to sell, Ethiopia's betting shutdown \| Gambling news 12 Oct 2026 | Learn Gambling | GENTING | 2026-10-12 | 48 | 0 | 0 | ok |
| [2GpqnuMTx6E](https://www.youtube.com/watch?v=2GpqnuMTx6E) #GENTING #GENM  #云顶双雄惨变云顶双熊 | MYtraderview 大马股市技术分析交易 + 生活日志 | UNKNOWN | 2026-10-12 | 92 | 0 | 0 | ok |
| [ub90Mnrpcvw](https://www.youtube.com/watch?v=ub90Mnrpcvw) 2027年财政预算案，团结政府放大招！人民有糖吃，企业却“薪“苦！｜顶级手套财报亮眼，营收盈利大涨，分析师却大泼冷水？｜龙马不精神，云顶联号公司恐面临除牌风险！｜财经祥谈 | Neo, Biz Editor  | UNKNOWN | 2026-10-10 | 6939 | 4 | 4 | ok |
| [xqIvHw0ujnE](https://www.youtube.com/watch?v=xqIvHw0ujnE) GENTING 云顶等第2支脚 #马来西亚 #马股 #技术分析 #云顶 #genting | Double Swords Investing | GENTING | 2026-09-24 | 3804 | 1 | 1 | ok |
| [z1eNVLae6wA](https://www.youtube.com/watch?v=z1eNVLae6wA) 云顶子公司债券被降至垃圾级！S&P：公司有“堕落天使”风险｜Zetrix坚持要高价收购菲律宾业务！旗下加密货币价格很不寻常？｜亚航又缺钱了！传政府或做担保人？｜财经祥谈 | Neo, Biz Editor  | UNKNOWN | 2026-09-12 | 10666 | 13 | 13 | ok |
| [46HDC6wYi9g](https://www.youtube.com/watch?v=46HDC6wYi9g) 大众银行香港子公司停牌超过1周！是出售还是私有化？｜云顶双雄Q2财报不甚理想？新加坡赌场竟或有续牌危机｜NexG狮子开大口：政府要收购请拿出75亿！｜财经祥谈 | Neo, Biz Editor  | UNKNOWN | 2026-08-29 | 8437 | 1 | 1 | ok |
| [HK1J2V0a88Y](https://www.youtube.com/watch?v=HK1J2V0a88Y) GENTING MALAYSIA Q2 2026 In 1 Min! 📊 \| NY Casino & Debt Risks! | Nighteyes08 | UNKNOWN | 2026-08-22 | 275 | 0 | 0 | ok |
| [5o9iWnSJxgE](https://www.youtube.com/watch?v=5o9iWnSJxgE) GENTING BERHAD暴跌到RM2.1,股价便宜了？投资接下来该怎么应对？庄家价格在哪里？#马股分析 #gentingberhad #云顶 #genting #genm #3182 | TI 懂一点 | UNKNOWN | 2026-08-08 | 3013 | 6 | 6 | ok |
| [KZJFDUxpSdQ](https://www.youtube.com/watch?v=KZJFDUxpSdQ) 云顶 GENM 4715 股价RM1.7算便宜了吗？#genm #云顶 #马股 #4715 #GentingHighlands #云顶股票 | TI 懂一点 | GENM | 2026-08-06 | 2727 | 0 | 0 | ok |
| [HVWBr6iqOjU](https://www.youtube.com/watch?v=HVWBr6iqOjU) 【直播】世界杯抢客影响赌场，云顶大马Q2可能陷入亏损？｜Tabung Haji皇家调查报告掀起千层浪，股市投资最大亏损达10亿却有政府打救！｜马来西亚雪邦再迎F1赛事｜财经祥谈（02/08/26） | Neo, Biz Editor  | GENM | 2026-08-03 | 1306 | 1 | 1 | ok |
| [QWTKt41C8CQ](https://www.youtube.com/watch?v=QWTKt41C8CQ) Billionaire Lim Kok Thay’s Genting Building New Hotel, Arena In $5.5 Billion New York Casino Push | Forbes | GENTING | 2026-07-28 | 34930 | 15 | 15 | ok |
| [0FQHdhac6iI](https://www.youtube.com/watch?v=0FQHdhac6iI) 20260718 Genting BHD 可以？AI双阳倍量教学课程04#不教玄学指标只讲能落地的盈利逻辑##双阳倍量  #技术分析 #trading #trending #倍量#ai #ai | 双阳倍量 Double Volume Bullish Channel  | GENTING | 2026-07-18 | 24 | 0 | 0 | ok |
| [GSJ4hcrvR-M](https://www.youtube.com/watch?v=GSJ4hcrvR-M) 20260717 Genting BHD 可以？AI双阳倍量教学课程04#不教玄学指标只讲能落地的盈利逻辑##双阳倍量  #技术分析 #trading #trending #倍量#ai #ai | 双阳倍量 Double Volume Bullish Channel  | GENTING | 2026-07-16 | 22 | 0 | 0 | ok |
| [SWrvAQDRqQU](https://www.youtube.com/watch?v=SWrvAQDRqQU) 投资者可以看GENM 了？股价趋势分析，庄家价位在哪里？#马股  #马来西亚股票 #genting #云顶 #genm #gentingmalaysia | TI 懂一点 | UNKNOWN | 2026-07-09 | 792 | 1 | 1 | ok |
| [AP7Nwmz2Gus](https://www.youtube.com/watch?v=AP7Nwmz2Gus) 云顶股东大会讯息爆棚，CEO竟说从未想要私有化云顶大马？｜登高处而不胜寒？TANCO单周市值蒸发百亿令吉！｜柔佛饼干公司HSS，卖年饼卖到上市！｜财经祥谈（13/06/26） | Neo, Biz Editor  | UNKNOWN | 2026-06-13 | 6525 | 14 | 14 | ok |
| [CqbdHIfu7uo](https://www.youtube.com/watch?v=CqbdHIfu7uo) MAYBANK首季财报不佳股价跌，云顶双雄一个亏一个大赚？｜陈志远、RHB纷纷退场，保险领域怎么了？｜面包店RT上市在即，华阳咖啡在烘培业也插一脚？｜财经祥谈（30/05/26） | Neo, Biz Editor  | UNKNOWN | 2026-05-30 | 4886 | 3 | 3 | ok |
| [Wou88wY4ZZs](https://www.youtube.com/watch?v=Wou88wY4ZZs) 马股大行情GENM股价趋势分析,庄家价位在哪里?#马股 #庄家 #genm #genting #云顶 | TI 懂一点 | UNKNOWN | 2026-05-30 | 672 | 0 | 0 | ok |
| [DzgQw9r3RUc](https://www.youtube.com/watch?v=DzgQw9r3RUc) 马股大行情GENTING股价趋势分析，庄家价位在哪里？#马股 #庄家 #genting #云顶 | TI 懂一点 | GENTING | 2026-05-23 | 742 | 1 | 1 | ok |
| [XVMPl05aqjw](https://www.youtube.com/watch?v=XVMPl05aqjw) E5: Genting 1Q profit surges, while GenM bleeds | The Edge TV | UNKNOWN | 2026-05-21 | 2215 | — | 0 | comment section unavailable (likely disabled) |
| [AdsvnNREkTQ](https://www.youtube.com/watch?v=AdsvnNREkTQ) 马股牛市大涨，GENTING，接下来会跟着上吗？注意这几点 #马股分析 #云顶 #genting #genm | TI 懂一点 | UNKNOWN | 2026-05-09 | 1657 | 2 | 2 | ok |
| [JHH3XRK55xk](https://www.youtube.com/watch?v=JHH3XRK55xk) 【独家】大马上市公司最高薪掌舵人，云顶林国泰去年喜提2亿薪酬！｜Padini被反贪会调查，大马时尚零售王者竟不是卖服装？｜东盟最大半导体IPO SkyeChip登场！｜财经祥谈（02/05/26） | Neo, Biz Editor  | UNKNOWN | 2026-05-02 | 4625 | 5 | 5 | ok |
| [zlVqagQXWag](https://www.youtube.com/watch?v=zlVqagQXWag) GENM股价反弹RM1.75-RM2.04 ，底部反弹了16%！接下来怎么看？#马股 #genm #云顶 #庄家 #股票分析 | TI 懂一点 | GENM | 2026-04-27 | 1063 | 1 | 1 | ok |
| [eRiTHPFaQVE](https://www.youtube.com/watch?v=eRiTHPFaQVE) Keuntungan bersih Genting Berhad susut 50 peratus | Astro AWANI | GENTING | 2026-04-20 | 291 | 0 | 0 | ok |
| [dfFC8xxF0tk](https://www.youtube.com/watch?v=dfFC8xxF0tk) GENM云顶私有化失败,接下来怎么看？  庄家价位在哪里？#马股 #genm #genting #云顶 #私有化 #庄家 | TI 懂一点 | UNKNOWN | 2026-04-09 | 1721 | 1 | 1 | ok |
| [dkeo5QFu0uw](https://www.youtube.com/watch?v=dkeo5QFu0uw) 云顶正在慢慢“老去”？大马赌场帝国背后的残酷经济现实 | 投资与财务 | GENTING | 2026-03-12 | 156050 | 229 | 229 | ok |
| [s1C6KRibltQ](https://www.youtube.com/watch?v=s1C6KRibltQ) GENTING 云顶 新的52周新低！可以去接刀吗？跌穿2.70. 筹码峰分析！中英字幕 ENG SUB. | Double Swords Investing | GENTING | 2026-03-03 | 1877 | 6 | 6 | ok |
| [xIhxttbFsEI](https://www.youtube.com/watch?v=xIhxttbFsEI) GENM 4715股价跌到这里反弹！庄家价位在 RM2? 是机会吗？#4715  #genm #genting #云顶 #马股 #庄家 #私有化 | TI 懂一点 | UNKNOWN | 2026-03-02 | 663 | 0 | 0 | ok |
| [tsg4D5203HI](https://www.youtube.com/watch?v=tsg4D5203HI) 27-2-2026 盘后浅谈 #KPJ 5878 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2026-03-01 | 56 | 1 | 1 | ok |
| [OzJiBiuJKKA](https://www.youtube.com/watch?v=OzJiBiuJKKA) 云顶家族又上演“溏心风暴”？最新财报亏损却依然宣布派息！｜消费类公司财报喜，马银行公布业绩后股价竟大跌！｜EPF  2025年派息6.15%，表现不如预期竟与令吉升值有关？｜财经祥谈（28/2/26） | Neo, Biz Editor  | GENTING | 2026-02-28 | 1257 | 1 | 1 | ok |
| [Iz4WpWaaWvg](https://www.youtube.com/watch?v=Iz4WpWaaWvg) GENM 4175 私有化失败，等下一轮?股价会反弹吗？投资者可以看？#马股 #genm #genting #云顶 #4175 | TI 懂一点 | UNKNOWN | 2026-01-23 | 1439 | 1 | 1 | ok |
| [e6nvtU5FVWw](https://www.youtube.com/watch?v=e6nvtU5FVWw) Gila!! Kasino Malaysia Runtuh dan anjlok 70%, Indonesia ikut rugi? | SAFRON (Safe Frontline) | GENTING | 2026-01-02 | 6763 | 49 | 49 | ok |
| [vOSTjBXzEIY](https://www.youtube.com/watch?v=vOSTjBXzEIY) Genting Malaysia’s ‘failed’ NY win | The Edge TV | UNKNOWN | 2025-12-31 | 5855 | — | 0 | comment section unavailable (likely disabled) |
| [Nkl96DNbPA4](https://www.youtube.com/watch?v=Nkl96DNbPA4) Kasino Malaysia Nyaris Bangkrut! Uang Judi Indonesia yang Menghidupi Negeri Tetangga | INFOIND | GENTING | 2025-12-29 | 114669 | 923 | 923 | ok |
| [Sh4X4zdst1s](https://www.youtube.com/watch?v=Sh4X4zdst1s) 云顶大马私有化，在2025十大财经新闻排名第三！ #财经新闻 #股市 #股票 #马股 #云顶 #genting #分析 #gentingmalaysia #财经评论 #2025 #回顾 #投资 | Neo, Biz Editor  | GENM | 2025-12-28 | 1020 | 0 | 0 | ok |
| [9sbT2hakPWc](https://www.youtube.com/watch?v=9sbT2hakPWc) 【2025年终回顾】十大财经新闻：云顶大马私有化排在第几名？｜十大马股之星：消费股成大赢家！｜十大财经风云人物：第一名果然是他！｜财经祥谈（27/12/25） | Neo, Biz Editor  | GENM | 2025-12-27 | 1015 | 0 | 0 | ok |
| [PL_QLD7nGes](https://www.youtube.com/watch?v=PL_QLD7nGes) 云顶大动作， GENM 私有化计划全解析 （部分精华版） | 第一天乡下茶话会 | GENM | 2025-12-12 | 4 | 0 | 0 | ok |
| [RLxJlnUkFE0](https://www.youtube.com/watch?v=RLxJlnUkFE0) 云顶大马私有化失败，赢得纽约赌牌股价不起反跌！｜汽车领域重磅消息，Bermaz Auto和KIA分手，Perodua推电动车！｜新加坡GXS裁员，大马数字银行前景如何？｜财经祥谈（06/12/25） | Neo, Biz Editor  | GENM | 2025-12-06 | 4302 | 0 | 0 | ok |
| [LvRMBu1DLjc](https://www.youtube.com/watch?v=LvRMBu1DLjc) 云顶大马私有化失败后😐云顶可以有的其他选项 🫢Tony 是财技高手 👏🏿CAPITAL A-LA 涨停板 👍🏿 分享 CAPITAL A分了AAX后😵‍💫的情况  -【阿Kya聊聊 - 021225】 | 金穗投资于生活 | GENM | 2025-12-02 | 5829 | 40 | 40 | ok |
| [c86ODJf2jFE](https://www.youtube.com/watch?v=c86ODJf2jFE) Saham Genting Ambruk 70%! Ironi Perbincangan Dana Indonesia di Balik Kasino Malaysia | Titik Jejak | UNKNOWN | 2025-11-30 | 3979 | 25 | 25 | ok |
| [hcC80TYxOjQ](https://www.youtube.com/watch?v=hcC80TYxOjQ) 云顶双雄净利大跌，竟然与令吉升值有关？｜郭鹤年旗下丰益再惹官非，PPB第三季业绩亏损！｜传统媒体亏损连连， 美食自媒体上市却受追捧！｜财经祥谈（29/11/25） | Neo, Biz Editor  | GENM | 2025-11-29 | 1116 | 2 | 2 | ok |
| [cec8OFYTN8U](https://www.youtube.com/watch?v=cec8OFYTN8U) IRONIS! Malaysia Kuasai 50% Listrik RI dari Bisnis Judi?! Saham Genting Ambruk 70%! | Bennix | UNKNOWN | 2025-11-26 | 388079 | 3901 | 3901 | ok |
| [0qnp-o2rDyY](https://www.youtube.com/watch?v=0qnp-o2rDyY) 《+1财经》赌牌路费小药丸 能救下云顶吗？ | 百格 Pocketimes | GENM | 2025-11-24 | 28072 | 47 | 47 | ok |
| [09O53Rp23NY](https://www.youtube.com/watch?v=09O53Rp23NY) 《财经随便聊》大马数据中心崛起! 马币走强!? 云顶大马 LOGO私有化进展！#podcast | Finance Lang | GENM | 2025-11-22 | 26869 | 45 | 45 | ok |
| [ZQdaX-32Rz0](https://www.youtube.com/watch?v=ZQdaX-32Rz0) 独立顾问说“No”! 散户能阻挡私有化大局吗?｜云顶大马: 12月1日的终极对决【谈股论今313】 | 陈剑老师投资教育频道 | GENM | 2025-11-21 | 16835 | 42 | 42 | ok |
| [s_6utmWR-_g](https://www.youtube.com/watch?v=s_6utmWR-_g) EDGE WEEKLY: Genting — a delicate balancing act between rising debt and growing reach | The Edge TV | UNKNOWN | 2025-11-20 | 815 | — | 0 | comment section unavailable (likely disabled) |
| [RcjWVhaFKBc](https://www.youtube.com/watch?v=RcjWVhaFKBc) 云顶私有化终局战：不公平、不合理？背后真相一次讲！｜第一天乡下茶话会 | 第一天投资理财研究所 | GENM | 2025-11-17 | 9886 | 28 | 28 | ok |
| [w0lr9txclcM](https://www.youtube.com/watch?v=w0lr9txclcM) 云顶大马私有化凉了？独立顾问：收购价不公平不合理！｜双威IJM又传合并，强强联手挑战GAMUDA？｜华文报业大亨离世，旗下公司股价又异动？｜财经祥谈（16/11/25） | Neo, Biz Editor  | GENM | 2025-11-16 | 2981 | 1 | 1 | ok |
| [lbv7QxEslO4](https://www.youtube.com/watch?v=lbv7QxEslO4) 14-11-2025 盘中浅谈 #MI 5286 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2025-11-14 | 124 | 2 | 2 | ok |
| [Azei7IGpD_E](https://www.youtube.com/watch?v=Azei7IGpD_E) 13-11-2025 盘中浅谈 #TCHONG 4405 #GENTING 3182 \| 马股 | 股市先锋队 | GENTING | 2025-11-13 | 133 | 1 | 1 | ok |
| [0wOv8Hqwkh0](https://www.youtube.com/watch?v=0wOv8Hqwkh0) Ahli Parlimen Bakri persoal turun naik luar biasa saham Genting Malaysia, gesa siasatan telus | DagangNews | UNKNOWN | 2025-11-06 | 55 | 0 | 0 | ok |
| [PzgrX4XD_p8](https://www.youtube.com/watch?v=PzgrX4XD_p8) 马股今天力排众议上涨1点 但是小股其实不美 🥲详细讲解云顶大马GENM“无条件”私有化真正的意识 🎰分享LCTITAN财报发现的端倪 🧐 - 【阿Kya聊聊 - 041125】 | 金穗投资于生活 | GENM | 2025-11-04 | 3723 | 26 | 26 | ok |
| [dYSV8GXdGuM](https://www.youtube.com/watch?v=dYSV8GXdGuM) Genting share🚀genting share price🚀genting berhad share price | APNA MARKET NEWS | GENTING | 2025-10-16 | 13 | 0 | 0 | ok |
| [EwKoGKRLIEY](https://www.youtube.com/watch?v=EwKoGKRLIEY) Genting Malaysia (GENM MK): Genting (GENT MK)'s Curious Offer | Smartkarma | UNKNOWN | 2025-10-15 | 32 | 0 | 0 | ok |
| [ouq8GSf6wGM](https://www.youtube.com/watch?v=ouq8GSf6wGM) E5: Analysts are split on Genting Malaysia takeover | The Edge TV | UNKNOWN | 2025-10-14 | 3374 | — | 0 | comment section unavailable (likely disabled) |
| [AgFy588WiNQ](https://www.youtube.com/watch?v=AgFy588WiNQ) 🇲🇾 Genting Buyout: What It Means for SG Investors #shorts \| 🦖 #InvestingIguana | Iggy the Investing Iguana | UNKNOWN | 2025-10-13 | 2709 | 6 | 6 | ok |
| [6bXa2gToYSA](https://www.youtube.com/watch?v=6bXa2gToYSA) 狠砸67亿收购云顶大马 云顶集团目的何在？ | 百格 Pocketimes | UNKNOWN | 2025-10-13 | 31227 | 28 | 28 | ok |
| [jur6jiNlupo](https://www.youtube.com/watch?v=jur6jiNlupo) E5: Genting privatises Genting Malaysia for RM6.7 bil | The Edge TV | UNKNOWN | 2025-10-13 | 6689 | — | 0 | comment section unavailable (likely disabled) |
| [8ae7GY2VOQc](https://www.youtube.com/watch?v=8ae7GY2VOQc) 云顶有隐忧？2026财政预算案会不会找博彩业开刀？ #马股投资 #budget2026 #云顶 #genting #gentingmalaysia #博彩 #财经 #股市 #马股 #万能 #多多 | Neo, Biz Editor  | UNKNOWN | 2025-10-04 | 865 | 0 | 0 | ok |
| [0p3Z8jqe6cA](https://www.youtube.com/watch?v=0p3Z8jqe6cA) Genting Berhad Q2 2025 (Aug-25) \| Can Long-Term Bets Spark a Turnaround? | Nighteyes08 | GENTING | 2025-09-02 | 148 | 1 | 1 | ok |
| [An_UyYtMPfs](https://www.youtube.com/watch?v=An_UyYtMPfs) 云顶集团 , 现在能抄底吗？20250827 | Robin Han | GENTING | 2025-08-28 | 1184 | 0 | 0 | ok |
| [oR01lNWc530](https://www.youtube.com/watch?v=oR01lNWc530) E5: Genting’s 1Q net profit plummets 99% | The Edge TV | GENTING | 2025-05-29 | 3915 | — | 0 | comment section unavailable (likely disabled) |
| [79bONSD30zQ](https://www.youtube.com/watch?v=79bONSD30zQ) 2025年跌出十大富豪榜：云顶集团掌舵人林国泰 \| 新闻报报看 17/04/2025 | Astro 本地圈 | GENTING | 2025-04-17 | 37482 | 63 | 63 | ok |
| [tJoYPQbhJxU](https://www.youtube.com/watch?v=tJoYPQbhJxU) 林氏父子频频增持股权！云顶翻身时机到了？ | Neo, Biz Editor  | GENTING | 2025-04-04 | 4519 | 0 | 0 | ok |
| [Rpt4krp2MhM](https://www.youtube.com/watch?v=Rpt4krp2MhM) 林国泰辞去首席执行官一职！ 云顶新CEO是何方神圣？ | Neo, Biz Editor  | GENTING | 2025-03-22 | 18403 | 7 | 7 | ok |
| [xEfEAKcbqt0](https://www.youtube.com/watch?v=xEfEAKcbqt0) 【快速解盘】GENM 今天破低是不好 ! 但是否就不能玩了 ？目前该如何看呢 ?@mytraderview | MYtraderview 大马股市技术分析交易 + 生活日志 | GENM | 2025-03-11 | 1501 | 15 | 15 | ok |
| [hi6z7UTSRLs](https://www.youtube.com/watch?v=hi6z7UTSRLs) Genting (3182) Stock Drops Big! Is It Time to Buy or Will It Fall Further? | SwiftScalper | GENTING | 2025-03-03 | 159 | 0 | 0 | ok |
| [77UvNuBOlfQ](https://www.youtube.com/watch?v=77UvNuBOlfQ) 【形态解读】GENM 周五股价暴跌后，几时可捞底 ?#shorts@mytraderview | MYtraderview 大马股市技术分析交易 + 生活日志 | GENM | 2025-03-03 | 109 | 1 | 1 | ok |
| [FZE34NOnreg](https://www.youtube.com/watch?v=FZE34NOnreg) 【形态解读】GENM 周五股价暴跌后，几时可捞底 ?@mytraderview | MYtraderview 大马股市技术分析交易 + 生活日志 | GENM | 2025-03-02 | 1327 | 17 | 17 | ok |
| [JHRo8ru1Ugg](https://www.youtube.com/watch?v=JHRo8ru1Ugg) Daily KLSE BURSA UPDATE - 28-2-2025 💥MRCB WINS LRT3 CONTRACT WORTH RM2.47b💥GENTING GENM SHARE FALL💥 | Trading with KS | UNKNOWN | 2025-02-28 | 809 | 4 | 4 | ok |
| [Ezrxtfrm7dU](https://www.youtube.com/watch?v=Ezrxtfrm7dU) 【形态解读】GENTING 周五突然大起17分！是不是要回来了 ？@mytraderview | MYtraderview 大马股市技术分析交易 + 生活日志 | GENTING | 2025-02-16 | 1176 | 3 | 3 | ok |
| [zJXEe_CoUNg](https://www.youtube.com/watch?v=zJXEe_CoUNg) GENM 云顶大马冲高回落,回调买上涨! | Double Swords Investing | GENM | 2024-11-29 | 4276 | 16 | 16 | ok |
| [uTgj8qV7EcM](https://www.youtube.com/watch?v=uTgj8qV7EcM) 被美国合伙人索偿， 云顶大马股价创今年新低？ | 陈剑老师投资教育频道 | GENM | 2024-10-16 | 13585 | 14 | 14 | ok |
| [gnl60BjiWM4](https://www.youtube.com/watch?v=gnl60BjiWM4) GENTING 云顶: 业绩无力,股价疲弱!! [CC 中英文字幕 ENG SUB] | Double Swords Investing | GENTING | 2024-09-01 | 3226 | 10 | 10 | ok |
| [OZ7mJgQK7Bs](https://www.youtube.com/watch?v=OZ7mJgQK7Bs) 【投资必知】看这三个数据就可以选到又快又稳的股票？！云顶股并没有想象中那么好？#SUNCON #GAMUDA #IJM #TENAGA #CIMB #GENTING #技术分析 | Andy Yew | GENTING | 2024-07-15 | 4671 | 4 | 4 | ok |
| [lyn7g936dtI](https://www.youtube.com/watch?v=lyn7g936dtI) GENTING GENM 云顶傻傻分不清楚｜了解云顶的结构｜八卦大小文｜投资分享 | 八卦大小文的闲聊股市 | UNKNOWN | 2024-06-23 | 4864 | 7 | 7 | ok |
| [bNaMnuWwTYY](https://www.youtube.com/watch?v=bNaMnuWwTYY) 云顶双雄股价下跌!?  最新的业绩到底说了什么？机会还是陷阱？10分钟带你了解你该不该投资! 【乐学成长空间 - LXInvest】 | 乐学成长空间 - LXInvest | GENM | 2024-06-07 | 15206 | 25 | 25 | ok |
| [FsQQHI-Qj5I](https://www.youtube.com/watch?v=FsQQHI-Qj5I) GENM GENTING MALAYSIA 云顶大马: 盈利 vs 净营业现金流. 支撑价位在那里？ | Double Swords Investing | UNKNOWN | 2024-06-01 | 5272 | 6 | 6 | ok |
| [TMWFee7Lzh8](https://www.youtube.com/watch?v=TMWFee7Lzh8) GENTING 云顶: 业绩大好,应该可以带动股价! 阻力在那里？ | Double Swords Investing | GENTING | 2024-05-30 | 4069 | 7 | 7 | ok |
| [fvqMRUrwwYc](https://www.youtube.com/watch?v=fvqMRUrwwYc) 旅游业大复苏，GENS大赚！云顶Genting Berhad要飞了？GENM & GENP也一起分析【理财投资】 ｜阿布abu | 阿布的鸟公司 | UNKNOWN | 2024-05-24 | 12666 | 25 | 25 | ok |
| [a4cgwF3B3mU](https://www.youtube.com/watch?v=a4cgwF3B3mU) 【马股分析】云顶反弹7%，要进场吗？现在最赚钱的股票是什么？#马股 #GENTING #PBBANK #CAPITALA #BURSA | Andy Yew | UNKNOWN | 2024-05-24 | 9581 | 12 | 12 | ok |
| [z-ouqUfSzI0](https://www.youtube.com/watch?v=z-ouqUfSzI0) 【马股分析】为什么云顶股票表现不佳？哪些更好的股票选择？📊✅ #马股 #GENTING #RCL #LVS #AirBNB | Andy Yew | GENTING | 2024-05-06 | 12129 | 8 | 8 | ok |
| [Vt_3YMmmUZI](https://www.youtube.com/watch?v=Vt_3YMmmUZI) GENM GENTING MALAYSIA - 不变应万变! [CC 中英字幕 ENG SUB] | Double Swords Investing | UNKNOWN | 2024-04-28 | 4476 | 4 | 4 | ok |
| [vQVnkeMgXFI](https://www.youtube.com/watch?v=vQVnkeMgXFI) GENTING 云顶 ： 股价跌跌不休,可否逢低买入长期持有？[CC 中英文字幕 ENG SUB]. | Double Swords Investing | GENTING | 2024-04-14 | 5208 | 8 | 8 | ok |
| [ffuR_j3QswI](https://www.youtube.com/watch?v=ffuR_j3QswI) GENTING 云顶 RM0.09 股息 ex-date 之前,出现了熊指标. 午盘筹码峰技术分析.[CC 中英文字幕 ENG SUB].19032024 | Double Swords Investing | GENTING | 2024-03-19 | 4101 | 6 | 6 | ok |
| [1l8b5-SJL_U](https://www.youtube.com/watch?v=1l8b5-SJL_U) 给我17分钟带你了解云顶集团 Genting Group 背后所有的上市公司 \| 股票投资 中文字幕 | 师奶股师 | UNKNOWN | 2024-02-27 | 10086 | 18 | 18 | ok |
| [GY_TyCgLBnQ](https://www.youtube.com/watch?v=GY_TyCgLBnQ) 2024年最值得投资的2支股票！｜GENM 和 SIME 谁与争锋 ｜云顶大马｜Genting Malaysia 【理财投资】​⁠ ｜阿布 abu | 阿布的鸟公司 | UNKNOWN | 2024-02-24 | 21350 | 68 | 68 | ok |
| [kmSfsXLo1F8](https://www.youtube.com/watch?v=kmSfsXLo1F8) GENTING 云顶 - 业绩公布前会站上5块钱吗？盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB].04022024 | Double Swords Investing | GENTING | 2024-02-04 | 3123 | 8 | 8 | ok |
| [GyH3s4kcuRs](https://www.youtube.com/watch?v=GyH3s4kcuRs) GENTING竟然这么便宜?！点进来看看这个超值大揭秘 \| 你敢不敢买?! 【乐学成长空间 - LXInvest】 | 乐学成长空间 - LXInvest | UNKNOWN | 2024-02-02 | 25846 | 36 | 36 | ok |
| [NIyv37O3KnE](https://www.youtube.com/watch?v=NIyv37O3KnE) GENM 子债母还!!?? 股价下跌背后的原因详细分析！机会还是陷阱!?! \| 【乐学成长空间 - LXInvest】 | 乐学成长空间 - LXInvest | GENM | 2024-01-19 | 14474 | 29 | 29 | ok |
| [FiN-q0Se1xE](https://www.youtube.com/watch?v=FiN-q0Se1xE) GENM GENTING MALAYSIA 云顶大马-今年站上3块钱不是问题. 盘后筹码峰技术分析.[CC 中英文字幕 ENG SUB]..07012024 | Double Swords Investing | UNKNOWN | 2024-01-07 | 4328 | 10 | 10 | ok |

## Largest comment threads

| Video | Ticker | Comments in window |
| --- | --- | ---: |
| [cec8OFYTN8U](https://www.youtube.com/watch?v=cec8OFYTN8U) IRONIS! Malaysia Kuasai 50% Listrik RI dari Bisnis Judi?! Saham Genting Ambruk 70%! | UNKNOWN | 3901 |
| [Nkl96DNbPA4](https://www.youtube.com/watch?v=Nkl96DNbPA4) Kasino Malaysia Nyaris Bangkrut! Uang Judi Indonesia yang Menghidupi Negeri Tetangga | GENTING | 923 |
| [dkeo5QFu0uw](https://www.youtube.com/watch?v=dkeo5QFu0uw) 云顶正在慢慢“老去”？大马赌场帝国背后的残酷经济现实 | GENTING | 229 |
| [GY_TyCgLBnQ](https://www.youtube.com/watch?v=GY_TyCgLBnQ) 2024年最值得投资的2支股票！｜GENM 和 SIME 谁与争锋 ｜云顶大马｜Genting Malaysia 【理财投资】​⁠ ｜阿布 abu | UNKNOWN | 68 |
| [79bONSD30zQ](https://www.youtube.com/watch?v=79bONSD30zQ) 2025年跌出十大富豪榜：云顶集团掌舵人林国泰 \| 新闻报报看 17/04/2025 | GENTING | 63 |
| [e6nvtU5FVWw](https://www.youtube.com/watch?v=e6nvtU5FVWw) Gila!! Kasino Malaysia Runtuh dan anjlok 70%, Indonesia ikut rugi? | GENTING | 49 |
| [0qnp-o2rDyY](https://www.youtube.com/watch?v=0qnp-o2rDyY) 《+1财经》赌牌路费小药丸 能救下云顶吗？ | GENM | 47 |
| [09O53Rp23NY](https://www.youtube.com/watch?v=09O53Rp23NY) 《财经随便聊》大马数据中心崛起! 马币走强!? 云顶大马 LOGO私有化进展！#podcast | GENM | 45 |
| [ZQdaX-32Rz0](https://www.youtube.com/watch?v=ZQdaX-32Rz0) 独立顾问说“No”! 散户能阻挡私有化大局吗?｜云顶大马: 12月1日的终极对决【谈股论今313】 | GENM | 42 |
| [LvRMBu1DLjc](https://www.youtube.com/watch?v=LvRMBu1DLjc) 云顶大马私有化失败后😐云顶可以有的其他选项 🫢Tony 是财技高手 👏🏿CAPITAL A-LA 涨停板 👍🏿 分享 CAPITAL A分了AAX后😵‍💫的情况  -【阿Kya聊聊 - 021225】 | GENM | 40 |
| [GyH3s4kcuRs](https://www.youtube.com/watch?v=GyH3s4kcuRs) GENTING竟然这么便宜?！点进来看看这个超值大揭秘 \| 你敢不敢买?! 【乐学成长空间 - LXInvest】 | UNKNOWN | 36 |
| [NIyv37O3KnE](https://www.youtube.com/watch?v=NIyv37O3KnE) GENM 子债母还!!?? 股价下跌背后的原因详细分析！机会还是陷阱!?! \| 【乐学成长空间 - LXInvest】 | GENM | 29 |

## Checked but not written

| Video | Uploaded | Reason |
| --- | --- | --- |
| [UCCEudWGYnA](https://www.youtube.com/watch?v=UCCEudWGYnA) EVENING 5: GenM unit named in US$600 mil lawsuit | 2024-10-14 | pre-window upload with no comment in the 2-year window |
| [KPNvs2Vg1rs](https://www.youtube.com/watch?v=KPNvs2Vg1rs) GENM 4715 你会投资老牌王国吗？ | 2024-05-17 | pre-window upload with no comment in the 2-year window |
| [cOjvRa8Qk4A](https://www.youtube.com/watch?v=cOjvRa8Qk4A) 云顶美国赌城遭一个投诉 市值即失守170亿 | 2024-08-19 | pre-window upload with no comment in the 2-year window |
| [TS8hZ3O5ba8](https://www.youtube.com/watch?v=TS8hZ3O5ba8) NEWS: Genting’s energy division could contribute US$1.3 bil in revenue | 2024-06-20 | pre-window upload with no comment in the 2-year window |

## Failures and gaps

- **Unavailable videos:** 28 candidates returned `This video is not available` and were skipped (deleted/private). They are not counted as videos.
- **Comment section unavailable (likely disabled):** 8 videos (6 in-window posts written with zero comments, plus 2 pre-window videos that were checked but not written):
  - `XVMPl05aqjw` — E5: Genting 1Q profit surges, while GenM bleeds
  - `ouq8GSf6wGM` — E5: Analysts are split on Genting Malaysia takeover
  - `jur6jiNlupo` — E5: Genting privatises Genting Malaysia for RM6.7 bil
  - `vOSTjBXzEIY` — Genting Malaysia’s ‘failed’ NY win
  - `s_6utmWR-_g` — EDGE WEEKLY: Genting — a delicate balancing act between rising debt and growing reach
  - `oR01lNWc530` — E5: Genting’s 1Q net profit plummets 99%
  - `UCCEudWGYnA` — EVENING 5: GenM unit named in US$600 mil lawsuit
  - `TS8hZ3O5ba8` — NEWS: Genting’s energy division could contribute US$1.3 bil in revenue
- **Zero-comment posts with comments enabled:** 21. They are kept as posts because they are part of the in-window Genting coverage; YouTube returned no comments, which is a real result, not a failure.
- **Comment extraction errors:** none. Every selected video that had a comment section returned metadata and comments.
- **Metadata not fetched for 460 prefiltered candidates.** These are almost all 2020–2023 archive videos surfaced by channel/playlist expansion. The subset whose titles carried a 2024–2026 date was checked separately (47 videos; 7 added). The rest would only qualify through comments in the window, and pre-2024 uploads were not comment-checked (see below).
- **Pre-2024 uploads were not comment-checked.** 23 pre-window videos uploaded in 2024 were checked and 19 had in-window comments; videos uploaded before 2024 were not re-checked in this pass. The existing `youtube.jsonl` and `youtube_2024-2025.jsonl` already cover 184 videos, including representative older uploads.
- **Search surface.** YouTube search returns at most ~100 results per query and personalises/ranks by relevance; 115 queries × 50 plus 20 × 100 is broad but cannot be proven to be the entire upload universe. Very low-view videos with no Genting keyword in title/description are the most likely omission.
- **Comment completeness.** YouTube omits deleted comments, comments held for review, and some comments on age-restricted videos. `comment_count` is approximate and can include replies that the extractor could not page to. Fetched counts are the authoritative measure of what was publicly retrievable; nothing was invented or padded.
- **Duplicate body texts:** 126 replies repeat another comment's exact text (short reactions, emoji, creator boilerplate). They are distinct comment ids and were kept.
- **Validator warnings (18).** Nineteen posts were uploaded before 2 Nov 2024 but drew comments inside the window; they are deliberately kept with their original upload dates. The validator's floor is 1 Oct 2024, so 2024 uploads before that date warn. Pre-window posts with no in-window comments were not written.

## Participation and language

21 comments are pinned and 178 are by the video uploader. The file is multilingual (English, Malay, Chinese, Indonesian); `lang` is left null because the collector does not run language detection on individual comments. Ticker `UNKNOWN` means the video covers both counters or does not make the parent/subsidiary distinction; it is not a missing value.

## Collection date coverage

Posts range from 7 Jan 2024 to 31 Oct 2026. Comments range from 2 Nov 2024 to 1 Nov 2026. The asymmetry at the start is intentional: an older video is included only when it received at least one comment inside the window. The 2024 posts are mostly January–October 2024 uploads that were still active after 2 Nov 2024.

