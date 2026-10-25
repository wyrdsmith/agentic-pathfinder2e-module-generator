from pydantic_ai import Agent
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider

def get_npc_scene_role_agent():
    model = OllamaModel(
        'gemma4-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    npc_scene_role_agent = Agent(
        model,
        system_prompt = textwrap.dedent("""
            # Role
            You are a highly creative writer and Pathfinder 2e Game Master in the process for creating NPCs for a quest.

            # Task
            Using the provided quest information, act summary, scene summary, and npc information, write a detailed description of the role the NPC plays in the scene.

            # Output Requirements
            Return only the NPC's scene role.

            # Constraints
            - Do NOT include any labels, information, or commentary other than the NPC's scene role.
            - Do not make up any information that is not in the quest information, act summary, scene summary, or npc information.
        """)
    )
    
    return npc_scene_role_agent