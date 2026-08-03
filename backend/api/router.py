"""
Central Router Registry for StudentSync Backend Services
"""

from backend.api import auth, todos, academics, lifestyle, analytics


class APIRouterRegistry:
    auth = auth
    todos = todos
    academics = academics
    lifestyle = lifestyle
    analytics = analytics
