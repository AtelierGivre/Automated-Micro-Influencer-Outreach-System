# Demo

A real captured terminal transcript from an actual run (`python main.py`),
output unedited. The run is reproducible: `config.DISCOVERY_SEED` is pinned,
and the template fallback is deterministic per profile.

## Full run output

```
============================================================
Influencer outreach pipeline - target niche: Fitness
============================================================

[1/7] Discovery: found 110 profiles -> data/influencers_raw.csv
[2/7] Filtering: 38 qualified, 72 rejected
       -> data/influencer_dataset.csv (all 110, pass + fail, with reasons)
[3/7] Enrichment: filled mandatory fields for 38 profiles
[4/7] Personalization (template fallback mode): generated email + DM for 38 profiles
       -> data/influencers_qualified.csv
       -> data/outreach.db (influencers table)

[5/7] Sample generated messages:

  Jordan Fit (YouTube, 74820 followers, 4.04% ER)
  Email (75 words): Hi Jordan, loved your recent strength training content - your Fitness audience is exactly who we're trying to reach. I'm reaching out from Voltura Fit - a DTC fitness apparel and supplement brand launching a new activewear line - because we're building out a creator program and think there's a natural fit here. We'd love to explore a barter collaboration (free product in exchange for content) together if that's something you're taking on right now.
  DM (26 words): Hi Jordan - big fan of your strength training content - we're looking for Fitness creators for a Voltura Fit campaign and you came to mind.

  Pooja Fit (Instagram, 85013 followers, 4.01% ER)
  Email (77 words): Hi Pooja, loved your recent nutrition & meal prep content - your Fitness audience is exactly who we're trying to reach. I'm reaching out from Voltura Fit - a DTC fitness apparel and supplement brand launching a new activewear line - because we're building out a creator program and think there's a natural fit here. If you're open to it, we'd like to set up a sponsored post - happy to share more details on your side.
  DM (21 words): Hi Pooja! Loved your nutrition & meal prep content - think you'd be a great match for a Voltura Fit partnership.

  Ananya Fit (TikTok, 60575 followers, 3.68% ER)
  Email (75 words): Hi Ananya, your mobility & stretching posts on TikTok stood out to me, especially how clearly you explain things. At Voltura Fit, we're a DTC fitness apparel and supplement brand launching a new activewear line, and we're putting together a small group of Fitness creators for our upcoming launch. We'd love to explore a sponsored post together if that's something you're taking on right now. Your 60,575 followers and 3.68% engagement are a strong signal.
  DM (25 words): Hey Ananya, your mobility & stretching posts are great - we're looking for Fitness creators for a Voltura Fit campaign and you came to mind.

[6/7] Sending: 29 sent (dry-run=True), 9 skipped -> data/outreach_tracker.csv
       -> data/outreach.db (outreach_log table)

[7/7] Done. 110 discovered -> 38 qualified -> 29 sent.
Data in data/*.csv, data/outreach.db, and data/outreach_log.json
```

## Qualified set (all 38, not just the 3 printed above)

| Name | Platform | Followers | Engagement | Email |
|---|---|---|---|---|
| Jordan Fit | YouTube | 74,820 | 4.04% | jordanfit117@creatoremail.com |
| Pooja Fit | Instagram | 85,013 | 4.01% | poojafit388@gmail.com |
| Ananya Fit | TikTok | 60,575 | 3.68% | ananyafit8@outlook.com |
| Vivaan Fit | Instagram | 30,289 | 5.87% | **Not Found** |
| Nikhil Fit | TikTok | 17,725 | 3.14% | **Not Found** |
| Sana Fit | YouTube | 73,631 | 5.57% | sanafit1288@outlook.com |
| Sam Fit | Instagram | 25,280 | 5.21% | samfit154@outlook.com |
| Sameer Fit | Instagram | 71,381 | 6.34% | sameerfit1658@creatoremail.com |
| Priya Fit | TikTok | 24,105 | 5.82% | priyafit1732@gmail.com |
| Ananya Fit | TikTok | 51,924 | 3.57% | ananyafit224@creatoremail.com |
| Kabir Fit | TikTok | 70,966 | 3.66% | kabirfit2545@gmail.com |
| Mia Fit | TikTok | 83,209 | 3.6% | miafit27@outlook.com |
| Sameer Fit | TikTok | 65,724 | 2.95% | sameerfit294@creatoremail.com |
| Pooja Fit | TikTok | 36,999 | 6.49% | **Not Found** |
| Tara Fit | YouTube | 30,950 | 4.88% | tarafit36@gmail.com |
| Sameer Fit | Instagram | 85,467 | 4.04% | sameerfit4517@gmail.com |
| Ananya Fit | YouTube | 77,577 | 5.92% | ananyafit5132@gmail.com |
| Ishita Fit | YouTube | 65,473 | 5.7% | ishitafit564@outlook.com |
| Pooja Fit | TikTok | 88,251 | 3.78% | **Not Found** |
| Sana Fit | Instagram | 84,411 | 5.89% | sanafit6188@outlook.com |
| Dev Fit | Instagram | 36,778 | 4.33% | devfit6358@gmail.com |
| Sam Fit | TikTok | 36,318 | 4.74% | samfit6632@gmail.com |
| Arjun Fit | Instagram | 16,024 | 2.65% | **Not Found** |
| Karan Fit | TikTok | 84,086 | 3.05% | **Not Found** |
| Mia Fit | YouTube | 72,350 | 3.99% | miafit7532@creatoremail.com |
| Kabir Fit | YouTube | 91,664 | 3.51% | kabirfit7817@outlook.com |
| Meera Fit | Instagram | 51,026 | 2.37% | meerafit804@outlook.com |
| Aarav Fit | Instagram | 50,086 | 6.57% | **Not Found** |
| Dev Fit | Instagram | 16,281 | 6.48% | devfit8317@gmail.com |
| Rohan Fit | TikTok | 52,914 | 4.76% | rohanfit8488@gmail.com |
| Rohan Fit | Instagram | 56,204 | 6.22% | rohanfit8572@outlook.com |
| Alex Fit | Instagram | 32,684 | 2.85% | alexfit8645@creatoremail.com |
| Pooja Fit | TikTok | 62,210 | 6.37% | poojafit8772@outlook.com |
| Vivaan Fit | TikTok | 5,650 | 3.46% | **Not Found** |
| Nikhil Fit | YouTube | 9,443 | 5.74% | nikhilfit9658@creatoremail.com |
| Sameer Fit | Instagram | 80,305 | 2.42% | **Not Found** |
| Dev Fit | Instagram | 50,258 | 4.34% | devfit10045@gmail.com |
| Rohan Fit | TikTok | 95,597 | 4.39% | rohanfit106@gmail.com |

9 of the 38 have no public email on file, correctly marked `Not Found`
rather than guessed - and correctly `Skipped` (not sent) in the tracker,
which is exactly the behavior the assignment asks for.

## Full dataset (the actual assignment deliverable)

`data/influencer_dataset.csv` has all 110 discovered profiles - the 38
above that qualified, plus all 72 that didn't, each with a `status` and a
`filter_reason` explaining exactly why. A few rejected rows as a sample:

| Name | Platform | Followers | Niche | Status | Reason |
|---|---|---|---|---|---|
| Diya Fit | YouTube | 113,833 | Fitness | Rejected | followers (113,833) outside 5,000-100,000 range; engagement rate 1.60% below 2.0% |
| Sameer Fit | TikTok | 139,842 | Fitness | Rejected | followers (139,842) outside 5,000-100,000 range |
| Meera Creates | YouTube | 219,442 | Beauty | Rejected | niche is 'Beauty', not 'Fitness'; followers (219,442) outside 5,000-100,000 range; engagement rate 1.29% below 2.0% |
| Priya Creates | Instagram | 3,584 | Fintech | Rejected | niche is 'Fintech', not 'Fitness'; followers (3,584) outside 5,000-100,000 range |

This is the file that matches the assignment's recommended dataset format
(Name / Platform / Followers / Engagement / Niche / Email / Profile URL /
Content Theme / Status) with 110 rows, well over the 50 minimum, and a
34.5% qualify rate that shows the filter doing real, meaningful work
rather than passing almost everything or almost nothing.

## Dedup check (ran the pipeline twice back to back, same data)

Run 1: `29 sent, 9 skipped` (9 skipped for no email on file).
Run 2, immediately after, same qualified set: `0 sent, 38 skipped` - every
influencer already marked `Sent` in the tracker got skipped instead of
re-messaged, and the 9 no-email profiles are still correctly skipped too.
This is the actual bug I caught and fixed while building this: the first
version compared status against the literal string `"Sent"`, but dry-run
writes `"Sent (dry-run)"`, so dedup silently wasn't working. Left this in
the doc because "did the dedup logic actually get tested" felt like a fair
thing to show, not just claim.

## Structured storage check

```
sqlite3.connect('data/outreach.db')
influencers table:   38 rows (stays flat across reruns - upsert on
                      (handle, platform), not a duplicating insert)
outreach_log table:  76 rows after two runs (grows by one row per attempt
                      per run - it's a log, not a dedup'd table)
```

## LLM integration check (mocked, since no API key is set in this environment)

Both provider paths are unit-tested against mocked responses, not assumed
to work. The suite covers the Anthropic path, the OpenAI path, provider
priority, and retry-then-template-fallback:

```
python -m pytest -q
18 passed in 0.37s
```

Relevant tests in `tests/test_pipeline.py`:
- `test_llm_path_is_used_when_a_key_is_configured` - Anthropic response text
  reaches the generated message.
- `test_llm_failure_falls_back_to_template` - a failing model does not crash
  the batch and does not leak `[generation failed]` into the copy.
- `test_langchain_backend_is_used_when_selected` - the optional LangChain
  adapter is used when selected.
- `test_langchain_selection_falls_back_to_direct_when_not_installed` - the
  default SDK path still works without the optional packages.
- `test_langchain_failure_falls_back_to_template` - a failing LangChain call
  is isolated per profile.
- `test_template_messages_respect_word_limits` - 30 generated messages all
  land inside the configured 60-90 / 15-30 word ranges.
- `test_send_batch_skips_missing_email_and_dedups` - second run sends 0.
- `test_smtp_failure_is_logged_per_recipient` - SMTP errors are isolated.

**This part is still simulated, not a live call** - no `ANTHROPIC_API_KEY`
or `OPENAI_API_KEY` was available in the environment this was built and run
in. Every message in this submission's dataset came from the
template-fallback generator, which is disclosed in the README rather than
presented as LLM output. If you run this with a real key exported, `[4/7]`
in the output above will say `(LLM mode)` instead of `(template fallback
mode)` and the messages will come from the model directly - no code
changes needed.
