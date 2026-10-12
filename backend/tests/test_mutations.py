from app.engine.world import create_world
from app.engine.mutations import apply_proposal
from app.models.schemas import DirectorProposal, DiscoveredObject


def test_discovered_object_is_added():
    world = create_world("hospital")

    proposal = DirectorProposal(
        narration="You find a flashlight.",
        discovered_objects=[
            DiscoveredObject(
                name="Flashlight",
                description="An old flashlight.",
                properties=[],
            )
        ],
        reasoning_summary="A flashlight is plausible.",
    )

    updated = apply_proposal(world, proposal)

    assert len(updated.objects) == 1
    assert updated.turn == 1
    assert len(updated.events) == 1

    # Original world must remain unchanged
    assert len(world.objects) == 0
    assert world.turn == 0