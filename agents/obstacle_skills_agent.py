from pydantic_ai import Agent, RunContext
import textwrap
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from pydantic_ai.settings import ModelSettings
from models.obstacle_concept import ObstacleSkillConcept
from typing import List

def get_obstacle_skills_agent():
    model = OllamaModel(
        'gemma3-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1'),
        settings = ModelSettings(temperature=0.5)
    )

    obstacles_agent = Agent(
        model,
        output_type = NativeOutput(List[ObstacleSkillConcept]),
        system_prompt = textwrap.dedent("""
            # Role
            You are a Pathfinder 2e Game Master helping generate an encounter that consists of a series of obstacles.

            # Task
            Given an obstacle's description, success resolution, failure resolution and a list of available skills, choose four appropriate skills that players could use to overcome the obstacle.

            # Output Requirements
            Return a list of four skills that make the most sense to overcome the obstacle. Each skill must include:
            1. Skill: The name of the skill.
            2. Difficulty: Ether easy, moderate or hard: how difficult it is to overcome the obstacle using this skill.

            # Output Format
            Return the skills as a list of objects, each with the following properties:
            - skill: string
            - difficulty: string

            # Constraints
            - Skill names must match the available skills exactly as listed.
            - Do NOT provide any additional information, explanation or commentary.
            - Difficulty MUST be either easy, moderate or hard.
        """)
    )
    
    return obstacles_agent