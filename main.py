"""
Runs the full pipeline end to end:
Discovery -> Filter/Classify -> Enrich -> Personalize -> Review -> Send -> Track

Usage: python main.py
"""

import csv
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config
from src import discovery, filter_classify, enrich, personalize, sending, db


def save_csv(rows, path, fieldnames):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main():
    print("=" * 60)
    print(f"Influencer outreach pipeline - target niche: {config.TARGET_NICHE}")
    print("=" * 60)

    # 1. Discovery
    try:
        raw = discovery.discover()
        discovery.save_raw(raw)
        print(f"\n[1/7] Discovery: found {len(raw)} profiles -> data/influencers_raw.csv")
    except Exception as e:
        print(f"\n[1/7] Discovery FAILED: {e}")
        return  # nothing downstream can run without raw data

    # 2. Filter & classify - a bad record here shouldn't kill the whole batch
    qualified, rejected = [], []
    for inf in raw:
        try:
            passed, reasons = filter_classify.evaluate(inf)
            inf["status"] = "Qualified" if passed else "Rejected"
            inf["filter_reason"] = "; ".join(reasons)
            (qualified if passed else rejected).append(inf)
        except (KeyError, ValueError, TypeError) as e:
            inf["status"] = "Error"
            inf["filter_reason"] = f"malformed record, skipped: {e}"
            rejected.append(inf)
    print(f"[2/7] Filtering: {len(qualified)} qualified, {len(rejected)} rejected")

    # Assignment's "Expected Output B" wants ONE dataset of 50+ influencers
    # in this shape - Name/Platform/Followers/Engagement/Niche/Email/
    # Profile URL/Content Theme/Status - showing who passed AND who failed,
    # with a reason. influencers_raw.csv (written above, pre-filter) can't
    # carry Status since filtering hadn't run yet, so we write a second,
    # complete file here that matches the spec exactly.
    full_dataset_fields = [
        "name", "platform", "followers", "engagement_rate", "niche",
        "email", "profile_url", "content_themes", "status", "filter_reason",
    ]
    save_csv(raw, config.FULL_DATASET_PATH, full_dataset_fields)
    print(f"       -> data/influencer_dataset.csv (all {len(raw)}, pass + fail, with reasons)")

    if not qualified:
        print("No profiles qualified - nothing to enrich/send. Check config.py thresholds.")
        return

    # 3. Enrich (qualified only - no point enriching rejects)
    enriched = enrich.enrich_all(qualified)
    print(f"[3/7] Enrichment: filled mandatory fields for {len(enriched)} profiles")

    # 4. Personalize (per-influencer error handling lives inside personalize_all)
    personalized = personalize.personalize_all(enriched)
    print(f"[4/7] Personalization ({personalize.llm_mode()} mode): generated email + DM for {len(personalized)} profiles")

    fieldnames = [
        "name", "handle", "platform", "followers", "engagement_rate", "niche",
        "content_themes", "email", "profile_url", "geography", "audience_age",
        "audience_gender", "status", "filter_reason", "email_pitch",
        "instagram_dm", "email_word_count", "dm_word_count",
    ]
    save_csv(personalized, config.QUALIFIED_PATH, fieldnames)
    print("       -> data/influencers_qualified.csv")

    # structured storage, alongside the CSV
    try:
        db.upsert_influencers(personalized)
        print("       -> data/outreach.db (influencers table)")
    except Exception as e:
        print(f"       [db warning] couldn't write to SQLite: {e}")

    # 5. Review - just print 3 samples so it's easy to eyeball quality
    print("\n[5/7] Sample generated messages:")
    for inf in personalized[:3]:
        print(f"\n  {inf['name']} ({inf['platform']}, {inf['followers']} followers, {inf['engagement_rate']}% ER)")
        print(f"  Email ({inf['email_word_count']} words): {inf['email_pitch']}")
        print(f"  DM ({inf['dm_word_count']} words): {inf['instagram_dm']}")

    # 6. Send + track
    tracker_rows = sending.send_batch(personalized)
    sent = sum(1 for r in tracker_rows if "Sent" in r["status"])
    skipped = sum(1 for r in tracker_rows if r["status"] == "Skipped")
    print(f"\n[6/7] Sending: {sent} sent (dry-run={config.DRY_RUN}), {skipped} skipped -> data/outreach_tracker.csv")

    try:
        db.log_outreach(tracker_rows)
        print("       -> data/outreach.db (outreach_log table)")
    except Exception as e:
        print(f"       [db warning] couldn't write to SQLite: {e}")

    print(f"\n[7/7] Done. {len(raw)} discovered -> {len(qualified)} qualified -> {sent} sent.")
    print("Data in data/*.csv, data/outreach.db, and data/outreach_log.json")


if __name__ == "__main__":
    main()
