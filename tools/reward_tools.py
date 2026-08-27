from tools.db_tools import get_connection, get_available_rarities
from pydantic_ai import RunContext
from models.quest import Quest
from tools.log_tools import *
import random
from models.reward import Reward

def get_possible_item_rewards(party_level: int, encounter_reward_budget: int) -> str:
    """
    This tool returns a list of possible item rewards for the given quest.
    
    Args:
        party_level: The level of the party in the quest.
        encounter_reward_budget: The value in gold pieces to spend on rewards.
    
    Returns:
        str: A list of possible item rewards for the given quest.
    """
    reward_item_categories = ['Weapons', 'Adventuring Gear', 'Alchemical Items', 'Armor', 'Shields', 'Consumables', 'Held Items', 'Worn Items', 'Runes', 'Wands', 'Staves']

    rarities = get_available_rarities()

    # get the rewards budget for the current quest
    max_level = party_level
    min_level = max(0, party_level - 4)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT name, description FROM items WHERE level >= ? AND level <= ? AND price <= ? AND rarity IN ({','.join(['?']*len(rarities))}) AND item_category IN ({','.join(['?']*len(reward_item_categories))}) ORDER BY price, level DESC", (min_level, max_level, encounter_reward_budget, *rarities, *reward_item_categories))
    rows = cursor.fetchall()
    conn.close()

    # Pick 50 random items
    reward_options = random.sample(rows, k=min(50, len(rows)))
    
    rewards_list = "Possible Reward Items:\n\n"
    for row in reward_options:
        rewards_list += f" - {row[0]}: {row[1]}\n\n"

    return rewards_list

def get_random_item(party_level: int, encounter_reward_budget: int) -> str:
    """
    This tool returns random item name.
    
    Args:
        party_level: The level of the party in the quest.
        encounter_reward_budget: The value in gold pieces to spend on rewards.
    
    Returns:
        str: A random item name.
    """
    reward_item_categories = ['Weapons', 'Adventuring Gear', 'Alchemical Items', 'Armor', 'Shields', 'Consumables', 'Held Items', 'Worn Items', 'Runes', 'Wands', 'Staves']

    rarities = get_available_rarities()

    # get the rewards budget for the current quest
    max_level = party_level
    min_level = max(0, party_level - 4)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM items WHERE level >= ? AND level <= ? AND price <= ? AND rarity IN ({','.join(['?']*len(rarities))}) AND item_category IN ({','.join(['?']*len(reward_item_categories))}) ORDER BY price, level DESC", (min_level, max_level, encounter_reward_budget, *rarities, *reward_item_categories))
    rows = cursor.fetchall()
    conn.close()

    # Pick 50 random items
    reward_options = random.choice(rows)
    
    return reward_options[0]

def get_item_details(item_name: str) -> Reward:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, description, price, url FROM items WHERE name = ?", (item_name,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    else:
        return Reward(
            name=row[0],
            reward_type="item",
            description=row[1],
            price=row[2],
            url= "https://2e.aonprd.com" + row[3]
        )
