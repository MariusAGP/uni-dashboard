from __future__ import annotations

from dataclasses import dataclass, field

from src.dto.ects_uebersicht import EctsUebersicht
from src.dto.offene_modul_info import OffeneModulInfo
from src.dto.semester_note import SemesterNote
from src.dto.wochen_stunden import WochenStunden


@dataclass
class DashboardDaten:
    studiengang_name: str
    aktuelles_semester: int
    gesamt_semester: int
    notendurchschnitt: float
    ziel_notenschnitt: float
    ects_erreicht: int
    ects_gesamt: int
    ects_soll_aktuell: int
    lernstunden_durchschnitt: float
    ziel_lernstunden: float
    ects_pro_semester: EctsUebersicht
    noten_pro_semester: list[SemesterNote] = field(default_factory=list)
    wochen_stunden: list[WochenStunden] = field(default_factory=list)
    offene_module: list[OffeneModulInfo] = field(default_factory=list)
