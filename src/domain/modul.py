from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.lerneinheit import Lerneinheit
from src.domain.modul_status_enum import ModulStatusEnum
from src.domain.pruefungsleistung import Pruefungsleistung


@dataclass
class Modul:
    name: str
    ects: int
    status: ModulStatusEnum
    pruefung: Pruefungsleistung | None = None
    lerneinheiten: list[Lerneinheit] = field(default_factory=list)

    def ist_bestanden(self) -> bool:
        return self.status == ModulStatusEnum.BESTANDEN

    def ist_offen(self) -> bool:
        return self.status == ModulStatusEnum.OFFEN

    def ist_laufend(self) -> bool:
        return self.status == ModulStatusEnum.LAUFEND

    def note(self) -> float | None:
        return self.pruefung.note if self.pruefung else None
