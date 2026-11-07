"""Discovery stage.

Live Instagram/YouTube/TikTok APIs need developer credentials, so this module
ships in a documented mock mode: it generates profiles with the same shape a
real search would return. Set ``config.MOCK_DISCOVERY = False`` and implement
``fetch_from_youtube`` / ``fetch_from_instagram`` / ``fetch_from_tiktok`` to go
live; the rest of the pipeline is unchanged.
"""

from __future__ import annotations

import csv
import os
import random

import config

# Relative search volume per niche. The target niche is intentionally
# over-represented (45%) so filtering has a meaningful pool to work with,
# while the remaining 55% still models off-topic search noise.
_NICHE_WEIGHTS = {
    "Fitness": 0.45,
    "Beauty": 0.1375,
    "Fintech": 0.1375,
    "Gaming": 0.1375,
    "Technology": 0.1375,
}

_CONTENT_THEMES = {
    "Fitness": [
        "strength training",
        "running/cardio",
        "home workouts",
        "mobility & stretching",
        "nutrition & meal prep",
        "yoga",
    ],
    "Beauty": ["skincare routines", "makeup tutorials", "clean beauty", "hair care"],
    "Fintech": ["personal finance", "investing basics", "credit & budgeting", "side hustles"],
    "Gaming": ["FPS gameplay", "indie reviews", "stream highlights", "esports commentary"],
    "Technology": ["gadget reviews", "coding tutorials", "AI tools", "productivity setups"],
}

_PLATFORM_URLS = {
    "Instagram": "https://instagram.com/{handle}",
    "YouTube": "https://youtube.com/@{handle}",
    "TikTok": "https://tiktok.com/@{handle}",
}

_FIRST_NAMES = [
    "Aarav", "Aditi", "Alex", "Ananya", "Arjun", "Dev", "Diya", "Ethan",
    "Ishita", "Jordan", "Kabir", "Karan", "Meera", "Mia", "Nikhil", "Pooja",
    "Priya", "Riya", "Rohan", "Sam", "Sameer", "Sana", "Tara", "Vivaan",
]

_AUDIENCE_AGES = ["18-24", "25-34", "25-34", "18-24", "35-44"]
_AUDIENCE_GENDERS = ["Mixed", "Mixed", "Female", "Male"]
_GEOGRAPHIES = ["India", "India", "United States", "United Kingdom", "UAE", "Canada"]


def _niche_weights() -> dict[str, float]:
    """Exposed for tests and for swapping in a real keyword-weight table."""
    return dict(_NICHE_WEIGHTS)


def _choose_niche(rng: random.Random) -> str:
    niches = list(_NICHE_WEIGHTS)
    return rng.choices(niches, weights=[_NICHE_WEIGHTS[n] for n in niches], k=1)[0]


def _followers_for(rng: random.Random, niche: str) -> int:
    """Three deliberate buckets: below, inside, and above the target range.

    Fitness profiles are more likely to land inside the configured range, which
    is what a keyword search for a fitness campaign would realistically return.
    """
    in_range = 0.72 if niche == config.TARGET_NICHE else 0.42
    roll = rng.random()
    if roll < in_range:
        return rng.randint(config.MIN_FOLLOWERS, config.MAX_FOLLOWERS)
    if roll < in_range + (1 - in_range) / 2:
        return rng.randint(500, config.MIN_FOLLOWERS - 1)
    return rng.randint(config.MAX_FOLLOWERS + 1, 250_000)


def _engagement_for(rng: random.Random, followers: int) -> float:
    """Engagement trends down as follower count rises, like real creator data."""
    if followers < config.MIN_FOLLOWERS:
        base = rng.uniform(4.2, 8.5)
    elif followers <= config.MAX_FOLLOWERS:
        base = rng.uniform(2.1, 6.8)
    else:
        base = rng.uniform(0.9, 3.4)
    return round(base, 2)


def _make_email(rng: random.Random, handle: str) -> str:
    # 24% of profiles have no public email on file. Never guess one.
    if rng.random() < 0.24:
        return "Not Found"
    domains = ["gmail.com", "outlook.com", "creatoremail.com"]
    suffixes = ["", "72", "88", "32", "58", "4", "17", "45"]
    return f"{handle}{rng.choice(suffixes)}@{rng.choice(domains)}"


def _make_profile(rng: random.Random, index: int) -> dict:
    niche = _choose_niche(rng)
    platform = rng.choice(config.ALLOWED_PLATFORMS)
    first = rng.choice(_FIRST_NAMES)
    last = "Fit" if niche == config.TARGET_NICHE else "Creates"
    name = f"{first} {last}"
    handle = f"{first.lower()}{last.lower()}{index}"
    followers = _followers_for(rng, niche)
    theme = rng.choice(_CONTENT_THEMES[niche])
    has_demographics = rng.random() < 0.62

    return {
        "name": name,
        "handle": handle,
        "platform": platform,
        "followers": followers,
        "engagement_rate": _engagement_for(rng, followers),
        "niche": niche,
        "content_themes": theme,
        "email": _make_email(rng, handle),
        "profile_url": _PLATFORM_URLS[platform].format(handle=handle),
        "geography": rng.choice(_GEOGRAPHIES) if has_demographics else "Not Available",
        "audience_age": rng.choice(_AUDIENCE_AGES) if has_demographics else "Not Available",
        "audience_gender": rng.choice(_AUDIENCE_GENDERS) if has_demographics else "Not Available",
        "discovered_via": "mock keyword search",
    }


def _mock_discover() -> list[dict]:
    # Seeded so demo runs and screenshots are reproducible.
    rng = random.Random(getattr(config, "DISCOVERY_SEED", 20240517))
    return [_make_profile(rng, i) for i in range(config.NUM_DISCOVERED)]


def fetch_from_youtube(*_args, **_kwargs):
    raise NotImplementedError(
        "YouTube discovery is not wired up. Add a YouTube Data API v3 search call "
        "here, map each item into the profile dict shape used by _make_profile(), "
        "and set config.MOCK_DISCOVERY = False."
    )


def fetch_from_instagram(*_args, **_kwargs):
    raise NotImplementedError(
        "Instagram discovery is not wired up. Add an Instagram Graph API business "
        "discovery call here, map results into the profile dict shape, and set "
        "config.MOCK_DISCOVERY = False."
    )


def fetch_from_tiktok(*_args, **_kwargs):
    raise NotImplementedError(
        "TikTok discovery is not wired up. Add a TikTok Research API call here, "
        "map results into the profile dict shape, and set config.MOCK_DISCOVERY = False."
    )


def discover() -> list[dict]:
    """Return discovered profiles. Mock mode is the default and is labelled."""
    if config.MOCK_DISCOVERY:
        return _mock_discover()

    live = []
    for fetcher in (fetch_from_instagram, fetch_from_youtube, fetch_from_tiktok):
        try:
            live.extend(fetcher())
        except NotImplementedError:
            # A platform without credentials simply contributes nothing.
            continue
    return live


def save_raw(rows: list[dict]) -> None:
    """Write the pre-filter discovery output to ``config.RAW_PATH``."""
    os.makedirs(os.path.dirname(config.RAW_PATH), exist_ok=True)
    fields = [
        "name", "handle", "platform", "followers", "engagement_rate", "niche",
        "content_themes", "email", "profile_url", "geography", "audience_age",
        "audience_gender", "discovered_via",
    ]
    with open(config.RAW_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
