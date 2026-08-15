from pydantic_ai import Agent, RunContext
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from models.scene_concept import SceneList
from models.quest import Quest
from tools.quest_tools import get_next_act_summary

def get_scenes_creation_agent():
    model = OllamaModel(
        'gemma-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    scenes_agent = Agent(
        model,
        deps_type = Quest,
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
            - Use the `get_next_act_summary` tool if you need context on how this act should end to transition into the next.
        """)
    )

    scenes_agent.tool(get_next_act_summary)
    
    return scenes_agent

def get_scenes_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    scenes_agent = Agent(
        model,
        output_type = NativeOutput(SceneList),
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Data Extraction Agent.

            # Task
            Extract the summary, location, encounter type, and rest opportunity for each scene.

            # Constraints
            - DO NOT add, infer, or simplify any information.
            - Do not provide explanations or commentary.
        """)
    )
    
    return scenes_agent