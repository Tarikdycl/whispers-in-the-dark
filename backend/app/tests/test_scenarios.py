
import pytest

from app.engine.world import create_world, load_scenario


@pytest.mark.parametrize(
    "scenario_id, expected_year",
    [
        ("hospital", 1980),
        ("forest", 1870),
        ("city", 2080),
    ],
)
def test_load_scenarios(scenario_id, expected_year):
    scenario = load_scenario(scenario_id)

    assert scenario.id == scenario_id
    assert scenario.year == expected_year
    assert scenario.starting_location


def test_create_world():
    world = create_world("city")

    assert world.scenario_id == "city"
    assert world.year == 2080
    assert world.health == 100
    assert world.hunger == 0
    assert world.inventory == []


def test_unknown_scenario():
    with pytest.raises(FileNotFoundError):
        load_scenario("unknown")


def test_invalid_scenario_id():
    with pytest.raises(ValueError):
        load_scenario("../secrets")
