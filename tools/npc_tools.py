from tools.db_tools import get_connection
from tools.db_tools import get_available_rarities
from tools.encounter_tools import get_threat_levels
from pydantic_ai import RunContext
from models.npc import NPC, Stats, Save
from models.quest import Quest
from tools.log_tools import *

def get_ancestries_with_descriptions() -> str:
    """
    Returns a list of ancestries with their descriptions.
    
    Args:
        None

    Returns:
        str: A list of ancestries with their descriptions.
    """
    log_write("AI Agent is getting ancestries from database...")
    rarities = get_available_rarities()
    query_string = "SELECT name, description FROM ancestries WHERE rarity IN ({})".format(",".join([f"'{rarity}'" for rarity in rarities]))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query_string)
    ancestries = cursor.fetchall()
    conn.close()
    ancestries = [f"Ancestry: {ancestry[0]}\nDescription: {ancestry[1]}" for ancestry in ancestries]
    ancestries_string = "\n\n".join(ancestries)
    return ancestries_string

def get_classes_with_descriptions():
    """
    Returns a list of classes with their descriptions.
    
    Args:
        None
    
    Returns:
        str: A list of classes with their descriptions.
    """
    log_write("AI Agent is getting classes from database...")
    rarities = get_available_rarities()
    query_string = "SELECT name, description FROM classes WHERE rarity IN ({})".format(",".join([f"'{rarity}'" for rarity in rarities]))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query_string)
    classes = cursor.fetchall()
    conn.close()
    classes = [f"Class: {each_class[0]}\nDescription: {each_class[1]}" for each_class in classes]
    classes_string = "\n\n".join(classes)
    return classes_string

def get_ancestry_description(ctx: RunContext[Quest], ancestry: str) -> str:
    """
    Returns the description of an ancestry.
    
    Args:
        ctx: The runtime context.
        ancestry: The name of the ancestry.

    Returns:
        str: The description of the ancestry.
    """
    log_write(f"AI Agent is getting ancestry description for {ancestry} from database...")
    query_string = "SELECT description FROM ancestries WHERE name = '{}'".format(ancestry)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query_string)
    ancestry_description = cursor.fetchone()
    conn.close()
    return ancestry_description[0] if ancestry_description else "No description was provided in the database."

def get_class_description(ctx: RunContext[Quest], class_name: str) -> str:
    """
    Returns the description of a class.
    
    Args:
        ctx: The runtime context.
        class_name: The name of the class.

    Returns:
        str: The description of the class.
    """
    log_write(f"AI Agent is getting class description for {class_name} from database...")
    query_string = "SELECT description FROM classes WHERE name = '{}'".format(class_name)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query_string)
    class_description = cursor.fetchone()
    conn.close()
    return class_description[0] if class_description else "No description was provided in the database."

def get_skills_with_descriptions() -> str:
    """
    Returns a list of skills with their descriptions.
    
    Args:
        None
    
    Returns:
        str: A list of skills with their descriptions.
    """
    log_write("AI Agent is getting skills from database...")
    query_string = "SELECT name, description FROM skills"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query_string)
    skills = cursor.fetchall()
    conn.close()
    skills = [f"Skill: {skill[0]}\nDescription: {skill[1]}" for skill in skills]
    skills_string = "\n\n".join(skills)
    return skills_string

def get_npc_base_stats(current_quest: Quest, npc: NPC) -> Stats:
    """
    Calculates and returns the base stats of the NPC based on their role in the quest.

    Args:
        current_quest: The quest the NPC is in.
        npc: The NPC to generate stats for.
    
    Returns:
        Stats: The base stats of the NPC.
    """
    # Get threat levels in order of level adjustment
    # 0 = -2 levels, 1 = -1 level, 2 = 0 adjustment, 3 = +1 level, 4 = +2 levels
    threat_levels = get_threat_levels()
    
    # Determine npc level adjustment based on the highest level threat level in the quest
    current_highest_threat_level = 0
    for role in npc.scene_roles:
        scene_threat_level = current_quest.acts[role.act_number-1].scenes[role.scene_number-1].encounter.threat_level
        if threat_levels.index(scene_threat_level) > current_highest_threat_level:
            current_highest_threat_level = threat_levels.index(scene_threat_level)
    level_adjustment = current_highest_threat_level - 2

    # Determine npc level based on level adjustment
    npc_level = max(-1, current_quest.party_level + level_adjustment)
    
    conn = get_connection()
    cursor = conn.cursor()
    query_string = "SELECT level, skill, ac, hp, strike_attack, strike_damage, spell_dc, spell_attack FROM creature_stats WHERE level = ?"
    cursor.execute(query_string, (npc_level,))
    base_stats = cursor.fetchone()
    conn.close()
    
    stats = Stats(
        level = base_stats[0],
        ac = base_stats[2],
        perception = base_stats[1],
        hp = base_stats[3],
        strike = base_stats[4],
        damage = base_stats[5],
        spellAttack = base_stats[7],
        spellDC = base_stats[6]
    )
    
    return stats

def get_npc_saves(npc_saves: List[str], npc_level: int) -> List[Tuple[str, int]]:
    conn = get_connection()
    cursor = conn.cursor()
    query_string = "SELECT high, medium, low FROM creature_stats WHERE level = ?"
    cursor.execute(query_string, (npc_level,))
    save_scores = cursor.fetchone()
    conn.close()
    
    saves = [
        Save(name=npc_saves[0], modifier=save_scores[0]),
        Save(name=npc_saves[1], modifier=save_scores[1]),
        Save(name=npc_saves[2], modifier=save_scores[2])
    ]
    
    return saves