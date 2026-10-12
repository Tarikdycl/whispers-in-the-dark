
from app.ai.director import WorldDirector
from app.engine.world import create_world


world = create_world("city")
director = WorldDirector()

print("World:", world.scenario_id)
print("Location:", world.location)

action = input("\nWhat do you do? ")

proposal = director.propose(world, action)

print("\n--- NARRATION ---")
print(proposal.narration)

print("\n--- STRUCTURED PROPOSAL ---")
print(proposal.model_dump_json(indent=2))

print("\n--- IMPORTANT ---")
print("This proposal has NOT modified WorldState.")
