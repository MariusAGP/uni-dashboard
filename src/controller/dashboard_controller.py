from __future__ import annotations

from datetime import date, timedelta

from src.domain.lerneinheit import Lerneinheit
from src.domain.modul_status_enum import ModulStatusEnum
from src.domain.pruefungsleistung import Pruefungsleistung
from src.dto.dashboard_daten import DashboardDaten
from src.dto.offene_modul_info import OffeneModulInfo
from src.repository.lerneinheit_repository import LerneinheitRepository
from src.repository.studiengang_repository import StudiengangRepository
from src.service.lern_service import LernService
from src.service.studien_service import StudienService


class DashboardController:
    def __init__(
        self,
        studien_service: StudienService,
        lern_service: LernService,
        studiengang_repo: StudiengangRepository,
        lerneinheit_repo: LerneinheitRepository,
    ) -> None:
        self._studien_service = studien_service
        self._lern_service = lern_service
        self._studiengang_repo = studiengang_repo
        self._lerneinheit_repo = lerneinheit_repo

    def speichere_pruefung(
        self, modul_name: str, note: float, datum: date, versuch: int
    ) -> None:
        pruefung = Pruefungsleistung(note=note, datum=datum, versuch=versuch)
        self._studiengang_repo.speichere_pruefung(modul_name, pruefung)

    def speichere_lerneinheit(self, datum: date, stunden: float, notiz: str) -> None:
        einheit = Lerneinheit(datum=datum, stunden=stunden, notiz=notiz)
        self._lerneinheit_repo.speichere(einheit)

    def lade_dashboard_daten(self) -> DashboardDaten:
        studiengang = self._studiengang_repo.lade_studiengang()

        bis = date.today()
        von = bis - timedelta(weeks=8)
        lerneinheiten = self._lerneinheit_repo.lade_nach_zeitraum(von, bis)

        alle_module = [m for sem in studiengang.semester for m in sem.module]

        notendurchschnitt = self._studien_service.berechne_notendurchschnitt(alle_module)
        ects_uebersicht = self._studien_service.berechne_ects_fortschritt(
            studiengang.semester,
            studiengang.gesamt_ects,
            studiengang.regelstudienzeit_semester,
        )
        noten_pro_semester = self._studien_service.berechne_noten_pro_semester(
            studiengang.semester
        )
        wochen_stunden = self._lern_service.berechne_wochenstunden(lerneinheiten)
        lernstunden_durchschnitt = self._lern_service.berechne_durchschnitt(lerneinheiten)

        ects_erreicht = sum(m.ects for m in alle_module if m.ist_bestanden())
        aktuelles_semester = len(studiengang.semester)
        ects_soll_aktuell = (
            ects_uebersicht.soll_werte[-1] if ects_uebersicht.soll_werte else 0
        )
        zeitplan_status = self._studien_service.berechne_zeitplan_status(
            ects_erreicht, ects_soll_aktuell
        )

        offene_module = [
            OffeneModulInfo(name=m.name, ects=m.ects, semester_nummer=sem.nummer)
            for sem in studiengang.semester
            for m in sem.module
            if m.status in (ModulStatusEnum.OFFEN, ModulStatusEnum.LAUFEND)
        ]

        return DashboardDaten(
            studiengang_name=studiengang.name,
            aktuelles_semester=aktuelles_semester,
            gesamt_semester=studiengang.regelstudienzeit_semester,
            notendurchschnitt=notendurchschnitt,
            ziel_notenschnitt=1.5,
            ects_erreicht=ects_erreicht,
            ects_gesamt=studiengang.gesamt_ects,
            ects_soll_aktuell=ects_soll_aktuell,
            lernstunden_durchschnitt=lernstunden_durchschnitt,
            ziel_lernstunden=20.0,
            zeitplan_status=zeitplan_status,
            ects_pro_semester=ects_uebersicht,
            noten_pro_semester=noten_pro_semester,
            wochen_stunden=wochen_stunden,
            offene_module=offene_module,
        )
