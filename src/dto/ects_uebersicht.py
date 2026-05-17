from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EctsUebersicht:
    semester_nummern: list[int] = field(default_factory=list)
    soll_werte: list[int] = field(default_factory=list)
    ist_werte: list[int] = field(default_factory=list)
