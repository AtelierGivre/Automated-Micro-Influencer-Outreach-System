"""Enrichment stage.

Fills the mandatory delivery fields for qualified profiles. Missing emails are
marked ``"Not Found"`` — never guessed — and optional audience data is marked
``"Not Available"`` when the source did not expose it.
"""

from __future__ import annotations

_MANDATORY = {
    "name": "Unknown Creator",
    "platform": "Unknown",
    "profile_url": "Not Available",
    "followers": 0,
    "engagement_rate": 0.0,
    "niche": "Unknown",
    "content_themes": "Not Available",
    "email": "Not Found",
}

_OPTIONAL = {
    "geography": "Not Available",
    "audience_age": "Not Available",
    "audience_gender": "Not Available",
}


def enrich(profile: dict) -> dict:
    """Return a copy with mandatory and optional fields present."""
    enriched = dict(profile)

    for field, fallback in _MANDATORY.items():
        value = enriched.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            enriched[field] = fallback

    # A blank email is the same as no email: never invent an address.
    if not str(enriched.get("email", "")).strip():
        enriched["email"] = "Not Found"
    enriched["email"] = str(enriched["email"]).strip()

    for field, fallback in _OPTIONAL.items():
        value = enriched.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            enriched[field] = fallback

    if not str(enriched.get("handle", "")).strip():
        enriched["handle"] = (
            str(enriched["name"]).lower().replace(" ", "") + "_creator"
        )

    if not str(enriched.get("profile_url", "")).strip():
        handle = str(enriched["handle"]).lstrip("@")
        enriched["profile_url"] = f"https://instagram.com/{handle}"

    enriched["enriched"] = True
    return enriched


def enrich_all(profiles: list[dict]) -> list[dict]:
    """Enrich every qualified profile. A bad row is isolated, not fatal."""
    enriched: list[dict] = []
    for profile in profiles:
        try:
            enriched.append(enrich(profile))
        except Exception as exc:  # noqa: BLE001 - keep the batch alive
            broken = dict(profile)
            broken["email"] = "Not Found"
            broken["enrichment_error"] = str(exc)
            enriched.append(broken)
    return enriched
