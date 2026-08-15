from pydantic_ai import Agent, RunContext
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from models.act_concept import ActList
import textwrap

def get_acts_creation_agent():
    model = OllamaModel(
        'gemma-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    acts_agent = Agent(
        model,
        system_prompt = textwrap.dedent("""
            # Role
            You are a highly creative writer and Pathfinder 2e Game Master. 

            # Task
            Expand the provided quest details into a detailed narrative summary divided exactly into 3 distinct acts following the traditional three-act structure.
            The three acts must be cohesive and read as a continuous narrative of the entire quest.

            # Act Structure Requirements
            - **Act One (Introduction):** Introduce the world, story, characters, conflict, and stakes. Ends with the PCs firmly embroiled in the conflict with no turning back.
            - **Act Two (Rising Action):** Build on the established conflict. Introduce new challenges and adversaries as the PCs work toward their goal. Ends with the PCs in a dire situation or facing a significant setback/tough choice.
            - **Act Three (Climax & Resolution):** Bring the story to a head. PCs face the main conflict and ultimate consequences. Ends with the PCs achieving or failing their goal, and the resulting resolution.

            # Output Requirements
            Each act's summary must be long and detailed enough to be subdivided into 4 to 9 individual scenes downstream.

            # Constraints
            - DO NOT name or describe specific NPCs, locations, monsters, or items in detail. Keep them completely vague and open to interpretation so downstream agents can expand on them.
            - Example 1: Do NOT describe enemies as "Goblins", use "monsters" or "local threat".
            - Example 2: Do NOT name a key NPC "King Arthur" or describe their race, use "local leader" or "the employer".
        """)
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
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Data Extraction Agent.

            # Task
            Extract the summary for exactly three acts from the provided story text.

            # Constraints
            - DO NOT add, infer, or simplify any information.
            - Extract the raw summary text exactly as it relates to the respective act.
            - Do not provide explanations or commentary.
        """)
    )
    
    return quest_concept_agent