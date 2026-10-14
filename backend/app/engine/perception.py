
from app.models.schemas import WorldState, GameObject


def get_visible_objects(
    world: WorldState,
) -> list[GameObject]:
    """
    Return objects visible in the player's current location.
    Hidden objects are excluded.
    """

    visible_objects = []

    for obj in world.objects.values():

        # Object must be in the current room.
        if obj.location != world.location:
            continue

        # Hidden objects cannot be seen.
        if obj.properties.get("visible", True) is False:
            continue

        visible_objects.append(obj)

    return visible_objects
