from pydantic_ai import Agent
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider

def get_scene_social_npc_update_agent():
    model = OllamaModel(
        'gemma3-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    scene_social_npc_update_agent = Agent(
        model,
        system_prompt = textwrap.dedent("""
            # Role
            You are a highly creative writer and Pathfinder 2e Game Master in the process of adjusting a scene with a social encounter for a quest.

            # Task
            The provided scene summary is supposed to contain a social encounter, but prior agents have marked it as missing an NPC for the
            player characters to interact with. Rewrite the scene summary to include an NPC for the social encounter.

            # Output Requirements
            Return only the rewritten scene summary.

            # Constraints
            - Do NOT include any information, labels or commentary other than the rewritten scene summary.
            - Do NOT name the NPC, use a vague identifier to refer to them (e.g. "the guard", "the innkeeper", etc.)
            - Do NOT make up any new information, only use the information provided in the scene summary.
            - The rewritten scene summary should be as close to the original scene summary as possible while including an NPC for the player
              characters to interact with.
        """)
    )
    
    return scene_social_npc_update_agent