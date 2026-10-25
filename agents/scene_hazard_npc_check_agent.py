from pydantic_ai import Agent
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput

def get_scene_hazard_npc_check_agent():
    model = OllamaModel(
        'gemma3-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    scene_hazard_npc_check_agent = Agent(
        model,
        output_type = NativeOutput(bool),
        system_prompt = textwrap.dedent("""
            # Role
            You are a Pathfinder 2e Game Master in the process of adjusting a scene with a hazard encounter for a quest.

            # Task
            Given the scene summary and the NPC description, determine if the scene summary is using the NPC description to describe a hazard or hazards for the player characters to overcome.

            # Output Requirements
            Return only True if the scene summary is using the NPC description to describe a hazard or hazards for the player characters to overcome and False if it is not.

            # Constraints
            - Do NOT include any information, labels or commentary other than True or False.
        """)
    )
    
    return scene_hazard_npc_check_agent