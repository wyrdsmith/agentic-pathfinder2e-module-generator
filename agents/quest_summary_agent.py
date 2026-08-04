from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider

def get_quest_summary_agent():
    model = OllamaModel(
        'gemma-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    quest_summary_agent = Agent(
        model,
        system_prompt = (
            "You are a creative writer and Pathfinder 2e Game Master. "
            "Write a summary based on the given quest concept describing how the player characters are introduced to the story and "
            "how they come to be involved in the quest. "
            "The summary should also, in a brief manner, describe the main goal or conflict of the quest and its resolution. "
            "Do not name or describe in detail any NPCs, locations, or monsters, they should be vague such that they can be expanded upon later. "
            "For example, if the quest is about fighting off enemies in a forest, do not describe the enemies as goblins, only enemies or monsters. "
            "Or, as another example, if there is a key npc, do not describe them as a human or give them a name, only describe them as a person or NPC or by their profession or purpose."
        )
    )
    
    return quest_summary_agent