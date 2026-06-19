# The Anderson Wire 🛰️

Your own personal, self-updating, AI-filtered news app. Completely free to run.

It pulls headlines from RSS feeds + (optionally) NewsAPI, sends them to a free
AI model (Groq's Llama 3.3) along with your interest profile, and the AI hands
back only the stories *you'd* actually care about — ranked and summarized. A
GitHub Action runs it on a schedule, and GitHub Pages serves a clean reading
page you can bookmark.

**Total cost: $0.** No credit card required anywhere.

---

## How it works

```
GitHub Actions (cron, hourly)
  → main.py
      → fetcher.py     pulls RSS + NewsAPI, drops stale/duplicate items
      → summarizer.py  Groq (Llama 3.3) filters + summarizes against YOUR profile
  → writes docs/output.json
  → commits it back to the repo
GitHub Pages serves docs/  →  index.html reads output.json  →  you read your wire
```

The only thing you ever need to edit to tune it is **`config.py`** — your feeds
and your interest profile live there.

---

## One-time setup (~15 minutes)

### Step 1 — Get your free API keys

**Groq (required — this is the AI):**
1. Go to https://console.groq.com and sign up (free, no card).
2. Open **API Keys** → **Create API Key**. Copy it somewhere safe.

**NewsAPI (optional — extra keyword headlines):**
1. Go to https://newsapi.org/register and sign up (free, no card).
2. Copy your API key.
3. *You can skip this entirely.* If you do, leave `NEWSAPI_KEYWORDS = []` in
   `config.py` and the app runs on RSS feeds alone — still fully functional.

### Step 2 — Put this code in a GitHub repo

1. Create a new repository on GitHub (public is simplest for free Pages).
2. Upload all these files (keep the folder structure — especially
   `.github/workflows/update.yml` and the `docs/` folder).

### Step 3 — Add your keys as repository secrets

In your repo: **Settings → Secrets and variables → Actions → New repository secret**

- Name: `GROQ_API_KEY`  → Value: your Groq key
- Name: `NEWSAPI_KEY`   → Value: your NewsAPI key *(skip if not using NewsAPI)*

Secrets are encrypted and never visible in the code or logs.

### Step 4 — Turn on GitHub Pages

**Settings → Pages → Build and deployment**
- Source: **Deploy from a branch**
- Branch: **main**, folder: **/docs**
- Save.

After a minute, your wire is live at:
`https://<your-username>.github.io/<your-repo-name>/`

Bookmark that. That's your news app.

### Step 5 — Trigger the first run

Scheduled runs only start on the next hour, so kick off the first one yourself:

**Actions tab → "Update Newswire" → Run workflow**

Watch it run (~30s). When it finishes, refresh your Pages URL — real stories
replace the placeholder samples.

---

## Tuning it (this is the fun part)

Everything lives in **`config.py`**:

- **`RSS_FEEDS`** — add/remove sources. More feeds = more raw material for the
  AI to choose from. To find a feed, try `<site>/feed` or `<site>/rss`, or
  search "*site name* rss". Reddit feeds are just `<subreddit-url>/.rss`.
- **`INTEREST_PROFILE`** — the heart of it. Rewrite this in your own words. The
  more specific you are, the sharper the filtering. ("NBA lineup construction
  and advanced stats" beats "basketball".)
- **`NEWSAPI_KEYWORDS`** — short list of keyword searches (each = 1 of your 100
  free daily NewsAPI requests). Leave empty to skip.
- **`MAX_STORIES`** — how many stories per digest (default 10).
- **`GROQ_MODEL`** — defaults to `llama-3.3-70b-versatile`. If you ever hit rate
  limits, switch to `llama-3.1-8b-instant`.

### Update frequency

In `.github/workflows/update.yml`, the line `cron: "0 * * * *"` means hourly.
Change to `"*/30 * * * *"` for ~30 min. Note: GitHub sometimes delays scheduled
runs under load on the free tier, so hourly is the reliable sweet spot. The page
itself also re-checks for a fresh digest every 5 minutes while open.

---

## Run it locally (optional, for testing)

```bash
pip install -r requirements.txt
export GROQ_API_KEY="your-key-here"
export NEWSAPI_KEY="your-key-here"   # optional
python main.py
```

Then open `docs/index.html` **via a local server** (not by double-clicking —
browsers block `fetch()` of local files over `file://`):

```bash
cd docs && python -m http.server 8000
# open http://localhost:8000
```

---

## Free-tier reality check

- **Groq:** generous free limits — hourly runs of ~70 headlines won't come close
  to hitting them.
- **NewsAPI:** 100 requests/day free. Each keyword = 1 request per run. 3 keywords
  hourly = 72/day. Stay under 4 keywords if running hourly, or drop NewsAPI.
- **GitHub Actions:** 2,000 free minutes/month for private repos, unlimited for
  public. Each run is well under a minute.
- **GitHub Pages:** free.

You're comfortably inside every free tier.

---

## Files

| File | What it does |
|------|--------------|
| `config.py` | **Your** feeds + interest profile. The one file you edit. |
| `fetcher.py` | Pulls and cleans RSS + NewsAPI articles. |
| `summarizer.py` | Sends headlines to Groq, gets back your ranked digest. |
| `main.py` | Runs the whole pipeline, writes `docs/output.json`. |
| `requirements.txt` | Python dependencies. |
| `.github/workflows/update.yml` | The hourly cron job. |
| `docs/index.html` | The reading page (your "app"). |
| `docs/output.json` | The current digest (regenerated each run). |
