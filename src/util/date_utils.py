from __future__ import annotations

from datetime import date, datetime


def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()
