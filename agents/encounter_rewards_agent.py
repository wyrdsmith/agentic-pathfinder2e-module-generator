from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
import textwrap
from pydantic_ai.settings import ModelSettings

def get_encounter_rewards_agent():
    model = OllamaModel(
        'gemma3-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1'),
        settings = ModelSettings(temperature=0.5)
    )

    encounter_rewards_agent = Agent(
        model,
        system_prompt = (
            textwrap.dedent("""
                # Role
                You are an expert Pathfinder 2e Game Master specializing in encounter design.
                # Context
                You are helping rewards for an encounter in a Pathfinder 2e adventure module.
                # Task
                Select the most appropriate or best reward item from the list of available reward items that makes sense for the encounter based on the provided encounter information.
                # Output Format
                Return ONLY the exact name of the selected reward item.
                # Constraints
                - DO NOT invent new reward items.
                - DO NOT select more than one reward item.
                - DO NOT include any explanations or commentary.
                - You MUST select a reward item.
            """)
        )
    )

    return encounter_rewards_agent