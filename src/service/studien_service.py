from __future__ import annotations

from src.domain.semester import Semester
from src.domain.studiengang import Studiengang
from src.dto.ects_uebersicht import EctsUebersicht
from src.dto.semester_note import SemesterNote


class StudienService:
    def berechne_notendurchschnitt(self, studiengang: Studiengang) -> float:
        noten = [
            m.note()
            for m in studiengang.alle_module()
            if m.ist_bestanden() and m.note() is not None
        ]
        if not noten:
            return 0.0
        return round(sum(noten) / len(noten), 2)

    def berechne_ects_fortschritt(
        self, semester: list[Semester], gesamt_ects: int, gesamt_semester: int
    ) -> EctsUebersicht:
        ects_pro_semester = gesamt_ects / gesamt_semester
        uebersicht = EctsUebersicht()
        kumuliert_ist = 0
        for i, sem in enumerate(semester, start=1):
            soll = round(ects_pro_semester * i)
            kumuliert_ist += sem.ects_bestanden()
            uebersicht.semester_nummern.append(sem.nummer)
            uebersicht.soll_werte.append(soll)
            uebersicht.ist_werte.append(kumuliert_ist)
        return uebersicht

    def berechne_noten_pro_semester(self, semester: list[Semester]) -> list[SemesterNote]:
        return [
            SemesterNote(semester_nummer=sem.nummer, durchschnitt=sem.berechne_notenschnitt())
            for sem in semester
            if sem.berechne_notenschnitt() > 0.0
        ]

    def berechne_zeitplan_status(self, ects_erreicht: int, ects_soll: int) -> str:
        if ects_soll == 0:
            return "Im Zeitplan"
        abweichung = (ects_erreicht - ects_soll) / ects_soll
        if abweichung >= -0.1:
            return "Im Zeitplan"
        if abweichung >= -0.25:
            return "Zeitplan prüfen"
        return "Zeitplan kritisch"
