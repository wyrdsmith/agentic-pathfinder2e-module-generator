from pydantic_ai import Agent, RunContext
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from models.quest_concept import QuestConcept
import textwrap

def get_quest_concept_creation_agent():
    model = OllamaModel(
        'gemma-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    quest_concept_agent = Agent(
        model,
        system_prompt = (
            textwrap.dedent("""
                # Role
                You are a highly creative Pathfinder 2e Game Master. 
                # Task
                Create a new, unique quest concept to pitch to the players. 
                # Output Requirements
                Your pitch must include exactly these four elements:
                1. Name of the quest
                2. Theme of the quest
                3. Setting of the quest
                4. Plot Hook (Must briefly cover: how the adventure begins, the primary goal/conflict, and the eventual resolution)
                # Constraints
                - DO NOT name or describe specific NPCs, locations, or monsters in detail. Keep them completely vague and open to interpretation so downstream agents can expand on them.
                - Example 1: Do NOT describe enemies as "Goblins", use "monsters" or "local threat".
                - Example 2: Do NOT name a key NPC "King Arthur" or describe their race, use "local leader" or "the employer".
                - Ensure your new concept is entirely unique and does not repeat previous names, themes, settings, or plot hooks provided in the context.
            """)
        )
    )

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
            textwrap.dedent("""
                # Role
                You are a highly skilled Data Extraction Agent.
                # Task
                Extract structured information from a given text.
                # Output Requirements
                Extract exactly these four fields:
                1. Name (String): The primary name of the subject.
                2. Theme (String): The main theme or topic.
                3. Setting (String): The setting or context.
                4. Plot Hook (String): A detailed description of the plot hook.
                # Constraints
                - DO NOT add, infer, or output any information not explicitly present in the source text.
                - If a specific field is not present in the source text, leave it as an empty string ("") but do not generate placeholder content.
                - Do not provide explanations or commentary.
            """)
        )
    )
    
    return quest_concept_agent