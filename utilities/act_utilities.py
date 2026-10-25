from models.quest import Quest
from models.act import Act
from tools.log_tools import *
from agents.acts_agent import get_acts_creation_agent, get_acts_extraction_agent

def generate_acts(current_quest: Quest):
    """
    Generates acts for the quest.
    Creative agent generates the acts, extraction agent converts it to a pydantic model.

    Args:
        current_quest: The Quest object to generate acts for.
    
    Returns:
        Quest: The updated Quest object.
    """
    log_status("Generating acts for quest...")
    
    # Instantiate the Agent for generating acts
    acts_creation_agent = get_acts_creation_agent()
    
    prompt = "# Quest Information:\n"
    prompt += f"Name: {current_quest.name}\n"
    prompt += f"Theme: {current_quest.theme}\n"
    prompt += f"Setting: {current_quest.setting}\n"
    prompt += f"Plot Hook: {current_quest.plot_hook}\n"
    prompt += f"Summary: {current_quest.summary}\n\n"
    prompt += "Generate the 3 acts for this quest."
    
    with console.status("[bold cyan]AI Agent is generating acts for the quest...[/bold cyan]", spinner="dots"):
        result = acts_creation_agent.run_sync(prompt)
    raw_acts = result.output

    # Run the extraction agent
    acts_extraction_agent = get_acts_extraction_agent()
    prompt = f"Extract the summary for each of the three acts from the following quest act summaries:\n\n{raw_acts}"
    with console.status("[bold cyan]AI Agent is extracting quest acts...[/bold cyan]", spinner="dots"):
        result = acts_extraction_agent.run_sync(prompt)
    act_concepts = result.output

    # Verify three acts were generated, if not, regenerate acts
    while len(act_concepts) != 3:
        log_error("Incorrect number of acts generated, regenerating...")
        prompt += "\n\nRemember to create exactly 3 acts."
        with console.status("[bold cyan]AI Agent is regenerating acts for the quest...[/bold cyan]", spinner="dots"):
            raw_acts = acts_creation_agent.run_sync(prompt)
        prompt = f"Extract the summary for each of the three acts from the following quest act summaries:\n\n{raw_acts}"
        with console.status("[bold cyan]AI Agent is extracting quest acts...[/bold cyan]", spinner="dots"):
            result = acts_extraction_agent.run_sync(prompt)
        act_concepts = result.output

    log_success('Quest Acts Generated...')

    # Map the generated acts to our main quest object
    log_output('Quest Acts:')
    act_number = 1
    for act_concept in act_concepts:
        new_act = Act(
            act_number = act_number,
            summary = act_concept.summary
        )
        current_quest.acts.append(new_act)
        log_output(f" - Act {new_act.act_number}: {new_act.summary}")
        act_number += 1
        
    return current_quest