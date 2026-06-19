"""
summarizer.py — sends raw headlines to Groq (free Llama 3.3) along with your
interest profile, and gets back a ranked, summarized digest of just the
stories worth your attention.
"""

import os
import json

from groq import Groq

import config


SYSTEM_PROMPT = """You are a sharp, no-nonsense personal news editor. You are \
given a reader's interest profile and a list of raw headlines pulled from RSS \
feeds and news APIs in the last day. Your job: pick ONLY the stories this \
specific reader would genuinely want, rank them by how much they'd care, and \
write a tight 2-sentence summary of each in a clear, direct voice.

Hard rules:
- Aim for a full digest. If there's enough relevant material, return close to \
the maximum requested rather than trimming aggressively — lean toward including \
a story when it's plausibly interesting to this reader. Only drop things that \
are clearly noise or clearly outside their interests.
- Each summary is your OWN words — never copy article text verbatim. Two \
sentences max. Lead with the substance, not "This article discusses...".
- Assign each story a category from this set: NBA, Sports, Tech/AI, Faith, \
Film, World, Other.
- Give each a relevance score 1-10 for THIS reader.
- Return STRICT JSON only. No markdown, no backticks, no preamble."""


def _build_user_prompt(articles: list[dict]) -> str:
    lines = []
    for i, a in enumerate(articles):
        src = a.get("source", "")
        title = a.get("title", "")
        summ = a.get("summary", "")
        lines.append(f"[{i}] ({src}) {title}\n    {summ}")
    headlines_block = "\n".join(lines)

    return f"""READER PROFILE:
{config.INTEREST_PROFILE}

RAW HEADLINES (each tagged with an index in brackets):
{headlines_block}

Return a JSON object with this exact shape:
{{
  "stories": [
    {{
      "index": <the [n] index of the source article>,
      "headline": "<a clean, punchy headline you write>",
      "summary": "<your 2-sentence summary>",
      "category": "<one of: NBA, Sports, Tech/AI, Faith, Film, World, Other>",
      "relevance": <1-10 integer>
    }}
  ]
}}

Include at most {config.MAX_STORIES} stories, ordered most-relevant first. \
Only include genuinely relevant stories."""


def summarize(articles: list[dict]) -> list[dict]:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Add it as a repo secret.")

    if not articles:
        print("No articles to summarize.")
        return []

    # Trim to the cap so the prompt stays a reasonable size.
    pool = articles[: config.MAX_HEADLINES_TO_AI]

    client = Groq(api_key=api_key)
    print(f"Asking Groq ({config.GROQ_MODEL}) to filter {len(pool)} headlines...")

    resp = client.chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(pool)},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    raw = resp.choices[0].message.content
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Defensive: strip stray fences if the model ever wraps the JSON.
        cleaned = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned)

    picked = data.get("stories", [])

    # Re-attach the real URL + source + published date from the original pool.
    enriched = []
    for s in picked:
        idx = s.get("index")
        if idx is None or not (0 <= idx < len(pool)):
            continue
        original = pool[idx]
        enriched.append({
            "headline": s.get("headline") or original.get("title", ""),
            "summary": s.get("summary", ""),
            "category": s.get("category", "Other"),
            "relevance": s.get("relevance", 5),
            "url": original.get("url", ""),
            "source": original.get("source", ""),
            "published": original.get("published"),
        })

    enriched.sort(key=lambda x: x.get("relevance", 0), reverse=True)
    print(f"Groq surfaced {len(enriched)} stories.")
    return enriched
