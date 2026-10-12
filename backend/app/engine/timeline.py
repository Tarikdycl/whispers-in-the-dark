import json
from pathlib import Path

from app.models.schemas import GameEvent, WorldState


TIMELINE_DIR = (
    Path(__file__).resolve().parent.parent / "scenarios"
)


def process_timeline(world: WorldState) -> WorldState:
    updated = world.model_copy(deep=True)

    timeline_path = (
        TIMELINE_DIR
        / f"{updated.scenario_id}_timeline.json"
    )

    if not timeline_path.exists():
        return updated

    with timeline_path.open(encoding="utf-8") as file:
        timeline = json.load(file)

    triggered = set(
        updated.flags.get("triggered_events", [])
    )

    for event in timeline["events"]:
        event_id = event["id"]

        if event_id in triggered:
            continue

        if updated.turn < event["trigger_turn"]:
            continue

        if event_id == "generator_failure":
            if updated.flags.get("generator_repaired"):
                outcome = "Generator remains operational."
            else:
                updated.flags["power_on"] = False
                outcome = "The emergency generator fails."

        elif event_id == "room_3_bomb":
            bomb_disabled = updated.flags.get(
                "bomb_disabled", False
            )
            bomb_location = updated.flags.get(
                "bomb_location", "room_3"
            )

            if bomb_disabled:
                outcome = "The bomb does not detonate."
            elif bomb_location == "room_3":
                updated.flags["room_3_destroyed"] = True
                outcome = "An explosion destroys Room 3."
            else:
                outcome = (
                    f"The bomb detonates at {bomb_location}."
                )

        else:
            continue

        updated.events.append(
            GameEvent(
                turn=updated.turn,
                event_type=event["type"],
                description=outcome,
                data={"timeline_event_id": event_id},
            )
        )

        triggered.add(event_id)

    updated.flags["triggered_events"] = sorted(triggered)

    return updated