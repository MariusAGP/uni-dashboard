from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from src.domain.modul import Modul


@dataclass
class Semester:
    nummer: int
    start_datum: date
    end_datum: date
    module: list[Modul] = field(default_factory=list)
