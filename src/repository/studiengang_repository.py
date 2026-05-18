from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

from src.domain.modul import Modul
from src.domain.modul_status_enum import ModulStatusEnum
from src.domain.pruefungsleistung import Pruefungsleistung
from src.domain.semester import Semester
from src.domain.studiengang import Studiengang
from src.repository import queries
from src.util.date_utils import parse_date


class StudiengangRepository:
    def __init__(self, db_pfad: str) -> None:
        self._db_pfad = db_pfad
        Path(db_pfad).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_pfad)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.executescript(queries.CREATE_SCHEMA)
            exists = conn.execute(queries.ZAEHLE_STUDIENGAENGE).fetchone()[0]
            if not exists:
                self._insert_beispieldaten(conn)

    def _insert_beispieldaten(self, conn: sqlite3.Connection) -> None:
        conn.execute(queries.INSERT_STUDIENGANG, ("Softwareentwicklung B.Sc.", 6, 180))
        studiengang_id = conn.execute(queries.LAST_INSERT_ID).fetchone()[0]

        semester_daten = [
            (1, "2024-10-01", "2025-03-31"),
            (2, "2025-04-01", "2025-09-30"),
            (3, "2025-10-01", "2026-03-31"),
        ]
        for nummer, start, end in semester_daten:
            conn.execute(queries.INSERT_SEMESTER, (studiengang_id, nummer, start, end))

        semester_ids = [
            r[0] for r in conn.execute(queries.LADE_SEMESTER_IDS).fetchall()
        ]

        module_sem1 = [
            ("Mathematik: Analysis", 5, "BESTANDEN", 1.7, "2025-01-15", 1),
            ("Einführung in die Programmierung", 5, "BESTANDEN", 1.3, "2025-01-22", 1),
            ("Grundlagen der Informatik", 5, "BESTANDEN", 2.0, "2025-02-05", 1),
            ("Wissenschaftliches Arbeiten", 5, "BESTANDEN", 1.0, "2025-02-12", 1),
            ("Statistik", 5, "BESTANDEN", 2.3, "2025-03-01", 1),
            ("Einführung in das Studium", 5, "BESTANDEN", 1.0, "2025-03-10", 1),
        ]
        module_sem2 = [
            ("Algorithmen und Datenstrukturen", 5, "BESTANDEN", 1.7, "2025-07-10", 1),
            ("Datenbanken", 5, "BESTANDEN", 2.0, "2025-07-17", 1),
            ("Objektorientierte Programmierung", 5, "BESTANDEN", 1.3, "2025-08-05", 1),
            ("Betriebssysteme und Netzwerke", 5, "LAUFEND", None, None, None),
            ("Web Engineering", 5, "LAUFEND", None, None, None),
        ]
        module_sem3 = [
            ("Softwareentwicklung und -architektur", 5, "OFFEN", None, None, None),
            ("Maschinelles Lernen", 5, "OFFEN", None, None, None),
            ("Agile Entwicklung", 5, "OFFEN", None, None, None),
            ("IT-Sicherheit", 5, "OFFEN", None, None, None),
            ("Projektmanagement", 5, "OFFEN", None, None, None),
        ]

        alle_module = [
            (semester_ids[0], module_sem1),
            (semester_ids[1], module_sem2),
            (semester_ids[2], module_sem3),
        ]

        for sem_id, module in alle_module:
            for name, ects, status, note, datum, versuch in module:
                conn.execute(queries.INSERT_MODUL, (sem_id, name, ects, status))
                modul_id = conn.execute(queries.LAST_INSERT_ID).fetchone()[0]
                if note is not None:
                    conn.execute(queries.INSERT_PRUEFUNG, (modul_id, note, datum, versuch))

    def lade_studiengang(self) -> Studiengang:
        with self._conn() as conn:
            sg_row = conn.execute(queries.LADE_STUDIENGANG).fetchone()
            semester_rows = conn.execute(
                queries.LADE_SEMESTER_FUER_STUDIENGANG, (sg_row["id"],)
            ).fetchall()

            semester_liste = []
            for sem_row in semester_rows:
                modul_rows = conn.execute(
                    queries.LADE_MODULE_FUER_SEMESTER, (sem_row["id"],)
                ).fetchall()

                module = []
                for m_row in modul_rows:
                    pruefung_row = conn.execute(
                        queries.LADE_PRUEFUNG_FUER_MODUL, (m_row["id"],)
                    ).fetchone()
                    pruefung = None
                    if pruefung_row:
                        pruefung = Pruefungsleistung(
                            note=pruefung_row["note"],
                            datum=parse_date(pruefung_row["datum"]),
                            versuch=pruefung_row["versuch"],
                        )
                    module.append(Modul(
                        name=m_row["name"],
                        ects=m_row["ects"],
                        status=ModulStatusEnum(m_row["status"]),
                        pruefung=pruefung,
                    ))

                semester_liste.append(Semester(
                    nummer=sem_row["nummer"],
                    start_datum=parse_date(sem_row["start_datum"]),
                    end_datum=parse_date(sem_row["end_datum"]),
                    module=module,
                ))

        return Studiengang(
            name=sg_row["name"],
            regelstudienzeit_semester=sg_row["regelstudienzeit_semester"],
            gesamt_ects=sg_row["gesamt_ects"],
            semester=semester_liste,
        )

    def speichere_pruefung(self, modul_name: str, pruefung: Pruefungsleistung) -> None:
        with self._conn() as conn:
            row = conn.execute(queries.LADE_MODUL_ID_NACH_NAME, (modul_name,)).fetchone()
            if row is None:
                raise ValueError(f"Modul '{modul_name}' nicht gefunden.")
            modul_id = row["id"]
            if pruefung.note <= 4.0:
                conn.execute(queries.UPDATE_MODUL_STATUS, (ModulStatusEnum.BESTANDEN.value, modul_id))
            conn.execute(
                queries.UPSERT_PRUEFUNG,
                (modul_id, pruefung.note, pruefung.datum.isoformat(), pruefung.versuch),
            )
