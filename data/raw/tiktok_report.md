# TikTok collection report — Malaysian Genting

- **Collected:** 2 Nov 2026
- **Window:** 2 Nov 2024 → 2 Nov 2026 inclusive (cutoff 3 Nov 2026 00:00 UTC)
- **Output:** `data/raw/tiktok.jsonl`
- **Records:** 1229 — 84 videos, 1145 comments (890 top-level, 255 replies)
- **Videos fetched vs written:** 85 relevant videos fetched, 84 written (the extra one is a pre-window upload with no in-window comments).
- **Videos by ticker:** GENM × 17, GENTING × 16, UNKNOWN × 51
- **Comments by post ticker:** GENM × 86, GENTING × 135, UNKNOWN × 924
- **Distinct comment authors:** 889
- **Post upload range:** 2022-09-21 → 2026-11-01 (82 of 84 posts uploaded inside the window)
- **Comment date range:** 2024-11-28 → 2026-11-01
- **Languages (API `comment_language`):** zh × 317, un × 280, en × 256, ms × 145, zh-Hant × 110, id × 23, hi × 2, tr × 2, bg × 1, sk × 1, es × 1, lb × 1, tl × 1, zy × 1, uz × 1, co × 1, vi × 1, pl × 1

## Method

A single headful Chrome session (nodriver 0.50.3, inside Xvfb) loaded the TikTok search page. Discovery called the site's own `search/general/full` endpoint from that page for 91 keyword queries and 5 hashtag queries, requesting 30 results per query (TikTok returned 27–43 depending on the query). Comment collection called `comment/list` and `comment/list/reply` with `count=50`, following `cursor` until `has_more` was false. All requests carried the browser's own cookies; no login, credentials or captcha solving was used.

Requests were serialised with 2–3.4 s between searches, 2–3.6 s between videos and ~0.5–1.2 s between comment pages. No HTTP 429, captcha or login wall was encountered while reading. Reading comments does not require login on TikTok.

The public web API exposes exact `create_time` epoch values for every video and comment, so no relative-date or year inference was needed. The original API timestamp is stored in `raw.create_time`; `raw.time_text` carries the UTC rendering and `raw.time_confidence` is `exact_api`. TikTok's UI may show only `MM-DD`, but that label was not used for timestamps.

`score` is the like count (`digg_count`) for comments and `diggCount` for videos. `num_comments` is the video's `commentCount`; the comment API's `total` is recorded in the report for reconciliation. Records are deduplicated by `(source, native_id)`.

## Discovery queries

| Query | Results | In-window kept videos |
| --- | ---: | ---: |
| `genting stock` | 31 | 16 |
| `genting share` | 32 | 3 |
| `genting share price` | 34 | 18 |
| `genting analysis` | 32 | 6 |
| `genting dividend` | 32 | 17 |
| `genting results` | 30 | 4 |
| `genting rights issue` | 32 | 8 |
| `genting debt` | 33 | 13 |
| `genting jatuh` | 27 | 0 |
| `genting crash` | 33 | 0 |
| `genting berhad` | 33 | 5 |
| `genting malaysia` | 33 | 0 |
| `GENM` | 33 | 0 |
| `GENM stock` | 35 | 4 |
| `GENM share price` | 31 | 2 |
| `4715` | 34 | 0 |
| `3182` | 37 | 0 |
| `genting stock analysis` | 38 | 18 |
| `genting bursa` | 32 | 6 |
| `genting klse` | 31 | 1 |
| `saham genting` | 43 | 14 |
| `saham genting jatuh` | 34 | 11 |
| `saham genm` | 31 | 2 |
| `genting rugi` | 32 | 5 |
| `genting untung` | 30 | 3 |
| `harga saham genting` | 36 | 11 |
| `analisis saham genting` | 33 | 8 |
| `genting rights issue saham` | 35 | 18 |
| `云顶` | 30 | 0 |
| `云顶大马` | 30 | 7 |
| `云顶股票` | 35 | 27 |
| `云顶 分析` | 30 | 20 |
| `云顶 股价` | 33 | 28 |
| `云顶 附加股` | 32 | 26 |
| `云顶 债务` | 33 | 16 |
| `云顶 业绩` | 31 | 16 |
| `hashtag #genting` | 31 | 0 |
| `hashtag #sahamgenting` | 42 | 15 |
| `hashtag #gentingstock` | 32 | 13 |
| `hashtag #bursa` | 33 | 0 |
| `hashtag #genm` | 33 | 1 |
| `genting 3182` | 30 | 0 |
| `genting 4715` | 30 | 1 |
| `genm 4715` | 31 | 0 |
| `genting stock news` | 34 | 19 |
| `genting share price today` | 33 | 17 |
| `genting privatisation` | 32 | 3 |
| `genm privatisation` | 29 | 1 |
| `genting warrant` | 28 | 6 |
| `genting cash call` | 30 | 0 |
| `genting bonds` | 32 | 4 |
| `genting analyst` | 32 | 7 |
| `genting malaysia share` | 33 | 0 |
| `genting bhd` | 42 | 5 |
| `harga saham genm` | 31 | 0 |
| `saham genting hari ini` | 31 | 5 |
| `genting 附加股` | 30 | 14 |
| `genting 凭单` | 34 | 4 |
| `genting 私有化` | 32 | 10 |
| `genting 股息` | 30 | 12 |
| `genting 财报` | 31 | 23 |
| `genting 业绩` | 0 | 0 |
| `云顶 3182` | 31 | 6 |
| `云顶 4715` | 31 | 11 |
| `云顶 私有化` | 0 | 0 |
| `云顶 股息` | 32 | 24 |
| `云顶 财报` | 33 | 22 |
| `genting 2025` | 34 | 0 |
| `genting 2024` | 41 | 0 |
| `genting stock 2025` | 35 | 7 |
| `genting stock 2024` | 36 | 7 |
| `genting results 2025` | 0 | 0 |
| `genting dividend 2025` | 30 | 9 |
| `genm 2025` | 35 | 0 |
| `genm privatisation offer` | 42 | 1 |
| `genting privatisation offer` | 36 | 1 |
| `genting rm2.35` | 30 | 3 |
| `genting takeover offer` | 36 | 6 |
| `genting share buyback` | 32 | 15 |
| `云顶 2025` | 0 | 0 |
| `云顶 2024` | 0 | 0 |
| `云顶 收购` | 32 | 12 |
| `云顶 附加股 2026` | 30 | 19 |
| `云顶 供股` | 33 | 28 |
| `genting minority shareholders` | 28 | 13 |
| `genting delisting` | 29 | 8 |
| `genting share suspension` | 30 | 5 |
| `genting trading halt` | 30 | 6 |
| `genting egm` | 31 | 0 |
| `genting agm 2025` | 34 | 0 |
| `genting lawsuit` | 35 | 8 |
| `genting family feud` | 30 | 2 |
| `genting 林国泰` | 34 | 19 |
| `云顶 股东大会` | 30 | 19 |
| `云顶 停牌` | 33 | 14 |
| `云顶 私有化 2025` | 31 | 10 |

Queries that returned TikTok status `203` on every retry and were left uncovered (they are included in the table with 0 results):

- `genting 业绩` — status 203 after four attempts
- `云顶 私有化` — status 203 after four attempts
- `genting results 2025` — status 203 after four attempts
- `云顶 2025` — status 203 after four attempts
- `云顶 2024` — status 203 after four attempts

Status 203 is TikTok's generic risk/empty-response code; a 2–6 s backoff and up to four attempts did not clear it for these labels. Every other query succeeded, including close variants that cover the same topic.

The per-query kept counts overlap: a video can appear in several searches, and the column counts written posts that appeared in that result page.

Unique videos discovered: **1,429**. Relevant after keyword filter and manual review: **85**. Fetched: **85**. Excluded before fetching: **1344** (no Genting mention, no stock language, travel/consumer, Kamen Rider, or manual review).

## Volume by month

| Month | Posts uploaded | Comments posted |
| --- | ---: | ---: |
| 2022-09 | 1 | 0 |
| 2024-07 | 1 | 0 |
| 2024-11 | 0 | 1 |
| 2024-12 | 1 | 0 |
| 2025-01 | 1 | 7 |
| 2025-02 | 1 | 0 |
| 2025-03 | 1 | 12 |
| 2025-05 | 0 | 9 |
| 2025-06 | 1 | 4 |
| 2025-07 | 0 | 1 |
| 2025-08 | 0 | 1 |
| 2025-10 | 7 | 309 |
| 2025-11 | 5 | 37 |
| 2025-12 | 0 | 8 |
| 2026-01 | 0 | 3 |
| 2026-02 | 0 | 1 |
| 2026-03 | 2 | 4 |
| 2026-04 | 2 | 4 |
| 2026-05 | 1 | 1 |
| 2026-06 | 1 | 11 |
| 2026-07 | 3 | 10 |
| 2026-08 | 3 | 2 |
| 2026-09 | 1 | 113 |
| 2026-10 | 51 | 596 |
| 2026-11 | 1 | 11 |

The two pre-window uploads appear under their real upload months (2022-09 and 2024-07); their comments are counted under the months they were posted, all inside the collection window.

## Videos collected

| Video | Author | Ticker | Uploaded | Likes | Comments (meta) | Top-level | Replies | In window |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| [7703017769343749384](https://www.tiktok.com/@xinxifdngzn/video/7703017769343749384) 云顶赌场帝国股价暴跌百分之十七，砸出二十年新低只剩一点五六令吉，掌门人林国泰紧急增持持股推到四成半，发新股筹资十二亿五千万还债，帝国转型阵痛看得见。 #财经 #经济 #fyp #T | @xinxifdngzn | UNKNOWN | 2026-11-01 | 69 | 1 | 1 | 0 | 1 |
| [7702031071894031617](https://www.tiktok.com/@shuzigpvyjq/video/7702031071894031617) 云顶摊上事了，十月中旬公司宣布要发附加股筹十二亿五千万令吉，消息一出市场直接用脚投票，股价被抛压砸得抬不起头#云顶 #财经 #马来西亚 #林国泰 #fyp | @shuzigpvyjq | UNKNOWN | 2026-10-29 | 193 | 4 | 4 | 0 | 4 |
| [7701932336161574165](https://www.tiktok.com/@bursamarketrookie/video/7701932336161574165) #GENTING #GENM #爆量了过后双双反弹 #还是要看看这波反弹可以持续多久啊 ＃马股交易 ＃BURSA | @bursamarketrookie | GENM | 2026-10-29 | 3 | 0 | 0 | 0 | 0 |
| [7701919467269278994](https://www.tiktok.com/@shuziduc9kf/video/7701919467269278994) 云顶集团老板林国泰这两天有个新动作.....#云顶集团 #林国泰 #财经 #fyp #马来西亚 | @shuziduc9kf | GENTING | 2026-10-29 | 50 | 1 | 1 | 0 | 1 |
| [7701607832591944966](https://www.tiktok.com/@adele.espinosa8/video/7701607832591944966) 云顶跌倒23年历史最低！林国泰父子砸900万抄底，别人恐惧，他贪婪！#马来西亚#云顶#股票#财经#fyp | @adele.espinosa8 | UNKNOWN | 2026-10-28 | 17 | 0 | 0 | 0 | 0 |
| [7701291417187912967](https://www.tiktok.com/@priscilla.dejesus4/video/7701291417187912967) 云顶跌到23年最低！林国泰父子砸900万抄底，别人恐惧他贪婪！#马来西亚 #云顶 #股票 #抄底 #投资 | @priscilla.dejesus4 | UNKNOWN | 2026-10-27 | 840 | 30 | 30 | 0 | 30 |
| [7701225101663931700](https://www.tiktok.com/@talk6885/video/7701225101663931700) 豪门二代不啃老，反手扫货自家股票，云顶集团二级市场增持，海外赌场项目大动作。#马来西亚 | @talk6885 | GENTING | 2026-10-27 | 134 | 4 | 4 | 0 | 4 |
| [7700059782526291220](https://www.tiktok.com/@shuzitmxkus/video/7700059782526291220) 曾经风光无限的云顶，现在要靠卖海外赌场股权回血，林国泰正在和中东主权基金悄悄谈判 #云顶 #林国泰 #马来西亚 #fyp #财经 | @shuzitmxkus | UNKNOWN | 2026-10-24 | 13 | 0 | 0 | 0 | 0 |
| [7700057326203440405](https://www.tiktok.com/@shuziofilim/video/7700057326203440405) 林国泰，正在和中东主权基金秘密谈判，打算卖掉云顶海外赌场度假村的部分股权 #林国泰 #中东主权基金 #云顶海外度假村 #马来西亚 #fyp | @shuziofilim | UNKNOWN | 2026-10-24 | 341 | 8 | 8 | 0 | 8 |
| [7700048548334816520](https://www.tiktok.com/@liwenyydkq9/video/7700048548334816520) 云顶股价近20年低位，林国泰家族筹12.5亿令吉偿债 #马来西亚 #云顶 #林国泰 #林梧桐 #债务 #财经 #fyp | @liwenyydkq9 | UNKNOWN | 2026-10-24 | 173 | 6 | 6 | 0 | 6 |
| [7699745258770353429](https://www.tiktok.com/@shoujttwcyu/video/7699745258770353429) 林国泰正在和中东主权基金秘密谈判，打算卖掉云顶海外赌场度假村的部分股权，一口气套现 32 亿令吉 #林国泰 #中东主权基金 #云顶赌场 #fyp #财经 | @shoujttwcyu | UNKNOWN | 2026-10-23 | 479 | 10 | 9 | 0 | 9 |
| [7699738036636273927](https://www.tiktok.com/@9w2lsn/video/7699738036636273927) 关于“谁获得了云顶集团30%的土著股份”这一提问，在马来西亚商业史和法律法规中需要区分国家整体政策配额与公司实际股权结构： 1. 马来西亚“30%土著股权”政策背景 马来西亚自19 | @9w2lsn | UNKNOWN | 2026-10-23 | 28 | 9 | 7 | 1 | 8 |
| [7699421028094627092](https://www.tiktok.com/@paerdvfu2ta/video/7699421028094627092) 云顶集团的林国泰最近被曝出，正在和中东一家主权基金谈判，计划出售云顶海外赌场度假村部分股权 #云顶集团 #林国泰 #fyp #马来西亚 #财经 | @paerdvfu2ta | GENTING | 2026-10-22 | 176 | 2 | 2 | 0 | 2 |
| [7699417740947279122](https://www.tiktok.com/@mahadsyhwt6/video/7699417740947279122) 云顶股价趴在二十年低位，自家老板林国泰出手了，建发实业一路增持到百分之四十五点二四，十七亿四千万股，老板在跟市场对赌翻身。 #财经 #经济 #fyp #TikTok #马来西亚 | @mahadsyhwt6 | UNKNOWN | 2026-10-22 | 298 | 10 | 10 | 0 | 10 |
| [7699342807756066049](https://www.tiktok.com/@beatriceatkins/video/7699342807756066049) 云顶林家爆发豪门股权之争！对簿公堂争的从来不是钱本身？#豪门 #股权 #云顶 #财经 #商业思维 #马来西亚 | @beatriceatkins | UNKNOWN | 2026-10-22 | 29 | 0 | 0 | 0 | 0 |
| [7698658019978300680](https://www.tiktok.com/@dausdkofficial/video/7698658019978300680) Saham Genting jatuh 23% dalam SATU HARI! Kejatuhan paling teruk sejak 1998. Syarikat sebes | @dausdkofficial | UNKNOWN | 2026-10-20 | 1915 | 61 | 46 | 15 | 61 |
| [7697823815954369793](https://www.tiktok.com/@liwenyydkq9/video/7697823815954369793) 云顶12.5亿令吉供股，股价一天跌22.87%？ #云顶 #马来西亚 #供股 #财经 #fyp | @liwenyydkq9 | UNKNOWN | 2026-10-18 | 42 | 2 | 2 | 0 | 2 |
| [7697472849371516176](https://www.tiktok.com/@z1097951xcx/video/7697472849371516176) 谁能想到，曾经被大家视作大马传奇的云顶博彩帝国，现在要向股东伸手借钱了。 #马来西亚 #云顶 #博彩 #fyp #财经 | @z1097951xcx | UNKNOWN | 2026-10-17 | 27 | 0 | 0 | 0 | 0 |
| [7697463252896271637](https://www.tiktok.com/@shuzitmxkus/video/7697463252896271637) 云顶，马来西亚最大的博彩帝国，如今也要向市场借钱。林国泰执掌的云顶集团官宣配股，计划筹资十二亿五千万令吉。 #云顶 #马来西亚 #林国泰 #云顶集团 #fyp | @shuzitmxkus | GENTING | 2026-10-17 | 93 | 4 | 4 | 0 | 4 |
| [7697085496110992646](https://www.tiktok.com/@jianyrqrrht/video/7697085496110992646) 印钞机巨头竟借钱还债，云顶发附加股股价单日暴跌22% #财经 #经济 #fyp #马来西亚 #云顶 | @jianyrqrrht | UNKNOWN | 2026-10-16 | 22 | 0 | 0 | 0 | 0 |
| [7697083899523992833](https://www.tiktok.com/@noro4556/video/7697083899523992833) 云顶帝国开始借钱了，配股筹资十二亿五千万令吉，股价暴跌百分之十七，一块五毛六创二十八年最大单日跌幅，印钞机竟成碎钞机 #财经 #经济 #fyp #TikTok #马来西亚 | @noro4556 | UNKNOWN | 2026-10-16 | 964 | 26 | 21 | 5 | 26 |
| [7696730900725288212](https://www.tiktok.com/@xqd983454w6/video/7696730900725288212) 云顶林家上演家族内战，孙辈告林国泰争控制权 #财经 #经济 #fyp #马来西亚 | @xqd983454w6 | UNKNOWN | 2026-10-15 | 108 | 6 | 6 | 0 | 6 |
| [7696720893849931014](https://www.tiktok.com/@liwenyydkq9/video/7696720893849931014) 云顶林家内斗升级，孙辈把林国泰告上法庭？ #云顶集团 #马来西亚 #家族 #财经 #fyp | @liwenyydkq9 | GENTING | 2026-10-15 | 357 | 11 | 12 | 0 | 12 |
| [7696499021115870516](https://www.tiktok.com/@timtiah/video/7696499021115870516) From RM7 billion in excess cash to almost RM28 billion more debt than cash. Genting shares | @timtiah | UNKNOWN | 2026-10-14 | 326 | 14 | 13 | 1 | 14 |
| [7696348306447895826](https://www.tiktok.com/@stocklah/video/7696348306447895826) Genting Berhad #stocklah #pelaburan #sahammalaysia #BursaMalaysia #genting | @stocklah | GENTING | 2026-10-14 | 141 | 5 | 4 | 0 | 4 |
| [7696297991052791048](https://www.tiktok.com/@listentolee77/video/7696297991052791048) 🚨 **云顶大马（4715）暴跌17%！母公司筹钱，子公司也遭殃？** 😱 10月12日，云顶系股票遭遇猛烈抛售！ 📉 云顶集团（3182）暴跌22.87% 📉 云顶大马（4715 | @listentolee77 | UNKNOWN | 2026-10-13 | 44 | 0 | 0 | 0 | 0 |
| [7696097951428414772](https://www.tiktok.com/@yoko01836/video/7696097951428414772) 告诉你个大瓜，马来西亚顶级华人家族云顶林家，现在自家内部彻底闹翻了。林梧桐的孙辈直接把林国泰告上法庭，硬刚争夺云顶集团的控制权。另一边，林梧桐女儿林秀琼那笔 16 亿令吉的遗产官司 | @yoko01836 | GENTING | 2026-10-13 | 28 | 2 | 2 | 0 | 2 |
| [7696097690232311046](https://www.tiktok.com/@boss73994/video/7696097690232311046) 你敢信吗？云顶林家，马来西亚最有钱的华人家族之一，现在自己人打起来了，林梧桐的孙辈，把叔伯告上法庭，争的是云顶的控制权，另一边，林梧桐女儿林秀琼那十六亿令吉的遗产案，也闹得不可开交 | @boss73994 | GENTING | 2026-10-13 | 77 | 1 | 1 | 0 | 1 |
| [7696016341442039048](https://www.tiktok.com/@listentolee77/video/7696016341442039048) 🚨 **云顶（Genting 3182）一天暴跌22.87%！** 从RM1.88跌到RM1.45！📉 很多人第一反应：跌这么多，可以捡便宜了吗？🤔 但这次暴跌，背后可不简单！ 💥 | @listentolee77 | GENTING | 2026-10-13 | 142 | 16 | 6 | 6 | 12 |
| [7696084200243432725](https://www.tiktok.com/@leonaci9366939/video/7696084200243432725) Genting一天蒸发22.87%! 供股稀释18%, 股价还会跌? #云顶股票 #马股散户 #云顶暴跌 #股票抄底 #供股风险 | @leonaci9366939 | UNKNOWN | 2026-10-13 | 30 | 2 | 2 | 0 | 2 |
| [7696080330310061332](https://www.tiktok.com/@holdenfang5/video/7696080330310061332) 马股散户注意 Genting跌到20年低位,现在抄底还是Cut Loss? #云顶股票 #马股散户 #云顶暴跌 #股票抄底 #供股风险 | @holdenfang5 | UNKNOWN | 2026-10-13 | 12 | 0 | 0 | 0 | 0 |
| [7696079609812618503](https://www.tiktok.com/@tahlialim75250/video/7696079609812618503) Genting一天暴跌22.87%! RM1.45到底是黄金坑还是接飞刀? #云顶集团 #马来西亚股票 #马股 #股票抄底 #附加股 | @tahlialim75250 | GENTING | 2026-10-13 | 22 | 1 | 1 | 0 | 1 |
| [7696079066838928648](https://www.tiktok.com/@remingtonchik5/video/7696079066838928648) Genting从RM1.88插水到RM1.45! 为什么大户还不敢接货? #云顶股票 #马股散户 #云顶暴跌 #股票抄底 #供股风险 | @remingtonchik5 | UNKNOWN | 2026-10-13 | 11 | 1 | 1 | 0 | 1 |
| [7696076649145683218](https://www.tiktok.com/@wtq2dtrjn4/video/7696076649145683218) 母公司云顶暴跌17%，新加坡云顶为什么只跌0.8%？#云顶 #新加坡云顶 #马来西亚云顶 #股票暴跌 #配股 #新加坡股市 | @wtq2dtrjn4 | UNKNOWN | 2026-10-13 | 65 | 0 | 0 | 0 | 0 |
| [7696058985127906578](https://www.tiktok.com/@tonianang43590/video/7696058985127906578) 马来西亚云顶暴跌17%，新加坡云顶为什么只跌0.8%？#云顶 #新加坡云顶 #马来西亚云顶 #股票暴跌 #配股 #新加坡股市 | @tonianang43590 | UNKNOWN | 2026-10-13 | 24 | 3 | 3 | 0 | 3 |
| [7696057270160887047](https://www.tiktok.com/@hwndympor6/video/7696057270160887047) 云顶一天暴跌17%，新加坡云顶为什么没跟着大跌？#云顶 #新加坡云顶 #马来西亚云顶 #股票暴跌 #配股 #新加坡股市 | @hwndympor6 | UNKNOWN | 2026-10-13 | 33 | 1 | 1 | 0 | 1 |
| [7696053672345734418](https://www.tiktok.com/@brandonsiu9991/video/7696053672345734418) 云顶一天暴跌17%，新加坡云顶为什么只跌了0.8%？#云顶 #新加坡云顶 #马来西亚云顶 #股票暴跌 #配股 #新加坡股市 | @brandonsiu9991 | UNKNOWN | 2026-10-13 | 114 | 3 | 3 | 0 | 3 |
| [7696053461204421895](https://www.tiktok.com/@francesseng41/video/7696053461204421895) 云顶一天暴跌17%，新加坡云顶为什么只跌了0.8%？#云顶 #新加坡云顶 #马来西亚云顶 #股票暴跌 #配股 #新加坡股市 | @francesseng41 | UNKNOWN | 2026-10-13 | 422 | 10 | 10 | 0 | 10 |
| [7696028751515225374](https://www.tiktok.com/@andyyew12/video/7696028751515225374) 云顶单日跌20%，是28年来最大的一次单日暴跌，你做么！？ 评论区留言 “GENTING" 我把图表发给你！ #gentinghighland #股票 #马股 #蓝筹股 #云顶 | @andyyew12 | UNKNOWN | 2026-10-13 | 30 | 1 | 1 | 0 | 1 |
| [7695976881241197876](https://www.tiktok.com/@paerdrhid0v/video/7695976881241197876) 云顶林家，马来西亚最有钱华人家族之一，现在自己人打起来了，林梧桐的孙辈把林国泰告上法庭 #云顶林家 #马来西亚 #林梧桐 #林国泰 #fyp | @paerdrhid0v | UNKNOWN | 2026-10-13 | 171 | 5 | 5 | 0 | 5 |
| [7695973046267514120](https://www.tiktok.com/@find56814/video/7695973046267514120) 云顶林家，马来西亚最有钱华人家族之一，现在自己人打起来了，林梧桐的孙辈把林国泰告上法庭 #马来西亚 #fyp #云顶林家 #林国泰 #华人 | @find56814 | UNKNOWN | 2026-10-13 | 2760 | 59 | 56 | 1 | 57 |
| [7695944113354558728](https://www.tiktok.com/@starbizmy/video/7695944113354558728) Genting’s shares plunged 23% in a single day, wiping out nearly RM1.7 billion in market va | @starbizmy | UNKNOWN | 2026-10-13 | 52 | 9 | 7 | 2 | 9 |
| [7695756501222247681](https://www.tiktok.com/@tradeforsaving/video/7695756501222247681) Saham Genting Bhd jatuh ke paras terendah hampir 2 dekad susulan cadangan right issues RM1 | @tradeforsaving | GENTING | 2026-10-12 | 2 | 0 | 0 | 0 | 0 |
| [7695713317549067538](https://www.tiktok.com/@marx6699/video/7695713317549067538) Genting暴跌22.9%！配股真是元凶吗？ 云顶集团（3182）股价突然跌至RM1.45，单日下跌22.9%。公司计划供股筹资RM12.5亿，其中RM8亿用于还债，市场担忧折价 | @marx6699 | GENTING | 2026-10-12 | 8 | 0 | 0 | 0 | 0 |
| [7695692221252750593](https://www.tiktok.com/@leonaci9366939/video/7695692221252750593) Genting跌到RM1.50多！现在抄底还是接刀？ #云顶股票 #马股分析 #股票砍仓 #马股散户 #附加股 | @leonaci9366939 | UNKNOWN | 2026-10-12 | 168 | 3 | 3 | 0 | 3 |
| [7695687079249988872](https://www.tiktok.com/@remingtonchik5/video/7695687079249988872) Genting暴跌近17%！亏30%的散户，现在应该砍仓吗？ #云顶股票 #马股分析 #股票砍仓 #马股散户 #附加股 | @remingtonchik5 | UNKNOWN | 2026-10-12 | 12 | 1 | 1 | 0 | 1 |
| [7695634409520663828](https://www.tiktok.com/@oh.my.bursa/video/7695634409520663828) 上个星期五的一张公告，让云顶 Genting 在星期一开市不到30分钟就蒸发了RM10亿市值。 供股集资RM12.5亿，当中RM8亿拿去还短期债务，听起来挺合理。 可是股价直接暴跌 | @oh.my.bursa | GENM | 2026-10-12 | 4 | 0 | 0 | 0 | 0 |
| [7695631359150230791](https://www.tiktok.com/@financemalaysia/video/7695631359150230791) 🤯🤯🤯 Focus of the Day: Genting Bhd 🤯🤯🤯 Genting Bhd fell to its lowest in nearly two decades | @financemalaysia | GENTING | 2026-10-12 | 8 | 0 | 0 | 0 | 0 |
| [7695612275172134164](https://www.tiktok.com/@sharetraders/video/7695612275172134164) Key Details of the Drop • The Cash Call: Genting announced a renounceable rights issue to  | @sharetraders | GENM | 2026-10-12 | 7 | 0 | 0 | 0 | 0 |
| [7695341690072075521](https://www.tiktok.com/@talk6885/video/7695341690072075521) 云顶林家自己人打起来了，林梧桐的孙辈把叔伯告上法庭争控制权，十六亿遗产案也闹得不可开交，豪门内斗比云顶赌局还刺激。 #财经 #经济 #fyp #TikTok #马来西亚 | @talk6885 | UNKNOWN | 2026-10-11 | 8380 | 232 | 207 | 18 | 225 |
| [7694979977657306389](https://www.tiktok.com/@oh.my.bursa/video/7694979977657306389) 云顶负债高达452亿，这次却是自己家族掏钱救自己？ 集团总负债达RM452.5亿，短期内就要还RM96.8亿。 云顶宣布供股集资RM12.5亿，当中RM8亿用来还债，每年省下RM4 | @oh.my.bursa | UNKNOWN | 2026-10-10 | 59 | 8 | 7 | 1 | 8 |
| [7694958498488012053](https://www.tiktok.com/@dindin_ong/video/7694958498488012053) 云顶可能向股东要12.5亿 你会掏钱买新股吗？ #云顶 | @dindin_ong | UNKNOWN | 2026-10-10 | 714 | 46 | 37 | 6 | 43 |
| [7683140446989618440](https://www.tiktok.com/@starbizmy/video/7683140446989618440) Genting was once worth RM41.5 billion. Today, it is worth less than RM8 billion. And now,  | @starbizmy | UNKNOWN | 2026-09-08 | 2417 | 113 | 84 | 35 | 119 |
| [7678917307447479572](https://www.tiktok.com/@listentolee77/video/7678917307447479572) 🔥 GENM 4715：营收暴增32%，净利却暴跌！美国业务能救回来吗？ GENM 4715 最新 2Q26 Financial Results 出炉！季度营收达到 RM3.85  | @listentolee77 | GENM | 2026-08-28 | 25 | 0 | 0 | 0 | 0 |
| [7677171803768294676](https://www.tiktok.com/@listentolee77/video/7677171803768294676) ‼️ 开赌场的都会亏钱？云顶发生什么事！ 📉 Genting 2026 Q2 重点 👍 营收：RM7.5 billion，同比增长约14% 🤣 净利润：去年 RM243.5m，今年 | @listentolee77 | GENM | 2026-08-23 | 6 | 0 | 0 | 0 | 0 |
| [7676700399964802324](https://www.tiktok.com/@oh.my.bursa/video/7676700399964802324) 斥资55亿美元打造的纽约赌场，云顶大马原本指望它成为新的摇钱树。 第二季营收大涨32%至RM38.5亿，净利润却暴跌89%，只剩RM4740万。 算上汇兑损失和高企营运成本，上半年 | @oh.my.bursa | GENM | 2026-08-22 | 0 | 0 | 0 | 0 | 0 |
| [7668536019246910740](https://www.tiktok.com/@listentolee77/video/7668536019246910740) 虽然公司 2026 财年第二季（2Q26） 业绩预计将面对压力，但分析员认为，这只是短期挑战。 📌 为什么第二季表现可能较弱？ 🔸 中东战争影响云顶世界云顶（RWG）及英国业务（G | @listentolee77 | GENM | 2026-07-31 | 0 | 0 | 0 | 0 | 0 |
| [7658189265444162823](https://www.tiktok.com/@_moneypov/video/7658189265444162823) 纽约项目、私有化传闻、股东问题 👀 你觉得云顶最大增长点会是什么？I heard this directly from management, not from headlines | @_moneypov | UNKNOWN | 2026-07-04 | 145 | 10 | 8 | 0 | 8 |
| [7658294482034609415](https://www.tiktok.com/@stocklah/video/7658294482034609415) Tan Sri Lim Kok Thay #stocklah #BursaMalaysia #infosaham #sahammalaysia #genting | @stocklah | UNKNOWN | 2026-07-03 | 478 | 2 | 1 | 2 | 3 |
| [7648972237172755719](https://www.tiktok.com/@financialfaiz/video/7648972237172755719) Genting Highlands dah ada tol Ada pengumuman baru-baru ini yang jalan nak ke Genting Highl | @financialfaiz | UNKNOWN | 2026-06-08 | 681 | 14 | 9 | 3 | 12 |
| [7638545373530770708](https://www.tiktok.com/@kleverstockmy/video/7638545373530770708) Genting Bhd has entered into a strategic partnership with Indonesian energy player PT Ruku | @kleverstockmy | GENTING | 2026-05-11 | 9 | 1 | 1 | 0 | 1 |
| [7634523658026765586](https://www.tiktok.com/@financemalaysia/video/7634523658026765586) (Breaking News) STOPPED 🚫🚫🚫 The High Court here has ruled in favour of Genting Malaysia Gr | @financemalaysia | GENM | 2026-04-30 | 14 | 0 | 0 | 0 | 0 |
| [7633207726075677960](https://www.tiktok.com/@starbizmy/video/7633207726075677960) Genting Bhd’s latest bond issue signals possible challenges for future dividends. While it | @starbizmy | UNKNOWN | 2026-04-26 | 53 | 3 | 3 | 0 | 3 |
| [7615160629166476552](https://www.tiktok.com/@saysdotcom/video/7615160629166476552) Several social media users have reported passing through the newly built Genting Highlands | @saysdotcom | GENM | 2026-03-09 | 188 | 5 | 4 | 0 | 4 |
| [7612875868469284104](https://www.tiktok.com/@starbizmy/video/7612875868469284104) PETALING JAYA: Genting Bhd’s core net profit (CNP) is expected to see a rise in the financ | @starbizmy | UNKNOWN | 2026-03-03 | 8 | 0 | 0 | 0 | 0 |
| [7575850476369988880](https://www.tiktok.com/@finance.lang/video/7575850476369988880) Finance Lang x 财经随便聊 EP16｜云顶大马选择私有化 散户是卖还是不卖？ 云顶大马选择私有化 手上还持有他们股份的散户们到底应不应该卖呢？我们一起来看看投资银行怎 | @finance.lang | GENM | 2025-11-23 | 380 | 5 | 5 | 0 | 5 |
| [7573528654140017921](https://www.tiktok.com/@pocketimes/video/7573528654140017921) 疫情前的云顶站在巅峰；全球停摆时，它从高原跌入寒冬；而在重开之后，复苏的脚步仍步步惊心。如今，林国泰的67亿之举是重整布局，还是另一场豪赌？ #百格 #Pocketimes #云顶 | @pocketimes | UNKNOWN | 2025-11-17 | 782 | 9 | 7 | 2 | 9 |
| [7572148154917752082](https://www.tiktok.com/@financemalaysia/video/7572148154917752082) 𝗚𝗲𝗻𝘁𝗶𝗻𝗴 𝗠𝗮𝗹𝗮𝘆𝘀𝗶𝗮 𝗕𝗵𝗱 (#GENM) has confirmed that there will be charges for vehicles enterin | @financemalaysia | GENM | 2025-11-13 | 6 | 0 | 0 | 0 | 0 |
| [7568699761243557140](https://www.tiktok.com/@sharetraders/video/7568699761243557140) KUALA LUMPUR (Nov 3): Genting Bhd said its takeover offer for Genting Malaysia Bhd has bec | @sharetraders | UNKNOWN | 2025-11-04 | 15 | 0 | 0 | 0 | 0 |
| [7568428352743230740](https://www.tiktok.com/@pocketimes/video/7568428352743230740) 从“高原梦”到“资本战”，云顶传奇再起波澜。六十年前，一个名叫林梧桐的福建青年，在荒山上种下了他的梦想，云顶高原。他靠着一股执念，从卖茶叶、种菜的普通劳工，变成开路筑梦的“Uncl | @pocketimes | GENTING | 2025-11-03 | 307 | 3 | 3 | 0 | 3 |
| [7561787190934506759](https://www.tiktok.com/@sense.and.cents/video/7561787190934506759) Tan Sri Lim Kok Thay is buying out Genting Malaysia. So, is this a Fair Deal or Daylight r | @sense.and.cents | GENM | 2025-10-16 | 686 | 51 | 32 | 18 | 50 |
| [7561756636679802130](https://www.tiktok.com/@dausdkofficial/video/7561756636679802130) Genting Berhad Nak privatekan company diorang? Eh Apa Dah Jadi ni? Haa Jom Daus explain #d | @dausdkofficial | GENTING | 2025-10-16 | 3118 | 88 | 68 | 20 | 88 |
| [7560853318298324242](https://www.tiktok.com/@starbizmy/video/7560853318298324242) PETALING JAYA: Genting Bhd’s offer to privatise Genting Malaysia Bhd at RM2.35 per share i | @starbizmy | UNKNOWN | 2025-10-13 | 90 | 0 | 0 | 0 | 0 |
| [7560696855181479189](https://www.tiktok.com/@pocketimes/video/7560696855181479189) 云顶集团今日（10月13日）丢出重磅消息，宣布将以超过67亿令吉的总代价全面收购旗下子公司云顶大马的所有剩余股权并想要私有化…… #百格 #Pocketimes #百格新闻 #云顶 | @pocketimes | UNKNOWN | 2025-10-13 | 3653 | 67 | 34 | 7 | 41 |
| [7560663879949356295](https://www.tiktok.com/@wuchangtan/video/7560663879949356295) 很臭，很多散戶買6元堅持10年了 結果答案不是回本 是被吃！ 這樣有錢的tan Sri 都喜歡吃人！ 老實說，看了很不爽！ #股票 #genm | @wuchangtan | GENM | 2025-10-13 | 16 | 0 | 0 | 0 | 0 |
| [7560638383882636562](https://www.tiktok.com/@sharetraders/video/7560638383882636562) In a bourse filing, the group said it is proposing to privatise Genting Malaysia via the a | @sharetraders | GENM | 2025-10-13 | 4 | 0 | 0 | 0 | 0 |
| [7560554639620377864](https://www.tiktok.com/@elainetan.1988/video/7560554639620377864) 🤔🤔🤔云顶发生什么事情，原来是股票停牌。。。 | @elainetan.1988 | UNKNOWN | 2025-10-13 | 1114 | 159 | 61 | 98 | 159 |
| [7519523008369806600](https://www.tiktok.com/@davechongdkic/video/7519523008369806600) 云顶人潮爆满，股价却不涨，你觉得为什么？ 📊 我在影片里讲了散户都忽略的重点 ⬇️ 评论告诉我，你有没有中招？ #davechong #dkic #dkinvestorclub # | @davechongdkic | UNKNOWN | 2025-06-24 | 101 | 4 | 3 | 1 | 4 |
| [7484490220897930514](https://www.tiktok.com/@neoinvestment/video/7484490220897930514) #投资 #股票 #马股 #云顶 #云顶大马 #genting #gentinghighlands #gentingmalaysia #林国泰 #财经 #股市 #CEO | @neoinvestment | GENM | 2025-03-22 | 486 | 22 | 8 | 9 | 17 |
| [7476605504475680007](https://www.tiktok.com/@doubleswords/video/7476605504475680007) GENM 云顶大马 暴量大跌不急捞#stock #股票 #stockstobuy #technicalanalysis #genting | @doubleswords | GENM | 2025-02-28 | 143 | 4 | 4 | 0 | 4 |
| [7455069800834878728](https://www.tiktok.com/@1stockaxia/video/7455069800834878728) 2025 genting lulus ✅️ | @1stockaxia | UNKNOWN | 2025-01-01 | 87 | 7 | 3 | 4 | 7 |
| [7445524380982971665](https://www.tiktok.com/@ctc.fm/video/7445524380982971665) Genting Berhad dan Genting Malaysia Berhad mungkin akan disingkarkan daripada menjadi seba | @ctc.fm | UNKNOWN | 2024-12-07 | 26 | 0 | 0 | 0 | 0 |
| [7394061312420023558](https://www.tiktok.com/@rita_efendy/video/7394061312420023558) Genting Malaysia beli lahan di Sentul City seharga Rp 2 triliun! 🎉 Dengan luas total 152 h | @rita_efendy | GENM | 2024-07-21 | 1811 | 128 | 96 | 31 | 6 |
| [7145701989320559898](https://www.tiktok.com/@aibusinessmy/video/7145701989320559898) #genting Malaysia kidnap kids viral to everyone to go Genting #云顶有骗小孩案例赶紧转发#4715和3182股价会不会 | @aibusinessmy | UNKNOWN | 2022-09-21 | 1863 | 20 | 18 | 2 | 2 |

## Relevant videos checked but not written

None: every video that passed the relevance filter and manual review was fetched. One additional pre-window video, `7342865655047130369` (5 Mar 2024, 'Genting 3182 云顶今年很多大动作'), was fetched but had no in-window comments and is therefore not written.

## Coverage and gaps

1229 records were written from 84 videos. No video recorded an API error; every comment page and reply page returned `status_code: 0`.

Videos where the retrieved set (top-level + replies) differs from the API `total`:

| Video | Meta comments | API total | Top-level | Replies | Retrieved | Difference |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 7695341690072075521 | 232 | 232 | 207 | 18 | 225 | +7 |
| 7683140446989618440 | 113 | 113 | 84 | 35 | 119 | -6 |
| 7695973046267514120 | 59 | 59 | 56 | 1 | 57 | +2 |
| 7648972237172755719 | 14 | 13 | 9 | 3 | 12 | +1 |
| 7394061312420023558 | 128 | 128 | 96 | 31 | 127 | +1 |

A positive difference means TikTok returned fewer comments than its own `total`: the public API omits folded/spam comments and some hidden replies (the response flags `has_filtered_comments`/`fold_status`), and deleted comments leave gaps. Across the affected videos this accounts for 11 comments. A negative difference means the retrieved set is larger than the (stale or top-level-only) API total; those extra records are real comments with ids and timestamps. No comment text was invented to close a gap.

## Pre-window uploads retained

These videos were uploaded before 2 Nov 2024 but received comments inside the collection window. They are kept so those in-window comments are not lost; the post `created_utc` is the real upload time and the validator flags them as outside the window.

| Video | Uploaded | Ticker | In-window comments |
| --- | --- | --- | ---: |
| [7394061312420023558](https://www.tiktok.com/@rita_efendy/video/7394061312420023558) Genting Malaysia beli lahan di Sentul City seharga Rp 2 triliun! 🎉 Den | 2024-07-21 | GENM | 6 |
| [7145701989320559898](https://www.tiktok.com/@aibusinessmy/video/7145701989320559898) #genting Malaysia kidnap kids viral to everyone to go Genting #云顶有骗小孩案 | 2022-09-21 | UNKNOWN | 2 |

## Comment text quality

29 replies have an empty body and are stored as `[deleted]`; TikTok returned a comment object with no text (sticker/emoji-only or removed). 246 non-empty reply bodies exactly repeat another reply's text; these are distinct comment ids (typically short reactions such as emoji, 'same', or thanks) and are kept. Neither case is a validation error, only a warning.

## Limitations

- TikTok's web search returns about 30 results per query and is recency-biased; 1,429 unique videos were discovered, but this is not an exhaustive index of every Genting video posted in the two years. Coverage is dense around the October 2025 GENM privatisation offer and the October 2026 rights-issue crash, and sparse in quiet months.
- The public comment API hides folded/spam comments and some replies. Those are missing from the file rather than guessed; the reconciliation table lists every video with a difference.
- Five search labels returned TikTok status 203 on every attempt and have no results; close variants of all five succeeded. No captcha was shown and no captcha-solving technique was used.
- Comment counts and like counts are a snapshot at collection time and will drift. Deleted comments are stored as `[deleted]` and counted as empty bodies.
- Only public reading was performed: no account, no login, no posting, no SQLite writes. The JSONL is the sole output.

## Exclusions

Search results included Genting Highlands travel/theme-park vlogs, casino clips, Kamen Rider 'Genm' edits and unrelated videos that merely used the word 'genting'. A video was kept only when its **caption** (not just a hashtag) contained Genting or GENM plus stock/market language; travel-heavy captions without stock language were dropped. Generic market round-ups that mention Genting only in passing were also dropped. A second manual pass removed items the keyword filter could not distinguish: hotel/theme-park/outlet promotions, jewellery-robbery news, property adverts, the Lim family inheritance dispute, Indonesian RAJA/RATU energy posts where Genting is only a counterparty, and Genting Hong Kong (not Bursa 3182/4715). The full 1,429-video set with a reason for each is in `/tmp/opencode/genting/tt/build_videos.json`; reviewed exclusions are in `/tmp/opencode/genting/tt/overrides.json`.

## Ticker assignment

`GENM` is used when the caption names GENM, 4715, 'Genting Malaysia' or 云顶大马; `GENTING` when it names Genting Berhad/Bhd, 3182, 云顶集团 or 云顶有限公司. Captions that name both, or only the generic group name 'Genting'/'云顶', are `UNKNOWN` rather than guessing which listed entity is meant. This is why `UNKNOWN` is the largest bucket.

