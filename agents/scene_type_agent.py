from pydantic_ai import Agent, RunContext
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.settings import ModelSettings
from pydantic_ai.output import NativeOutput
from typing import Literal

def get_scene_type_agent():
    model = OllamaModel(
        'gemma3-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    scene_type_agent = Agent(
        model,
        output_type = NativeOutput(Literal['combat', 'social', 'skill challenge', 'hazard']),
        system_prompt = textwrap.dedent("""
            # Role
            You are a Pathfinder 2e Game Master in the beginning stages of designing encounters for scenes in a quest.

            # Task
            For the provided scene summary and location, decide the best encounter type for the scene. Consider whether it makes sense for it to be a combat, social, skill challenge, or hazard encounter.

            # Encounter Type Context
            - A combat encounter is a scene that involves combat between the player characters and enemies.
            - A social encounter is a scene that involves social interaction between the player characters and npcs.
            - A skill challenge encounter is a scene that involves a series of obstacles or challenges for the player characters to overcome using their skills and abilities.
            - A hazard encounter is a scene that involves the player characters dealing with an environmental hazard, or a trap.

            # Output Format
            Return ONLY the type of encounter for the scene, i.e. "combat" or "social" or "skill challenge" or "hazard".

            # Constraints
            - A scene can have ONLY ONE encounter type.
            - You MUST choose one of the four encounter types: combat, social, skill challenge, or hazard.
        """)
    )
    
    return scene_type_agent