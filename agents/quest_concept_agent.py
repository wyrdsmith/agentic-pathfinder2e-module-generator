from pydantic_ai import Agent, RunContext
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.settings import ModelSettings
from pydantic_ai.output import NativeOutput
from models.quest_concept import QuestConcept
import textwrap

def get_quest_concept_creation_agent():
    model = OllamaModel(
        'gemma3-quest',
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
        provider = OllamaProvider(base_url='http://localhost:11434/v1'),
        settings = ModelSettings(temperature=0.0)
    )

    quest_concept_agent = Agent(
        model,
        output_type = NativeOutput(QuestConcept),
        system_prompt = (
            textwrap.dedent("""
                # Role
                You are a highly skilled Data Extraction Agent.
                
                # Task
                Extract the quest concept data from the provided quest concept.
                
                # Output Requirements
                Extract the following information:
                1. Name: The name of the quest.
                2. Theme: The theme of the quest.
                3. Setting: The setting of the quest.
                4. Plot Hook: The plot hook of the quest.

                # Output Format
                Return the quest concept as an object with the following properties:
                - name: string
                - theme: string
                - setting: string
                - plot_hook: string
                
                # Constraints
                - DO NOT add, infer, or output any information not explicitly present in the source text.
                - If a specific field is not present in the source text, leave it as an empty string ("") but do not generate placeholder content.
                - Do not provide explanations or commentary.
            """)
        )
    )
    
    return quest_concept_agent