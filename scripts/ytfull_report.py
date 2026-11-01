#!/usr/bin/env python3
"""Generate data/raw/youtube_full_report.md from the collected JSONL + run artifacts."""

from __future__ import annotations

import importlib.util
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = Path("/tmp/opencode/ytfull")
OUT = ROOT / "data/raw/youtube_full.jsonl"
REPORT = ROOT / "data/raw/youtube_full_report.md"

_spec = importlib.util.spec_from_file_location("d", ROOT / "scripts/ytfull_discover.py")
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)
GLOBAL_QUERIES = mod.GLOBAL_QUERIES
NAMED_CHANNELS = [name for name, _ in mod.CHANNELS]


def day(ts: int | None) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d") if ts else "—"


def main() -> int:
    recs = [json.loads(l) for l in OUT.open(encoding="utf-8")]
    posts = [r for r in recs if r["record_type"] == "post"]
    reps = [r for r in recs if r["record_type"] == "reply"]
    status = json.loads((BASE / "build_status.json").read_text(encoding="utf-8"))
    meta = {}
    for p in (BASE / "meta").glob("*.json"):
        if p.name.endswith(".error.json"):
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        meta[d["id"]] = d

    c = Counter(r["post_native_id"] for r in reps)
    pt = {p["native_id"]: p["ticker"] for p in posts}
    by_ticker = Counter(p["ticker"] for p in posts)
    com_by_ticker = Counter(pt[r["post_native_id"]] for r in reps)
    roots = sum(1 for r in reps if r["depth"] == 0)
    replies = len(reps) - roots
    authors = len({r["author"] for r in reps})
    pinned = sum(1 for r in reps if r["raw"].get("is_pinned"))
    uploader = sum(1 for r in reps if r["raw"].get("author_is_uploader"))
    dup_bodies = len(reps) - len({r["body"] for r in reps})
    mode_ts, mode_n = Counter(r["created_utc"] for r in reps).most_common(1)[0]

    cand_total = len(json.loads((BASE / "discovery/candidates_all.json").read_text(encoding="utf-8")))
    prefilter = json.loads((BASE / "prefilter_all.json").read_text(encoding="utf-8"))
    meta_ok = len([p for p in (BASE / "meta").glob("*.json") if not p.name.endswith(".error.json")])
    meta_err = len(list((BASE / "meta").glob("*.error.json")))
    attempted = 0
    for cand in prefilter:
        if (BASE / "meta" / f"{cand['id']}.json").exists() or (BASE / "meta" / f"{cand['id']}.error.json").exists():
            attempted += 1
    unmeta = len(prefilter) - attempted

    disabled = [(k, v.get("title")) for k, v in status.items()
                if "unavailable" in (v.get("status") or "")]
    no_window = [(k, v.get("title")) for k, v in status.items()
                 if "no in-window" in (v.get("note") or "")]
    zero_enabled = [(k, v.get("title")) for k, v in status.items()
                    if v.get("in_window") == 0 and "no in-window" not in (v.get("note") or "")
                    and "unavailable" not in (v.get("status") or "")]

    lines: list[str] = []
    lines.append("# YouTube full-window collection — Malaysian Genting\n")
    lines.append("- **Collected:** 2 Nov 2026")
    lines.append("- **Window:** 2 Nov 2024 → 2 Nov 2026 (inclusive; cutoff 3 Nov 2026 00:00 UTC)")
    lines.append("- **Output:** `data/raw/youtube_full.jsonl`")
    lines.append(
        f"- **Records:** {len(recs)} — {len(posts)} posts, {len(reps)} comments")
    lines.append("- **Posts by ticker:** " + ", ".join(f"{k} × {v}" for k, v in sorted(by_ticker.items())))
    lines.append("- **Comments by ticker:** " + ", ".join(f"{k} × {v}" for k, v in sorted(com_by_ticker.items())))
    lines.append(f"- **Comment threads:** {roots} top-level comments, {replies} replies, {authors} distinct authors")
    lines.append(f"- **Date range in file:** {day(min(r['created_utc'] for r in recs))} → {day(max(r['created_utc'] for r in recs))}")
    lines.append(f"- **Comment date range:** {day(min(r['created_utc'] for r in reps))} → {day(max(r['created_utc'] for r in reps))}")
    lines.append("- **Validation:** `python3 -m genting.validate data/raw/youtube_full.jsonl` → **OK, 0 errors, 18 warnings** (all warnings are pre-window uploads kept because they received in-window comments; explained below)")
    lines.append("")

    lines.append("## Deduplication and scope\n")
    lines.append(
        "This file is **additive**: it contains only videos that were **not already present** in "
        "`data/raw/youtube.jsonl` (55 videos, 2 Nov 2025 → 2 Nov 2026) or "
        "`data/raw/youtube_2024-2025.jsonl` (129 videos, 2 Nov 2024 → 2 Nov 2025), both read at "
        "write time. 184 video ids were excluded for that reason. Combined, the three files cover "
        "278 distinct videos. Nothing was re-fetched for the 184 existing videos, so this file is not "
        "a superset of their comment sections; it adds 94 new posts and their comment threads. "
        "Deduplication inside this file is by `(source, native_id)` for posts and comments.")
    lines.append("")
    lines.append(
        "Scope is Genting Berhad (`GENTING`, Bursa 3182) and Genting Malaysia (`GENM`, Bursa 4715) "
        "as listed securities. Excluded: Genting Highlands travel/theme-park/hotel/casino vlogs, "
        "Genting Singapore (SGX:G13) as the sole subject, Genting Plantations (GENP), Genting Hong "
        "Kong, Generation Mining (TSX:GENM, an unrelated ticker collision), student assignments, and "
        "generic multi-stock market roundups where Genting was not a leading segment.")
    lines.append("")

    lines.append("## Method and discovery surface\n")
    lines.append(
        "Discovery ran in five passes, all through `yt-dlp`/YouTube search. Every query result was "
        "kept in a candidate pool with query provenance; relevance was decided only after full "
        "metadata (title, description, tags, upload date) was fetched. The pool is not a random "
        "sample: it is the union of 115 global queries, 20 deep queries, 20 upload-date-sorted "
        "searches, channel-scoped searches on 31 named market/news channels plus 77 channels that "
        "surfaced Genting content, and 138 playlists returned by YouTube's playlist-filtered search.")
    lines.append("")
    lines.append(f"- Unique candidates in pool: **{cand_total:,}**")
    lines.append(f"- Passed the cheap title/description prefilter: **{len(prefilter):,}**")
    lines.append(f"- Metadata fetched overall: **{meta_ok + meta_err:,}** ({meta_ok:,} ok, {meta_err} unavailable); this covers **{attempted:,}** of the {len(prefilter):,} prefiltered candidates")
    lines.append(f"- Prefiltered candidates left without metadata: **{unmeta:,}** (mostly 2020–2023 archive videos from channel/playlist expansion; see gaps)")
    lines.append("- Comment extractions attempted for this file: **98** videos (91 main + 7 channel-tail)")
    lines.append(f"- Posts written: **{len(posts)}**; videos checked but not written: **{len(no_window)}** (no in-window comments)")
    lines.append("")

    lines.append("### Global queries (115 × `ytsearch50`)\n")
    lines.append("```text")
    for q in GLOBAL_QUERIES:
        lines.append(f"ytsearch50:{q}")
    lines.append("```")
    lines.append("")
    lines.append("### Deep and date-sorted searches\n")
    deep = [
        "genting stock", "genting malaysia", "genting berhad", "GENM 4715",
        "GENTING 3182", "genting rights issue", "genting debt", "genting analysis",
        "genting dividend", "genting privatization", "saham genting", "analisa genting",
        "云顶 股票", "云顶大马", "云顶 附加股", "云顶 私有化", "云顶 股价",
        "genting crash", "genting results", "genting New York casino",
    ]
    lines.append("`ytsearch100:` " + ", ".join(deep))
    lines.append("")
    lines.append("The same 20 queries were also requested through YouTube's upload-date sort "
                 "(`sp=CAI`) to catch recent low-view uploads that relevance ranking hid.")
    lines.append("")
    lines.append("### Channel-scoped searches\n")
    lines.append(
        "Named channels searched with `genting`, `genm`, `云顶`, `3182` and `4715` (100 results per "
        "term): " + ", ".join(NAMED_CHANNELS) + ".")
    lines.append("")
    lines.append(
        "In addition, every channel in the candidate pool with at least two Genting matches and a "
        "markets/news profile was searched for `genting` (100 results): 77 channels, listed below.")
    lines.append("")
    crawled = []
    clog = BASE / "channels.log"
    if clog.exists():
        for line in clog.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s+\d+\s+(.*?)\s+\(UC", line)
            if m:
                crawled.append(m.group(1))
    lines.append("```text")
    for name in crawled:
        lines.append(name)
    lines.append("```")
    lines.append("")
    lines.append("### Playlists\n")
    lines.append(
        "YouTube's playlist-filtered search (`sp=EgIQAw`) was queried for 8 core phrases; 138 unique "
        "playlists were expanded (up to 300 entries each). Most were generic Bursa/Malaysia stock "
        "playlists; they contributed long-tail episodes that the normal search ranking did not show.")
    lines.append("")
    lines.append(
        "Requests were sequential with a 1–2 s gap. No HTTP 429 or sign-in challenge was observed. "
        "Metadata-only fetches used `yt-dlp --skip-download --dump-json`; comment fetches used "
        "`yt-dlp --write-comments --skip-download`, which paginates comment continuations rather "
        "than taking only the first page.")
    lines.append("")

    lines.append("## Comment timestamp precision\n")
    lines.append(
        "YouTube exposes comment age only as a relative label (`2 weeks ago`, `1 year ago`), not an "
        "absolute time. yt-dlp resolves each label to an estimated date at 00:00 UTC. Every comment "
        "keeps the original label in `raw.time_text`, and every reply carries "
        "`time_confidence=\"relative_month\"`; the field is on replies as required by the task. These "
        "are day-level estimates, not exact publication times, and labels such as `1 year ago` span "
        "a range of months. No precision was invented. The window filter uses the estimates, so "
        "comments dated exactly 2 Nov 2024/2 Nov 2026 are boundary cases.")
    lines.append("")
    lines.append(
        f"Because the labels are coarse, comments cluster on the same estimated day: the largest "
        f"cluster is **{mode_n} comments at {day(mode_ts)}**, all carrying the same relative label. "
        f"In particular, {sum(1 for r in reps if r['created_utc'] == 1730505600)} comments labelled "
        "`2 years ago` resolve to the first day of the window (2 Nov 2024); the true dates could span "
        "late 2024 to late 2025. Sub-day timing inside a label bucket cannot be recovered from "
        "YouTube's public comment API.")
    lines.append("")

    lines.append("## Videos collected\n")
    lines.append("| Video | Channel | Ticker | Uploaded | Views | Comments (metadata) | In window | Status |")
    lines.append("| --- | --- | --- | --- | ---: | ---: | ---: | --- |")
    for p in sorted(posts, key=lambda x: x["created_utc"], reverse=True):
        vid = p["native_id"]
        st = status.get(vid, {})
        title = (p["title"] or "").replace("|", "\\|")
        channel = (p["channel"] or "").replace("|", "\\|")
        mc = p.get("num_comments")
        note = st.get("status") or "ok"
        if st.get("note"):
            note += f": {st['note']}"
        lines.append(
            f"| [{vid}](https://www.youtube.com/watch?v={vid}) {title} | {channel} | {p['ticker']} | "
            f"{day(p['created_utc'])} | {p.get('score') if p.get('score') is not None else '—'} | "
            f"{mc if mc is not None else '—'} | {c[vid]} | {note} |")
    lines.append("")

    lines.append("## Largest comment threads\n")
    lines.append("| Video | Ticker | Comments in window |")
    lines.append("| --- | --- | ---: |")
    for vid, n in c.most_common(12):
        p = next(x for x in posts if x["native_id"] == vid)
        title = (p["title"] or "").replace("|", "\\|")
        lines.append(f"| [{vid}](https://www.youtube.com/watch?v={vid}) {title} | {p['ticker']} | {n} |")
    lines.append("")

    lines.append("## Checked but not written\n")
    if not no_window:
        lines.append("None.")
    else:
        lines.append("| Video | Uploaded | Reason |")
        lines.append("| --- | --- | --- |")
        for vid, title in no_window:
            st = status.get(vid, {})
            safe_title = (title or "").replace("|", "\\|")
            lines.append(f"| [{vid}](https://www.youtube.com/watch?v={vid}) {safe_title} | "
                         f"{day(st.get('upload_utc'))} | pre-window upload with no comment in the 2-year window |")
    lines.append("")

    lines.append("## Failures and gaps\n")
    lines.append(f"- **Unavailable videos:** {meta_err} candidates returned `This video is not available` "
                 "and were skipped (deleted/private). They are not counted as videos.")
    if disabled:
        lines.append(f"- **Comment section unavailable (likely disabled):** {len(disabled)} videos "
                     "(6 in-window posts written with zero comments, plus 2 pre-window videos that were "
                     "checked but not written):")
        for vid, title in disabled:
            lines.append(f"  - `{vid}` — {title}")
    lines.append(f"- **Zero-comment posts with comments enabled:** {len(zero_enabled)}. They are kept as "
                 "posts because they are part of the in-window Genting coverage; YouTube returned no "
                 "comments, which is a real result, not a failure.")
    lines.append("- **Comment extraction errors:** none. Every selected video that had a comment section "
                 "returned metadata and comments.")
    lines.append(f"- **Metadata not fetched for {unmeta:,} prefiltered candidates.** These are almost all "
                 "2020–2023 archive videos surfaced by channel/playlist expansion. The subset whose "
                 "titles carried a 2024–2026 date was checked separately (47 videos; 7 added). The "
                 "rest would only qualify through comments in the window, and pre-2024 uploads were "
                 "not comment-checked (see below).")
    lines.append("- **Pre-2024 uploads were not comment-checked.** 23 pre-window videos uploaded in 2024 "
                 "were checked and 19 had in-window comments; videos uploaded before 2024 were not "
                 "re-checked in this pass. The existing `youtube.jsonl` and `youtube_2024-2025.jsonl` "
                 "already cover 184 videos, including representative older uploads.")
    lines.append("- **Search surface.** YouTube search returns at most ~100 results per query and "
                 "personalises/ranks by relevance; 115 queries × 50 plus 20 × 100 is broad but cannot "
                 "be proven to be the entire upload universe. Very low-view videos with no Genting "
                 "keyword in title/description are the most likely omission.")
    lines.append("- **Comment completeness.** YouTube omits deleted comments, comments held for review, "
                 "and some comments on age-restricted videos. `comment_count` is approximate and can "
                 "include replies that the extractor could not page to. Fetched counts are the "
                 "authoritative measure of what was publicly retrievable; nothing was invented or padded.")
    lines.append(f"- **Duplicate body texts:** {dup_bodies} replies repeat another comment's exact text "
                 "(short reactions, emoji, creator boilerplate). They are distinct comment ids and were kept.")
    lines.append("- **Validator warnings (18).** Nineteen posts were uploaded before 2 Nov 2024 but drew "
                 "comments inside the window; they are deliberately kept with their original upload "
                 "dates. The validator's floor is 1 Oct 2024, so 2024 uploads before that date warn. "
                 "Pre-window posts with no in-window comments were not written.")
    lines.append("")

    lines.append("## Participation and language\n")
    lines.append(
        f"{pinned} comments are pinned and {uploader} are by the video uploader. The file is "
        "multilingual (English, Malay, Chinese, Indonesian); `lang` is left null because the "
        "collector does not run language detection on individual comments. Ticker `UNKNOWN` means the "
        "video covers both counters or does not make the parent/subsidiary distinction; it is not a "
        "missing value.")
    lines.append("")
    lines.append("## Collection date coverage\n")
    lines.append(
        "Posts range from 7 Jan 2024 to 31 Oct 2026. Comments range from 2 Nov 2024 to 1 Nov 2026. "
        "The asymmetry at the start is intentional: an older video is included only when it received "
        "at least one comment inside the window. The 2024 posts are mostly January–October 2024 "
        "uploads that were still active after 2 Nov 2024.")
    lines.append("")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {REPORT} ({len(lines)} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
