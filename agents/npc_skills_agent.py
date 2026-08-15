from pydantic_ai import Agent, RunContext
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from typing import List
from models.quest import Quest
from tools.npc_tools import get_skills_with_descriptions

def get_npc_skills_creation_agent():
    model = OllamaModel(
        'gemma-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
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

            # Constraints
            - You MUST use the `get_skills_with_descriptions` tool to see all available skills and their descriptions.
            - Do not invent skills that are not on the provided list.
            - Do not provide explanations or other text.
        """)
    )
    
    npcs_agent.tool_plain(get_skills_with_descriptions)
    
    return npcs_agent