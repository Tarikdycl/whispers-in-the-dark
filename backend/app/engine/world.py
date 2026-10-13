
import json
from pathlib import Path

from app.models.schemas import ScenarioConfig, WorldState

from datetime import datetime

SCENARIO_START_TIMES = {
    "hospital": datetime(1980, 10, 10, 22, 0),
    "forest": datetime(1870, 10, 10, 21, 0),
    "city": datetime(2080, 10, 10, 20, 0),
}


SCENARIOS_DIR = Path(__file__).resolve().parent.parent / "scenarios"


def load_scenario(scenario_id: str) -> ScenarioConfig:
    """Load and validate a scenario from its JSON file."""

    if not scenario_id or not scenario_id.isidentifier():
        raise ValueError("Invalid scenario ID")

    file_path = SCENARIOS_DIR / f"{scenario_id}.json"

    if not file_path.is_file():
        raise FileNotFoundError(
            f"Scenario '{scenario_id}' does not exist."
        )

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    scenario = ScenarioConfig.model_validate(data)

    if scenario.id != scenario_id:
        raise ValueError("Scenario ID does not match the filename")

    return scenario


def create_world(scenario_id: str) -> WorldState:
    """Create a new game state from a scenario configuration."""

    scenario = load_scenario(scenario_id)
    

    return WorldState(
        scenario_id=scenario.id,
        year=scenario.year,
        game_time=SCENARIO_START_TIMES.get(scenario.id),
        location=scenario.starting_location,
    )
