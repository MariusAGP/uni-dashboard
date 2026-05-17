from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SemesterNote:
    semester_nummer: int
    durchschnitt: float
