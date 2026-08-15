from pydantic_ai import Agent, RunContext
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from models.scene_concept import SceneList
from tools.quest_tools import get_quest_summary, get_act_summary, get_previous_scene_summary, get_next_scene_summary, get_previous_act_summary, get_next_act_summary, get_npcs_for_scene

def get_scene_details_creation_agent():
    model = OllamaModel(
        'gemma-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    scene_details_agent = Agent(
        model,
        system_prompt = textwrap.dedent("""
            # Role
            You are a highly creative writer and Pathfinder 2e Game Master.

            # Task
            Expand the summary of a scene into detailed events. The tone and details must be consistent with the overall quest theme and setting.

            # Output Requirements
            Provide the following exactly, clearly labeled:
            1. Introduction: Sets the stage for the scene (narrative style).
            2. Description: Detailed account of the events taking place (descriptive style).
            3. Resolution: Conclusion to the scene (narrative style).

            # Constraints
            - Use your provided tools (quest_summary, act_summary, next/previous scenes/acts, npcs_for_scene) to ensure narrative consistency.
            - Do not include any information outside of the requested fields.
        """)
    )
    
    scene_details_agent.tool(get_quest_summary)
    scene_details_agent.tool(get_act_summary)
    scene_details_agent.tool(get_previous_scene_summary)
    scene_details_agent.tool(get_next_scene_summary)
    scene_details_agent.tool(get_previous_act_summary)
    scene_details_agent.tool(get_next_act_summary)
    scene_details_agent.tool(get_npcs_for_scene)

    return scene_details_agent

def get_scene_details_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    scene_details_agent = Agent(
        model,
        output_type = NativeOutput(SceneList),
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Data Extraction Agent.

            # Task
            Extract the introduction, description, and resolution of the provided scene.

            # Constraints
            - DO NOT add, infer, or simplify any information.
            - Do not provide explanations or commentary.
        """)
    )
    
    return scene_details_agent