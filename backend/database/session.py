"""
Database Connection and Session Manager for StudentSync Backend
Uses Python standard library sqlite3 for zero-dependency portability across environments.
"""

import sqlite3
import os
from pathlib import Path
from backend.config.settings import settings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "studentsync_backend.db"


def get_db_connection():
    """Establishes connection to SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialises SQLite database schema."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        hashed_password TEXT NOT NULL,
        college TEXT DEFAULT '',
        gpa_scale INTEGER DEFAULT 10,
        is_active BOOLEAN DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Todos table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS todos (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        subject TEXT DEFAULT '',
        priority TEXT DEFAULT 'medium',
        due_date TEXT DEFAULT '',
        completed BOOLEAN DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Subjects table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        name TEXT NOT NULL,
        code TEXT DEFAULT '',
        teacher TEXT DEFAULT '',
        credits INTEGER DEFAULT 3,
        attended INTEGER DEFAULT 0,
        bunked INTEGER DEFAULT 0,
        room TEXT DEFAULT '',
        color TEXT DEFAULT '#2563EB',
        emoji TEXT DEFAULT '📚'
    );
    """)

    # Assignments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        title TEXT NOT NULL,
        subject TEXT DEFAULT '',
        due_date TEXT DEFAULT '',
        priority TEXT DEFAULT 'medium',
        status TEXT DEFAULT 'not_started'
    );
    """)

    # Notes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        title TEXT NOT NULL,
        content TEXT DEFAULT '',
        subject TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Habits table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS habits (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        name TEXT NOT NULL,
        icon TEXT DEFAULT '⭐',
        streak INTEGER DEFAULT 0
    );
    """)

    # Diet table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS diet (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        date TEXT NOT NULL,
        meal TEXT DEFAULT 'breakfast',
        name TEXT NOT NULL,
        calories INTEGER DEFAULT 0
    );
    """)

    # Workouts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        date TEXT NOT NULL,
        name TEXT NOT NULL,
        type TEXT DEFAULT 'strength',
        duration INTEGER DEFAULT 30,
        calories INTEGER DEFAULT 200
    );
    """)

    # Sleep table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sleep (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        date TEXT NOT NULL,
        duration REAL DEFAULT 7.5,
        quality INTEGER DEFAULT 3,
        bedtime TEXT DEFAULT '',
        wake_time TEXT DEFAULT ''
    );
    """)

    conn.commit()
    conn.close()


def get_db():
    """Dependency for database connection."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()
