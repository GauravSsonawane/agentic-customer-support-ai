import sqlite3
import json
from datetime import datetime

DB_PATH = "data/agent_state.db"

class SQLiteCheckpointer:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_state (
            thread_id TEXT PRIMARY KEY,
            state_json TEXT,
            updated_at TEXT
        )
        """)
        conn.commit()
        conn.close()

    def load(self, thread_id: str) -> dict | None:
        conn = sqlite3.connect(self.db_path)
        row = conn.execute(
            "SELECT state_json FROM agent_state WHERE thread_id = ?",
            (thread_id,)
        ).fetchone()
        conn.close()

        if not row:
            return None

        return json.loads(row[0])

    def save(self, thread_id: str, state: dict):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
        INSERT INTO agent_state (thread_id, state_json, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(thread_id) DO UPDATE SET
            state_json=excluded.state_json,
            updated_at=excluded.updated_at
        """, (
            thread_id,
            json.dumps(state),
            datetime.utcnow().isoformat()
        ))
        conn.commit()
        conn.close()
