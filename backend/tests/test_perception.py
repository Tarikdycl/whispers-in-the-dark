
from app.engine.world import create_world
from app.engine.seeding import seed_world
from app.engine.perception import get_visible_objects


def test_hidden_objects_are_not_visible():

    world = create_world("hospital")
    world = seed_world(world)

    visible = get_visible_objects(world)

    names = {obj.name for obj in visible}

    assert "Hospital Bed" in names
    assert "Pillow" in names
    assert "Small Metal Scalpel" not in names


def test_objects_in_other_rooms_are_not_visible():

    world = create_world("hospital")
    world = seed_world(world)

    world.location = "Hallway"

    visible = get_visible_objects(world)

    assert visible == []
