"""
preprocessing/date_resolver.py — Layer 2: Date Resolver.

Resolves natural-language date expressions to ISO-8601 strings (YYYY-MM-DD).
"""

import re
from datetime import date, timedelta


class DateResolver:
    """
    Resolve natural-language date expressions to ISO-8601 strings.

    Resolution strategy
    -------------------
    1. Fast manual rules handle the most common business phrases exactly.
    2. ``dateparser`` library handles everything else with PREFER_DATES_FROM=future.
    3. Returns None for any expression that cannot be confidently resolved.
    """

    @staticmethod
    def _next_weekday(base: date, weekday: int) -> date:
        """Return the upcoming occurrence of ``weekday`` (0=Mon...6=Sun) on or after base+1."""
        days_ahead = weekday - base.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return base + timedelta(days=days_ahead)

    @staticmethod
    def _last_day_of_month(d: date) -> date:
        """Return the last calendar day of the month containing ``d``."""
        if d.month == 12:
            return date(d.year + 1, 1, 1) - timedelta(days=1)
        return date(d.year, d.month + 1, 1) - timedelta(days=1)

    @classmethod
    def resolve(cls, expression: str | None, today: date) -> str | None:
        """
        Convert a date expression to YYYY-MM-DD anchored at ``today``.
        Returns None if the expression is empty or cannot be resolved.
        """
        if not expression:
            return None

        expr = expression.strip().lower()

        if expr in ("today", "eod", "cob", "by eod", "by cob"):
            return today.isoformat()
        if expr in ("tomorrow",):
            return (today + timedelta(days=1)).isoformat()
        if expr in ("this friday", "friday", "end of week", "eow", "by friday"):
            return cls._next_weekday(today, 4).isoformat()
        if expr in ("this monday", "monday", "next week", "start of next week"):
            return cls._next_weekday(today, 0).isoformat()
        if expr in ("this tuesday", "tuesday"):
            return cls._next_weekday(today, 1).isoformat()
        if expr in ("this wednesday", "wednesday", "mid-week"):
            return cls._next_weekday(today, 2).isoformat()
        if expr in ("this thursday", "thursday"):
            return cls._next_weekday(today, 3).isoformat()
        if expr in ("this saturday", "saturday"):
            return cls._next_weekday(today, 5).isoformat()
        if expr in ("this sunday", "sunday", "end of weekend"):
            return cls._next_weekday(today, 6).isoformat()
        if expr in ("end of month", "eom", "by end of month"):
            return cls._last_day_of_month(today).isoformat()
        if expr in ("this week",):
            return cls._next_weekday(today, 4).isoformat()
        if expr in ("next friday",):
            upcoming = cls._next_weekday(today, 4)
            return (upcoming + timedelta(weeks=1)).isoformat()
        if expr in ("next monday",):
            upcoming = cls._next_weekday(today, 0)
            return (upcoming + timedelta(weeks=1)).isoformat()

        m = re.fullmatch(r"in (\d+) days?", expr)
        if m:
            return (today + timedelta(days=int(m.group(1)))).isoformat()

        m = re.fullmatch(r"in (\d+) weeks?", expr)
        if m:
            return (today + timedelta(weeks=int(m.group(1)))).isoformat()

        m = re.fullmatch(r"by (.+)", expr)
        if m:
            return cls.resolve(m.group(1), today)

        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", expression):
            try:
                date.fromisoformat(expression)
                return expression
            except ValueError:
                return None

        # dateparser fallback
        try:
            import dateparser  # type: ignore
            parsed = dateparser.parse(
                expression,
                settings={
                    "PREFER_DATES_FROM": "future",
                    "RELATIVE_BASE": today,
                    "RETURN_AS_TIMEZONE_AWARE": False,
                },
            )
            if parsed:
                return parsed.date().isoformat()
        except Exception:
            pass

        return None
