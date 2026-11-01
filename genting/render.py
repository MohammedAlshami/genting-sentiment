"""Turn stored rows into a readable markdown transcript."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

MYT = timezone(timedelta(hours=8))


def fmt_time(ts: int | None) -> str:
    if not ts:
        return "unknown time"
    return datetime.fromtimestamp(int(ts), tz=MYT).strftime("%Y-%m-%d %H:%M MYT")


def _body(text: str | None) -> str:
    text = (text or "").strip()
    if not text:
        return "*(empty)*"
    # Keep markdown, but normalise excessive blank lines.
    lines = [line.rstrip() for line in text.splitlines()]
    out: list[str] = []
    blank = 0
    for line in lines:
        if line:
            blank = 0
            out.append(line)
        else:
            blank += 1
            if blank <= 1:
                out.append("")
    return "\n".join(out).strip()


def build_tree(comments) -> tuple[list, dict]:
    by_id = {c["id"]: c for c in comments}
    children: dict[str, list] = defaultdict(list)
    roots = []

    for comment in comments:
        parent = (comment["parent_id"] or "").removeprefix("t1_")
        if parent in by_id and parent != comment["id"]:
            children[parent].append(comment)
        else:
            roots.append(comment)

    def sort_key(c):
        return (-(c["score"] or 0), c["created_utc"] or 0)

    roots.sort(key=sort_key)
    for kids in children.values():
        kids.sort(key=sort_key)
    return roots, children


def render_thread(thread, comments, include_raw_note: bool = False) -> str:
    roots, children = build_tree(comments)
    lines: list[str] = []

    title = thread["title"] or "(untitled)"
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"- **Subreddit:** r/{thread['subreddit'] or '?'}")
    lines.append(f"- **Author:** u/{thread['author'] or '[deleted]'}")
    lines.append(f"- **Posted:** {fmt_time(thread['created_utc'])}")
    ratio = thread["upvote_ratio"]
    ratio_txt = f" ({round(ratio * 100)}% upvoted)" if ratio else ""
    lines.append(f"- **Score:** {thread['score']}{ratio_txt}")
    lines.append(f"- **Comments stored:** {len(comments)}")
    if thread["permalink"]:
        lines.append(f"- **Link:** https://www.reddit.com{thread['permalink']}")
    if thread["flair"]:
        lines.append(f"- **Flair:** {thread['flair']}")
    lines.append("")

    lines.append("## Post")
    lines.append("")
    lines.append(_body(thread["selftext"]))
    lines.append("")

    lines.append("## Comments")
    lines.append("")
    if not comments:
        lines.append("*(none)*")
        return "\n".join(lines)

    def emit(comment, depth: int) -> None:
        prefix = "> " * depth
        header = (
            f"{prefix}**u/{comment['author'] or '[deleted]'}**"
            f" · {comment['score']} point{'s' if comment['score'] != 1 else ''}"
            f" · {fmt_time(comment['created_utc'])}"
        )
        if comment["is_submitter"]:
            header += " · *OP*"
        lines.append(header)
        lines.append("")
        for line in _body(comment["body"]).splitlines():
            lines.append(f"{prefix}{line}" if line else prefix.rstrip())
        lines.append("")
        for child in children.get(comment["id"], []):
            emit(child, depth + 1)

    for root in roots:
        emit(root, 0)

    if include_raw_note:
        lines.append("---")
        lines.append("Raw API payloads are stored in the `raw_json` columns.")

    return "\n".join(lines).rstrip() + "\n"
