"""Scope of the collection: which companies, keywords and subreddits."""

# Malaysian listings only (the user is tracking Genting in Malaysia).
TICKERS = {
    "GENTING": {
        "name": "Genting Berhad",
        "bursa": "3182",
        "yahoo": "GENTING.KL",
    },
    "GENM": {
        "name": "Genting Malaysia",
        "bursa": "4715",
        "yahoo": "GENM.KL",
    },
}

# Keywords used for Reddit search. Kept deliberately tight: "genting" alone also
# matches Genting Highlands travel posts, which we filter loosely by subreddit.
KEYWORDS = [
    "genting",
    "genm",
    "genting malaysia",
    "genting berhad",
    "genting share",
    "genting rights issue",
]

# Subreddits worth polling. r/MalaysiaPF is where the linked thread lives.
SUBREDDITS = [
    "MalaysiaPF",
    "malaysia",
    "BursaMalaysia",
    "MalaysianPF",
    "investing",
]

# Posts older than this are ignored by `collect` unless --days is given.
DEFAULT_LOOKBACK_DAYS = 365

# Politeness delay between API calls, seconds.
REQUEST_DELAY = 0.7
