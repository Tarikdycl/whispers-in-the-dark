from app.engine.world import create_world, load_scenario
from app.ai.director import WorldDirector

scenario = load_scenario("hospital")
world = create_world("hospital")

director = WorldDirector()

proposal = director.propose(
    scenario=scenario,
    world=world,
    player_action="I look around.",
    available_exits=[]
)

print(proposal.model_dump_json(indent=2))