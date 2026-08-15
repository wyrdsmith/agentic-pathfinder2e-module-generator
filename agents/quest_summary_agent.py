from pydantic_ai import Agent
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider

def get_quest_summary_agent():
    model = OllamaModel(
        'gemma-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    quest_summary_agent = Agent(
        model,
        system_prompt = textwrap.dedent("""
            # Role
            You are a highly creative writer and Pathfinder 2e Game Master.

            # Task
            Write a brief narrative summary based on the given quest concept.
            The summary must describe:
            1. How the player characters are introduced to the story and involved in the quest.
            2. The main goal or conflict of the quest.
            3. The eventual resolution.

            # Constraints
            - DO NOT name or describe specific NPCs, locations, or monsters in detail. Keep them completely vague so downstream agents can expand on them.
            - Example 1: Do NOT describe enemies as "Goblins", use "monsters" or "local threat".
            - Example 2: Do NOT name a key NPC "King Arthur" or describe their race, use "local leader" or "the employer".
        """)
    )
    
    return quest_summary_agent