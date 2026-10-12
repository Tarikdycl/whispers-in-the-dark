import sqlite3
from pathlib import Path

DATABASE_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "game.db"
)


def get_connection(db_path=DATABASE_PATH):
    db_path = Path(db_path)

    db_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database(db_path=DATABASE_PATH):
    with get_connection(db_path) as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                scenario_id TEXT NOT NULL,
                world_state TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',

                FOREIGN KEY (session_id)
                    REFERENCES sessions(id)
                    ON DELETE CASCADE,

                UNIQUE(session_id, id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS connections (
                session_id TEXT NOT NULL,
                from_location TEXT NOT NULL,
                to_location TEXT NOT NULL,
                locked INTEGER NOT NULL DEFAULT 0
                    CHECK(locked IN (0, 1)),

                PRIMARY KEY (
                    session_id,
                    from_location,
                    to_location
                ),

                FOREIGN KEY (session_id, from_location)
                    REFERENCES locations(session_id, id)
                    ON DELETE CASCADE,

                FOREIGN KEY (session_id, to_location)
                    REFERENCES locations(session_id, id)
                    ON DELETE CASCADE,

                CHECK(from_location != to_location)
            )
        """)