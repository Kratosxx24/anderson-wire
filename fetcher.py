"""
fetcher.py — pulls raw headlines from RSS feeds and (optionally) NewsAPI,
normalizes them into a common shape, drops stale and duplicate items.
"""

import os
import time
import html
import urllib.request
import json
from datetime import datetime, timezone, timedelta

import feedparser

import config


def _strip_html(text: str) -> str:
    """Crude tag stripper for RSS summaries — keeps prompts clean."""
    if not text:
        return ""
    out, in_tag = [], False
    for ch in text:
        if ch == "<":
            in_tag = True
        elif ch == ">":
            in_tag = False
        elif not in_tag:
            out.append(ch)
    return html.unescape("".join(out)).strip()


def _entry_time(entry) -> datetime | None:
    """Best-effort published time as a tz-aware UTC datetime."""
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            return datetime(*t[:6], tzinfo=timezone.utc)
    return None


def fetch_rss() -> list[dict]:
    """Pull every configured RSS feed. Network errors on one feed never
    kill the run — we just skip it and move on."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=config.FRESHNESS_HOURS)
    articles = []

    for label, url in config.RSS_FEEDS:
        try:
            parsed = feedparser.parse(url)
        except Exception as e:
            print(f"  ! {label}: failed to parse ({e})")
            continue

        if parsed.bozo and not parsed.entries:
            print(f"  ! {label}: no entries (feed may be down)")
            continue

        kept = 0
        for entry in parsed.entries:
            published = _entry_time(entry)
            if published and published < cutoff:
                continue  # too old
            articles.append({
                "title": _strip_html(entry.get("title", "")).strip(),
                "summary": _strip_html(entry.get("summary", ""))[:500],
                "url": entry.get("link", ""),
                "source": label,
                "published": published.isoformat() if published else None,
            })
            kept += 1
        print(f"  - {label}: {kept} fresh")

    return articles


def fetch_newsapi() -> list[dict]:
    """Optional keyword layer. Skipped entirely if no key or no keywords."""
    api_key = os.environ.get("NEWSAPI_KEY")
    if not api_key or not config.NEWSAPI_KEYWORDS:
        if config.NEWSAPI_KEYWORDS and not api_key:
            print("  ! NEWSAPI_KEY not set — skipping NewsAPI layer")
        return []

    cutoff = (datetime.now(timezone.utc)
              - timedelta(hours=config.FRESHNESS_HOURS)).strftime("%Y-%m-%dT%H:%M:%S")
    articles = []

    for kw in config.NEWSAPI_KEYWORDS:
        q = urllib.parse.quote(kw)
        endpoint = (
            f"https://newsapi.org/v2/everything?q={q}"
            f"&from={cutoff}&sortBy=publishedAt&language=en&pageSize=10"
            f"&apiKey={api_key}"
        )
        try:
            req = urllib.request.Request(endpoint, headers={"User-Agent": "newswire/1.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode())
        except Exception as e:
            print(f"  ! NewsAPI '{kw}': {e}")
            continue

        for a in data.get("articles", []):
            articles.append({
                "title": (a.get("title") or "").strip(),
                "summary": (a.get("description") or "")[:500],
                "url": a.get("url", ""),
                "source": f"NewsAPI:{kw}",
                "published": a.get("publishedAt"),
            })
        print(f"  - NewsAPI '{kw}': {len(data.get('articles', []))}")
        time.sleep(1)  # be gentle on the free tier

    return articles


def dedupe(articles: list[dict]) -> list[dict]:
    """Drop exact-URL and near-identical-title duplicates."""
    seen_urls, seen_titles, out = set(), set(), []
    for a in articles:
        url = a.get("url", "")
        title_key = a.get("title", "").lower().strip()[:80]
        if not a.get("title"):
            continue
        if url and url in seen_urls:
            continue
        if title_key and title_key in seen_titles:
            continue
        seen_urls.add(url)
        seen_titles.add(title_key)
        out.append(a)
    return out


def fetch_all() -> list[dict]:
    print("Fetching RSS feeds...")
    rss = fetch_rss()
    print("Fetching NewsAPI...")
    napi = fetch_newsapi()
    combined = dedupe(rss + napi)
    print(f"\nTotal fresh, de-duplicated articles: {len(combined)}")
    return combined
