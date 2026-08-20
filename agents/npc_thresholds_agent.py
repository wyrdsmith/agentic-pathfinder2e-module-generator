from pydantic_ai import Agent
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from models.npc_influence import Thresholds
from pydantic_ai.settings import ModelSettings

def get_npc_thresholds_creation_agent():
    model = OllamaModel(
        'gemma4-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    npc_agent = Agent(
        model,
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Pathfinder 2e Game Master.

            # Context
            The players will have an encounter with an NPC and attempt to influence them during the adventure module. When an NPC is successfully influenced, they may provide a minor boon, a boon, or a major boon based on the number successes achieved, the Thresholds (four, six and eight), while influencing the NPC.

            # Task
            Based on the provided quest, act, scene and NPC information, describe appropriate boons for the scene that can be granted by the NPC if they are successfully influenced at each Threshold (four successes: minor boon, six successes: boon, eight successes: major boon).

            # Output Requirements
            For each Threshold, output the following:
            1. Threshold: The Threshold (four, six, or eight).
            2. Boon: A description of the boon that the players can recieve at this threshold.

            # Constraints
            - Do not change anything else about the NPC.
            - Do not include any other information in your response.
            - ONLY list the thresholds and boons.
        """)
    )

    return npc_agent

def get_npc_thresholds_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1'),
        settings = ModelSettings(temperature=0.0)
    )

    npc_agent = Agent(
        model,
        output_type = NativeOutput(Thresholds),
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Data Extraction Agent.

            # Context
            You will be provided with a list of thresholds and their boons.

            # Task
            Extract the boons for each threshold from the provided text and return it as a thresholds object.

            # Output Requirements
            The thresholds object has three properties, each corresponding to a threshold:
            - four: The boon for four successes.
            - six: The boon for six successes.
            - eight: The boon for eight successes.

            # Output Format
            Return a thresholds object with the following properties:
            - four: string
            - six: string
            - eight: string

            # Constraints
            - DO NOT add, infer, or simplify any information.
            - Do not provide explanations or commentary.
            - Only extract the boons for each threshold.
        """)
    )
    
    return npc_agent