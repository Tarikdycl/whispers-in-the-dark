import os

from dotenv import load_dotenv
from openai import OpenAI
from app.ai.context_builder import build_world_context

from app.models.schemas import (
    ScenarioConfig,
    WorldState,
    DirectorProposal,
)

load_dotenv()


class WorldDirector:
    def __init__(self):
        self.client = OpenAI()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    def propose(
    self,
    scenario: ScenarioConfig,
    world: WorldState,
    player_action: str,
    available_exits: list[dict],
) -> DirectorProposal:

        instructions = """
        You are the World Director of an open-ended
        survival-horror simulation.

        Interpret the player's action realistically.

        Respect:
        - The scenario's historical period.
        - Established world facts.
        - Existing objects and their properties.
        - Physical and narrative consistency.

        Player actions may fail.

        Only propose newly discovered objects when plausible.
        Do not recreate objects that already exist.

        You propose events but do not directly modify WorldState.

        WORLD CONSISTENCY:
- Objects in CURRENT WORLD already exist.
- Never contradict their established properties.
- Do not recreate objects that already exist.
- An object with visible=false is hidden.
- Do not reveal hidden objects unless the player's
  investigation could reasonably discover them.
- Do not claim that a visible existing object is absent.
- A player's attempt to move does not prove that
  movement succeeded.
- Never narrate a successful inventory transfer
  unless it has been confirmed by the engine.

WORLD OPERATIONS:
- Interpret the player's natural-language intentions.
- Propose operations using the operations field.
- Supported types: pickup, drop, inspect.
- Use exact object IDs from CURRENT WORLD.
- Never invent IDs.
- If an object does not exist, do not create a
  fake operation for it.
- Multiple operations may be proposed in order.
- Return an empty operations list when appropriate.
- Set legacy pickup_object_id to null.
- Do not claim an operation succeeded before validation.
- Only describe observable facts in narration.
- Keep narration short and matter-of-fact.
- Supported types: pickup, drop, inspect, move.
- For movement, use the "move" operation.
- The target_id must match an exact destination ID
  from AVAILABLE EXITS.
- Never invent destination IDs.
- A locked exit cannot be traversed.
- Do not claim movement succeeded before validation.

                NARRATION STYLE:
        - Use restrained, detached, matter-of-fact prose.
        - Normally write 1-3 short sentences.
        - Prefer 12-35 words total.
        - Do not describe every detail of a room.
        - Reveal information gradually as the player investigates.
        - Do not explain hidden events, motivations, or threats.
        - Never describe emotions on behalf of the player.
        - Avoid phrases such as "you feel terrified",
        "a chill runs down your spine", or "ominous presence".
        - Do not force suspense into every action.
        - Ordinary actions may have ordinary consequences.  
        - Never introduce a major event merely for dramatic effect.
        - Describe only information available to the player.
        """

        context = f"""
            SCENARIO:
            {scenario.model_dump_json(indent=2)}

            CURRENT WORLD:
            {world.model_dump_json(indent=2)}

            AVAILABLE EXITS:
            {available_exits}

            PLAYER ACTION:
            {player_action}
            """

        response = self.client.responses.parse(
            model=self.model,
            instructions=instructions,
            input=context,
            text_format=DirectorProposal,
            store=False,
        )

        if response.output_parsed is None:
            raise RuntimeError(
                "The model did not return a valid DirectorProposal."
            )

        return response.output_parsed