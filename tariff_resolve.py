"""Цена и описание тарифа по ключу callback (в т.ч. new_*), число дней для панели X3."""
from __future__ import annotations

from typing import Tuple

from lexicon import dct_desc, dct_desc_friends, dct_price, dct_price_friends


def tariff_rub_and_desc(duration_key: str) -> Tuple[int, str]:
    if duration_key in dct_price_friends:
        return dct_price_friends[duration_key], dct_desc_friends[duration_key]
    return dct_price[duration_key], dct_desc[duration_key]


def tariff_days_for_x3(duration_key_plain: str) -> int:
    """
    Ключ без префикса white_ (уже отрезан при необходимости).
    Примеры: '7', '30', 'new_7', 'new_3000'.
    """
    if duration_key_plain.startswith("new_"):
        if duration_key_plain == "new_3000":
            return 3000
        return int(duration_key_plain.replace("new_", "", 1))
    return int(duration_key_plain)
