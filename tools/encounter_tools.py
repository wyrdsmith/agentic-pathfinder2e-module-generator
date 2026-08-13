from tools.db_tools import get_connection

ENCOUNTER_TYPES = [
    "combat",
    "social",
    "skill challenge",
    "hazard"
]

def get_threat_levels() -> List[str]:
    """Returns a list of threat levels."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM threat_levels order by level_adjustment")
    threat_levels = cursor.fetchall()
    conn.close()
    return [threat_level[0] for threat_level in threat_levels]

def get_encounter_experience(threat_level: str) -> tuple[int, int]:
    """Get the base experience and adjustment for a given threat level."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT experience, adjustment FROM encounter_experience WHERE threat_level = ?", (threat_level,))
    encounter_experience = cursor.fetchall()
    conn.close()
    return encounter_experience[0][0], encounter_experience[0][1]

def get_encounter_experience_budget(threat_level: str, num_characters: int) -> int:
    """Get the experience budget for a given threat level and number of characters."""
    encounter_experience, adjustment = get_encounter_experience(threat_level)
    encounter_budget = encounter_experience + ((4 - num_characters) * adjustment)
    if encounter_budget < 0:
        encounter_budget = encounter_experience
    return encounter_budget

def get_encounter_level(party_level: int, threat_level: str) -> int:
    """Get the encounter level based on the party level and threat level."""
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
    """Get the reward budget for a given threat level and encounter level."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT treasure FROM treasure_encounter WHERE threat_level = ? AND level = ?", (threat_level, encounter_level))
    encounter_reward_budget = cursor.fetchall()
    conn.close()
    return int(encounter_reward_budget[0][0])