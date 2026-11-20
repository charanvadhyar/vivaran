"""Credits, tiers and plans, read from the database the website shares.

The rules live in SQL (platform/schema.sql: vivaran_tier, vivaran_ensure_monthly,
vivaran_balance, vivaran_spend, vivaran_refund) so the site and this server can
never disagree. This module only works out what a render costs and asks.

A credit is one video of up to `minutes_per_credit` minutes. A video voiced with
the platform's voice costs `voiced` credits per started block of that length; a
silent one, or one voiced on the user's own Gnani key, costs `silent_or_own_key`.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

DEFAULT_PLANS: dict[str, Any] = {
    "free": {"monthly_credits": 3, "max_minutes": 10, "watermark": True, "figures_per_month": 5},
    "pro": {"monthly_credits": 6, "max_minutes": 20, "watermark": False, "figures_per_month": 60, "price_inr": 299},
    "cost": {"minutes_per_credit": 10, "voiced": 1, "silent_or_own_key": 0.25},
    "rewards": {"creator_join": 2, "first_publish": 1, "subscribe": 1, "referral": 1, "views_1k": 2, "views_10k": 5},
    "packs": [], "downloads_per_day": 10, "youtube_channel_url": "",
    "cost_model": {"gnani_inr_per_1k_chars": 2.65, "server_inr_per_video_minute": 0.76, "inr_per_usd": 93.3},
}


def plans(db) -> dict[str, Any]:
    row = db.execute("select value from settings where key = 'plans'").fetchone()
    value = (row or {}).get("value") if isinstance(row, dict) else (row[0] if row else None)
    if isinstance(value, str):
        value = json.loads(value)
    merged = json.loads(json.dumps(DEFAULT_PLANS))
    for key, part in (value or {}).items():
        if isinstance(part, dict) and isinstance(merged.get(key), dict):
            merged[key].update(part)
        else:
            merged[key] = part
    return merged


def cost(p: dict[str, Any], seconds: float, voiced_on_platform: bool) -> float:
    """Credits for a video of this length."""
    c = p["cost"]
    blocks = max(1, math.ceil(seconds / 60 / float(c["minutes_per_credit"]) - 1e-9))
    rate = float(c["voiced"] if voiced_on_platform else c["silent_or_own_key"])
    return round(blocks * rate, 2)


def tier(db, user_id: str) -> str:
    row = db.execute("select vivaran_tier(%s::uuid) as t", (user_id,)).fetchone()
    return (row["t"] if isinstance(row, dict) else row[0]) or "free"


def balance(db, user_id: str) -> dict[str, float]:
    db.execute("select vivaran_ensure_monthly(%s::uuid)", (user_id,))
    row = db.execute("select monthly, bonus from vivaran_balance(%s::uuid)", (user_id,)).fetchone()
    monthly, bonus = (row["monthly"], row["bonus"]) if isinstance(row, dict) else row
    return {"monthly": float(monthly), "bonus": float(bonus), "total": float(monthly) + float(bonus)}


def spend(db, user_id: str, amount: float, video_id: str) -> bool:
    row = db.execute("select vivaran_spend(%s::uuid, %s::numeric, %s::text, 'render') as ok", (user_id, amount, video_id)).fetchone()
    return bool(row["ok"] if isinstance(row, dict) else row[0])


def refund(db, video_id: str) -> float:
    row = db.execute("select vivaran_refund(%s::text) as back", (video_id,)).fetchone()
    return float((row["back"] if isinstance(row, dict) else row[0]) or 0)


def event(db, type_: str, user_id: str | None = None, video_id: str | None = None, **meta: Any) -> None:
    db.execute("insert into events (type, user_id, video_id, meta) values (%s, %s::uuid, %s, %s::jsonb)",
               (type_, user_id, video_id, json.dumps(meta) if meta else None))


def apply_schema(database_url: str, platform_dir: str | None) -> bool:
    """Bring the database up to date with platform/schema.sql (safe to run again)."""
    import psycopg
    for candidate in (Path(platform_dir) / "schema.sql" if platform_dir else None,
                      Path(__file__).resolve().parents[2] / "platform" / "schema.sql"):
        if candidate and candidate.is_file():
            with psycopg.connect(database_url, autocommit=True) as db:
                db.execute(candidate.read_text(encoding="utf-8"))
            return True
    return False
