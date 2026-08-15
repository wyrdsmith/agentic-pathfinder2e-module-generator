from pydantic_ai import Agent, RunContext
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from models.npc_concept import NPCConceptList
from models.quest import Quest
from tools.npc_tools import get_ancestries_with_descriptions, get_classes_with_descriptions
from tools.name_tools import get_npc_name

ENCOUNTER_AGENTS = {
    'combat': {
        'creation_agent': get_combat_encounter_creation_agent(),
        'extraction_agent': get_combat_encounter_extraction_agent()
    },
    'social': {
        'creation_agent': get_social_encounter_creation_agent(),
        'extraction_agent': get_social_encounter_extraction_agent()
    },
    'skill_challenge': {
        'creation_agent': get_skill_challenge_encounter_creation_agent(),
        'extraction_agent': get_skill_challenge_encounter_extraction_agent()
    },
    'hazard': {
        'creation_agent': get_hazard_encounter_creation_agent(),
        'extraction_agent': get_hazard_encounter_extraction_agent()
    }
}

def get_combat_encounter_creation_agent():
    model = OllamaModel(
        'gemma-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    encounter_agent = Agent(
        model,
        deps_type = Quest,
        system_prompt = (
            "You are a creative writer and a Pathfinder 2e Game Master. "
        )
    )
    
    return encounter_agent

def get_combat_encounter_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    encounter_agent = Agent(
        model,
        output_type = NativeOutput(NPCConceptList),
        system_prompt = (
            "You are an expert Data Extraction Agent. "
            "Your only purpose is to extract the encounter data from the provided encounter information. "
            "Do not add any additional information or simplify/summarize any part of the encounter data, just extract the data and return it."
        )
    )
    
    return encounter_agent

def get_social_encounter_creation_agent():
    model = OllamaModel(
        'gemma-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    encounter_agent = Agent(
        model,
        deps_type = Quest,
        system_prompt = (
            "You are a creative writer and a Pathfinder 2e Game Master. "
        )
    )
    
    return encounter_agent

def get_social_encounter_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    encounter_agent = Agent(
        model,
        output_type = NativeOutput(NPCConceptList),
        system_prompt = (
            "You are an expert Data Extraction Agent. "
            "Your only purpose is to extract the encounter data from the provided encounter information. "
            "Do not add any additional information or simplify/summarize any part of the encounter data, just extract the data and return it."
        )
    )
    
    return encounter_agent

def get_skill_challenge_encounter_creation_agent():
    model = OllamaModel(
        'gemma-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    encounter_agent = Agent(
        model,
        deps_type = Quest,
        system_prompt = (
            "You are a creative writer and a Pathfinder 2e Game Master. "
        )
    )
    
    return encounter_agent

def get_skill_challenge_encounter_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    encounter_agent = Agent(
        model,
        output_type = NativeOutput(NPCConceptList),
        system_prompt = (
            "You are an expert Data Extraction Agent. "
            "Your only purpose is to extract the encounter data from the provided encounter information. "
            "Do not add any additional information or simplify/summarize any part of the encounter data, just extract the data and return it."
        )
    )
    
    return encounter_agent

def get_hazard_encounter_creation_agent():
    model = OllamaModel(
        'gemma-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    encounter_agent = Agent(
        model,
        deps_type = Quest,
        system_prompt = (
            "You are a creative writer and a Pathfinder 2e Game Master. "
        )
    )
    
    return encounter_agent

def get_hazard_encounter_extraction_agent():
    model = OllamaModel(
        'qwen2.5-quest',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )

    encounter_agent = Agent(
        model,
        output_type = NativeOutput(NPCConceptList),
        system_prompt = (
            "You are an expert Data Extraction Agent. "
            "Your only purpose is to extract the encounter data from the provided encounter information. "
            "Do not add any additional information or simplify/summarize any part of the encounter data, just extract the data and return it."
        )
    )
    
    return encounter_agent