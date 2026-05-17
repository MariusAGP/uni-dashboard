# Studium Dashboard

Prototypisches Dashboard für ein B.Sc. Softwareentwicklung-Studium an der IU.

## Voraussetzungen

- Python 3.12
- pip

## Installation

```bash
pip install -r requirements.txt
```

## Start

```bash
streamlit run dashboard_app.py
```

Das Dashboard öffnet sich unter http://localhost:8501.

Beim ersten Start wird automatisch eine SQLite-Datenbank mit Beispieldaten angelegt (`studium_dashboard/data/studium.db`).

## Architektur

```
Domain  →  DTO  →  Service  →  Repository  →  Controller  →  View
```

- **Domain**: Fachklassen als @dataclass (Studiengang, Semester, Modul, …)
- **DTO**: Typisierte Transfer-Objekte zwischen Controller und View
- **Service**: Fachliche Berechnungen (StudienService, LernService)
- **Repository**: SQLite-Zugriff (StudiengangRepository, LerneinheitRepository)
- **Controller**: Orchestrierung, baut DashboardDaten zusammen
- **View**: Streamlit-Darstellung, greift nur auf DTOs zu
