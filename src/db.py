"""SQLite storage layer.

The CSV files remain the deliverables; SQLite is the queryable copy. Both
tables are written defensively so one malformed row cannot roll back a batch.
"""

from __future__ import annotations

import os
import sqlite3

import config


def _db_path() -> str:
    return getattr(config, "DB_PATH", os.path.join(config.DATA_DIR, "outreach.db"))


def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(_db_path()), exist_ok=True)
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS influencers (
                handle TEXT NOT NULL,
                platform TEXT NOT NULL,
                name TEXT,
                followers INTEGER,
                engagement_rate REAL,
                niche TEXT,
                content_themes TEXT,
                email TEXT,
                profile_url TEXT,
                geography TEXT,
                audience_age TEXT,
                audience_gender TEXT,
                status TEXT,
                filter_reason TEXT,
                email_pitch TEXT,
                instagram_dm TEXT,
                email_word_count INTEGER,
                dm_word_count INTEGER,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (handle, platform)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS outreach_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                name TEXT,
                handle TEXT,
                platform TEXT,
                email TEXT,
                status TEXT,
                reason TEXT,
                email_pitch TEXT,
                instagram_dm TEXT
            )
            """
        )


def upsert_influencers(rows: list[dict]) -> int:
    """Insert or update on ``(handle, platform)`` so reruns stay flat."""
    init_db()
    written = 0
    with _connect() as conn:
        for row in rows:
            try:
                conn.execute(
                    """
                    INSERT INTO influencers (
                        handle, platform, name, followers, engagement_rate, niche,
                        content_themes, email, profile_url, geography, audience_age,
                        audience_gender, status, filter_reason, email_pitch,
                        instagram_dm, email_word_count, dm_word_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(handle, platform) DO UPDATE SET
                        name=excluded.name,
                        followers=excluded.followers,
                        engagement_rate=excluded.engagement_rate,
                        niche=excluded.niche,
                        content_themes=excluded.content_themes,
                        email=excluded.email,
                        profile_url=excluded.profile_url,
                        geography=excluded.geography,
                        audience_age=excluded.audience_age,
                        audience_gender=excluded.audience_gender,
                        status=excluded.status,
                        filter_reason=excluded.filter_reason,
                        email_pitch=excluded.email_pitch,
                        instagram_dm=excluded.instagram_dm,
                        email_word_count=excluded.email_word_count,
                        dm_word_count=excluded.dm_word_count,
                        updated_at=CURRENT_TIMESTAMP
                    """,
                    (
                        row.get("handle"), row.get("platform"), row.get("name"),
                        _as_int(row.get("followers")), _as_float(row.get("engagement_rate")),
                        row.get("niche"), row.get("content_themes"), row.get("email"),
                        row.get("profile_url"), row.get("geography"), row.get("audience_age"),
                        row.get("audience_gender"), row.get("status"), row.get("filter_reason"),
                        row.get("email_pitch"), row.get("instagram_dm"),
                        _as_int(row.get("email_word_count")), _as_int(row.get("dm_word_count")),
                    ),
                )
                written += 1
            except sqlite3.Error:
                continue
    return written


def log_outreach(rows: list[dict]) -> int:
    """Append one audit row per attempt (sends, skips and failures)."""
    init_db()
    written = 0
    with _connect() as conn:
        for row in rows:
            try:
                conn.execute(
                    """
                    INSERT INTO outreach_log (
                        timestamp, name, handle, platform, email, status,
                        reason, email_pitch, instagram_dm
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row.get("timestamp"), row.get("name"), row.get("handle"),
                        row.get("platform"), row.get("email"), row.get("status"),
                        row.get("reason"), row.get("email_pitch"), row.get("instagram_dm"),
                    ),
                )
                written += 1
            except sqlite3.Error:
                continue
    return written


def counts() -> dict[str, int]:
    init_db()
    with _connect() as conn:
        influencers = conn.execute("SELECT COUNT(*) FROM influencers").fetchone()[0]
        outreach = conn.execute("SELECT COUNT(*) FROM outreach_log").fetchone()[0]
    return {"influencers": influencers, "outreach_log": outreach}


def _as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
