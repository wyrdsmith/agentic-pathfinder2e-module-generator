from typing import List

class Rewards:
    value: int #Total treasure value of encounter after threat level modification in gold pieces
    description: str #Detailed description of items and currency awarded
    boons: List[str] #List of boons awarded (strings)
    key_items: List[str] #List of key items awarded (strings)
    
    def __init__(self, value=0, description="", boons=[], key_items=[]):
        self.value = value
        self.description = description
        self.boons = boons
        self.key_items = key_items
    
    def add_boon(self, boon):
        self.boons.append(boon)

    def add_key_item(self, key_item):
        self.key_items.append(key_item)