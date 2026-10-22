from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.ai.context_builder import build_world_context
from app.ai.director import WorldDirector
from app.engine.actions import resolve_operations
from app.engine.clock import advance_time, resolve_duration
from app.engine.emotions import process_emotional_events
from app.engine.mutations import apply_proposal
from app.engine.seeding import seed_world
from app.engine.timeline import process_timeline
from app.engine.world import create_world, load_scenario
from app.storage.database import initialize_database
from app.storage.graph import add_location, connect_locations, get_neighbors
from app.storage.sessions import load_session, save_session

router = APIRouter(prefix="/game", tags=["Game"])


class StartRequest(BaseModel):
    scenario_id: str


class ActionRequest(BaseModel):
    session_id: str
    action: str = Field(min_length=1)


def build_public_world(world, session_id: str) -> dict:
    """Return player-facing state without leaking undiscovered objects."""
    exits = (
        get_neighbors(session_id, world.current_location_id)
        if world.current_location_id else []
    )
    public = world.model_dump(mode="json")
    public["objects"] = {
        object_id: obj.model_dump(mode="json")
        for object_id, obj in world.objects.items()
        if obj.location == "inventory"
        or (
            obj.location == world.location
            and obj.properties.get("visible", True) is not False
        )
    }
    public["available_exits"] = exits
    # Event metadata can expose hidden discoveries and future triggers.
    public.pop("events", None)
    public.pop("flags", None)
    return public


@router.post("/start")
def start_game(request: StartRequest):
    try:
        world = create_world(request.scenario_id)
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail="Scenario not found") from exc

    if world.game_time is None:
        world.game_time = datetime(world.year, 10, 10, 22, 0)

    initialize_database()
    world = seed_world(world)
    session_id = save_session(world)
    starting_id = add_location(
        session_id=session_id,
        name=world.location,
        description="Starting location.",
    )
    world.current_location_id = starting_id

    if world.scenario_id == "hospital":
        hallway_id = add_location(
            session_id=session_id,
            name="Hallway",
            description="A long corridor with flickering lights.",
        )
        nurse_station_id = add_location(
            session_id=session_id,
            name="Nurse Station",
            description="An abandoned nurse station.",
        )
        for source, destination in (
            (starting_id, hallway_id),
            (hallway_id, starting_id),
            (hallway_id, nurse_station_id),
            (nurse_station_id, hallway_id),
        ):
            connect_locations(session_id, source, destination)

    save_session(world, session_id=session_id)
    return {
        "session_id": session_id,
        "world": build_public_world(world, session_id),
        "narration": f"You find yourself in {world.location}. What do you do?",
        "response_time": world.game_time.isoformat(),
    }


@router.post("/action")
def perform_action(request: ActionRequest):
    try:
        world = load_session(request.session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Session not found") from exc

    if world.game_time is None:
        world.game_time = datetime(world.year, 10, 10, 22, 0)
    action_time = world.game_time
    scenario = load_scenario(world.scenario_id)
    exits = (
        get_neighbors(request.session_id, world.current_location_id)
        if world.current_location_id else []
    )

    # Check duration before expensive AI work or state mutation.
    try:
        duration_seconds = resolve_duration(request.action)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    director = WorldDirector()
    proposal = director.propose(
        scenario=scenario,
        world=world,
        player_action=request.action,
        available_exits=exits,
    )
    updated_world = apply_proposal(world, proposal)
    updated_world, action_results = resolve_operations(
        updated_world,
        proposal.operations,
        session_id=request.session_id,
    )
    updated_world = advance_time(updated_world, duration_seconds)
    updated_world = process_timeline(updated_world)
    new_events = updated_world.events[len(world.events):]
    updated_world = process_emotional_events(updated_world, new_events)
    save_session(updated_world, session_id=request.session_id)

    narration = "\n".join(action_results) if action_results else "Nothing changes."
    important_discovery = any(
        event.event_type == "object_search"
        and bool(event.data.get("discovered"))
        for event in new_events
    )
    if important_discovery:
        try:
            final_exits = (
                get_neighbors(request.session_id, updated_world.current_location_id)
                if updated_world.current_location_id else []
            )
            context = build_world_context(updated_world, final_exits)
            narration = director.narrate_result(
                player_action=request.action,
                action_results=action_results,
                world_context=context,
            )
        except Exception as exc:
            print(f"AI narration failed: {exc}", flush=True)

    return {
        "session_id": request.session_id,
        "duration_seconds": duration_seconds,
        "action_time": action_time.isoformat(),
        "response_time": updated_world.game_time.isoformat(),
        "narration": narration,
        "world": build_public_world(updated_world, request.session_id),
    }


@router.get("/{session_id}")
def get_game(session_id: str):
    try:
        world = load_session(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Session not found") from exc
    return {
        "session_id": session_id,
        "world": build_public_world(world, session_id),
    }
