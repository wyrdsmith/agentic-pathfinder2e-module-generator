from pydantic_ai import Agent, RunContext
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from typing import List

def get_npc_saves_creation_agent():
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
            Determine the order from best to worst of an NPC's saving throws (Fortitude, Reflex, Will) based on their class and quest role.
            - **Fortitude:** Resisting physical effects (poisons, diseases).
            - **Reflex:** Dodging physical effects (arrows, fireballs).
            - **Will:** Resisting mental effects (charms, illusions).

            # Output Requirements
            Supply ONLY a list of the save names in order from best to worst.
            - Example (Wizard): Will, Reflex, Fortitude
            - Example (Fighter): Fortitude, Reflex, Will
            - Example (Rogue): Reflex, Fortitude, Will

            # Constraints
            - Do not provide explanations or other text, only the list of save names.
            - Use the `get_class_description` tool if you need more information about the NPC's class.
        """)
    )
    
    return npcs_agent