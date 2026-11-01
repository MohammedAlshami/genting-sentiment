#!/usr/bin/env python3
"""Build data/raw/youtube_full.jsonl from discovered + fetched YouTube videos.

Stages:
  review   -> /tmp/opencode/ytfull/review.tsv with auto relevance decisions
  fetch    -> download metadata + all comments for selected videos (cached)
  write    -> emit posts + in-window comments, excluding videos already present
              in data/raw/youtube.jsonl and data/raw/youtube_2024-2025.jsonl
  report   -> data/raw/youtube_full_report.md
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = Path("/tmp/opencode/ytfull")
META = BASE / "meta"
FULL = BASE / "full"
YTDLP = Path.home() / ".local/bin/yt-dlp"
OUT = ROOT / "data/raw/youtube_full.jsonl"
REPORT = ROOT / "data/raw/youtube_full_report.md"
REVIEW = BASE / "review.tsv"
SELECTION = BASE / "selected.json"

START = int(datetime(2024, 11, 2, tzinfo=timezone.utc).timestamp())
END = int(datetime(2026, 11, 3, tzinfo=timezone.utc).timestamp())  # exclusive
EXISTING_FILES = [ROOT / "data/raw/youtube.jsonl", ROOT / "data/raw/youtube_2024-2025.jsonl"]

GENT = re.compile(r"genting|genm|云顶|\b3182\b|\b4715\b", re.I)
GENT_STRONG = re.compile(
    r"(?i:\b(?:genm|3182|4715)\b)|\bGENTING\b|(?i:genting (?:berhad|malaysia))|"
    r"云顶大马|云顶集团|云顶有限公司")
GENT_MY = re.compile(
    r"(?i:\b(?:genm|3182|4715)\b)|\bGENTING\b|(?i:genting (?:berhad|malaysia))|"
    r"云顶大马|云顶集团")
GENT_SG = re.compile(r"Genting Singapore|SGX:\s*G13|\bG13\b", re.I)
FIN = re.compile(
    r"\b(stocks?|shares?|share price|saham|bursa|klse|klci|ticker|valuation|earnings?|results?|"
    r"revenue|profit|net loss|debt|dividend|rights? issue|cash call|bonds?|credit rating|market cap|"
    r"analysts?|target price|buy|sell|hold|invest(?:ing|ment)?|ipo|privatis|privatiz|takeover|vgo|"
    r"general offer|minority|shareholders?|agm|eps|p/e|fundamentals?|technical analysis|stock market|"
    r"crash(?:ed|es|ing)?|plung(?:e|ed|es|ing)|slump(?:ed|s)?|tumbl(?:e|ed|es|ing)|"
    r"sell-?off|rally|rebound)\b"
    r"|股价|股票|财报|业绩|股息|债务|附加股|私有化|收购|全面收购|集资|分析|暴跌|投资|股东|市值|每股|"
    r"除牌|上市|季报|年报|亏损|盈利|营收",
    re.I)
TOURISM = re.compile(
    r"hotel|resort|theme park|skyway|skyworlds|cable car|premium outlet|travel|trip|staycation|vlog|food|"
    r"restaurant|visit|kids|rides|retire|hillclimb|highlands?|gunung|naik genting|genting run|"
    r"motor|moto|hiking|trek|casino|baccarat|百家乐|betting|gambling|scholarship|云顶之弈|金铲铲|云顶新耀|"
    r"\bcar\b|\bcars\b|driving|\bdrive\b|\bbike\b|\bride\b|\brun\b|"
    r"酒店|旅游|乐园|云顶高原|自助餐|餐厅|住宿|景点|缆车|赌场攻略", re.I)
EDUCATION = re.compile(
    r"\bassignment\b|\bpresentation\b|\bstudent\b|university|college|\bHRM\b|\bPFM\b|\bMGMB\b|thesis|"
    r"strategic audit|sustainability reporting|corporate practices|financial analysis \(|"
    r"\bFAR570\b|\bHTM401\b|\bACC3228\b|group assignment|study of relationship|"
    r"financial statement analysis", re.I)
OUT_OF_SCOPE = re.compile(
    r"Genting Plantations|Genting Hong Kong|Genting SkyWorlds|Resorts World Genting|"
    r"Generation Mining|TSX:\s*GENM|TSE:\s*GENM|Genting Singapore|SGX:\s*G13", re.I)
INDONESIA = re.compile(r"IHSG|Rupiah|BKSL|Prabowo|KDM|BEI|idx|emiten", re.I)
FIN_CHANNEL = re.compile(
    r"the edge|invest|finance|saham|stock|bursa|market|财经|股市|投资|理财|论股|股票|证券|交易所|"
    r"南洋商报|百格|pocketimes|astro awani|tv3|rtm|八度空间|新闻|capital|business|forbes|bloomberg|"
    r"reuters|nikkei|money|wealth|trade", re.I)
ROUNDUP = re.compile(
    r"evening 5|morning brief|morning call|market wrap|market watch|weekly review|weekly klse|"
    r"daily klse|daily financial news|market digest|roundup|round-up|收盘|一周|市场总结", re.I)
EXPLICIT_TICKER = re.compile(
    r"(?i:\b(?:genm|3182|4715)\b)|Genting Berhad|Genting Malaysia|云顶大马|云顶集团")

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = html.unescape(value)
    value = value.replace("\u200b", "").replace("\ufeff", "")
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def epoch_from_date(date: str | None) -> int | None:
    if not date:
        return None
    try:
        return int(datetime.strptime(date, "%Y%m%d").replace(tzinfo=timezone.utc).timestamp())
    except ValueError:
        return None


def load_meta() -> dict[str, dict]:
    out = {}
    for p in META.glob("*.json"):
        if p.name.endswith(".error.json"):
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if d.get("id"):
            out[d["id"]] = d
    return out


def load_candidates() -> dict[str, dict]:
    src = BASE / "discovery" / "candidates_all.json"
    if not src.exists():
        src = BASE / "discovery" / "candidates_plus_playlists.json"
    if not src.exists():
        src = BASE / "discovery" / "candidates.json"
    return {c["id"]: c for c in json.loads(src.read_text(encoding="utf-8"))}


def classify(title: str, desc: str) -> str:
    t = f"{title}\n{desc[:800]}"
    genm = re.search(r"\bGENM\b|\b4715\b|Genting Malaysia|云顶大马|云顶马来西亚", t, re.I)
    gent = re.search(r"\bGENTING\b|\b3182\b|Genting Berhad|云顶集团|云顶有限公司", t, re.I)
    if genm and gent:
        return "UNKNOWN"
    if genm:
        return "GENM"
    if gent:
        return "GENTING"
    return "UNKNOWN"


def relevance(info: dict, cand: dict) -> tuple[int, str]:
    """Return (score, reason). Score >= 3 means auto-selected."""
    title = info.get("title") or cand.get("title") or ""
    desc = info.get("description") or cand.get("description") or ""
    tags = " ".join(info.get("tags") or [])
    channel = info.get("channel") or cand.get("channel") or ""
    t = f"{title}\n{desc}\n{tags}"
    if not GENT.search(t):
        return -10, "no Genting mention"
    if OUT_OF_SCOPE.search(title):
        return -10, "other Genting entity / tourism venue"
    if EDUCATION.search(title):
        return -10, "student / academic presentation"
    if GENT_SG.search(t) and not re.search(
            r"(?i:\b(?:genm|3182|4715)\b)|Genting Berhad|Genting Malaysia|云顶大马|云顶集团", t):
        return -10, "Genting Singapore only"
    if INDONESIA.search(title) and not GENT_STRONG.search(title):
        return -10, "Indonesian 'genting' / non-Malaysian context"
    strong_title = bool(GENT_STRONG.search(title + " " + tags))
    explicit = bool(EXPLICIT_TICKER.search(title + " " + tags))
    fin_title = bool(FIN.search(title + " " + tags))
    fin_any = bool(FIN.search(desc))
    if TOURISM.search(title) and not fin_title:
        return -10, "tourism title without finance term"
    if ROUNDUP.search(title) and not explicit:
        return -10, "generic market roundup"
    if not explicit and not fin_title:
        return -10, "no ticker or finance term in title"
    if not (strong_title or fin_title or fin_any or FIN_CHANNEL.search(channel)):
        return -10, "no finance context"
    if not (strong_title or fin_title):
        return -10, "weak mention"

    score = 0
    reasons = []
    if strong_title:
        score += 4
        reasons.append("ticker in title")
    if GENT_STRONG.search(desc):
        score += 2
        reasons.append("ticker in description")
    if fin_title:
        score += 2
        reasons.append("finance term in title")
    if fin_any:
        score += 1
        reasons.append("finance term in description")
    if FIN_CHANNEL.search(channel):
        score += 1
        reasons.append("finance/news channel")
    if ROUNDUP.search(title) and not GENT_STRONG.search(title):
        pos = desc.lower().find("genting")
        if pos < 0:
            pos = desc.find("云顶")
        if pos > 320:
            score -= 4
            reasons.append("roundup mentions Genting late")
        else:
            reasons.append("roundup with early Genting segment")
    return score, ", ".join(reasons) or "weak mention"


def review() -> None:
    metas = load_meta()
    cands = load_candidates()
    rows = []
    for vid, info in metas.items():
        cand = cands.get(vid, {})
        score, reason = relevance(info, cand)
        title = (info.get("title") or "").replace("\t", " ").replace("\n", " ")
        desc = (info.get("description") or "").replace("\t", " ").replace("\n", " ")
        rows.append({
            "id": vid,
            "upload": info.get("upload_date") or "",
            "channel": info.get("channel") or "",
            "ticker": classify(title, desc),
            "score": score,
            "reason": reason,
            "views": info.get("view_count") or 0,
            "title": title,
            "snippet": desc[:180],
            "queries": ";".join(cand.get("queries", []))[:300],
        })
    rows.sort(key=lambda r: (r["score"], r["upload"]), reverse=True)
    REVIEW.parent.mkdir(parents=True, exist_ok=True)
    def flat(v):
        return re.sub(r"[\t\r\n]+", " ", str(v or ""))
    with REVIEW.open("w", encoding="utf-8") as fh:
        fh.write("id\tupload\tchannel\tticker\tscore\treason\tviews\ttitle\tsnippet\tqueries\n")
        for r in rows:
            fh.write("\t".join(flat(r[k]) for k in
                               ["id", "upload", "channel", "ticker", "score", "reason", "views", "title", "snippet", "queries"]) + "\n")
    c = Counter("select" if r["score"] >= 3 else ("maybe" if r["score"] >= 1 else "drop") for r in rows)
    print(f"reviewed {len(rows)}: {dict(c)}")
    print(f"wrote {REVIEW}")
    sel = [{"id": r["id"], "ticker": r["ticker"], "note": r["reason"]} for r in rows if r["score"] >= 3]
    SELECTION.write_text(json.dumps(sel, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"auto-selected {len(sel)} -> {SELECTION}")


def info_path(vid: str) -> Path:
    return FULL / f"{vid}.info.json"


def fetch_comments(vid: str, force: bool = False) -> dict:
    FULL.mkdir(parents=True, exist_ok=True)
    done = FULL / f"{vid}.done"
    if done.exists() and info_path(vid).exists() and not force:
        return json.loads(info_path(vid).read_text(encoding="utf-8"))
    legacy = Path("/tmp/opencode/yt/full") / f"{vid}.info.json"
    if legacy.exists() and not force:
        info_path(vid).write_text(legacy.read_text(encoding="utf-8"), encoding="utf-8")
        done.write_text("ok\n", encoding="utf-8")
        return json.loads(info_path(vid).read_text(encoding="utf-8"))
    cmd = [
        str(YTDLP), "--write-comments", "--skip-download", "--no-warnings",
        "--no-progress", "--ignore-errors", "--socket-timeout", "30",
        "--retries", "4", "--extractor-retries", "2",
        "-o", str(FULL / "%(id)s.%(ext)s"),
        f"https://www.youtube.com/watch?v={vid}",
    ]
    print(f"comments {vid} ...", flush=True)
    started = time.monotonic()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    (FULL / f"{vid}.log").write_text(
        f"exit={proc.returncode}\nelapsed={time.monotonic()-started:.1f}s\n"
        f"--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}\n", encoding="utf-8")
    if info_path(vid).exists():
        done.write_text("ok\n", encoding="utf-8")
        return json.loads(info_path(vid).read_text(encoding="utf-8"))
    raise RuntimeError(f"no info.json for {vid}")


def comment_status(vid: str, info: dict | None, error: str | None = None) -> str:
    log = FULL / f"{vid}.log"
    text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    if "comments are disabled" in text.lower() or "comments is disabled" in text.lower():
        return "comments disabled"
    if "Sign in to confirm" in text:
        return "bot check / sign-in required"
    if "HTTP Error 429" in text or "Too Many Requests" in text:
        return "rate limited (429)"
    if "This video is not available" in text or "Private video" in text:
        return "video unavailable (deleted/private)"
    if "Unable to extract comments" in text:
        return "comment extraction failed"
    if error:
        return error
    if info is not None and "comments" not in info and info.get("comment_count") is None:
        return "comment section unavailable (likely disabled)"
    return "ok"


def existing_ids() -> set[str]:
    ids: set[str] = set()
    for path in EXISTING_FILES:
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if r.get("record_type") == "post" and r.get("source") == "youtube":
                    ids.add(str(r.get("native_id")))
    return ids


def depth_map(comments: list[dict]) -> dict[str, int]:
    parents = {c.get("id"): c.get("parent") for c in comments if c.get("id")}
    cache: dict[str, int] = {}

    def d(cid: str, guard: int = 0) -> int:
        if cid in cache:
            return cache[cid]
        p = parents.get(cid)
        if p in (None, "root") or guard > 20:
            cache[cid] = 0
        else:
            cache[cid] = d(p, guard + 1) + 1
        return cache[cid]

    return {cid: d(cid) for cid in parents}


def build(selection: list[dict]) -> None:
    skip = existing_ids()
    print(f"existing video ids excluded: {len(skip)}")
    records: list[dict] = []
    seen: set[tuple[str, str]] = set()
    statuses: dict[str, dict] = {}
    for i, spec in enumerate(selection):
        vid = spec["id"]
        if vid in skip:
            statuses[vid] = {"status": "skipped_existing", "note": "already in an existing youtube file",
                             "ticker": spec.get("ticker"), "in_window": 0, "comments_fetched": 0}
            continue
        if i and not (FULL / f"{vid}.done").exists():
            time.sleep(2.0)
        try:
            info = fetch_comments(vid)
        except Exception as exc:  # noqa: BLE001
            print(f"  ERROR {vid}: {exc}", flush=True)
            statuses[vid] = {"status": "error", "note": str(exc), "ticker": spec.get("ticker"),
                             "in_window": 0, "comments_fetched": 0}
            continue
        upload_ts = info.get("timestamp") or epoch_from_date(info.get("upload_date"))
        comments = info.get("comments") or []
        statuses[vid] = {
            "status": comment_status(vid, info),
            "note": "",
            "comments_fetched": len(comments),
            "comment_count_metadata": info.get("comment_count"),
            "upload_date": info.get("upload_date"),
            "upload_utc": int(upload_ts) if upload_ts else None,
            "title": info.get("title"),
            "channel": info.get("channel") or info.get("uploader"),
            "view_count": info.get("view_count"),
            "ticker": spec.get("ticker") or "UNKNOWN",
        }
        in_window = [c for c in comments if isinstance(c.get("timestamp"), int)
                     and START <= c["timestamp"] < END]
        if upload_ts is None or (upload_ts < START and not in_window):
            statuses[vid]["note"] = "no in-window comments; post not written"
            statuses[vid]["in_window"] = 0
            continue
        channel = info.get("channel") or info.get("uploader")
        description = info.get("description") or ""
        post_rec = {
            "record_type": "post",
            "source": "youtube",
            "channel": channel,
            "native_id": vid,
            "ticker": spec.get("ticker") or "UNKNOWN",
            "title": info.get("title"),
            "author": channel,
            "author_id": info.get("channel_id"),
            "created_utc": int(upload_ts),
            "url": f"https://www.youtube.com/watch?v={vid}",
            "body": description[:2000] or None,
            "score": info.get("view_count"),
            "num_comments": info.get("comment_count"),
            "lang": None,
            "raw": {
                "id": vid,
                "channel_id": info.get("channel_id"),
                "upload_date": info.get("upload_date"),
                "timestamp": info.get("timestamp"),
                "duration": info.get("duration"),
                "view_count": info.get("view_count"),
                "like_count": info.get("like_count"),
                "comment_count": info.get("comment_count"),
                "categories": info.get("categories"),
                "tags": (info.get("tags") or [])[:25],
                "availability": info.get("availability"),
                "age_limit": info.get("age_limit"),
                "webpage_url": info.get("webpage_url"),
                "description": description[:2000] or None,
            },
        }
        if ("youtube", vid) not in seen:
            records.append(post_rec)
            seen.add(("youtube", vid))
        depths = depth_map(comments)
        for c in sorted(in_window, key=lambda x: (x["timestamp"], x.get("id") or "")):
            cid = c.get("id")
            if not cid or ("youtube", cid) in seen:
                continue
            parent = c.get("parent")
            if parent in (None, "root"):
                parent_id = None
                depth = 0
            else:
                parent_id = str(parent)
                depth = depths.get(cid, 1)
            body = clean_text(c.get("text")) or "[deleted]"
            raw = {
                "id": cid,
                "parent": parent,
                "text": c.get("text"),
                "timestamp": c.get("timestamp"),
                "time_text": c.get("_time_text"),
                "like_count": c.get("like_count"),
                "author": c.get("author"),
                "author_id": c.get("author_id"),
                "author_is_uploader": c.get("author_is_uploader"),
                "author_is_verified": c.get("author_is_verified"),
                "is_favorited": c.get("is_favorited"),
                "is_pinned": c.get("is_pinned"),
                "reply_count": c.get("reply_count"),
            }
            records.append({
                "record_type": "reply",
                "source": "youtube",
                "channel": channel,
                "native_id": cid,
                "post_native_id": vid,
                "parent_native_id": parent_id,
                "depth": depth,
                "author": c.get("author"),
                "author_id": c.get("author_id"),
                "created_utc": int(c["timestamp"]),
                "body": body,
                "score": c.get("like_count"),
                "url": f"https://www.youtube.com/watch?v={vid}&lc={cid}",
                "lang": None,
                "time_confidence": "relative_month",
                "raw": raw,
            })
        statuses[vid]["in_window"] = len(in_window)
        statuses[vid]["min_comment_utc"] = min((c["timestamp"] for c in in_window), default=None)
        statuses[vid]["max_comment_utc"] = max((c["timestamp"] for c in in_window), default=None)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    (BASE / "build_status.json").write_text(
        json.dumps(statuses, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {len(records)} records to {OUT}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["review", "fetch", "write", "report"])
    ap.add_argument("--select", type=Path, default=SELECTION)
    args = ap.parse_args()
    if args.stage == "review":
        review()
    elif args.stage == "fetch":
        sel = json.loads(args.select.read_text(encoding="utf-8"))
        for i, spec in enumerate(sel):
            vid = spec["id"]
            if (FULL / f"{vid}.done").exists():
                continue
            if i:
                time.sleep(2.0)
            try:
                info = fetch_comments(vid)
                print(f"  {vid}: {len(info.get('comments') or [])} comments", flush=True)
            except Exception as exc:  # noqa: BLE001
                print(f"  ERROR {vid}: {exc}", flush=True)
    elif args.stage == "write":
        sel = json.loads(args.select.read_text(encoding="utf-8"))
        build(sel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
