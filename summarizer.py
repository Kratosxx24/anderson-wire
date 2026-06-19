"""
summarizer.py — two-pass AI pipeline with code-enforced category quotas.

Pass 1 (triage): the AI categorizes and scores EVERY headline (cheap, no
                 summaries written).
Selection:       code picks stories to satisfy per-category minimums, then
                 fills remaining slots by overall relevance, capped at MAX_STORIES.
Pass 2 (write):  the AI writes a headline + 2-sentence summary for only the
                 selected stories (done in small batches to stay light).

This guarantees the minimums in config.CATEGORY_MINIMUMS whenever enough
relevant articles exist, instead of hoping the model self-balances.
"""

import os
import json
from collections import Counter

from groq import Groq

import config

CATEGORIES = ["NBA", "Sports", "Tech/AI", "Faith", "Film", "Music", "World", "Other"]
SUMMARY_BATCH = 20   # how many summaries to request per call (keeps responses small)


def _client() -> Groq:
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is not set. Add it as a repo secret.")
    return Groq(api_key=key)


# ---------------------------------------------------------------------------
# Pass 1: triage — categorize + score every headline
# ---------------------------------------------------------------------------

_TRIAGE_SYSTEM = """You are a fast, sharp news triage assistant. You are given a \
reader's interest profile and a numbered list of raw headlines. For EVERY \
headline, decide its single best category and a relevance score from 1-10 for \
THIS specific reader. Do not write summaries. Be decisive. Return STRICT JSON \
only — no markdown, no backticks, no commentary."""


def triage(articles: list[dict]):
    pool = articles[: config.MAX_HEADLINES_TO_AI]
    lines = [f"[{i}] ({a.get('source','')}) {a.get('title','')}" for i, a in enumerate(pool)]

    user = f"""READER PROFILE:
{config.INTEREST_PROFILE}

HEADLINES:
{chr(10).join(lines)}

Return JSON of this exact shape, with one entry for EVERY index from 0 to {len(pool)-1}:
{{"items": [{{"index": <int>, "category": "<one of: {', '.join(CATEGORIES)}>", "relevance": <1-10 integer>}}]}}

Rules: category must be from the list; relevance is how relevant to THIS reader.
Return only the JSON."""

    resp = _client().chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "system", "content": _TRIAGE_SYSTEM},
                  {"role": "user", "content": user}],
        temperature=0.2,
        max_tokens=8000,
        response_format={"type": "json_object"},
    )
    data = json.loads(resp.choices[0].message.content)

    out = []
    for it in data.get("items", []):
        idx = it.get("index")
        if not isinstance(idx, int) or not (0 <= idx < len(pool)):
            continue
        cat = it.get("category", "Other")
        if cat not in CATEGORIES:
            cat = "Other"
        try:
            rel = int(it.get("relevance", 5))
        except (TypeError, ValueError):
            rel = 5
        rel = max(1, min(10, rel))
        out.append({"index": idx, "category": cat, "relevance": rel})
    return pool, out


# ---------------------------------------------------------------------------
# Selection: enforce minimums, then fill by relevance, cap at MAX_STORIES
# ---------------------------------------------------------------------------

def select_with_quotas(triaged: list[dict]) -> list[dict]:
    mins = config.CATEGORY_MINIMUMS
    target = config.MAX_STORIES

    # de-dupe by index, keep highest relevance per index
    best = {}
    for t in triaged:
        i = t["index"]
        if i not in best or t["relevance"] > best[i]["relevance"]:
            best[i] = t
    items = sorted(best.values(), key=lambda t: t["relevance"], reverse=True)

    by_cat: dict[str, list] = {}
    for t in items:
        by_cat.setdefault(t["category"], []).append(t)

    selected, chosen = [], set()

    # Phase 1 — satisfy each category's minimum (highest-relevance items first)
    for cat, m in mins.items():
        for t in by_cat.get(cat, [])[:m]:
            if t["index"] not in chosen:
                selected.append(t)
                chosen.add(t["index"])

    # Phase 2 — fill remaining slots with the best of what's left
    for t in items:
        if len(selected) >= target:
            break
        if t["index"] not in chosen:
            selected.append(t)
            chosen.add(t["index"])

    selected = selected[:target]
    selected.sort(key=lambda t: t["relevance"], reverse=True)
    return selected


# ---------------------------------------------------------------------------
# Pass 2: write headline + summary for the selected stories (batched)
# ---------------------------------------------------------------------------

_SUMMARY_SYSTEM = """You are a sharp, no-nonsense personal news editor. You are \
given a set of pre-selected headlines, each with an index. For each one, write a \
clean, punchy headline and a tight 2-sentence summary in your OWN words — never \
copy article text verbatim. Lead with substance, not "This article discusses". \
Return STRICT JSON only — no markdown, no backticks, no commentary."""


def _summarize_batch(pool: list[dict], batch: list[dict]) -> dict:
    lines = []
    for s in batch:
        a = pool[s["index"]]
        lines.append(f"[{s['index']}] ({a.get('source','')}) {a.get('title','')}\n    {a.get('summary','')[:400]}")

    user = f"""Write a headline and 2-sentence summary for each, keyed by index:
{chr(10).join(lines)}

Return JSON:
{{"stories": [{{"index": <int>, "headline": "<your headline>", "summary": "<two sentences>"}}]}}
Return only the JSON."""

    resp = _client().chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "system", "content": _SUMMARY_SYSTEM},
                  {"role": "user", "content": user}],
        temperature=0.3,
        max_tokens=6000,
        response_format={"type": "json_object"},
    )
    data = json.loads(resp.choices[0].message.content)
    smap = {}
    for st in data.get("stories", []):
        idx = st.get("index")
        if isinstance(idx, int):
            smap[idx] = st
    return smap


def write_summaries(pool: list[dict], selected: list[dict]) -> list[dict]:
    smap = {}
    for i in range(0, len(selected), SUMMARY_BATCH):
        batch = selected[i:i + SUMMARY_BATCH]
        print(f"  - summarizing batch {i // SUMMARY_BATCH + 1} ({len(batch)} stories)")
        try:
            smap.update(_summarize_batch(pool, batch))
        except Exception as e:
            print(f"    ! batch failed ({e}); falling back to raw titles for it")

    final = []
    for s in selected:
        a = pool[s["index"]]
        st = smap.get(s["index"], {})
        final.append({
            "headline": st.get("headline") or a.get("title", ""),
            "summary": st.get("summary", ""),
            "category": s["category"],
            "relevance": s["relevance"],
            "url": a.get("url", ""),
            "source": a.get("source", ""),
            "published": a.get("published"),
        })
    return final


# ---------------------------------------------------------------------------
# Orchestrator (public entry point — main.py calls this)
# ---------------------------------------------------------------------------

def summarize(articles: list[dict]) -> list[dict]:
    if not articles:
        print("No articles to summarize.")
        return []

    n = min(len(articles), config.MAX_HEADLINES_TO_AI)
    print(f"Triaging {n} headlines with Groq ({config.GROQ_MODEL})...")
    pool, triaged = triage(articles)
    print(f"  - categorized {len(triaged)} headlines")

    selected = select_with_quotas(triaged)
    spread = dict(Counter(s["category"] for s in selected))
    print(f"Selected {len(selected)}/{config.MAX_STORIES} after quotas: {spread}")

    print("Writing summaries...")
    final = write_summaries(pool, selected)
    print(f"Final stories: {len(final)}")
    return final
