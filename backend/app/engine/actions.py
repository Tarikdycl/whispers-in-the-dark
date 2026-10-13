from app.models.schemas import WorldState, WorldOperation, GameEvent


def resolve_operations(
    world: WorldState,
    operations: list[WorldOperation],
) -> tuple[WorldState, list[str]]:

    updated = world.model_copy(deep=True)
    results = []

    for operation in operations:
        object_id = operation.target_id
        obj = updated.objects.get(object_id) if object_id else None

        if obj is None:
            results.append("That object is not available.")
            continue

        if operation.type == "pickup":

            if object_id in updated.inventory:
                results.append(f"You already have the {obj.name}.")
                continue

            if obj.location != updated.location:
                results.append(f"The {obj.name} is out of reach.")
                continue

            if obj.properties.get("portable") in (False, "false"):
                results.append(f"You cannot carry the {obj.name}.")
                continue

            updated.inventory.append(object_id)
            obj.location = "inventory"
            result = f"You take the {obj.name}."

        elif operation.type == "drop":

            if object_id not in updated.inventory:
                results.append(f"You are not carrying the {obj.name}.")
                continue

            updated.inventory.remove(object_id)
            obj.location = updated.location
            result = f"You leave the {obj.name} behind."

        elif operation.type == "inspect":

            if (
                obj.location != updated.location
                and object_id not in updated.inventory
            ):
                results.append(f"You cannot see the {obj.name}.")
                continue

            result = f"{obj.name}: {obj.properties}"

        else:
            results.append("That action is not supported.")
            continue

        updated.events.append(
            GameEvent(
                turn=updated.turn,
                event_type=f"object_{operation.type}",
                description=result,
                data={"object_id": object_id},
            )
        )

        results.append(result)

    return updated, results