from tools.log_tools import *
from tools.quest_tools import scene_has_npc
from models.quest import Quest
from models.act import Act
from models.scene import Scene
from models.scene_concept import SceneConcept
from models.npc import NPC, SceneRole
from agents.scene_type_agent import get_scene_type_agent
from agents.scene_rest_opportunity_agent import get_scene_rest_opportunity_agent
from agents.scenes_agent import get_scenes_creation_agent, get_scenes_extraction_agent
from agents.scene_details_agent import get_scene_details_creation_agent, get_scene_details_extraction_agent
from agents.scene_social_npc_update_agent import get_scene_social_npc_update_agent
from agents.scene_combat_npc_check_agent import get_scene_combat_npc_check_agent
from agents.scene_combat_npc_update_agent import get_scene_combat_npc_update_agent
from agents.scene_skill_challenge_npc_check_agent import get_scene_skill_challenge_npc_check_agent
from agents.scene_skill_challenge_npc_update_agent import get_scene_skill_challenge_npc_update_agent
from agents.scene_hazard_npc_check_agent import get_scene_hazard_npc_check_agent
from agents.scene_hazard_npc_update_agent import get_scene_hazard_npc_update_agent
from agents.scene_update_npc_names_agent import get_scene_update_npc_names_agent
from agents.npc_identifier_agent import get_npc_identifier_agent

def determine_scene_type(current_scene: SceneConcept) -> str:
    """
    Determines the scene/encounter types for each scene in the quest.
    Agent determines if the scene is a combat, social, skill challenge, or hazard scene
    """
    scene_type_agent = get_scene_type_agent()
    prompt = f"# Scene Information:\n"
    prompt += f"Scene Summary: {current_scene.summary}\n"
    prompt += f"Scene Location: {current_scene.location}\n\n"
    prompt += f"Determine the type of encounter for this scene.  You MUST choose one of the following options: 'combat', 'social', 'skill challenge', or 'hazard'."

    with console.status(f"[bold cyan]AI Agent is determining the scene type for a scene...[/bold cyan]", spinner="dots"):
        result = scene_type_agent.run_sync(prompt)
    scene_type = result.output
    
    return scene_type

def determine_scene_rest_opportunity(current_scene: SceneConcept, next_scene: SceneConcept) -> str:
    """
    Determines the rest opportunity for each scene in the quest.
    Agent determines if the scene should have a short rest, long rest or no rest opportunity.
    """
    scene_rest_opportunity_agent = get_scene_rest_opportunity_agent()
    prompt = f"# Current Scene Information:\n"
    prompt += f"Scene Summary: {current_scene.summary}\n"
    prompt += f"Scene Location: {current_scene.location}\n"
    prompt += f"Scene Encounter Type: {current_scene.encounter_type}\n\n"
    prompt += f"# Next Scene Information:\n"
    prompt += f"Scene Summary: {next_scene.summary}\n"
    prompt += f"Scene Location: {next_scene.location}\n"
    prompt += f"Scene Encounter Type: {next_scene.encounter_type}\n\n"
    prompt += f"Determine the rest opportunity for the current scene.  You MUST choose one of the following options: 'short rest', 'long rest', or 'no rest opportunity'."
    
    with console.status(f"[bold cyan]AI Agent is determining the rest opportunity for a scene...[/bold cyan]", spinner="dots"):
        result = scene_rest_opportunity_agent.run_sync(prompt)
    scene_rest_opportunity = result.output
    
    return scene_rest_opportunity

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
        prompt = f"Extract the summary and location for each of the scenes from the following quest scene summaries:\n\n{raw_scenes}"
        with console.status(f"[bold cyan]AI Agent is extracting quest scenes for Act {current_act.act_number}...[/bold cyan]", spinner="dots"):
            result = scenes_extraction_agent.run_sync(prompt)
        scenes_concepts = result.output

        # Verify scenes were generated, if not, regenerate scenes for this act
        while len(scenes_concepts) < 4 or len(scenes_concepts) > 9:
            log_error(f"Incorrect number of scenes generated for Act {current_act.act_number}, regenerating...")
            prompt += "\n\nRemember to create 4 to 9 scenes."
            with console.status(f"[bold cyan]AI Agent is regenerating scenes for Act {current_act.act_number}...[/bold cyan]", spinner="dots"):
                raw_scenes = scenes_creation_agent.run_sync(prompt)
            prompt = f"Extract the summary and location for each of the scenes from the following quest scene summaries:\n\n{raw_scenes}"
            with console.status(f"[bold cyan]AI Agent is extracting quest scenes for Act {current_act.act_number}...[/bold cyan]", spinner="dots"):
                result = scenes_extraction_agent.run_sync(prompt)
            scenes_concepts = result.output

        log_success(f'Scenes Generated for Act {current_act.act_number}...')

        # Map the generated scenes to the current act
        log_output(f'Scenes for Act {current_act.act_number}:')
        scene_number = 1
        for scene_concept in scenes_concepts:
            scene_type = determine_scene_type(scene_concept)
            if scene_number < len(scenes_concepts):
                scene_rest_opportunity = determine_scene_rest_opportunity(scene_concept, scenes_concepts[scene_number])
            else:
                scene_rest_opportunity = 'long rest'
            new_scene = Scene(
                scene_number = scene_number,
                summary = scene_concept.summary,
                location = scene_concept.location,
                encounter_type = scene_type,
                rest_opportunity = scene_rest_opportunity
            )
            current_act.scenes.append(new_scene)
            log_output(f" - Scene {new_scene.scene_number} ({new_scene.encounter_type}): {new_scene.summary}")
            log_output(f" - - Location: {new_scene.location}")
            log_output(f" - - Rest Opportunity: {new_scene.rest_opportunity}")
            scene_number += 1
    
    return current_quest

def verify_social_scenes_have_npcs(current_quest: Quest) -> Quest:
    """
    Verifies that each social scene in the quest has an NPC, if not, then it generates an NPC for the scene.

    Args:
        quest: The Quest object to verify social scenes for.
    
    Returns:
        Quest: The updated Quest object.
    """
    npc_identifier_agent = get_npc_identifier_agent()
    scene_social_npc_update_agent = get_scene_social_npc_update_agent()

    for act in current_quest.acts:
        for scene in act.scenes:
            if scene.encounter_type == "social":
                has_npc = False
                for npc in current_quest.npcs:
                    for scene_role in npc.scene_roles:
                        if scene_role.act_number == act.act_number and scene_role.scene_number == scene.scene_number:
                            has_npc = True
                            break
                    if has_npc:
                        break
                if not has_npc:
                    log_error(f"Social scene Act {act.act_number}, Scene {scene.scene_number} does not have an NPC.")

                    log_status(f'Identifying NPC for scene Act {act.act_number}, Scene {scene.scene_number}...')

                    prompt = f"# Scene Information:\n"
                    prompt += f"Scene Summary: {scene.summary}\n"
                    prompt += f"Scene Location: {scene.location}\n\n"

                    prompt += "Identify the NPC that the player characters will interact with in this scene."

                    with console.status(f"[bold cyan]AI Agent is identifying NPC for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                        result = npc_identifier_agent.run_sync(prompt)
                    npc_identifier = result.output.strip()

                    while npc_identifier == '':
                        log_error(f"No NPC identified for social scene Act {act.act_number}, Scene {scene.scene_number}.")
                        
                        log_status(f"Rewriting scene summary for Act {act.act_number}, Scene {scene.scene_number} to include an NPC...")

                        prompt = f"# Scene Information:\n"
                        prompt += f"Scene Summary: {scene.summary}\n"
                        prompt += f"Scene Location: {scene.location}\n\n"

                        prompt += "Rewrite the scene summary to include an NPC that the player characters will interact with in this scene."

                        with console.status(f"[bold cyan]AI Agent is rewriting scene summary for Act {act.act_number}, Scene {scene.scene_number} to include an NPC...[/bold cyan]", spinner="dots"):
                            result = scene_social_npc_update_agent.run_sync(prompt)
                        scene.summary = result.output.strip()
                        
                        log_success(f'Rewrote scene summary for Act {act.act_number}, Scene {scene.scene_number} to include an NPC...')

                        log_status(f'Identifying NPC for scene Act {act.act_number}, Scene {scene.scene_number}...')

                        prompt = f"# Scene Information:\n"
                        prompt += f"Scene Summary: {scene.summary}\n"
                        prompt += f"Scene Location: {scene.location}\n\n"

                        prompt += "Identify the NPC that the player characters will interact with in this scene."

                        with console.status(f"[bold cyan]AI Agent is identifying NPC for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                            result = npc_identifier_agent.run_sync(prompt)
                        npc_identifier = result.output.strip()

                    new_npc = NPC(
                        identifier = npc_identifier,
                        scene_roles = [
                            SceneRole(
                                act_number = act.act_number,
                                scene_number = scene.scene_number
                            )
                        ]
                    )

                    log_output(f"Generated NPC: {npc_identifier} for scene Act {act.act_number}, Scene {scene.scene_number}.")

                    current_quest.npcs.append(new_npc)

    log_success("Verified that all social scenes have NPCs.")
    
    return current_quest

def evaluate_and_modify_combat_scenes_with_npcs(current_quest: Quest) -> Quest:
    """
    Evaluates and modifies combat scenes with NPCs.

    Args:
        current_quest: The Quest object to evaluate and modify combat scenes for.
    
    Returns:
        Quest: The updated Quest object.
    """
    log_status("Evaluating and modifying combat scenes with NPCs...")

    scene_combat_npc_check_agent = get_scene_combat_npc_check_agent()
    scene_combat_npc_update_agent = get_scene_combat_npc_update_agent()

    # Remove NPCs that are clearly monster descriptions
    for act in current_quest.acts:
        for scene in act.scenes:
            if scene.encounter_type == "combat" and scene_has_npc(current_quest, act.act_number, scene.scene_number):
                for npc in current_quest.npcs:
                    scene_roles_to_remove = []
                    for scene_role in npc.scene_roles:
                        if scene_role.act_number == act.act_number and scene_role.scene_number == scene.scene_number:
                            prompt = "# Scene Information:\n"
                            prompt += f"Scene Summary: {scene.summary}\n"
                            prompt += "NPC for this scene:\n"
                            prompt += f"- {npc.identifier}\n\n"

                            prompt += "Determine if the NPC listed above is actually a monster or enemy to be fought in a combat encounter. Return True if it is and False if it is not."

                            with console.status(f"[bold cyan]AI Agent is removing monster descriptions from Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                                npc_is_monster = scene_combat_npc_check_agent.run_sync(prompt)
                            if npc_is_monster:
                                scene_roles_to_remove.append(scene_role)
                                log_output(f"Removed NPC: {npc.identifier} from scene Act {act.act_number}, Scene {scene.scene_number}.")
                    for scene_role in scene_roles_to_remove:
                        npc.scene_roles.remove(scene_role)

    # Update scene summaries with NPC information
    for act in current_quest.acts:
        for scene in act.scenes:
            if scene.encounter_type == "combat" and scene_has_npc(current_quest, act.act_number, scene.scene_number):
                prompt = "# Scene Information:\n"
                prompt += f"Scene Summary: {scene.summary}\n"
                prompt += f"Scene Location: {scene.location}\n\n"
                prompt += "NPCs for this scene:\n"
                for npc in current_quest.npcs:
                    for scene_role in npc.scene_roles:
                        if scene_role.act_number == act.act_number and scene_role.scene_number == scene.scene_number:
                            prompt += f"- {npc.identifier}\n\n"

                prompt += "Rewrite the scene summary so the listed NPCs do not directly engage in combat alongside the party."

                with console.status(f"[bold cyan]AI Agent is updating scene summary for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                    result = scene_combat_npc_update_agent.run_sync(prompt)
                    scene.summary = result.output.strip()

    log_success("Combat scenes with NPCs evaluated and modified.")
    
    return current_quest

def evaluate_and_modify_hazard_scenes_with_npcs(current_quest: Quest) -> Quest:
    """
    Evaluates and modifies hazard scenes with NPCs.

    Args:
        current_quest: The Quest object to evaluate and modify combat scenes for.
    
    Returns:
        Quest: The updated Quest object.
    """
    log_status("Evaluating and modifying hazard scenes with NPCs...")

    scene_hazard_npc_check_agent = get_scene_hazard_npc_check_agent()
    scene_hazard_npc_update_agent = get_scene_hazard_npc_update_agent()

    # Remove NPCs that are clearly hazard descriptions
    for act in current_quest.acts:
        for scene in act.scenes:
            if scene.encounter_type == "hazard" and scene_has_npc(current_quest, act.act_number, scene.scene_number):
                for npc in current_quest.npcs:
                    scene_roles_to_remove = []
                    for scene_role in npc.scene_roles:
                        if scene_role.act_number == act.act_number and scene_role.scene_number == scene.scene_number:
                            prompt = "# Scene Information:\n"
                            prompt += f"Scene Summary: {scene.summary}\n"
                            prompt += "NPC for this scene:\n"
                            prompt += f"- {npc.identifier}\n"

                            prompt += "Determine if the NPC listed above is actually a hazard that must be overcome by the party. Return True if it is and False if it is not."

                            with console.status(f"[bold cyan]AI Agent is removing hazard descriptions from Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                                npc_is_hazard = scene_hazard_npc_check_agent.run_sync(prompt)
                            if npc_is_hazard:
                                scene_roles_to_remove.append(scene_role)
                                log_output(f"Removed NPC: {npc.identifier} from scene Act {act.act_number}, Scene {scene.scene_number}.")
                    for scene_role in scene_roles_to_remove:
                        npc.scene_roles.remove(scene_role)

    # Update scene summaries with NPC information
    for act in current_quest.acts:
        for scene in act.scenes:
            if scene.encounter_type == "hazard" and scene_has_npc(current_quest, act.act_number, scene.scene_number):
                prompt = "# Scene Information:\n"
                prompt += f"Scene Summary: {scene.summary}\n"
                prompt += f"Scene Location: {scene.location}\n\n"
                prompt += "NPCs for this scene:\n"
                for npc in current_quest.npcs:
                    for scene_role in npc.scene_roles:
                        if scene_role.act_number == act.act_number and scene_role.scene_number == scene.scene_number:
                            prompt += f"- {npc.identifier}\n"

                prompt += "Rewrite the scene summary so the listed NPCs do not directly engage with the hazard the party is facing and so the NPC is not the hazard described to be overcome."

                with console.status(f"[bold cyan]AI Agent is updating scene summary for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                    result = scene_hazard_npc_update_agent.run_sync(prompt)
                    scene.summary = result.output.strip()

    log_success("Hazard scenes with NPCs evaluated and modified.")
    
    return current_quest

def evaluate_and_modify_skill_challenge_scenes_with_npcs(current_quest: Quest) -> Quest:
    """
    Evaluates and modifies skill challenge scenes with NPCs.

    Args:
        current_quest: The Quest object to evaluate and modify skill challenge scenes for.
    
    Returns:
        Quest: The updated Quest object.
    """
    log_status("Evaluating and modifying skill challenge scenes with NPCs...")

    scene_skill_challenge_npc_check_agent = get_scene_skill_challenge_npc_check_agent()
    scene_skill_challenge_npc_update_agent = get_scene_skill_challenge_npc_update_agent()

    # Remove NPCs that are clearly skill challenge descriptions
    for act in current_quest.acts:
        for scene in act.scenes:
            if scene.encounter_type == "skill_challenge" and scene_has_npc(current_quest, act.act_number, scene.scene_number):
                for npc in current_quest.npcs:
                    scene_roles_to_remove = []
                    for scene_role in npc.scene_roles:
                        if scene_role.act_number == act.act_number and scene_role.scene_number == scene.scene_number:
                            prompt = "# Scene Information:\n"
                            prompt += f"Scene Summary: {scene.summary}\n"
                            prompt += "NPC for this scene:\n"
                            prompt += f"- {npc.identifier}\n"

                            prompt += "Determine if the NPC listed above is actually an obstacle or hazard that must be overcome by the party. Return True if it is and False if it is not."

                            with console.status(f"[bold cyan]AI Agent is removing skill challenge descriptions from Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                                npc_is_skill_challenge = scene_skill_challenge_npc_check_agent.run_sync(prompt)
                            if npc_is_skill_challenge:
                                scene_roles_to_remove.append(scene_role)
                                log_output(f"Removed NPC: {npc.identifier} from scene Act {act.act_number}, Scene {scene.scene_number}.")
                    for scene_role in scene_roles_to_remove:
                        npc.scene_roles.remove(scene_role)

    # Update scene summaries with NPC information
    for act in current_quest.acts:
        for scene in act.scenes:
            if scene.encounter_type == "skill_challenge" and scene_has_npc(current_quest, act.act_number, scene.scene_number):
                prompt = "# Scene Information:\n"
                prompt += f"Scene Summary: {scene.summary}\n"
                prompt += f"Scene Location: {scene.location}\n\n"
                prompt += "NPCs for this scene:\n"
                for npc in current_quest.npcs:
                    for scene_role in npc.scene_roles:
                        if scene_role.act_number == act.act_number and scene_role.scene_number == scene.scene_number:
                            prompt += f"- {npc.identifier}\n"

                prompt += "Rewrite the scene summary so the listed NPCs are not a part of the obstacles or hazards the party must overcome."

                with console.status(f"[bold cyan]AI Agent is updating scene summary for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                    result = scene_skill_challenge_npc_update_agent.run_sync(prompt)
                    scene.summary = result.output.strip()

    log_success("Skill challenge scenes with NPCs evaluated and modified.")
    
    return current_quest

def update_scene_summaries_with_npc_names(current_quest: Quest) -> Quest:
    """
    Updates the scene summaries to include the NPC names.

    Args:
        current_quest: The Quest object to update scene summaries for.
    
    Returns:
        Quest: The updated Quest object.
    """
    log_status("Updating scene summaries with NPC names...")

    for act in current_quest.acts:
        for scene in act.scenes:
            if scene_has_npc(current_quest, act.act_number, scene.scene_number):
                scene_update_npc_names_agent = get_scene_update_npc_names_agent()

                prompt = "# Scene Information:\n"
                prompt += f"Scene Summary: {scene.summary}\n\n"
                prompt += "# NPCs for this scene:\n"
                for npc in current_quest.npcs:
                    for scene_role in npc.scene_roles:
                        if scene_role.act_number == act.act_number and scene_role.scene_number == scene.scene_number:
                            prompt += f"Vague Identifier: {npc.identifier}\n"
                            prompt += f"Name: {npc.name}\n\n"

                prompt += "Update the scene summary with the NPC names."

                with console.status(f"[bold cyan]AI Agent is updating scene summary for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                    result = scene_update_npc_names_agent.run_sync(prompt)
                scene.summary = result.output.strip()

                log_output(f"Updated scene summary for Act {act.act_number}, Scene {scene.scene_number}: {scene.summary}")

    log_success("Scene summaries updated with NPC names.")
    
    return current_quest

def generate_scene_details(current_quest: Quest) -> Quest:
    """
    Generates the scene details for each scene: the introduction, description and resolution
    
    Args:
        current_quest: The Quest object to generate scene details for.
    
    Returns:
        The Quest object with scene details generated.
    """

    log_status("Generating scene details for quest...")

    scene_details_creation_agent = get_scene_details_creation_agent()
    scene_details_extraction_agent = get_scene_details_extraction_agent()
    
    for act in current_quest.acts:
        for scene in act.scenes:
            log_output(f"Act {act.act_number}, Scene {scene.scene_number}:")
            prompt = "# Current Scene Information:\n"
            prompt += f"Current Scene Summary: {scene.summary}\n"
            prompt += f"Current Scene Location: {scene.location}\n"
            prompt += "# Current Scene Encounter Information:\n"
            prompt += f"Current Scene Encounter Type: {scene.encounter.encounter_type}\n"
            if scene.encounter.encounter_type == 'combat':
                prompt += f"Current Scene Encounter Enemy: {scene.encounter.enemies[0].name}\n"
                prompt += f"Current Scene Encounter Enemy Description: {scene.encounter.enemies[0].description}\n"
                prompt += f"Current Scene Encounter Enemy Count: {len(scene.encounter.enemies)}\n"
            elif scene.encounter.encounter_type == 'social':
                prompt += "Current Scene Encounter NPCs:\n"
                for quest_npc in current_quest.npcs:
                    for scene_role in quest_npc.scene_roles:
                        if scene_role.act_number == act.act_number and scene_role.scene_number == scene.scene_number:
                            prompt += f" - NPC Name: {quest_npc.name}\n"
                            prompt += f" - - Scene Role: {scene_role.role}\n"
            elif scene.encounter.encounter_type == 'hazard':
                prompt += f"Current Scene Encounter Hazard: {scene.encounter.hazard.name}\n"
                prompt += f"Current Scene Encounter Hazard Description: {scene.encounter.hazard.description}\n"
            else:
                prompt += "Current Scene Encounter Obstacles:\n"
                for obstacle in scene.encounter.obstacles:
                    prompt += f" - Name: {obstacle.name}\n"
                    prompt += f" - Description: {obstacle.description}\n"
            prompt += f"Current Scene Rest Opportunity: {scene.rest_opportunity}\n\n"
            if scene.scene_number > 1:
                prompt += f"# Previous Scene Summary: {act.scenes[scene.scene_number - 1].summary}\n\n"
            if scene.scene_number < len(act.scenes) - 1:
                prompt += f"# Next Scene Summary: {act.scenes[scene.scene_number + 1].summary}\n\n"
            prompt += "# Task:\n\n"
            prompt += "Expand the summary of the scene into three detailed sections: introduction, description and resolution."

            with console.status(f"[bold cyan]AI Agent is generating scene details for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                result = scene_details_creation_agent.run_sync(prompt)
                raw_scene_details = result.output

            with console.status(f"[bold cyan]AI Agent is extracting scene details for Act {act.act_number}, Scene {scene.scene_number}...[/bold cyan]", spinner="dots"):
                result = scene_details_extraction_agent.run_sync(raw_scene_details)
                scene_details = result.output
            
            scene.introduction = scene_details.introduction
            log_output(f" - Introduction: {scene.introduction}")
            scene.description = scene_details.description
            log_output(f" - Description: {scene.description}")
            scene.resolution = scene_details.resolution
            log_output(f" - Resolution: {scene.resolution}")
    
    log_success("Scene details generated...")

    return current_quest