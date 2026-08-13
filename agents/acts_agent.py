from pydantic_ai import Agent, RunContext
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from models.act_concept import ActList

def get_acts_creation_agent():
    model = OllamaModel(
        'gemma-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    acts_agent = Agent(
        model,
        system_prompt = (
            "You are a creative writer and Pathfinder 2e Game Master. "
            "Based on the provided quest details, expand the quest summary into a detailed narrative summary for each of 3 distinct acts following the three act story structure. "
            "Act One is the introduction to the quest. It should introduce the player characters to the world, the story, and the characters they will meet. "
            "It should also establish the conflict and the stakes of the quest. Act One should end with the player characters firmly embroiled in the conflict with no easy way to turn back. "
            "Act Two is the rising action of the quest. It should continue the story, building on the conflict and stakes established in Act One. "
            "It should also introduce new characters and challenges that the player characters will face. Act Two should see the player characters working toward their goal "
            "while also dealing with new complications and adversaries. Act Two should end with the player characters in a dire situation, facing a significant setback or tough choice that will determine the outcome of the quest."
            "Act Three is the climax and resolution of the quest. It should bring the story to a head, with the player characters facing the main conflict and the ultimate consequences of their decisions. "
            "Act Three should see the player characters working to resolve the main conflict while dealing with the complications and adversaries introduced in Act Two. "
            "Act Three should end with the player characters achieving their goal or failing to achieve it, and the resolution of the story as a result of their success or failure. "
            "The three acts should be able to be read in such a way as it tells the entire story of the quest in a narrative fashion."
            "Do not describe any NPCs, locations, monsters or items in detail. Keep them vague and open to interpretation such that they can be expanded upon later."
            "For example, if the quest is about fighting off enemies in a forest, do not describe the enemies as goblins, only enemies or monsters. "
            "Or, as another example, if there is a key npc, do not describe them as a human or give them a name, only describe them as a person or NPC or by their profession or purpose. "
            "Each act's summary should long enough and detailed enough to be used to create 4 to 9 scenes for each act later on."
        )
    )
    
    return acts_agent

def get_acts_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    quest_concept_agent = Agent(
        model,
        output_type = NativeOutput(ActList),
        system_prompt = (
            "You are an expert Data Extraction Agent. "
            "You will be provided the summaries for three acts in a story. Your only purpose is to extract the summary of each act. "
            "Do not add any additional information or simplify/summarize any part of the summaries, just extract the data and return it."
        )
    )
    
    return quest_concept_agent