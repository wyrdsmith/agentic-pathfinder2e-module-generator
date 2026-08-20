from pydantic_ai import Agent, RunContext
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.settings import ModelSettings
from pydantic_ai.output import NativeOutput
from models.npc_concept import NPCConceptList, NPCSceneRole
from models.quest import Quest
from tools.name_tools import get_npc_name
from typing import List

def get_npcs_creation_agent():
    model = OllamaModel(
        'gemma4-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    npcs_agent = Agent(
        model,
        deps_type = Quest,
        system_prompt = textwrap.dedent("""
            # Role
            You are a highly creative writer and Pathfinder 2e Game Master.

            # Task
            Create a list of NPC concepts for a provided quest. NPCs should only be included in scenes where they have a narrative role.

            # Scene Context
            Each scene has one of four encounter types: social, combat, skill challenge or hazard.
            - Social encounters MUST include at least one NPC.
            - Combat encounters may or may not include NPCs, but they MUST NOT be the enemies in the encounter.
            - Skill challenge encounters may or may not include NPCs, but only to introduce or resolve the scene.
            - Hazard encounters may or may not include NPCs, but only to introduce or resolve the scene.

            # Workflow Requirements
            1. Analyze the provided quest, act, and scene summaries.
            2. For each NPC, select an ancestry and a class.
            3. You MUST use the `get_npc_name` tool to generate the NPC's name.
            4. Define the NPC's role in the overall quest.
            5. For each scene the NPC appears in, describe their role in that scene. Each description MUST begin with the act and scene number (e.g., "Act One, Scene One: ...").

            # Output Requirements
            Each NPC in your final list must clearly label:
            - Name
            - Ancestry
            - Class
            - Quest Role
            - Scene Roles

            # Constraints
            - Do NOT include any information other than the list of NPC concepts.
            - Do NOT invent any ancestries; use only the ones in the list provided.
            - Do NOT invent any classes; use only the ones in the list provided.
        """)
    )

    # Register our tools
    npcs_agent.tool(get_npc_name)
    
    return npcs_agent

def get_npcs_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1'),
        settings = ModelSettings(temperature=0.0)
    )

    npcs_agent = Agent(
        model,
        output_type = NativeOutput(NPCConceptList),
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Data Extraction Agent.

            # Task
            Extract the NPC concept data from the provided list of NPCs.

            # Output Requirements
            Extract the following fields for each NPC: name, ancestry, class, quest_role, scene_roles.
            - The `scene_roles` property must contain all lines of text that begin with "Act [ordinal], Scene [ordinal]:" for the NPC.

            # Output Format
            Return the NPCs as a list of objects with the following properties:
            - name: string
            - ancestry: string
            - class: string
            - quest_role: string
            - scene_roles: string

            # Constraints
            - DO NOT add, infer, or simplify any information.
            - Do not provide explanations or commentary.
        """)
    )
    
    return npcs_agent

def get_npc_scenes_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1'),
        settings = ModelSettings(temperature=0.0)
    )

    npcs_agent = Agent(
        model,
        output_type = NativeOutput(List[NPCSceneRole]),
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Data Extraction Agent.

            # Task
            Extract the NPC scene role data from the provided description.

            # Output Requirements
            Extract the act number, the scene number, and the entire role description for each scene role.

            # Output Format
            Return the scene roles as a list of objects with the following properties:
            - act: integer
            - scene: integer
            - role: string

            # Constraints
            - DO NOT add, infer, or simplify any information.
            - Do not provide explanations or commentary.
        """)
    )
    
    return npcs_agent