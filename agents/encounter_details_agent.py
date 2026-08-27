from pydantic_ai import Agent, RunContext
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from models.encounter_details import EncounterDetails

def get_encounter_details_creation_agent():
    model = OllamaModel(
        'gemma3-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    encounter_details_agent = Agent(
        model,
        system_prompt = textwrap.dedent("""
            # Role
            You are a highly creative writer and Pathfinder 2e Game Master.

            # Task
            Given the information about a scene and the encounter within the scene, expand the encounter information into three sections without repeating the scene's introduction, description or resolution.

            # Output Requirements
            Provide the following exactly, clearly labeled:
            1. Introduction: A narrative description of what happens immediately preceding the start of the encounter, i.e. how the encounter begins, (narrative style intended to be read to the players by the gamemaster).
            2. Description: A brief description of what happens during the encounter, (descriptive style intended to be known only by the gamemaster).
            3. Resolution: A narrative description of what happens immediately following the conclusion of the encounter, i.e. how the encounter ends, (narrative style intended to be read to the players by the gamemaster).

            # Constraints
            - Do NOT include any information outside of the requested fields.
            - Do NOT include any mechanics, stats, or rules. This is CRITICAL.
            - If the Encounter Type is 'hazard' DO NOT describe or include the hazard in the introduction.
        """)
    )

    return encounter_details_agent

def get_encounter_details_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    encounter_details_agent = Agent(
        model,
        output_type = NativeOutput(EncounterDetails),
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Data Extraction Agent.

            # Task
            Extract the introduction, description, and resolution of the provided encounter details.

            # Output Format
            Return the encounter details as an object with the following properties:
            1. introduction: string
            2. description: string
            3. resolution: string

            # Constraints
            - DO NOT add, infer, or simplify any information.
            - Do not provide explanations or commentary.
        """)
    )
    
    return encounter_details_agent