from rich.console import Console
from models.quest import Quest
from models.act import Act
from models.scene import Scene
from models.npc import NPC
from tools.db_tools import check_database, add_quest_concept
from tools.quest_tools import adjust_encounter_threat_levels, distribute_experience_budgets, distribute_reward_budgets
from agents.quest_concept_agent import get_quest_concept_creation_agent, get_quest_concept_extraction_agent
from agents.quest_summary_agent import get_quest_summary_agent
from agents.acts_agent import get_acts_creation_agent, get_acts_extraction_agent
from agents.scenes_agent import get_scenes_creation_agent, get_scenes_extraction_agent
from agents.npcs_agent import get_npcs_creation_agent, get_npcs_extraction_agent

console = Console()

def generate_quest_concept(current_quest: Quest):
    """
    Generates a quest concept including title, theme, setting, and plot hook.
    Creative agent generates the concept, extraction agent converts it to a pydantic model.
    Saves the generated quest concept to the database to prevent repetition.
    Returns the updated Quest object
    """
    # Instantiate the Agent
    quest_concept_creation_agent = get_quest_concept_creation_agent()

    print(f"Generating quest concept for {current_quest.player_count} players at level {current_quest.party_level}...")
    
    # Run the creation agent
    prompt = f"Create a new quest concept for a party of {current_quest.player_count} characters at level {current_quest.party_level}."
    with console.status("[bold cyan]AI Agent is currently thinking...", spinner="dots"):
        result = quest_concept_creation_agent.run_sync(prompt)
    raw_concept = result.output
    
    print('Quest Concept Generated...')
    
    # Run the extraction agent
    print('Extracting Quest Concept Data...')
    
    quest_concept_extraction_agent = get_quest_concept_extraction_agent()
    prompt = f"Extract the quest name, theme, setting, and plot hook from the following quest concept: {raw_concept}"
    with console.status("[bold yellow]AI Agent is currently extracting data...", spinner="dots"):
        result = quest_concept_extraction_agent.run_sync(prompt)
    concept = result.output

    print('Quest Concept Extracted...')

    # Map the generated concept back to our main quest object
    current_quest.name = concept.name
    print(f'Quest Name: {current_quest.name}')
    current_quest.theme = concept.theme
    print(f'Quest Theme: {current_quest.theme}')
    current_quest.setting = concept.setting
    print(f'Quest Setting: {current_quest.setting}')
    current_quest.plot_hook = concept.plot_hook
    print(f'Quest Plot Hook: {current_quest.plot_hook}')
    
    # Save the new plot hook to the database so we don't repeat it next time
    add_quest_concept(current_quest.name, current_quest.theme, current_quest.setting, current_quest.plot_hook)
    
    return current_quest

def generate_quest_summary(current_quest: Quest):
    """
    Generates a quest summary including theme, setting, and plot hook.
    Creative agent generates the summary, extraction agent converts it to a pydantic model.

    Returns the updated Quest object
    """
    # Instantiate the Agent
    quest_summary_agent = get_quest_summary_agent()
    
    print(f"Generating quest summary for {current_quest.name}...")
    
    # Run the creation agent
    prompt = (
        f"Quest Name: {current_quest.name}\n"
        f"Theme: {current_quest.theme}\n"
        f"Setting: {current_quest.setting}\n"
        f"Plot Hook: {current_quest.plot_hook}\n\n"
        "Generate the quest summary."
    )
    with console.status("[bold cyan]AI Agent is currently thinking...", spinner="dots"):
        result = quest_summary_agent.run_sync(prompt)
    summary = result.output
    
    # Map the generated summary back to our main quest object
    print('Quest Summary Generated...')
    current_quest.summary = summary
    print(f'Quest Summary: {current_quest.summary}')
    
    return current_quest

def generate_acts(current_quest: Quest):
    # Instantiate the Agent for generating acts
    acts_creation_agent = get_acts_creation_agent()
    
    print(f"Generating 3 acts for '{current_quest.name}'...")
    
    prompt = (
        f"Quest Name: {current_quest.name}\n"
        f"Theme: {current_quest.theme}\n"
        f"Setting: {current_quest.setting}\n"
        f"Plot Hook: {current_quest.plot_hook}\n"
        f"Summary: {current_quest.summary}\n\n"
        "Generate the 3 acts for this quest."
    )
    with console.status("[bold cyan]AI Agent is currently thinking...", spinner="dots"):
        result = acts_creation_agent.run_sync(prompt)
    raw_acts = result.output

    print('Quest Acts Generated...')

    # Run the extraction agent
    print('Extracting Quest Acts...')
    acts_extraction_agent = get_acts_extraction_agent()
    prompt = f"Extract the summary for each of the three acts from the following quest act summaries:\n\n{raw_acts}"
    with console.status("[bold yellow]AI Agent is currently extracting data...", spinner="dots"):
        result = acts_extraction_agent.run_sync(prompt)
    acts = result.output

    print('Quest Acts Extracted...')

    # Verify three acts were generated, if not, regenerate acts
    while len(acts.acts) != 3:
        print("Incorrect number of acts generated, regenerating...")
        acts.acts = []
        raw_acts = acts_creation_agent.run_sync(prompt)
        result = acts_extraction_agent.run_sync(prompt)
        acts = result.output
    
    # Map the generated acts to our main quest object
    print('Acts Generated...')
    act_number = 1
    for act_concept in acts.acts:
        new_act = Act(
            act_number = act_number,
            summary = act_concept.summary
        )
        current_quest.acts.append(new_act)
        print(f"Act {new_act.act_number} Summary: {new_act.summary}")
        act_number += 1
        
    return current_quest

def generate_scenes_for_act(current_quest: Quest, current_act: Act):
    # Instantiate the Agent for generating scenes
    scenes_creation_agent = get_scenes_creation_agent()
    
    print(f"Generating scenes for Act {current_act.act_number}...")
    
    prompt = (
        f"Quest Name: {current_quest.name}\n"
        f"Theme: {current_quest.theme}\n"
        f"Setting: {current_quest.setting}\n"
        f"Overall Quest Summary: {current_quest.summary}\n\n"
        f"Act {current_act.act_number} Summary: {current_act.summary}\n\n"
        f"Generate the scenes for Act {current_act.act_number}."
    )
    with console.status("[bold cyan]AI Agent is currently thinking...", spinner="dots"):
        result = scenes_creation_agent.run_sync(prompt)
    raw_scenes = result.output

    print('Quest Scenes Generated...')

    # Run the extraction agent
    print('Extracting Quest Scenes...')
    scenes_extraction_agent = get_scenes_extraction_agent()
    prompt = f"Extract the summary, location, encounter type, and rest opportunity for each of the scenes from the following quest scene summaries:\n\n{raw_scenes}"
    with console.status("[bold yellow]AI Agent is currently extracting data...", spinner="dots"):
        result = scenes_extraction_agent.run_sync(prompt)
    scenes = result.output

    print('Quest Scenes Extracted...')

    # Verify scenes were generated, if not, regenerate scenes for this act
    while len(scenes.scenes) < 4 or len(scenes.scenes) > 9:
        print("Incorrect number of scenes generated, regenerating...")
        scenes.scenes = []
        raw_scenes = scenes_creation_agent.run_sync(prompt)
        result = scenes_extraction_agent.run_sync(prompt)
        scenes = result.output
    
    # Map the generated scenes to the current act
    print(f'Scenes for Act {current_act.act_number} Generated...')
    scene_number = 1
    for scene_concept in scenes.scenes:
        new_scene = Scene(
            scene_number = scene_number,
            summary = scene_concept.summary,
            location = scene_concept.location,
            encounter_type = scene_concept.encounter_type,
            rest_opportunity = scene_concept.rest_opportunity
        )
        current_act.scenes.append(new_scene)
        print(f"  - Scene {new_scene.scene_number} ({new_scene.encounter_type}): {new_scene.summary}")
        print(f"  - - Location: {new_scene.location}")
        print(f"  - - Rest Opportunity: {new_scene.rest_opportunity}")
        scene_number += 1
        
    return current_act

def generate_global_npc_list(quest: Quest) -> Quest:
    # Instantiate the agent for NPC creation
    npc_creation_agent = get_npcs_creation_agent()
    
    print(f"Generating global cast for '{quest.name}'...")

    # Generate the prompt for the npc_creation_agent
    prompt_string = f"Quest Summary: {quest.summary}\n\n"

    # Add act and scene summaries
    for act in quest.acts:
        prompt_string += f"Act {act.act_number} Summary: {act.summary}\n"
        for scene in act.scenes:
            prompt_string += f"  - Scene {scene.scene_number} ({scene.encounter_type}): {scene.summary}\n"
        prompt_string += "\n"

    prompt_string += "Generate the list of NPCs for this quest."
    
    # Run the creation agent
    prompt = (prompt_string)
    with console.status("[bold cyan]AI Agent is currently thinking...", spinner="dots"):
        result = npc_creation_agent.run_sync(prompt, deps=quest)
    raw_npc_concepts = result.output

    print('Global NPC List Generated...')
    print(raw_npc_concepts)
    # Run the extraction agent
    print('Extracting Global NPC List...')
    npc_extraction_agent = get_npcs_extraction_agent()
    prompt = f"Extract the NPC concepts from the following list of NPC concepts:\n\n{raw_npc_concepts}"
    with console.status("[bold yellow]AI Agent is currently extracting data...", spinner="dots"):
        result = npc_extraction_agent.run_sync(prompt)
    npc_concepts_list = result.output

    print('Global NPC List Extracted...')

    # Map the generated NPC concepts to our main quest object
    print('Global NPC List:')
    for npc_concept in npc_concepts_list.npc_concepts:
        new_npc = NPC(
            name = npc_concept.name,
            ancestry = npc_concept.ancestry,
            class_name = npc_concept.class_name,
            quest_role = npc_concept.quest_role,
            scene_roles = npc_concept.scene_roles
        )
        current_quest.npcs.append(new_npc)
        print(f"  - NPC: {new_npc.name}, {new_npc.ancestry}, {new_npc.class_name}")
        print(f"  - - Role: {new_npc.quest_role}")
        print(f"  - - Scene Roles:")
        for scene_role in new_npc.scene_roles:
            print(f"  - - - Act: {scene_role.act_number}, Scene {scene_role.scene_number}: {scene_role.role}")
    
    return quest

def generate_scene_details(quest: Quest) -> Quest:

    return quest

def main():
    # Verify DB first
    if not check_database():
        print("Database failed verification. Exiting.")
        return

    # Set up initial quest object
    current_quest = Quest(player_count=4, party_level=1)

    # Generate the quest concept
    current_quest = generate_quest_concept(current_quest)

    # Generate the quest summary
    current_quest = generate_quest_summary(current_quest)
    
    # Generate the acts
    current_quest = generate_acts(current_quest)
    
    # Generate scenes for each act
    for act in current_quest.acts:
        act = generate_scenes_for_act(current_quest, act)

    # Adjust the encounter threat levels
    current_quest = adjust_encounter_threat_levels(current_quest)

    # Distribute the encounter experience budgets
    current_quest = distribute_experience_budgets(current_quest)

    # Distribute the reward budgets
    current_quest = distribute_reward_budgets(current_quest)

    # Generate global list of NPCs for the quest
    current_quest = generate_global_npc_list(current_quest)

if __name__ == "__main__":
    main()
