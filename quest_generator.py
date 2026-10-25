from models.quest import Quest
from tools.log_tools import *
from tools.db_tools import check_database
from tools.quest_tools import write_quest_to_file, load_quest_from_file, adjust_encounter_threat_levels, distribute_experience_budgets, distribute_reward_budgets
from utilities.quest_utilities import generate_quest_concept, generate_quest_summary
from utilities.act_utilities import generate_acts
from utilities.scene_utilities import generate_scenes_for_acts, verify_social_scenes_have_npcs, evaluate_and_modify_combat_scenes_with_npcs, evaluate_and_modify_hazard_scenes_with_npcs, evaluate_and_modify_skill_challenge_scenes_with_npcs, update_scene_summaries_with_npc_names, generate_scene_details
from utilities.npc_utilities import generate_quest_npc_list, generate_npc_basic_information, generate_npc_details, generate_npc_stats, generate_npc_influence_info, remove_npcs_without_scene_roles, generate_npc_quest_roles, generate_npc_scene_roles
from utilities.encounter_utilities import generate_encounter_enemies, generate_encounter_hazards, generate_quest_obstacles, generate_encounter_rewards, generate_encounter_details

def generate_quest(player_count: int = 4, party_level: int = 1):
    # Verify DB first
    if not check_database():
        log_error("Database verification failed... Exiting.")
        return None

    log_status(f"Beginning quest generation for {player_count} players at level {party_level}...")

    #current_quest = load_quest_from_file("output/The_Stone_Singer's_Lament.json")

    # Set up initial quest object
    current_quest = Quest(player_count=player_count, party_level=party_level)

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

    # Generate list of NPCs to be created for the quest
    current_quest = generate_quest_npc_list(current_quest)

    # Verify that all social scenes have an NPC, generate one if not
    current_quest = verify_social_scenes_have_npcs(current_quest)

    # Evaluate and modify any combat scenes with NPCs
    current_quest = evaluate_and_modify_combat_scenes_with_npcs(current_quest)

    # Evaluate and modify any hazard scenes with NPCs
    current_quest = evaluate_and_modify_hazard_scenes_with_npcs(current_quest)

    # Evaluate and modify any skill challenge scenes with NPCs
    current_quest = evaluate_and_modify_skill_challenge_scenes_with_npcs(current_quest)

    # Clean up NPC list and remove any NPCs without scene roles
    current_quest = remove_npcs_without_scene_roles(current_quest)

    # Generate basic information for NPCs in the quest
    current_quest = generate_npc_basic_information(current_quest)

    # Update scene summaries with NPC names
    current_quest = update_scene_summaries_with_npc_names(current_quest)

    # Generate quest roles for NPCs
    current_quest = generate_npc_quest_roles(current_quest)

    # Generate scene roles for NPCs
    current_quest = generate_npc_scene_roles(current_quest)

    # Generate NPC details: appearance, personality, behavior, and attitude
    current_quest = generate_npc_details(current_quest)
    
    # Generate NPC stats
    current_quest = generate_npc_stats(current_quest)

    # Generate NPC influence information for social encounters
    current_quest = generate_npc_influence_info(current_quest)
    
    # Generate combat encounter enemies
    current_quest = generate_encounter_enemies(current_quest)

    # Generate hazard encounters
    current_quest = generate_encounter_hazards(current_quest)

    # Generate quest obstacles
    current_quest = generate_quest_obstacles(current_quest)

    # Generate encounter rewards
    current_quest = generate_encounter_rewards(current_quest)
    
    # Generate scene details
    current_quest = generate_scene_details(current_quest)

    # Generate encounter details
    current_quest = generate_encounter_details(current_quest)

    log_success(f"Quest '{current_quest.name}' generated successfully...")
    
    write_quest_to_file(current_quest)

    return current_quest
