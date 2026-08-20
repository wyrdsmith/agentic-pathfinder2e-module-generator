from pydantic_ai import Agent, RunContext
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.settings import ModelSettings
from pydantic_ai.output import NativeOutput
from models.scene_concept import SceneConcept
from typing import List

def get_scenes_creation_agent():
    model = OllamaModel(
        'gemma4-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    scenes_agent = Agent(
        model,
        system_prompt = textwrap.dedent("""
            # Role
            You are a highly creative writer and Pathfinder 2e Game Master.

            # Task
            Generate a continuous narrative series of scenes for the provided act summary. 
            The scenes must flow sequentially into each other to tell the story of the act.

            # Scene Requirements
            Create exactly 4 to 9 scenes using the minimum number needed. Each scene MUST clearly label:
            1. Summary of events.
            2. Location (must be consistent across scenes if it is the same place).
            3. Encounter Type (combat, social, skill challenge, or hazard). Keep in mind combat/social are most common.
            4. Rest Opportunity ("short rest", "long rest", or "no rest opportunity"). Provide rest especially after combat/hazard, unless narrative dictates otherwise.

            # Constraints
            - DO NOT name or describe specific NPCs, locations, or monsters in detail. Keep them vague.
            - Example: Do NOT describe enemies as "Goblins", use "monsters". Do NOT name a key NPC, use "local leader".
        """)
    )
    
    return scenes_agent

def get_scenes_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1'),
        settings = ModelSettings(temperature=0.0)
    )

    scenes_agent = Agent(
        model,
        output_type = NativeOutput(List[SceneConcept]),
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Data Extraction Agent.

            # Task
            Given a list of scenes, extract the summary, location, encounter type, and rest opportunity for each scene.

            # Output Format
            Return the scenes as a list of objects with the following properties:
            - summary: string
            - location: string
            - encounter_type: string
            - rest_opportunity: string

            # Constraints
            - DO NOT add, infer, or simplify any information.
            - Do not provide explanations or commentary.
        """)
    )
    
    return scenes_agent