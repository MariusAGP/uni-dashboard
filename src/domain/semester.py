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

    def ects_bestanden(self) -> int:
        return sum(m.ects for m in self.module if m.ist_bestanden())

    def berechne_notenschnitt(self) -> float:
        noten = [m.note() for m in self.module if m.ist_bestanden() and m.note() is not None]
        if not noten:
            return 0.0
        return round(sum(noten) / len(noten), 2)
