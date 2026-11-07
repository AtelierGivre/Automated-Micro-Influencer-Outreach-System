"""Filtering and classification.

The implemented filter category is the configured niche (Fitness by default).
Every record gets a pass/fail decision *and* a human-readable reason per failed
check, so the main dataset can explain itself row by row.
"""

from __future__ import annotations

import config

_REQUIRED = ("niche", "followers", "engagement_rate", "platform")


def _fmt_int(value) -> str:
    return f"{int(value):,}"


def evaluate(profile: dict) -> tuple[bool, list[str]]:
    """Return ``(passed, reasons)`` for one discovered profile.

    Raises ``KeyError`` / ``ValueError`` / ``TypeError`` for malformed records;
    ``main.py`` catches those, marks the row ``Error`` and keeps the batch going.
    """
    missing = [key for key in _REQUIRED if key not in profile]
    if missing:
        raise KeyError(f"missing field(s): {', '.join(missing)}")

    try:
        followers = int(profile["followers"])
        engagement = float(profile["engagement_rate"])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"non-numeric followers/engagement: {exc}") from exc

    if followers < 0 or engagement < 0:
        raise ValueError("followers and engagement_rate must be non-negative")

    reasons: list[str] = []

    niche = str(profile["niche"]).strip()
    if niche.lower() != config.TARGET_NICHE.lower():
        reasons.append(f"niche is '{niche}', not '{config.TARGET_NICHE}'")

    if not (config.MIN_FOLLOWERS <= followers <= config.MAX_FOLLOWERS):
        reasons.append(
            f"followers ({_fmt_int(followers)}) outside "
            f"{_fmt_int(config.MIN_FOLLOWERS)}-{_fmt_int(config.MAX_FOLLOWERS)} range"
        )

    if engagement < config.MIN_ENGAGEMENT_RATE:
        reasons.append(
            f"engagement rate {engagement:.2f}% below {config.MIN_ENGAGEMENT_RATE:.1f}%"
        )

    platform = str(profile["platform"]).strip()
    if platform not in config.ALLOWED_PLATFORMS:
        reasons.append(f"platform '{platform}' not in {config.ALLOWED_PLATFORMS}")

    return not reasons, reasons


def classify(profile: dict) -> dict:
    """Convenience wrapper that annotates a profile in place and returns it."""
    passed, reasons = evaluate(profile)
    profile["status"] = "Qualified" if passed else "Rejected"
    profile["filter_reason"] = "; ".join(reasons)
    return profile
