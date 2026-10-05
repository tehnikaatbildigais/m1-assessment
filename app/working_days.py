"""Darba dienu aprēķins pēc Latvijas svētku dienām 2026–2027.

Vienkāršots mācību vajadzībām: Ministru kabineta pārceltās darba dienas
un vienreizējas brīvdienas nav iekļautas.
"""

import json
from datetime import date, timedelta
from pathlib import Path

_DATA = Path(__file__).parent / "data" / "holidays_lv.json"
HOLIDAYS = {
    date.fromisoformat(item["date"]): item["name"]
    for item in json.loads(_DATA.read_text(encoding="utf-8"))["holidays"]
}
FIRST_YEAR = min(day.year for day in HOLIDAYS)
LAST_YEAR = max(day.year for day in HOLIDAYS)


def _check_range(day: date) -> None:
    if not FIRST_YEAR <= day.year <= LAST_YEAR:
        raise ValueError(f"Svētku dienas zināmas tikai {FIRST_YEAR}–{LAST_YEAR}")


def is_working_day(day: date) -> bool:
    _check_range(day)
    return day.weekday() < 5 and day not in HOLIDAYS


def next_working_day(day: date) -> date:
    """Atgriež pašu dienu, ja tā ir darba diena, citādi nākamo darba dienu."""
    while not is_working_day(day):
        day += timedelta(days=1)
    return day


def add_working_days(start: date, days: int) -> date:
    """Pieskaita darba dienas. Pati sākuma diena netiek skaitīta."""
    if days < 0:
        raise ValueError("Darba dienu skaits nedrīkst būt negatīvs")
    day = start
    remaining = days
    while remaining:
        day += timedelta(days=1)
        if is_working_day(day):
            remaining -= 1
    return day
