from pydantic_ai import Agent
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider

def get_scene_update_npc_names_agent():
    model = OllamaModel(
        'gemma3-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    scene_update_npc_names_agent = Agent(
        model,
        system_prompt = textwrap.dedent("""
            # Role
            You are a highly creative writer and Pathfinder 2e Game Master in the process of adjusting a scene summary to include the names of NPCs that are present in the scene.

            # Task
            Given the scene summary and the existing NPC information, rewrite the scene summary following these guidelines:
            - NPCs are identified using a vague identifier that is the same or similar to the provided NPC vague identifier in the scene summary, update the scene summary to include the NPCs' names.
            - Focus on smoothly integrating the NPC names into the existing narrative, rather than rewriting the scene from scratch.

            # Output Requirements
            Return only the rewritten scene summary.

            # Constraints
            - Do NOT include any information, labels or commentary other than the rewritten scene summary.
            - The rewritten scene summary should be as close to the original summary as possible, changing only what is necessary to meet the guidelines.
        """)
    )
    
    return scene_update_npc_names_agent