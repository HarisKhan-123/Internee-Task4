"""
Lightweight SQLite persistence: one row per intern "session" (identified
by a browser-set cookie), holding their profile, the paths that were
generated for them, which path they're following, and a timestamped
completion record per learning step. This is what makes "track progress
over time" real rather than something that resets on refresh.
"""

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

DB_PATH = "career_recommender.db"


def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                profile_json TEXT NOT NULL DEFAULT '{}',
                paths_json TEXT NOT NULL DEFAULT '[]',
                selected_path_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                session_id TEXT NOT NULL,
                step_id TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                PRIMARY KEY (session_id, step_id)
            )
        """)


@contextmanager
def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _now():
    return datetime.now(timezone.utc).isoformat()


def create_session():
    session_id = str(uuid.uuid4())
    with _connect() as conn:
        conn.execute(
            "INSERT INTO sessions (id, created_at, updated_at) VALUES (?, ?, ?)",
            (session_id, _now(), _now()),
        )
    return session_id


def save_recommendation(session_id, profile, paths):
    with _connect() as conn:
        conn.execute(
            """UPDATE sessions
               SET profile_json = ?, paths_json = ?, selected_path_id = NULL,
                   updated_at = ?
               WHERE id = ?""",
            (json.dumps(profile), json.dumps(paths), _now(), session_id),
        )
        # a fresh recommendation clears old progress for this session
        conn.execute("DELETE FROM progress WHERE session_id = ?", (session_id,))


def select_path(session_id, path_id):
    with _connect() as conn:
        conn.execute(
            "UPDATE sessions SET selected_path_id = ?, updated_at = ? WHERE id = ?",
            (path_id, _now(), session_id),
        )


def set_step_progress(session_id, step_id, completed):
    with _connect() as conn:
        if completed:
            conn.execute(
                """INSERT INTO progress (session_id, step_id, completed_at)
                   VALUES (?, ?, ?)
                   ON CONFLICT(session_id, step_id) DO NOTHING""",
                (session_id, step_id, _now()),
            )
        else:
            conn.execute(
                "DELETE FROM progress WHERE session_id = ? AND step_id = ?",
                (session_id, step_id),
            )
        conn.execute(
            "UPDATE sessions SET updated_at = ? WHERE id = ?", (_now(), session_id)
        )


def get_state(session_id):
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if row is None:
            return None
        progress_rows = conn.execute(
            "SELECT step_id, completed_at FROM progress WHERE session_id = ?",
            (session_id,),
        ).fetchall()

    return {
        "session_id": row["id"],
        "profile": json.loads(row["profile_json"]),
        "paths": json.loads(row["paths_json"]),
        "selected_path_id": row["selected_path_id"],
        "progress": {r["step_id"]: r["completed_at"] for r in progress_rows},
    }
