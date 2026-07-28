from typing import List

class Hazard:
    name: str #The name of the hazard
    level: int #The level of the hazard
    hazard_type: str #The type of the hazard
    traits: List[str] #The trait of the hazard
    description: str #The description of the hazard
    url: str #The URL to the hazard's Archives of Nethys page

    def __init__(self, name = "", level = 0, hazard_type = "", traits = [], description = "", url = ""):
        self.name = name
        self.level = level
        self.hazard_type = hazard_type
        self.traits = traits
        self.description = description
        self.url = url