from __future__ import annotations

from src.controller.dashboard_controller import DashboardController
from src.repository.lerneinheit_repository import LerneinheitRepository
from src.repository.studiengang_repository import StudiengangRepository
from src.service.lern_service import LernService
from src.service.studien_service import StudienService
from src.view.dashboard_view import DashboardView

_DB_PFAD = "src/data/studium.db"


class DashboardApp:
    def start(self) -> None:
        studiengang_repo = StudiengangRepository(_DB_PFAD)
        lerneinheit_repo = LerneinheitRepository(_DB_PFAD)
        controller = DashboardController(
            studien_service=StudienService(),
            lern_service=LernService(),
            studiengang_repo=studiengang_repo,
            lerneinheit_repo=lerneinheit_repo,
        )
        daten = controller.lade_dashboard_daten()
        view = DashboardView()
        view.zeige_dashboard(daten)


DashboardApp().start()
