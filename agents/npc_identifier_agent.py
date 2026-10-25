from pydantic_ai import Agent
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider

def get_npc_identifier_agent():
    model = OllamaModel(
        'gemma3-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    npc_identifier_agent = Agent(
        model,
        system_prompt = textwrap.dedent("""
            # Role
            You are a Pathfinder 2e Game Master working on the first step of creating NPCs for a quest.

            # Task
            Given a scene summary and scene location, come up with a one to four word description of the NPC that will be present in that scene and interact with the party.
            - The description should be a vague identifier of the NPC, e.g. "a shopkeeper", "the elder", "the village mayor", "a guard".
            - The description should be based on the scene summary and scene location.

            # Output Requirements
            Return only the NPC's descriptive identifier.

            # Constraints
            - Do NOT include any information other than the NPC's descriptive identifier.
            - The NPC's descriptive identifier MUST ONLY be one to four words. This is important.
        """)
    )
    
    return npc_identifier_agent