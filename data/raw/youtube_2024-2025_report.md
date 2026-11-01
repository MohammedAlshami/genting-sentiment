# YouTube collection report — Malaysian Genting, earlier year

- **Collected:** 2 Nov 2026
- **Window:** 2 Nov 2024 00:00 MYT → 1 Nov 2025 23:59:59 MYT (1 Nov 2024 16:00 UTC → 1 Nov 2025 16:00 UTC)
- **Output:** `data/raw/youtube_2024-2025.jsonl`
- **Records:** 1546 — 129 posts, 1417 comments
- **Posts by ticker:** GENM × 70, GENTING × 50, UNKNOWN × 9
- **Comments by post ticker:** GENM × 774, GENTING × 508, UNKNOWN × 135
- **Comment threads:** 1099 top-level comments, 318 replies, 580 distinct authors
- **Date range in file:** 2024-11-08 → 2025-10-28
- **Comment date range:** 2025-05-06 → 2025-10-28
- **Validation:** `python3 -m genting.validate data/raw/youtube_2024-2025.jsonl` → **OK, 0 errors, 0 warnings**

## Method

Discovery used yt-dlp's YouTube search with YouTube's `after:`/`before:` operators, so every query was restricted to uploads dated 1 Nov 2024 – 2 Nov 2025. 40 queries of up to 40 results each were run (English, Malay and Chinese), plus metadata checks on every shortlisted video. The searches were:

- `ytsearch40:genting malaysia stock after:2024-11-01 before:2025-11-02`
- `ytsearch40:genting berhad stock analysis after:2024-11-01 before:2025-11-02`
- `ytsearch40:GENM 4715 after:2024-11-01 before:2025-11-02`
- `ytsearch40:genting share price after:2024-11-01 before:2025-11-02`
- `ytsearch40:saham genting after:2024-11-01 before:2025-11-02`
- `ytsearch40:genting stock 2025 after:2024-11-01 before:2025-11-02`
- `ytsearch40:genting malaysia 2025 after:2024-11-01 before:2025-11-02`
- `ytsearch40:genting berhad 2025 after:2024-11-01 before:2025-11-02`
- `ytsearch40:genting results 2025 after:2024-11-01 before:2025-11-02`
- `ytsearch40:genting quarterly results after:2024-11-01 before:2025-11-02`
- `ytsearch40:genting new york casino after:2024-11-01 before:2025-11-02`
- `ytsearch40:genting privatisation after:2024-11-01 before:2025-11-02`
- `ytsearch40:genting takeover GENM after:2024-11-01 before:2025-11-02`
- `ytsearch40:genting dividend after:2024-11-01 before:2025-11-02`
- `ytsearch40:genting analysis after:2024-11-01 before:2025-11-02`
- `ytsearch40:genting buy or sell after:2024-11-01 before:2025-11-02`
- `ytsearch40:genting share price 2025 after:2024-11-01 before:2025-11-02`
- `ytsearch40:genting malaysia news after:2024-11-01 before:2025-11-02`
- `ytsearch40:berita genting after:2024-11-01 before:2025-11-02`
- `ytsearch40:genting untung after:2024-11-01 before:2025-11-02`
- `ytsearch40:云顶 股票 after:2024-11-01 before:2025-11-02`
- `ytsearch40:云顶大马 after:2024-11-01 before:2025-11-02`
- `ytsearch40:云顶 2025 after:2024-11-01 before:2025-11-02`
- `ytsearch40:云顶 业绩 after:2024-11-01 before:2025-11-02`
- `ytsearch40:云顶 财报 after:2024-11-01 before:2025-11-02`
- `ytsearch40:云顶 股价 after:2024-11-01 before:2025-11-02`
- `ytsearch40:云顶 分析 after:2024-11-01 before:2025-11-02`
- `ytsearch40:云顶 私有化 after:2024-11-01 before:2025-11-02`
- `ytsearch40:云顶 股息 after:2024-11-01 before:2025-11-02`
- `ytsearch40:Genting 3182 after:2024-11-01 before:2025-11-02`
- `ytsearch40:GENM 云顶大马 after:2024-11-01 before:2025-11-02`
- `ytsearch40:云顶 附加股 after:2024-11-01 before:2025-11-02`
- `ytsearch40:云顶 股东大会 after:2024-11-01 before:2025-11-02`
- `ytsearch40:云顶 股价 2025 after:2024-11-01 before:2025-11-02`
- `ytsearch40:genting 2024 after:2024-11-01 before:2025-11-02`
- `ytsearch40:genting 2025 after:2024-11-01 before:2025-11-02`
- `ytsearch40:genm 2025 after:2024-11-01 before:2025-11-02`
- `ytsearch40:genting malaysia 2024 after:2024-11-01 before:2025-11-02`
- `ytsearch40:saham genting 2024 after:2024-11-01 before:2025-11-02`
- `ytsearch40:saham genting 2025 after:2024-11-01 before:2025-11-02`

The shortlist contains 138 videos whose subject is Genting Berhad (GENTING, 3182) or Genting Malaysia (GENM, 4715) as listed companies/securities. Tourism, theme-park, hotel, casino-consumer, Kamen Rider/GenM-brand and other-company videos were excluded. Each shortlisted video was fetched with `yt-dlp --write-comments --skip-download`, one at a time with a 2-second gap; yt-dlp paginates the comment continuations and retrieves every comment, not only the top ones.

Six videos in this window were already written as posts in `data/raw/youtube.jsonl` because they continued to receive comments after 2 Nov 2025: `6Tp_HHbypSQ`, `6wqA59uSSlY`, `SAXnfqtbvOU`, `gESZSALUDJE`, `kX2YXGLlygc`, `ltChQ03z2Gg`. Their comment ids were checked against that file; 56 boundary comments are already present there (yt-dlp dates `1 year ago` to 2025-11-02, the start of the 2025-2026 window) and are therefore not duplicated here. The 2025-2026 file was not edited; those comments keep their original 2025-11-02 date.

## Comment timestamps (important caveat)

YouTube exposes only a relative age for comments, never an absolute publication time. At collection on 2 Nov 2026 every comment in this earlier year carries the label **`1 year ago`** (comments in the first hours of 2 Nov 2024 can carry `2 years ago`). yt-dlp resolves `1 year ago` to **2025-11-02 00:00 UTC**, which is one day *after* this file's window, and `2 years ago` to 2024-11-02 00:00 UTC. A plain yt-dlp timestamp would therefore put almost the whole year outside the window.

This collector keeps the original label in `raw.time_text`, keeps yt-dlp's resolved value in `raw.timestamp`, and sets `created_utc` to the **midpoint of the label's feasible interval**, clipped to the video's upload time and the window. The interval bounds are stored in `raw.time_text_interval_start` / `raw.time_text_interval_end` and the method in `raw.timestamp_estimate_method`. For a video uploaded in, say, October 2025, the estimate is late October 2025; for a video uploaded in November 2024 it is around May 2025. These are day-level estimates, not exact times, and the coarse label cannot distinguish a comment posted in December 2024 from one posted in October 2025 on an older video. Sub-month timing within the `1 year ago` bucket is not recoverable from YouTube's public comment API; `raw.time_text` remains the authoritative original observation.

Because the labels are coarse, replies cluster on the same estimated day: the largest cluster is **112 replies at 2025-07-02**. This is an artefact of the label, not evidence of a one-day burst of discussion.

## Videos collected

| Video | Channel | Ticker | Uploaded | Views | Comments (metadata) | Fetched | In window | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| [62YZNQppl_w](https://www.youtube.com/watch?v=62YZNQppl_w) 林国泰低价扫货，云顶大马私有化成功在望？｜寿司店、面包店陆续上市，美食物IPO为何突然冒起？｜Perak Transit突然暴跌，难道又有人中Margin Call？｜财经祥谈（25/10/25） | Neo, Biz Editor  | GENM | 2025-10-25 | 3461 | 5 | 5 | 5 | ok |
| [ms9hhXvrDcI](https://www.youtube.com/watch?v=ms9hhXvrDcI) 【马股最新走势】牛市结束?! Genting 成反转信号？#股票 #股票分析 #genting #DRB | Angie玩股知多点  | GENTING | 2025-10-18 | 10268 | 67 | 67 | 67 | ok |
| [gCvLgY6skM4](https://www.youtube.com/watch?v=gCvLgY6skM4) 简评2026财案赢家输家｜大马车市明年大变天？｜云顶大马私有化市场读懂了林老板的“暗示”？【谈股论今306】 | 陈剑老师投资教育频道 | GENM | 2025-10-17 | 23751 | 24 | 24 | 23 | ok |
| [1ubPzjnQHNE](https://www.youtube.com/watch?v=1ubPzjnQHNE) Genting Surges, Moody’s Flags Risk \| Malaysia Daily Financial News Digest 17th Oct 25 | Malaysia Money Matters | GENTING | 2025-10-17 | 21 | 0 | 0 | 0 | ok |
| [sUP1VSNKQF0](https://www.youtube.com/watch?v=sUP1VSNKQF0) Genting Berhad 9月19就瞄准了！#gentinghighland  #gentinghighlandmalaysia #genm #双阳倍量 #投資 #股市 #klci #3182 | 双阳倍量 Double Volume Bullish Channel  | GENTING | 2025-10-16 | 41 | 0 | 0 | 0 | ok |
| [vu5XjOGwX-s](https://www.youtube.com/watch?v=vu5XjOGwX-s) 今天云顶大起不关我事 😐 虽然昨天的影片有叫你换市场变🐵市 小股带量上涨需注意砂劳越主题股 - CMSB 晶圆厂 - DNEX 走势不错? 🤔 - 【阿Kya聊聊 - 151025】 | 金穗投资于生活 | GENTING | 2025-10-15 | 3112 | 37 | 37 | 37 | ok |
| [6Sgjityu1Nk](https://www.youtube.com/watch?v=6Sgjityu1Nk) Daily KLSE BURSA UPDATE - 15-10-2025💥GENTING BIG SPIKE 13%💥MRDIY IS GOING FOR LISTING IN THAILAND💥 | Trading with KS | GENTING | 2025-10-15 | 2053 | 0 | 0 | 0 | ok |
| [S93wk_Sik3c](https://www.youtube.com/watch?v=S93wk_Sik3c) 云顶集团拟私有化云顶大马，成功几率有多高？Ft. 刘礼誉，M+Global研究主管 | BFM 財今 | GENM | 2025-10-15 | 26836 | 55 | 55 | 52 | ok |
| [YzCvCc9EjmI](https://www.youtube.com/watch?v=YzCvCc9EjmI) 云顶马来西亚私有化背后的战略意图与资本运作 | germaine chan | GENTING | 2025-10-15 | 404 | — | 0 | 0 | comments_disabled: comment section unavailable (YouTube returned no comments or count; likely disabled) |
| [a1vUWOXrSqs](https://www.youtube.com/watch?v=a1vUWOXrSqs) Genting Malaysia GENM Privatisation and How to do? | NBLM | GENM | 2025-10-15 | 222 | 0 | 0 | 0 | ok |
| [iqVZQ9eAuQU](https://www.youtube.com/watch?v=iqVZQ9eAuQU) 15-10-2025 盘中浅谈 #GENTING 3182 \| 马股 | 股市先锋队 | GENTING | 2025-10-15 | 352 | 2 | 2 | 2 | ok |
| [vq8h8woymNc](https://www.youtube.com/watch?v=vq8h8woymNc) Genting’s RM2.35 Offer Divides Analysts \| Malaysia Daily Financial News Digest 15th Oct 25 | Malaysia Money Matters | GENTING | 2025-10-15 | 48 | 1 | 1 | 0 | ok |
| [yEeGYKS89CY](https://www.youtube.com/watch?v=yEeGYKS89CY) 大马Genting私有化了Genting Berhad会不会飞#gentinghighland #gentinghighlandmalaysia #genm #双阳倍量 #投資 #股市 #klci | 双阳倍量 Double Volume Bullish Channel  | GENTING | 2025-10-14 | 319 | 3 | 3 | 3 | ok |
| [IZsQKlRs5cU](https://www.youtube.com/watch?v=IZsQKlRs5cU) Daily KLSE BURSA UPDATE - 14-10-2025💥GENTING MAKES RM6.74bil PRIVATISATION BID FOR GENTING MALAYSIA | Trading with KS | GENM | 2025-10-14 | 811 | 0 | 0 | 0 | ok |
| [GspK-6kD3Y0](https://www.youtube.com/watch?v=GspK-6kD3Y0) KS看股 - 马股 KLSE BURSA 分享 - 14-10-2025💥云顶67.4亿私有化云顶大马💥OMESTI获3031万合约💥MCEMENT 99SMART AXIATA HTPADU | Trading with KS | GENM | 2025-10-14 | 3937 | 15 | 15 | 15 | ok |
| [zz3ugEGysog](https://www.youtube.com/watch?v=zz3ugEGysog) GENTING BERHAD@SUPER STOCK | I AM LEGEND | GENTING | 2025-10-14 | 198 | 1 | 1 | 1 | ok |
| [BfZk9D14Ox8](https://www.youtube.com/watch?v=BfZk9D14Ox8) 14-10-2025 盘中浅谈 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2025-10-14 | 216 | 1 | 1 | 1 | ok |
| [hRmHmYB_Hnc](https://www.youtube.com/watch?v=hRmHmYB_Hnc) 云顶斥67亿私有化 云顶大马料马股下市【2025.10.14 八度空间早晨新闻】 | 八度空间华语新闻 | GENM | 2025-10-14 | 17331 | 6 | 6 | 6 | ok |
| [e9f57zVbLFE](https://www.youtube.com/watch?v=e9f57zVbLFE) GENM｜善待股民停止折磨！ | 大老板投资记录本 | GENM | 2025-10-13 | 20953 | 56 | 56 | 55 | ok |
| [Wvv6M6Sgs7M](https://www.youtube.com/watch?v=Wvv6M6Sgs7M) 云顶拟私有化云顶大马 献购每股2.35令吉【2025.10.13 八度空间华语新闻】 | 八度空间华语新闻 | GENM | 2025-10-13 | 3968 | 0 | 0 | 0 | ok |
| [HI7DZykfHJ8](https://www.youtube.com/watch?v=HI7DZykfHJ8) TACO再现 特朗普又反转 亚股不跟美股大跌 😐云顶(GENTING )欲收购云顶大马(GENM) RM2.35 😲 - 【阿Kya聊聊 - 131025】 | 金穗投资于生活 | GENM | 2025-10-13 | 4220 | 21 | 21 | 21 | ok |
| [qC91b7lLrJE](https://www.youtube.com/watch?v=qC91b7lLrJE) Daily KLSE BURSA UPDATE - 13-10-2025💥GENTING GENM SHARE SUSPENDED PENDING ANNOUNCEMENT💥 KSL UNISEM | Trading with KS | UNKNOWN | 2025-10-13 | 1158 | 4 | 4 | 4 | ok |
| [o8sKkEkKMVw](https://www.youtube.com/watch?v=o8sKkEkKMVw) 【今早9时云顶突暂停交易，有好消息？坏消息？】马股一开盘云顶和云顶大马双股统统暂停交易,即将发布什么重大宣布？云顶暂停交易引起市场关注GentingBerhadGentingM'siaTrading | ZZgogo ZZ去哪儿 | GENM | 2025-10-13 | 5295 | 9 | 9 | 9 | ok |
| [vpPR3ni1NrA](https://www.youtube.com/watch?v=vpPR3ni1NrA) GENM GENTING MALAYSIA  云顶大马- 出现买入信号???? 中英文字幕 ENG SUB. #股票 #马股 #genting #technicalanalysis #技术分析 | Double Swords Investing | GENM | 2025-10-09 | 2306 | 13 | 13 | 11 | ok |
| [jQ3eby7mnc4](https://www.youtube.com/watch?v=jQ3eby7mnc4) GENM 云顶大马, 出现了买入信号！GENTING MALAYSIA, 中英字幕 ENG SUB. #technicalanalysis #股票 #马股 #genting #技术分析 | Double Swords Investing | GENM | 2025-09-12 | 4499 | 4 | 4 | 4 | ok |
| [rg_4BOD3w70](https://www.youtube.com/watch?v=rg_4BOD3w70) 10-9-2025 浅谈 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2025-09-10 | 198 | 2 | 2 | 2 | ok |
| [o0yOBSqvvXI](https://www.youtube.com/watch?v=o0yOBSqvvXI) Genting Malaysia 我为什么会在1 6买入？#技术分析 #trading #双阳倍量 #gentinghighland #云顶 #trending #股市#stockmarket | 双阳倍量 Double Volume Bullish Channel  | GENM | 2025-09-02 | 331 | 2 | 2 | 2 | ok |
| [JtM8zwOcN7I](https://www.youtube.com/watch?v=JtM8zwOcN7I) 帝国重组、进军农业、业绩好转，云顶（GENTING）快翻身了吗？ | Neo, Biz Editor  | GENTING | 2025-09-02 | 3137 | 1 | 1 | 1 | ok |
| [yRy_vUl52Tk](https://www.youtube.com/watch?v=yRy_vUl52Tk) GENTING 云顶 没有派息! 套牢盘挡路!  #马股 #股票 #筹码峰 #技术分析 #投資 中英字幕 ENG SUB | Double Swords Investing | GENTING | 2025-08-29 | 3483 | 5 | 5 | 5 | ok |
| [QXQlTNZ1874](https://www.youtube.com/watch?v=QXQlTNZ1874) Genting Malaysia Q2 2025 Results & Outlook \| Earnings Analysis | Nighteyes08 | GENM | 2025-08-29 | 74 | 0 | 0 | 0 | ok |
| [9owwzU9w1yI](https://www.youtube.com/watch?v=9owwzU9w1yI) 19-8-2025 盘中浅谈 #GENTING 3182 \| 马股 | 股市先锋队 | GENTING | 2025-08-19 | 377 | 5 | 5 | 5 | ok |
| [N04YqGipXOI](https://www.youtube.com/watch?v=N04YqGipXOI) GENTING 云顶 止跌回升弹上去了, 现在可以捞底吗？马股  技术分析 筹码峰 @doubleswords9564 中英字幕 ENG SUB | Double Swords Investing | GENTING | 2025-08-17 | 3514 | 7 | 7 | 7 | ok |
| [0YynQhz4Vuc](https://www.youtube.com/watch?v=0YynQhz4Vuc) 15-8-2025 浅谈 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2025-08-16 | 353 | 1 | 1 | 1 | ok |
| [lA3_Mpz9zjw](https://www.youtube.com/watch?v=lA3_Mpz9zjw) 9-7-2025 盘中浅谈 #GENM 4715 #NGGB 7241 \| 马股 | 股市先锋队 | GENM | 2025-07-09 | 392 | 1 | 1 | 1 | ok |
| [wOW41wo4Kco](https://www.youtube.com/watch?v=wOW41wo4Kco) 1-7-2025 浅谈 #ECOWLD 8206 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2025-07-01 | 155 | 3 | 3 | 3 | ok |
| [M5oMt6HYmHA](https://www.youtube.com/watch?v=M5oMt6HYmHA) 9-6-2025 浅谈 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2025-06-09 | 268 | 2 | 2 | 2 | ok |
| [JbpiP7c_QSU](https://www.youtube.com/watch?v=JbpiP7c_QSU) GENM 云顶大马今天大涨！可以追吗？GENTING #stock #bursamalaysia #technicalanalysis #股票 #技术分析 #马股 #genting #genm | Double Swords Investing | GENM | 2025-06-09 | 4292 | 7 | 7 | 7 | ok |
| [OqIPlAthjv0](https://www.youtube.com/watch?v=OqIPlAthjv0) Daily KLSE BURSA UPDATE - 9-6-2025 💥TECHNOLOGY SECTOR BIG REBOUND!💥GENM BIG SURGE!💥PENTA SAM GREATEC | Trading with KS | GENM | 2025-06-09 | 817 | 0 | 0 | 0 | ok |
| [ujTDTyEVq-Q](https://www.youtube.com/watch?v=ujTDTyEVq-Q) KS看股 - 马股 KLSE BURSA 分享 - 9-6-2025 💥科技板块大反弹!💥云顶马来西亚大涨!💥MPI PIE PENTA QL GENM GENTING VSTECS SAM D&O | Trading with KS | GENM | 2025-06-09 | 3211 | 4 | 4 | 4 | ok |
| [ojRx7HNz63M](https://www.youtube.com/watch?v=ojRx7HNz63M) Inside Genting Berhad \| Deep Dive into Q1 2025 Earnings & Strategic Outlook | Nighteyes08 | GENTING | 2025-06-06 | 76 | 0 | 0 | 0 | ok |
| [_yEQQewII-I](https://www.youtube.com/watch?v=_yEQQewII-I) Genting Malaysia (GENM) Q1 2025 Deep Dive - Forex Gain Masks Core Profit Drop & Leadership Change | Nighteyes08 | GENM | 2025-06-03 | 187 | 0 | 0 | 0 | ok |
| [LGPv4x06G-c](https://www.youtube.com/watch?v=LGPv4x06G-c) Genting Bhd Posts Revenue Dip in Q1 2025 Amid Leisure Segment Slowdown | iGAMING IN GHANA  | GENTING | 2025-05-31 | 14 | — | 0 | 0 | comments_disabled: comment section unavailable (YouTube returned no comments or count; likely disabled) |
| [AY4hzxTjWU4](https://www.youtube.com/watch?v=AY4hzxTjWU4) 博彩业不行了？！Genting & GENM   业绩表现如何？ | Invest8ddy-YC | UNKNOWN | 2025-05-30 | 2885 | 5 | 5 | 5 | ok |
| [GL_mQ_Wxdbc](https://www.youtube.com/watch?v=GL_mQ_Wxdbc) 马交所狂追问！云顶大马收购帝国为何不用开EGM？ | Neo, Biz Editor  | GENM | 2025-05-21 | 2038 | 1 | 1 | 1 | ok |
| [HNGftA3535Q](https://www.youtube.com/watch?v=HNGftA3535Q) 战略收购变财务救援？云顶大马暗渡陈仓，激怒大马交易所？AI晶片出口限制转向，数据中心概念股翻身？【谈股论今 271】 | 陈剑老师投资教育频道 | GENM | 2025-05-19 | 13964 | 12 | 12 | 12 | ok |
| [YBtho2jzjes](https://www.youtube.com/watch?v=YBtho2jzjes) GENTING 云顶- 如何确认上升趋势, 跟随趋势交易！趋势是你的朋友！买入信号！价格行为！技术分析！[中文字幕］ | Double Swords Investing | GENTING | 2025-05-09 | 2535 | 6 | 6 | 6 | ok |
| [6v1mxfdFP0E](https://www.youtube.com/watch?v=6v1mxfdFP0E) 全面收购帝国度假村！云顶大马股价反弹在即？ | 夜月投资 | GENM | 2025-05-08 | 12798 | 25 | 25 | 25 | ok |
| [iVUpxymfu44](https://www.youtube.com/watch?v=iVUpxymfu44) GENM吃哑巴亏？林老板更喜欢GENTING！ | 大老板投资记录本 | GENM | 2025-05-07 | 11204 | 36 | 36 | 36 | ok |
| [ejk2t_iynXw](https://www.youtube.com/watch?v=ejk2t_iynXw) GENM 云顶大马- 阻力重重, 套牢盘多！如何识别阻力轻重？GENTING MALAYSIA. 筹码峰分析！洗筹码！技术分析！[中文字幕] | Double Swords Investing | GENM | 2025-04-29 | 2156 | 6 | 6 | 6 | ok |
| [kl0fhX5lEOc](https://www.youtube.com/watch?v=kl0fhX5lEOc) 29-4-2025 盘中浅谈 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2025-04-29 | 112 | 0 | 0 | 0 | ok |
| [7rcI3vQ20zQ](https://www.youtube.com/watch?v=7rcI3vQ20zQ) GENTING 云顶 - 现在是形成第二支脚吗？买入信号！筹码峰！藍筹股！技术分析！双剑技巧！[ENG SUB] | Double Swords Investing | GENTING | 2025-04-23 | 2441 | 7 | 7 | 7 | ok |
| [E4VFoCaEtIc](https://www.youtube.com/watch?v=E4VFoCaEtIc) GENM 云顶大马 - 套牢盘挡路, 如何抓反弹？买入信号！GENTING MALAYSIA. 筹码峰！技术分析！双剑技巧！[ENG SUB] | Double Swords Investing | GENM | 2025-04-21 | 2014 | 8 | 8 | 8 | ok |
| [T15nzJFJy4w](https://www.youtube.com/watch?v=T15nzJFJy4w) 16-4-2025 盘中浅谈 #GENTING 3182 \| 马股【电话版】 | 股市先锋队 | GENTING | 2025-04-16 | 84 | 0 | 0 | 0 | ok |
| [sCmG-NYnoJg](https://www.youtube.com/watch?v=sCmG-NYnoJg) GENM 云顶大马, 动能衰竭,难突破套牢盘！但也给抓反弹的机会！第二支脚！买入信号！GENTING MALAYSIA. 技术分析！筹码主力线！形态分析！[ENG SUB] | Double Swords Investing | GENM | 2025-04-15 | 1878 | 10 | 10 | 10 | ok |
| [D6qF3W0vgig](https://www.youtube.com/watch?v=D6qF3W0vgig) GENTING 云顶, 双底形态成形中, 突破这个价位是买入信号！趋势反转信号！颈线！技术分析！筹码峰！[ENG SUB］ | Double Swords Investing | GENTING | 2025-04-14 | 2634 | 11 | 11 | 11 | ok |
| [F_41VTaszoM](https://www.youtube.com/watch?v=F_41VTaszoM) 2-4-2025 盘中浅谈 #MERSEC 0285 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2025-04-02 | 186 | 0 | 0 | 0 | ok |
| [Svem8WCaf78](https://www.youtube.com/watch?v=Svem8WCaf78) 股价13个月跌38%，市值从160亿跌到99亿，股息减33%，成本高涨，case study: GENTING MALAYSIA | James Share Investing | GENM | 2025-03-31 | 4009 | 2 | 2 | 2 | ok |
| [OEzWHc3-dcw](https://www.youtube.com/watch?v=OEzWHc3-dcw) GENTING 云顶 - 上涨 要靠 TauRx 老人药！反转信号？支撑线？阻力线？套牢盘？技术分析. 筹码主力线！[ENG SUB] | Double Swords Investing | GENTING | 2025-03-30 | 3241 | 8 | 8 | 8 | ok |
| [iZshSGEOCLs](https://www.youtube.com/watch?v=iZshSGEOCLs) GENM GENTING MALAYSIA 云顶大马 52周新低, 如何确认止跌？什么时候可以去捞？技术分析！筹码峰！[ENG SUB] | Double Swords Investing | GENM | 2025-03-27 | 4205 | 11 | 11 | 11 | ok |
| [rneqGaUi5sY](https://www.youtube.com/watch?v=rneqGaUi5sY) Genting Malaysia Berhad: Leading integrated resort operator | Blue Tech Wave Media | GENM | 2025-03-26 | 141 | 1 | 1 | 1 | ok |
| [hZITCjlS3eE](https://www.youtube.com/watch?v=hZITCjlS3eE) GENTING 云顶 - 产生第二支脚, 如何精准操作买入？目标价是多少？技术分析！[ENG SUB] | Double Swords Investing | GENTING | 2025-03-25 | 3616 | 5 | 5 | 5 | ok |
| [U_ZnLjkOSDY](https://www.youtube.com/watch?v=U_ZnLjkOSDY) 【金穗早晨股市速报 - 250325】ABMB附加股大跌 \| CIMB MBB看好云顶和解案 \| IJM不怕市场谣言 \| Apex技术分析雷达: BNASTRA & AUMAS | 金穗投资于生活 | GENTING | 2025-03-25 | 2009 | 9 | 9 | 9 | ok |
| [GFGzqb0msbo](https://www.youtube.com/watch?v=GFGzqb0msbo) GENTING 云顶 - 回调买上涨的机会！支撑阻力在哪里？老板又买入！老人药有消息？[ENG SUB] | Double Swords Investing | GENTING | 2025-03-17 | 2698 | 9 | 9 | 9 | ok |
| [ptUGXafAnVU](https://www.youtube.com/watch?v=ptUGXafAnVU) GENM GENTING MALAYSIA 云顶大马 - 終于站上1.80！ 可以进场了吗？有没有套牢盘档路？如何操作？[ENG SUB] | Double Swords Investing | GENM | 2025-03-17 | 4047 | 13 | 13 | 13 | ok |
| [FTeez1YU23Q](https://www.youtube.com/watch?v=FTeez1YU23Q) 2025 一支影片带你去了解 云顶双雄何去何从！大势已去?! \| ⚠️⚠️【乐学成长空间 - LXInvest】 | 乐学成长空间 - LXInvest | UNKNOWN | 2025-03-15 | 21119 | 20 | 20 | 20 | ok |
| [RqhtJEOsga0](https://www.youtube.com/watch?v=RqhtJEOsga0) GENTING 云顶-  3大原因, 股价逆市而涨！老人药？技术分析又如何看？[ENG SUB] | Double Swords Investing | GENTING | 2025-03-12 | 4091 | 10 | 10 | 10 | ok |
| [yKBBgoyAkQE](https://www.youtube.com/watch?v=yKBBgoyAkQE) GENM GENTING MALAYSIA 云顶大马-  跌破心理价位1.80, 现在怎么办？可以捞吗？[ENG SUB] | Double Swords Investing | GENM | 2025-03-11 | 4205 | 14 | 14 | 14 | ok |
| [A5NXmIP-HUw](https://www.youtube.com/watch?v=A5NXmIP-HUw) Genting's Stock Crash: Buy Now?  \| 🦖 #TheInvestingIguana EP739 | Iggy the Investing Iguana | GENTING | 2025-03-10 | 1808 | 2 | 2 | 2 | ok |
| [SC4eT3ubSFg](https://www.youtube.com/watch?v=SC4eT3ubSFg) EDGE WEEKLY: Can Genting extract more value from Genting Singapore? | The Edge TV | GENTING | 2025-03-10 | 2773 | — | 0 | 0 | comments_disabled: comment section unavailable (YouTube returned no comments or count; likely disabled) |
| [n176wDIiM_U](https://www.youtube.com/watch?v=n176wDIiM_U) 【快速解盘】GENTING 老板开始增持自家股票，大跌后能否让股价转跌回升吗 ?#shorts@mytraderview | MYtraderview 大马股市技术分析交易 + 生活日志 | GENTING | 2025-03-10 | 156 | 1 | 1 | 1 | ok |
| [Ssr3vBSvP1g](https://www.youtube.com/watch?v=Ssr3vBSvP1g) GENTING 云顶   止跌回升, 弹上去？可以追吗？［ENG SUB] | Double Swords Investing | GENTING | 2025-03-10 | 2320 | 10 | 10 | 10 | ok |
| [sBccXz1dJSE](https://www.youtube.com/watch?v=sBccXz1dJSE) 【快速解盘】GENTING 老板开始增持自家股票，大跌后能否让股价转跌回升吗 ?@mytraderview | MYtraderview 大马股市技术分析交易 + 生活日志 | GENTING | 2025-03-09 | 1598 | 19 | 19 | 19 | ok |
| [43Rdr06BHP0](https://www.youtube.com/watch?v=43Rdr06BHP0) 7-3-2025 浅谈 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2025-03-09 | 301 | 0 | 0 | 0 | ok |
| [SWjGqeBNNas](https://www.youtube.com/watch?v=SWjGqeBNNas) 7-3-2025 浅谈 #GENTING 3182 \| 马股 | 股市先锋队 | GENTING | 2025-03-08 | 751 | 4 | 4 | 4 | ok |
| [6DpF0CfYL9g](https://www.youtube.com/watch?v=6DpF0CfYL9g) GENM GENTING MALAYSIA 云顶大马 - 走势疲软, 继续等! 什么时候可以进场？[ENG SUB] | Double Swords Investing | GENM | 2025-03-07 | 3496 | 14 | 14 | 14 | ok |
| [FWc5c_d483M](https://www.youtube.com/watch?v=FWc5c_d483M) 《GENTING 从辉煌到跌落神坛！》马股一波未平一波又起！云顶双雄怎么了？ | Andy Yew | UNKNOWN | 2025-03-03 | 4194 | 1 | 1 | 1 | ok |
| [YJzqRTJSkZg](https://www.youtube.com/watch?v=YJzqRTJSkZg) 03 03 2025 第616期：GENM 是时候捞了吗？ | 我是雷公 | GENM | 2025-03-03 | 2086 | 6 | 6 | 6 | ok |
| [5uaAzNbi6W0](https://www.youtube.com/watch?v=5uaAzNbi6W0) GENM GENTING MALAYSIA 云顶大马 Q4 FY24 季报深度分析解读! 业绩有这么差吗？股价大跌的原因是什么？长期投资可否布局？ [CC ENG SUB] | Double Swords Investing | GENM | 2025-03-03 | 5069 | 12 | 12 | 12 | ok |
| [G_707EDOtcI](https://www.youtube.com/watch?v=G_707EDOtcI) GENM 业绩核爆 \| 云顶大马股价一天暴跌近20% 现在该买还是该卖? \| 魔鬼藏在细节里, 一起剖析财报中的秘密, 寻找赚钱的机会 \| 金穗投资 | 金穗投资于生活 | GENM | 2025-03-02 | 11198 | 32 | 32 | 32 | ok |
| [nACn1SnarDM](https://www.youtube.com/watch?v=nACn1SnarDM) 云顶大马出现业绩炸弹？股价暴跌19%？是时候捞底了吗？ | 夜月投资 | GENM | 2025-03-02 | 42530 | 112 | 112 | 112 | ok |
| [DPO8IAlHWjw](https://www.youtube.com/watch?v=DPO8IAlHWjw) 【形态解读】GENTING 股价跳水暴跌 11%！ 要跌完了吗？要如何应对？#shorts@mytraderview | MYtraderview 大马股市技术分析交易 + 生活日志 | GENTING | 2025-03-02 | 411 | 8 | 8 | 8 | ok |
| [3sr4z_POzK0](https://www.youtube.com/watch?v=3sr4z_POzK0) 28-2-2025 浅谈 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2025-03-01 | 1004 | 0 | 0 | 0 | ok |
| [pZL2KCSOSZ0](https://www.youtube.com/watch?v=pZL2KCSOSZ0) GENM 云顶大马暴量大跌不急捞 [ENG SUB] | Double Swords Investing | GENM | 2025-02-28 | 5166 | 14 | 14 | 14 | ok |
| [AEORBBjXi2M](https://www.youtube.com/watch?v=AEORBBjXi2M) 【形态解读】GENTING 股价跳水暴跌 11%！ 要跌完了吗？要如何应对？@mytraderview | MYtraderview 大马股市技术分析交易 + 生活日志 | GENTING | 2025-02-28 | 4009 | 38 | 38 | 38 | ok |
| [TAsMYObi5k0](https://www.youtube.com/watch?v=TAsMYObi5k0) KS看股 - 马股 KLSE BURSA 分享 - 28-2-2025 💥马资源获 24.7亿令吉LRT3工程💥业绩令人失望 云顶双雄股价下跌💥CIMB SPSETIA UNISEM IJM QL | Trading with KS | UNKNOWN | 2025-02-28 | 3714 | 14 | 14 | 14 | ok |
| [j75HBiYkUxE](https://www.youtube.com/watch?v=j75HBiYkUxE) 【金穗早晨股市速报 - 280225】云顶双雄又亏钱?!!🤷🏻‍♀️ \| NVIDIA带飞NATGATE \| MRCB获LRT3近25亿合约 \| Apex技术分析雷达:UTDPLT & RHBBANK | 金穗投资于生活 | UNKNOWN | 2025-02-28 | 2140 | 5 | 5 | 5 | ok |
| [Xq6svjv0G00](https://www.youtube.com/watch?v=Xq6svjv0G00) Genting Malaysia (GENM) 4Q24: Revenue Soars, Profits Sink - Why? | Nighteyes08 | GENM | 2025-02-27 | 149 | 0 | 0 | 0 | ok |
| [vRRdj5B0B3s](https://www.youtube.com/watch?v=vRRdj5B0B3s) GENM 云顶大马 强势突破 200 天均线！还能继续追涨吗？ | Double Swords Investing | GENM | 2025-02-14 | 4855 | 23 | 23 | 23 | ok |
| [NpYm3zVGsUQ](https://www.youtube.com/watch?v=NpYm3zVGsUQ) 14-2-2025 盘中浅谈 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2025-02-14 | 377 | 0 | 0 | 0 | ok |
| [1uKAl580Jog](https://www.youtube.com/watch?v=1uKAl580Jog) GENTING 云顶 低位买入已盈利！短线该止盈还是加仓？ | Double Swords Investing | GENTING | 2025-02-14 | 39144 | 18 | 18 | 18 | ok |
| [4L8IG2ZgzsA](https://www.youtube.com/watch?v=4L8IG2ZgzsA) GENM 云顶大马放量突破关键阻力！确认买入信号？ | Double Swords Investing | GENM | 2025-02-13 | 78666 | 18 | 18 | 18 | ok |
| [3SlxFV-6mMk](https://www.youtube.com/watch?v=3SlxFV-6mMk) 13-2-2025 盘中浅谈 #GENTING 3182 \| 马股 | 股市先锋队 | GENTING | 2025-02-13 | 195 | 0 | 0 | 0 | ok |
| [P9d2tG45y_Y](https://www.youtube.com/watch?v=P9d2tG45y_Y) GENTING 云顶 筹码结构分析！主力吸筹，散户如何跟进？ | Double Swords Investing | GENTING | 2025-02-08 | 2989 | 5 | 5 | 5 | ok |
| [a92CsBNLivw](https://www.youtube.com/watch?v=a92CsBNLivw) GENM 云顶大马  短线反弹即将启动？如何找到进场买点？ | Double Swords Investing | GENM | 2025-02-08 | 3216 | 5 | 5 | 5 | ok |
| [tDtXdeSOglc](https://www.youtube.com/watch?v=tDtXdeSOglc) GENM 云顶大马 突破这个价位可以抓反弹! | Double Swords Investing | GENM | 2025-02-02 | 3340 | 12 | 12 | 12 | ok |
| [4tS7SBTsBj4](https://www.youtube.com/watch?v=4tS7SBTsBj4) GENTING 云顶 底部筹码不稳定. | Double Swords Investing | GENTING | 2025-01-31 | 2279 | 13 | 13 | 13 | ok |
| [QBlqw0dTqLo](https://www.youtube.com/watch?v=QBlqw0dTqLo) 【金穗早晨股市速报 - 280125】一只蓝鲸掀翻YTLPOWR \| BURSA年度业绩创高 \| HLBank叫买GENTING \| Apex技术分析雷达: PTRANS  & IHH | 金穗投资于生活 | GENTING | 2025-01-28 | 2984 | 0 | 0 | 0 | ok |
| [qmQm5DQmjAA](https://www.youtube.com/watch?v=qmQm5DQmjAA) GENM 云顶大马 耐心等待捞底的机会! | Double Swords Investing | GENM | 2025-01-21 | 3525 | 8 | 8 | 8 | ok |
| [0jE_jzY36SQ](https://www.youtube.com/watch?v=0jE_jzY36SQ) GENM 云顶大马 形成第二支脚,有机会突破筹码主力线! | Double Swords Investing | GENM | 2025-01-18 | 3191 | 10 | 10 | 10 | ok |
| [rkOWak1xY3Y](https://www.youtube.com/watch?v=rkOWak1xY3Y) 14-1-2025 浅谈 #EATECH 5259 #GENTING 3182 \| 马股 | 股市先锋队 | GENTING | 2025-01-14 | 86 | 0 | 0 | 0 | ok |
| [mGcQx6Mxy9U](https://www.youtube.com/watch?v=mGcQx6Mxy9U) 【金穗早晨股市速报 - 140125】CIMB 喊买 GENM 槟城LRT最大受惠GAMUDA Apex技术分析雷达:  WASCO & KPJ | 金穗投资于生活 | GENM | 2025-01-14 | 103 | 0 | 0 | 0 | ok |
| [izUrp8_W2qk](https://www.youtube.com/watch?v=izUrp8_W2qk) GENTING 云顶 果然是假突破! 有跌有机会! 什么价位可以去捞底？ | Double Swords Investing | GENTING | 2025-01-09 | 4233 | 13 | 13 | 13 | ok |
| [Sr3bP989oog](https://www.youtube.com/watch?v=Sr3bP989oog) GENM 云顶大马看看有什么东西挡路？ | Double Swords Investing | GENM | 2025-01-06 | 3609 | 15 | 15 | 15 | ok |
| [-3iPfEPUFZk](https://www.youtube.com/watch?v=-3iPfEPUFZk) 6-1-2025 盘中浅谈 #CORAZA 0240 #GENM 4715 \| 马股 | 股市先锋队 | GENM | 2025-01-06 | 85 | 0 | 0 | 0 | ok |
| [w16c_bIxaIY](https://www.youtube.com/watch?v=w16c_bIxaIY) GENTING. 云顶, 动能开始转弱,回调买上涨! | Double Swords Investing | GENTING | 2024-12-31 | 2624 | 16 | 16 | 16 | ok |
| [plZs0FJzlVE](https://www.youtube.com/watch?v=plZs0FJzlVE) GENM 云顶大马 走势乏力,回调机会大! | Double Swords Investing | GENM | 2024-12-30 | 3417 | 8 | 8 | 8 | ok |
| [vURkzAJqwOQ](https://www.youtube.com/watch?v=vURkzAJqwOQ) GENTING 云顶 回调买上涨的机会又来了! | Double Swords Investing | GENTING | 2024-12-28 | 372797 | 44 | 44 | 44 | ok |
| [otzvM4QMfzU](https://www.youtube.com/watch?v=otzvM4QMfzU) 26-12-2024 浅谈 #GENTING 3182 \| 马股 | 股市先锋队 | GENTING | 2024-12-26 | 149 | 0 | 0 | 0 | ok |
| [TjRL9SlBkHs](https://www.youtube.com/watch?v=TjRL9SlBkHs) 投资云顶的5大争议点，云顶是价值陷阱还是谣言没有止于智者？GENM GENTING【理财投资】 ｜阿布abu | 阿布的鸟公司 | UNKNOWN | 2024-12-20 | 17109 | 85 | 85 | 85 | ok |
| [3Q-qkGO57k8](https://www.youtube.com/watch?v=3Q-qkGO57k8) GENM 云顶大马-已经站上去了橙紫灰包线! | Double Swords Investing | GENM | 2024-12-19 | 5395 | 18 | 18 | 18 | ok |
| [Av_yRLnH3no](https://www.youtube.com/watch?v=Av_yRLnH3no) EVENING 5: Genting, GenM skid to four-year lows | The Edge TV | UNKNOWN | 2024-12-17 | 3780 | — | 0 | 0 | comments_disabled: comment section unavailable (YouTube returned no comments or count; likely disabled) |
| [p8EnV2q7raw](https://www.youtube.com/watch?v=p8EnV2q7raw) 股价从巅峰下跌超过60%！云顶还能重返辉煌吗？ | Neo, Biz Editor  | GENTING | 2024-12-16 | 19174 | 19 | 19 | 16 | ok |
| [qM6RX2o9XVQ](https://www.youtube.com/watch?v=qM6RX2o9XVQ) GENM 云顶大马 等筹码稳定后,就可以进场了！ | Double Swords Investing | GENM | 2024-12-11 | 5263 | 23 | 23 | 23 | ok |
| [M9IU8gPrXOg](https://www.youtube.com/watch?v=M9IU8gPrXOg) 跌出综指30大成分股！云顶股票是个机会？还是个陷阱？【谈股论今 232】 | 陈剑老师投资教育频道 | GENTING | 2024-12-09 | 60738 | 59 | 59 | 59 | ok |
| [UVdfZ1YGRrU](https://www.youtube.com/watch?v=UVdfZ1YGRrU) Deep Dive into Genting Malaysia  (GENM) Q3 2024:  Profits Rise, But Challenges Loom Large | Nighteyes08 | GENM | 2024-12-08 | 112 | 0 | 0 | 0 | ok |
| [rEC5Q48ykJ8](https://www.youtube.com/watch?v=rEC5Q48ykJ8) GENM 云顶大马 止跌回升了吗？ | Double Swords Investing | GENM | 2024-12-06 | 3033 | 16 | 16 | 16 | ok |
| [58s_wlpnAzw](https://www.youtube.com/watch?v=58s_wlpnAzw) GENM 云顶大马 支撑阻力线在那里？ | Double Swords Investing | GENM | 2024-12-04 | 4068 | 10 | 10 | 10 | ok |
| [g4ZcGogBU2o](https://www.youtube.com/watch?v=g4ZcGogBU2o) GENTING 云顶 跌破支撑底底低! | Double Swords Investing | GENTING | 2024-12-03 | 3889 | 11 | 11 | 11 | ok |
| [orndQ85zdp8](https://www.youtube.com/watch?v=orndQ85zdp8) Daily KLSE BURSA UPDATE - 29-11-2024 💥GENM 3Q NET PROFIT LEAP TO RM569mil💥CAPITALA 3Q NET PROFIT💥 | Trading with KS | GENM | 2024-11-29 | 786 | 0 | 0 | 0 | ok |
| [T-KsbZ7Z46c](https://www.youtube.com/watch?v=T-KsbZ7Z46c) KS看股 - 马股 KLSE BURSA 分享 - 29-11-2024 💥云顶大马净利翻倍涨 💥壹必投第三季净赚16.4亿💥VSTECS MAHSING FFB PBBANK RHBBANK | Trading with KS | GENM | 2024-11-29 | 3085 | 5 | 5 | 5 | ok |
| [iPPrdK3i_9o](https://www.youtube.com/watch?v=iPPrdK3i_9o) GENM 云顶大马 弱势无力,等公布业绩! | Double Swords Investing | GENM | 2024-11-22 | 2753 | 9 | 9 | 9 | ok |
| [1W3uKviFkh8](https://www.youtube.com/watch?v=1W3uKviFkh8) GENTING 云顶止跌了,下个阻力线在那里？ | Double Swords Investing | GENTING | 2024-11-19 | 2950 | 10 | 10 | 10 | ok |
| [5WaRG_l3HYQ](https://www.youtube.com/watch?v=5WaRG_l3HYQ) GENM 云顶大马 -止跌了... | Double Swords Investing | GENM | 2024-11-18 | 3380 | 8 | 8 | 8 | ok |
| [ja5-xMZGGKc](https://www.youtube.com/watch?v=ja5-xMZGGKc) 【云顶好热闹 -旅游业复苏但云顶系股价不起反跌？ 】云顶几时股价可以超越10零吉？云顶股价低于预期迟迟不能兑现 云顶新加坡业绩 GentingSharePrice2024 | ZZgogo ZZ去哪儿 | UNKNOWN | 2024-11-17 | 2011 | 1 | 1 | 1 | ok |
| [juzx6u9m6gQ](https://www.youtube.com/watch?v=juzx6u9m6gQ) 云顶Genting 走势分析，值得入手吗？ | IM_万事如意 | GENTING | 2024-11-13 | 813 | 6 | 6 | 6 | ok |
| [OczYueSN6uI](https://www.youtube.com/watch?v=OczYueSN6uI) GENM 云顶大马 止跌了？稳了？ | Double Swords Investing | GENM | 2024-11-13 | 4521 | 12 | 12 | 12 | ok |
| [VErk8Te8hQI](https://www.youtube.com/watch?v=VErk8Te8hQI) GENTING 跌破 3.80 下个支撑在那里？老人药是救星？ | Double Swords Investing | GENTING | 2024-11-12 | 5006 | 16 | 16 | 16 | ok |
| [bw7Q7STEvxY](https://www.youtube.com/watch?v=bw7Q7STEvxY) GENM 云顶大马 跌穿了! 52周新低!大跌的两个原因! | Double Swords Investing | GENM | 2024-11-11 | 9425 | 21 | 21 | 21 | ok |
| [4bquF4qM0m8](https://www.youtube.com/watch?v=4bquF4qM0m8) GENTING 双顶的跌幅满足到达了, 破底翻？ | Double Swords Investing | GENTING | 2024-11-08 | 5648 | 6 | 6 | 6 | ok |

## Videos checked but not written as posts

| Video | Uploaded | Fetched comments | Reason |
| --- | --- | ---: | --- |
| [SAXnfqtbvOU](https://www.youtube.com/watch?v=SAXnfqtbvOU) GENTING 3182私有化GENM后的价格技术分析 #股票投資 #马股 #云顶 #genm #genting | 2025-10-22 | 6 | post already in data/raw/youtube.jsonl; earlier comments written here |
| [6Tp_HHbypSQ](https://www.youtube.com/watch?v=6Tp_HHbypSQ) 云顶大马的最后一页… | 2025-10-22 | 3 | post already in data/raw/youtube.jsonl; earlier comments written here |
| [6wqA59uSSlY](https://www.youtube.com/watch?v=6wqA59uSSlY) 林国泰的豪赌：67亿私有化云顶大马，背后的棋局与信号 | 2025-10-20 | 16 | post already in data/raw/youtube.jsonl; earlier comments written here |
| [ltChQ03z2Gg](https://www.youtube.com/watch?v=ltChQ03z2Gg) 林国泰出手私有化云顶大马！2.35令吉收购价合理吗？｜2026财政预算案赢家输家诞生，99超市股价和创办人身家暴涨！｜马币势如破竹升破4在望，亚航或成大赢家？｜财经祥谈（17/10/25） | 2025-10-17 | 2 | post already in data/raw/youtube.jsonl; earlier comments written here |
| [kX2YXGLlygc](https://www.youtube.com/watch?v=kX2YXGLlygc) 云顶大动作！GENM 私有化计划全解析 ｜第一天乡下茶话会 | 2025-10-16 | 33 | post already in data/raw/youtube.jsonl; earlier comments written here |
| [gESZSALUDJE](https://www.youtube.com/watch?v=gESZSALUDJE) GENTING MALAYSIA BERHAD@SUPER STOCK | 2025-07-08 | 1 | post already in data/raw/youtube.jsonl; earlier comments written here |
| [xOfWkHEbWPs](https://www.youtube.com/watch?v=xOfWkHEbWPs) Genting Malaysia: off its game | 2020-05-31 | 0 | no in-window comments; post not written |
| [i4VXDtQQkKE](https://www.youtube.com/watch?v=i4VXDtQQkKE) Genting Malaysia - Quarter Review | 2019-12-21 | 0 | no in-window comments; post not written |
| [fY7ZKLqjMAg](https://www.youtube.com/watch?v=fY7ZKLqjMAg) Genting, the Empire strikes back? | 2019-07-28 | 0 | no in-window comments; post not written |

## Largest comment threads
| Video | Ticker | Comments in window |
| --- | --- | ---: |
| [nACn1SnarDM](https://www.youtube.com/watch?v=nACn1SnarDM) 云顶大马出现业绩炸弹？股价暴跌19%？是时候捞底了吗？ | GENM | 112 |
| [TjRL9SlBkHs](https://www.youtube.com/watch?v=TjRL9SlBkHs) 投资云顶的5大争议点，云顶是价值陷阱还是谣言没有止于智者？GENM GENTING【理财投资】 ｜阿布abu | UNKNOWN | 85 |
| [ms9hhXvrDcI](https://www.youtube.com/watch?v=ms9hhXvrDcI) 【马股最新走势】牛市结束?! Genting 成反转信号？#股票 #股票分析 #genting #DRB | GENTING | 67 |
| [M9IU8gPrXOg](https://www.youtube.com/watch?v=M9IU8gPrXOg) 跌出综指30大成分股！云顶股票是个机会？还是个陷阱？【谈股论今 232】 | GENTING | 59 |
| [e9f57zVbLFE](https://www.youtube.com/watch?v=e9f57zVbLFE) GENM｜善待股民停止折磨！ | GENM | 55 |
| [S93wk_Sik3c](https://www.youtube.com/watch?v=S93wk_Sik3c) 云顶集团拟私有化云顶大马，成功几率有多高？Ft. 刘礼誉，M+Global研究主管 | GENM | 52 |
| [vURkzAJqwOQ](https://www.youtube.com/watch?v=vURkzAJqwOQ) GENTING 云顶 回调买上涨的机会又来了! | GENTING | 44 |
| [AEORBBjXi2M](https://www.youtube.com/watch?v=AEORBBjXi2M) 【形态解读】GENTING 股价跳水暴跌 11%！ 要跌完了吗？要如何应对？@mytraderview | GENTING | 38 |
| [vu5XjOGwX-s](https://www.youtube.com/watch?v=vu5XjOGwX-s) 今天云顶大起不关我事 😐 虽然昨天的影片有叫你换市场变🐵市 小股带量上涨需注意砂劳越主题股 - CMSB 晶圆厂 - DNEX 走势不错? 🤔 - 【阿Kya聊聊 - 151025】 | GENTING | 37 |
| [iVUpxymfu44](https://www.youtube.com/watch?v=iVUpxymfu44) GENM吃哑巴亏？林老板更喜欢GENTING！ | GENM | 36 |
| [G_707EDOtcI](https://www.youtube.com/watch?v=G_707EDOtcI) GENM 业绩核爆 \| 云顶大马股价一天暴跌近20% 现在该买还是该卖? \| 魔鬼藏在细节里, 一起剖析财报中的秘密, 寻找赚钱的机会 \| 金穗投资 | GENM | 32 |
| [6v1mxfdFP0E](https://www.youtube.com/watch?v=6v1mxfdFP0E) 全面收购帝国度假村！云顶大马股价反弹在即？ | GENM | 25 |
| [qM6RX2o9XVQ](https://www.youtube.com/watch?v=qM6RX2o9XVQ) GENM 云顶大马 等筹码稳定后,就可以进场了！ | GENM | 23 |
| [vRRdj5B0B3s](https://www.youtube.com/watch?v=vRRdj5B0B3s) GENM 云顶大马 强势突破 200 天均线！还能继续追涨吗？ | GENM | 23 |
| [gCvLgY6skM4](https://www.youtube.com/watch?v=gCvLgY6skM4) 简评2026财案赢家输家｜大马车市明年大变天？｜云顶大马私有化市场读懂了林老板的“暗示”？【谈股论今306】 | GENM | 23 |

## Failures and gaps

- `Av_yRLnH3no` (EVENING 5: Genting, GenM skid to four-year lows) — comment section unavailable (YouTube returned no comments or count; likely disabled); fetched 0 comments, 0 in window; post written.
- `LGPv4x06G-c` (Genting Bhd Posts Revenue Dip in Q1 2025 Amid Leisure Segment Slowdown) — comment section unavailable (YouTube returned no comments or count; likely disabled); fetched 0 comments, 0 in window; post written.
- `YzCvCc9EjmI` (云顶马来西亚私有化背后的战略意图与资本运作) — comment section unavailable (YouTube returned no comments or count; likely disabled); fetched 0 comments, 0 in window; post written.
- `SC4eT3ubSFg` (EDGE WEEKLY: Can Genting extract more value from Genting Singapore?) — comment section unavailable (YouTube returned no comments or count; likely disabled); fetched 0 comments, 0 in window; post written.

## Exclusions

The discovery pool contained Genting Highlands travel/theme-park/hotel videos, casino and baccarat content, Kamen Rider `Genm` videos, unrelated `GenM` brand/certification videos, Generation Mining (`GENM` on TSX) and Genting Singapore (SGX:G13) analysis. Those were excluded because they are not about GENTING/GENM as Malaysian listed securities. Generic multi-stock market roundups were also dropped unless Genting was the specific subject; daily technical videos dedicated to 3182/4715 were kept.

Videos uploaded before 2 Nov 2024 were not added unless they were still drawing comments in the window. The six overlapping posts above are already in `youtube.jsonl`; their 56 boundary comments are not duplicated here. Many replies are short repeated reactions (emoji, thanks, creator boilerplate): 548 reply bodies repeat another reply's exact text. They are distinct comment ids and are kept.

