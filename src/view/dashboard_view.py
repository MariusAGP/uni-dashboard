from __future__ import annotations

import pandas as pd
import streamlit as st

from src.dto.dashboard_daten import DashboardDaten


class DashboardView:
    def zeige_dashboard(self, daten: DashboardDaten) -> None:
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

    def _zeige_header(self, daten: DashboardDaten) -> None:
        col_titel, col_info = st.columns([3, 1])
        with col_titel:
            st.title("Studium Dashboard")
            st.caption(f"{daten.studiengang_name}")
        with col_info:
            st.metric(
                label="Semester",
                value=f"{daten.aktuelles_semester} / {daten.gesamt_semester}",
            )
            fortschritt = daten.aktuelles_semester / daten.gesamt_semester
            if fortschritt <= 0.5:
                st.success("Im Zeitplan")
            elif fortschritt <= 0.75:
                st.warning("Zeitplan prüfen")
            else:
                st.error("Zeitplan kritisch")

    def zeige_kpi_karten(self, daten: DashboardDaten) -> None:
        k1, k2, k3, k4 = st.columns(4)

        with k1:
            st.metric(
                label="Semester",
                value=f"{daten.aktuelles_semester} / {daten.gesamt_semester}",
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
