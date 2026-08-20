from pydantic_ai import Agent
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from pydantic_ai.settings import ModelSettings
from typing import List

def get_npc_skills_creation_agent():
    model = OllamaModel(
        'gemma3-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1'),
        settings = ModelSettings(temperature=0.5)
    )

    npcs_agent = Agent(
        model,
        output_type = NativeOutput(List[str]),
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Pathfinder 2e Game Master.

            # Task
            Select 3 to 6 appropriate skills for an NPC based on their class and quest role.

            # Output Requirements
            Supply ONLY a list of the selected skill names.

            # Output Format
            Return the skills as a list of strings.

            # Constraints
            - Do not invent skills that are not on the provided list.
            - Do not provide explanations or other text.
        """)
    )
    
    return npcs_agent