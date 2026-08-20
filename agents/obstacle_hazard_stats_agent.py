from pydantic_ai import Agent, RunContext
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.settings import ModelSettings
from pydantic_ai.output import NativeOutput
from models.obstacle_concept import HazardStatsConcept

def get_obstacle_hazard_stats_agent():
    model = OllamaModel(
        'gemma3-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1'),
        settings = ModelSettings(temperature=0.0)
    )

    obstacles_agent = Agent(
        model,
        output_type = NativeOutput(HazardStatsConcept),
        system_prompt = textwrap.dedent("""
            # Role
            You are a Pathfinder 2e Game Master helping generate an encounter that consists of a series of obstacles.

            # Task
            Given a hazardous obstacle's description, success resolution and failure resolution, determine the hazard type and the save type.

            # Hazardous Obstacle Context
            - An attack hazard makes an attack against each character in the party.
            - If the hazardouse obstacle is an attack hazard type, the save type MUST be AC.
            - An area hazard means that each member of the party rolls a save (Fortitude, Reflex or Will) against the hazard.
            - A Fortitude save is when a character must physically endure the effects.
            - A Reflex save is when a character can physically avoid the effects.
            - A Will save is when a character must mentally or spiritually endure the effects.
            - The save type for an area hazard MUST be either Fortitude, Reflex or Will.

            # Output Requirements
            Return only the following
            1. Hazard Type: Either attack or area.
            2. Save Type: Either Fortitude, Reflex, Will or AC.

            # Output Format
            Return the hazard stats as an object with the following properties:
            - hazard_type: string
            - save_type: string

            # Constraints
            - Do NOT provide any additional information, explanation or commentary.
        """)
    )
    
    return obstacles_agent