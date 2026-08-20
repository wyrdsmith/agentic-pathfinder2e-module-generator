from pydantic_ai import Agent
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from pydantic_ai.settings import ModelSettings
from models.npc_influence_concept import DiscoveryConcept
from typing import List

def get_npc_discoveries_concept_creation_agent():
    model = OllamaModel(
        'gemma3-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1'),
        settings = ModelSettings(temperature=0.5)
    )

    npc_agent = Agent(
        model,
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Pathfinder 2e Game Master.

            # Context
            The players will have an encounter with an NPC and attempt to influence them during the adventure module.

            # Task
            Based on the provided quest, act, scene and NPC information, select 2 to 3 skills from the provided skills list, and determine the difficulty to discover the methods to influence the NPC in this scene.

            # Output Requirements
            For each skill selected, output the following:
            1. Skill: The name of the skill.
            2. Difficulty: How difficult it is to use the skill to discover the methods to influence the NPC in this scene (easy, moderate, or hard).

            # Constraints
            - Do not change anything else about the NPC.
            - Do not include any other information in your response.
            - Only choose from the skills provided in the skills list.
            - Only select between 2 and 3 skills.
            - The difficulty must be one of the following: easy, moderate, or hard.
        """)
    )

    return npc_agent

def get_npc_discoveries_concept_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1'),
        settings = ModelSettings(temperature=0.0)
    )

    npc_agent = Agent(
        model,
        output_type = NativeOutput(List[DiscoveryConcept]),
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Data Extraction Agent.

            # Context
            You will be provided with a list of skills and their difficulties. Each pair of skill and difficulty is considered a Discovery.

            # Task
            Extract the NPC Discoveries (skill and difficulty) from the provided text.

            # Output Format
            Return the discoveries as a list of objects with the following properties:
            - skill: string
            - difficulty: string

            # Constraints
            - DO NOT add, infer, or simplify any information.
            - Do not provide explanations or commentary.
            - Only extract the NPC Discoveries (skill and difficulty).
        """)
    )
    
    return npc_agent