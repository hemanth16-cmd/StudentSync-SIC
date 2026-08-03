"""
Global State Notifier & Event System for StudentSync Flet App
"""

from typing import Callable, List, Dict, Any
import flet as ft

class AppState:
    current_page: str = "dashboard"
    dark_mode: bool = True
    search_query: str = ""
    page_change_listeners: List[Callable[[str], None]] = []
    theme_change_listeners: List[Callable[[bool], None]] = []
    search_listeners: List[Callable[[str], None]] = []
    toast_listener: Callable[[str, str], None] = None

    @classmethod
    def set_page(cls, page_key: str):
        cls.current_page = page_key
        for listener in cls.page_change_listeners:
            listener(page_key)

    @classmethod
    def toggle_theme(cls) -> bool:
        cls.dark_mode = not cls.dark_mode
        for listener in cls.theme_change_listeners:
            listener(cls.dark_mode)
        return cls.dark_mode

    @classmethod
    def set_search(cls, query: str):
        cls.search_query = query
        for listener in cls.search_listeners:
            listener(query)

    @classmethod
    def show_toast(cls, message: str, message_type: str = "success"):
        if cls.toast_listener:
            cls.toast_listener(message, message_type)
