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
    # --- NBA / basketball (heavy — your main lane) ---
    ("ESPN NBA", "https://www.espn.com/espn/rss/nba/news"),
    ("HoopsHype", "https://hoopshype.com/feed/"),
    ("r/NBA", "https://www.reddit.com/r/nba/.rss"),
    ("r/NBA Discussion", "https://www.reddit.com/r/nbadiscussion/.rss"),
    ("r/NBA Analytics", "https://www.reddit.com/r/nbaanalysis/.rss"),

    # --- Sports (volleyball, fantasy football, general) ---
    ("Volleyball Mag", "https://volleyballmag.com/feed/"),
    ("ESPN Sports", "https://www.espn.com/espn/rss/news"),
    ("r/FantasyFootball", "https://www.reddit.com/r/fantasyfootball/.rss"),

    # --- Tech / AI (Apple, Anthropic/LLMs, consumer tech) ---
    ("Stratechery", "https://stratechery.com/feed/"),
    ("Daring Fireball", "https://daringfireball.net/feeds/main"),
    ("Simon Willison", "https://simonwillison.net/atom/everything/"),
    ("MKBHD", "https://www.youtube.com/feeds/videos.xml?channel_id=UCBJycsmduvYEL83R_U4JriQ"),
    ("Hacker News", "https://hnrss.org/frontpage"),
    ("r/MachineLearning", "https://www.reddit.com/r/MachineLearning/.rss"),
    ("r/Artificial", "https://www.reddit.com/r/artificial/.rss"),

    # --- Faith / culture (Presbyterian/Reformed lean) ---
    ("The Gospel Coalition", "https://www.thegospelcoalition.org/feed/"),
    ("Desiring God", "https://www.desiringgod.org/articles.rss"),
    ("Ligonier", "https://www.ligonier.org/blog/feed/"),

    # --- Film / scores ---
    ("IndieWire", "https://www.indiewire.com/feed/"),

    # --- Music ---
    ("Pitchfork", "https://pitchfork.com/feed/feed-album-reviews/rss"),

    # --- World Cup 2026 / soccer ---
    ("ESPN Soccer", "https://www.espn.com/espn/rss/soccer/news"),

    # --- General / world ---
    ("AP Top News", "https://rsshub.app/apnews/topics/apf-topnews"),
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
I'm Anderson — a college student and builder. My Christian faith is central to
who I am, and I'm a serious sports/analytics nerd. There's no strict ranking
between these areas (balance is handled separately) — what matters is judging
relevance WELL WITHIN each area:

- NBA: the THINKING side — lineup construction, advanced stats, roster building,
  trades and their second-order effects, front-office strategy, draft analysis.
  Score analytical/strategic pieces high; score gossip and pure highlights low.
- Faith: Reformed/Presbyterian theology and culture (The Gospel Coalition,
  Desiring God, Ligonier). Score substantive theology and thoughtful cultural
  commentary high; score surface devotional filler and prosperity-gospel low.
- Sports: volleyball especially, plus basketball/football analysis and fantasy
  football (lineup/start-sit/waiver strategy).
- Tech/AI: predictive modeling, applied ML, and forecasting — especially applied
  to sports or real decisions. Also Apple (products, the company), Anthropic and
  the broader LLM/AI race (Claude, frontier models), and sharp consumer-tech
  reviews and analysis (MKBHD-style). Score thoughtful analysis high, rumor-mill
  churn lower.
- Film: high-concept sci-fi and great film scores.
- Music: album reviews and music criticism (Pitchfork), jazz, and film scores.
- World Cup 2026: results, storylines, tactical breakdowns.
- World: genuinely important news an informed person should know.

Always score as noise (low relevance): celebrity gossip, clickbait,
marketing/advertising industry news, prosperity gospel, and opinion ragebait.
"""


# ---------------------------------------------------------------------------
# 4. TUNING
# ---------------------------------------------------------------------------

# How many stories to show per dispatch (hard cap; you'll only see fewer if the
# feeds genuinely didn't produce this many fresh, relevant articles this run).
MAX_STORIES = 50

# Per-category minimums. Code guarantees at least this many of each — IF that
# many relevant articles exist in the pool. Remaining slots (up to MAX_STORIES)
# fill by overall relevance. Minimums should sum to <= MAX_STORIES.
CATEGORY_MINIMUMS = {
    "NBA":     8,
    "Faith":   3,
    "Sports":  3,
    "Tech/AI": 3,
    "Film":    2,
    "Music":   2,
    "World":   3,
    "Other":   1,
}

# How many raw headlines to triage per run. Bigger pool = better odds of filling
# 50 and hitting minimums. The triage pass is cheap (no summaries), so go big.
MAX_HEADLINES_TO_AI = 150

# Only consider articles published within this many hours (keeps it fresh).
# Widen this if you aren't consistently filling 50 stories.
FRESHNESS_HOURS = 24

# Groq model. llama-3.3-70b-versatile is free and strong. If you hit rate limits
# at this volume, swap to "llama-3.1-8b-instant" (faster, higher limits).
GROQ_MODEL = "llama-3.3-70b-versatile"
