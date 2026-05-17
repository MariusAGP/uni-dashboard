from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class Lerneinheit:
    datum: date
    stunden: float
    notiz: str
