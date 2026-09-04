"""
Central config for the outreach pipeline.
Change these values to target a different niche / brand without touching pipeline code.
"""

import os

# Loads a local .env file if present (never committed - see .gitignore).
# This is how you'd set ANTHROPIC_API_KEY/OPENAI_API_KEY locally without
# ever putting a real key in a file that goes to GitHub. If python-dotenv
# isn't installed, this just no-ops and falls back to real env vars only.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---- Brand / campaign context (used for personalization prompts) ----
BRAND_NAME = "Voltura Fit"
BRAND_DESCRIPTION = "a DTC fitness apparel and supplement brand launching a new activewear line"
COLLAB_ANGLES = [
    "sponsored post",
    "affiliate campaign (commission on sales via unique code)",
    "UGC content creation",
    "barter collaboration (free product in exchange for content)",
]

# ---- Discovery ----
# We don't have live Instagram/YouTube/TikTok API access in this environment
# (no API keys, and platform scraping is blocked by ToS for automated access
# without a registered developer app). MOCK_DISCOVERY=True generates a
# realistic dataset with the same shape live scraping would return, so the
# rest of the pipeline (filter -> enrich -> personalize -> send -> track) is
# fully real and testable. See README "Limitations" for how to swap this
# out for real Instagram Graph API / YouTube Data API calls.
MOCK_DISCOVERY = True
NUM_DISCOVERED = 110  # oversample since not every discovered profile matches
# the target niche/follower/engagement range - 110 discovered, with
# discovery weighted toward the target niche (see discovery._niche_weights),
# lands a qualified set large enough to actually demonstrate filtering and
# personalization at a meaningful scale instead of a handful of rows

# ---- Filtering (chosen niche for the required filter category) ----
TARGET_NICHE = "Fitness"
MIN_FOLLOWERS = 5000
MAX_FOLLOWERS = 100000
MIN_ENGAGEMENT_RATE = 2.0  # percent
ALLOWED_PLATFORMS = ["Instagram", "YouTube", "TikTok"]

# ---- Personalization ----
# If set, personalize.py will call a real LLM. Otherwise it falls back to
# a rule-based generator that still varies per-influencer (see src/personalize.py).
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

EMAIL_WORD_RANGE = (60, 90)
DM_WORD_RANGE = (15, 30)

# ---- Sending ----
DRY_RUN = True  # True = simulate sending, log everything, no real emails go out
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
FROM_ADDRESS = os.environ.get("FROM_ADDRESS", "partnerships@volturafit.com")

# ---- Paths ----
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
RAW_PATH = os.path.join(DATA_DIR, "influencers_raw.csv")
QUALIFIED_PATH = os.path.join(DATA_DIR, "influencers_qualified.csv")
FULL_DATASET_PATH = os.path.join(DATA_DIR, "influencer_dataset.csv")
TRACKER_PATH = os.path.join(DATA_DIR, "outreach_tracker.csv")
LOG_PATH = os.path.join(DATA_DIR, "outreach_log.json")
