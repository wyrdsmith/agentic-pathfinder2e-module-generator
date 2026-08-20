from pydantic_ai import Agent
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from pydantic_ai.settings import ModelSettings
from models.npc_influence_concept import NPCInfluenceInfoConcept

def get_npc_influence_info_concept_creation_agent():
    model = OllamaModel(
        'gemma4-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    npc_agent = Agent(
        model,
        system_prompt = textwrap.dedent("""
            # Role
            You are an highly creative Pathfinder 2e Game Master.

            # Context
            The players will have an encounter with an NPC and attempt to influence them during the adventure module.  This NPC has certain resistances, weaknesses, and a penalty to different methods of influence.

            # Task
            Based on the provided NPC information, determine the NPC's resistances, weaknesses, and a penalty to different methods of influence specific to the scene.

            # Output Requirements
            Provide the following, clearly labeled:
            1. Resistances: A single sentence describing 1 to 2 methods of influence and topics of conversation the NPC is resistant to, making them harder to influence.
            2. Weaknesses: A single sentence describing 1 to 2 methods of influence and topics of conversation the NPC is weak to, making them easier to influence.
            3. Penalty: A single sentence describing a single taboo topic or taboo method of influence that the NPC is strongly against.

            # Constraints
            - Do NOT change anything else about the NPC.
            - Do NOT include any other information in your response.
            - Do NOT name any specific skills, mechanics, or abilities. This is critical. The penalty should be described in terms of the NPC's personality, beliefs, and culture, not in terms of game mechanics.
        """)
    )

    return npc_agent

def get_npc_influence_info_concept_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1'),
        settings = ModelSettings(temperature=0.0)
    )

    npc_agent = Agent(
        model,
        output_type = NativeOutput(NPCInfluenceInfoConcept),
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Data Extraction Agent.

            # Task
            Extract the NPC Influence Information (resistances, weaknesses and penalty) from the provided text.

            # Output Format
            Return the influence information as an object with the following properties:
            - resistances: string
            - weaknesses: string
            - penalty: string

            # Constraints
            - DO NOT add, infer, or simplify any information.
            - Do not provide explanations or commentary.
        """)
    )
    
    return npc_agent