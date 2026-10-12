from app.engine.world import create_world
from app.storage.database import initialize_database
from app.storage.sessions import save_session, load_session


def test_save_and_load_session(tmp_path):

    db_path = tmp_path / "test_game.db"

    initialize_database(db_path)

    world = create_world("hospital")
    world.health = 75
    world.turn = 3

    session_id = save_session(
        world,
        db_path=db_path,
    )

    loaded_world = load_session(
        session_id,
        db_path=db_path,
    )

    assert loaded_world.health == 75
    assert loaded_world.turn == 3
    assert loaded_world.scenario_id == "hospital"


def test_update_existing_session(tmp_path):

    db_path = tmp_path / "test_game.db"

    initialize_database(db_path)

    world = create_world("forest")

    session_id = save_session(
        world,
        db_path=db_path,
    )

    world.health = 50

    save_session(
        world,
        session_id=session_id,
        db_path=db_path,
    )

    loaded_world = load_session(
        session_id,
        db_path=db_path,
    )

    assert loaded_world.health == 50