from tools.log_tools import *
from tools.npc_tools import get_npc_base_stats, get_npc_saves, get_ancestry_description, get_class_description, get_ancestries_with_descriptions, get_classes_with_descriptions, get_skills_with_descriptions, get_npcs_for_scene, get_npc_influence_dc, get_scene_role_for_npc
from tools.quest_tools import scene_has_npc
from tools.name_tools import get_npc_name
from models.quest import Quest
from models.npc import NPC, SceneRole, Skill
from models.npc_influence import Discovery, Influence, Penalty, NPCInfluenceInfo
from agents.npc_list_agent import get_npc_list_creation_agent, get_npc_list_extraction_agent
from agents.npc_identifier_agent import get_npc_identifier_agent
from agents.npcs_agent import get_npcs_creation_agent, get_npcs_extraction_agent
from agents.npc_ancestry_agent import get_npc_ancestry_agent
from agents.npc_class_agent import get_npc_class_agent
from agents.npc_quest_role_agent import get_npc_quest_role_agent
from agents.npc_scene_role_agent import get_npc_scene_role_agent
from agents.npc_details_agent import get_npc_details_creation_agent, get_npc_details_extraction_agent
from agents.npc_skills_agent import get_npc_skills_creation_agent
from agents.npc_saves_agent import get_npc_saves_creation_agent
from agents.npc_influence_info_concept_agent import get_npc_influence_info_concept_creation_agent, get_npc_influence_info_concept_extraction_agent
from agents.npc_discoveries_concept_agent import get_npc_discoveries_concept_creation_agent, get_npc_discoveries_concept_extraction_agent
from agents.npc_influences_concept_agent import get_npc_influences_concept_creation_agent, get_npc_influences_concept_extraction_agent
from agents.npc_thresholds_agent import get_npc_thresholds_creation_agent, get_npc_thresholds_extraction_agent

def generate_quest_npc_list(current_quest: Quest) -> Quest:
    """
    Generates a list of NPCs to be created for the quest from the scene summaries.
    Creative agent generates the basic NPC concepts (identifiers and scenes), extraction agent converts it to a pydantic model.
    """
    log_status("Generating NPC list for quest...")

    # Instantiate the agent for NPC creation
    npc_list_creation_agent = get_npc_list_creation_agent()
    npc_list_extraction_agent = get_npc_list_extraction_agent()
    
    prompt = "# Scene Summaries\n\n"
    for act in current_quest.acts:
        for scene in act.scenes:
            prompt += f"Act {act.act_number}, Scene {scene.scene_number}: {scene.summary}\n\n"
    
    prompt += "Identify and list the npcs to be created for the quest with the scenes they're in based on the scene summaries provided above."
    
    with console.status("[bold cyan]AI Agent is generating the NPC list for the quest...[/bold cyan]", spinner="dots"):
        result = npc_list_creation_agent.run_sync(prompt)
    raw_npc_list = result.output

    with console.status("[bold cyan]AI Agent is extracting NPC data...[/bold cyan]", spinner="dots"):
        result = npc_list_extraction_agent.run_sync(f"Extract the NPC data from the following NPC list:\n\n{raw_npc_list}")
    npc_list = result.output
    
    # Verify NPC list was generated if needed
    number_of_social_scenes = 0
    for act in current_quest.acts:
        for scene in act.scenes:
            if scene.encounter_type == "social":
                number_of_social_scenes += 1
    
    while len(npc_list) == 0 and number_of_social_scenes > 0:
        log_error("Not enough NPCs were generated, regenerating...")
        with console.status("[bold cyan]AI Agent is regenerating the NPC list for the quest...[/bold cyan]", spinner="dots"):
            raw_npc_list = npc_list_creation_agent.run_sync(prompt)
        with console.status("[bold cyan]AI Agent is extracting NPC data...[/bold cyan]", spinner="dots"):
            result = npc_list_extraction_agent.run_sync(f"Extract the NPC data from the following NPC list:\n\n{raw_npc_list}")
        npc_list = result.output

    log_success(f'NPC list generated...')

    # Map the generated NPCs to the current quest
    log_output(f'NPCs for quest:')
    for npc in npc_list:
        output_string = f" - {npc.identifier}"
        scene_roles = []
        for scene in npc.scenes:
            output_string += f", Act {scene[0]}, Scene {scene[1]}"
            scene_roles.append(
                SceneRole(
                    act_number = scene[0],
                    scene_number = scene[1]
                )
            )
        new_npc = NPC(
            identifier = npc.identifier,
            scene_roles = scene_roles
        )
        current_quest.npcs.append(new_npc)
        log_output(output_string)

    return current_quest

def generate_npc_basic_information(current_quest: Quest) -> Quest:
    """
    Generates the basic information (name and ancestry) for each NPC in the quest.

    Args:
        current_quest: The Quest object to generate NPC basic information for.
    
    Returns:
        Quest: The updated Quest object.
    """
    log_status("Generating basic information for NPCs in the quest...")
    
    # Instantiate the Agent for generating NPCs
    npc_ancestry_agent = get_npc_ancestry_agent()
    
    log_output("NPC Basic Information:")

    for npc in current_quest.npcs:
        log_output(f" - {npc.identifier}:")
        
        # Generate the prompt for the npc_basic_information_agent
        prompt = "# Quest Information:\n"
        prompt += f"Quest Theme: {current_quest.theme}\n"
        prompt += f"Quest Setting: {current_quest.setting}\n"
        prompt += f"Quest Summary: {current_quest.summary}\n\n"
        
        # Add available ancestries
        prompt += "# Available Ancestries:\n"
        prompt += get_ancestries_with_descriptions()
        prompt += "\n"

        prompt += "# NPC Information:\n"
        prompt += f"Description: {npc.identifier}\n"

        prompt += "Select an ancestry for the NPC from the list above."

        with console.status(f"[bold cyan]AI Agent is generating basic information for NPC '{npc.identifier}'...[/bold cyan]", spinner="dots"):
            result = npc_ancestry_agent.run_sync(prompt)
        npc_ancestry = result.output.strip()

        while get_ancestry_description(npc_ancestry) == "No description was provided in the database.":
            log_error("Invalid ancestry provided by agent. Regenerating...")
            with console.status(f"[bold cyan]AI Agent is regenerating ancestry for {npc.identifier}...[/bold cyan]", spinner="dots"):
                result = npc_ancestry_agent.run_sync(prompt)
            npc_ancestry = result.output.strip()

        # Assign the generated basic information to the NPC
        npc.ancestry = npc_ancestry
        npc_name = get_npc_name(npc_ancestry)

        npc_names = []
        for npc in current_quest.npcs:
            npc_names.append(npc.name)

        while npc_name in npc_names:
            log_error("Duplicate name generated. Regenerating...")
            npc_name = get_npc_name(npc_ancestry)

        npc.name = npc_name

        output_string = f" - - {npc.name} ({npc.ancestry})"
        log_output(output_string)

    log_success("NPC basic information generated...")

    return current_quest

def remove_npcs_without_scene_roles(current_quest: Quest) -> Quest:
    """
    Removes NPCs that don't have any scene roles.

    Args:
        current_quest: The Quest object to remove NPCs without scene roles for.
    
    Returns:
        Quest: The updated Quest object.
    """
    log_status("Removing NPCs without scene roles...")
    
    # Filter out NPCs without scene roles
    current_quest.npcs = [npc for npc in current_quest.npcs if npc.scene_roles and len(npc.scene_roles) > 0]
    
    log_success("NPCs without scene roles removed...")
    
    return current_quest

def generate_npc_quest_roles(current_quest: Quest) -> Quest:
    """
    Generates the quest role for each NPC in the quest.

    Args:
        current_quest: The Quest object to generate NPC quest roles for.
    
    Returns:
        Quest: The updated Quest object.
    """
    log_status("Generating NPC quest roles...")

    npc_quest_role_agent = get_npc_quest_role_agent()

    log_output("NPC Quest Roles:")

    for npc in current_quest.npcs:
        prompt = "# Quest Information:\n"
        prompt += f"Quest Theme: {current_quest.theme}\n"
        prompt += f"Quest Setting: {current_quest.setting}\n"
        prompt += f"Quest Summary: {current_quest.summary}\n\n"

        prompt += "# NPC Information:\n"
        prompt += f"Name: {npc.name}\n"
        prompt += f"Ancestry: {npc.ancestry}\n"
        prompt += f"Identifier: {npc.identifier}\n\n"

        prompt += "# Scene Summaries:\n"
        for scene_role in npc.scene_roles:
            current_act = current_quest.acts[scene_role.act_number - 1]
            current_scene = current_act.scenes[scene_role.scene_number - 1]
            prompt += f"  - Act {scene_role.act_number}, Scene {scene_role.scene_number} Summary: {current_scene.summary}\n"
        prompt += "\n"
        
        prompt += f"Write a detailed description of the quest role the NPC '{npc.name}' plays in this quest."

        with console.status(f"[bold cyan]AI Agent is generating the quest role for the NPC '{npc.name}'...[/bold cyan]", spinner="dots"):
            result = npc_quest_role_agent.run_sync(prompt)
        npc.quest_role = result.output.strip()

        log_output(f" - {npc.name}: {npc.quest_role}")

    log_success("NPC quest roles generated...")

    return current_quest

def generate_npc_scene_roles(current_quest: Quest) -> Quest:
    """
    Generates scene roles for each NPC in the quest based on the NPC's quest role and scene summary.

    Args:
        current_quest: The Quest object to generate NPC scene roles for.
    
    Returns:
        Quest: The updated Quest object.
    """
    log_status("Generating NPC scene roles for quest...")

    npc_scene_role_agent = get_npc_scene_role_agent()

    log_output("NPC Scene Roles:")

    for npc in current_quest.npcs:
        log_output(f" - {npc.name}:")
        for scene_role in npc.scene_roles:
            current_act = current_quest.acts[scene_role.act_number - 1]
            current_scene = current_act.scenes[scene_role.scene_number - 1]
            
            prompt = "# Quest Information:\n"
            prompt += f"Quest Theme: {current_quest.theme}\n"
            prompt += f"Quest Setting: {current_quest.setting}\n"
            prompt += f"Quest Summary: {current_quest.summary}\n\n"

            prompt += "# Act Summary:\n"
            prompt += f"Act {current_act.act_number} Summary: {current_act.summary}\n\n"

            prompt += "# Scene Summary:\n"
            prompt += f"Scene {current_scene.scene_number} Summary: {current_scene.summary}\n\n"
            
            prompt += "# NPC Information:\n"
            prompt += f"Name: {npc.name}\n"
            prompt += f"Ancestry: {npc.ancestry}\n"
            prompt += f"Identifier: {npc.identifier}\n"
            prompt += f"Quest Role: {npc.quest_role}\n\n"

            prompt += f"Write a detailed description of the role the NPC '{npc.name}' plays in this scene, Act {current_act.act_number}, Scene {current_scene.scene_number}."
            
            with console.status(f"[bold cyan]AI Agent is generating Act {current_act.act_number}, Scene {current_scene.scene_number} scene role for the NPC '{npc.name}'...[/bold cyan]", spinner="dots"):
                result = npc_scene_role_agent.run_sync(prompt, deps=current_quest)
            scene_role.role = result.output.strip()
            
            log_output(f" - - Act {current_act.act_number}, Scene {current_scene.scene_number}: {scene_role.role}")

    log_success("NPC scene roles generated...")

    return current_quest

def generate_npc_classes(current_quest: Quest) -> Quest:
    """
    Generates the class for each NPC in the quest.

    Args:
        current_quest: The Quest object to generate NPC classes for.
    
    Returns:
        Quest: The updated Quest object.
    """
    log_status("Generating NPC classes for quest...")
    
    npc_class_agent = get_npc_class_agent()
    
    log_output("NPC Classes:")

    for npc in current_quest.npcs:
        prompt = "# Quest Information:\n"
        prompt += f"Quest Theme: {current_quest.theme}\n"
        prompt += f"Quest Setting: {current_quest.setting}\n"
        prompt += f"Quest Summary: {current_quest.summary}\n\n"

        prompt += "# Available classes\n"
        prompt += get_classes_with_descriptions()

        prompt += "# NPC Information:\n"
        prompt += f"Name: {npc.name}\n"
        prompt += f"Ancestry: {npc.ancestry}\n"
        prompt += f"Identifier: {npc.identifier}\n"
        prompt += f"Quest Role: {npc.quest_role}\n\n"

        prompt += "Select and return the single most appropriate class name from the list above for the NPC in this quest."

        with console.status(f"[bold cyan]AI Agent is generating class for {npc.name}...[/bold cyan]", spinner="dots"):
            result = npc_class_agent.run_sync(prompt)
        class_name = result.output.strip()

        while get_class_description(class_name) == "No description was provided in the database.":
            log_error("Invalid class name provided by agent. Regenerating...")
            with console.status(f"[bold cyan]AI Agent is regenerating class for {npc.name}...[/bold cyan]", spinner="dots"):
                result = npc_class_agent.run_sync(prompt)
            class_name = result.output.strip()

        npc.class_name = class_name

        log_output(f" - {npc.name}: {npc.class_name}")

    log_success("NPC classes generated...")
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
    npc_details_extraction_agent = get_npc_details_extraction_agent()
    
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
        prompt += f"NPC Identifier: {npc.identifier}\n"
        prompt += f"NPC Ancestry: {npc.ancestry}\n"
        prompt += f" - Ancestry Description: {get_ancestry_description(npc.ancestry)}\n"
        prompt += f"NPC Class: {npc.class_name}\n"
        prompt += f" - Class Description: {get_class_description(npc.class_name)}\n"
        prompt += f"NPC Quest Role: {npc.quest_role}\n\n"

        prompt += "Generate the details (appearance, personality, behavior, attitude) for the NPC in this quest."
        
        with console.status(f"[bold cyan]AI Agent is generating details for {npc.name}...[/bold cyan]", spinner="dots"):
            result = npc_details_creation_agent.run_sync(prompt)
        raw_npc_details = result.output

        # Run the extraction agent to get basic NPC information
        prompt = f"Extract the NPC details data from the provided NPC details:\n\n{raw_npc_details}"
        with console.status(f"[bold cyan]AI Agent is extracting details data for {npc.name}...[/bold cyan]", spinner="dots"):
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
                    with console.status(f"[bold cyan]AI Agent is extracting NPC resistances, weaknesses and penalty for {npc.name}...[/bold cyan]", spinner="dots"):
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
                    with console.status(f"[bold cyan]AI Agent is extracting NPC discoveries for {npc.name}...[/bold cyan]", spinner="dots"):
                        result = npc_discoveries_concept_extraction_agent.run_sync(raw_npc_discoveries_concept)
                    npc_discoveries_concept = result.output

                    while len(npc_discoveries_concept) < 2 or len(npc_discoveries_concept) > 3:
                        log_error(f"Incorrect number of discoveries were generated for {npc.name}. Retrying...")
                        with console.status(f"[bold cyan]AI Agent is re-generating discoveries for {npc.name}...[/bold cyan]", spinner="dots"):
                            result = npc_discoveries_concept_creation_agent.run_sync(prompt_discoveries_concept)
                        raw_npc_discoveries_concept = result.output

                        with console.status(f"[bold cyan]AI Agent is re-extracting discoveries for {npc.name}...[/bold cyan]", spinner="dots"):
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
                    with console.status(f"[bold cyan]AI Agent is extracting NPC influences for {npc.name}...[/bold cyan]", spinner="dots"):
                        result = npc_influences_concept_extraction_agent.run_sync(raw_npc_influences_concept)
                    npc_influences_concept = result.output

                    while len(npc_influences_concept) < 3 or len(npc_influences_concept) > 4:
                        log_error(f"Incorrect number of influences were generated for {npc.name}. Retrying...")
                        with console.status(f"[bold cyan]AI Agent is re-generating influences for {npc.name}...[/bold cyan]", spinner="dots"):
                            result = npc_influences_concept_creation_agent.run_sync(prompt_influences_concept)
                        raw_npc_influences_concept = result.output

                        with console.status(f"[bold cyan]AI Agent is re-extracting influences for {npc.name}...[/bold cyan]", spinner="dots"):
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
                    with console.status(f"[bold cyan]AI Agent is extracting NPC thresholds for {npc.name}...[/bold cyan]", spinner="dots"):
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

                    # Set the number of rounds to influence the NPC: default 2 + 4 * the number of NPCs rounds
                    scene.encounter.rounds = 2 + (4 * len(scene.encounter.npc_influence_info))
                    log_output(f" - Rounds: {scene.encounter.rounds}")
                    
                    # Set the GM Information for the encounter
                    scene.encounter.gm_information = f"A social encounter uses the NPC Influence subsystem found at https://2e.aonprd.com/Rules.aspx?ID=3040. The players have a limited number of rounds ({scene.encounter.rounds}) to influence the NPCs, attempting a skill check each round against an NPC of their choice. A critical success earns the party 2 influence points. A success earns the party 1 influence point. A failure results in nothing happening. A critical failure results in the loss of an influence point. Each NPC has a set of boon thresholds. When the party reaches a threshold, they gain the associated boon. Boons should be largely narrative in nature, so use your best judgement as a gamemaster when determining what rewarding the party with a boon entails."
            else:
                continue
    
    log_success("Quest NPC influence info generated...")
    
    return current_quest