"""Darba dienu palīgfunkcija (vienkāršots Latvijas kalendārs 2026–2027)."""

from datetime import date

import pytest

from app.working_days import add_working_days, is_working_day, next_working_day


def test_sunday_is_not_a_working_day():
    assert not is_working_day(date(2026, 11, 1))


def test_proclamation_day_is_not_a_working_day():
    assert not is_working_day(date(2026, 11, 18))


def test_next_working_day_after_sunday_is_monday():
    assert next_working_day(date(2026, 11, 1)) == date(2026, 11, 2)


def test_next_working_day_skips_ligo_and_jani():
    assert next_working_day(date(2027, 6, 23)) == date(2027, 6, 25)


def test_add_five_working_days_skips_weekend():
    # Ceturtdiena + 5 darba dienas → nākamā ceturtdiena
    assert add_working_days(date(2026, 10, 1), 5) == date(2026, 10, 8)


def test_add_working_days_skips_holiday():
    # 13.11. (piektdiena) + 5 darba dienas, 18.11. ir svētku diena
    assert add_working_days(date(2026, 11, 13), 5) == date(2026, 11, 23)


def test_year_outside_calendar_is_rejected():
    with pytest.raises(ValueError):
        is_working_day(date(2028, 1, 3))
