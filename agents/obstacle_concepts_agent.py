from pydantic_ai import Agent, RunContext
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from pydantic_ai.settings import ModelSettings
from models.obstacle_concept import ObstacleConcept
from typing import List

def get_obstacle_concepts_creation_agent():
    model = OllamaModel(
        'gemma3-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    obstacles_agent = Agent(
        model,
        system_prompt = textwrap.dedent("""
            # Role
            You are a highly creative Pathfinder 2e Game Master in the brainstorming phase of designing an encounter.

            # Task
            Create a series of obstacles (6 to 10) for the players to overcome as they progress through the current scene.

            # Obstacle Context
            - The obstacles should represent a series of challenges that the players must overcome in order to progress through the scene.
            - Obstacles can be physical or magical in nature.
            - A majority of obstacles hinder the party's progress in some way if failed to overcome.
            - A very few obstacles can harm the party; if the obstacle can harm the party, such as a trap or dangerous area, then it is a hazard.
            - Each obstacle should have two resolutions: one for if the party successfully overcomes the obstacle, and one for if the party fails to overcome the obstacle.
            - Both success and failure resolutions should be appropriate for the entire party, affecting all members.

            # Obstacle Requirements
            Create 6 to 10 obstacles for the provided scene context in a list. Each obstacle must include:
            1. Name: The name of the obstacle in a single phrase.
            2. Description: The description of the obstacle.
            3. Success Resolution: A description of what happens after the party successfully overcomes the obstacle.
            4. Failure Resolution: A description of what happens after the party fails to overcome the obstacle.
            5. Is Hazard: Whether the obstacle is hazard that can damage the party (either true or false).

            # Constraints
            - DO NOT include any enemies, creatures or NPCs as obstacles.
            - DO NOT include how to overcome the obstacle in the description, only describe the obstacle and the environment.
            - DO NOT include any game mechanics in the description, success resolution or failure resolution.
            - Provide ONLY general descriptions of what happens if the players overcome it or fail to overcome it.
            - CRITICAL: Do NOT include any details such as checks, DCs, damage or saving throws or any other game mechanics; these will be determined later on in the encounter development process.
        """)
    )
    
    return obstacles_agent

def get_obstacle_concepts_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1'),
        settings = ModelSettings(temperature=0.0)
    )

    obstacles_agent = Agent(
        model,
        output_type = NativeOutput(List[ObstacleConcept]),
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert Data Extraction Agent.

            # Task
            Extract the name, description, success_resolution, failure_resolution, and is_hazard for each obstacle in the provided list of obstacles.

            # Output Format
            Return the obstacles as a list of objects, each with the following properties:
            - name: string
            - description: string
            - success_resolution: string
            - failure_resolution: string
            - is_hazard: boolean

            # Constraints
            - DO NOT add, infer, or simplify any information.
            - Do not provide explanations or commentary.
        """)
    )
    
    return obstacles_agent