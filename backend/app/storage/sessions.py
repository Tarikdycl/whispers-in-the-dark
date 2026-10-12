from uuid import uuid4

from app.models.schemas import WorldState
from app.storage.database import (
    get_connection,
    DATABASE_PATH,
)


def save_session(
    world: WorldState,
    session_id: str | None = None,
    db_path=DATABASE_PATH,
) -> str:

    if session_id is None:
        session_id = str(uuid4())

    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO sessions (
                id, scenario_id, world_state
            )
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                scenario_id = excluded.scenario_id,
                world_state = excluded.world_state,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                session_id,
                world.scenario_id,
                world.model_dump_json(),
            ),
        )

    return session_id


def load_session(
    session_id: str,
    db_path=DATABASE_PATH,
) -> WorldState:

    with get_connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT world_state
            FROM sessions
            WHERE id = ?
            """,
            (session_id,),
        ).fetchone()

    if row is None:
        raise ValueError("Session not found")

    return WorldState.model_validate_json(row[0])