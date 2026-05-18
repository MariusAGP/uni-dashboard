from __future__ import annotations

# --- Schema ---

CREATE_SCHEMA = """
    CREATE TABLE IF NOT EXISTS studiengang (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        regelstudienzeit_semester INTEGER NOT NULL,
        gesamt_ects INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS semester (
        id INTEGER PRIMARY KEY,
        studiengang_id INTEGER NOT NULL,
        nummer INTEGER NOT NULL,
        start_datum TEXT NOT NULL,
        end_datum TEXT NOT NULL,
        FOREIGN KEY (studiengang_id) REFERENCES studiengang(id)
    );
    CREATE TABLE IF NOT EXISTS modul (
        id INTEGER PRIMARY KEY,
        semester_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        ects INTEGER NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (semester_id) REFERENCES semester(id)
    );
    CREATE TABLE IF NOT EXISTS pruefungsleistung (
        id INTEGER PRIMARY KEY,
        modul_id INTEGER NOT NULL UNIQUE,
        note REAL NOT NULL,
        datum TEXT NOT NULL,
        versuch INTEGER NOT NULL,
        FOREIGN KEY (modul_id) REFERENCES modul(id)
    );
"""

CREATE_LERNEINHEIT_SCHEMA = """
    CREATE TABLE IF NOT EXISTS lerneinheit (
        id INTEGER PRIMARY KEY,
        datum TEXT NOT NULL,
        stunden REAL NOT NULL,
        notiz TEXT NOT NULL DEFAULT ''
    )
"""

# --- Studiengang ---

ZAEHLE_STUDIENGAENGE = "SELECT COUNT(*) FROM studiengang"
LADE_STUDIENGANG = "SELECT * FROM studiengang LIMIT 1"
INSERT_STUDIENGANG = (
    "INSERT INTO studiengang (name, regelstudienzeit_semester, gesamt_ects) VALUES (?, ?, ?)"
)

# --- Semester ---

LADE_SEMESTER_FUER_STUDIENGANG = (
    "SELECT * FROM semester WHERE studiengang_id = ? ORDER BY nummer"
)
LADE_SEMESTER_IDS = "SELECT id FROM semester ORDER BY nummer"
INSERT_SEMESTER = (
    "INSERT INTO semester (studiengang_id, nummer, start_datum, end_datum) VALUES (?, ?, ?, ?)"
)

# --- Modul ---

LADE_MODULE_FUER_SEMESTER = "SELECT * FROM modul WHERE semester_id = ?"
LADE_MODUL_ID_NACH_NAME = "SELECT id FROM modul WHERE name = ?"
UPDATE_MODUL_STATUS = "UPDATE modul SET status = ? WHERE id = ?"
INSERT_MODUL = "INSERT INTO modul (semester_id, name, ects, status) VALUES (?, ?, ?, ?)"

# --- Pruefungsleistung ---

LADE_PRUEFUNG_FUER_MODUL = "SELECT * FROM pruefungsleistung WHERE modul_id = ?"
INSERT_PRUEFUNG = (
    "INSERT INTO pruefungsleistung (modul_id, note, datum, versuch) VALUES (?, ?, ?, ?)"
)
UPSERT_PRUEFUNG = """
    INSERT INTO pruefungsleistung (modul_id, note, datum, versuch)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(modul_id) DO UPDATE SET
        note = excluded.note,
        datum = excluded.datum,
        versuch = excluded.versuch
"""

# --- Lerneinheit ---

ZAEHLE_LERNEINHEITEN = "SELECT COUNT(*) FROM lerneinheit"
LADE_ALLE_LERNEINHEITEN = "SELECT * FROM lerneinheit ORDER BY datum"
LADE_LERNEINHEITEN_ZEITRAUM = (
    "SELECT * FROM lerneinheit WHERE datum >= ? AND datum <= ? ORDER BY datum"
)
INSERT_LERNEINHEIT = (
    "INSERT INTO lerneinheit (datum, stunden, notiz) VALUES (?, ?, ?)"
)

# --- Hilfsfunktionen ---

LAST_INSERT_ID = "SELECT last_insert_rowid()"
