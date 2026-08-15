from pydantic_ai import Agent, RunContext
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from models.npc_concept import NPCConceptList, NPCSceneRolesList
from models.quest import Quest
from tools.name_tools import get_npc_name

def get_npcs_creation_agent():
    model = OllamaModel(
        'gemma-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    npcs_agent = Agent(
        model,
        deps_type = Quest,
        system_prompt = textwrap.dedent("""
            # Role
            You are a highly creative writer and Pathfinder 2e Game Master.

            # Task
            Create a list of NPC concepts for a provided quest. NPCs should only be included in scenes where they play a narrative role.
            - Social encounters MUST include at least one NPC.
            - Combat, skill challenge, or hazard encounters may or may not include NPCs.

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
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    npcs_agent = Agent(
        model,
        output_type = NativeOutput(NPCConceptList),
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Data Extraction Agent.

            # Task
            Extract the NPC concept data from the provided list.

            # Output Requirements
            Extract the following fields for each NPC: name, ancestry, class, quest_role, scene_roles.
            - The `scene_roles` attribute must contain all lines of text that begin with "Act [ordinal], Scene [ordinal]:".

            # Constraints
            - DO NOT add, infer, or simplify any information.
            - Do not provide explanations or commentary.
        """)
    )
    
    return npcs_agent

def get_npc_scenes_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    npcs_agent = Agent(
        model,
        output_type = NativeOutput(NPCSceneRolesList),
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Data Extraction Agent.

            # Task
            Extract the NPC scene role data from the provided description.

            # Output Requirements
            Extract the act number, the scene number, and the entire role description for each scene role.

            # Constraints
            - DO NOT add, infer, or simplify any information.
            - Do not provide explanations or commentary.
        """)
    )
    
    return npcs_agent