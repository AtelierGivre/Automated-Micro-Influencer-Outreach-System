"""Personalization stage.

Two messages per qualified influencer:

* email pitch, constrained to ``config.EMAIL_WORD_RANGE``
* Instagram DM, constrained to ``config.DM_WORD_RANGE``

If ``ANTHROPIC_API_KEY`` or ``OPENAI_API_KEY`` is set, a real model writes the
copy (Anthropic has priority, OpenAI is the fallback). Otherwise a randomized,
deterministic-per-profile template generator is used. Both paths enforce the
word limits and log the actual counts.
"""

from __future__ import annotations

import os
import random
import re

import config

_EMAIL_PADDING = [
    "Happy to share more details, rates, and past campaign results whenever works for you.",
    "If this is interesting, I can send a short brief and a couple of examples from similar creators.",
    "No pressure either way - just thought a direct note was better than another generic pitch.",
]

_DM_PADDING = [
    "Worth a quick chat?",
    "Open to it?",
    "Interested?",
    "Let me know?",
]

_EMAIL_OPENERS = [
    "Hi {first}, been going through your {theme} content on {platform} and really liked how you break things down.",
    "Hi {first}, loved your recent {theme} content - your {niche} audience is exactly who we're trying to reach.",
    "Hi {first}, your {theme} posts on {platform} stood out to me, especially how clearly you explain things.",
]

_EMAIL_BODY = [
    "At {brand}, we're {description}, and we're putting together a small group of {niche} creators for our upcoming launch.",
    "I'm reaching out from {brand} - {description} - because we're building out a creator program and think there's a natural fit here.",
]

_EMAIL_CTA = [
    "We'd love to explore {article} {angle} together if that's something you're taking on right now.",
    "If you're open to it, we'd like to set up {article} {angle} - happy to share more details on your side.",
    "Would you be open to {article} {angle}? I can send over the brief and rates.",
]

_DM_OPENERS = [
    "Hi {first}! Loved your {theme} content",
    "Hi {first} - big fan of your {theme} content!",
    "Hey {first}, your {theme} posts are great",
]

_DM_BODY = [
    "your {niche} audience would be a great fit for a {brand} collab.",
    "think you'd be a great match for a {brand} partnership.",
    "we're looking for {niche} creators for a {brand} campaign and you came to mind.",
]


def _first_name(name: str) -> str:
    return str(name).split()[0] if str(name).strip() else "there"


def _article(word: str) -> str:
    """'a affiliate campaign' -> 'an affiliate campaign'."""
    return "an" if str(word).strip()[:1].lower() in "aeiou" else "a"


def _word_count(text: str) -> int:
    return len(str(text).split())


def _fit_word_range(text: str, low: int, high: int) -> str:
    """Guarantee the word count is inside ``[low, high]``.

    Padding sentences are appended first. If the result is still too long, whole
    trailing sentences are dropped, then the final fallback trims words. This is
    what makes the logged ``*_word_count`` values trustworthy.
    """
    text = re.sub(r"\s+", " ", str(text)).strip()
    if not text:
        text = "Hello, I would like to discuss a potential collaboration."

    padding = _EMAIL_PADDING if high > 40 else _DM_PADDING
    guard = 0
    while _word_count(text) < low and guard < 20:
        text = f"{text} {padding[guard % len(padding)]}".strip()
        guard += 1

    if _word_count(text) > high:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        while len(sentences) > 1 and _word_count(" ".join(sentences)) > high:
            sentences.pop()
        text = " ".join(sentences).strip()

    if _word_count(text) > high:
        words = text.split()[:high]
        text = " ".join(words).rstrip(",;:-") + "."

    if _word_count(text) < low:
        # Extremely defensive: keep appending until the floor is met.
        while _word_count(text) < low:
            text = f"{text} Thanks."

    return text


def _template_email(profile: dict, rng: random.Random) -> str:
    angle = rng.choice(config.COLLAB_ANGLES)
    text = " ".join(
        [
            rng.choice(_EMAIL_OPENERS).format(
                first=_first_name(profile.get("name", "")),
                theme=profile.get("content_themes", "your"),
                platform=profile.get("platform", "social"),
                niche=profile.get("niche", "creator"),
            ),
            rng.choice(_EMAIL_BODY).format(
                brand=config.BRAND_NAME,
                description=config.BRAND_DESCRIPTION,
                niche=profile.get("niche", "creator"),
            ),
            rng.choice(_EMAIL_CTA).format(angle=angle, article=_article(angle)),
        ]
    )
    # Vary the middle sentence so two profiles with identical inputs still differ.
    if rng.random() < 0.5:
        text += f" Your {profile.get('followers', 0):,} followers and {profile.get('engagement_rate', 0)}% engagement are a strong signal."
    return _fit_word_range(text, *config.EMAIL_WORD_RANGE)


def _template_dm(profile: dict, rng: random.Random) -> str:
    opener = rng.choice(_DM_OPENERS).format(
        first=_first_name(profile.get("name", "")),
        theme=profile.get("content_themes", "your"),
    ).rstrip("!.- ")
    body = rng.choice(_DM_BODY).format(
        niche=profile.get("niche", "creator"),
        brand=config.BRAND_NAME,
    )
    return _fit_word_range(f"{opener} - {body}", *config.DM_WORD_RANGE)


def _system_prompt(kind: str, low: int, high: int) -> str:
    label = "email pitch" if kind == "email" else "Instagram DM"
    return (
        f"You write a short {label} for a brand partnership outreach. "
        f"Hard constraints: {low}-{high} words, warm but not pushy, no generic filler, "
        f"reference the creator's real niche and content theme, name one real collaboration "
        f"type from the brand's list, and output ONLY the message body with no preamble, "
        f"subject line, markdown, or quotation marks."
    )


def _user_prompt(profile: dict, kind: str) -> str:
    return (
        f"Brand: {config.BRAND_NAME} - {config.BRAND_DESCRIPTION}\n"
        f"Collaboration types: {', '.join(config.COLLAB_ANGLES)}\n"
        f"Creator: {profile.get('name', 'Unknown')} (@{profile.get('handle', 'unknown')})\n"
        f"Platform: {profile.get('platform', 'Unknown')}\n"
        f"Niche: {profile.get('niche', 'Unknown')}\n"
        f"Content theme: {profile.get('content_themes', 'Unknown')}\n"
        f"Followers: {profile.get('followers', 0)}\n"
        f"Engagement rate: {profile.get('engagement_rate', 0)}%\n"
        f"Write the {'email' if kind == 'email' else 'DM'} now."
    )


def _retrying_call(call, attempts: int = 3):
    last_error: Exception | None = None
    for _ in range(attempts):
        try:
            return call()
        except Exception as exc:  # noqa: BLE001 - retried, then surfaced
            last_error = exc
    raise RuntimeError(f"LLM generation failed after {attempts} attempts: {last_error}")


def _call_anthropic(prompt: str, system: str) -> str:
    from anthropic import Anthropic

    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=400,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if hasattr(block, "text")).strip()


def _call_openai(prompt: str, system: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=config.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        max_tokens=400,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return (response.choices[0].message.content or "").strip()


def _generate_llm_message(profile: dict, kind: str) -> str:
    low, high = config.EMAIL_WORD_RANGE if kind == "email" else config.DM_WORD_RANGE
    system = _system_prompt(kind, low, high)
    prompt = _user_prompt(profile, kind)

    if config.ANTHROPIC_API_KEY:
        text = _retrying_call(lambda: _call_anthropic(prompt, system))
    elif config.OPENAI_API_KEY:
        text = _retrying_call(lambda: _call_openai(prompt, system))
    else:
        raise NotImplementedError("No LLM key configured - see config.py")

    # The model may ignore the limit; enforce it rather than trusting it.
    return _fit_word_range(text, low, high)


def personalize(profile: dict, rng: random.Random | None = None) -> dict:
    """Attach ``email_pitch``, ``instagram_dm`` and their word counts."""
    rng = rng or random.Random(f"{profile.get('handle', '')}:{profile.get('platform', '')}")
    enriched = dict(profile)

    use_llm = bool(config.ANTHROPIC_API_KEY or config.OPENAI_API_KEY)
    if use_llm:
        try:
            email = _generate_llm_message(enriched, "email")
            dm = _generate_llm_message(enriched, "dm")
        except Exception:  # noqa: BLE001 - fall back to templates for this row
            email = _template_email(enriched, rng)
            dm = _template_dm(enriched, rng)
    else:
        email = _template_email(enriched, rng)
        dm = _template_dm(enriched, rng)

    enriched["email_pitch"] = email
    enriched["instagram_dm"] = dm
    enriched["email_word_count"] = _word_count(email)
    enriched["dm_word_count"] = _word_count(dm)
    return enriched


def personalize_all(profiles: list[dict]) -> list[dict]:
    """Personalize every profile; one failure cannot crash the batch."""
    output: list[dict] = []
    for profile in profiles:
        try:
            output.append(personalize(profile))
        except Exception as exc:  # noqa: BLE001
            broken = dict(profile)
            broken["email_pitch"] = f"[generation failed: {exc}]"
            broken["instagram_dm"] = f"[generation failed: {exc}]"
            broken["email_word_count"] = 0
            broken["dm_word_count"] = 0
            output.append(broken)
    return output


def llm_mode() -> str:
    return "LLM" if (config.ANTHROPIC_API_KEY or config.OPENAI_API_KEY) else "template fallback"


# Kept for callers that want to check the configured word limits.
def word_limits(kind: str) -> tuple[int, int]:
    return config.EMAIL_WORD_RANGE if kind == "email" else config.DM_WORD_RANGE


def _clear_env_cache() -> None:
    """Tests change env vars; config reads them at import time, so mirror that."""
    config.ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    config.OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
