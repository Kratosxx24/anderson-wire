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


def main():
    print("=" * 60)
    print(f"NEWSWIRE RUN — {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    articles = fetcher.fetch_all()
    stories = summarizer.summarize(articles)

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
