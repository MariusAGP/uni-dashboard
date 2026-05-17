from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class Pruefungsleistung:
    note: float
    datum: date
    versuch: int
