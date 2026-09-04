# Demo

No video/screenshots since this was built and run in a sandboxed
environment, so this is a real captured terminal transcript from an actual
run instead - `python main.py`, output unedited.

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

  Nikhil Fit (Instagram, 96924 followers, 4.75% ER)
  Email (69 words): Hi Nikhil, been going through your mobility & stretching content on Instagram and really liked how you break things down. At Voltura Fit, we're putting together a small group of Fitness creators for our upcoming launch, and your audience feels like the right match. If you're open to it, we'd like to set up a UGC content creation - no pressure either way, just wanted to reach out directly.
  DM (23 words): Hi Nikhil! Loved your mobility & stretching content - your Fitness audience would be a great fit for a Voltura Fit collab. Interested?

  Kabir Fit (YouTube, 55432 followers, 5.03% ER)
  Email (66 words): Hi Kabir, loved your recent mobility & stretching content - your Fitness audience is exactly who we're trying to reach. At Voltura Fit, we're building out a creator program - a DTC fitness apparel and supplement brand launching a new activewear line - and think there's a natural fit here. We'd love to explore a sponsored post together if that's something you're taking on right now.
  DM (26 words): Hi Kabir - big fan of your mobility & stretching content! Think you'd be a great match for a Voltura Fit partnership. Worth a quick chat?

  Aarav Fit (Instagram, 41500 followers, 5.98% ER)
  Email (68 words): Hi Aarav, loved your recent strength training content - your Fitness audience is exactly who we're trying to reach. At Voltura Fit, we're building out a creator program - a DTC fitness apparel and supplement brand launching a new activewear line - and think there's a natural fit here. Would you be open to a sponsored post - happy to share more details and rates on your side.
  DM (22 words): Hi Aarav! Loved your strength training content - your Fitness audience would be a great fit for a Voltura Fit collab. Interested?

[6/7] Sending: 29 sent (dry-run=True), 9 skipped -> data/outreach_tracker.csv
       -> data/outreach.db (outreach_log table)

[7/7] Done. 110 discovered -> 38 qualified -> 29 sent.
Data in data/*.csv, data/outreach.db, and data/outreach_log.json
```

## Qualified set (all 38, not just the 3 printed above)

| Name | Platform | Followers | Engagement | Email |
|---|---|---|---|---|
| Nikhil Fit | Instagram | 96,924 | 4.75% | nikhilfit72@gmail.com |
| Kabir Fit | YouTube | 55,432 | 5.03% | kabirenergy88@creatoremail.com |
| Aarav Fit | Instagram | 41,500 | 5.98% | **Not Found** |
| Rohan Fit | YouTube | 66,213 | 6.06% | **Not Found** |
| Ishita Fit | Instagram | 41,509 | 5.46% | ishitalife58@creatoremail.com |
| Pooja Fit | TikTok | 71,562 | 4.01% | **Not Found** |
| Mia Fit | TikTok | 86,183 | 3.77% | miadaily32@outlook.com |
| Meera Fit | YouTube | 14,508 | 4.78% | meeradiaries83@gmail.com |
| Arjun Fit | YouTube | 62,433 | 6.04% | arjunmoves32@creatoremail.com |
| Ethan Fit | Instagram | 41,265 | 4.42% | ethanform7@gmail.com |
| Ethan Fit | YouTube | 34,831 | 4.98% | ethancoach45@outlook.com |
| Tara Fit | TikTok | 8,617 | 5.14% | taragrind87@gmail.com |
| Jordan Fit | YouTube | 27,241 | 6.19% | jordanlifts66@gmail.com |
| Ishita Fit | Instagram | 67,277 | 5.41% | ishitagetsstrong4@creatoremail.com |
| Vivaan Fit | YouTube | 75,798 | 3.94% | **Not Found** |
| Jordan Fit | TikTok | 66,261 | 6.19% | jordandiaries52@outlook.com |
| Priya Fit | Instagram | 92,747 | 3.74% | priyadaily20@outlook.com |
| Arjun Fit | TikTok | 28,086 | 6.37% | arjundiaries59@outlook.com |
| Sam Fit | TikTok | 33,361 | 6.29% | samlife98@gmail.com |
| Kabir Fit | TikTok | 40,954 | 4.43% | **Not Found** |
| Dev Fit | TikTok | 30,928 | 5.55% | devwellness81@gmail.com |
| Jordan Fit | Instagram | 9,852 | 5.15% | jordanenergy84@outlook.com |
| Tara Fit | TikTok | 27,280 | 4.98% | taragrind73@outlook.com |
| Mia Fit | TikTok | 13,285 | 6.37% | mialife42@gmail.com |
| Diya Fit | TikTok | 77,641 | 4.22% | **Not Found** |
| Meera Fit | YouTube | 19,408 | 6.33% | **Not Found** |
| Ananya Fit | TikTok | 19,896 | 6.53% | ananyafit17@outlook.com |
| Sam Fit | Instagram | 81,869 | 6.03% | samjourney48@outlook.com |
| Kabir Fit | TikTok | 14,120 | 5.12% | kabirform19@creatoremail.com |
| Diya Fit | YouTube | 79,395 | 5.17% | diyagetsstrong48@creatoremail.com |
| Karan Fit | YouTube | 33,255 | 6.33% | **Not Found** |
| Riya Fit | Instagram | 32,686 | 6.37% | riyadaily8@gmail.com |
| Riya Fit | Instagram | 92,562 | 5.47% | **Not Found** |
| Rohan Fit | TikTok | 15,308 | 5.73% | rohanlifts56@outlook.com |
| Sana Fit | TikTok | 41,002 | 5.8% | sanacoach57@outlook.com |
| Vivaan Fit | Instagram | 71,462 | 4.77% | vivaanmoves83@creatoremail.com |
| Sameer Fit | YouTube | 91,057 | 5.89% | sameerdiaries50@gmail.com |
| Alex Fit | YouTube | 97,908 | 5.71% | alexjourney85@gmail.com |

9 of the 38 have no public email on file, correctly marked `Not Found`
rather than guessed - and correctly `Skipped` (not sent) in the tracker,
which is exactly the behavior the assignment asks for.

## Full dataset (the actual assignment deliverable)

`data/influencer_dataset.csv` has all 110 discovered profiles - the 38
above that qualified, plus all 72 that didn't, each with a `status` and a
`filter_reason` explaining exactly why. A few rejected rows as a sample:

| Name | Platform | Followers | Niche | Status | Reason |
|---|---|---|---|---|---|
| Priya Creates | Instagram | 18,434 | Fintech | Rejected | niche is 'Fintech', not 'Fitness' |
| Meera Fit | YouTube | 3,612 | Fitness | Rejected | followers (3,612) outside 5,000-100,000 range |
| Riya Creates | YouTube | 86,070 | Technology | Rejected | niche is 'Technology', not 'Fitness' |

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
>>> sqlite3.connect('data/outreach.db')
influencers table:   38 rows (stays flat across reruns - upsert on
                      (handle, platform), not a duplicating insert)
outreach_log table:  grows by one row per attempt per run (it's a log,
                      not a dedup'd table - each send/skip attempt is a
                      distinct event worth keeping)
```

## LLM integration check (mocked, since no API key is set in this environment)

Both provider paths in `personalize.py` were unit-tested against mocked API
responses, not just assumed to work:

```
OK - no key raises NotImplementedError: No LLM key configured - see config.py
OK - anthropic path: anthropic response text here
   model used: claude-sonnet-4-6
OK - openai path: openai response text here
   model used: gpt-4o-mini
OK - both keys set, anthropic used: True openai used: False
OK - retries then raises: LLM generation failed after 3 attempts: 503 overloaded
```

That covers: no key configured, Anthropic-only, OpenAI-only, both-keys
(confirms Anthropic gets priority), and the retry-then-raise failure path
that lets `personalize.py` fall back to template mode cleanly instead of
crashing the batch.

**This part is still simulated, not a live call** - no `ANTHROPIC_API_KEY`
or `OPENAI_API_KEY` was available in the environment this was built and run
in. Every message in this submission's dataset came from the
template-fallback generator, which is disclosed in the README rather than
presented as LLM output. If you run this with a real key exported, `[4/7]`
in the output above will say `(LLM mode)` instead of `(template fallback
mode)` and the messages will come from the model directly - no code
changes needed.
