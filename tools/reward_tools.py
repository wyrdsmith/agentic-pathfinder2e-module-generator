from tools.db_tools import get_connection, get_available_rarities
from pydantic_ai import RunContext
from models.quest import Quest
from tools.log_tools import *

def get_possible_item_rewards(ctx: RunContext[Quest], encounter_reward_budget: int) -> str:
    """
    This tool returns a list of possible item rewards for the given quest.
    
    Args:
        ctx: The runcontext containing the quest data.
        encounter_reward_budget: The value in gold pieces to spend on rewards.
    
    Returns:
        str: A list of possible item rewards for the given quest.
    """
    log_write(f"AI Agent is getting possible item rewards for reward budget: {encounter_reward_budget}...")
    current_quest = ctx.deps

    if encounter_reward_budget == 0:
        return "No rewards budget available."

    reward_item_categories = ['Weapons', 'Adventuring Gear', 'Alchemical Items', 'Armor', 'Shields', 'Consumables', 'Held Items', 'Worn Items', 'Runes', 'Wands', 'Staves']

    # get the rewards budget for the current quest
    conn = get_connection()
    cursor = conn.cursor()
    rarities = get_available_rarities(conn)
    cursor.execute("SELECT * FROM items WHERE level <= ? AND rarity IN %s AND category IN %s ORDER BY price, level DESC", (current_quest.party_level, tuple(rarities), tuple(reward_item_categories)))
    rows = cursor.fetchall()
    conn.close()
    
    rewards_list = f"Possible Reward Items (Reward Budget: {encounter_reward_budget} gp):\n\n"
    for row in rows:
        rewards_list += f" - {row['name']} ({row['rarity']}) - {row['value']} gp: {row['description']}\n\n"

    return rewards_list