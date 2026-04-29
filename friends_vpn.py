"""Режим «VPN для своих»: порог по дате регистрации (UTC), инвайт по рефке/метке, отдельные тарифы и реф-бонус."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Optional, Tuple

_RAW = os.environ.get("FRIENDS_VPN_CUTOFF_UTC", "").strip()


def _parse_cutoff(raw: str) -> Optional[datetime]:
    if not raw:
        return None
    for fmt in ("%d.%m.%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


FRIENDS_VPN_CUTOFF_UTC: Optional[datetime] = _parse_cutoff(_RAW)


def _as_naive_utc(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def user_created_before_cutoff(create_user: datetime) -> bool:
    if FRIENDS_VPN_CUTOFF_UTC is None:
        return True
    return _as_naive_utc(create_user) < FRIENDS_VPN_CUTOFF_UTC


def has_invite_source(ref: Any, stamp: Any) -> bool:
    return bool(str(ref or "").strip()) or bool(str(stamp or "").strip())


def omit_new_user_db_on_plain_start(had_row_before: bool, message_text: str) -> bool:
    """
    Новый пользователь, только команда /start без параметров — не создаём строку в users
    (при включённом пороге FRIENDS_VPN_CUTOFF_UTC).
    """
    if FRIENDS_VPN_CUTOFF_UTC is None or had_row_before:
        return False
    parts = (message_text or "").strip().split()
    return len(parts) == 1


def is_friends_only_locked(user_row: Tuple) -> bool:
    """
    После порога без рефки и без метки и без доступа в панель — только сообщение «для своих».
    Уже подключённых (in_panel) не блокируем (подарок, пробная оплата и т.д.).
    """
    if FRIENDS_VPN_CUTOFF_UTC is None:
        return False
    create_user = user_row[6]
    if not create_user or user_created_before_cutoff(create_user):
        return False
    if user_row[4]:
        return False
    if has_invite_source(user_row[2], user_row[14]):
        return False
    return True


def uses_new_friend_tariffs(user_row: Tuple) -> bool:
    """Новые цены: зарегистрирован после порога и пришёл с рефкой или меткой."""
    if FRIENDS_VPN_CUTOFF_UTC is None:
        return False
    create_user = user_row[6]
    if not create_user or user_created_before_cutoff(create_user):
        return False
    return has_invite_source(user_row[2], user_row[14])


def referrer_ref_bonus_days(referrer_row: Tuple) -> int:
    """+7 дней у «старых» рефереров (до порога), +30 — у зарегистрированных после порога."""
    create_user = referrer_row[6]
    if not create_user or user_created_before_cutoff(create_user):
        return 7
    return 30


# Лимит устройств в панели (hwid) для PRO — одинаковый для всех пользователей.
PRO_HWID_DEVICE_LIMIT = 5


def pro_hwid_device_limit_for_user_row(user_row: Optional[Tuple]) -> int:
    return PRO_HWID_DEVICE_LIMIT
