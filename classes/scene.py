from typing import List
from classes.encounter import Encounter
from classes.npc import NPC

class Scene:
    scene_number: int #The number of the scene in the quest
    introduction: str #The introduction of the scene
    summary: str #A summary of what happens in the scene
    resolution: str #The result of the scene after the encounter
    time_of_day: str #The time of day when the scene takes place
    time_passed: str #The amount of time that passes during the scene
    rest_opportunity: str #An opportunity for a rest in the scene
    location: str #The location of the scene
    npcs: List[NPC] #A list of npcs in the scene
    encounter: Encounter #An encounter that takes place in the scene
    
    def __init__(self, scene_number = 0, introduction = "", summary = "", resolution = "", time_of_day = "", time_passed = "", rest_opportunity = "", location = None, npcs = [], encounter = None):
        self.scene_number = scene_number
        self.introduction = introduction
        self.summary = summary
        self.resolution = resolution
        self.time_of_day = time_of_day
        self.time_passed = time_passed
        self.rest_opportunity = rest_opportunity
        self.location = location
        self.npcs = npcs
        self.encounter = encounter
        