from app.models.schemas import WorldState


def pick_up_object(
    world: WorldState,
    object_id: str,
) -> tuple[WorldState, bool, str]:

    updated = world.model_copy(deep=True)

    obj = updated.objects.get(object_id)

    if obj is None:
        return updated, False, "There is no such object."

    if object_id in updated.inventory:
        return updated, False, "You already have it."

    if obj.location != updated.location:
        return updated, False, "It is not within reach."

    # Transfer ownership to player inventory
    updated.inventory.append(object_id)
    obj.location = "inventory"

    return updated, True, f"You take the {obj.name}."