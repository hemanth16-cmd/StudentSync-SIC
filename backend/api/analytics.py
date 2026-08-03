"""
Analytics & Dashboard Insights API Router
"""

from backend.database import get_db
from backend.services.analytics_service import AnalyticsService


def get_summary(conn=None):
    if conn is None: conn = next(get_db())
    return AnalyticsService.get_dashboard_summary(conn)
