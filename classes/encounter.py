from typing import List
from classes.npc import NPC
from classes.enemy import Enemy
from classes.obstacle import Obstacle
from classes.hazard import Hazard
from classes.rewards import Rewards

class Encounter:
    level: int #Actual level of the encounter after modifiers
    encounter_type: str #Either combat, social, skill challenge or hazard
    threat_level: str #Either trivial, low, moderate, severe or extreme
    xp_value: int #Based on encounter level after modification by threat level and number of party members
    introduction: str #Line spoken to introduce the encounter
    resolution: str #Line spoken to conclude the encounter
    description: str #Detailed description of the encounter
    gm_information: str #Information about the encounter for the GM's eyes only
    turns: int #The number of turns the party has to overcome this encounter if it's a social or skill challenge encounter
    victory_points_required: int #The number of victory points required to overcome this encounter if it's a skill challenge encounter
    enemies: List[Enemy] #List of enemies in the encounter
    npcs: List[NPC] #List of npcs in the encounter
    obstacles: List[Obstacle] #List of obstacles in the encounter
    hazard: Hazard #Hazard in the encounter
    rewards: Rewards #Reward object to be filled with rewards data

    def __init__(self, level=1, encounter_type="combat", threat_level="moderate", xp_value=80, introduction="", resolution="", description="", gm_information="", turns=0, victory_points_required=0, enemies=[], npcs=[], obstacles=[], hazard=None, rewards=None):
        self.level = level
        self.encounter_type = encounter_type
        self.threat_level = threat_level
        self.xp_value = xp_value
        self.introduction = introduction
        self.resolution = resolution
        self.description = description
        self.gm_information = gm_information
        self.turns = turns
        self.victory_points_required = victory_points_required
        self.enemies = enemies
        self.npcs = npcs
        self.obstacles = obstacles
        self.hazard = hazard
        self.rewards = rewards

    def set_rewards(self, rewards):
        self.rewards = rewards