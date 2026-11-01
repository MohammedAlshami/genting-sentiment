"""Widen Reddit discovery through Arctic Shift's post search (read-only)."""
import json, time, urllib.parse, urllib.request

BASE = "https://arctic-shift.photon-reddit.com/api/posts/search"
UA = "genting-sentiment/0.1 (research collector)"
SUBS = ["MalaysiaPF", "MalaysianPF", "malaysia", "BursaMalaysia", "bursabets", "investing"]
QUERIES = ["genting", "GENM", "3182", "4715", "genting malaysia", "genting berhad"]

def get(params):
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except Exception as e:
            print("retry", attempt, e)
            time.sleep(2 ** attempt)
    raise SystemExit("failed " + url)

out = {}
for sub in SUBS:
    for q in QUERIES:
        d = get({"subreddit": sub, "query": q, "limit": 100, "sort": "desc"})
        data = d.get("data", [])
        print(sub, q, len(data))
        for p in data:
            out[p["id"]] = p
        time.sleep(1.2)

json.dump(list(out.values()), open("/tmp/opencode/arctic_candidates.json", "w"))
print("unique", len(out))
