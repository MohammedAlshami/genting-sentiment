"""Reddit collector backed by the Arctic Shift archive API.

Reddit itself returns 403 to anonymous JSON requests from this machine, so we
read the same posts and comments through Arctic Shift, which mirrors Reddit and
exposes a public API. Trade-off: the mirror can lag a day or two behind live
Reddit, which is fine for daily sentiment buckets.
"""

from __future__ import annotations

import re
import time
from typing import Iterable

import requests

from .. import config

BASE = "https://arctic-shift.photon-reddit.com/api"
USER_AGENT = "genting-sentiment/0.1 (research collector)"
PAGE_SIZE = 100


class ArcticShiftError(RuntimeError):
    pass


_session = requests.Session()
_session.headers.update({"User-Agent": USER_AGENT})


def _get(path: str, params: dict, retries: int = 4, timeout: int = 90) -> dict:
    url = f"{BASE}{path}"
    last_error: Exception | None = None

    for attempt in range(retries):
        try:
            resp = _session.get(url, params=params, timeout=timeout)
        except requests.RequestException as exc:
            last_error = exc
        else:
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code in (429, 500, 502, 503, 504):
                last_error = ArcticShiftError(f"{resp.status_code} from {path}")
            else:
                raise ArcticShiftError(f"{resp.status_code} from {path}: {resp.text[:200]}")
        time.sleep(config.REQUEST_DELAY * (2**attempt))

    raise ArcticShiftError(f"giving up on {path}: {last_error}")


_POST_ID_RE = re.compile(r"/comments/([a-z0-9]+)", re.IGNORECASE)


def parse_post_id(value: str) -> str:
    """Accept a full Reddit URL, a t3_ id, or a bare post id."""
    value = value.strip()
    match = _POST_ID_RE.search(value)
    if match:
        return match.group(1)
    return value.removeprefix("t3_")


def fetch_post(post_id: str) -> dict:
    payload = _get("/posts/ids", {"ids": post_id})
    data = payload.get("data") or []
    if not data:
        raise ArcticShiftError(f"post {post_id} not found in the archive")
    return data[0]


def fetch_comments(link_id: str) -> list[dict]:
    """Every comment in a thread, including nested replies, oldest first.

    The archive returns comments flat with parent_id/depth, which is all we need
    to rebuild the tree. Paginate by created_utc; the cursor is inclusive, so
    dedupe by id.
    """
    comments: dict[str, dict] = {}
    cursor: int | None = None

    while True:
        params = {
            "link_id": link_id,
            "limit": PAGE_SIZE,
            "sort": "asc",
        }
        if cursor is not None:
            params["after"] = cursor

        page = _get("/comments/search", params).get("data") or []
        if not page:
            break

        new = 0
        for comment in page:
            if comment["id"] not in comments:
                comments[comment["id"]] = comment
                new += 1

        newest = max(int(c.get("created_utc") or 0) for c in page)
        if len(page) < PAGE_SIZE or new == 0 or newest == cursor:
            break
        cursor = newest
        time.sleep(config.REQUEST_DELAY)

    return sorted(comments.values(), key=lambda c: (c.get("created_utc") or 0, c["id"]))


def search_posts(
    subreddit: str,
    query: str,
    after: int | None = None,
    limit: int = PAGE_SIZE,
) -> Iterable[dict]:
    """Yield posts in one subreddit matching a keyword, oldest first."""
    cursor = after
    seen: set[str] = set()

    while True:
        params = {
            "subreddit": subreddit,
            "query": query,
            "limit": limit,
            "sort": "asc",
        }
        if cursor is not None:
            params["after"] = cursor

        try:
            page = _get("/posts/search", params).get("data") or []
        except ArcticShiftError as exc:
            raise ArcticShiftError(f"search r/{subreddit} for {query!r} failed: {exc}") from exc

        if not page:
            return

        fresh = 0
        for post in page:
            if post["id"] in seen:
                continue
            seen.add(post["id"])
            fresh += 1
            yield post

        newest = max(int(p.get("created_utc") or 0) for p in page)
        if len(page) < limit or fresh == 0 or newest == cursor:
            return
        cursor = newest
        time.sleep(config.REQUEST_DELAY)
