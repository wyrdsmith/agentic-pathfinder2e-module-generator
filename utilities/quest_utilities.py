from models.quest import Quest
from tools.log_tools import *
from tools.db_tools import add_quest_concept, get_quest_concepts
from agents.quest_concept_agent import get_quest_concept_creation_agent, get_quest_concept_extraction_agent
from agents.quest_summary_agent import get_quest_summary_agent

def generate_quest_concept(current_quest: Quest):
    """
    Generates a quest concept including title, theme, setting, and plot hook.
    Creative agent generates the concept, extraction agent converts it to a pydantic model.
    Saves the generated quest concept to the database to prevent repetition.

    Args:
        current_quest: The Quest object to generate a concept for.
    
    Returns:
        Quest: The updated Quest object.
    """
    log_status("Generating quest concept...")

    # Instantiate the Agent
    quest_concept_creation_agent = get_quest_concept_creation_agent()

    # Run the creation agent
    past_concepts = get_quest_concepts()
    prompt = f"Create a new quest concept for a party of {current_quest.player_count} characters at level {current_quest.party_level}.\n\n"
    prompt += f"Context regarding past quests you have run (DO NOT REPEAT THESE):\n"
    if past_concepts:
        prompt += f"{past_concepts}\n\n"
    
    with console.status(f"[bold cyan]AI Agent is generating quest concept for {current_quest.player_count} players at level {current_quest.party_level}...[/bold cyan]", spinner="dots"):
        result = quest_concept_creation_agent.run_sync(prompt)
    raw_concept = result.output
    
    # Run the extraction agent
    quest_concept_extraction_agent = get_quest_concept_extraction_agent()
    prompt = f"Extract the quest name, theme, setting, and plot hook from the following quest concept: {raw_concept}"
    with console.status("[bold cyan]AI Agent is extracting the quest concept data...[/bold cyan]", spinner="dots"):
        result = quest_concept_extraction_agent.run_sync(prompt)
    concept = result.output

    log_success('Quest Concept Generated...')

    # Map the generated concept back to our main quest object
    log_output('Quest Concept:')
    current_quest.name = concept.name
    log_output(f' - Name: {current_quest.name}')
    current_quest.theme = concept.theme
    log_output(f' - Theme: {current_quest.theme}')
    current_quest.setting = concept.setting
    log_output(f' - Setting: {current_quest.setting}')
    current_quest.plot_hook = concept.plot_hook
    log_output(f' - Plot Hook: {current_quest.plot_hook}')
    
    # Save the new plot hook to the database so we don't repeat it next time
    add_quest_concept(current_quest.name, current_quest.theme, current_quest.setting, current_quest.plot_hook)
    
    return current_quest

def generate_quest_summary(current_quest: Quest):
    """
    Generates a quest summary including theme, setting, and plot hook.
    Creative agent generates the summary, extraction agent converts it to a pydantic model.

    Args:
        current_quest: The Quest object to generate a summary for.
    
    Returns:
        Quest: The updated Quest object.
    """
    log_status("Generating quest summary...")

    # Instantiate the Agent
    quest_summary_agent = get_quest_summary_agent()
    
    # Run the creation agent
    prompt = "# Quest Information:\n"
    prompt += f"Name: {current_quest.name}\n"
    prompt += f"Theme: {current_quest.theme}\n"
    prompt += f"Setting: {current_quest.setting}\n"
    prompt += f"Plot Hook: {current_quest.plot_hook}\n\n"
    prompt += "Generate the quest summary."
    
    with console.status("[bold cyan]AI Agent is generating quest summary...[/bold cyan]", spinner="dots"):
        result = quest_summary_agent.run_sync(prompt)
    summary = result.output
    
    log_success('Quest Summary Generated...')
    
    # Map the generated summary back to our main quest object
    current_quest.summary = summary
    log_output(f'Quest Summary: {current_quest.summary}')
    
    return current_quest