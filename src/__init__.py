"""Core pipeline modules for the micro-influencer outreach prototype.

Discovery -> Filter/Classify -> Enrich -> Personalize -> Send -> Track.
Only the discovery source is mocked; every other stage runs real logic.
"""

__all__ = [
    "discovery",
    "filter_classify",
    "enrich",
    "personalize",
    "sending",
    "db",
]
