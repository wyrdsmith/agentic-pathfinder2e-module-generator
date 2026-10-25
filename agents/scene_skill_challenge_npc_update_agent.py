from pydantic_ai import Agent
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider

def get_scene_skill_challenge_npc_update_agent():
    model = OllamaModel(
        'gemma3-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    scene_skill_challenge_npc_update_agent = Agent(
        model,
        system_prompt = textwrap.dedent("""
            # Role
            You are a highly creative writer and Pathfinder 2e Game Master in the process of adjusting a scene with a skill challenge encounter for a quest.

            # Task
            Given the scene summary, scene location, and the existing NPC information, rewrite the scene summary following these guidelines:
            - NPCs are not to participate in the skill challenge in anyway.
            - If the NPCs are enemies, the challenge faced by the party is caused by the NPCs.
            - If the NPCs are allies, they cannot provide support of any kind except in the form of information or narrative guidance.
            - The rewritten scene summary should be as close to the original summary as possible, changing only what is necessary to meet the guidelines.

            # Output Requirements
            Return only the rewritten scene summary.

            # Constraints
            - Do NOT include any information, labels or commentary other than the rewritten scene summary.
            - Use the NPC's description as a basis to describe them in the rewritten scene summary.
        """)
    )
    
    return scene_skill_challenge_npc_update_agent