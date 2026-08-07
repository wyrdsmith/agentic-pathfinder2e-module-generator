from models.quest import Quest
from models.act import Act
from models.scene import Scene
from tools.db_tools import check_database, add_quest_concept
from tools.quest_tools import adjust_encounter_threat_levels, distribute_experience_budgets, distribute_reward_budgets
from agents.quest_concept_agent import get_quest_concept_creation_agent, get_quest_concept_extraction_agent
from agents.quest_summary_agent import get_quest_summary_agent
from agents.acts_agent import get_acts_creation_agent, get_acts_extraction_agent
from agents.scenes_agent import get_scenes_creation_agent, get_scenes_extraction_agent

def generate_quest_concept(current_quest: Quest):
    # Instantiate the Agent
    quest_concept_creation_agent = get_quest_concept_creation_agent()

    print(f"Generating quest concept for {current_quest.player_count} players at level {current_quest.party_level}...")
    
    # Run the creation agent
    prompt = f"Create a new quest concept for a party of {current_quest.player_count} characters at level {current_quest.party_level}."
    result = quest_concept_creation_agent.run_sync(prompt)
    raw_concept = result.output
    
    print('Quest Concept Generated...')
    
    # Run the extraction agent
    print('Extracting Quest Concept Data...')
    
    quest_concept_extraction_agent = get_quest_concept_extraction_agent()
    prompt = f"Extract the quest name, theme, setting, and plot hook from the following quest concept: {raw_concept}"
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
    result = acts_creation_agent.run_sync(prompt)
    raw_acts = result.output

    print('Quest Acts Generated...')

    # Run the extraction agent
    print('Extracting Quest Acts...')
    acts_extraction_agent = get_acts_extraction_agent()
    prompt = f"Extract the summary for each of the three acts from the following quest act summaries:\n\n{raw_acts}"
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
    result = scenes_creation_agent.run_sync(prompt)
    raw_scenes = result.output

    print('Quest Scenes Generated...')

    # Run the extraction agent
    print('Extracting Quest Scenes...')
    scenes_extraction_agent = get_scenes_extraction_agent()
    prompt = f"Extract the summary, location, encounter type, and rest opportunity for each of the scenes from the following quest scene summaries:\n\n{raw_scenes}"
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

    # Distribute the encounter budgets
    current_quest = distribute_experience_budgets(current_quest)

    # Distribute the reward budgets
    current_quest = distribute_reward_budgets(current_quest)

if __name__ == "__main__":
    main()
