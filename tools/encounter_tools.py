from tools.db_tools import get_connection
from models.quest import Quest
from pydantic_ai import RunContext
from typing import List
from tools.log_tools import *

ENCOUNTER_TYPES = [
    "combat",
    "social",
    "skill challenge",
    "hazard"
]

def get_threat_levels() -> List[str]:
    """
    Returns a list of threat levels.
    
    Args:
        None
    
    Returns:
        List[str]: A list of threat levels.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM threat_levels order by level_adjustment")
    threat_levels = cursor.fetchall()
    conn.close()
    return [threat_level[0] for threat_level in threat_levels]

def get_encounter_experience(threat_level: str) -> tuple[int, int]:
    """
    Get the base experience and adjustment for a given threat level.
    
    Args:
        threat_level: The threat level of the encounter.
    
    Returns:
        tuple[int, int]: The base experience and adjustment for the given threat level.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT experience, adjustment FROM encounter_experience WHERE threat_level = ?", (threat_level,))
    encounter_experience = cursor.fetchall()
    conn.close()
    return encounter_experience[0][0], encounter_experience[0][1]

def get_encounter_experience_budget(threat_level: str, num_characters: int) -> int:
    """
    Get the experience budget for a given threat level and number of characters.
    
    Args:
        threat_level: The threat level of the encounter.
        num_characters: The number of characters in the encounter.
    
    Returns:
        int: The experience budget for the given threat level and number of characters.
    """
    encounter_experience, adjustment = get_encounter_experience(threat_level)
    encounter_budget = encounter_experience + ((4 - num_characters) * adjustment)
    if encounter_budget < 0:
        encounter_budget = encounter_experience
    return encounter_budget

def get_encounter_level(party_level: int, threat_level: str) -> int:
    """
    Get the encounter level based on the party level and threat level.
    
    Args:
        party_level: The level of the party.
        threat_level: The threat level of the encounter.
    
    Returns:
        int: The encounter level based on the party level and threat level.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT level_adjustment FROM threat_levels WHERE name = ?", (threat_level,))
    level_adjustment = cursor.fetchall()
    conn.close()
    encounter_level = party_level + int(level_adjustment[0][0])
    if encounter_level < 0:
        encounter_level = 0
    return encounter_level

def get_encounter_reward_budget(threat_level: str, encounter_level: int) -> int:
    """
    Get the reward budget for a given threat level and encounter level.
    
    Args:
        threat_level: The threat level of the encounter.
        encounter_level: The level of the encounter.
    
    Returns:
        int: The reward budget for the given threat level and encounter level.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT treasure FROM treasure_encounter WHERE threat_level = ? AND level = ?", (threat_level, encounter_level))
    encounter_reward_budget = cursor.fetchall()
    conn.close()
    return int(encounter_reward_budget[0][0])

def get_possible_enemies(ctx: RunContext[Quest], act_number: int, scene_number: int) -> str:
    """
    Get the possible enemies for the encounter in a given act_number and scene_number.
    
    Args:
        ctx: The RunContext that contains the quest data.
        act_number: The act number of the encounter.
        scene_number: The scene number of the encounter.
    
    Returns:
        str: The possible enemies for the encounter.
    """
    log_write("AI Agent is getting possible enemies for the encounter...")
    
    current_quest = ctx.deps
    party_level = current_quest.party_level
    encounter = current_quest.acts[act_number-1].scenes[scene_number-1].encounter
    encounter_experience_budget = encounter.xp_budget

    min_level = party_level - 4
    max_level = party_level + 4
    if min_level < -1:
        min_level = -1
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT level, name, description FROM creatures WHERE level BETWEEN ? AND ? ORDER BY level DESC", (min_level, max_level))
    encounter_enemies = cursor.fetchall()
    
    enemies_list = []
    # Loop through the possible enemies and add them to the list along with xp cost
    for enemy in encounter_enemies:
        level_difference = enemy[0] - party_level
        cursor.execute(f"SELECT xp FROM creature_experience WHERE level_difference = ?", (level_difference,))
        xp = cursor.fetchall()
        enemies_list.append((enemy[0], enemy[1], enemy[2], xp[0][0]))
    conn.close()

    # Remove enemies whose experience cost are greater than the encounter budget
    for enemy in enemies_list:
        if enemy[3] > encounter_experience_budget:
            enemies_list.remove(enemy)

    enemies_string = "Possible enemies for this encounter:\n\n"
    for enemy in enemies_list:
        # 0 Level, 1 Name, 2 Description, 3 XP Cost
        enemies_string += f"Name: {enemy[1]}\n"
        enemies_string += f"- Level: {enemy[0]}\n"
        enemies_string += f"- Description: {enemy[2]}\n"
        enemies_string += f"- Experience Cost: {enemy[3]}\n\n"

    return enemies_string