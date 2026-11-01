# Facebook — public collection report

**Window:** 2024-11-02 00:00:00 UTC → 2026-11-02 23:59:59 UTC (2024-11-02 08:00 → 2026-11-03 07:59:59 MYT).
**Output:** `data/raw/facebook_public.jsonl` — 37 posts and 94 visible comments/replies.
**Status:** **partial**. The posts below are genuinely public and were read without login; Facebook does **not** expose a complete public archive to a logged-out client, so this is not a census of all Genting posts.

## Summary

| Item | Count |
|---|---:|
| Posts written | 37 |
| Replies/comments written | 94 |
| Total records | 131 |
| Pages/channels represented | 27 |
| `GENTING` posts | 16 |
| `GENM` posts | 21 |
| Post date range (UTC) | 2025-01-07 03:56 → 2026-10-19 00:05 |
| Reply date range (UTC) | 2025-05-29 10:42 → 2026-10-19 00:08 |
| Comments reported by Facebook | 610 |
| Comments captured | 94 |
| Comments not visible without login | 516 |

The 610 figure is the sum of the `total_count` values Facebook renders for these posts. Only the comments Facebook chose to include in the logged-out HTML were captured (usually the top 10, sometimes fewer). 17 posts have a gap; 14 posts report zero comments.

## What was publicly accessible

Direct public post URLs returned HTTP 200 and contained the post body plus a subset of comments in the server-rendered HTML. No cookies, credentials, login or captcha solving were used. The same was true for `m.facebook.com` post URLs, which redirected to the desktop URL and rendered the post.

Public page shells were also readable for some pages, but only the latest post was rendered:

| URL | Result |
|---|---|
| `https://www.facebook.com/ResortsWorldGenting` | HTTP 200; page shell, 479,876 followers; one latest post (`/reel/2276604772914160/`, 2026-11-01, concert promotion). No Genting stock content. |
| `https://www.facebook.com/BursaMalaysia` | HTTP 200; page shell; one latest post (2026-11-01, Bursa Gold Dinar commemorative coin). No Genting content. |
| `https://www.facebook.com/genting.berhad/` | HTTP 200 profile shell (reached from `facebook.com/GentingBerhad`); no feed/posts. |
| `https://www.facebook.com/pages/Genting-Malaysia-Berhad/105007946206205/` | HTTP 200; title “Genting Malaysia Berhad”; no posts or messages in the logged-out HTML. |

All 37 collected posts are from public pages/profiles and public post URLs; each post page’s JSON carried `privacy_scope.description = "Public"`. They include:

- **October 2026 rights issue / price collapse:** ELITISTA, Nanyang Siang Pau, The Edge Malaysia, Share Traders, NST Online, The Star, 马股-报报看, 企业商学, Money POV, 9shares.my.
- **October–November 2025 GENM privatisation:** Nazri Hamdan, DagangNews, Latest Malaysia News, BFM Radio, Finance Malaysia, The Edge Malaysia, Ringgit Dan Sen, Ziet Invests, financialfreedom001, 8TV News, TIAcademy Mandarin.
- **2025–2026 results, dividends, ratings and technical posts:** BZbiznews, StarBiz, Windscopo001, The Business Times, Bursa Screener, KC, 9shares.my, Bilyonaryo, TIAcademy Mandarin.

## Blocked or closed surfaces

### Page URLs

| URL | Observed result |
|---|---|
| `https://www.facebook.com/gentingmalaysia` | HTTP 200, 321,711 bytes, title “Facebook”; body says “This content isn’t available at the moment” and contains a login form. No page, no posts. |
| `https://www.facebook.com/GentingBerhad` | HTTP 200, redirects to `https://www.facebook.com/genting.berhad/`; profile metadata only. |
| `https://www.facebook.com/genting.berhad/posts` | HTTP 200, 323,849 bytes; “This content isn’t available at the moment”; no posts. |
| `https://www.facebook.com/genting.berhad?sk=wall` | HTTP 200; no post messages. |
| `https://www.facebook.com/pages/Genting-Malaysia-Berhad/105007946206205/` | HTTP 200; page name only, no posts. |
| `https://mbasic.facebook.com/gentingmalaysia` | HTTP 200 after redirect to `https://www.facebook.com/login/?next=...`; login wall. |
| `https://mbasic.facebook.com/GentingBerhad` | Same login redirect. |
| `https://mbasic.facebook.com/ResortsWorldGenting` | Same login redirect. |
| `https://mbasic.facebook.com/BursaMalaysia` | Same login redirect. |
| `https://mbasic.facebook.com/elitistaofficial/posts/1134586812440649` | Same login redirect. |
| `https://mbasic.facebook.com/story.php?story_fbid=1134586812440649&id=100076680222827` | Same login redirect. |
| `https://lite.facebook.com/elitistaofficial/posts/1134586812440649` | Redirects to `https://www.facebook.com/`; login shell. |
| `https://www.facebook.com/search/posts/?q=genting%20saham` | HTTP 404 “Not Found”. |
| `https://www.facebook.com/search/top?q=genting%20saham` | HTTP 404 “Not Found”. |
| `https://www.facebook.com/public/Genting` | HTTP 200 login page (“Log in”, “Sign up”); no profile results. |
| `https://www.facebook.com/plugins/post.php?href=...` | HTTP 200 but “This Facebook post is no longer available. It may have been removed, or the privacy settings of the post may have changed.” The direct post URL still worked, so the embed is not a usable route. |

`m.facebook.com/<page>` and `m.facebook.com/<post>` redirect to `www.facebook.com`; they do not expose an additional timeline. `m.facebook.com/gentingmalaysia` lands on the same “content isn’t available” shell.

### Page-timeline limitation

Only one latest post is rendered for `ResortsWorldGenting` and `BursaMalaysia`. `/posts`, `?sk=wall` and `?ref=page_internal` returned the same single post; no pagination or “older posts” cursor is available without login. The `Genting Berhad` profile rendered no posts at all.

### Comments limitation

The logged-out HTML renders at most the first ten comments (“Most relevant” selection). `?filter=all`, `?sorting_setting=CHRONOLOGICAL` and a comment-tracking parameter all returned the same ten comments for a post with 17 reported comments. No public comment-pagination endpoint was available. Only one nested reply (depth 1) survived in the rendered HTML across all 37 posts.

Examples of the gap:

| Post | Facebook total | Captured |
|---|---:|---:|
| 马股-报报看 Budget 2027 post | 189 | 10 |
| financialfreedom001 privatisation video | 113 | 2 |
| 9shares.my Kien Huat post | 75 | 10 |
| 8TV News privatisation video | 50 | 2 |
| Windscopo001 GENM Q4 post | 41 | 8 |
| BFM Radio privatisation post | 35 | 10 |
| Nazri Hamdan privatisation post | 19 | 10 |
| Nanyang Siang Pau IDSS post | 17 | 10 |

## Search-engine discovery

Queries used (exact forms):

- `site:facebook.com genting saham`
- `site:facebook.com "genting malaysia"`
- `site:facebook.com GENM 4715`
- plus `site:facebook.com "genting berhad" saham`, `site:facebook.com genting rights issue`, `site:facebook.com genting privatization`, `site:facebook.com/groups genting saham`, `site:facebook.com "云顶" 股票`, `site:facebook.com genting 3182`, `site:facebook.com genm saham`, and date/event variants.

| Engine | Result |
|---|---|
| **DuckDuckGo HTML** | Two of the first three queries returned 10 Facebook result links each (including the ELITISTA and GIDinvest posts). The second query already returned HTTP 202 with the “Select all squares containing a duck” challenge. Every subsequent DDG query (eight additional query sets plus a group query) returned the same challenge. No captcha was solved. |
| **Bing** | HTTP 200, 102,000–336,000 claimed results, but **zero `facebook.com` result URLs** for any `site:facebook.com ...` query. Results were unrelated domains (dailymail.com, dailymotion.com, rwgenting.com, genting.com). `site:facebook.com` alone also returned dailymail/dailymotion. Bing provided no indexed Facebook posts. |
| **Mojeek** | First query HTTP 200 but body was “Captcha … JavaScript is required to complete this challenge”; second HTTP 403; third HTTP 200 with the same captcha. No results. |
| **Google** (extra check) | HTTP 200 but a JavaScript/consent redirect page (“Please click here if you are not redirected…”); zero results. |
| **Yahoo** (supplementary fallback) | HTTP 200; 7 results per query across 28 queries; this is where most seed URLs came from. It is Bing-backed but its `site:` filter worked in this environment. |
| **Brave / Startpage / Ecosia** (extra checks) | Brave HTTP 429 + suspicious/captcha page; Startpage “Verifying your request…” JavaScript gate; Ecosia HTTP 403 firewall/captcha. Zero results. |

**Conclusion:** DuckDuckGo was the only required engine that returned any indexed Facebook posts, and it rate-limited into a captcha after roughly a dozen queries. Bing returned zero Facebook results; Mojeek returned only a captcha. Yahoo was used as a legitimate supplementary discovery engine.

## Wayback Machine / archive.org CDX

CDX API queried with `from=20241102&to=20261102`, `filter=statuscode:200`, `collapse=urlkey`:

| Prefix | In-window 200 captures |
|---|---:|
| `facebook.com/gentingmalaysia*` | 0 |
| `facebook.com/genting.berhad*` | 0 |
| `facebook.com/GentingBerhad*` | 0 |
| `facebook.com/ResortsWorldGenting*` | 3 (all video URLs: `10156865559595999`, `288273078658676`, `792095946692196`) |
| `facebook.com/BursaMalaysia*` | 20; the returned rows were dominated by malformed `/posts/js/...` asset URLs, not Genting posts |
| specific ELITISTA post URL | 0 |
| `facebook.com/groups/335183518109927*` | 0 |

No capture was returned for any of the Genting page/post prefixes queried. The Wayback Machine is not a viable route for this source.

## Meta Content Library and API

Sources checked:

- `https://transparency.meta.com/researchtools/meta-content-library/` (HTTP 200; page updated 2026-04-30)
- `https://developers.facebook.com/docs/content-library-and-api`
- `https://developers.facebook.com/docs/content-library-and-api/get-access` (HTTP 200)

Eligibility, quoted from Meta’s get-access documentation:

> “To be eligible for access, applicants must be affiliated with a qualified academic institution or a qualified non-academic research institution.”

For academic institutions, “qualified” means: dedicated to education/research, accredited, qualified to grant academic degrees, and not-for-profit. For non-academic institutions, it must be a not-for-profit whose primary purpose is scientific or public-interest research.

Process:

1. Lead researcher applies through **Meta Research Tools Manager** (desktop/laptop only).
2. **CASD** (Secure Data Access Center) independently reviews the application; review typically 2–3 weeks.
3. Meta processing typically another 2–3 weeks.
4. If approved, access is granted through the **Secure Research Environment** or an approved third-party cleanroom.

**Is an application the only route?** Yes. There is no anonymous public search endpoint for the Content Library or Content Library API. The web tool and API require an approved research programme and institutional affiliation. General readers, individual retail investors and for-profit organisations without a qualifying research affiliation are not eligible. No application was submitted for this task.

## Facebook Graph API without a token

Tested directly, no token:

| Request | Response |
|---|---|
| `https://graph.facebook.com/v26.0/100064754198442/posts` | HTTP 400, `OAuthException`, code 104: “An access token is required to request this resource.” |
| `https://graph.facebook.com/v26.0/gentingmalaysia/posts` | HTTP 400, code 100, subcode 33: “Unsupported get request. Object with ID ‘gentingmalaysia’ does not exist, cannot be loaded due to missing permissions, or does not support this operation.” |
| `https://graph.facebook.com/v26.0/1134586812440649?fields=message,created_time` | HTTP 400, code 12: “singular statuses API is deprecated for versions v2.4 and higher.” Individual post reads are not a public route either. |

The Graph API is closed without an access token. It is not a public read route, and a token would require a Meta app and the appropriate permissions/page role.

## Public groups

| Group | Landing page | Result |
|---|---|---|
| **Intraday Saham Malaysia** (`/groups/335183518109927`) | HTTP 200 | **“Public group · 25.3K members”**; group name, member count and a few recent posts visible without login. The only indexed Genting post found is `705315327763409`, “genting ini kali la bos ku”, dated **2023-01-27** — outside the window. Facebook reports 2 comments; 1 was visible. No in-window Genting post appeared in the visible feed. |
| **Pelabur Saham Bursa Malaysia** (`/groups/pelabursahambursamalaysia`) | HTTP 200 | **“Private group · 29.0K members”**; description visible, no posts. |
| `/groups/1488250196331034` | HTTP 200 → `/login/?next=...` | Login wall. |
| `/groups/383234831776414` | HTTP 200 → `/login/?next=...` | Login wall. |
| `/groups/908137271254150` | HTTP 200 → `/login/?next=...` | Login wall. |
| `/groups/1482336428651961` | HTTP 200 → `/login/?next=...` | Login wall. |
| `/groups/pelaburansahammalaysia` | HTTP 200 → `/login/?next=...` | Login wall. |
| `/groups/7790866358` (Resorts World Genting shows/entertainment) | HTTP 200 → `/login/?next=...` | Login wall. |

Some individual group-post URLs rendered content to a logged-out client even when the group landing page redirected to login. Because group privacy could not be established without logging in, those posts were **not** included in the JSONL. This was a deliberate privacy precaution, not a technical limitation. The only group used as positive evidence is the explicitly labelled **Public group** `Intraday Saham Malaysia`, and it had no in-window Genting post.

## Method and fields

- **Discovery:** DuckDuckGo HTML and Yahoo `site:facebook.com` queries. Facebook’s own search was 404; no Facebook search API was used.
- **Collection:** direct public post URLs fetched with `curl_cffi` impersonating Chrome. No cookies, no credentials, no login, no captcha solving. At least 1.3 seconds between Facebook requests (usually 2 seconds); back-off on 429/5xx.
- **Cache:** `data/raw/cache/facebook/posts/<sha1>.html`, plus page/group/search probe HTML in `data/raw/cache/facebook/`.
- **Requests made:** approximately 180 logged-out HTTP requests: 13 initial page probes, 9 page-slug variants, 9 page-tab variants, 4 post-variant probes, 55 candidate-post HTML fetches, 37 final seed fetches, 28 Yahoo queries, 3 initial query sets each for DuckDuckGo/Bing/Mojeek/Google (plus follow-up DDG queries), 3 other search engines, 7 CDX queries, 3 Graph API calls, 3 Meta documentation fetches, and about 20 group-page probes. Facebook requests were paced at 1.3–2 seconds; search engines were queried at 2–3.5 second intervals.
- **Dedup:** `(source, native_id)`; post `native_id` is Facebook’s numeric `post_id`; reply `native_id` is the numeric comment id (`legacy_fbid`).
- **`channel`:** page slug (e.g. `elitistaofficial`, `nanyang.nysp`, `theedgemalaysia`) or `groups/<id>` if a group post were included.
- **`created_utc`:** Facebook’s integer `creation_time` for page/posts, or the main video’s `publish_time` for video pages. `raw.time_source` records which. No relative times were converted.
- **`body`:** JSON `message.text`, HTML-stripped, entity-decoded, whitespace-normalised. For photo/video pages without a Story object, the caption/message text was used; `raw.og_description` preserves Facebook’s meta description. On the ELITISTA post the headline is the post body and the page’s longer analysis is a page-authored comment; that analysis is recorded as a reply, not merged into the post body.
- **`title`:** first substantive line of the body (blank, hashtag/mention-only and very short lines skipped), truncated to 200 characters.
- **`num_comments`:** Facebook’s `comment_rendering_instance.comments.total_count` (the count shown to a logged-out viewer), not the number captured.
- **Replies:** `depth` comes from Facebook’s `Comment.depth`; `parent_native_id` is decoded from `comment_direct_parent.id`; `post_native_id` is the post’s numeric id. No parent/depth values were inferred.
- **`score`:** `null`; reaction counts were not consistently available in the rendered text and were not inferred.
- **`lang`:** `null`; language was not inferred.
- **Ticker:** assigned from the post text. `GENTING` for GENTING/3182/Genting Berhad; `GENM` for GENM/4715/Genting Malaysia. Posts discussing both (e.g. the 9shares.my Moody’s post) are tagged `GENTING` as the parent/primary subject; the body retains both names.
- **`raw`:**
  - `post_id`, `story_id`, `page_id`
  - `comment_total_count`, `comments_captured`, `comment_gap`
  - `privacy` (`Public` when Facebook’s page JSON says so)
  - `time_source`, `discovery_query`, `seed_ticker`
  - `access_note`, `fetched_utc`, `http_status`, `final_url`
  - `og_title`, `og_description`, `body_truncated`
- **Idempotence:** the collector re-uses cached HTML and writes deterministic records; re-running produced the same 131 records.

## Known gaps and limitations

1. **Not a complete census.** Discovery depends on search-engine indexes. Only 37 public posts were reachable; there are almost certainly many more public Facebook posts about Genting that neither DuckDuckGo nor Yahoo surfaced. The collected range starts on 2025-01-07; no in-window posts from 2024-11-02 to 2025-01-06 were found. This is a discovery gap, not evidence that no such posts exist.
2. **Page timelines are one-post previews.** Facebook exposes only the latest post for public pages to a logged-out client. There is no public “older posts” pagination for `ResortsWorldGenting`, `BursaMalaysia`, or the Genting profiles.
3. **Comments are a top-N sample.** 94 of 610 reported comments were visible. The rest require login, a page role, or Meta Content Library/API access. Nested replies are almost entirely absent (1 depth-1 reply).
4. **“Most relevant” filtering.** Facebook’s logged-out comment selection is ranked/filtered, so even a later visit may show a different subset. Some captured comments are page-authored link dumps or very short reactions; they are retained as visible source text rather than filtered out.
5. **Group content excluded unless verified public.** Individual group-post URLs sometimes rendered; group landing pages were login-walled or “Private group”, so those posts were not used.
6. **Search-engine blocks.** DuckDuckGo captcha after ~12 queries; Bing zero Facebook results; Mojeek captcha; Google JavaScript gate; Brave/Startpage/Ecosia blocked. Yahoo was a working fallback but is not a complete index either.
7. **No Wayback captures** of Genting Berhad/GENM posts in the window; only three ResortsWorldGenting video captures and malformed BursaMalaysia asset captures.
8. **No Meta Content Library access.** The application route is institutional and was not pursued. No Graph API token.
9. **One visible caption ends in an ellipsis.** The Latest Malaysia post (`1224327853049730`) has `raw.body_truncated=true`; Facebook’s own meta description ends with “...”. The missing tail is not invented.
10. **Page identity.** `facebook.com/gentingmalaysia` is not a working page slug. The legacy page `/pages/Genting-Malaysia-Berhad/105007946206205/` exists but exposes no posts. `facebook.com/GentingBerhad` resolves to a profile (`genting.berhad`) with no feed.
11. **Reaction/view counts** are not included in `score`; they were not needed for the contract and are inconsistently rendered.
12. **No SQLite writes.** This collector only wrote JSONL and cache/report files.

## Legitimate access routes

| Route | What it gives | Requirements |
|---|---|---|
| **Direct public post URLs** | Post body, page name, timestamp, up to ~10 top comments | None; public URL must be known. This is what was used. Not enumerable at scale. |
| **Meta Content Library / Content Library API** | Comprehensive public Facebook/Instagram archive, including public page/group posts and comments | Application via Research Tools Manager; affiliation with a qualified academic or non-profit research institution; CASD review (2–3 weeks) + Meta processing (2–3 weeks); access in Secure Research Environment/approved cleanroom. |
| **Graph API with a Meta app** | Page posts/comments for pages you can access | App access token; Page Public Content Access or page role; app review where required. Not available anonymously. |
| **Page admin export (Meta Business Suite)** | Full post/comment export for pages you administer | Admin/analyst role on the page. Not applicable to third-party pages. |
| **Group admin export / member access** | Full group content | Group admin or member, depending on group privacy. Not applicable to public collection. |
| **Search-engine discovery** | URLs and snippets of indexed public posts | No login, but incomplete and subject to bot challenges. Useful as a seed generator only. |

CrowdTangle is not a route for this window: Meta retired it before the collection period, and its old domain did not resolve from this environment.

## Validation

```text
$ python3 -m genting.validate data/raw/facebook_public.jsonl
data/raw/facebook_public.jsonl
  records=131 {'post': 37, 'reply': 94} tickers={'GENTING': 16, 'GENM': 21} | 2025-01-07 → 2026-10-19
  empty_or_deleted=0 duplicate_body_texts=0

OK: 0 errors
```

No warnings: no empty/deleted bodies, no duplicate body texts, and every reply references a post in the same file. The 516-comment gap is a source-access limitation, not a validation warning.

## Files

- `data/raw/facebook_public.jsonl` — 131 records (37 posts, 94 replies).
- `data/raw/facebook_report.md` — this report.
- `data/raw/facebook_fetch_log.json` — per-URL fetch log: post id, HTTP status, timestamp, reported/captured comment counts.
- `data/raw/cache/facebook/` — raw HTML probes, search results, CDX results, and per-post cached HTML.
- `scripts/collect_facebook.py` — reproducible collector for the 37 curated public post URLs.
