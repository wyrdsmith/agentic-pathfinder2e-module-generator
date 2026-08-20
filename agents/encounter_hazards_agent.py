from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
import textwrap
from pydantic_ai.settings import ModelSettings

def get_encounter_hazard_agent():
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
                You are helping build a hazard encounter in a scene for a Pathfinder 2e adventure module.
                # Task
                Select the most appropriate hazard from the list of available hazards that makes sense for the scene based on the provided quest, act and scene information.
                # Output Format
                Return ONLY the name of the selected hazard.
                # Constraints
                - DO NOT invent new hazards.
                - DO NOT select more than one hazard.
                - DO NOT include any explanations or commentary.
                - You MUST select an hazard.
            """)
        )
    )

    return encounter_agent