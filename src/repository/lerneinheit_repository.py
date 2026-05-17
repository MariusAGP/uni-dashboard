from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

from src.domain.lerneinheit import Lerneinheit


def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


class LerneinheitRepository:
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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lerneinheit (
                    id INTEGER PRIMARY KEY,
                    datum TEXT NOT NULL,
                    stunden REAL NOT NULL,
                    notiz TEXT NOT NULL DEFAULT ''
                )
            """)
            exists = conn.execute("SELECT COUNT(*) FROM lerneinheit").fetchone()[0]
            if not exists:
                self._insert_beispieldaten(conn)

    def _insert_beispieldaten(self, conn: sqlite3.Connection) -> None:
        heute = date.today()
        montag_dieser_woche = heute - timedelta(days=heute.weekday())

        eintraege = []
        wochen_stunden = [18.5, 21.0, 17.5, 22.0, 19.0, 20.5, 16.0, 23.5]

        for wochen_rueck in range(7, -1, -1):
            woche_montag = montag_dieser_woche - timedelta(weeks=wochen_rueck)
            ziel_stunden = wochen_stunden[7 - wochen_rueck]

            verteilung = [0.25, 0.20, 0.20, 0.20, 0.15]
            tage = [0, 1, 2, 3, 6]
            for i, (anteil, tag_offset) in enumerate(zip(verteilung, tage)):
                tag = woche_montag + timedelta(days=tag_offset)
                stunden = round(ziel_stunden * anteil, 1)
                notizen = [
                    "Vorlesung nachbereitet",
                    "Übungsaufgaben gelöst",
                    "Kapitel gelesen",
                    "Projekt bearbeitet",
                    "Lerngruppe",
                ]
                eintraege.append((tag.isoformat(), stunden, notizen[i]))

        conn.executemany(
            "INSERT INTO lerneinheit (datum, stunden, notiz) VALUES (?, ?, ?)",
            eintraege,
        )

    def lade_alle(self, modul_id: int) -> list[Lerneinheit]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM lerneinheit ORDER BY datum"
            ).fetchall()
        return [
            Lerneinheit(datum=_parse_date(r["datum"]), stunden=r["stunden"], notiz=r["notiz"])
            for r in rows
        ]

    def lade_nach_zeitraum(self, von: date, bis: date) -> list[Lerneinheit]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM lerneinheit WHERE datum >= ? AND datum <= ? ORDER BY datum",
                (von.isoformat(), bis.isoformat()),
            ).fetchall()
        return [
            Lerneinheit(datum=_parse_date(r["datum"]), stunden=r["stunden"], notiz=r["notiz"])
            for r in rows
        ]

    def speichere(self, einheit: Lerneinheit) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO lerneinheit (datum, stunden, notiz) VALUES (?, ?, ?)",
                (einheit.datum.isoformat(), einheit.stunden, einheit.notiz),
            )
