"""Sending + tracking stage.

Email is the only real delivery channel. ``config.DRY_RUN`` is ``True`` by
default, so the full select -> skip -> log flow runs without sending anything.
Instagram DMs are generated for manual sending (Meta does not allow automated
bulk DMs for outreach), and the tracker records that decision explicitly.
"""

from __future__ import annotations

import csv
import json
import os
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage

import config

_TRACKER_FIELDS = [
    "timestamp", "name", "handle", "platform", "email", "status",
    "reason", "email_pitch", "instagram_dm",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _read_tracker() -> list[dict]:
    if not os.path.exists(config.TRACKER_PATH):
        return []
    with open(config.TRACKER_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _already_contacted() -> set[tuple[str, str]]:
    """Dedup key: (handle, platform) for every prior successful send.

    Note the ``startswith("Sent")`` check: dry-run writes ``"Sent (dry-run)"``,
    and comparing against the literal ``"Sent"`` silently broke dedup once.
    """
    done: set[tuple[str, str]] = set()
    for row in _read_tracker():
        if str(row.get("status", "")).startswith("Sent"):
            done.add((row.get("handle", ""), row.get("platform", "")))
    return done


def _send_smtp(profile: dict) -> None:
    if not (config.SMTP_USER and config.SMTP_PASSWORD):
        raise RuntimeError("SMTP_USER / SMTP_PASSWORD are not configured")

    message = EmailMessage()
    message["From"] = config.FROM_ADDRESS
    message["To"] = profile["email"]
    message["Subject"] = f"{config.BRAND_NAME} x {profile.get('name', 'creator')} - collaboration idea"
    message.set_content(profile.get("email_pitch", ""))

    context = ssl.create_default_context()
    if config.SMTP_PORT == 465:
        with smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT, context=context, timeout=20) as server:
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.send_message(message)
    else:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=20) as server:
            server.starttls(context=context)
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.send_message(message)


def send_batch(profiles: list[dict]) -> list[dict]:
    """Send (or simulate) one email per qualified profile and log every attempt."""
    contacted = _already_contacted()
    rows: list[dict] = []

    for profile in profiles:
        row = {
            "timestamp": _now(),
            "name": profile.get("name", ""),
            "handle": profile.get("handle", ""),
            "platform": profile.get("platform", ""),
            "email": profile.get("email", "Not Found"),
            "status": "",
            "reason": "",
            "email_pitch": profile.get("email_pitch", ""),
            "instagram_dm": profile.get("instagram_dm", ""),
        }
        key = (row["handle"], row["platform"])

        if row["email"] in ("", "Not Found", None):
            row["status"] = "Skipped"
            row["reason"] = "no email on file (never guessed)"
        elif key in contacted:
            row["status"] = "Skipped"
            row["reason"] = "already contacted (dedup)"
        elif config.DRY_RUN:
            row["status"] = "Sent (dry-run)"
            row["reason"] = "dry-run enabled - no real email sent"
            contacted.add(key)
        else:
            try:
                _send_smtp(profile)
                row["status"] = "Sent"
                row["reason"] = "delivered to SMTP"
                contacted.add(key)
            except Exception as exc:  # noqa: BLE001 - per-recipient isolation
                row["status"] = "Failed"
                row["reason"] = f"{type(exc).__name__}: {exc}"

        rows.append(row)

    _append_tracker(rows)
    _write_log(rows)
    return rows


def _append_tracker(rows: list[dict]) -> None:
    os.makedirs(os.path.dirname(config.TRACKER_PATH), exist_ok=True)
    new_file = not os.path.exists(config.TRACKER_PATH)
    with open(config.TRACKER_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_TRACKER_FIELDS, extrasaction="ignore")
        if new_file:
            writer.writeheader()
        writer.writerows(rows)


def _write_log(rows: list[dict]) -> None:
    os.makedirs(os.path.dirname(config.LOG_PATH), exist_ok=True)
    existing: list[dict] = []
    if os.path.exists(config.LOG_PATH):
        try:
            with open(config.LOG_PATH, encoding="utf-8") as f:
                existing = json.load(f)
            if not isinstance(existing, list):
                existing = []
        except (OSError, json.JSONDecodeError):
            existing = []
    with open(config.LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(existing + rows, f, indent=2, ensure_ascii=False)
