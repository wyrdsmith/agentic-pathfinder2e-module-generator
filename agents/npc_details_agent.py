from pydantic_ai import Agent, RunContext
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from models.npc_details import NPCDetails
from models.quest import Quest
from tools.quest_tools import get_quest_theme
from tools.quest_tools import get_quest_setting
from tools.quest_tools import get_quest_summary
from tools.npc_tools import get_ancestry_description
from tools.npc_tools import get_class_description

def get_npc_details_creation_agent():
    model = OllamaModel(
        'gemma-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    npcs_agent = Agent(
        model,
        deps_type=Quest,
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
            - Use your provided tools to gather necessary context (ancestry description, class description, quest theme, quest setting, quest summary).
        """)
    )
    
    npcs_agent.tool(get_quest_theme)
    npcs_agent.tool(get_quest_setting)
    npcs_agent.tool(get_ancestry_description)
    npcs_agent.tool(get_class_description)
    npcs_agent.tool(get_quest_summary)

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