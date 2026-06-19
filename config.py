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
    ("Hoops Rumors", "https://www.hoopsrumors.com/feed"),
    ("HoopsHype", "https://hoopshype.com/feed/"),
    ("r/NBA", "https://www.reddit.com/r/nba/.rss"),
    ("r/NBA Discussion", "https://www.reddit.com/r/nbadiscussion/.rss"),
    ("r/NBA Analytics", "https://www.reddit.com/r/nbaanalysis/.rss"),

    # --- Volleyball / other sports ---
    ("Volleyball Mag", "https://volleyballmag.com/feed/"),
    ("ESPN Sports", "https://www.espn.com/espn/rss/news"),

    # --- Tech / AI / predictive modeling ---
    ("Hacker News", "https://hnrss.org/frontpage"),
    ("r/MachineLearning", "https://www.reddit.com/r/MachineLearning/.rss"),
    ("r/Artificial", "https://www.reddit.com/r/artificial/.rss"),

    # --- Faith / culture (Presbyterian/Reformed lean) ---
    ("The Gospel Coalition", "https://www.thegospelcoalition.org/feed/"),
    ("Desiring God", "https://www.desiringgod.org/articles.rss"),
    ("Ligonier", "https://www.ligonier.org/blog/feed/"),

    # --- Film / scores ---
    ("IndieWire", "https://www.indiewire.com/feed/"),

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
I'm Anderson — a college student, builder, and sports/analytics nerd. Here's
what I actually care about, roughly in priority order:

1. NBA, but the THINKING side: lineup construction, advanced stats, roster
   building, trades and their second-order effects, front-office strategy,
   draft analysis. Less gossip, more signal — why teams win or lose.
2. Volleyball (my favorite sport to play) and sports analytics broadly.
3. Predictive modeling, applied ML, data-driven forecasting — especially
   applied to sports or real-world decision-making.
4. Christian faith and culture from a Reformed/Presbyterian lens — theology,
   culture commentary, the intersection of faith and modern life. Sources I
   trust: The Gospel Coalition, Desiring God, Ligonier. Skip surface-level
   devotional content and anything from a prosperity-gospel angle.
5. High-concept sci-fi film and great film scores (Interstellar, Blade Runner
   2049, Dune, Ex Machina) and jazz.
6. The 2026 FIFA World Cup — results, storylines, tactical breakdowns.
7. Genuinely important world news I should know as an informed person.

Skip entirely: celebrity gossip, clickbait, marketing/advertising industry
news, prosperity gospel, opinion ragebait, and anything that's heat over signal.
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
