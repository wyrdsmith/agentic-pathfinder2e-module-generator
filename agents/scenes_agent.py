from pydantic_ai import Agent, RunContext
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from models.scene_concept import SceneList

def get_scenes_creation_agent():
    model = OllamaModel(
        'gemma-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    scenes_agent = Agent(
        model,
        system_prompt = (
            "You are a creative writer and a Pathfinder 2e Game Master. "
            "Based on the provided quest context and the specific act summary, generate a series of 5 to 9 narrative scenes for this act. "
            "The scenes should be detailed enough to give the reader a clear understanding of the events that take place in the act covering plot points, enemies, and NPCs encountered. "
            "Each scene should consist of: "
            "a summary of the events in the scene, "
            "a description of the location where the scene takes place, "
            "the type of encounter that takes place in the scene, "
            "and the type of rest opportunity available after the scene. "
            "The type of encounter can be combat, social, skill challenge, or hazard: "
            "a combat encounter is one in which the players face enemies in combat; "
            "a social encounter is one in which the players engage in roleplay with npcs; "
            "a skill challenge is one in which the players use their skills to overcome a series of obstacles or challenges; "
            "a hazard encounter is one in which the players face a hazard, such as a trap or a natural disaster. "
            "Combat and social encounters are the most common, while skill challenges and hazard encounters are rarer. "
            "Scenes should end with an opportunity for the player characters to have a short rest (10 minutes) or a long rest (8 hours), especially after combat or hazard encounters. "
            "Alternatively, the scene may not provide a rest opportunity if it makes sense for the narrative. "
            "You must create from 5 to 9 scenes depending on what is needed to tell the story of this act appropriately. "
            "Multiple scenes may take place in the same location, so describe the location the same way in each scene description if it's the same location. "
            "The list of scenes should be able to be read in order to tell the story of this act in a narrative fashion, with each scene flowing into the next with no gaps in the narrative. "
            "The location of the scene, the type of encounter in the scene, and the rest opportunity for each scene should be easily identifiable."
        )
    )
    
    return scenes_agent

def get_scenes_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    scenes_agent = Agent(
        model,
        output_type = NativeOutput(SceneList),
        system_prompt = (
            "You are an expert Data Extraction Agent. "
            "Your only purpose is to extract the summary of each scene along with the scene's location, encounter type, and the type of rest opportunity for each scene. "
            "Do not add any additional information or simplify/summarize any part of the summaries, just extract the data and return it."
        )
    )
    
    return scenes_agent