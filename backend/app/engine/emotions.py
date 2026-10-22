
from app.models.schemas import WorldState, GameEvent


EMOTIONAL_EFFECTS = {
    "threat_encountered": {
        "fear": 25,
        "stress": 15,
        "composure": -10,
        "hope": -5,
    },
    "threat_escaped": {
        "fear": -15,
        "stress": -10,
        "composure": 10,
        "hope": 10,
    },
    "safe_room_entered": {
        "fear": -10,
        "stress": -10,
        "composure": 10,
        "hope": 5,
    },
    "player_injured": {
        "fear": 10,
        "stress": 20,
        "composure": -10,
        "hope": -10,
    },
}


def clamp(value: int) -> int:
    """Keep emotional values between 0 and 100."""
    return max(0, min(100, value))


def apply_emotional_event(
    world: WorldState,
    event_type: str,
) -> WorldState:
    """
    Apply the emotional effects of one verified world event.
    Unknown events leave the state unchanged.
    """

    effects = EMOTIONAL_EFFECTS.get(event_type)

    if effects is None:
        return world

    updated = world.model_copy(deep=True)
    emotions = updated.emotional_state

    for attribute, change in effects.items():
        current_value = getattr(emotions, attribute)
        setattr(
            emotions,
            attribute,
            clamp(current_value + change),
        )

    updated.events.append(
        GameEvent(
            turn=updated.turn,
            event_type="emotional_change",
            description=(
                f"Emotional state changed after {event_type}."
            ),
            data={
                "cause": event_type,
                "effects": effects,
                "state": emotions.model_dump(),
            },
        )
    )

    return updated


def process_emotional_events(
    world: WorldState,
    new_events: list[GameEvent],
) -> WorldState:
    """
    Apply emotional effects only for newly created,
    verified world events.
    """
    updated = world

    for event in new_events:
        if event.event_type in EMOTIONAL_EFFECTS:
            updated = apply_emotional_event(
                updated,
                event.event_type,
            )

    return updated

