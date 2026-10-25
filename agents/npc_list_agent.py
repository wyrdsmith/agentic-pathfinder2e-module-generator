from pydantic_ai import Agent, RunContext
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.settings import ModelSettings
from pydantic_ai.output import NativeOutput
from models.npc_concept import NPCConcept
from models.quest import Quest
from tools.name_tools import get_npc_name
from typing import List

def get_npc_list_creation_agent():
    model = OllamaModel(
        'gemma3-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    npc_list_agent = Agent(
        model,
        system_prompt = textwrap.dedent("""
            # Role
            You are a Pathfinder 2e Game Master working on the first step of creating NPCs for a quest.

            # Task
            Analyze the scenes in a quest, and based on the summaries provided, identify the NPCs that need to be created.
            - You must list each NPC to be created using a one to four word description of the NPC as an identifier pulled from the scene summary.
            - Then list the act and scene numbers the NPC appears in.

            # Scene Context
            Not every scene includes an NPC. The scene summary will describe an NPC using a vague identifier (e.g., "a shopkeeper", "the elder", "the village mayor", "a guard") in the scene if one exists.
            - If the scene summary describes an NPC using a vague identifier, then that NPC MUST be included in the list of NPCs.
            - Do NOT create an NPC for a scene that does not have an NPC in its summary.
            - If more than one scene summary uses the same or similar identifiers for an NPC, then it can be assumed they are the same NPC and they should be listed as such adding the scene to the NPC's list of scenes.

            # Output Requirements
            Each NPC in your final list must clearly label:
            - NPC Identifier (a unique one to four word description of the NPC that will be used to refer to them throughout the quest; e.g., "young farm boy", "wise woman", "the elder", "the mayor", "the guard")
            - Scenes (semicolon delimited list of act and scene numbers the NPC appears in, e.g. "Act 1, Scene 2; Act 2, Scene 1; Act 3, Scene 3")

            # Constraints
            - Do NOT include any information other than the list of NPCs to be created and the scenes they appear in.
            - The scenes list must include all scenes the NPC appears in, not just the first one.
        """)
    )
    
    return npc_list_agent

def get_npc_list_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1'),
        settings = ModelSettings(temperature=0.0)
    )

    npc_list_agent = Agent(
        model,
        output_type = NativeOutput(List[NPCConcept]),
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Data Extraction Agent.

            # Task
            Extract the NPC concept data from the provided list of NPCs.

            # Output Requirements
            Extract the following fields for each NPC: identifier and scenes.
            - The scenes data is pulled from a semicolon delimited list of act numbers and scene labels, e.g. "Act 1, Scene 2; Act 2, Scene 1; Act 3, Scene 3".
            - Parse the scenes data into a list of tuples of (act_number, scene_number), e.g. [(1, 2), (2, 1), (3, 3)].

            # Output Format
            Return the NPCs as a list of objects with the following properties:
            - identifier: string
            - scenes: list[tuple[int, int]]

            # Constraints
            - DO NOT add, infer, or simplify any information.
            - Extract and provide only the identifier and scenes, DO NOT generate any additional fields.
            - Do not provide explanations or commentary.
        """)
    )
    
    return npc_list_agent