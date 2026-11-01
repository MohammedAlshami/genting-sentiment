#!/usr/bin/env python3
"""Facebook public-post collector for the 2-year Genting window.

Reads seed URLs from a JSON file (list of {"url", "query"}), fetches each public
post URL logged-out with curl_cffi, extracts the post and every comment that
Facebook renders in the public HTML, and writes the contract JSONL.

No cookies, no credentials, no login. Existing records may be merged with
--merge so the output covers 2 Nov 2024 -> 2 Nov 2026 without duplication.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html as html_lib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "raw" / "cache" / "facebook" / "posts"

WINDOW_START = int(datetime(2024, 11, 2, tzinfo=timezone.utc).timestamp())
WINDOW_END = int(datetime(2026, 11, 2, 23, 59, 59, tzinfo=timezone.utc).timestamp())


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode()).hexdigest()[:12]


def norm(text: str | None) -> str:
    if not text:
        return ""
    text = html_lib.unescape(text)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fetch(url: str) -> tuple[str, int, str]:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{sha1(url)}.html"
    if path.exists() and path.stat().st_size > 10_000:
        return path.read_text(encoding="utf-8"), 200, url
    last_err = None
    for attempt in range(3):
        try:
            r = requests.get(url, impersonate="chrome", timeout=45, allow_redirects=True)
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(2**attempt * 3)
                continue
            path.write_text(r.text, encoding="utf-8")
            time.sleep(2.0)
            return r.text, r.status_code, str(r.url)
        except Exception as exc:  # network errors
            last_err = exc
            time.sleep(2**attempt * 3)
    raise RuntimeError(f"fetch failed for {url}: {last_err!r}")


def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk(value)


def load_json_scripts(html: str):
    objects = []
    for raw in re.findall(r'<script type="application/json"[^>]*>(.*?)</script>', html, re.S):
        try:
            objects.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return objects


def decode_comment_id(value: str | None) -> str | None:
    if not value:
        return None
    try:
        padded = value + "=" * (-len(value) % 4)
        return base64.b64decode(padded).decode("utf-8", "replace")
    except Exception:
        return None


def pick_post_id(html: str, objects) -> str | None:
    counts: dict[str, int] = {}
    for obj in walk(objects):
        pid = obj.get("post_id")
        if isinstance(pid, str) and pid.isdigit():
            counts[pid] = counts.get(pid, 0) + 1
    if counts:
        return max(counts, key=counts.get)
    nums = re.findall(r"/(\d+)/?$", html)
    return nums[-1] if nums else None


def infer_ticker(text: str, page: str = "") -> str:
    t = (text or "").lower()
    page = (page or "").lower()
    if any(k in t for k in ("genm", "4715", "genting malaysia", "云顶大马", "云顶马来西亚")):
        return "GENM"
    if any(k in t for k in ("genting berhad", "3182", "genting bhd", "云顶集团", "云顶（genting", "genting (")):
        return "GENTING"
    if any(k in page for k in ("gentingmalaysia", "resortsworldgenting")):
        return "GENM"
    if "genting" in t or "云顶" in t:
        return "UNKNOWN"
    return "UNKNOWN"


def parse_post(url: str, seed: dict) -> tuple[dict | None, list[dict], dict]:
    """Return (post, replies, log). Post is None when out of window/unparseable."""
    html, status, final_url = fetch(url)
    objects = load_json_scripts(html)
    post_id = pick_post_id(html, objects)
    log = {"url": url, "status": status, "query": seed.get("query")}
    if not post_id:
        log["reason"] = "no post id"
        return None, [], log
    log["post_id"] = post_id

    story = None
    for obj in walk(objects):
        if (
            obj.get("__typename") == "Story"
            and str(obj.get("post_id")) == post_id
            and isinstance(obj.get("comet_sections"), dict)
        ):
            msg = (
                ((obj.get("comet_sections") or {}).get("content") or {})
                .get("story", {})
                .get("message")
                or {}
            ).get("text")
            if msg:
                story = obj
                break

    message = ""
    author = author_id = created = None
    time_source = None

    if story:
        message = (
            ((story.get("comet_sections") or {}).get("content") or {})
            .get("story", {})
            .get("message", {})
            .get("text", "")
        )
        created = story.get("creation_time")
        time_source = "story.creation_time"
        actors = story.get("actors") or []
        if actors:
            author = actors[0].get("name")
            author_id = actors[0].get("id")

    if created is None:
        video_match = re.search(r"/(?:videos|reel)/(?:[^/]+/)?(\d+)/?$", url)
        video_id = video_match.group(1) if video_match else None
        if video_id:
            m = re.search(r'"videoId":"' + re.escape(video_id) + r'"', html)
            if m:
                pm = re.search(r'"publish_time":(\d+)', html[m.start() : m.start() + 1500])
                if pm:
                    created = int(pm.group(1))
                    time_source = "video.publish_time"

    if created is None:
        for m in re.finditer(r'"post_id":"' + re.escape(post_id) + r'"', html):
            window = html[max(0, m.start() - 2500) : m.start() + 2500]
            times = re.findall(r'"creation_time":(\d+)', window)
            if times:
                created = int(times[0])
                time_source = "story.creation_time (near post_id)"
                break

    if created is None:
        times = re.findall(r'"creation_time":(\d+)', html)
        if times:
            created = int(times[0])
            time_source = "first creation_time on page"

    og_desc = ""
    m = re.search(r'<meta property="og:description" content="([^"]*)"', html)
    if m:
        og_desc = norm(html_lib.unescape(m.group(1)))
    if not message:
        candidates = []
        for m in re.finditer(r'"message":\{"text":"((?:[^"\\]|\\.)*)"', html):
            try:
                text = json.loads('"' + m.group(1) + '"')
            except json.JSONDecodeError:
                continue
            text = norm(text)
            if text:
                candidates.append(text)
        if candidates:
            prefix = og_desc[:40]
            match = [c for c in candidates if prefix and c.startswith(prefix)]
            message = match[0] if match else max(candidates, key=len)
        elif og_desc:
            message = og_desc

    if not message and og_desc:
        message = og_desc

    if not author:
        am = re.search(r'"actors":\[\{"__typename":"User","name":"([^"]+)"', html)
        if am:
            author = html_lib.unescape(am.group(1))
            aid = re.search(
                r'"actors":\[\{"__typename":"User","name":"' + re.escape(am.group(1)) + r'","id":"(\d+)"',
                html,
            )
            if aid:
                author_id = aid.group(1)

    comments: dict[str, dict] = {}
    for obj in walk(objects):
        if obj.get("__typename") != "Comment":
            continue
        body = (obj.get("body") or {}).get("text")
        if not body or not body.strip():
            continue
        cid = obj.get("legacy_fbid")
        if not cid:
            decoded = decode_comment_id(obj.get("id"))
            if decoded and "_" in decoded:
                cid = decoded.rsplit("_", 1)[-1]
        if not cid:
            continue
        parent = None
        pd = obj.get("comment_direct_parent") or {}
        decoded_parent = decode_comment_id(pd.get("id"))
        if decoded_parent and "_" in decoded_parent:
            parent = decoded_parent.rsplit("_", 1)[-1]
        comments[str(cid)] = {
            "id": str(cid),
            "parent": parent,
            "depth": int(obj.get("depth") or 0),
            "created": obj.get("created_time"),
            "author": (obj.get("author") or {}).get("name"),
            "author_id": (obj.get("author") or {}).get("id"),
            "body": norm(body),
        }

    total_m = re.search(
        r'"comment_rendering_instance":\{"comments":\{"total_count":(\d+)\}', html
    )
    comment_total = int(total_m.group(1)) if total_m else None

    comment_rows = []
    for c in sorted(comments.values(), key=lambda x: x["created"] or 0):
        if not c["created"] or not isinstance(c["created"], int):
            continue
        if not (WINDOW_START <= c["created"] <= WINDOW_END):
            continue
        comment_rows.append(c)

    log["created_utc"] = created
    log["comments_total"] = comment_total
    log["comments_captured"] = len(comment_rows)
    if created is None or not (WINDOW_START <= created <= WINDOW_END):
        log["reason"] = "outside window or no timestamp"
        return None, [], log

    path = url.split("facebook.com/", 1)[-1]
    if path.startswith("groups/"):
        log["reason"] = "group post (excluded)"
        return None, [], log
    channel = path.split("/", 1)[0]

    title = next((ln.strip() for ln in message.splitlines() if ln.strip()), "")
    if not title:
        title = f"{author or channel} post {post_id}"
    if len(title) > 200:
        title = title[:197].rstrip() + "..."

    body_lower = message.lower()
    seed_ticker = seed.get("ticker")
    if seed_ticker in ("GENTING", "GENM"):
        ticker = seed_ticker
    else:
        ticker = infer_ticker(message + " " + title, channel)
        if ticker == "UNKNOWN" and infer_ticker("", channel) == "GENM":
            ticker = "GENM"

    raw = {
        "post_id": post_id,
        "story_id": story.get("id") if story else None,
        "page_id": author_id,
        "comment_total_count": comment_total,
        "comments_captured": len(comment_rows),
        "comment_gap": (comment_total - len(comment_rows)) if comment_total is not None else None,
        "privacy": "Public" if '"description":"Public"' in html else None,
        "time_source": time_source,
        "discovery_query": seed.get("query"),
        "seed_ticker": seed_ticker,
        "access_note": (
            "Fetched from the direct public post URL without cookies or login; "
            "Facebook served the post body and the top comments in logged-out HTML."
        ),
        "fetched_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "http_status": status,
        "final_url": final_url,
        "body_truncated": bool(re.search(r"(\.\.\.|…)\s*$", message)),
    }

    post = {
        "record_type": "post",
        "source": "facebook",
        "channel": channel,
        "native_id": post_id,
        "ticker": ticker,
        "title": title,
        "author": author,
        "author_id": author_id,
        "created_utc": int(created),
        "url": url,
        "body": message or None,
        "score": None,
        "num_comments": comment_total,
        "lang": None,
        "raw": raw,
    }

    replies = []
    sep = "&" if "?" in url else "?"
    for c in comment_rows:
        replies.append(
            {
                "record_type": "reply",
                "source": "facebook",
                "channel": channel,
                "native_id": c["id"],
                "post_native_id": post_id,
                "parent_native_id": c["parent"],
                "depth": c["depth"],
                "author": c["author"],
                "author_id": c["author_id"],
                "created_utc": int(c["created"]),
                "body": c["body"],
                "score": None,
                "url": f"{url}{sep}comment_id={c['id']}",
                "lang": None,
                "raw": {
                    "post_id": post_id,
                    "comment_total_count": comment_total,
                    "comments_captured": len(comment_rows),
                    "comment_gap": (comment_total - len(comment_rows)) if comment_total is not None else None,
                    "access_note": raw["access_note"],
                },
            }
        )
    return post, replies, log


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("seeds", type=Path, help="JSON list of {url, query, ticker?}")
    ap.add_argument("--out", type=Path, default=ROOT / "data/raw/facebook_2y.jsonl")
    ap.add_argument("--merge", type=Path, action="append", default=[])
    ap.add_argument("--log", type=Path, default=ROOT / "data/raw/facebook_2y_fetch_log.json")
    args = ap.parse_args()

    seeds = json.loads(args.seeds.read_text(encoding="utf-8"))
    records: list[dict] = []
    seen: set[tuple[str, str]] = set()
    logs = []
    skipped = []

    # Preserve existing rows first (the one-year file must not be touched).
    for path in args.merge:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            key = (rec.get("source"), str(rec.get("native_id")))
            if key in seen:
                continue
            seen.add(key)
            records.append(rec)

    for seed in seeds:
        url = seed["url"]
        try:
            post, replies, log = parse_post(url, seed)
        except Exception as exc:
            skipped.append({"url": url, "reason": f"error: {exc!r}"})
            continue
        logs.append(log)
        if not post:
            skipped.append({"url": url, "reason": log.get("reason", "unparsed")})
            continue
        key = ("facebook", post["native_id"])
        if key in seen:
            skipped.append({"url": url, "post_id": post["native_id"], "reason": "duplicate"})
            continue
        seen.add(key)
        records.append(post)
        for rep in replies:
            rkey = ("facebook", rep["native_id"])
            if rkey in seen:
                continue
            seen.add(rkey)
            records.append(rep)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    posts = [r for r in records if r["record_type"] == "post"]
    log_obj = {
        "window_start_utc": WINDOW_START,
        "window_end_utc": WINDOW_END,
        "seeds": len(seeds),
        "posts_written": len(posts),
        "replies_written": sum(1 for r in records if r["record_type"] == "reply"),
        "min_created_utc": min((p["created_utc"] for p in posts), default=None),
        "max_created_utc": max((p["created_utc"] for p in posts), default=None),
        "fetch_log": logs,
        "skipped": skipped,
    }
    args.log.write_text(json.dumps(log_obj, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {args.out} ({len(records)} records)")
    print(f"posts={len(posts)} replies={log_obj['replies_written']}")
    for entry in skipped:
        print("skipped:", entry)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
