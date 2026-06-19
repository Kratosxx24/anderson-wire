"""
config.py — your sources and your interest profile.

This is the only file you ever really need to edit to tune the app.
Add/remove RSS feeds, change the interest profile, adjust how many
stories you want per run.
"""

# ---------------------------------------------------------------------------
# 1. RSS FEEDS
# ---------------------------------------------------------------------------
# Each entry: (label, url). The label is just for your own reference and gets
# attached to stories so you can see where things came from. Add as many as
# you like — more feeds = more raw material for the AI to filter from.
#
# To find a feed for a site, try <site-url>/feed, /rss, or /feed.xml, or
# search "<site name> rss". Reddit feeds are just <subreddit-url>/.rss
# ---------------------------------------------------------------------------

RSS_FEEDS = [
    # --- NBA / basketball ---
    ("ESPN NBA", "https://www.espn.com/espn/rss/nba/news"),
    ("r/NBA", "https://www.reddit.com/r/nba/.rss"),
    ("HoopsHype", "https://hoopshype.com/feed/"),
    ("Reddit NBA Analytics", "https://www.reddit.com/r/nbadiscussion/.rss"),

    # --- Volleyball / other sports ---
    ("Volleyball Mag", "https://volleyballmag.com/feed/"),

    # --- Tech / AI / predictive modeling ---
    ("Hacker News", "https://hnrss.org/frontpage"),
    ("r/MachineLearning", "https://www.reddit.com/r/MachineLearning/.rss"),

    # --- Faith / culture ---
    ("Christianity Today", "https://www.christianitytoday.com/rss/"),
    ("The Gospel Coalition", "https://www.thegospelcoalition.org/feed/"),

    # --- Film / scores ---
    ("IndieWire", "https://www.indiewire.com/feed/"),

    # --- World Cup 2026 / soccer ---
    ("ESPN Soccer", "https://www.espn.com/espn/rss/soccer/news"),

    # --- General / world ---
    ("Reuters Top News", "https://www.reutersagency.com/feed/?best-topics=top-news&post_type=best"),
]


# ---------------------------------------------------------------------------
# 2. NEWSAPI KEYWORDS (optional layer)
# ---------------------------------------------------------------------------
# NewsAPI lets you pull keyword-based headlines on top of the RSS feeds.
# Free tier = 100 requests/day, so keep this list short. Each keyword = 1
# request per run. Leave the list empty ([]) to skip NewsAPI entirely and
# run on RSS alone (fully free, no key needed).
# ---------------------------------------------------------------------------

NEWSAPI_KEYWORDS = [
    "NBA trade",
    "FIFA World Cup 2026",
]


# ---------------------------------------------------------------------------
# 3. YOUR INTEREST PROFILE
# ---------------------------------------------------------------------------
# This is the heart of the personalization. The AI reads this verbatim and
# uses it to decide what's worth your attention. Write it like you're
# describing yourself to a sharp assistant. Be specific — "NBA lineup
# construction and advanced stats" gets you better results than "basketball".
# ---------------------------------------------------------------------------

INTEREST_PROFILE = """
I'm Anderson — a college student, builder, and sports/analytics nerd. Here's
what I actually care about, roughly in priority order:

1. NBA, but the THINKING side of it: lineup construction, advanced stats,
   roster building, trades and their second-order effects, front-office moves.
   I care less about gossip and highlight noise, more about why teams win.
2. Volleyball (my favorite sport to play), plus basketball and football
   generally.
3. Predictive modeling, applied ML, and data-driven forecasting — especially
   anything I could apply to sports or business.
4. Christian faith and culture, from a thoughtful Protestant/Presbyterian lens.
5. High-concept sci-fi film and great film scores (think Interstellar, Blade
   Runner 2049, Dune) and jazz.
6. The 2026 FIFA World Cup.
7. Genuinely major world news I should know about as an informed person.

Skip: celebrity gossip, clickbait, pure opinion ragebait, marketing/advertising
industry news, and anything that's all heat and no signal.
"""


# ---------------------------------------------------------------------------
# 4. TUNING
# ---------------------------------------------------------------------------

# How many stories the AI should surface each run.
MAX_STORIES = 25

# How many raw headlines to feed the AI per run. Higher = more to choose from
# but a bigger prompt. 60–100 is a good balance for the free tier.
MAX_HEADLINES_TO_AI = 90

# Only consider articles published within this many hours (keeps it fresh).
FRESHNESS_HOURS = 24

# Groq model. llama-3.3-70b-versatile is free and strong. If you ever hit
# rate limits, swap to "llama-3.1-8b-instant" (faster, lighter).
GROQ_MODEL = "llama-3.3-70b-versatile"
