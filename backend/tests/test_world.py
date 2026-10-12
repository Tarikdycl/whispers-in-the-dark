
from app.models.schemas import GameObject, WorldState


def test_dynamic_object():
    world = WorldState(
        scenario_id="city",
        year=2080,
        location="abandoned_shelter",
    )

    phone = GameObject(
        name="Cracked Smartphone",
        location="player_pocket",
        properties={
            "battery": 23,
            "working": True,
        },
    )

    world.objects[phone.id] = phone
    world.inventory.append(phone.id)

    assert phone.id in world.objects
    assert phone.id in world.inventory
    assert world.objects[phone.id].properties["battery"] == 23


def test_isolated_worlds():
    world_a = WorldState(
        scenario_id="forest",
        year=1870,
        location="forest",
    )

    world_b = WorldState(
        scenario_id="city",
        year=2080,
        location="shelter",
    )

    world_a.inventory.append("old_watch")

    assert world_b.inventory == []
