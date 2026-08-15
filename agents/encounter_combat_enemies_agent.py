from typing import List
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from models.quest import Quest
from tools.encounter_tools import get_possible_enemies
import textwrap

def get_combat_encounter_creation_agent():
    model = OllamaModel(
        'gemma-quest',
        output_type = NativeOutput(List[str]),
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    encounter_agent = Agent(
        model,
        deps_type = Quest,
        system_prompt = (
            textwrap.dedent("""
                # Role
                You are an expert Pathfinder 2e Game Master specializing in combat encounter design.
                # Context
                You are currently in the encounter generation phase of a quest generation pipeline. The encounter experience budget and threat level have already been mathematically balanced for you.
                # Task
                Select appropriate enemies for the scene that fit the provided Experience Budget.
                # Constraints
                - DO NOT invent new enemies.
                - DO NOT exceed the Experience Budget.
            """)
        )
    )

    encounter_agent.tool(get_possible_enemies)
    encounter_agent.tool(get_quest_theme)
    encounter_agent.tool(get_quest_setting)
    encounter_agent.tool(get_quest_summary)
    encounter_agent.tool(get_act_summary)
    
    return encounter_agent