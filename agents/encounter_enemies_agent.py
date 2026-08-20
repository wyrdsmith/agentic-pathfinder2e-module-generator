from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
import textwrap
from pydantic_ai.settings import ModelSettings

def get_encounter_enemy_agent():
    model = OllamaModel(
        'gemma3-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1'),
        settings = ModelSettings(temperature=0.5)
    )

    encounter_agent = Agent(
        model,
        system_prompt = (
            textwrap.dedent("""
                # Role
                You are an expert Pathfinder 2e Game Master specializing in combat encounter design.
                # Context
                You are helping build a combat encounter in a scene for a Pathfinder 2e adventure module.
                # Task
                Select the most appropriate enemy from the list of available enemies that makes sense for the scene based on the provided quest, act and scene information.
                # Output Format
                Return ONLY the name of the selected enemy.
                # Constraints
                - DO NOT invent new enemies.
                - DO NOT select more than one enemy.
                - DO NOT include any explanations or commentary.
                - You MUST select an enemy.
            """)
        )
    )

    return encounter_agent