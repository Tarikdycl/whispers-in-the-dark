
from app.models.schemas import WorldState
from app.engine.perception import get_visible_objects


def build_world_context(
    world: WorldState,
    available_exits: list[dict],
) -> dict:
    """Build a compact context for the AI Director."""

    visible_objects = get_visible_objects(world)

    objects = [
        {
            "id": obj.id,
            "name": obj.name,
            "properties": obj.properties,
        }
        for obj in visible_objects
    ]

    inventory = [
        {
            "id": obj.id,
            "name": obj.name,
            "properties": obj.properties,
        }
        for object_id in world.inventory
        if (obj := world.objects.get(object_id)) is not None
    ]

    return {
        "scenario_id": world.scenario_id,
        "year": world.year,
        "game_time": (
            world.game_time.isoformat()
            if world.game_time else None
        ),
        "location": world.location,
        "health": world.health,
        "hunger": world.hunger,
        "visible_objects": objects,
        "inventory": inventory,
        "available_exits": available_exits,
        "emotional_state": world.emotional_state.model_dump(),
        "survival": world.survival.model_dump(),
    }
