
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


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


class WorldState(BaseModel):
    scenario_id: str
    year: int
    location: str

    health: int = Field(default=100, ge=0, le=100)
    hunger: int = Field(default=0, ge=0, le=100)
    turn: int = 0

    objects: dict[str, GameObject] = Field(default_factory=dict)
    inventory: list[str] = Field(default_factory=list)
    events: list[GameEvent] = Field(default_factory=list)

    flags: dict[str, Any] = Field(default_factory=dict)

class ScenarioConfig(BaseModel):
    id: str
    name: str
    year: int
    setting: str
    starting_location: str
    description: str

    technology: list[str] = Field(default_factory=list)
    threats: list[str] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)

class ObjectProperty(BaseModel):
    key: str
    value: str


class DiscoveredObject(BaseModel):
    name: str
    description: str
    properties: list[ObjectProperty]


class DirectorProposal(BaseModel):
    narration: str
    discovered_objects: list[DiscoveredObject]
    reasoning_summary: str
    pickup_object_id: str | None = None