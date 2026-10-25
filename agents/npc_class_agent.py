from pydantic_ai import Agent
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider

def get_npc_class_agent():
    model = OllamaModel(
        'gemma3-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    npc_class_agent = Agent(
        model,
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Pathfinder 2e Game Master in the process for creating NPCs for a quest.

            # Task
            Using the provided quest information and npc information, select the most appropriate class based on your judgement for the NPC from the list of available classes and their descriptions.

            # Output Requirements
            Return only the name of the NPC's class exactly as it appears in the provided list.

            # Constraints
            - Do NOT include any labels, information, or commentary other than the NPC's class.
            - Do not make up any information that is not in the quest information or npc information.
            - Do not make up any class that is not in the provided list.
            - The class name MUST match exactly how it is written in the provided list. This is CRITICAL.
        """)
    )
    
    return npc_class_agent