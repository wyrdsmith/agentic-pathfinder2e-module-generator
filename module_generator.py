from pydantic_ai import Agent, RunContext
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.output import NativeOutput
from models.quest_concept import QuestConcept
from models.act_concept import ActList
from models.quest import Quest
from models.act import Act
from tools.db_tools import check_database, get_plot_hooks, add_plot_hook

def generate_quest_concept(current_quest: Quest):
    # Instantiate the Agent
    model = OllamaModel(
        'gemma4:12b',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )
    concept_agent = Agent(
        model,
        output_type = NativeOutput(QuestConcept),
        system_prompt = (
            "You are a creative Pathfinder 2e Game Master. Design a unique quest concept for the party. "
            "Use your tools to read past plot hooks to ensure you don't repeat them."
        )
    )

    # Register our database tools
    concept_agent.tool_plain(get_plot_hooks)

    print(f"Generating quest concept for {current_quest.player_count} players at level {current_quest.party_level}...")
    
    # Run the agent
    prompt = f"Create a new quest concept for a party of {current_quest.player_count} characters at level {current_quest.party_level}."
    result = concept_agent.run_sync(prompt)
    concept = result.output
    
    # Map the generated concept back to our main quest object
    print('Quest Concept Generated...')
    current_quest.name = concept.name
    print(f'Quest Name: {current_quest.name}')
    current_quest.theme = concept.theme
    print(f'Quest Theme: {current_quest.theme}')
    current_quest.setting = concept.setting
    print(f'Quest Setting: {current_quest.setting}')
    current_quest.plot_hook = concept.plot_hook
    print(f'Quest Plot Hook: {current_quest.plot_hook}')
    current_quest.summary = concept.summary
    print(f'Quest Summary: {current_quest.summary}')
    
    # Save the new plot hook to the database so we don't repeat it next time
    add_plot_hook(current_quest.plot_hook)
    
    return current_quest

def generate_acts(current_quest: Quest):
    # Instantiate the Agent for generating acts
    model = OllamaModel(
        'gemma4:12b',
        provider = OllamaProvider(base_url='http://localhost:11434/v1')
    )
    acts_agent = Agent(
        model,
        output_type = NativeOutput(ActList),
        system_prompt = (
            "You are an expert Pathfinder 2e Game Master. "
            "Based on the provided quest concept and summary, expand the quest summary into 3 distinct acts following the three act story structure. "
            "Do not generate scenes or encounters yet, just provide a detailed summary of what happens in each of the 3 acts."
        )
    )
    
    print(f"Generating 3 acts for '{current_quest.name}'...")
    
    prompt = (
        f"Quest Name: {current_quest.name}\n"
        f"Theme: {current_quest.theme}\n"
        f"Setting: {current_quest.setting}\n"
        f"Plot Hook: {current_quest.plot_hook}\n"
        f"Summary: {current_quest.summary}\n\n"
        "Generate the 3 acts for this quest."
    )
    result = acts_agent.run_sync(prompt)
    
    # Map the generated acts to our main quest object
    print('Acts Generated...')
    for act_concept in result.output.acts:
        new_act = Act(
            act_number=act_concept.act_number,
            summary=act_concept.summary
        )
        current_quest.acts.append(new_act)
        print(f"Act {new_act.act_number} Summary: {new_act.summary}")
        
    return current_quest

def main():
    # Verify DB first
    if not check_database():
        print("Database failed verification. Exiting.")
        return

    # Set up initial quest object
    current_quest = Quest(player_count=4, party_level=1)

    # Generate the quest concept
    current_quest = generate_quest_concept(current_quest)
    
    # Generate the acts
    current_quest = generate_acts(current_quest)

if __name__ == "__main__":
    main()
