from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.semester import Semester


@dataclass
class Studiengang:
    name: str
    regelstudienzeit_semester: int
    gesamt_ects: int
    semester: list[Semester] = field(default_factory=list)
