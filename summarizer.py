"""
summarizer.py — two-pass AI pipeline with code-enforced category quotas
and a multi-provider fallback chain.

Provider waterfall (tried in order, automatic fallback on any rate-limit):
  1. Groq     — llama-3.3-70b-versatile  (best quality, 100k TPD free)
  2. Cerebras — llama-3.3-70b            (CEREBRAS_API_KEY, same weights, generous free)
  3. Gemini   — gemini-1.5-flash         (GEMINI_API_KEY, 1M tokens/day free)
  4. Groq     — llama3-70b-8192          (same key, older model, separate limit)
  5. Groq     — llama-3.1-8b-instant     (same key, last resort, ~500k TPD)

Any provider without a key set is skipped automatically. You only need to add
keys for providers you've signed up for — everything else keeps working.

Pass 1 (triage): AI categorizes + scores every headline (no summaries).
Selection:       code enforces per-category minimums, fills to MAX_STORIES.
Pass 2 (write):  AI writes headline + 2-sentence summary for selected stories.
"""

import os
import json
import time
from collections import Counter

from groq import Groq

import config

CATEGORIES = ["NBA", "Sports", "Tech/AI", "Faith", "Film", "Music", "World", "Other"]
SUMMARY_BATCH = 10
BATCH_SLEEP = 12   # seconds between summary batches to stay under TPM limits


# ---------------------------------------------------------------------------
# Multi-provider fallback engine
# ---------------------------------------------------------------------------

# Each provider entry: (name, key_env_var, call_fn)
# call_fn(messages, temperature, max_tokens, json_mode) -> str (raw JSON text)

def _groq_call(model: str, key: str):
    """Returns a call function for a specific Groq model."""
    def call(messages, temperature, max_tokens, json_mode):
        client = Groq(api_key=key)
        kwargs = dict(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        resp = client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content
    return call


def _gemini_call(key: str):
    """Call Google Gemini via its REST API (no extra package needed)."""
    import urllib.request
    def call(messages, temperature, max_tokens, json_mode):
        # Flatten messages to a single prompt for Gemini
        prompt = "\n\n".join(
            f"{'System' if m['role']=='system' else 'User'}: {m['content']}"
            for m in messages
        )
        if json_mode:
            prompt += "\n\nRespond with valid JSON only."
        body = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }).encode()
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"gemini-1.5-flash:generateContent?key={key}")
        req = urllib.request.Request(url, data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
        return data["candidates"][0]["content"]["parts"][0]["text"]
    return call


def _openai_compat_call(base_url: str, key: str, model: str):
    """OpenAI-compatible endpoint (Cerebras, Together, etc.)"""
    import urllib.request
    def call(messages, temperature, max_tokens, json_mode):
        body = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **({"response_format": {"type": "json_object"}} if json_mode else {}),
        }).encode()
        req = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=body,
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {key}"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
        return data["choices"][0]["message"]["content"]
    return call


def _build_provider_chain():
    """Build the list of available providers at runtime based on which keys exist.
    Ordered by output quality — best first, last-resort fallbacks last."""
    chain = []
    groq_key = os.environ.get("GROQ_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    cerebras_key = os.environ.get("CEREBRAS_API_KEY")

    # Tier 1 — llama-3.3-70b across multiple providers (same weights, best quality)
    if groq_key:
        chain.append(("Groq/llama-3.3-70b-versatile",
                       _groq_call("llama-3.3-70b-versatile", groq_key)))
    if cerebras_key:
        chain.append(("Cerebras/llama-3.3-70b",
                       _openai_compat_call(
                           "https://api.cerebras.ai/v1",
                           cerebras_key, "llama-3.3-70b")))

    # Tier 2 — Gemini Flash (different architecture, still very capable)
    if gemini_key:
        chain.append(("Gemini/gemini-1.5-flash", _gemini_call(gemini_key)))

    # Tier 3 — older/smaller Groq models (last resort, same key)
    if groq_key:
        chain.append(("Groq/llama3-70b-8192",
                       _groq_call("llama3-70b-8192", groq_key)))
        chain.append(("Groq/llama-3.1-8b-instant",
                       _groq_call("llama-3.1-8b-instant", groq_key)))

    if not chain:
        raise RuntimeError("No AI provider keys found. Set at least GROQ_API_KEY.")
    return chain


_RATE_LIMIT_CODES = {429, 413, 503}
_RATE_LIMIT_PHRASES = ("rate limit", "quota", "too large", "capacity", "overloaded")

def _is_rate_limit(e: Exception) -> bool:
    msg = str(e).lower()
    if hasattr(e, "status_code") and e.status_code in _RATE_LIMIT_CODES:
        return True
    if any(p in msg for p in _RATE_LIMIT_PHRASES):
        return True
    return False


def llm_complete(messages: list[dict], temperature: float = 0.2,
                 max_tokens: int = 4000, json_mode: bool = True) -> str:
    """Try each provider in the chain; fall through on rate limits."""
    chain = _build_provider_chain()
    last_err = None
    for name, call_fn in chain:
        try:
            result = call_fn(messages, temperature, max_tokens, json_mode)
            if chain[0][0] != name:   # only log if we actually fell back
                print(f"  ✓ using fallback provider: {name}")
            return result
        except Exception as e:
            if _is_rate_limit(e):
                print(f"  ! {name} rate-limited, trying next provider...")
                last_err = e
                continue
            raise   # non-rate-limit errors bubble up immediately
    raise RuntimeError(
        f"All providers exhausted. Last error: {last_err}"
    )


def _parse_json(raw: str) -> dict:
    """Strip markdown fences if a model wraps its JSON, then parse."""
    clean = raw.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(clean)


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
    lines = [f"[{i}] ({a.get('source','')}) {a.get('title','')}"
             for i, a in enumerate(pool)]

    user = f"""READER PROFILE:
{config.INTEREST_PROFILE}

HEADLINES:
{chr(10).join(lines)}

Return JSON with one entry for EVERY index from 0 to {len(pool)-1}:
{{"items": [{{"index": <int>, "category": "<one of: {', '.join(CATEGORIES)}>", "relevance": <1-10 integer>}}]}}

Rules: category must be exactly from the list; relevance is for THIS reader.
Return only the JSON."""

    raw = llm_complete(
        messages=[{"role": "system", "content": _TRIAGE_SYSTEM},
                  {"role": "user", "content": user}],
        temperature=0.2,
        max_tokens=4000,
        json_mode=True,
    )
    data = _parse_json(raw)

    out = []
    for it in data.get("items", []):
        idx = it.get("index")
        if not isinstance(idx, int) or not (0 <= idx < len(pool)):
            continue
        cat = it.get("category", "Other")
        if cat not in CATEGORIES:
            cat = "Other"
        try:
            rel = max(1, min(10, int(it.get("relevance", 5))))
        except (TypeError, ValueError):
            rel = 5
        out.append({"index": idx, "category": cat, "relevance": rel})
    return pool, out


# ---------------------------------------------------------------------------
# Selection: enforce category minimums, fill to MAX_STORIES by relevance
# ---------------------------------------------------------------------------

def select_with_quotas(triaged: list[dict]) -> list[dict]:
    mins = config.CATEGORY_MINIMUMS
    target = config.MAX_STORIES

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

    for cat, m in mins.items():
        for t in by_cat.get(cat, [])[:m]:
            if t["index"] not in chosen:
                selected.append(t)
                chosen.add(t["index"])

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
# Pass 2: write headline + summary for selected stories (batched)
# ---------------------------------------------------------------------------

_SUMMARY_SYSTEM = """You are a sharp, no-nonsense personal news editor. For each \
headline given, write a clean punchy headline and a tight 2-sentence summary in \
your OWN words — never copy article text verbatim. Lead with substance, not \
"This article discusses". Return STRICT JSON only — no markdown, no backticks."""


def _summarize_batch(pool: list[dict], batch: list[dict]) -> dict:
    lines = []
    for s in batch:
        a = pool[s["index"]]
        lines.append(
            f"[{s['index']}] ({a.get('source','')}) {a.get('title','')}\n"
            f"    {a.get('summary','')[:300]}"
        )
    user = (f"Write a headline and 2-sentence summary for each:\n"
            f"{chr(10).join(lines)}\n\n"
            f'Return JSON: {{"stories": [{{"index": <int>, "headline": "<headline>", "summary": "<two sentences>"}}]}}\n'
            f"Return only the JSON.")

    raw = llm_complete(
        messages=[{"role": "system", "content": _SUMMARY_SYSTEM},
                  {"role": "user", "content": user}],
        temperature=0.3,
        max_tokens=3000,
        json_mode=True,
    )
    data = _parse_json(raw)
    smap = {}
    for st in data.get("stories", []):
        idx = st.get("index")
        if isinstance(idx, int):
            smap[idx] = st
    return smap


def write_summaries(pool: list[dict], selected: list[dict]) -> list[dict]:
    smap = {}
    batches = [selected[i:i+SUMMARY_BATCH]
               for i in range(0, len(selected), SUMMARY_BATCH)]
    for n, batch in enumerate(batches, 1):
        print(f"  - summarizing batch {n}/{len(batches)} ({len(batch)} stories)")
        try:
            smap.update(_summarize_batch(pool, batch))
        except Exception as e:
            print(f"    ! batch {n} failed ({e}); using raw titles")
        if n < len(batches):
            time.sleep(BATCH_SLEEP)

    final = []
    for s in selected:
        a = pool[s["index"]]
        st = smap.get(s["index"], {})
        final.append({
            "headline": st.get("headline") or a.get("title", ""),
            "summary":  st.get("summary", ""),
            "category": s["category"],
            "relevance": s["relevance"],
            "url":      a.get("url", ""),
            "source":   a.get("source", ""),
            "published": a.get("published"),
        })
    return final


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def summarize(articles: list[dict]) -> list[dict]:
    if not articles:
        print("No articles to summarize.")
        return []

    n = min(len(articles), config.MAX_HEADLINES_TO_AI)
    print(f"Triaging {n} headlines (chain: Groq-70b → Cerebras-70b → "
          f"Gemini-Flash → Groq-legacy → Groq-8b)...")
    pool, triaged = triage(articles)
    print(f"  - categorized {len(triaged)} headlines")

    selected = select_with_quotas(triaged)
    spread = dict(Counter(s["category"] for s in selected))
    print(f"Selected {len(selected)}/{config.MAX_STORIES} after quotas: {spread}")

    print("Writing summaries...")
    final = write_summaries(pool, selected)
    print(f"Final stories: {len(final)}")
    return final
