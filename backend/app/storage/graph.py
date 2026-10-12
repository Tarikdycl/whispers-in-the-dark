from uuid import uuid4

from app.storage.database import (
    get_connection,
    DATABASE_PATH,
)


def add_location(
    session_id: str,
    name: str,
    description: str = "",
    db_path=DATABASE_PATH,
) -> str:

    if not name.strip():
        raise ValueError("Location name cannot be empty")

    location_id = str(uuid4())

    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO locations (
                id, session_id, name, description
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                location_id,
                session_id,
                name,
                description,
            ),
        )

    return location_id


def connect_locations(
    session_id: str,
    from_id: str,
    to_id: str,
    locked: bool = False,
    db_path=DATABASE_PATH,
):
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO connections (
                session_id,
                from_location,
                to_location,
                locked
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                session_id,
                from_id,
                to_id,
                int(locked),
            ),
        )


def get_neighbors(
    session_id: str,
    location_id: str,
    db_path=DATABASE_PATH,
):
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT
                l.id,
                l.name,
                l.description,
                c.locked

            FROM connections AS c

            JOIN locations AS l
                ON l.session_id = c.session_id
                AND l.id = c.to_location

            WHERE c.session_id = ?
              AND c.from_location = ?
            """,
            (session_id, location_id),
        ).fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "locked": bool(row[3]),
        }
        for row in rows
    ]