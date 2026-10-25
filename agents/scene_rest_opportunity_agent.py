from pydantic_ai import Agent, RunContext
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.settings import ModelSettings
from pydantic_ai.output import NativeOutput
from typing import Literal

def get_scene_rest_opportunity_agent():
    model = OllamaModel(
        'gemma3-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    scene_rest_opportunity_agent = Agent(
        model,
        output_type = NativeOutput(Literal['short rest', 'long rest', 'no rest opportunity']),
        system_prompt = textwrap.dedent("""
            # Role
            You are a Pathfinder 2e Game Master in the beginning stages of designing encounters for scenes in a quest.

            # Task
            For the provided current scene summary, location, and encounter type and the next scene summary, location and encounter, decide the best rest opportunity for after the current scene, whether it's a "short rest", "long rest", or "no rest opportunity". If it is a combat encounter, you should consider whether it makes sense for it to be a short rest or long rest opportunity.

            # Rest Opportunity Context
            - A short rest is a rest that takes 10 minutes to complete.
            - A long rest is a rest that takes a few hours to complete.
            - A no rest opportunity is a scene that does not have a rest opportunity and the next scene immediately takes place.

            # Output Format
            Return ONLY the rest opportunity for the current scene, i.e. "short rest", "long rest", or "no rest opportunity".

            # Constraints
            - A scene can have ONLY ONE rest opportunity.
            - You MUST choose one of the three rest opportunities: "short rest", "long rest", or "no rest opportunity".
        """)
    )
    
    return scene_rest_opportunity_agent