"""
StudentSync Backend Service Launcher
Initialises SQLite database and exposes backend services.
"""

from backend.config.settings import settings
from backend.database import init_db
from backend.services.analytics_service import AnalyticsService
from backend.database import get_db_connection


def start_backend_service():
    """Initialises backend database tables and runs health check."""
    init_db()
    print(f"\n[StudentSync Backend] Initialised successfully.")
    print(f"[StudentSync Backend] Environment: {settings.ENVIRONMENT}")
    print(f"[StudentSync Backend] Database Path: {settings.DATABASE_URL}")

    # Run quick analytics query check
    conn = get_db_connection()
    summary = AnalyticsService.get_dashboard_summary(conn)
    conn.close()
    print(f"[StudentSync Backend] Dashboard metrics check OK: {summary}\n")


if __name__ == "__main__":
    start_backend_service()
