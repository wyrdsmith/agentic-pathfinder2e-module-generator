import time
from models.quest import Quest
from models.act import Act
from models.scene import Scene
from models.npc import NPC, SceneRole, Skill
from tools.log_tools import *
from tools.db_tools import check_database, add_quest_concept, get_quest_concepts
from tools.quest_tools import adjust_encounter_threat_levels, distribute_experience_budgets, distribute_reward_budgets
from tools.npc_tools import get_npc_base_stats, get_npc_saves, get_ancestry_description, get_class_description, get_ancestries_with_descriptions, get_classes_with_descriptions, get_skills_with_descriptions
from agents.quest_concept_agent import get_quest_concept_creation_agent, get_quest_concept_extraction_agent
from agents.quest_summary_agent import get_quest_summary_agent
from agents.acts_agent import get_acts_creation_agent, get_acts_extraction_agent
from agents.scenes_agent import get_scenes_creation_agent, get_scenes_extraction_agent
from agents.npcs_agent import get_npcs_creation_agent, get_npcs_extraction_agent, get_npc_scenes_extraction_agent
from agents.npc_details_agent import get_npc_details_creation_agent, get_npc_details_extraction_agent
from agents.npc_skills_agent import get_npc_skills_creation_agent
from agents.npc_saves_agent import get_npc_saves_creation_agent

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
    
    log_success('Quest Concept Generated...')
    
    # Run the extraction agent
    quest_concept_extraction_agent = get_quest_concept_extraction_agent()
    prompt = f"Extract the quest name, theme, setting, and plot hook from the following quest concept: {raw_concept}"
    with console.status("[bold orange1]AI Agent is extracting the quest concept data...[/bold orange1]", spinner="dots"):
        result = quest_concept_extraction_agent.run_sync(prompt)
    concept = result.output

    log_success('Quest Concept Extracted...')

    # Map the generated concept back to our main quest object
    log_write('Quest Concept:')
    current_quest.name = concept.name
    log_write(f' - Name: {current_quest.name}')
    current_quest.theme = concept.theme
    log_write(f' - Theme: {current_quest.theme}')
    current_quest.setting = concept.setting
    log_write(f' - Setting: {current_quest.setting}')
    current_quest.plot_hook = concept.plot_hook
    log_write(f' - Plot Hook: {current_quest.plot_hook}')
    
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
    log_write(f'Quest Summary: {current_quest.summary}')
    
    return current_quest

def generate_acts(current_quest: Quest):
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

    log_success('Quest Acts Generated...')

    # Run the extraction agent
    acts_extraction_agent = get_acts_extraction_agent()
    prompt = f"Extract the summary for each of the three acts from the following quest act summaries:\n\n{raw_acts}"
    with console.status("[bold orange1]AI Agent is extracting quest acts...[/bold orange1]", spinner="dots"):
        result = acts_extraction_agent.run_sync(prompt)
    acts = result.output

    # Verify three acts were generated, if not, regenerate acts
    while len(acts.acts) != 3:
        log_error("Incorrect number of acts generated, regenerating...")
        acts.acts = []
        prompt += "\n\nRemember to create exactly 3 acts."
        with console.status("[bold cyan]AI Agent is regenerating acts for the quest...[/bold cyan]", spinner="dots"):
            raw_acts = acts_creation_agent.run_sync(prompt)
        prompt = f"Extract the summary for each of the three acts from the following quest act summaries:\n\n{raw_acts}"
        with console.status("[bold orange1]AI Agent is extracting quest acts...[/bold orange1]", spinner="dots"):
            result = acts_extraction_agent.run_sync(prompt)
        acts = result.output
    
    log_success('Quest Acts Extracted...')

    # Map the generated acts to our main quest object
    log_write('Acts Generated:')
    act_number = 1
    for act_concept in acts.acts:
        new_act = Act(
            act_number = act_number,
            summary = act_concept.summary
        )
        current_quest.acts.append(new_act)
        log_write(f" - Act {new_act.act_number}: {new_act.summary}")
        act_number += 1
        
    return current_quest

def generate_scenes_for_act(current_quest: Quest, current_act: Act):
    """
    Generates scenes for a given act.
    Creative agent generates the scenes, extraction agent converts it to a pydantic model.

    Args:
        current_quest: The Quest object to generate scenes for.
        current_act: The Act object to generate scenes for.
    
    Returns:
        Quest: The updated Quest object.
    """
    # Instantiate the Agent for generating scenes
    scenes_creation_agent = get_scenes_creation_agent()
    
    prompt = "# Quest Information:\n"
    prompt += f"Quest Name: {current_quest.name}\n"
    prompt += f"Theme: {current_quest.theme}\n"
    prompt += f"Setting: {current_quest.setting}\n"
    prompt += f"Overall Quest Summary: {current_quest.summary}\n\n"
    prompt += "# Current Act Scenes Should be Created For:\n"
    prompt += f"Act {current_act.act_number} Summary: {current_act.summary}\n\n"
    
    # If not the first act, add the previous act summary
    if current_act.act_number > 1:
        prompt += "# Previous Act in Quest:\n"
        prompt += f"Act {current_act.act_number - 1} Summary: {current_quest.acts[current_act.act_number - 1].summary}\n\n"
    
    # If not the last act, add the next act summary
    if current_act.act_number < len(current_quest.acts):
        prompt += "# Next Act in Quest:\n"
        prompt += f"Act {current_act.act_number + 1} Summary: {current_quest.acts[current_act.act_number].summary}\n\n"
    
    prompt += f"Generate the scenes for Act {current_act.act_number}."

    with console.status(f"[bold cyan]AI Agent is generating scenes for Act {current_act.act_number}...[/bold cyan]", spinner="dots"):
        result = scenes_creation_agent.run_sync(prompt, deps=current_quest)
    raw_scenes = result.output

    log_success(f'Quest Scenes Generated for Act {current_act.act_number}...')

    # Run the extraction agent
    scenes_extraction_agent = get_scenes_extraction_agent()
    prompt = f"Extract the summary, location, encounter type, and rest opportunity for each of the scenes from the following quest scene summaries:\n\n{raw_scenes}"
    with console.status(f"[bold orange1]AI Agent is extracting quest scenes for Act {current_act.act_number}...[/bold orange1]", spinner="dots"):
        result = scenes_extraction_agent.run_sync(prompt)
    scenes = result.output

    # Verify scenes were generated, if not, regenerate scenes for this act
    while len(scenes.scenes) < 4 or len(scenes.scenes) > 9:
        log_error(f"Incorrect number of scenes generated for Act {current_act.act_number}, regenerating...")
        scenes.scenes = []
        prompt += "\n\nRemember to create 4 to 9 scenes."
        with console.status(f"[bold cyan]AI Agent is regenerating scenes for Act {current_act.act_number}...[/bold cyan]", spinner="dots"):
            raw_scenes = scenes_creation_agent.run_sync(prompt)
        prompt = f"Extract the summary, location, encounter type, and rest opportunity for each of the scenes from the following quest scene summaries:\n\n{raw_scenes}"
        with console.status(f"[bold orange1]AI Agent is extracting quest scenes for Act {current_act.act_number}...[/bold orange1]", spinner="dots"):
            result = scenes_extraction_agent.run_sync(prompt)
        scenes = result.output
    
    log_success(f'Quest Scenes Extracted for Act {current_act.act_number}...')

    # Map the generated scenes to the current act
    log_write(f'Scenes for Act {current_act.act_number}:')
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
        log_write(f" - Scene {new_scene.scene_number} ({new_scene.encounter_type}): {new_scene.summary}")
        log_write(f" - - Location: {new_scene.location}")
        log_write(f" - - Rest Opportunity: {new_scene.rest_opportunity}")
        scene_number += 1
        
    return current_act

def generate_quest_npc_list(current_quest: Quest) -> Quest:
    """
    Generates a list of NPCs for the quest.
    Creative agent generates the NPCs, extraction agent converts it to a pydantic model.
    A second extraction agent extracts the NPC roles for each scene.

    Args:
        quest: The Quest object to generate NPCs for.
    
    Returns:
        Quest: The updated Quest object.
    """
    # Instantiate the agent for NPC creation
    npc_creation_agent = get_npcs_creation_agent()
    
    # Generate the prompt for the npc_creation_agent
    prompt = "#Quest Information:\n"
    prompt += f"Quest Theme: {current_quest.theme}\n"
    prompt += f"Quest Setting: {current_quest.setting}\n"
    prompt += f"Quest Summary: {current_quest.summary}\n\n"

    # Add act and scene summaries
    for act in current_quest.acts:
        prompt += f"Act {act.act_number} Summary: {act.summary}\n"
        for scene in act.scenes:
            prompt += f"  - Scene {scene.scene_number} ({scene.encounter_type}): {scene.summary}\n"
        prompt += "\n"

    prompt += "# Available Ancestries:\n"
    prompt += get_ancestries_with_descriptions()
    prompt += "\n"

    prompt += "# Available Classes:\n"
    prompt += get_classes_with_descriptions()
    prompt += "\n"

    prompt += "Generate the list of NPCs for this quest."
    
    # Run the creation agent
    with console.status("[bold cyan]AI Agent is generating the NPCs for the quest...[/bold cyan]", spinner="dots"):
        result = npc_creation_agent.run_sync(prompt, deps=current_quest)
    raw_npc_concepts = result.output

    log_success('Quest NPC Concepts Generated...')

    # Run the extraction agent to get basic NPC information
    npc_extraction_agent = get_npcs_extraction_agent()
    prompt = f"Extract the NPC concepts from the following list of NPC concepts:\n\n{raw_npc_concepts}"
    with console.status("[bold orange1]AI Agent is extracting the NPC concepts...[/bold orange1]", spinner="dots"):
        result = npc_extraction_agent.run_sync(prompt)
    npc_concepts_list = result.output

    log_success('Quest NPC List Extracted...')

    current_quest.npcs = []

    # Extract scene roles for each NPC
    npc_scene_extraction_agent = get_npc_scenes_extraction_agent()
    for npc_concept in npc_concepts_list.npc_concepts:
        prompt = f"""
        Extract the scene role data for the following NPC's scene roles description:\n\n{npc_concept.scene_roles}
        """
        with console.status(f"[bold orange1]AI Agent is extracting the scene roles for {npc_concept.name}...[/bold orange1]", spinner="dots"):
            result = npc_scene_extraction_agent.run_sync(prompt)
        npc_scene_roles = result.output
        new_NPC = NPC(
            name = npc_concept.name,
            ancestry = npc_concept.ancestry,
            class_name = npc_concept.class_name,
            quest_role = npc_concept.quest_role,
        )
        for scene_role in npc_scene_roles.scene_roles:
            new_NPC.scene_roles.append(SceneRole(
                act_number = scene_role.act_number,
                scene_number = scene_role.scene_number,
                role = scene_role.role
            ))
        current_quest.npcs.append(new_NPC)

    log_success('Quest NPC Scene Roles Extracted...')

    # Log the created NPC scene roles
    log_write('Quest NPC List:')
    for npc in current_quest.npcs:
        log_write(f"  - NPC: {npc.name}, {npc.ancestry}, {npc.class_name}")
        log_write(f"  - - Role: {npc.quest_role}")
        log_write(f"  - - Scene Roles:")
        for scene_role in npc.scene_roles:
            log_write(f"  - - - Act: {scene_role.act_number}, Scene {scene_role.scene_number}: {scene_role.role}")
    
    return current_quest

def generate_npc_details(current_quest: Quest) -> Quest:
    """
    Generates the details for each NPC in the quest.

    Args:
        current_quest: The Quest object to generate NPC details for.
    
    Returns:
        Quest: The updated Quest object.
    """
    # Instantiate the agent for NPC details creation
    npc_details_creation_agent = get_npc_details_creation_agent()
    
    # Iterate through each npc and send the NPC info to the creation agent then extract the data
    for npc in current_quest.npcs:
        prompt = "#Quest Information:\n"
        prompt += f"Quest Theme: {current_quest.theme}\n"
        prompt += f"Quest Setting: {current_quest.setting}\n"
        prompt += f"Quest Summary: {current_quest.summary}\n\n"
        prompt += "#NPC Concept:\n"
        prompt += f"NPC Name: {npc.name}\n"
        prompt += f"NPC Ancestry: {npc.ancestry}\n"
        prompt += f" - Ancestry Description: {get_ancestry_description(npc.ancestry)}\n"
        prompt += f"NPC Class: {npc.class_name}\n"
        prompt += f" - Class Description: {get_class_description(npc.class_name)}\n"
        prompt += f"NPC Quest Role: {npc.quest_role}\n\n"
        prompt += "Generate the details for the NPC in this quest."
        with console.status(f"[bold cyan]AI Agent is generating details for {npc.name}...[/bold cyan]", spinner="dots"):
            result = npc_details_creation_agent.run_sync(prompt)
        raw_npc_details = result.output

        log_success(f"NPC Details Generated for {npc.name}...")

        # Run the extraction agent to get basic NPC information
        npc_details_extraction_agent = get_npc_details_extraction_agent()
        prompt = f"Extract the NPC details data from the provided NPC details:\n\n{raw_npc_details}"
        with console.status(f"[bold orange1]AI Agent is extracting details data for {npc.name}...[/bold orange1]", spinner="dots"):
            result = npc_details_extraction_agent.run_sync(prompt)
        npc_details = result.output

        log_success(f"NPC Details Extracted for {npc.name}...")

        # Map the generated NPC details to the current NPC
        npc.appearance = npc_details.appearance
        npc.personality = npc_details.personality
        npc.behavior = npc_details.behavior
        npc.attitude = npc_details.attitude

    # Print the results
    log_success("Quest NPC Details Extracted...")
    log_write("Quest NPC Details:")
    for npc in current_quest.npcs:
        log_write(f"  - NPC: {npc.name}")
        log_write(f"  - - Appearance: {npc.appearance}")
        log_write(f"  - - Personality: {npc.personality}")
        log_write(f"  - - Behavior: {npc.behavior}")
        log_write(f"  - - Attitude: {npc.attitude}")
    
    return current_quest

def generate_npc_stats(current_quest: Quest) -> Quest:
    """
    Generates the stats for each NPC in the quest.

    Args:
        current_quest: The Quest object to generate NPC stats for.
    
    Returns:
        Quest: The updated Quest object.
    """
    # Instantiate the agent for NPC skills creation
    npc_skills_agent = get_npc_skills_creation_agent()
    npc_saves_agent = get_npc_saves_creation_agent()
    
    # Iterate through each NPC, create stat block from creature_stats table
    for npc in current_quest.npcs:
        # Get Base Stats from creature_stats table in database
        npc.stats = get_npc_base_stats(current_quest, npc)

        log_success(f"NPC Base Stats Generated for {npc.name}...")

        # Run the skill selection agent
        prompt = "#Quest Information:\n"
        prompt += f"Quest Summary: {current_quest.summary}\n\n"
        prompt += "# NPC Information:\n"
        prompt += f"NPC Name: {npc.name}\n"
        prompt += f"NPC Ancestry: {npc.ancestry}\n"
        prompt += f"NPC Class: {npc.class_name}\n"
        prompt += f" - Class Description: {get_class_description(npc.class_name)}\n"
        prompt += f"NPC Quest Role: {npc.quest_role}\n\n"
        prompt += "# Available Skills:\n"
        prompt += f"{get_skills_with_descriptions()}\n\n"
        prompt += "Select the appropriate skills for this NPC based on their class and quest role"
        with console.status(f"[bold cyan]AI Agent is selecting appropriate skills for {npc.name}...[/bold cyan]", spinner="dots"):
            result = npc_skills_agent.run_sync(prompt)
        selected_skills = result.output
        
        # Assign skills as Skill models
        npc_skills = []
        for skill_name in selected_skills:
            # Use perception value because skill from creature_stats was used to determine perception
            npc_skills.append(Skill(name=skill_name, modifier=npc.stats.perception))
        npc.stats.skills = npc_skills

        log_success(f"NPC Skills Selected for {npc.name}...")

        # Run the saves ordering agent
        prompt = "#NPC Information:"
        prompt += f"NPC Name: {npc.name}\n"
        prompt += f"NPC Class: {npc.class_name}\n"
        prompt += f" - Class Description: {get_class_description(npc.class_name)}\n"
        prompt += f"NPC Quest Role: {npc.quest_role}\n\n"
        prompt += "Order the NPC's saves from best to worst based on their class and quest role"
        with console.status(f"[bold cyan]AI Agent is ordering saves for {npc.name}...[/bold cyan]", spinner="dots"):
            result = npc_saves_agent.run_sync(prompt)
        npc_saves = result.output

        # Assign saves to NPC
        npc.stats.saves = get_npc_saves(npc_saves, npc.stats.level)

        log_success(f"NPC Saves Generated for {npc.name}...")

    # Print the results
    log_write(f"Quest NPC Stats:")
    for npc in current_quest.npcs:
        log_write(f"  - NPC: {npc.name}")
        log_write(f"  - - Stats:")
        log_write(f"  - - - Level: {npc.stats.level}")
        log_write(f"  - - - Perception: {npc.stats.perception}")
        log_write(f"  - - - AC: {npc.stats.ac}")
        log_write(f"  - - - HP: {npc.stats.hp}")
        log_write(f"  - - - Strike: {npc.stats.strike}")
        log_write(f"  - - - Damage: {npc.stats.damage}")
        log_write(f"  - - - Spell Attack: {npc.stats.spellAttack}")
        log_write(f"  - - - Spell DC: {npc.stats.spellDC}")
        log_write(f"  - - - Saves:")
        for save in npc.stats.saves:
            log_write(f"  - - - - {save.name}: {save.modifier}")
        log_write(f"  - - Skills:")
        for skill in npc.stats.skills:
            log_write(f"  - - - {skill.name}: {skill.modifier}")

    log_success("Quest NPC stats generated...")
    
    return current_quest

def generate_npc_influence_info(current_quest: Quest) -> Quest:
    
    return current_quest

def generate_scene_details(current_quest: Quest) -> Quest:

    return current_quest

def write_quest_to_file(current_quest: Quest):
    """
    Writes the quest to a file.

    Args:
        current_quest: The Quest object to write to a file.
    
    Returns:
        None
    """
    filename = f"output/{current_quest.name.replace(' ','_')}.json"
    with open(filename, "w") as f:
        f.write(current_quest.model_dump_json(indent=2))
    log_success(f"Quest '{current_quest.name}' written to file: {filename}")

def main():
    # Reset log
    log_clear()

    # Start timer
    start_time = time.time()
    
    # Verify DB first
    if not check_database():
        log_error("Database verification failed... Exiting.")
        return

    log_success("Beginning adventure module generation...")

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

    # Generate list of NPCs for the quest
    current_quest = generate_quest_npc_list(current_quest)

    # Generate NPC details: appearance, personality, behavior, and attitude
    current_quest = generate_npc_details(current_quest)
    
    # Generate NPC stats
    current_quest = generate_npc_stats(current_quest)

    # Generate NPC influence information
    # current_quest = generate_npc_influence_info(current_quest)
    
    write_quest_to_file(current_quest)

    end_time = time.time()
    elapsed = end_time - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    log_success(f"Module generation complete in {minutes}m {seconds}s")

if __name__ == "__main__":
    main()
