from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OffeneModulInfo:
    name: str
    ects: int
    semester_nummer: int
