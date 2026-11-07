# Automated Micro-Influencer Outreach System — Mock Automation Prototype

An end-to-end Python automation pipeline that discovers influencer profiles, filters and qualifies them, enriches their information, generates personalized outreach messages, and tracks outreach attempts while preventing duplicate messaging.

Full pipeline: discover
influencers → filter/classify → enrich profiles → generate personalized
outreach copy → send (simulated) → track results, with dedup so nobody gets
messaged twice.

## Setup instructions

```bash
pip install -r requirements.txt   # optional - stdlib only unless you set an LLM key
python main.py
```

No API keys required to see the full workflow run end to end. Output lands in `data/`:

| File | What it is |
|---|---|
| `influencer_dataset.csv` | **The main deliverable** — all 110 discovered profiles, pass *and* fail, with `status` + `filter_reason` on every row. Matches the assignment's recommended format. |
| `influencers_raw.csv` | Raw discovery output, pre-filter |
| `influencers_qualified.csv` | Just the qualified profiles, enriched, with generated email + DM |
| `outreach_tracker.csv` | Send log — one row per attempt |
| `outreach_log.json` | Same as the tracker, plus full message text |
| `outreach.db` | Same data again, in SQLite |

To try the live LLM personalization path instead of the template fallback:
copy `.env.example` to `.env`, fill in `ANTHROPIC_API_KEY` (or
`OPENAI_API_KEY`), then run `python main.py` again. **`.env` is
gitignored** — it never gets pushed to GitHub, so there's no risk of a key
ending up in a public repo, and no key is needed for anyone cloning this to
run the pipeline and read the logic. Alternatively, `export
ANTHROPIC_API_KEY=sk-...` in your shell works the same way without a file
at all.

To send real emails instead of dry-run: set `config.DRY_RUN = False` and
provide `SMTP_USER` / `SMTP_PASSWORD` the same way (`.env` or env var).

See `DEMO.md` for a full captured run (a real terminal transcript, since
video/screenshots weren't possible in this sandboxed environment) and
`automation_workflow.n8n.json` for the no-code automation version.

Run the offline test suite (no API keys, no network):

```bash
python -m pytest -q     # 15 tests
```

## Technology stack

- **Python 3**, mostly standard library (`csv`, `sqlite3`, `smtplib`, `json`, `ssl`) — no dependency wall to get the core pipeline running
- **Anthropic API** (`anthropic` SDK) for LLM-based personalization
- **SQLite** for structured, queryable storage alongside the CSV exports
- **n8n** — reference workflow for the no-code automation angle

## APIs / tools used

- **Anthropic Messages API** (primary) and **OpenAI Chat Completions API** (automatic fallback if only `OPENAI_API_KEY` is set) — real integration in `src/personalize.py` (see "AI model / prompt used" below)
- **SMTP** (`smtplib`) — the actual sending mechanism, dry-run by default
- **SQLite3** (Python stdlib) — structured storage
- **n8n** — automation workflow reference (JSON file, importable)
- No Instagram/YouTube/TikTok API calls are live in this submission — see "Data sources" below for why, and how to wire them in

## Data sources

I don't have API credentials for Instagram Graph API, YouTube Data API, or
TikTok's Research API in this environment, and didn't want to submit
scraped data that could be stale, against a platform's ToS, or — worse —
just invented numbers presented as real (the assignment explicitly says not
to fabricate influencer data or guess emails, and I take that seriously).

So `src/discovery.py` runs in a documented mock mode: it generates 110
influencer profiles in the exact shape real discovery would return —
mixed niches, realistic follower/engagement distributions, some profiles
deliberately outside the target range so filtering has real work to do.
Every field downstream (filtering, enrichment, personalization, sending,
tracking) runs on genuine logic against that data; only the discovery
source itself is synthetic, and it's labeled that way throughout.

**To go live:** set `config.MOCK_DISCOVERY = False` and fill in
`fetch_from_youtube()` / `fetch_from_instagram()` in `discovery.py` with
real API calls using your own keys.

## Discovery methodology

`discovery.discover()` generates profiles across 5 niches (Fitness, Beauty,
Fintech, Gaming, Technology), weighted 45% toward the configured target
niche and 55% split across the other four — modeling a real hashtag/keyword
search, which returns mostly-on-topic results with some off-niche noise
mixed in, not an even 1-in-5 split. So the target-niche filter still has
real work to do (roughly 2 in 3 discovered profiles get rejected on this
run), it's just not artificially starved down to a handful of qualifiers.
Follower counts are drawn from three deliberate buckets (below/in/above the
5K–100K range) and engagement rate is modeled to trend down as followers go
up, which is roughly how real influencer data looks. `config.NUM_DISCOVERED`
controls volume (currently 110, weighted toward the target niche so
filtering has a meaningful pool to work with rather than a near-empty one,
comfortably over the 50-minimum).

## Filtering logic

Implemented filter category: **Fitness niche** (the assignment only
requires one complete category). Checks live in `config.py` so they're
easy to retarget at a different niche or brand:

- Niche == Fitness
- Followers between 5,000–100,000
- Engagement rate ≥ 2%
- Platform in [Instagram, YouTube, TikTok]

Every influencer — pass or fail — gets a `status` (`Qualified` /
`Rejected`) and a `filter_reason` explaining exactly which check(s) it
failed, not just a pass/fail count. This is what `influencer_dataset.csv`
shows for all 110 rows.

## Enrichment process

`src/enrich.py` fills in the mandatory fields (name, platform, URL,
followers, engagement, niche, content themes, email) for every qualified
profile. If an email genuinely can't be found, it's marked `"Not Found"` —
never guessed, per the assignment's explicit instruction. Optional fields
(audience age/gender/geography) are filled where discovery has them,
`"Not Available"` otherwise.

## AI model / prompt used

**Model:** Claude, via the `anthropic` SDK (model string `claude-sonnet-4-6`,
configurable via `config.ANTHROPIC_MODEL`) — primary provider. Falls back
to OpenAI (`config.OPENAI_MODEL`, default `gpt-4o-mini`) automatically if
only `OPENAI_API_KEY` is set. Same prompts either way — nothing
provider-specific, so switching is a config change, not a rewrite.

**Prompt design** (in `src/personalize.py`): separate system + user prompts
for the email and the DM. The system prompt encodes the hard constraints —
word count range, tone, "no generic filler," must reference a real
collaboration type from the brand's list, output only the message body
with no preamble. The user prompt passes the influencer's actual niche,
platform, content themes, follower count, and engagement rate, so the
model has real signals instead of a name to slot into a template.

**Status of this integration:** it's a real, working implementation — not
a stub — but I don't have an API key provisioned in this sandboxed
environment, so it hasn't generated the submitted messages. I unit-tested
both the Anthropic and OpenAI call paths against mocked API responses
(happy path, provider-priority when both keys are set, and the
retry-then-fallback error path) to confirm the integration actually works
before relying on it (see `DEMO.md`). Set `ANTHROPIC_API_KEY` or
`OPENAI_API_KEY` and it takes over automatically, no code changes needed.

**What actually generated the submitted messages:** a template-fallback
generator (also in `personalize.py`) that pulls each influencer's real
niche, content theme, platform, and a randomly chosen collab angle into a
randomized template bank, so no two messages are identical even without a
live model call.

**Why there's no key in this repo:** an API key is a secret tied to
someone's billing account, not something that belongs in version control —
committing one to a public GitHub repo would expose it within minutes to
anyone scanning for leaked keys. `.env` (where a real key would go
locally) is listed in `.gitignore` for exactly this reason. The
expectation is that the logic gets reviewed as code — the prompts, the
retry/fallback handling, the unit tests in `DEMO.md` — rather than by
running it against a live model with a reviewer-supplied key.

## Personalization logic

Two messages per qualified influencer:
- **Email pitch**, 60–90 words, referencing niche/content theme/proposed
  collaboration/value prop
- **Instagram DM**, 15–30 words, short and casual

Personalization signals used: niche, primary content theme, platform,
follower tier (implicitly, via which collab angle gets chosen), and the
brand context from `config.py`. Word counts are checked and logged per
message (`email_word_count`, `dm_word_count` columns) so it's verifiable
that the length constraints are actually met, not just claimed.

## Sending mechanism

`src/sending.py`, `DRY_RUN = True` by default — the full select → send →
log flow runs, but no real email goes out. Flip to `False` and provide
SMTP credentials to send for real. For each qualified influencer it:

1. Skips anyone without a real email on file (`"Not Found"`)
2. Checks the tracker for anyone already marked `Sent` and skips them —
   **dedup**, verified by running the pipeline twice back-to-back and
   confirming the second run sends 0 (see `DEMO.md`)
3. Logs every attempt — sent, skipped, or failed, with a reason — to both
   `outreach_tracker.csv` and `data/outreach.db`

**Instagram DMs are not auto-sent.** Meta doesn't permit automated bulk DM
sending for outreach use cases through any public API, and the assignment
is explicit about not routing around that. The DM copy is generated and
logged the same way as the email, ready for manual sending.

## Error handling

- A malformed/missing-field record during filtering doesn't crash the run
  — it's caught, marked `status="Error"`, logged with the reason, and the
  batch continues
- `personalize_all()` runs per-influencer in a try/except — one bad record
  or failed LLM call produces a `[generation failed: ...]` placeholder for
  just that influencer, not a crashed batch
- LLM calls retry once on failure before falling back to template mode
- SMTP failures are caught per-recipient and logged as `Failed` with the
  actual exception message
- A bad row on SQLite insert is skipped with a warning, not a rolled-back
  batch
- Zero qualified influencers → pipeline stops cleanly with a message
  instead of crashing on an empty list downstream

## Limitations

- Discovery runs on generated sample data, not live scraping (see "Data
  sources" above for the full reasoning). Everything downstream is real.
- The submitted messages came from template-fallback mode since no LLM key
  is configured here — the real LLM path exists and is tested, just not
  live for this submission.
- Audience demographics (age/gender/geography) are the fields most likely
  to be `"Not Available"` in real scraping too — most platforms don't
  expose this without the creator's own analytics access.
- Sending is email-only for real delivery; Instagram DM sending is
  intentionally manual (platform policy, not a technical gap).

## Scalability (50 → 500+ influencers)

- Swap the CSV files for Postgres — schema's already flat, and the SQLite
  layer (`src/db.py`) already speaks structured SQL, so this is a
  connection-string change, not a rewrite
- Batch the personalization step instead of looping one-by-one, especially
  once it's calling a real LLM (rate limits matter at that volume)
- Move sending to a queue (Celery + Redis, or a cron job batching N per
  hour) to respect email provider sending limits
- Discovery would need to paginate through the source APIs rather than
  pulling everything in one call

## Structured storage (`src/db.py`)

Every run also writes to `data/outreach.db` (SQLite): an `influencers`
table and an `outreach_log` table, using `INSERT ... ON CONFLICT DO UPDATE`
keyed on `(handle, platform)` so re-runs update existing records instead of
duplicating them — verified by running the pipeline twice and checking the
row count stayed flat.

## Automation workflow (`automation_workflow.n8n.json`)

A reference n8n workflow mapping this pipeline onto a no-code automation
tool: scheduled trigger → discovery → follower-range filter → LLM
personalization → branch on email availability → send → log to tracker.
Importable into a real n8n instance; not run live here (no n8n instance
available in this environment) — each node's notes explain which Python
module it corresponds to.

## Sample output

See `data/influencer_dataset.csv` for the full 110-row set (pass + fail,
with reasons) or `data/influencers_qualified.csv` for just the 38 qualified,
enriched, and messaged profiles. Example from the current seeded run:

> **Jordan Fit** — YouTube, 74,820 followers, 4.04% engagement
> **Email:** "Hi Jordan, loved your recent strength training content - your
> Fitness audience is exactly who we're trying to reach. I'm reaching out
> from Voltura Fit... We'd love to explore a barter collaboration..."
> **DM:** "Hi Jordan - big fan of your strength training content - we're
> looking for Fitness creators for a Voltura Fit campaign and you came to mind."

## Project structure

```
influencer_outreach/
├── config.py                    # all thresholds, brand info, API keys live here
├── main.py                       # runs the full pipeline
├── requirements.txt
├── .env.example                  # template - copy to .env locally, never commit .env
├── .gitignore                    # keeps .env, __pycache__ out of the repo
├── automation_workflow.n8n.json  # reference n8n workflow (importable)
├── README.md
├── DEMO.md                       # captured run output / evidence
├── src/
│   ├── discovery.py
│   ├── filter_classify.py
│   ├── enrich.py
│   ├── personalize.py            # includes real Anthropic + OpenAI API integration
│   ├── sending.py
│   └── db.py                     # SQLite storage layer
├── tests/test_pipeline.py        # 15 offline tests
└── data/                          # generated on run
    ├── influencer_dataset.csv     # main deliverable - all 110, pass + fail
    ├── influencers_raw.csv
    ├── influencers_qualified.csv
    ├── outreach_tracker.csv
    ├── outreach_log.json
    └── outreach.db
```
