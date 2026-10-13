from app.models.schemas import GameObject, WorldState


STARTING_OBJECTS = {
    "hospital": [
        {
            "name": "Hospital Bed",
            "properties": {
                "description": "An old metal-framed hospital bed.",
                "portable": False,
                "visible": True,
            },
        },
        {
            "name": "Pillow",
            "properties": {
                "description": "A worn pillow on the bed.",
                "portable": True,
                "visible": True,
            },
        },
        {
            "name": "Blanket",
            "properties": {
                "description": "A thin hospital blanket.",
                "portable": True,
                "visible": True,
            },
        },
        {
            "name": "Window",
            "properties": {
                "description": "A window overlooking the hospital grounds.",
                "portable": False,
                "visible": True,
                "openable": True,
                "locked": True,
            },
        },
        {
            "name": "Small Metal Scalpel",
            "properties": {
                "description": "A surgical instrument underneath the bed.",
                "portable": True,
                "visible": False,
                "hidden_under": "Hospital Bed",
            },
        },
    ],
}


def seed_world(world: WorldState) -> WorldState:
    updated = world.model_copy(deep=True)

    for item in STARTING_OBJECTS.get(world.scenario_id, []):
        obj = GameObject(
            name=item["name"],
            location=updated.location,
            properties=item["properties"].copy(),
        )

        updated.objects[obj.id] = obj

    return updated