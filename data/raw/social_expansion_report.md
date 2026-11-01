# Social expansion report — RED, Instagram, LinkedIn, Facebook

Run date: **2 November 2026** (Asia/Kuala_Lumpur). Collection window:
**2 Nov 2024 → 2 Nov 2026** UTC, inclusive.

Scope: Malaysian Genting — Genting Berhad (`GENTING`, Bursa 3182) and Genting
Malaysia (`GENM`, Bursa 4715).

Method: no accounts, cookies, credentials or captcha solving. JavaScript-heavy
pages were opened in **nodriver 0.50.3**, headful under `xvfb-run -a` (the same
setup that works for TikTok). Static public HTML was fetched with
`curl_cffi` `impersonate="chrome"`. Page loads were spaced 2–4 s apart; Google
discovery was stopped as soon as it served a challenge.

## Outputs

| Platform | File | Posts | Replies | Post date range | Status |
|---|---|---:|---:|---|---|
| Xiaohongshu / RED | — (no file) | 0 | 0 | — | **Blocked** — login wall on every public surface |
| Instagram | `data/raw/instagram.jsonl` | 41 | 43 | 2025-02-28 → 2026-10-26 | Partial — public post pages work, history limited |
| LinkedIn | `data/raw/linkedin.jsonl` | 16 | 0 | 2025-12-31 → 2026-10-29 | Partial — posts only, comments login-gated |
| Facebook | `data/raw/facebook_2y.jsonl` | 74 | 133 | 2024-12-07 → 2026-10-20 | Collected — 2-year superset of the existing file |

`data/raw/facebook_public.jsonl` was **read only** and merged into the 2-year
file by `(source, native_id)`. It was not overwritten by these collectors.

Ticker split:

| Platform | GENTING | GENM | UNKNOWN |
|---|---:|---:|---:|
| Instagram | 16 | 20 | 5 |
| LinkedIn | 6 | 10 | 0 |
| Facebook | 22 | 36 | 16 |

`UNKNOWN` is used for genuine Genting content that does not identify a listed
entity (resort/travel posts, index round-ups, mixed market recaps). It is not a
guess at a ticker.

---

## 1. Xiaohongshu / RED — inaccessible without login

RED is the most aggressively walled of the four. Every tested public entry
point either redirected to login or returned a QR-code page. No notes or
comments could be read, so **no `red.jsonl` was written** and no RED rows were
invented.

| Test | Result |
|---|---|
| `xiaohongshu.com/search_result?keyword=云顶` in browser | HTTP 200 shell, visible overlay **“登录后查看搜索结果”** (“log in to view search results”); zero note cards in DOM or `__INITIAL_STATE__` |
| Same query with `云顶大马`, `genting 股票`, `马来西亚 股票` | Same login overlay; no results rendered |
| `xiaohongshu.com/explore` | 302 → `/login?redirectPath=...` |
| `xiaohongshu.com/explore/<note_id>?xsec_token=...` (token copied from a public XHS page) | 404 “当前笔记暂时无法浏览” / “请打开小红书App扫码查看” |
| `m.xiaohongshu.com/search_result` | Connection timed out |
| Legacy JSON endpoints `/web_api/sns/v3/search/notes`, `/api/sns/web/v1/search/notes` | HTTP 500 `create invoker failed` (endpoints retired) |
| `r.jina.ai` reader proxy over search and note URLs | Login shell for search; 404/login page for the note |
| Baidu `site:xiaohongshu.com 云顶 股票` | Baidu security-verification page (not bypassed) |
| Google / Bing `site:xiaohongshu.com ...` | No Xiaohongshu note URLs returned for these queries |

Third-party RED wrappers tested:

| Site | Result |
|---|---|
| `xhs.hackliu.com` | DNS does not resolve |
| `rednote.tools` / `www.rednote.tools` | DNS does not resolve |
| `xhs.iiilab.com` | HTTP 404 |
| `xhsdl.com` | Unrelated pirate streaming site, not a RED viewer |

**Conclusion:** as of the run date there is no logged-out public search, feed or
note view. Search, note bodies and comments all require an account/app scan.
This is a platform access blocker, not a data gap that can be filled from public
HTML.

---

## 2. Instagram — public post pages work; history is limited

### Access method

Public Instagram **post** URLs (`instagram.com/p/<shortcode>/`) were opened in a
logged-out browser. Instagram served:

- the full caption,
- exact `taken_at` epoch,
- like count and total comment count,
- the first page of comments with exact `created_at`, usernames and comment likes.

Example: `instagram.com/p/DPvp2R3jcL_/` (nstonline, 13 Oct 2025) rendered the
caption and 7 comments without login.

What is walled:

| Surface | Logged-out result |
|---|---|
| Hashtag pages (`/explore/tags/genting/`) | Login form |
| Profile pagination (“Show more posts”) | Login wall; profile JSON exposes only the latest 12 posts |
| `graphql/query` profile timeline (`query_hash`) | HTTP 401 `require_login: true` |
| “View more comments” | Login wall; only the first comment page is in HTML |

Profile pages themselves are public (e.g. `resortsworldgenting`, 106K
followers), but their embedded JSON has no `taken_at`; each post had to be
opened individually for an exact timestamp.

Handle tests: `resortsworldgenting` is the live official account;
`bursamalaysia` is live but its latest 12 posts contain no Genting reference;
`gentingmalaysia`, `gentingberhad`, `genting_berhad` and
`resourcestoworldgenting` all return “Profile isn't available”.

### Result

- **41 posts, 43 replies**, 2025-02-28 → 2026-10-26.
- 81 comments declared across those posts; 43 captured (53%). The gap is the
  login-gated “more comments” pages plus deleted/restricted comments.
- Channels: The Edge Malaysia (9), Asia Gaming Brief (3), Resorts World Genting
  (3), Enanyang (3), The Exchange Asia (2), Free Malaysia Today (2), Oriental
  Daily News (2), Bernama TV (1), NST Online (1), Sin Chew Daily (1), Bursa
  News (1), StarBiz (1), and finance creators.
- Content covers the Oct 2025 privatisation offer, the Dec 2025 New York casino
  decision, Fitch/Moody’s downgrades, FY2025/Q1–Q2 2026 results, the Oct 2026
  rights issue and share collapse, plus official Resorts World Genting posts.

### Gaps

- No Nov 2024 – Feb 2025 posts; H1 2025 is sparse (one post each in Feb, Jul,
  Aug). Instagram search is login-only, so historical discovery depended on
  external indexes.
- Comment coverage is structurally partial even on accessible posts.

### Third-party Instagram viewers tested

| Site | Result | Usable |
|---|---|---|
| Picuki | Redirects to `tikvib.com`; Cloudflare 403 “Just a moment…” | No |
| Imginn | Cloudflare 403 | No |
| Pixwox | Redirects to `pixnoy.com`; Cloudflare 403 | No |
| Dumpor | Loads, then “we need to verify you're not a bot” | No |
| Greatfon | 301 → Dumpor bot check | No |
| Picnob | Cloudflare 403 | No |
| Gramhir | 200 but 114-byte JS shell, no content | No |
| Instagub | Domain for sale | No |
| Instalker | Cloudflare 403 | No |
| Instanavigation | DNS does not resolve | No |
| Instagram `/api/v1/oembed/?url=...` | 200; returns caption, author, media_id, thumbnail — **no timestamp or comments** | Limited |
| Instagram GraphQL timeline | 401 `require_login` | No |

Direct public post pages were strictly better than every wrapper.

---

## 3. LinkedIn — public company posts, comments hidden

### Access method

Public company pages and public post pages render JSON-LD
(`SocialMediaPosting`) when logged out. Company pages exposed:

- **Genting Berhad** (`linkedin.com/company/genting-berhad`): latest 5 posts.
- **Resorts World Genting** (`linkedin.com/company/resorts-world-genting`):
  latest 10 posts.
- One public commentator post found by search
  (`linkedin.com/posts/pirginezra_...activity-7515309138923491330...`).

Each record has `datePublished`, body text, author and like count. Comment
count is sometimes present; comment **bodies are not** — the page says “To view
or add a comment, sign in”.

### Result

- **16 posts, 0 replies**, 2025-12-31 → 2026-10-29.
- 6 GENTING (Genting Berhad page + commentator), 10 GENM (Resorts World
  Genting page).
- Comments are login-gated, so replies were not fabricated. `num_comments` is
  null where LinkedIn did not publish a count.

### Gaps

- `/company/<slug>/posts/` redirects to the LinkedIn sign-up wall.
- Only the latest 5/10 posts are in the public company HTML; no pagination.
- No Nov 2024 – Dec 2025 posts were reachable without login. The one public
  commentator post is from Oct 2026.
- No free LinkedIn wrapper was found or needed; direct public pages are the
  only surface.

---

## 4. Facebook — extended to two years

### Access method

Direct public post URLs (`facebook.com/<page>/posts/...`, `/videos/...`) were
fetched with `curl_cffi` (`impersonate="chrome"`). Facebook returned HTTP 200,
the post body and the comments it renders to logged-out visitors (usually the
top 5–10, sometimes none). No cookies or login were used.

Page-level surfaces were not usable for history:

| Surface | Result |
|---|---|
| `facebook.com/<page>/` | Only the latest/pinned post in logged-out HTML |
| `facebook.com/<page>/posts/` | Same single post, no timeline feed |
| `mbasic.facebook.com/...` | HTTP 400 |
| `facebook.com/public/...` | HTTP 400 |
| Wayback CDX for page post prefixes | No captures for the tested pages; domain query returned 503 (IA temporarily offline) |

### Discovery

Google was queried in a real browser with `site:facebook.com` plus
`after:`/`before:` operators. It produced usable post URLs for roughly ten
queries, then redirected to `/sorry/` (captcha). Collection stopped there; no
captcha was solved. Additional seeds came from the configured web-search
integration and from page-scoped queries (The Star, The Edge, NST, StarBiz,
Bursa Malaysia, 8TV, BFM, DagangNews, 9shares, RinggitDanSen, ZietInvests,
Bursa Screener, etc.).

Search engines that did **not** work for discovery:

| Engine | Result |
|---|---|
| DuckDuckGo HTML/Lite | HTTP 202 bot block |
| Yahoo | TLS connection reset |
| Bing | Ignored `site:`; returned generic Genting pages |
| Mojeek | Captcha |
| Brave Search | HTTP 429 |
| Baidu | Security verification |
| Google (after ~12 queries) | `/sorry/` captcha; stopped |

### Result

- **74 posts, 133 replies**, 2024-12-07 → 2026-10-20.
- 22 GENTING, 36 GENM, 16 UNKNOWN.
- 2,415 comments declared across the posts; 133 captured. The large gap is
  expected: logged-out Facebook renders only a small top-comment slice, and
  several high-volume posts declare hundreds of comments.
- Channels include The Edge Malaysia (9), The Star Online (7), TIAcademy
  Mandarin (5), StarBiz (5), NST Online (4), Finance Malaysia (3), 9shares
  (2), Resorts World Genting (2), plus BFM, 8TV News, DagangNews,
  RinggitDanSen, ZietInvests, Bursa Screener, Elitista, Nanyang, BusinessToday,
  Focus Gaming News and others.

### Coverage by month (posts)

```
2024-12  1
2025-01  2
2025-02  3
2025-05  2
2025-06  1
2025-07  4
2025-08  7
2025-09  1
2025-10 10
2025-11  7
2025-12  4
2026-02  6
2026-03  1
2026-06  2
2026-07  1
2026-08  6
2026-09  5
2026-10 11
```

### Gaps

- **2 Nov – 6 Dec 2024**: no public post found. The earliest record is the
  7 Dec 2024 KLCI-removal post by OnlineForexRadio.
- Mar–Apr 2025 and Jan/Apr–May 2026 are thin or empty. These are genuine
  discovery gaps: Facebook offers no logged-out keyword search or page
  timeline, and Google stopped serving results.
- Comment coverage is partial by design of the logged-out page, not truncation
  by the collector.

---

## 5. Wrapper sites evaluated (summary)

| Platform | Wrapper | Result | Usable |
|---|---|---|---|
| RED | xhs.hackliu.com | DNS failure | No |
| RED | rednote.tools | DNS failure | No |
| RED | xhs.iiilab.com | 404 | No |
| RED | xhsdl.com | Unrelated streaming site | No |
| RED | r.jina.ai reader | Login shell / 404 | No |
| Instagram | Picuki, Imginn, Pixwox, Picnob, Instalker | Cloudflare 403 | No |
| Instagram | Dumpor, Greatfon | Bot-verification page | No |
| Instagram | Gramhir | Empty JS shell | No |
| Instagram | Instagub | Domain for sale | No |
| Instagram | Instagram GraphQL timeline | 401 `require_login` | No |
| Facebook | whopostedwhat.com | Requires a Facebook session for search; not used | No |
| Facebook | Direct public post URL | 200, body + top comments | **Yes** |
| LinkedIn | Direct company/post page | 200, post JSON-LD; comments gated | **Yes (posts only)** |

The working “wrappers” are therefore the platforms’ own logged-out post pages,
not third-party mirrors.

---

## 6. Validation

```text
python3 -m genting.validate data/raw/instagram.jsonl
  records=84 {'post': 41, 'reply': 43} tickers={'GENTING': 16, 'GENM': 20, 'UNKNOWN': 5}
  2025-02-28 → 2026-10-30 | OK: 0 errors

python3 -m genting.validate data/raw/linkedin.jsonl
  records=16 {'post': 16} tickers={'GENTING': 6, 'GENM': 10}
  2025-12-31 → 2026-10-29 | OK: 0 errors

python3 -m genting.validate data/raw/facebook_2y.jsonl
  records=207 {'post': 74, 'reply': 133} tickers={'GENTING': 22, 'GENM': 36, 'UNKNOWN': 16}
  2024-12-07 → 2026-10-20 | OK: 0 errors
```

Warnings explained:

- Instagram reports 3 duplicate body texts. These are short, independently
  posted comments (e.g. emoji-only or “Genting is so boring”) by different
  users, not duplicated records. IDs are unique.
- Facebook and Instagram comment counts in `num_comments` are the platforms’
  declared totals; `raw.comments_captured` and `raw.comment_gap` record how many
  were actually visible logged-out.
- No timestamps were inferred from relative strings. Facebook uses
  `creation_time` / comment `created_time`; Instagram uses `taken_at` /
  comment `created_at`; LinkedIn uses ISO `datePublished`.

## 7. Ticker mapping

- `GENM` when text contains `GENM`, `4715`, “Genting Malaysia”, “云顶大马” or
  “云顶马来西亚”.
- `GENTING` when text contains `GENTING`, `3182`, “Genting Berhad”, “Genting
  Bhd”, “云顶集团” or an unambiguous Genting Berhad reference.
- `UNKNOWN` otherwise, including generic Genting Highlands travel content and
  broad market round-ups that mention Genting only in passing.
- Existing Facebook rows kept their original seed ticker where one was already
  assigned.

## 8. Files written

- `data/raw/instagram.jsonl` — 84 records
- `data/raw/instagram_fetch_log.json` — per-post access log, comment gaps
- `data/raw/linkedin.jsonl` — 16 records
- `data/raw/linkedin_fetch_log.json` — company-page access log
- `data/raw/facebook_2y.jsonl` — 207 records (2-year superset)
- `data/raw/facebook_2y_fetch_log.json` — seed log, skips, coverage
- `data/raw/social_expansion_report.md` — this report

No `red.jsonl` was written because no public RED content was reachable.
