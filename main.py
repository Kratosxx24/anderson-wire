"""
main.py — the orchestrator. Run this and it does the whole pipeline:
fetch -> filter/summarize via Groq -> write docs/output.json

The GitHub Action runs this on a schedule; you can also run it locally.
"""

import json
import os
from datetime import datetime, timezone

import fetcher
import summarizer

OUTPUT_PATH = os.path.join("docs", "output.json")


def _load_cache() -> dict:
    """Previous run's stories, keyed by URL. Lets summarize() skip AI calls
    for stories that are still selected this run (see summarizer.summarize)."""
    if not os.path.exists(OUTPUT_PATH):
        return {}
    try:
        with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}
    return {s["url"]: s for s in data.get("stories", []) if s.get("url")}


def main():
    print("=" * 60)
    print(f"NEWSWIRE RUN — {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    cache = _load_cache()
    articles = fetcher.fetch_all()
    stories = summarizer.summarize(articles, cache=cache)
    stories = fetcher.enrich_published_dates(stories)
    for s in stories:
        s.pop("_from_cache", None)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "story_count": len(stories),
        "stories": stories,
    }

    os.makedirs("docs", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {len(stories)} stories to {OUTPUT_PATH}")
    print("Done.")


if __name__ == "__main__":
    main()
