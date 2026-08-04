import random
from models.quest import Quest
from models.encounter import Encounter

# Standard Pathfinder 2e XP awards for a party of 4
THREAT_XP = {
    "Trivial": 40,
    "Low": 60,
    "Moderate": 80,
    "Severe": 120,
    "Extreme": 160
}

# The progression of threat levels
THREAT_TIERS = ["Trivial", "Low", "Moderate", "Severe", "Extreme"]

def distribute_encounter_budgets(quest: Quest) -> Quest:
    print("\nBalancing Encounter Experience Budgets...")
    
    # We only assign XP to scenes that have a formal encounter type
    valid_encounter_types = ["combat", "social", "skill challenge", "hazard"]
    
    # Track metadata for upgrading scenes
    encounter_scenes = []
    
    for act in quest.acts:
        # Determine max threat tier for the act
        if act.act_number == 1:
            max_tier = 2 # Max Moderate
            base_tier = 0 # Start Trivial
        elif act.act_number == 2:
            max_tier = 3 # Max Severe
            base_tier = 1 # Start Low
        else:
            max_tier = 4 # Max Extreme
            base_tier = 2 # Start Moderate
            
        for scene in act.scenes:
            if scene.encounter_type in valid_encounter_types:
                # Initialize the encounter object if it doesn't exist
                if not scene.encounter:
                    scene.encounter = Encounter(encounter_type=scene.encounter_type)
                
                scene.encounter.threat_level = THREAT_TIERS[base_tier]
                scene.encounter.xp_value = THREAT_XP[scene.encounter.threat_level]
                
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
        chosen["scene"].encounter.threat_level = THREAT_TIERS[chosen["current_tier"]]
        chosen["scene"].encounter.xp_value = THREAT_XP[chosen["scene"].encounter.threat_level]
        
        total_xp = get_total_xp()

    print(f"Encounter Budgeting Complete! Total XP: {total_xp}")
    for act in quest.acts:
        for scene in act.scenes:
            if scene.encounter:
                print(f"  - Act {act.act_number} Scene {scene.scene_number}: {scene.encounter.threat_level} ({scene.encounter.xp_value} XP)")
                
    return quest
