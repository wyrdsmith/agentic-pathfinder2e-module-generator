from pydantic_ai import Agent, RunContext
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from pydantic_ai.settings import ModelSettings
from models.scene_details import SceneDetails

def get_scene_details_creation_agent():
    model = OllamaModel(
        'gemma4-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    scene_details_agent = Agent(
        model,
        system_prompt = textwrap.dedent("""
            # Role
            You are a highly creative writer and Pathfinder 2e Game Master.

            # Task
            Given the information about a scene and the encounter within the scene, expand the summary of the scene into three detailed sections.

            # Output Requirements
            Provide the following exactly, clearly labeled:
            1. Introduction: Sets the stage for the scene leading up to the encounter, but does not include how the encounter begins (narrative style intended to be read to the players by the gamemaster).
            2. Description: Brief description of the events taking place during the scene outside of the encounter (descriptive style intended to be known only by the gamemaster).
            3. Resolution: Conclusion to the scene after the encounter including any rest opportunities that are provided, but does not include how the encounter ends (narrative style intended to be read to the players by the gamemaster).

            # Constraints
            - Do NOT include any information outside of the requested fields.
            - Do NOT include any mechanics, stats, or rules. This is CRITICAL.
            - If the encounter type is 'hazard', DO NOT describe or include any information about the hazard in the introduction.
        """)
    )

    return scene_details_agent

def get_scene_details_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1'),
        settings = ModelSettings(temperature=0.0)
    )

    scene_details_agent = Agent(
        model,
        output_type = NativeOutput(SceneDetails),
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Data Extraction Agent.

            # Task
            Extract the introduction, description, and resolution of the provided scene details.

            # Output Format
            Return the scene details as an object with the following properties:
            1. introduction: string
            2. description: string
            3. resolution: string

            # Constraints
            - DO NOT add, infer, or simplify any information.
            - Do not provide explanations or commentary.
        """)
    )
    
    return scene_details_agent