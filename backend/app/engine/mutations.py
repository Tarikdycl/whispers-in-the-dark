from app.models.schemas import (
    WorldState,
    DirectorProposal,
    GameObject,
    GameEvent,
)


def apply_proposal(
    world: WorldState,
    proposal: DirectorProposal,
) -> WorldState:

    # Make a copy so the original state remains unchanged
    updated_world = world.model_copy(deep=True)

    updated_world.turn += 1

    existing_names = {
        obj.name.strip().casefold()
        for obj in updated_world.objects.values()
        if obj.location == updated_world.location
    }

    for discovered in proposal.discovered_objects:

        name = discovered.name.strip()

        # Basic validation: reject empty or duplicate names
        if not name or name.casefold() in existing_names:
            continue

        properties = {
            prop.key: prop.value
            for prop in discovered.properties
        }

        new_object = GameObject(
            name=name,
            location=updated_world.location,
            properties=properties,
        )

        updated_world.objects[new_object.id] = new_object
        existing_names.add(name.casefold())

        updated_world.events.append(
            GameEvent(
                turn=updated_world.turn,
                event_type="object_discovered",
                description=f"Discovered {name}",
                data={"object_id": new_object.id},
            )
        )

    return updated_world