from typing import List

class Enemy:
    level: int #Level of the enemy creature
    name: str #Name of the enemy creature
    description: str #Description of the enemy creature
    traits: List[str] #List of traits of the enemy creature
    xp_value: int #XP value of the enemy creature
    url: str #URL to the enemy creature's Archives of Nethys page

    def __init__(self, level = 1, name = "", description = "", traits = [], xp_value = 40, url = ""):
        self.level = level
        self.name = name
        self.description = description
        self.traits = traits
        self.xp_value = xp_value
        self.url = url
        