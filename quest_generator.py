import time
from models.quest import Quest
from models.act import Act
from models.scene import Scene
from models.npc import NPC, SceneRole, Skill
from models.enemy import Enemy
from models.npc_influence import NPCInfluenceInfo, Discovery, Influence, Thresholds, Penalty
from models.obstacle import Obstacle, ObstacleSkill, HazardStats
from tools.log_tools import *
from tools.db_tools import check_database, add_quest_concept, get_quest_concepts
from tools.quest_tools import adjust_encounter_threat_levels, distribute_experience_budgets, distribute_reward_budgets
from tools.npc_tools import get_npc_base_stats, get_npc_saves, get_ancestry_description, get_class_description, get_ancestries_with_descriptions, get_classes_with_descriptions, get_skills_with_descriptions, get_npcs_for_scene, get_npc_influence_dc, get_scene_role_for_npc
from tools.encounter_tools import get_possible_enemies, get_enemy_data, get_possible_hazards, get_obstacle_skill_dc, get_obstacle_hazard_stats
from agents.quest_concept_agent import get_quest_concept_creation_agent, get_quest_concept_extraction_agent
from agents.quest_summary_agent import get_quest_summary_agent
from agents.acts_agent import get_acts_creation_agent, get_acts_extraction_agent
from agents.scenes_agent import get_scenes_creation_agent, get_scenes_extraction_agent
from agents.npcs_agent import get_npcs_creation_agent, get_npcs_extraction_agent, get_npc_scenes_extraction_agent
from agents.npc_details_agent import get_npc_details_creation_agent, get_npc_details_extraction_agent
from agents.npc_skills_agent import get_npc_skills_creation_agent
from agents.npc_saves_agent import get_npc_saves_creation_agent
from agents.encounter_enemies_agent import get_encounter_enemy_agent
from agents.encounter_hazards_agent import get_encounter_hazard_agent
from agents.npc_influence_info_concept_agent import get_npc_influence_info_concept_creation_agent, get_npc_influence_info_concept_extraction_agent
from agents.npc_discoveries_concept_agent import get_npc_discoveries_concept_creation_agent, get_npc_discoveries_concept_extraction_agent
from agents.npc_influences_concept_agent import get_npc_influences_concept_creation_agent, get_npc_influences_concept_extraction_agent
from agents.npc_thresholds_agent import get_npc_thresholds_creation_agent, get_npc_thresholds_extraction_agent
from agents.obstacle_concepts_agent import get_obstacle_concepts_creation_agent, get_obstacle_concepts_extraction_agent
from agents.obstacle_skills_agent import get_obstacle_skills_agent
from agents.obstacle_hazard_stats_agent import get_obstacle_hazard_stats_agent

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
    with console.status("[bold orange1]AI Agent is extracting the quest concept data...[/bold orange1]", spinner="dots"):
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
    with console.status("[bold orange1]AI Agent is extracting quest acts...[/bold orange1]", spinner="dots"):
        result = acts_extraction_agent.run_sync(prompt)
    act_concepts = result.output

    # Verify three acts were generated, if not, regenerate acts
    while len(act_concepts) != 3:
        log_error("Incorrect number of acts generated, regenerating...")
        prompt += "\n\nRemember to create exactly 3 acts."
        with console.status("[bold cyan]AI Agent is regenerating acts for the quest...[/bold cyan]", spinner="dots"):
            raw_acts = acts_creation_agent.run_sync(prompt)
        prompt = f"Extract the summary for each of the three acts from the following quest act summaries:\n\n{raw_acts}"
        with console.status("[bold orange1]AI Agent is extracting quest acts...[/bold orange1]", spinner="dots"):
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

def generate_scenes_for_acts(current_quest: Quest):
    """
    Generates scenes for a given act.
    Creative agent generates the scenes, extraction agent converts it to a pydantic model.

    Args:
        current_quest: The Quest object to generate scenes for.
        current_act: The Act object to generate scenes for.
    
    Returns:
        Quest: The updated Quest object.
    """
    log_status(f"Generating scenes for quest acts...")

    # Instantiate the Agent for generating scenes
    scenes_creation_agent = get_scenes_creation_agent()

    for current_act in current_quest.acts:
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

        # Run the extraction agent
        scenes_extraction_agent = get_scenes_extraction_agent()
        prompt = f"Extract the summary, location, encounter type, and rest opportunity for each of the scenes from the following quest scene summaries:\n\n{raw_scenes}"
        with console.status(f"[bold orange1]AI Agent is extracting quest scenes for Act {current_act.act_number}...[/bold orange1]", spinner="dots"):
            result = scenes_extraction_agent.run_sync(prompt)
        scenes_concepts = result.output

        # Verify scenes were generated, if not, regenerate scenes for this act
        while len(scenes_concepts) < 4 or len(scenes_concepts) > 9:
            log_error(f"Incorrect number of scenes generated for Act {current_act.act_number}, regenerating...")
            prompt += "\n\nRemember to create 4 to 9 scenes."
            with console.status(f"[bold cyan]AI Agent is regenerating scenes for Act {current_act.act_number}...[/bold cyan]", spinner="dots"):
                raw_scenes = scenes_creation_agent.run_sync(prompt)
            prompt = f"Extract the summary, location, encounter type, and rest opportunity for each of the scenes from the following quest scene summaries:\n\n{raw_scenes}"
            with console.status(f"[bold orange1]AI Agent is extracting quest scenes for Act {current_act.act_number}...[/bold orange1]", spinner="dots"):
                result = scenes_extraction_agent.run_sync(prompt)
            scenes_concepts = result.output

        log_success(f'Scenes Generated for Act {current_act.act_number}...')

        # Map the generated scenes to the current act
        log_output(f'Scenes for Act {current_act.act_number}:')
        scene_number = 1
        for scene_concept in scenes_concepts:
            new_scene = Scene(
                scene_number = scene_number,
                summary = scene_concept.summary,
                location = scene_concept.location,
                encounter_type = scene_concept.encounter_type,
                rest_opportunity = scene_concept.rest_opportunity
            )
            current_act.scenes.append(new_scene)
            log_output(f" - Scene {new_scene.scene_number} ({new_scene.encounter_type}): {new_scene.summary}")
            log_output(f" - - Location: {new_scene.location}")
            log_output(f" - - Rest Opportunity: {new_scene.rest_opportunity}")
            scene_number += 1
    
    return current_quest

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
    log_status("Generating NPC list for quest...")

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

    # Run the extraction agent to get basic NPC information
    npc_extraction_agent = get_npcs_extraction_agent()
    prompt = f"Extract the NPC concepts from the following list of NPC concepts:\n\n{raw_npc_concepts}"
    with console.status("[bold orange1]AI Agent is extracting the NPC concepts...[/bold orange1]", spinner="dots"):
        result = npc_extraction_agent.run_sync(prompt)
    npc_concepts_list = result.output

    log_success('NPC concepts Generated...')

    current_quest.npcs = []

    log_output('NPCs:')

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
            quest_role = npc_concept.quest_role
        )

        log_output(f"  - NPC: {new_NPC.name}, {new_NPC.ancestry}, {new_NPC.class_name}")
        log_output(f"  - - Role: {new_NPC.quest_role}")
        log_output(f"  - - Scene Roles:")

        for scene_role in npc_scene_roles:
            new_scene_role = SceneRole(
                act_number = scene_role.act_number,
                scene_number = scene_role.scene_number,
                role = scene_role.role
            )
            log_output(f"  - - - Act: {new_scene_role.act_number}, Scene {new_scene_role.scene_number}: {new_scene_role.role}")
            new_NPC.scene_roles.append(new_scene_role)

        current_quest.npcs.append(new_NPC)

    log_success('NPCs generated...')
    
    return current_quest

def generate_npc_details(current_quest: Quest) -> Quest:
    """
    Generates the details for each NPC in the quest.

    Args:
        current_quest: The Quest object to generate NPC details for.
    
    Returns:
        Quest: The updated Quest object.
    """
    log_status("Generating NPC details for quest...")

    # Instantiate the agent for NPC details creation
    npc_details_creation_agent = get_npc_details_creation_agent()
    
    log_output("NPC Details:")

    # Iterate through each npc and send the NPC info to the creation agent then extract the data
    for npc in current_quest.npcs:
        log_output(f"  - NPC: {npc.name}")

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

        # Run the extraction agent to get basic NPC information
        npc_details_extraction_agent = get_npc_details_extraction_agent()
        prompt = f"Extract the NPC details data from the provided NPC details:\n\n{raw_npc_details}"
        with console.status(f"[bold orange1]AI Agent is extracting details data for {npc.name}...[/bold orange1]", spinner="dots"):
            result = npc_details_extraction_agent.run_sync(prompt)
        npc_details = result.output

        # Map the generated NPC details to the current NPC
        npc.appearance = npc_details.appearance
        npc.personality = npc_details.personality
        npc.behavior = npc_details.behavior
        npc.attitude = npc_details.attitude
        log_output(f"  - - Appearance: {npc.appearance}")
        log_output(f"  - - Personality: {npc.personality}")
        log_output(f"  - - Behavior: {npc.behavior}")
        log_output(f"  - - Attitude: {npc.attitude}")

    log_success("NPC details generated...")
    
    return current_quest

def generate_npc_stats(current_quest: Quest) -> Quest:
    """
    Generates the stats for each NPC in the quest.

    Args:
        current_quest: The Quest object to generate NPC stats for.
    
    Returns:
        Quest: The updated Quest object.
    """
    log_status("Generating NPC stats...")

    # Instantiate the agent for NPC skills creation
    npc_skills_agent = get_npc_skills_creation_agent()
    npc_saves_agent = get_npc_saves_creation_agent()

    log_output(f"NPC Stats:")
    
    # Iterate through each NPC, create stat block from creature_stats table
    for npc in current_quest.npcs:
        log_output(f"  - NPC: {npc.name}")

        # Get Base Stats from creature_stats table in database
        npc.stats = get_npc_base_stats(current_quest, npc)

        log_output(f"  - - Stats:")
        log_output(f"  - - - Level: {npc.stats.level}")
        log_output(f"  - - - Perception: {npc.stats.perception}")
        log_output(f"  - - - AC: {npc.stats.ac}")
        log_output(f"  - - - HP: {npc.stats.hp}")
        log_output(f"  - - - Strike: {npc.stats.strike}")
        log_output(f"  - - - Damage: {npc.stats.damage}")
        log_output(f"  - - - Spell Attack: {npc.stats.spellAttack}")
        log_output(f"  - - - Spell DC: {npc.stats.spellDC}")

        # Run the skill selection agent
        prompt = "#Quest Information:\n"
        prompt += f"Quest Summary: {current_quest.summary}\n\n"
        prompt += "# NPC Information:\n"
        prompt += f"NPC Name: {npc.name}\n"
        prompt += f"NPC Class: {npc.class_name}\n"
        prompt += f" - Class Description: {get_class_description(npc.class_name)}\n"
        prompt += f"NPC Quest Role: {npc.quest_role}\n\n"
        prompt += "# Available Skills:\n"
        prompt += f"{get_skills_with_descriptions()}\n\n"
        prompt += "Select 3 to 6 appropriate skills for this NPC based on their class and quest role"
        with console.status(f"[bold cyan]AI Agent is selecting appropriate skills for {npc.name}...[/bold cyan]", spinner="dots"):
            result = npc_skills_agent.run_sync(prompt)
        selected_skills = result.output

        while len(selected_skills) < 3 or len(selected_skills) > 6:
            log_error(f"Incorrect number of skills were generated for {npc.name}. Retrying...")
            with console.status(f"[bold cyan]AI Agent is re-generating skills for {npc.name}...[/bold cyan]", spinner="dots"):
                result = npc_skills_agent.run_sync(prompt)
            selected_skills = result.output
        
        # Assign skills as Skill models
        npc_skills = []
        for skill_name in selected_skills:
            # Use perception value because skill from creature_stats was used to determine perception
            npc_skills.append(Skill(name=skill_name, modifier=npc.stats.perception))
        npc.stats.skills = npc_skills
        log_output(f"  - - Skills:")
        for skill in npc.stats.skills:
            log_output(f"  - - - {skill.name}: {skill.modifier}")

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
        log_output(f"  - - - Saves:")
        for save in npc.stats.saves:
            log_output(f"  - - - - {save.name}: {save.modifier}")

    log_success("Quest NPC stats generated...")
    
    return current_quest

def generate_npc_influence_info(current_quest: Quest) -> Quest:
    """
    Generates the NPC influence info for each social encounter.
    
    Args:
        current_quest: The Quest object to generate NPC influence info for.
    
    Returns:
        Quest: The Quest object with NPC influence info generated.
    """
    log_status("Generating NPC influence info for quest...")

    # Get Agents
    npc_influence_info_concept_creation_agent = get_npc_influence_info_concept_creation_agent()
    npc_influence_info_concept_extraction_agent = get_npc_influence_info_concept_extraction_agent()

    npc_discoveries_concept_creation_agent = get_npc_discoveries_concept_creation_agent()
    npc_discoveries_concept_extraction_agent = get_npc_discoveries_concept_extraction_agent()

    npc_influences_concept_creation_agent = get_npc_influences_concept_creation_agent()
    npc_influences_concept_extraction_agent = get_npc_influences_concept_extraction_agent()

    npc_thresholds_creation_agent = get_npc_thresholds_creation_agent()
    npc_thresholds_extraction_agent = get_npc_thresholds_extraction_agent()
    
    log_output("Quest NPC Influence Info:")
    for act in current_quest.acts:
        for scene in act.scenes:
            if scene.encounter_type == "social" and scene.encounter.encounter_type == "social":
                log_output(f" - Act {act.act_number} Scene {scene.scene_number}")
                
                # Get NPCs in Scene
                npcs = get_npcs_for_scene(act.act_number, scene.scene_number, current_quest)
                
                scene.encounter.npc_influence_info = []

                for npc in npcs:
                    log_output(f" - - NPC Name: {npc.name}")

                    # Instantiate NPCInfluenceInfo object
                    npc_influence_info = NPCInfluenceInfo(npc_name = npc.name)

                    # Get NPC information for prompt
                    prompt_info = "# NPC Information:\n"
                    prompt_info += f" - Name: {npc.name}\n"
                    prompt_info += f" - Ancestry: {npc.ancestry}\n"
                    prompt_info += f" - Class: {npc.class_name}\n"
                    prompt_info += f" - Personality: {npc.personality}\n"
                    prompt_info += f" - Attitude: {npc.attitude}\n"
                    prompt_info += f" - Quest Role: {npc.quest_role}\n"
                    prompt_info += f" - Scene Role: {get_scene_role_for_npc(act.act_number, scene.scene_number, npc.name, current_quest)}\n\n"

                    # Generate Resistances, Weaknesses and Penalty
                    prompt_influence_concept = prompt_info + "Determine the NPC's resistances, weaknesses and penalty to different methods of influence specific to the scene."
                    with console.status(f"[bold cyan]AI Agent is generating NPC resistances, weaknesses and penalty for {npc.name}...[/bold cyan]", spinner="dots"):
                        result = npc_influence_info_concept_creation_agent.run_sync(prompt_influence_concept)
                    raw_npc_influence_concept = result.output
                    
                    # Use extraction agent to extract resistances, weaknesses and penalty
                    with console.status(f"[bold orange1]AI Agent is extracting NPC resistances, weaknesses and penalty for {npc.name}...[/bold orange1]", spinner="dots"):
                        result = npc_influence_info_concept_extraction_agent.run_sync(raw_npc_influence_concept)
                    npc_influence_concept = result.output
                    
                    npc_influence_info.resistances = npc_influence_concept.resistances
                    npc_influence_info.weaknesses = npc_influence_concept.weaknesses
                    npc_influence_info.penalty = Penalty(
                        description = npc_influence_concept.penalty,
                        penalty = f"Reduce the number of rounds the party has to influence {npc.name} by 1.",
                    )
                    log_output(f" - - - Resistances: {npc_influence_info.resistances}")
                    log_output(f" - - - Weaknesses: {npc_influence_info.weaknesses}")
                    log_output(f" - - - Penalty: {npc_influence_info.penalty.description}")

                    prompt_skills = "# Available Skills:\n\n" + get_skills_with_descriptions() + "\n\n"

                    # Generate Discoveries
                    prompt_discoveries_concept = prompt_info + prompt_skills + "Select 2 to 3 skills from the list of skills that can be used to discover methods of influencing the NPC specific to this scene. Determine the difficulty for each skill (easy, moderate, or hard)."
                    with console.status(f"[bold cyan]AI Agent is generating NPC discoveries for {npc.name}...[/bold cyan]", spinner="dots"):
                        result = npc_discoveries_concept_creation_agent.run_sync(prompt_discoveries_concept)
                    raw_npc_discoveries_concept = result.output
                    
                    # Use extraction agent to extract discoveries
                    with console.status(f"[bold orange1]AI Agent is extracting NPC discoveries for {npc.name}...[/bold orange1]", spinner="dots"):
                        result = npc_discoveries_concept_extraction_agent.run_sync(raw_npc_discoveries_concept)
                    npc_discoveries_concept = result.output

                    while len(npc_discoveries_concept) < 2 or len(npc_discoveries_concept) > 3:
                        log_error(f"Incorrect number of discoveries were generated for {npc.name}. Retrying...")
                        with console.status(f"[bold cyan]AI Agent is re-generating discoveries for {npc.name}...[/bold cyan]", spinner="dots"):
                            result = npc_discoveries_concept_creation_agent.run_sync(prompt_discoveries_concept)
                        raw_npc_discoveries_concept = result.output

                        with console.status(f"[bold orange1]AI Agent is re-extracting discoveries for {npc.name}...[/bold orange1]", spinner="dots"):
                            result = npc_discoveries_concept_extraction_agent.run_sync(raw_npc_discoveries_concept)
                        npc_discoveries_concept = result.output

                    # Assign discoveries to NPCInfluenceInfo
                    npc_influence_info.discoveries = []
                    npc_influence_info.discoveries.append(Discovery(
                        skill = "Perception",
                        dc = get_npc_influence_dc(npc.stats.level, "moderate"),
                    ))
                    for discovery in npc_discoveries_concept:
                        npc_influence_info.discoveries.append(Discovery(
                            skill = discovery.skill,
                            dc = get_npc_influence_dc(npc.stats.level, discovery.difficulty),
                        ))
                    log_output(f" - - - Discoveries:")
                    for discovery in npc_influence_info.discoveries:
                        log_output(f" - - - - Skill: {discovery.skill} - DC: {discovery.dc}")

                    # Generate Influences
                    prompt_influences_concept = prompt_info + prompt_skills + "Select 3 to 4 skills from the list of skills that can be used to influence the NPC specific to this scene. Determine the difficulty to influence the NPC with each skill (easy, moderate, or hard)."
                    with console.status(f"[bold cyan]AI Agent is generating NPC influences for {npc.name}...[/bold cyan]", spinner="dots"):
                        result = npc_influences_concept_creation_agent.run_sync(prompt_influences_concept)
                    raw_npc_influences_concept = result.output
                    
                    # Use extraction agent to extract influences
                    with console.status(f"[bold orange1]AI Agent is extracting NPC influences for {npc.name}...[/bold orange1]", spinner="dots"):
                        result = npc_influences_concept_extraction_agent.run_sync(raw_npc_influences_concept)
                    npc_influences_concept = result.output

                    while len(npc_influences_concept) < 3 or len(npc_influences_concept) > 4:
                        log_error(f"Incorrect number of influences were generated for {npc.name}. Retrying...")
                        with console.status(f"[bold cyan]AI Agent is re-generating influences for {npc.name}...[/bold cyan]", spinner="dots"):
                            result = npc_influences_concept_creation_agent.run_sync(prompt_influences_concept)
                        raw_npc_influences_concept = result.output

                        with console.status(f"[bold orange1]AI Agent is re-extracting influences for {npc.name}...[/bold orange1]", spinner="dots"):
                            result = npc_influences_concept_extraction_agent.run_sync(raw_npc_influences_concept)
                        npc_influences_concept = result.output

                    # Assign influences to NPCInfluenceInfo
                    npc_influence_info.influences = []
                    for influence in npc_influences_concept:
                        npc_influence_info.influences.append(Influence(
                            skill = influence.skill,
                            dc = get_npc_influence_dc(npc.stats.level, influence.difficulty),
                        ))
                    log_output(f" - - - Influences:")
                    for influence in npc_influence_info.influences:
                        log_output(f" - - - - Skill: {influence.skill} - DC: {influence.dc}")

                    # Generate Thresholds
                    prompt_thresholds = prompt_info + "Determine the boons that can be granted by the NPC if they are successfully influenced at each Threshold (four successes: minor boon, six successes: boon, eight successes: major boon)."
                    with console.status(f"[bold cyan]AI Agent is generating NPC thresholds for {npc.name}...[/bold cyan]", spinner="dots"):
                        result = npc_thresholds_creation_agent.run_sync(prompt_thresholds)
                    raw_npc_thresholds = result.output
                    
                    # Use extraction agent to extract thresholds
                    with console.status(f"[bold orange1]AI Agent is extracting NPC thresholds for {npc.name}...[/bold orange1]", spinner="dots"):
                        result = npc_thresholds_extraction_agent.run_sync(raw_npc_thresholds)
                    npc_thresholds = result.output

                    # Assign thresholds to NPCInfluenceInfo
                    npc_influence_info.thresholds = npc_thresholds
                    log_output(f" - - - Thresholds:")
                    log_output(f" - - - - 4 Successes: {npc_influence_info.thresholds.four}")
                    log_output(f" - - - - 6 Successes: {npc_influence_info.thresholds.six}")
                    log_output(f" - - - - 8 Successes: {npc_influence_info.thresholds.eight}")

                    # Assign to scene.encounter.npc_influence_info
                    scene.encounter.npc_influence_info.append(npc_influence_info)
            else:
                continue
    
    log_success("Quest NPC influence info generated...")
    
    return current_quest

def generate_encounter_enemies(current_quest: Quest):
    log_status("Generating encounter enemies for quest...")
    
    # Instantiate the Agent
    encounter_enemies_agent = get_encounter_enemy_agent()

    log_output("Selected Combat Encounter Enemies:")
    # Iterate through each encounter
    for act in current_quest.acts:
        for scene in act.scenes:
            if scene.encounter_type == "combat" and scene.encounter.encounter_type == "combat":
                # Get a list of enemies that fall under the encounter experience budget and where the encounter
                # budget is cleanly divisible by the xp_value of the enemy. This cheats the enemy selection by
                # letting the agent select the most fitting enemy, rather than selecting multiple enemies that fit a budget.
                # We can then use the xp_value to determine the number of enemies in the encounter.
                possible_enemies = get_possible_enemies(current_quest.party_level, scene.encounter.xp_budget)
                
                prompt = "# Quest Information:\n"
                prompt += f"Quest Theme: {current_quest.theme}\n"
                prompt += f"Quest Setting: {current_quest.setting}\n"
                prompt += f"Quest Summary: {current_quest.summary}\n\n"
                prompt += "# Act Information:\n"
                prompt += f"Act Summary: {act.summary}\n\n"
                prompt += "# Scene Information:\n"
                prompt += f"Scene Summary: {scene.summary}\n"
                prompt += f"Scene Location: {scene.location}\n\n"
                prompt += "# Available Enemies:\n"
                for enemy in possible_enemies:
                    prompt += f"Name: {enemy.name}\n"
                    prompt += f"- Description: {enemy.description}\n"
                prompt += "# Task:\n\n"
                prompt += "Select the most appropriate enemy for the scene."
                
                with console.status(f"[bold cyan]AI Agent is selecting appropriate enemy for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                    result = encounter_enemies_agent.run_sync(prompt)
                enemy_name = result.output.strip()
                
                selected_enemy = next((enemy for enemy in possible_enemies if enemy.name == enemy_name), None)

                if selected_enemy is None:
                    log_error(f"Enemy name provided by agent ({enemy_name}) did not match any of the available enemies. Trying again...")
                    prompt += "Remember that you must select an enemy from the available enemies list and output the exact name of the enemy. Do not output the count of enemies or any other information."
    
                while selected_enemy is None:
                    with console.status(f"[bold cyan]AI Agent is re-selecting appropriate enemy for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                        result = encounter_enemies_agent.run_sync(prompt)
                    enemy_name = result.output
                    
                    selected_enemy = next((enemy for enemy in possible_enemies if enemy.name == enemy_name), None)

                enemy_count = scene.encounter.xp_budget // selected_enemy.xp_value
                for _ in range(max(enemy_count, 1)):
                    scene.encounter.enemies.append(selected_enemy)

                # Log chosen enemies for encounter
                log_output(f" - Act {act.act_number}, Scene {scene.scene_number} - {selected_enemy.name} ({selected_enemy.xp_value} XP) x {enemy_count}")
            else:
                pass

    log_success("Quest combat encounter enemies selected...")
    
    return current_quest

def generate_encounter_hazards(current_quest: Quest) -> Quest:
    """
    Generates the hazards for each hazard type encounter.

    Args:
        current_quest: The Quest object to generate hazards for.
    
    Returns:
        Quest: The Quest object with hazards generated.
    """
    log_status("Generating encounter hazards for quest...")
    
    log_output("Quest Hazard Encounters:")
    for act in current_quest.acts:
        for scene in act.scenes:
            if scene.encounter_type == "hazard" and scene.encounter.encounter_type == "hazard":
                possible_hazards = get_possible_hazards(scene.encounter.level)
                if not possible_hazards:
                    log_error(f"No hazards found for encounter level {scene.encounter.level}.")
                    continue
                elif len(possible_hazards) == 1:
                    selected_hazard = possible_hazards[0]
                else:
                    encounter_hazard_agent = get_encounter_hazard_agent()
                    prompt = "# Quest Information:\n"
                    prompt += f"Quest Theme: {current_quest.theme}\n"
                    prompt += f"Quest Setting: {current_quest.setting}\n"
                    prompt += f"Quest Summary: {current_quest.summary}\n\n"
                    prompt += "# Act Information:\n"
                    prompt += f"Act Summary: {act.summary}\n\n"
                    prompt += "# Scene Information:\n"
                    prompt += f"Scene Summary: {scene.summary}\n"
                    prompt += f"Scene Location: {scene.location}\n\n"
                    prompt += "# Available Hazards:\n"
                    for hazard in possible_hazards:
                        prompt += f"Name: {hazard.name}\n"
                        prompt += f"- Description: {hazard.description}\n"
                    prompt += "# Task:\n\n"
                    prompt += "Select the most appropriate hazard for the scene."
                    
                    with console.status(f"[bold cyan]AI Agent is selecting appropriate hazard for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                        result = encounter_hazard_agent.run_sync(prompt)
                    hazard_name = result.output
                    
                    selected_hazard = next((hazard for hazard in possible_hazards if hazard.name == hazard_name), None)

                    if selected_hazard is None:
                        log_error(f"Hazard name provided by agent ({hazard_name}) did not match any of the available hazards. Trying again...")
                        prompt += "Remember that you must select a hazard from the available hazards list and output the exact name of the hazard. Do not output the count of hazards or any other information."
            
                    while selected_hazard is None:
                        with console.status(f"[bold cyan]AI Agent is re-selecting appropriate hazard for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                            result = encounter_hazard_agent.run_sync(prompt)
                        hazard_name = result.output
                        
                        selected_hazard = next((hazard for hazard in possible_hazards if hazard.name == hazard_name), None)
                
                scene.encounter.hazard = selected_hazard
                log_output(f" - Act {act.act_number}, Scene {scene.scene_number} - {selected_hazard.name} (Level {selected_hazard.level})")

    log_success("Quest hazard encounters generated...")

    return current_quest

def generate_quest_obstacles(current_quest: Quest) -> Quest:
    """
    Generates the obstacles for each skill challenge scene in the quest.

    Args:
        current_quest: The Quest object to generate obstacles for.
    
    Returns:
        Quest: The Quest object with obstacles generated.
    """
    log_status("Generating obstacles for quest...")

    obstacle_concepts_creation_agent = get_obstacle_concepts_creation_agent()
    obstacle_concepts_extraction_agent = get_obstacle_concepts_extraction_agent()

    obstacle_skills_agent = get_obstacle_skills_agent()

    obstacle_hazard_stats_agent = get_obstacle_hazard_stats_agent()
    
    log_output("Quest Obstacles:")
    for act in current_quest.acts:
        for scene in act.scenes:
            if scene.encounter_type == "skill challenge" and scene.encounter.encounter_type == "skill challenge":
                log_output(f" - Act {act.act_number}, Scene {scene.scene_number}:")

                # Get list of obstacles
                prompt = "# Scene Information:\n"
                prompt += f" - Summary: {scene.summary}\n"
                prompt += f" - Location: {scene.location}\n\n"
                prompt += "# Task:\n"
                prompt += "Create a series of 6 to 10 obstacles for the players to overcome in the current scene."

                with console.status(f"[bold cyan]AI Agent is creating obstacles for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                    result = obstacle_concepts_creation_agent.run_sync(prompt)
                raw_obstacle_concepts = result.output

                with console.status(f"[bold orange1]AI Agent is extracting obstacles for Act {act.act_number}, Scene {scene.scene_number}...[/bold orange1]", spinner="dots"):
                    result = obstacle_concepts_extraction_agent.run_sync(raw_obstacle_concepts)
                obstacle_concepts = result.output

                while len(obstacle_concepts) < 6 or len(obstacle_concepts) > 10:
                    log_error(f"Incorrect number of obstacles were generated for Act {act.act_number}, Scene {scene.scene_number}. Retrying...")
                    with console.status(f"[bold orange1]AI Agent is re-generating obstacles for Act {act.act_number}, Scene {scene.scene_number}...[/bold orange1]", spinner="dots"):
                        result = obstacle_concepts_creation_agent.run_sync(prompt)
                    raw_obstacle_concepts = result.output

                    with console.status(f"[bold orange1]AI Agent is re-extracting obstacles for Act {act.act_number}, Scene {scene.scene_number}...[/bold orange1]", spinner="dots"):
                        result = obstacle_concepts_extraction_agent.run_sync(raw_obstacle_concepts)
                    obstacle_concepts = result.output
                
                scene.encounter.obstacles = []
                for obstacle_concept in obstacle_concepts:
                    obstacle = Obstacle(
                        name = obstacle_concept.name,
                        description = obstacle_concept.description,
                        success_resolution = obstacle_concept.success_resolution,
                        failure_resolution = obstacle_concept.failure_resolution,
                        is_hazard = obstacle_concept.is_hazard
                    )

                    log_output(f" - - {obstacle.name}: {obstacle.description}")
                    log_output(f" - - - Success: {obstacle.success_resolution}")
                    log_output(f" - - - Failure: {obstacle.failure_resolution}")
                    
                    # Get skills to overcome the obstacle
                    prompt = "# Obstacle Information:\n"
                    prompt += f" - Name: {obstacle.name}\n"
                    prompt += f" - Description: {obstacle.description}\n"
                    prompt += f" - Success Resolution: {obstacle.success_resolution}\n"
                    prompt += f" - Failure Resolution: {obstacle.failure_resolution}\n\n"
                    prompt += "# Available Skills:\n\n"
                    prompt += get_skills_with_descriptions() + "\n\n"
                    prompt += "# Task:\n"
                    prompt += "Create a list of four skills with their difficulties from the available skills that could be used to overcome the obstacle."
                                      
                    with console.status(f"[bold cyan]AI Agent is selecting skills for obstacle "
                        f"'{obstacle.name}' in Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", 
                        spinner="dots"):  
                        result = obstacle_skills_agent.run_sync(prompt)
                    obstacle_skills = result.output

                    while len(obstacle_skills) != 4:
                        log_error(f"Incorrect number of skills were generated for obstacle '{obstacle.name}' in Act {act.act_number}, Scene {scene.scene_number}. Retrying...")
                        with console.status(f"[bold cyan]AI Agent is re-generating skills for obstacle '{obstacle.name}' in Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):  
                            result = obstacle_skills_agent.run_sync(prompt)
                        obstacle_skills = result.output

                    log_output(" - - - Skills:")
                    for skill in obstacle_skills:
                        obstacle_skill = ObstacleSkill(
                            skill = skill.skill,
                            difficulty = get_obstacle_skill_dc(scene.encounter.level, skill.difficulty)
                        )
                        log_output(f" - - - - {obstacle_skill.skill}: DC {obstacle_skill.difficulty}")
                        obstacle.skills.append(obstacle_skill)
                    
                    log_output(f" - - - Is Hazard: {obstacle.is_hazard}")
                    if obstacle.is_hazard:
                        log_output(" - - - Hazard Stats:")

                        # Get hazard stats
                        prompt = "# Hazardous Obstacle Information:\n"
                        prompt += f" - Name: {obstacle.name}\n"
                        prompt += f" - Description: {obstacle.description}\n"
                        prompt += f" - Success Resolution: {obstacle.success_resolution}\n"
                        prompt += f" - Failure Resolution: {obstacle.failure_resolution}\n\n"
                        prompt += "# Task:\n"
                        prompt += "Determine the hazard type and save type for the hazard."

                        with console.status(f"[bold cyan]AI Agent is determining the hazard type and save type for the obstacle "
                            f"'{obstacle.name}' in Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", 
                            spinner="dots"):
                            result = obstacle_hazard_stats_agent.run_sync(prompt)
                        hazard_stats = result.output

                        obstacle.hazard_stats = get_obstacle_hazard_stats(hazard_stats.hazard_type, hazard_stats.save_type, max(-1, scene.encounter.level))
                        
                        log_output(f" - - - - Hazard Level: {obstacle.hazard_stats.level}")
                        log_output(f" - - - - Hazard Type: {obstacle.hazard_stats.hazard_type}")
                        log_output(f" - - - - Attack: {obstacle.hazard_stats.attack}")
                        log_output(f" - - - - Damage: {obstacle.hazard_stats.damage}")
                        log_output(f" - - - - Save Type: {obstacle.hazard_stats.save_type}")
                        log_output(f" - - - - Save DC: {obstacle.hazard_stats.area_dc}")            
            
                    scene.encounter.obstacles.append(obstacle)

    log_success("Quest obstacles generated...")

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

def load_quest_from_file(file: str) -> Quest:
    """
    Loads a quest from a file for debugging purposes.

    Args:
        filename: The name of the file to load the quest from.
    
    Returns:
        The Quest object loaded from the file.
    """
    log_status(f"Loading existing quest from file: {file}...")
    with open(file, "r") as f:
        quest = Quest.model_validate_json(f.read())
    log_success("Quest loaded successfully...")
    return quest

def generate_quest():
    # Reset log
    log_clear()

    # Start timer
    start_time = time.time()
    
    # Verify DB first
    if not check_database():
        log_error("Database verification failed... Exiting.")
        return

    log_status("Beginning quest generation...")

    # Set up initial quest object
    current_quest = Quest(player_count=4, party_level=1)

    # Generate the quest concept
    current_quest = generate_quest_concept(current_quest)

    # Generate the quest summary
    current_quest = generate_quest_summary(current_quest)
    
    # Generate the acts
    current_quest = generate_acts(current_quest)
    
    # Generate scenes for each act
    current_quest = generate_scenes_for_acts(current_quest)

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

    # Generate combat encounter enemies
    current_quest = generate_encounter_enemies(current_quest)

    # Generate hazard encounters
    current_quest = generate_encounter_hazards(current_quest)

    # Generate NPC influence information for social encounters
    current_quest = generate_npc_influence_info(current_quest)
    
    #current_quest = load_quest_from_file("output/The_Flickering_Veil.json")

    # Generate quest obstacles
    current_quest = generate_quest_obstacles(current_quest)

    write_quest_to_file(current_quest)

    end_time = time.time()
    elapsed = end_time - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    log_success(f"Module generation complete in {minutes}m {seconds}s")

if __name__ == "__main__":
    generate_quest()
