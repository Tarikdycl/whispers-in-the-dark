"""Calculate and advance fictional time independently of the player's real-world clock."""
import re
from datetime import timedelta
from app.models.schemas import WorldState

DURATION_PATTERN = re.compile(
    r"\b(?:for\s+)?(\d+(?:\.\d+)?)\s*(seconds?|minutes?|hours?|days?)\b",
    re.IGNORECASE,
)
UNIT_SECONDS = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}


def resolve_duration(action: str, operations=None) -> int:
    """Return the in-game action duration in seconds."""
    match = DURATION_PATTERN.search(action)
    if match:
        amount = float(match.group(1))
        unit = match.group(2).lower().rstrip("s")
        if not 0 < amount <= 100000:
            raise ValueError("Invalid action duration")
        return max(1, round(amount * UNIT_SECONDS[unit]))

    action = action.lower()
    if re.search(r"\b(sleep|rest|nap)\b", action):
        return 8 * 3600
    if re.search(r"\b(search|explore)\b", action):
        return 5 * 60
    if re.search(r"\b(walk|move|leave|enter)\b|go to", action):
        return 60
    if re.search(r"\b(pick up|grab|drop|take)\b", action):
        return 10
    return 60


def advance_time(world: WorldState, duration_seconds: int) -> WorldState:
    if duration_seconds < 0:
        raise ValueError("Duration cannot be negative")
    updated = world.model_copy(deep=True)
    if updated.game_time is None:
        raise ValueError("Game clock is not initialized")
    updated.game_time += timedelta(seconds=duration_seconds)
    return updated
