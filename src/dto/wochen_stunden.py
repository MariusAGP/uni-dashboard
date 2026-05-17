from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WochenStunden:
    kalenderwoche: int
    stunden: float
