from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.ai.director import WorldDirector
from app.engine.actions import pick_up_object
from app.engine.mutations import apply_proposal
from app.engine.timeline import process_timeline
from app.engine.world import create_world, load_scenario
from app.models.schemas import GameEvent
from app.storage.database import initialize_database
from app.storage.graph import add_location
from app.storage.sessions import load_session, save_session

router = APIRouter(prefix="/game", tags=["Game"])


class StartRequest(BaseModel):
    scenario_id: str


class ActionRequest(BaseModel):
    session_id: str
    action: str = Field(min_length=1)


@router.post("/start")
def start_game(request: StartRequest):
    try:
        world = create_world(request.scenario_id)
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail="Scenario not found") from exc

    initialize_database()
    session_id = save_session(world)

    add_location(
        session_id=session_id,
        name=world.location,
        description="Starting location",
    )

    return {
        "session_id": session_id,
        "world": world.model_dump(),
        "narration": (
            f"You find yourself in {world.location}. "
            "What do you do?"
        ),
    }


@router.post("/action")
def perform_action(request: ActionRequest):
    try:
        world = load_session(request.session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Session not found") from exc

    scenario = load_scenario(world.scenario_id)
    director = WorldDirector()

    proposal = director.propose(
        scenario=scenario,
        world=world,
        player_action=request.action,
    )

    updated_world = apply_proposal(world, proposal)
    pickup_result = None

    if proposal.pickup_object_id is not None:
        updated_world, success, pickup_result = pick_up_object(
            updated_world,
            proposal.pickup_object_id,
        )

        if success:
            updated_world.events.append(
                GameEvent(
                    turn=updated_world.turn,
                    event_type="object_picked_up",
                    description=pickup_result,
                    data={"object_id": proposal.pickup_object_id},
                )
            )

    previous_event_count = len(updated_world.events)
    updated_world = process_timeline(updated_world)
    timeline_events = updated_world.events[previous_event_count:]

    save_session(updated_world, session_id=request.session_id)

    # A proposed narration is not guaranteed to reflect validated actions.
    # On a pickup turn, use the engine's authoritative outcome instead.
    # Any timeline events are appended so they are not silently omitted.
    if proposal.pickup_object_id is not None:
        narration = pickup_result or "Nothing is taken."
    else:
        narration = proposal.narration

    if timeline_events:
        narration += "\n\n" + "\n".join(
            event.description for event in timeline_events
        )

    return {
        "session_id": request.session_id,
        "narration": narration,
        "world": updated_world.model_dump(),
    }


@router.get("/{session_id}")
def get_game(session_id: str):
    try:
        world = load_session(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Session not found") from exc

    return {
        "session_id": session_id,
        "world": world.model_dump(),
    }
