import random
from collections import defaultdict
from pydantic_ai import RunContext
from tools.db_tools import get_connection
from models.quest import Quest
from tools.log_tools import *

class MarkovNameGenerator:
    def __init__(self, order=3):
        """
        'order' dictates how many previous characters to look at. 
        Order 2 means it looks at the last 2 letters to guess the 3rd.
        Higher order = closer to the original names. Lower order = more alien/random.
        """
        self.order = order
        self.models = defaultdict(lambda: defaultdict(list))
        self.starts = defaultdict(list)

    def train(self, category: str, names: list[str]):
        """
        Feeds a list of seed names into the model for a specific category (e.g., 'Elf', 'Dwarf').
        """
        for name in names:
            name = name.lower()
            # Add start and end boundaries to know how names begin and end
            padded_name = f"{' ' * self.order}{name} " 
            
            # Record valid starting n-grams
            self.starts[category].append(padded_name[:self.order])

            # Build the probability chain
            for i in range(len(padded_name) - self.order):
                current_gram = padded_name[i:i + self.order]
                next_char = padded_name[i + self.order]
                self.models[category][current_gram].append(next_char)

    def generate(self, category: str, min_length=3, max_length=15) -> str:
        """
        Generates a new name based on the trained category.
        """
        if category not in self.models:
            return "Unknown"

        for _ in range(50): # Retry loop to ensure length constraints
            # Pick a random starting sequence
            current_gram = random.choice(self.starts[category])
            result = current_gram.strip()

            # Generate characters until we hit a space (the end boundary)
            while True:
                next_chars = self.models[category].get(current_gram)
                if not next_chars:
                    break
                
                next_char = random.choice(next_chars)
                if next_char == ' ':
                    break
                    
                result += next_char
                # Slide the window forward
                current_gram = current_gram[1:] + next_char

            if min_length <= len(result) <= max_length:
                return result.capitalize()
                
        return f"A name could not be produced. Come up with a unique name fit for a {ancestry}."

def get_ancestry_name_seeds(ancestry: str) -> list[str]:
    """
    Get the name seeds for a given ancestry.
    
    Args:
        ancestry: The ancestry to get the name seeds for.
    
    Returns:
        list[str]: A list of name seeds for the given ancestry.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM ancestry_names WHERE ancestry = ?", (ancestry,))
    names = cursor.fetchall()
    conn.close()
    return [name[0] for name in names]

def get_npc_name(ctx: RunContext[Quest], ancestry: str) -> str:
    """
    Generates a culturally appropriate name for a given ancestry. Ancestry argument is the name of an ancestry, e.g. Dwarf, Elf, etc.

    Args:
        ctx: The runtime context containing the quest data.
        ancestry: The ancestry to generate a name for.
    
    Returns:
        str: A culturally appropriate name for the given ancestry.
    """
    ancestries_with_selected_names = ["awakened_animal", "kashirishi", "kholo", "leshy", "poppet", "surki"]
    if ancestry.lower().replace(" ", "_") in ancestries_with_selected_names:
        names = get_ancestry_name_seeds(ancestry.lower().replace(" ", "_"))
        return random.choice(names)
    else:
        name_engine = MarkovNameGenerator(order=3)
        name_seeds = get_ancestry_name_seeds(ancestry.lower().replace(" ", "_"))
        if not name_seeds or len(name_seeds) < 5:
            return f"A name could not be produced. Come up with a unique name fit for a {ancestry}."
        name_engine.train(ancestry.lower().replace(" ", "_"), name_seeds)
        return name_engine.generate(ancestry.lower().replace(" ", "_"))