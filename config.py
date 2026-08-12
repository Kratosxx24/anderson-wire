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
    # ESPN NBA, CBS Sports NBA, Yahoo Sports NBA, ClutchPoints, and BasketballNews
    # all dropped 2026-08-12 — wire/tabloid reporting the profile scores low, or
    # (ESPN) dead. Kept a pure analytical/front-office-strategy lane instead.
    ("Third Apron", "https://www.thirdapron.com/feed"),          # salary cap / CBA mechanics
    ("Neil Paine", "https://neilpaine.substack.com/feed"),        # stats-driven analysis
    ("The Finder", "https://www.tomthefinder.com/feed"),          # team-strength / title-race analysis
    ("Basketball Intelligence", "https://www.basketballintelligence.net/feed"),  # curated daily digest
    ("r/NBA", "https://www.reddit.com/r/nba/.rss"),
    ("r/NBA Discussion", "https://www.reddit.com/r/nbadiscussion/.rss"),
    ("r/NBA Analytics", "https://www.reddit.com/r/nbaanalysis/.rss"),

    # --- NFL / football (analytical lane, added 2026-08-12, same bar as NBA) ---
    ("Cap & Trade", "https://www.capandtrade.football/feed"),      # salary cap / roster building
    ("MatchQuarters", "https://www.matchquarters.com/feed"),        # schematic / defensive breakdowns
    ("Too Deep Zone", "https://miketanier.substack.com/feed"),      # veteran analytics writer

    # --- Sports (volleyball, fantasy football, general) ---
    ("Volleyball Mag", "https://volleyballmag.com/feed/"),
    # ESPN Sports replaced 2026-08-12: same ESPN bot-block as above.
    ("CBS Sports", "https://www.cbssports.com/rss/headlines/"),
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
    ("Challies", "https://www.challies.com/feed/"),
    ("Tabletalk", "https://tabletalkmagazine.com/feed/"),
    ("9Marks", "https://www.9marks.org/feed/"),

    # --- Music ---
    ("Pitchfork", "https://pitchfork.com/feed/feed-album-reviews/rss"),

    # --- World Cup 2026 / soccer ---
    # ESPN Soccer replaced 2026-08-12: same ESPN bot-block as above.
    ("BBC Football", "http://feeds.bbci.co.uk/sport/football/rss.xml"),

    # --- General / world ---
    ("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml"),
    ("NPR News", "https://feeds.npr.org/1001/rss.xml"),
]


# ---------------------------------------------------------------------------
# 2. NEWSAPI KEYWORDS (optional layer)
# ---------------------------------------------------------------------------
# NewsAPI lets you pull keyword-based headlines on top of the RSS feeds.
# Free tier = 100 requests/day, so keep this list short. Each keyword = 1
# request per run. Leave the list empty ([]) to skip NewsAPI entirely and
# run on RSS alone (fully free, no key needed).
# ---------------------------------------------------------------------------

# NewsAPI keyword layer — DISABLED. The key was returning 401 (invalid/not set),
# and the RSS feeds provide plenty of material. To re-enable: add a valid
# NEWSAPI_KEY repo secret and put keywords back in this list (keep it short —
# each keyword is 1 of 100 free daily requests).
NEWSAPI_KEYWORDS = []


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
- NFL: the same THINKING side — scheme and play-design breakdowns, salary cap
  and contract strategy, roster construction, draft analysis. Score analytical/
  strategic pieces high; score rumor-mill churn and pure highlights low.
- Faith: Reformed/Presbyterian theology and culture (The Gospel Coalition,
  Desiring God, Ligonier). Score substantive theology and thoughtful cultural
  commentary high; score surface devotional filler and prosperity-gospel low.
- Sports: volleyball especially, plus fantasy football (lineup/start-sit/waiver
  strategy) and general sports.
- Tech/AI: predictive modeling, applied ML, and forecasting — especially applied
  to sports or real decisions. Also Apple (products, the company), Anthropic and
  the broader LLM/AI race (Claude, frontier models), and sharp consumer-tech
  reviews and analysis (MKBHD-style). Score thoughtful analysis high, rumor-mill
  churn lower.
- Music: album reviews and music criticism (Pitchfork), jazz, and film scores.
- World Cup 2026: results, storylines, tactical breakdowns.
- World: substantive geopolitics, economics, and policy an informed person
  should track — elections, wars, central bank moves, major diplomacy, science
  breakthroughs. Score explanatory/analytical pieces high. Score anything
  built to shock rather than inform — palace-intrigue, "secretly escaped",
  security-scare, and other tabloid-style political theater — LOW even if it's
  about a major figure or from a reputable outlet. The test: would this still
  matter in a week, or is it just a dramatic headline?

Always score as noise (low relevance): celebrity gossip, clickbait,
marketing/advertising industry news, prosperity gospel, opinion ragebait, and
sensationalized "you won't believe" framing regardless of category.
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
    "NBA":     4,
    "NFL":     4,
    "Faith":   7,
    "Sports":  3,
    "Tech/AI": 3,
    "Music":   2,
    "World":   1,
    "Other":   1,
}

# How many raw headlines to triage per run. The 8b model on Groq's free tier
# has a 6,000 tokens-per-minute limit. Each headline is ~20 tokens, plus ~500
# for the system prompt and interest profile, so the safe ceiling is ~50-55
# headlines per triage call. Set to 50 to stay comfortably under.
MAX_HEADLINES_TO_AI = 75

# Only consider articles published within this many hours (keeps it fresh).
# Widen this if you aren't consistently filling 50 stories.
FRESHNESS_HOURS = 24

# Primary model. The fallback chain in summarizer.py automatically waterfalls
# to Groq 8b, Groq legacy, Gemini, Cerebras, and Together if this hits limits.
GROQ_MODEL = "llama-3.3-70b-versatile"
