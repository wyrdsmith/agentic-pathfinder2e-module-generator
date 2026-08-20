from tools.db_tools import get_connection
from models.quest import Quest
from pydantic_ai import RunContext
from typing import List
from tools.log_tools import *
from tools.db_tools import get_available_rarities
from models.encounter import Enemy
from models.hazard import Hazard
from models.obstacle import HazardStats
import random

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

def get_possible_enemies(party_level: int, encounter_experience_budget: int) -> List[Enemy]:
    """
    Get a list of 50 possible enemies for a given party level and encounter experience budget.
    Intended to allow LLM to select the most appropriate enemy from a restricted pool of enemies.
    
    Args:
        party_level: The level of the party.
        encounter_experience_budget: The experience budget for the encounter.
    
    Returns:
        List[Enemy]: A list of possible enemies for the encounter.
    """
    min_level = party_level - 4
    max_level = party_level + 4
    if min_level < -1:
        min_level = -1
    rarities = get_available_rarities()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT level, name, description, url FROM creatures WHERE level BETWEEN ? AND ? AND rarity IN ({','.join(['?']*len(rarities))}) ORDER BY level DESC", (min_level, max_level, *rarities))
    raw_level_appropriate_enemies = cursor.fetchall()
    
    level_appropriate_enemies = []
    # Loop through the possible enemies and add them to the list along with xp cost
    for enemy in raw_level_appropriate_enemies:
        level_difference = enemy[0] - party_level
        cursor.execute(f"SELECT xp FROM creature_experience WHERE level_difference = ?", (level_difference,))
        xp = cursor.fetchone()
        level_appropriate_enemies.append(Enemy(
            name=enemy[1],
            level=enemy[0],
            description=enemy[2],
            url=enemy[3],
            xp_value=xp[0]
        ))
    conn.close()

    # Remove enemies whose experience cost are greater than the encounter budget
    for enemy in level_appropriate_enemies:
        if enemy.xp_value > encounter_experience_budget:
            level_appropriate_enemies.remove(enemy)

    # Cheat enemy selection by only providing enemies for which the budget is cleanly divisible by enemy's xp cost
    possible_enemies = []
    for enemy in level_appropriate_enemies:
        if encounter_experience_budget % enemy.xp_value == 0:
            possible_enemies.append(enemy)

    # Choose 50 random enemies from the list of possible enemies
    if len(possible_enemies) > 50:
        possible_enemies = random.sample(possible_enemies, 50)

    return possible_enemies

def get_enemy_data(enemy_name: str) -> Enemy:
    """
    Get the data for a specific enemy.
    
    Args:
        enemy_name: The name of the enemy.
    
    Returns:
        Enemy: The data for the enemy.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT name, level FROM creatures WHERE name = ?", (enemy_name,))
    enemy_data = cursor.fetchall()
    conn.close()
    if len(enemy_data) == 0:
        log_error(f"Enemy not found in database: {enemy_name}")
        return None
    return Enemy(
        name=enemy_data[0][0],
        level=enemy_data[0][1]
    )

def get_possible_hazards(encounter_level: int) -> List[Hazard]:
    """
    Returns a list of possible hazards for a given encounter level.
    
    Args:
        encounter_level: The level of the encounter.
    
    Returns:
        List[Hazard]: A list of possible hazards.
    """
    rarities = get_available_rarities()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT name, level, hazard_type, description, url FROM hazards WHERE level = ? AND rarity IN ({','.join(['?']*len(rarities))})", (encounter_level, *rarities))
    possible_hazards = cursor.fetchall()
    conn.close()
    if not possible_hazards:
        return []
    else:
        return [Hazard(name=row[0], level=row[1], hazard_type=row[2], description=row[3], url=row[4]) for row in possible_hazards]

def get_obstacle_skill_dc(encounter_level: int, difficulty: str) -> int:
    """
    Returns the difficulty class for an obstacle skill based on the encounter level and the difficulty of the skill check.
    
    Args:
        encounter_level: The level of the encounter.
        difficulty: The difficulty of the skill check (easy, moderate, or hard).
    
    Returns:
        int: The difficulty class for the skill check.
    """
    conn = get_connection()
    cursor = conn.cursor()
    query_string = "SELECT difficulty FROM difficulties WHERE level = ?"
    cursor.execute(query_string, (max(-1, encounter_level),))
    dc = cursor.fetchone()
    conn.close()

    modifier = 0
    if difficulty == "easy":
        modifier = -2
    elif difficulty == "moderate":
        modifier = 0
    else:
        modifier = 2
    
    return dc[0] + modifier

def get_obstacle_hazard_stats(hazard_type: str, save_type: str, encounter_level: int) -> HazardStats:
    """
    Returns the stats for an obstacle hazard based on the encounter level.
    
    Args:
        hazard_type: The type of hazard, either area or attack.
        encounter_level: The level of the encounter.
    
    Returns:
        HazardStats: The stats for the hazard.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT level, attack, damage, area_dc FROM hazard_stats WHERE level = ?", (encounter_level,))
    hazard_stats = cursor.fetchone()
    conn.close()
    return HazardStats(
        level = hazard_stats[0],
        hazard_type = hazard_type,
        attack = hazard_stats[1],
        damage = hazard_stats[2],
        save_type = save_type,
        area_dc = hazard_stats[3]
    )