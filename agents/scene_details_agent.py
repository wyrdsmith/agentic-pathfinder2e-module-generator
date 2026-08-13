from pydantic_ai import Agent, RunContext
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from models.scene_concept import SceneList
from tools.quest_tools import get_quest_summary, get_current_act_summary, get_previous_scene_summary, get_next_scene_summary, get_previous_act_summary, get_next_act_summary, get_npcs_for_scene

def get_scene_details_creation_agent():
    model = OllamaModel(
        'gemma-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    scene_details_agent = Agent(
        model,
        system_prompt = (
            "You are a creative writer and a Pathfinder 2e Game Master. "
            "You will be given the summary of a scene in an act of an adventure module quest, and are to come up with the details of the scene based on the summary. "
            "You are to write an introduction, resolution and a detailed description of the events in a scene that takes place in an adventure module quest. "
            "The introduction should set the stage for the scene, the resolution should provide a conclusion to the scene, and the description should provide a detailed account of the events that take place in the scene. "
            "The details of the scene should be based on the summary of the scene, and should be consistent with the overall theme and tone of the quest. "
            "The introduction and resolution should be written in a narrative style, while the description should be written in a more detailed and descriptive style. "
            "The introduction, resolution and description should be clearly labeled. "
            "You have access to tools to get more information about the quest, use them to make sure your details are consistent with the quest. "
        )
    )
    
    scene_details_agent.tool(get_quest_summary)
    scene_details_agent.tool(get_current_act_summary)
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
        system_prompt = (
            "You are an expert Data Extraction Agent. "
            "Your only purpose is to extract the introduction, description and resolution of the provided scene. "
            "Do not add any additional information or simplify/summarize any part of the scene information, just extract the data and return it."
        )
    )
    
    return scene_details_agent