from typing import List
import random
from models.quest import Quest
from models.encounter import Encounter
from tools.encounter_tools import ENCOUNTER_TYPES, get_threat_levels, get_encounter_experience, get_encounter_experience_budget, get_encounter_reward_budget

def adjust_encounter_threat_levels(quest: Quest) -> Quest:
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
        print("Warning: No encounters found to distribute XP across.")
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
            print("Warning: Maxed out all threat tiers and still under 1000 XP. Unlocking higher tiers.")
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

    print(f"Encounter Threat Level Adjustment Complete... Total XP: {total_xp}")
    for act in quest.acts:
        for scene in act.scenes:
            if scene.encounter:
                print(f"  - Act {act.act_number} Scene {scene.scene_number}: {scene.encounter.threat_level} ({scene.encounter.xp_value} XP)")
                
    return quest

def distribute_experience_budgets(quest: Quest) -> Quest:
    for act in quest.acts:
        for scene in act.scenes:
            if scene.encounter:
                scene.encounter.xp_budget = get_encounter_experiencebudget(scene.encounter.threat_level, quest.player_count)

    print(f"Encounter Experience Budgeting Complete...")
    for act in quest.acts:
        for scene in act.scenes:
            if scene.encounter:
                print(f"  - Act {act.act_number} Scene {scene.scene_number}: {scene.encounter.threat_level} ({scene.encounter.xp_budget} XP)")
                
    return quest

def distribute_reward_budgets(quest: Quest) -> Quest:
    # Determine Target Reward Budget
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT total, extra FROM treasure_level WHERE level = '{quest.party_level}'")
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

    print(f"Encounter Reward Budgeting Complete... (Total Budget: {total_budget} gp / Target Budget: {target_reward_budget} gp)")
    for act in quest.acts:
        for scene in act.scenes:
            if scene.encounter:
                print(f"  - Act {act.act_number} Scene {scene.scene_number}: Level {scene.encounter.encounter_level} ({scene.encounter.threat_level}) {scene.encounter.reward_budget} Reward Budget")
                
    return quest