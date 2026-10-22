
from typing import Any, Literal
from uuid import uuid4
from datetime import datetime

from pydantic import BaseModel, Field, model_validator


# ----------------------------------------
# WORLD OBJECTS & EVENTS
# ----------------------------------------

class GameObject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    location: str
    properties: dict[str, Any] = Field(default_factory=dict)


class GameEvent(BaseModel):
    turn: int
    event_type: str
    description: str
    data: dict[str, Any] = Field(default_factory=dict)


# ----------------------------------------
# PLAYER EMOTIONAL STATE
# ----------------------------------------

class EmotionalState(BaseModel):
    fear: int = Field(default=15, ge=0, le=100)
    stress: int = Field(default=10, ge=0, le=100)
    composure: int = Field(default=85, ge=0, le=100)
    hope: int = Field(default=70, ge=0, le=100)


# ----------------------------------------
# PLAYER SURVIVAL STATE
# ----------------------------------------

class SurvivalState(BaseModel):
    alive: bool = True
    escaped: bool = False
    threat_active: bool = False

    @model_validator(mode="after")
    def validate_outcome(self):
        if not self.alive and self.escaped:
            raise ValueError(
                "A player cannot be both dead and escaped."
            )
        return self


# ----------------------------------------
# AUTHORITATIVE WORLD STATE
# ----------------------------------------

class WorldState(BaseModel):
    scenario_id: str
    year: int
    location: str

    current_location_id: str | None = None
    game_time: datetime | None = None

    # Physical condition
    health: int = Field(default=100, ge=0, le=100)
    hunger: int = Field(default=0, ge=0, le=100)

    # Psychological condition
    emotional_state: EmotionalState = Field(
        default_factory=EmotionalState
    )

    # Survival and game outcome
    survival: SurvivalState = Field(
        default_factory=SurvivalState
    )

    turn: int = 0

    # World entities
    objects: dict[str, GameObject] = Field(
        default_factory=dict
    )

    inventory: list[str] = Field(
        default_factory=list
    )

    events: list[GameEvent] = Field(
        default_factory=list
    )

    # Scenario-specific state
    flags: dict[str, Any] = Field(
        default_factory=dict
    )


# ----------------------------------------
# SCENARIO CONFIGURATION
# ----------------------------------------

class ScenarioConfig(BaseModel):
    id: str
    name: str
    year: int
    setting: str
    starting_location: str
    description: str

    technology: list[str] = Field(
        default_factory=list
    )

    threats: list[str] = Field(
        default_factory=list
    )

    rules: list[str] = Field(
        default_factory=list
    )


# ----------------------------------------
# AI DIRECTOR STRUCTURED OUTPUTS
# ----------------------------------------

class ObjectProperty(BaseModel):
    key: str
    value: str


class DiscoveredObject(BaseModel):
    name: str
    description: str
    properties: list[ObjectProperty]


class WorldOperation(BaseModel):
    type: Literal[
        "pickup",
        "drop",
        "inspect",
        "move",
        "search",
    ]

    target_id: str | None
    parameters: list[ObjectProperty]


class DirectorProposal(BaseModel):
    narration: str
    discovered_objects: list[DiscoveredObject]
    reasoning_summary: str
    pickup_object_id: str | None
    operations: list[WorldOperation]
