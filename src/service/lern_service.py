from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from src.domain.lerneinheit import Lerneinheit
from src.dto.wochen_stunden import WochenStunden


class LernService:
    def berechne_wochenstunden(self, einheiten: list[Lerneinheit]) -> list[WochenStunden]:
        wochen: dict[int, float] = defaultdict(float)
        for einheit in einheiten:
            kw = einheit.datum.isocalendar()[1]
            wochen[kw] += einheit.stunden
        return [
            WochenStunden(kalenderwoche=kw, stunden=round(stunden, 2))
            for kw, stunden in sorted(wochen.items())
        ]

    def berechne_durchschnitt(self, einheiten: list[Lerneinheit]) -> float:
        if not einheiten:
            return 0.0
        wochen = self.berechne_wochenstunden(einheiten)
        if not wochen:
            return 0.0
        gesamt = sum(w.stunden for w in wochen)
        return round(gesamt / len(wochen), 2)

    def lade_lerneinheiten_letzte_wochen(
        self, einheiten: list[Lerneinheit], wochen: int = 8
    ) -> list[Lerneinheit]:
        grenze = date.today() - timedelta(weeks=wochen)
        return [e for e in einheiten if e.datum >= grenze]
