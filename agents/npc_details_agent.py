from pydantic_ai import Agent
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from models.npc_details import NPCDetails

def get_npc_details_creation_agent():
    model = OllamaModel(
        'gemma-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    npcs_agent = Agent(
        model,
        system_prompt = textwrap.dedent("""
            # Role
            You are a highly creative writer and a Pathfinder 2e Game Master.

            # Task
            Expand on an NPC concept to flesh out their details for an adventure module.

            # Output Requirements
            Provide the following exactly, clearly labeled:
            1. Appearance: A description of the NPC's physical appearance.
            2. Personality: A description of the NPC's personality.
            3. Behavior: A description of how the NPC behaves.
            4. Attitude: A description of the NPC's attitude towards the player characters.

            # Constraints
            - Do not change anything else about the NPC.
            - Do not include any other information in your response.
        """)
    )

    return npcs_agent

def get_npc_details_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    npcs_agent = Agent(
        model,
        output_type = NativeOutput(NPCDetails),
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Data Extraction Agent.

            # Task
            Extract the NPC details (appearance, personality, behavior, attitude) from the provided text.

            # Constraints
            - DO NOT add, infer, or simplify any information.
            - Do not provide explanations or commentary.
        """)
    )
    
    return npcs_agent