from typing import List
import random
from models.quest import Quest
from models.encounter import Encounter
from tools.encounter_tools import ENCOUNTER_TYPES, get_threat_levels, get_encounter_experience, get_encounter_experience_budget, get_encounter_reward_budget, get_encounter_level
from tools.db_tools import get_connection
from pydantic_ai import RunContext
from tools.log_tools import *

def adjust_encounter_threat_levels(quest: Quest) -> Quest:
    """
    Updates threat levels of encounters in a quest to meet a minimum 1000 XP value.
    
    Args:
        quest: The quest to adjust the encounter threat levels for.
    
    Returns:
        Quest: The quest with the adjusted encounter threat levels.
    """
    # We only assign XP to scenes that have a formal encounter type
    valid_encounter_types = ENCOUNTER_TYPES

    # Get the list of threat levels in order of tier
    # 0 = Trivial, 1 = Low, 2 = Moderate, 3 = Severe, 4 = Extreme
    threat_levels = get_threat_levels()
    
    # Track metadata for upgrading scenes
    encounter_scenes = []
    
    for act in quest.acts:
        for scene in act.scenes:
            if scene.encounter_type in valid_encounter_types:
                # Initialize the encounter object if it doesn't exist
                if not scene.encounter:
                    scene.encounter = Encounter(encounter_type=scene.encounter_type)
                
                base_tier = act.act_number - 1
                if scene.encounter_type == "combat" or scene.encounter_type == "hazard":
                    base_tier += 1
                max_tier = act.act_number + 1
                scene.encounter.threat_level = threat_levels[base_tier]
                scene.encounter.encounter_type = scene.encounter_type
                scene.encounter.xp_value = get_encounter_experience(scene.encounter.threat_level)[0]
                scene.encounter.level = get_encounter_level(quest.party_level, scene.encounter.threat_level)
                
                encounter_scenes.append({
                    "act_num": act.act_number,
                    "scene": scene,
                    "max_tier": max_tier,
                    "current_tier": base_tier
                })
    
    if not encounter_scenes:
        log_warning("No encounters found to distribute XP across.")
        return quest

    # Helper to calculate total XP
    def get_total_xp():
        return sum(s["scene"].encounter.xp_value for s in encounter_scenes)
        
    total_xp = get_total_xp()
    
    # Loop to upgrade threat levels until XP >= 1000
    while total_xp < 1000:
        # Filter scenes that can still be upgraded
        upgradeable = [s for s in encounter_scenes if s["current_tier"] < s["max_tier"]]
        
        if not upgradeable:
            # Failsafe: if we maxed out all acts and still under 1000
            log_warning("Maxed out all threat tiers and still under 1000 XP. Unlocking higher tiers.")
            for s in encounter_scenes:
                s["max_tier"] = min(4, s["max_tier"] + 1)
            continue
            
        # Pick a random scene to upgrade
        chosen = random.choice(upgradeable)
        chosen["current_tier"] += 1
        chosen["scene"].encounter.threat_level = threat_levels[chosen["current_tier"]]
        chosen["scene"].encounter.xp_value = get_encounter_experience(chosen["scene"].encounter.threat_level)[0]
        chosen["scene"].encounter.level = get_encounter_level(quest.party_level, chosen["scene"].encounter.threat_level)
        
        total_xp = get_total_xp()

    log_success(f"Encounter Threat Level Adjustment Complete... Total XP: {total_xp}")
    for act in quest.acts:
        for scene in act.scenes:
            if scene.encounter:
                log_write(f"  - Act {act.act_number} Scene {scene.scene_number}: {scene.encounter.threat_level} ({scene.encounter.xp_value} XP)")
                
    return quest

def distribute_experience_budgets(quest: Quest) -> Quest:
    """
    Distributes experience budgets to encounters in a quest.
    
    Args:
        quest: The quest to distribute experience budgets for.
    
    Returns:
        Quest: The quest with the distributed experience budgets.
    """
    for act in quest.acts:
        for scene in act.scenes:
            if scene.encounter:
                scene.encounter.xp_budget = get_encounter_experience_budget(scene.encounter.threat_level, quest.player_count)

    log_success(f"Encounter Experience Budgeting Complete...")
    for act in quest.acts:
        for scene in act.scenes:
            if scene.encounter:
                log_write(f"  - Act {act.act_number} Scene {scene.scene_number}: {scene.encounter.threat_level} ({scene.encounter.xp_budget} XP)")
                
    return quest

def distribute_reward_budgets(quest: Quest) -> Quest:
    """
    Distributes reward budgets to encounters in a quest.
    
    Args:
        quest: The quest to distribute reward budgets for.
    
    Returns:
        Quest: The quest with the distributed reward budgets.
    """
    # Determine Target Reward Budget
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT total, extra FROM treasure_level WHERE level = ?", (quest.party_level,))
    treasure_level = cursor.fetchall()[0]
    target_reward_budget = treasure_level[0] + (treasure_level[1] * (4 - quest.player_count))
    conn.close()
    
    # Total reward budget for the quest
    total_budget = 0
    
    # Distribute Reward Budget
    for act in quest.acts:
        for scene in act.scenes:
            if scene.encounter:
                scene.encounter.reward_budget = get_encounter_reward_budget(scene.encounter.threat_level, quest.party_level)
                total_budget += scene.encounter.reward_budget

    log_success(f"Encounter Reward Budgeting Complete... (Total Budget: {total_budget} gp / Target Budget: {target_reward_budget} gp)")
    for act in quest.acts:
        for scene in act.scenes:
            if scene.encounter:
                log_write(f"  - Act {act.act_number} Scene {scene.scene_number}: Level {scene.encounter.level} ({scene.encounter.threat_level}) {scene.encounter.reward_budget}gp Reward Budget")
                
    return quest

def get_quest_theme(ctx: RunContext[Quest]) -> str:
    """
    Returns the theme of the quest.
    
    Args:
        ctx: The runtime context containing the quest data.
    
    Returns:
        str: The theme of the quest.
    """
    current_quest = ctx.deps
    return current_quest.theme

def get_quest_setting(ctx: RunContext[Quest]) -> str:
    """
    Returns the setting of the quest.
    
    Args:
        ctx: The runtime context containing the quest data.
    
    Returns:
        str: The setting of the quest.
    """
    current_quest = ctx.deps
    return current_quest.setting

def get_quest_summary(ctx: RunContext[Quest]) -> str:
    """
    Returns the summary of the quest.
    
    Args:
        ctx: The runtime context containing the quest data.
    
    Returns:
        str: The summary of the quest.
    """
    current_quest = ctx.deps
    return current_quest.summary

def get_npcs_for_scene(ctx: RunContext[Quest], act_number: int, scene_number: int) -> List[NPC]:
    """
    Returns a list of NPCs that appear in a scene of an act of the quest based on the provided act and scene numbers.
    
    Args:
        ctx: The runtime context containing the quest data.
        act_number: The act number to get the NPCs for.
        scene_number: The scene number to get the NPCs for.
    
    Returns:
        List[NPC]: A list of NPCs that appear in the specified scene of an act of the quest.
    """
    current_quest = ctx.deps
    act = current_quest.acts[act_number - 1]
    scene = act.scenes[scene_number - 1]
    npcs = []
    for npc in current_quest.npcs:
        for scene_role in npc.scene_roles:
            if scene_role.act == act_number and scene_role.scene == scene_number:
                npcs.append(npc)
    return npcs

def get_list_of_acts(ctx: RunContext[Quest]) -> str:
    """
    Returns a list of all act numbers in the quest.
    
    Args:
        ctx: The runtime context containing the quest data.
    
    Returns:
        str: A list of all act numbers in the quest.
    """
    current_quest = ctx.deps
    acts = []
    for act in current_quest.acts:
        acts.append(f"Act {act.act_number}")
    return "\n".join(acts)

def get_list_of_scenes(ctx: RunContext[Quest], act_number: int) -> str:
    """
    Returns a list of all scene numbers in an act of the quest based on the provided act number.
    
    Args:
        ctx: The runtime context containing the quest data.
        act_number: The act number to get the scenes for.
    
    Returns:
        str: A list of all scene numbers in the specified act of the quest.
    """
    current_quest = ctx.deps
    act = current_quest.acts[act_number - 1]
    scenes = []
    for scene in act.scenes:
        scenes.append(f"Scene {scene.scene_number}")
    return "\n".join(scenes)

def get_act_summary(ctx: RunContext[Quest], act_number: int) -> str:
    """
    Returns a summary of an act in the quest based on the provided act number.
    
    Args:
        ctx: The runtime context containing the quest data.
        act_number: The act number to get the summary for.
    
    Returns:
        str: The summary of the specified act in the quest.
    """
    current_quest = ctx.deps
    act = current_quest.acts[act_number - 1]
    return f"Act {act_number} summary: {act.summary}"

def get_next_act_summary(ctx: RunContext[Quest], current_act_number: int) -> str:
    """
    Returns a summary of the next act in the quest based on the current act number.
    
    Args:
        ctx: The runtime context containing the quest data.
        current_act_number: The current act number.
    
    Returns:
        str: The summary of the next act in the quest.
    """
    current_quest = ctx.deps
    next_act_number = current_act_number + 1
    log_write(f"AI Agent is getting summary for Act {next_act_number}...")
    if (next_act_number > 3):
        return "There is no next act. The current act is the final act. The quest concludes after this act."
    act = current_quest.acts[next_act_number - 1]
    return f"Act {next_act_number} summary: {act.summary}"

def get_previous_act_summary(ctx: RunContext[Quest], current_act_number: int) -> str:
    """
    Returns a summary of the previous act in the quest based on the current act number.
    
    Args:
        ctx: The runtime context containing the quest data.
        current_act_number: The current act number.
    
    Returns:
        str: The summary of the previous act in the quest.
    """
    current_quest = ctx.deps
    previous_act_number = current_act_number - 1
    log_write(f"AI Agent is getting summary for Act {previous_act_number}...")
    if (previous_act_number < 1):
        return "There is no previous act. The current act is the first act."
    act = current_quest.acts[previous_act_number - 1]
    return f"Act {previous_act_number} summary: {act.summary}"

def get_scene_summary(ctx: RunContext[Quest], act_number: int, scene_number: int) -> str:
    """
    Returns a summary of a specific scene in a specific act of the quest.
    
    Args:
        ctx: The runtime context containing the quest data.
        act_number: The act number to get the summary for.
        scene_number: The scene number to get the summary for.
    
    Returns:
        str: The summary of the specified scene in the specified act of the quest.
    """
    current_quest = ctx.deps
    act = current_quest.acts[act_number - 1]
    scene = act.scenes[scene_number - 1]
    return f"Act {act_number} Scene {scene_number} summary: {scene.summary}"

def get_next_scene_summary(ctx: RunContext[Quest], current_act_number: int, current_scene_number: int) -> str:
    """
    Returns a summary of the next scene after the current scene in the current act of the quest.
    
    Args:
        ctx: The runtime context containing the quest data.
        current_act_number: The current act number.
        current_scene_number: The current scene number.
    
    Returns:
        str: The summary of the next scene in the current act of the quest.
    """
    current_quest = ctx.deps
    next_scene_number = current_scene_number + 1
    if (next_scene_number >= len(current_quest.acts[current_act_number - 1].scenes)):
        return "There is no next scene. The current scene is the final scene in this act."
    act = current_quest.acts[current_act_number - 1]
    scene = act.scenes[next_scene_number - 1]
    return f"Act {current_act_number} Scene {next_scene_number} summary: {scene.summary}"

def get_previous_scene_summary(ctx: RunContext[Quest], current_act_number: int, current_scene_number: int) -> str:
    """
    Returns a summary of the previous scene before the current scene in the current act of the quest.
    
    Args:
        ctx: The runtime context containing the quest data.
        current_act_number: The current act number.
        current_scene_number: The current scene number.
    
    Returns:
        str: The summary of the previous scene in the current act of the quest.
    """
    current_quest = ctx.deps
    previous_scene_number = current_scene_number - 1
    if (previous_scene_number < 1):
        return "There is no previous scene. The current scene is the first scene in this act."
    act = current_quest.acts[current_act_number - 1]
    scene = act.scenes[previous_scene_number - 1]
    return f"Act {current_act_number} Scene {previous_scene_number} summary: {scene.summary}"