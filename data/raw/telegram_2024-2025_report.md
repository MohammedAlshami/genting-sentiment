# Telegram — 2024-2025 backfill report

Public Telegram channel previews (`https://t.me/s/<username>`), searched with the preview keyword filter (`?q=...`) and paginated with `&before=<id>`.
Source id is `telegram`; each message is a **post**, not a comment.

This is the **backfill** for the missing earlier year. It is separate from `data/raw/telegram.jsonl` (2025-11-04 → 2026-10-30), which was not modified.

Window: **2024-11-02 → 2025-11-01 inclusive**, interpreted in Malaysia time (UTC+8): `created_utc` 1730476800–1762012799.

## Requests

- Channels attempted: **49**
- Channels with a usable public preview: **48**
- Search page fetches (including cached reads): **395**
- Search pages parsed: **206**
- Unique posts scanned across all keyword searches: **1528**
- In-window keyword candidates before content filtering: **233**
- Records written: **108**

Keywords used per channel: `genting`, `genm`, `3182`, `4715`, `云顶`, `lim kok thay`, `resorts world`. Results were deduplicated by `(channel, message id)`. At least 1.2 s between HTTP requests; HTTP 429/5xx responses were retried with exponential back-off.

## Channels checked

| Channel | Title | Subscribers | Posts scanned | Genting candidates | Kept | Oldest hit | Newest hit |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| @bursakakis | BursaKakis Channel 👣 | 13500 | 101 | 16 | 4 | 2016-09-19 00:41 UTC | 2026-10-16 23:15 UTC |
| @cgsi_my | CGS International Securities Malaysia | 10900 | 65 | 8 | 8 | 2022-01-20 00:20 UTC | 2026-10-18 23:45 UTC |
| @UOBKayHianMalaysia | UOB Kay Hian Malaysia (Official) | 8570 | 42 | 12 | 0 | 2023-11-16 00:32 UTC | 2025-07-03 00:31 UTC |
| @maahadbursa | Maahad Bursa | 10900 | 2 | 0 | 0 | 2020-12-19 01:24 UTC | 2021-06-19 23:50 UTC |
| @AsriAhmadAcademy | Asri Ahmad Academy | 33800 | 0 | 0 | 0 | n/a | n/a |
| @SahamMastery | Saham Mastery Channel | 3560 | 4 | 0 | 0 | 2020-07-01 08:25 UTC | 2022-06-10 04:19 UTC |
| @bursamalaysiaofficial | Bursa Malaysia | 15000 | 23 | 1 | 1 | 2022-10-11 00:58 UTC | 2025-02-26 09:00 UTC |
| @duniasaham | Dunia Saham Bursa (Stocks) | 1010 | 6 | 0 | 0 | 2018-01-20 11:49 UTC | 2022-01-30 16:10 UTC |
| @pedagangbursa | Pedagang Bursa | 2070 | 34 | 0 | 0 | 2018-08-07 12:04 UTC | 2022-03-11 00:32 UTC |
| @BursaKLSEsignals | — | — | 0 | 0 | 0 | n/a | n/a |
| @ipobursa | Bursa IPO Updates | 2790 | 0 | 0 | 0 | n/a | n/a |
| @duniafcpo | Dunia FCPO (Palm Oil) | 1570 | 2 | 0 | 0 | 2019-09-30 19:10 UTC | 2020-01-20 04:38 UTC |
| @BURSAMASTER_BULLSEYE | BURSAMASTER CHANNEL 🌈 | 12800 | 14 | 0 | 0 | 2015-11-30 11:59 UTC | 2021-08-05 05:06 UTC |
| @sahambursa | Channel Along | 3470 | 5 | 0 | 0 | 2019-06-22 08:09 UTC | 2020-09-01 09:17 UTC |
| @saham_the_insider | Saham Insider BSKL | 4200 | 1 | 0 | 0 | 2022-12-17 09:16 UTC | 2022-12-17 09:16 UTC |
| @bursaFATA | 默泰然马股分享区 | 2340 | 22 | 0 | 0 | 2018-10-22 07:49 UTC | 2022-01-08 03:36 UTC |
| @BursaMalaysiaTopGainer | BSKL Top Chart & Trading Idea for Bursa Malaysia | 1260 | 3 | 0 | 0 | 2020-05-30 13:09 UTC | 2022-02-04 00:54 UTC |
| @bursatrades | InvestMy | 827 | 3 | 0 | 0 | 2020-08-27 12:32 UTC | 2020-09-17 13:11 UTC |
| @Bursa_Fx_KLSE_Inv | 📊 BURSA FX INVESTING 📊 | 139 | 3 | 0 | 0 | 2020-09-15 16:30 UTC | 2020-10-30 12:50 UTC |
| @klsealert | Public KLSE Alert | 3760 | 39 | 0 | 0 | 2022-04-22 08:52 UTC | 2022-07-21 08:43 UTC |
| @KLSETA | Elliot Wave Technical Analysis | 3230 | 33 | 0 | 0 | 2017-08-04 00:55 UTC | 2020-03-15 13:07 UTC |
| @klseDIVIDENDvsTRENDstock | 投资理财的记忆 频道 | 2220 | 7 | 0 | 0 | 2021-03-17 09:17 UTC | 2024-01-09 00:53 UTC |
| @klseinsidertips | Warrior Traders 🔥 | 1260 | 0 | 0 | 0 | n/a | n/a |
| @klsestockmarket2 | 财经头条 | 1110 | 101 | 6 | 2 | 2022-12-13 15:12 UTC | 2025-10-20 09:35 UTC |
| @superbullklsechannel | 【公开广播 Public Broadcast】 牛转钱坤 Superbull | 4420 | 33 | 2 | 2 | 2020-12-15 10:23 UTC | 2025-05-14 09:26 UTC |
| @DoubleSwordsKLSE | 双剑合璧KLSE吹水站 Channel | 2120 | 42 | 15 | 12 | 2025-05-30 02:16 UTC | 2026-10-30 09:28 UTC |
| @B2MKLSE | B2M KLSE Bursa Saham | 704 | 10 | 0 | 0 | 2017-03-17 00:57 UTC | 2020-11-11 00:28 UTC |
| @itchyitchytraderclub | itchy itchy Trader club ( iiTc ) | 3630 | 136 | 15 | 4 | 2018-02-28 00:48 UTC | 2026-10-29 23:32 UTC |
| @mplusOTG | M+ On-The-Go | 26200 | 53 | 17 | 1 | 2018-11-05 09:21 UTC | 2026-10-12 09:28 UTC |
| @TradewithMaybank | Trade With Maybank | 25400 | 51 | 23 | 14 | 2022-06-17 00:00 UTC | 2026-10-13 00:01 UTC |
| @RHBInvestmentBankOfficial | RHB Investment Bank Official | 20300 | 25 | 1 | 0 | 2021-04-21 02:00 UTC | 2025-08-29 09:41 UTC |
| @FinancialFaiz | Financial Faiz | 21900 | 0 | 0 | 0 | n/a | n/a |
| @infosahammalaysiachannel | Info Saham Malaysia 🇲🇾 Channel | 250 | 40 | 0 | 0 | 2021-06-25 14:29 UTC | 2024-01-05 00:12 UTC |
| @kelassahambursamsia | Kelas Saham Bursa Malaysia | 220 | 0 | 0 | 0 | n/a | n/a |
| @AffinHwangIBDailyBoost | Affin Hwang IB Daily Boost | 4360 | 25 | 8 | 0 | 2022-11-29 00:57 UTC | 2026-02-27 02:18 UTC |
| @MarhaenTrader8 | Marhaen Trader | 5060 | 39 | 0 | 0 | 2021-03-03 03:30 UTC | 2026-10-17 04:46 UTC |
| @PhillipCapitalStocks | Phillip Capital Stocks | 1530 | 35 | 11 | 1 | 2024-04-15 14:37 UTC | 2026-05-11 03:01 UTC |
| @amequities | AmEquities | 3540 | 54 | 2 | 2 | 2021-01-14 00:35 UTC | 2026-10-19 00:03 UTC |
| @fifointrabursa | FIFO - Intraday Bursa 📈 | 1120 | 16 | 1 | 0 | 2021-05-24 01:20 UTC | 2026-01-16 23:19 UTC |
| @ltadiary | Logic Trading Analysis Diary | 2930 | 2 | 0 | 0 | 2025-12-02 00:41 UTC | 2025-12-02 00:48 UTC |
| @market_demon | Market Demon | 19100 | 6 | 0 | 0 | 2022-07-15 13:50 UTC | 2025-11-13 10:24 UTC |
| @marketfeed | Market News Feed | 39500 | 62 | 0 | 0 | 2021-12-07 10:28 UTC | 2026-11-01 13:13 UTC |
| @mywealthfort | WealthFort Investing Channel | 622 | 50 | 12 | 12 | 2022-01-24 00:10 UTC | 2026-10-19 02:17 UTC |
| @newbietradingchannel | Newbie Trading Channel | 6450 | 94 | 19 | 18 | 2019-07-25 12:52 UTC | 2026-10-18 23:51 UTC |
| @sharesinfo4u | 十方财经 Sharesinfo4u.com | 3670 | 53 | 11 | 10 | 2023-02-23 13:44 UTC | 2026-10-13 07:13 UTC |
| @sharestraders | Share Traders | 2980 | 54 | 1 | 1 | 2018-11-27 01:14 UTC | 2026-10-20 10:04 UTC |
| @tcyapstockinvest | TCYap马股投资频道 ✨ 😎 | 8590 | 58 | 12 | 8 | 2020-06-16 12:51 UTC | 2026-10-12 05:59 UTC |
| @titanpublicchannel | Titan Trading Channel | US 🇺🇸 • MY 🇲🇾 • HK 🇭🇰 | 4460 | 39 | 27 | 8 | 2023-02-19 09:48 UTC | 2025-12-07 18:42 UTC |
| @trendbandcyclealert | ⚠️ TrendBand Cycle Alert | 1780 | 41 | 13 | 0 | 2025-07-24 10:05 UTC | 2026-10-29 10:22 UTC |

Channels where keyword search did **not** span the whole window (oldest/newest hit seen, including candidates later filtered out):

- @UOBKayHianMalaysia: 2023-11-16 00:32 UTC → 2025-07-03 00:31 UTC
- @bursamalaysiaofficial: 2022-10-11 00:58 UTC → 2025-02-26 09:00 UTC
- @superbullklsechannel: 2020-12-15 10:23 UTC → 2025-05-14 09:26 UTC
- @DoubleSwordsKLSE: 2025-05-30 02:16 UTC → 2026-10-30 09:28 UTC
- @RHBInvestmentBankOfficial: 2021-04-21 02:00 UTC → 2025-08-29 09:41 UTC
- @trendbandcyclealert: 2025-07-24 10:05 UTC → 2026-10-29 10:22 UTC
- **@DoubleSwordsKLSE search reaches back only to 2025-05-30 02:16 UTC**; the earlier part of the window is not covered for that channel.
- **@ltadiary search reaches back only to 2025-12-02 00:41 UTC**; the earlier part of the window is not covered for that channel.
- **@trendbandcyclealert search reaches back only to 2025-07-24 10:05 UTC**; the earlier part of the window is not covered for that channel.
- **No keyword search hits at all** (so no backfill coverage): @AsriAhmadAcademy, @ipobursa, @klseinsidertips, @FinancialFaiz, @kelassahambursamsia.

## Date range and ticker counts

- Earliest post written: **2024-11-08 01:16 UTC**
- Latest post written: **2025-10-30 02:06 UTC**
- Ticker counts: GENM=50, GENTING=56, UNKNOWN=2

## What the corpus contains

The backfill contains a mix of retail/technical-analysis posts, broker/research notes and business-news shares. The channel table shows which channels produced hits in this earlier year. Broker and news digests are kept only where the post contains a dedicated Genting paragraph, not a bare price list.

The same RHB brief can appear on several channels. Those are distinct channel posts (different `native_id`) and are kept separately; the contract's deduplication key is `(source, native_id)`, not body text.

## Method and fields

- `native_id` = `<username>/<message_id>` (the `data-post` attribute).
- `created_utc` = the `<time datetime>` value converted to integer epoch seconds UTC. Telegram preview timestamps include an explicit offset.
- `body` = `.tgme_widget_message_text` HTML converted to text; `<br>` and block tags become line breaks, entities decoded, whitespace normalised. For URL-only posts the body is the URL; the linked article headline and summary are preserved in `raw.link_preview`.
- `score` = view count shown in the preview (approximate above 1,000, as Telegram rounds it, e.g. `1.13K` → 1130).
- `title` = the visible link-preview headline when it names Genting; otherwise the first body line that names Genting (or the first body line if none). Telegram has no post-title field, and the validator requires a non-empty title, so this is the closest source-derived value rather than an invented headline.
- `num_comments` = reply/comment count visible on the post, or `null` when the preview shows no discussion link. **No post in this collection exposed a visible reply count**; every `num_comments` is `null`.
- `author` = channel title; `channel` = `@username`; `url` = canonical `https://t.me/<username>/<id>`.
- `raw` holds views, forward source, outbound links, channel title and subscriber count at collection time, the search keywords that found the post, the link preview, the reply URL if any, and all tickers detected.
- Ticker assignment: `GENM` for GENM/4715/Genting Malaysia; `GENTING` for GENTING/3182/Genting Berhad; `UNKNOWN` for a bare "Genting"/云顶 mention with no qualifier. When both are discussed, the first strong token in the text decides the primary ticker; `raw.tickers` lists every ticker detected.

## Content filter

A candidate is kept only when it genuinely mentions the gaming companies (Genting Berhad/GENTING/3182, Genting Malaysia/GENM/4715, 云顶集团/云顶大马, Resorts World) **and** falls in the window. Genting Plantations (GENP), Genting Singapore, Ho Wah Genting, Resorts World Sentosa, Antara Genting (a property project), Genting Sempah, Genting Permai, Genting Highlands Premium Outlets, Genting Property and other place/project names are not treated as gaming-company mentions unless the post also names GENTING/GENM/the codes. Generic market round-ups (market wrap, top gainers/losers/active, FBM KLCI recaps, "saham paling aktif", trading-ideas lists, screener lists) are dropped unless the post contains a dedicated Genting paragraph of at least 120 characters whose subject is Genting, or a headline/caption that leads with Genting (e.g. a chart video or a dedicated article share). This removes list-only mentions while keeping news, analysis, broker notes and investor discussion.

## Coverage gaps and limitations

1. **Comments are not collected.** `t.me/s/<channel>` exposes channel posts only. Reply/comment threads live in linked discussion groups, which are usually private or not reachable through the public preview; the preview only shows a comment count when a discussion link exists. `num_comments` is that visible count (often `null`); no comment text is in this file, and posts must not be read as comments. **All records are `record_type: post`; there are zero `reply` records.**
2. **Search history is not the full channel archive.** Telegram's public keyword search returns a limited slice (about 20–40 hits per keyword in this run, newest first, paginated backwards). The "Oldest hit" and "Newest hit" columns show what each channel's searches actually reached. Where the newest hit is earlier than 2025-11-01, the channel's later posts did not match any keyword (or are not indexed); where the oldest hit is later than 2024-11-02, earlier Genting posts may exist but were not reachable. Non-keyword posts are not enumerated, so `messages_scanned` counts only posts returned by the seven searches.
3. Some channels have no public preview or return Telegram's "channel not found" shell. They are still listed in the table with 0 posts and are excluded from the JSONL; see the unavailable-channel list below.
4. View counts are as shown at collection time and are rounded by Telegram above 1,000. Forward counts are not exposed by the preview; `raw.forwards` records the forward source name when the post is a forward, otherwise `null`.
5. Channel subscriber counts are as shown at collection time.

## Validation

`python3 -m genting.validate data/raw/telegram_2024-2025.jsonl` → **OK, 0 errors** (108 records).

## Unavailable channels

- @BursaKLSEsignals — no public preview / no channel info.

## Errors

- @BursaKLSEsignals: no public channel preview (t.me/s returned no channel info)

