import sqlite3

import pytest

from app.engine.world import create_world
from app.storage.database import initialize_database
from app.storage.sessions import save_session
from app.storage.graph import (
    add_location,
    connect_locations,
    get_neighbors,
)


def test_world_graph(tmp_path):
    db_path = tmp_path / "test_graph.db"

    initialize_database(db_path)

    world = create_world("hospital")
    session_id = save_session(world, db_path=db_path)

    room_id = add_location(
        session_id,
        "Hospital Room",
        db_path=db_path,
    )

    hallway_id = add_location(
        session_id,
        "Hallway",
        db_path=db_path,
    )

    storage_id = add_location(
        session_id,
        "Storage Room",
        db_path=db_path,
    )

    connect_locations(
        session_id,
        room_id,
        hallway_id,
        db_path=db_path,
    )

    connect_locations(
        session_id,
        hallway_id,
        storage_id,
        locked=True,
        db_path=db_path,
    )

    room_neighbors = get_neighbors(
        session_id,
        room_id,
        db_path=db_path,
    )

    hallway_neighbors = get_neighbors(
        session_id,
        hallway_id,
        db_path=db_path,
    )

    assert len(room_neighbors) == 1
    assert room_neighbors[0]["name"] == "Hallway"
    assert room_neighbors[0]["locked"] is False

    assert len(hallway_neighbors) == 1
    assert hallway_neighbors[0]["name"] == "Storage Room"
    assert hallway_neighbors[0]["locked"] is True


def test_cross_session_connection_rejected(tmp_path):
    db_path = tmp_path / "test_graph.db"
    initialize_database(db_path)

    session_a = save_session(
        create_world("hospital"),
        db_path=db_path,
    )
    session_b = save_session(
        create_world("forest"),
        db_path=db_path,
    )

    room_a = add_location(
        session_a, "Room A", db_path=db_path
    )
    room_b = add_location(
        session_b, "Room B", db_path=db_path
    )

    with pytest.raises(sqlite3.IntegrityError):
        connect_locations(
            session_a,
            room_a,
            room_b,
            db_path=db_path,
        )