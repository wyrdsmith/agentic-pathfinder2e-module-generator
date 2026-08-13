from pydantic_ai import Agent, RunContext
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from models.quest_concept import QuestConcept
from tools.db_tools import get_quest_concepts

def get_quest_concept_creation_agent():
    model = OllamaModel(
        'gemma-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    quest_concept_agent = Agent(
        model,
        system_prompt = (
            "You are a creative Pathfinder 2e Game Master. Create a unique quest concept for the party to pitch to the players. "
            "Make sure to provide the name of the quest, the theme of the quest, the setting of the quest, and the plot hook of the quest. "
            "The plot hook should be brief, but cover how the adventure begins, the primary goal or conflict and the eventual resolution of the quest. "
            "Do not name or describe any NPCs, locations, or monsters in detail. Keep them vague and open to interpretation such that they can be expanded upon later. "
            "For example, if the quest is about fighting off enemies in a forest, do not describe the enemies as goblins, only enemies or monsters. "
            "Or, as another example, if there is a key npc, do not describe them as a human or give them a name, only describe them as a person or NPC or by their profession or purpose. "
            "Use your tool, get_quest_concepts, to read past quest concepts to ensure you don't repeat them or create a new quest concept that's too similar. "
            "You only need to run this tool once to get a complete list of all previous quest concepts."
        )
    )

    # Register our database tools
    quest_concept_agent.tool_plain(get_quest_concepts)
    
    return quest_concept_agent

def get_quest_concept_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    quest_concept_agent = Agent(
        model,
        output_type = NativeOutput(QuestConcept),
        system_prompt = (
            "You are an expert Data Extraction Agent. "
            "Your only purpose is to extract the name of the quest, the theme of the quest, the setting of the quest, and the plot hook of the quest. "
            "Do not add any additional information, just extract the data and return it."
        )
    )
    
    return quest_concept_agent