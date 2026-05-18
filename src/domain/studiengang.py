from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.modul import Modul
from src.domain.semester import Semester


@dataclass
class Studiengang:
    name: str
    regelstudienzeit_semester: int
    gesamt_ects: int
    semester: list[Semester] = field(default_factory=list)

    def alle_module(self) -> list[Modul]:
        return [m for sem in self.semester for m in sem.module]

    def offene_module(self) -> list[tuple[Modul, Semester]]:
        return [
            (m, sem)
            for sem in self.semester
            for m in sem.module
            if m.ist_offen() or m.ist_laufend()
        ]
