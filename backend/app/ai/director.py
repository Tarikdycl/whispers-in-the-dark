import os
import json

from app.ai.context_builder import build_world_context
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
            - CURRENT PLAYER-VISIBLE WORLD contains the information
            available to the player.
            - Respect the current location, game time, inventory,
            visible objects, and available exits.
            - Do not invent existing object IDs or destination IDs.
            - Never contradict established world facts.
            - Hidden or inaccessible objects cannot be directly
            inspected, picked up, or interacted with.
            - Do not reveal information unavailable to the player.
            - Player actions may fail.
            - Never assume that a proposed action succeeded.

            WORLD OPERATIONS:
            - Interpret the player's natural-language intentions.
            - Supported types: pickup, drop, inspect, move, search.
            SEARCH OPERATIONS:
            - Use search when the player deliberately investigates
            a visible object or searches underneath it.
            - The target_id must be an existing visible object ID.
            - Search may reveal previously hidden objects.
            - Never invent the identity of a hidden object.
            - Do not claim that anything was discovered before
            the Python engine validates the search.
            - For pickup and inspect, use exact object IDs from
            visible_objects or inventory, as appropriate.
            - For drop, use exact object IDs from inventory.
            - For move, use the exact destination ID from
            available_exits.
            - Never invent IDs.
            - A locked exit cannot be traversed.
            - Propose operations; the Python engine determines
            whether they succeed.
            - Multiple operations may be proposed in order.
            - Return an empty operations list when appropriate.
            - Set legacy pickup_object_id to null.
            - Do not narrate an operation as successful before
            engine validation.

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
        world_context = build_world_context(
    world=world,
    available_exits=available_exits,
)

        context = f"""
        SCENARIO:
        {scenario.model_dump_json(indent=2)}

        CURRENT PLAYER-VISIBLE WORLD:
        {json.dumps(world_context, indent=2)}

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

    
    def narrate_result(
        self,
        player_action: str,
        action_results: list[str],
        world_context: dict,
    ) -> str:
        """
        Narrate only confirmed engine results.
        Never modify the world state.
        """

        import json

        instructions = """
        You are the narrator of a survival-horror game.

        Describe only the confirmed outcomes provided.

        RULES:
        - Never invent objects, actions, discoveries, or events.
        - Never contradict the confirmed results.
        - Never claim an unsuccessful action succeeded.
        - Respect the location, historical year and game time.
        - Do not introduce new threats or characters.
        - Use restrained, atmospheric horror prose.
        - Write 1-3 short sentences.
        - Avoid describing the player's emotions.
        - Do not add facts beyond the confirmed results.
        """

        context = {
            "player_action": player_action,
            "confirmed_results": action_results,
            "current_world": world_context,
        }

        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=json.dumps(context),
            max_output_tokens=150,
            store=False,
        )

        narration = response.output_text.strip()

        if not narration:
            raise RuntimeError("Narrator returned empty text.")

        return narration
