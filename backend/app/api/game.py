
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.ai.director import WorldDirector
from app.engine.actions import resolve_operations
from app.engine.clock import advance_time, resolve_duration
from app.engine.mutations import apply_proposal
from app.engine.seeding import seed_world
from app.engine.timeline import process_timeline
from app.engine.world import create_world, load_scenario
from app.storage.database import initialize_database
from app.storage.graph import (
    add_location,
    connect_locations,
    get_neighbors,
)
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
        raise HTTPException(
            status_code=404,
            detail="Scenario not found",
        ) from exc

    # Initialize the game clock if necessary.
    if world.game_time is None:
        world.game_time = datetime(world.year, 10, 10, 22, 0)

    # Initialize database and starting objects.
    initialize_database()
    world = seed_world(world)

    # Create a new persistent game session.
    session_id = save_session(world)

    # Create the starting location.
    starting_location_id = add_location(
        session_id=session_id,
        name=world.location,
        description="Starting location.",
    )

    world.current_location_id = starting_location_id

    # Create the initial hospital location graph.
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

        # Hospital Room <-> Hallway
        connect_locations(
            session_id,
            starting_location_id,
            hallway_id,
        )

        connect_locations(
            session_id,
            hallway_id,
            starting_location_id,
        )

        # Hallway <-> Nurse Station
        connect_locations(
            session_id,
            hallway_id,
            nurse_station_id,
        )

        connect_locations(
            session_id,
            nurse_station_id,
            hallway_id,
        )

    # Save the world with its starting location ID.
    save_session(world, session_id=session_id)

    return {
        "session_id": session_id,
        "world": world.model_dump(mode="json"),
        "narration": (
            f"You find yourself in {world.location}. What do you do?"
        ),
        "response_time": world.game_time.isoformat(),
    }


@router.post("/action")
def perform_action(request: ActionRequest):
    # Load the existing world.
    try:
        world = load_session(request.session_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        ) from exc

    # Initialize the game clock if necessary.
    if world.game_time is None:
        world.game_time = datetime(world.year, 10, 10, 22, 0)

    action_time = world.game_time

    # Load the scenario configuration.
    scenario = load_scenario(world.scenario_id)

    # Retrieve available exits from SQLite.
    available_exits = (
        get_neighbors(
            request.session_id,
            world.current_location_id,
        )
        if world.current_location_id
        else []
    )

    # Ask the AI Director to interpret the action.
    director = WorldDirector()

    proposal = director.propose(
        scenario=scenario,
        world=world,
        player_action=request.action,
        available_exits=available_exits,
    )

    # Apply discoveries and resolve supported operations.
    updated_world = apply_proposal(world, proposal)

    updated_world, action_results = resolve_operations(
    updated_world,
    proposal.operations,
    session_id=request.session_id,
)

    # Calculate the action duration.
    try:
        duration_seconds = resolve_duration(request.action)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    # Advance the fictional game clock.
    updated_world = advance_time(
        updated_world,
        duration_seconds,
    )

    # Process scheduled events (currently turn-based).
    updated_world = process_timeline(updated_world)

    # Persist the updated world.
    save_session(
        updated_world,
        session_id=request.session_id,
    )

    # Use validated operation results when available.
    narration = (
        "\n".join(action_results)
        if action_results
        else proposal.narration
    )

    return {
        "session_id": request.session_id,
        "duration_seconds": duration_seconds,
        "action_time": action_time.isoformat(),
        "response_time": updated_world.game_time.isoformat(),
        "narration": narration,
        "world": updated_world.model_dump(mode="json"),
    }


@router.get("/{session_id}")
def get_game(session_id: str):
    try:
        world = load_session(session_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        ) from exc

    return {
        "session_id": session_id,
        "world": world.model_dump(mode="json"),
    }
