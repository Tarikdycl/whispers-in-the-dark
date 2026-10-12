import os

from dotenv import load_dotenv
from openai import OpenAI

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

        OBJECT INTERACTIONS:
- Players may attempt to pick up objects.
- If the player explicitly tries to take an existing object,
  set pickup_object_id to its exact ID from WorldState.
- Never invent an object ID.
- If no pickup is attempted, return null.
- Do not assume an object was successfully picked up.
- The Python engine decides whether the action succeeds.
- Keep narration focused on observable details.
- Avoid announcing a successful pickup before validation.

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