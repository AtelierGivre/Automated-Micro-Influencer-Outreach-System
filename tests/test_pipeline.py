"""Offline tests for the outreach pipeline.

Run with:  python -m pytest -q
"""

from __future__ import annotations

import csv
import json

import pytest

import config
from src import db, discovery, enrich, filter_classify, personalize, sending


# --------------------------------------------------------------------------- discovery
def test_discovery_is_deterministic_and_complete():
    config.DISCOVERY_SEED = 76
    first = discovery._mock_discover()
    second = discovery._mock_discover()
    assert first == second
    assert len(first) == config.NUM_DISCOVERED
    required = {
        "name", "handle", "platform", "followers", "engagement_rate",
        "niche", "content_themes", "email", "profile_url",
    }
    assert required.issubset(first[0])


def test_discovery_weights_target_niche():
    config.DISCOVERY_SEED = 76
    rows = discovery._mock_discover()
    fitness = sum(1 for r in rows if r["niche"] == "Fitness")
    # 45% target weight, with normal sampling noise.
    assert 30 <= fitness <= 65


# --------------------------------------------------------------------------- filtering
def test_filter_accepts_a_qualified_profile():
    passed, reasons = filter_classify.evaluate(
        {"niche": "Fitness", "followers": 20_000, "engagement_rate": 4.0, "platform": "Instagram"}
    )
    assert passed is True
    assert reasons == []


def test_filter_explains_every_failure():
    passed, reasons = filter_classify.evaluate(
        {"niche": "Fintech", "followers": 3_612, "engagement_rate": 1.2, "platform": "Facebook"}
    )
    assert passed is False
    joined = "; ".join(reasons)
    assert "Fintech" in joined
    assert "3,612" in joined
    assert "1.20%" in joined
    assert "Facebook" in joined


def test_filter_rejects_malformed_records():
    with pytest.raises(KeyError):
        filter_classify.evaluate({"niche": "Fitness"})
    with pytest.raises(ValueError):
        filter_classify.evaluate(
            {"niche": "Fitness", "followers": "many", "engagement_rate": 3, "platform": "Instagram"}
        )


# --------------------------------------------------------------------------- enrichment
def test_enrich_never_guesses_missing_email():
    out = enrich.enrich({"name": "Aarav Fit", "email": "", "handle": "aaravfit"})
    assert out["email"] == "Not Found"
    assert out["geography"] == "Not Available"
    assert out["enriched"] is True


def test_enrich_fills_mandatory_fields():
    out = enrich.enrich({"name": "Aarav Fit", "handle": "aaravfit", "email": "a@b.com"})
    assert out["profile_url"]
    assert out["platform"] == "Unknown"
    assert out["email"] == "a@b.com"


# --------------------------------------------------------------------------- personalization
def test_template_messages_respect_word_limits():
    profile = {
        "name": "Kabir Fit", "handle": "kabirfit1", "platform": "TikTok",
        "followers": 68_565, "engagement_rate": 5.44, "niche": "Fitness",
        "content_themes": "running/cardio", "email": "kabir@example.com",
    }
    for _ in range(30):
        out = personalize.personalize(profile)
        assert config.EMAIL_WORD_RANGE[0] <= out["email_word_count"] <= config.EMAIL_WORD_RANGE[1]
        assert config.DM_WORD_RANGE[0] <= out["dm_word_count"] <= config.DM_WORD_RANGE[1]
        assert out["email_pitch"]
        assert out["instagram_dm"]


def test_personalization_varies_between_profiles():
    a = personalize.personalize({"name": "A Fit", "handle": "a", "platform": "TikTok",
                                 "niche": "Fitness", "content_themes": "yoga"})
    b = personalize.personalize({"name": "B Fit", "handle": "b", "platform": "YouTube",
                                 "niche": "Fitness", "content_themes": "strength training"})
    assert a["email_pitch"] != b["email_pitch"]


def test_llm_path_is_used_when_a_key_is_configured(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(
        personalize, "_call_anthropic",
        lambda prompt, system: "Model written message that mentions Fitness and a sponsored post clearly.",
    )
    out = personalize.personalize({"name": "Mia Fit", "handle": "mia", "platform": "TikTok",
                                   "niche": "Fitness", "content_themes": "yoga"})
    assert out["email_pitch"].startswith("Model written message")
    assert config.EMAIL_WORD_RANGE[0] <= out["email_word_count"] <= config.EMAIL_WORD_RANGE[1]


def test_llm_failure_falls_back_to_template(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(personalize, "_call_anthropic", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("503")))
    monkeypatch.setattr(personalize, "_retrying_call", lambda call, attempts=3: call())
    out = personalize.personalize({"name": "Mia Fit", "handle": "mia", "platform": "TikTok",
                                   "niche": "Fitness", "content_themes": "yoga"})
    assert "generation failed" not in out["email_pitch"]
    assert out["email_word_count"] > 0


def test_langchain_backend_is_used_when_selected(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(config, "PERSONALIZE_BACKEND", "langchain")
    monkeypatch.setattr(personalize, "_langchain_available", lambda: True)
    monkeypatch.setattr(
        personalize, "_call_langchain",
        lambda prompt, system: "LangChain written message that mentions Fitness and a sponsored post clearly.",
    )
    out = personalize.personalize({"name": "Mia Fit", "handle": "mia", "platform": "TikTok",
                                   "niche": "Fitness", "content_themes": "yoga"})
    assert out["email_pitch"].startswith("LangChain written message")
    assert config.EMAIL_WORD_RANGE[0] <= out["email_word_count"] <= config.EMAIL_WORD_RANGE[1]
    assert personalize.llm_mode() == "LLM via LangChain"


def test_langchain_selection_falls_back_to_direct_when_not_installed(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(config, "PERSONALIZE_BACKEND", "langchain")
    monkeypatch.setattr(personalize, "_langchain_available", lambda: False)
    monkeypatch.setattr(
        personalize, "_call_anthropic",
        lambda prompt, system: "Direct SDK message that mentions Fitness and a sponsored post clearly.",
    )
    out = personalize.personalize({"name": "Mia Fit", "handle": "mia", "platform": "TikTok",
                                   "niche": "Fitness", "content_themes": "yoga"})
    assert out["email_pitch"].startswith("Direct SDK message")
    assert personalize.llm_mode() == "LLM"


def test_langchain_failure_falls_back_to_template(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(config, "PERSONALIZE_BACKEND", "langchain")
    monkeypatch.setattr(personalize, "_langchain_available", lambda: True)
    monkeypatch.setattr(
        personalize, "_call_langchain",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("langchain 503")),
    )
    monkeypatch.setattr(personalize, "_retrying_call", lambda call, attempts=3: call())
    out = personalize.personalize({"name": "Mia Fit", "handle": "mia", "platform": "TikTok",
                                   "niche": "Fitness", "content_themes": "yoga"})
    assert "generation failed" not in out["email_pitch"]
    assert out["email_word_count"] > 0


# --------------------------------------------------------------------------- sending
@pytest.fixture()
def isolated_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(config, "TRACKER_PATH", str(tmp_path / "tracker.csv"))
    monkeypatch.setattr(config, "LOG_PATH", str(tmp_path / "log.json"))
    monkeypatch.setattr(config, "DB_PATH", str(tmp_path / "outreach.db"))
    monkeypatch.setattr(config, "DRY_RUN", True)
    return tmp_path


def test_send_batch_skips_missing_email_and_dedups(isolated_paths):
    rows = [
        {"name": "A", "handle": "a", "platform": "TikTok", "email": "a@x.com",
         "email_pitch": "hello", "instagram_dm": "hi"},
        {"name": "B", "handle": "b", "platform": "TikTok", "email": "Not Found",
         "email_pitch": "hello", "instagram_dm": "hi"},
    ]
    first = sending.send_batch(rows)
    assert [r["status"] for r in first] == ["Sent (dry-run)", "Skipped"]

    second = sending.send_batch(rows)
    assert [r["status"] for r in second] == ["Skipped", "Skipped"]
    assert "dedup" in second[0]["reason"]

    with open(config.TRACKER_PATH, newline="", encoding="utf-8") as f:
        assert len(list(csv.DictReader(f))) == 4
    with open(config.LOG_PATH, encoding="utf-8") as f:
        assert len(json.load(f)) == 4


def test_smtp_failure_is_logged_per_recipient(isolated_paths, monkeypatch):
    monkeypatch.setattr(config, "DRY_RUN", False)
    monkeypatch.setattr(sending, "_send_smtp", lambda profile: (_ for _ in ()).throw(RuntimeError("smtp down")))
    out = sending.send_batch([{"name": "A", "handle": "a", "platform": "TikTok",
                               "email": "a@x.com", "email_pitch": "hello"}])
    assert out[0]["status"] == "Failed"
    assert "smtp down" in out[0]["reason"]


# --------------------------------------------------------------------------- storage
def test_db_upsert_is_idempotent(isolated_paths):
    rows = [{"handle": "a", "platform": "TikTok", "name": "A", "followers": 10,
             "engagement_rate": 3.0, "email": "a@x.com"}]
    db.upsert_influencers(rows)
    db.upsert_influencers(rows)
    assert db.counts()["influencers"] == 1


def test_db_logs_outreach(isolated_paths):
    db.log_outreach([{"handle": "a", "platform": "TikTok", "status": "Sent (dry-run)"}])
    db.log_outreach([{"handle": "a", "platform": "TikTok", "status": "Skipped"}])
    assert db.counts()["outreach_log"] == 2
