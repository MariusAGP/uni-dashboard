from __future__ import annotations

from collections.abc import Callable
from datetime import date

import pandas as pd
import streamlit as st

from src.dto.dashboard_daten import DashboardDaten


class DashboardView:
    def zeige_dashboard(
        self,
        daten: DashboardDaten,
        on_save_pruefung: Callable[[str, float, date, int], None],
        on_save_lerneinheit: Callable[[date, float, str], None],
    ) -> None:
        st.set_page_config(page_title="Studium Dashboard", layout="wide")
        self._zeige_header(daten)
        self.zeige_kpi_karten(daten)
        st.divider()
        col_links, col_rechts = st.columns(2)
        with col_links:
            self.zeige_ects_chart(daten)
        with col_rechts:
            self.zeige_noten_chart(daten)
        st.divider()
        col_unten_links, col_unten_rechts = st.columns(2)
        with col_unten_links:
            self.zeige_workload_chart(daten)
        with col_unten_rechts:
            self.zeige_offene_module(daten)
        self._zeige_dialoge(daten, on_save_pruefung, on_save_lerneinheit)

    def _zeige_header(self, daten: DashboardDaten) -> None:
        col_titel, col_rechts = st.columns([3, 1])
        with col_titel:
            st.title("Studium Dashboard")
            st.caption(f"{daten.studiengang_name}")
        with col_rechts:
            if st.button("Prüfung eintragen", use_container_width=True):
                st.session_state["dialog_pruefung"] = True
            if st.button("Lerneinheit eintragen", use_container_width=True):
                st.session_state["dialog_lerneinheit"] = True

    def zeige_kpi_karten(self, daten: DashboardDaten) -> None:
        k1, k2, k3, k4 = st.columns(4)

        with k1:
            if daten.ects_soll_aktuell > 0:
                ects_abweichung = (daten.ects_erreicht - daten.ects_soll_aktuell) / daten.ects_soll_aktuell
            else:
                ects_abweichung = 0.0
            if ects_abweichung >= -0.1:
                status = "Im Zeitplan"
            elif ects_abweichung >= -0.25:
                status = "Zeitplan prüfen"
            else:
                status = "Zeitplan kritisch"
            st.metric(
                label="Semester",
                value=f"{daten.aktuelles_semester} / {daten.gesamt_semester}",
                delta=status,
                delta_color="off",
                help="Aktuelles Semester / Regelstudienzeit",
            )

        with k2:
            delta_note = round(daten.notendurchschnitt - daten.ziel_notenschnitt, 2)
            st.metric(
                label="Notenschnitt",
                value=f"{daten.notendurchschnitt:.2f}",
                delta=f"{delta_note:+.2f} zum Ziel ({daten.ziel_notenschnitt})",
                delta_color="inverse",
            )

        with k3:
            delta_ects = daten.ects_erreicht - daten.ects_soll_aktuell
            st.metric(
                label="ECTS",
                value=f"{daten.ects_erreicht} / {daten.ects_gesamt}",
                delta=f"{delta_ects:+d} vs. Soll ({daten.ects_soll_aktuell})",
            )

        with k4:
            delta_h = round(daten.lernstunden_durchschnitt - daten.ziel_lernstunden, 1)
            st.metric(
                label="Lernstunden / Woche",
                value=f"{daten.lernstunden_durchschnitt:.1f} h",
                delta=f"{delta_h:+.1f} h zum Ziel ({daten.ziel_lernstunden:.0f} h)",
            )

    def zeige_ects_chart(self, daten: DashboardDaten) -> None:
        st.subheader("ECTS-Fortschritt pro Semester")
        if not daten.ects_pro_semester.semester_nummern:
            st.info("Keine ECTS-Daten vorhanden.")
            return

        df = pd.DataFrame(
            {
                "Soll (kumuliert)": daten.ects_pro_semester.soll_werte,
                "Ist (kumuliert)": daten.ects_pro_semester.ist_werte,
            },
            index=[f"Sem. {n}" for n in daten.ects_pro_semester.semester_nummern],
        )
        st.bar_chart(df)

    def zeige_noten_chart(self, daten: DashboardDaten) -> None:
        st.subheader("Notenentwicklung pro Semester")
        if not daten.noten_pro_semester:
            st.info("Noch keine Noten vorhanden.")
            return

        noten = [s.durchschnitt for s in daten.noten_pro_semester]
        labels = [f"Sem. {s.semester_nummer}" for s in daten.noten_pro_semester]
        ziel = [daten.ziel_notenschnitt] * len(noten)

        df = pd.DataFrame(
            {"Notenschnitt": noten, f"Ziel ({daten.ziel_notenschnitt})": ziel},
            index=labels,
        )
        st.line_chart(df)

    def zeige_workload_chart(self, daten: DashboardDaten) -> None:
        st.subheader("Lernstunden pro Woche (letzte 8 Wochen)")
        if not daten.wochen_stunden:
            st.info("Keine Lerndaten vorhanden.")
            return

        stunden = [w.stunden for w in daten.wochen_stunden]
        labels = [f"KW {w.kalenderwoche}" for w in daten.wochen_stunden]
        ziel = [daten.ziel_lernstunden] * len(stunden)

        df = pd.DataFrame(
            {
                "Lernstunden": stunden,
                f"Ziel ({daten.ziel_lernstunden:.0f} h)": ziel,
            },
            index=labels,
        )
        st.bar_chart(df)

    def zeige_offene_module(self, daten: DashboardDaten) -> None:
        st.subheader("Offene & laufende Module")
        if not daten.offene_module:
            st.success("Alle Module abgeschlossen!")
            return

        for modul in daten.offene_module:
            st.markdown(
                f"**{modul.name}** — {modul.ects} ECTS "
                f"*(Semester {modul.semester_nummer})*"
            )

    def _zeige_dialoge(
        self,
        daten: DashboardDaten,
        on_save_pruefung: Callable[[str, float, date, int], None],
        on_save_lerneinheit: Callable[[date, float, str], None],
    ) -> None:
        @st.dialog("Prüfung eintragen")
        def pruefung_dialog() -> None:
            modul_namen = [m.name for m in daten.offene_module]
            if not modul_namen:
                st.info("Alle Module bestanden.")
                return
            with st.form("pruefung_form"):
                modul = st.selectbox("Modul", modul_namen)
                note = st.selectbox(
                    "Note",
                    [1.0, 1.3, 1.7, 2.0, 2.3, 2.7, 3.0, 3.3, 3.7, 4.0, 5.0],
                )
                pruef_datum = st.date_input("Prüfungsdatum", value=date.today())
                versuch = st.number_input("Versuch", min_value=1, max_value=3, value=1, step=1)
                if st.form_submit_button("Speichern", use_container_width=True):
                    on_save_pruefung(modul, float(note), pruef_datum, int(versuch))
                    st.rerun()

        @st.dialog("Lerneinheit eintragen")
        def lerneinheit_dialog() -> None:
            with st.form("lerneinheit_form"):
                lern_datum = st.date_input("Datum", value=date.today())
                stunden = st.number_input(
                    "Stunden", min_value=0.5, max_value=12.0, value=2.0, step=0.5
                )
                notiz = st.text_input("Notiz (optional)", value="")
                if st.form_submit_button("Speichern", use_container_width=True):
                    on_save_lerneinheit(lern_datum, float(stunden), notiz)
                    st.rerun()

        if st.session_state.pop("dialog_pruefung", False):
            pruefung_dialog()
        if st.session_state.pop("dialog_lerneinheit", False):
            lerneinheit_dialog()
