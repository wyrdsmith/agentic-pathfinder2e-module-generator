from __future__ import annotations
from typing import List

class Obstacle:
    name: str #The name of the obstacle
    description: str #The description of the obstacle
    skills: List[ObstacleSkill] #List of ObstacleSkills required to overcome the obstacle which contains the skill and the difficulty
    success_resolution: str #The resolution if the obstacle is overcome
    failure_resolution: str #The resolution if the obstacle is not overcome
    is_hazard: bool #Whether the obstacle is hazard that can damage the party
    hazard_stats: HazardStats #The HazardStats object for the obstacle if it is a hazard

    def __init__(self, name = "", description = "", skills = [], success_resolution = "", failure_resolution = "", is_hazard = False, hazard_stats = None):
        self.name = name
        self.description = description
        self.skills = skills
        self.success_resolution = success_resolution
        self.failure_resolution = failure_resolution
        self.is_hazard = is_hazard
        self.hazard_stats = hazard_stats

class ObstacleSkill:
    skill: str #The name of the skill
    difficulty: int #The difficulty of the skill

    def __init__(self, skill = "", difficulty = 10):
        self.skill = skill
        self.difficulty = difficulty

class HazardStats:
    level: int #The level of the hazard
    hazard_type: str #The type of hazard, either attack, single or area
    stealth_dc: int #The stealth dc of the hazard
    disable_dc: int #The disable dc of the hazard
    ac: int #The ac of the hazard
    fortitude: int #The fortitude save of the hazard
    reflex: int #The reflex save of the hazard
    will: int #The will save of the hazard
    hardness: int #The hardness of the hazard
    hp: int #The hp of the hazard
    broken_threshold: int #The broken threshold of the hazard
    attack: int #The attack of the hazard
    damage: str #The damage of the hazard
    area_dc: int #The area dc of the hazard
    single_dc: int #The single dc of the hazard

    def __init__(self, level = 0, hazard_type = "attack", stealth_dc = 0, disable_dc = 0, ac = 0, fortitude = 0, reflex = 0, will = 0, hardness = 0, hp = 0, broken_threshold = 0, attack = 0, damage = "", area_dc = 0, single_dc = 0):
        self.level = level
        self.hazard_type = hazard_type
        self.stealth_dc = stealth_dc
        self.disable_dc = disable_dc
        self.ac = ac
        self.fortitude = fortitude
        self.reflex = reflex
        self.will = will
        self.hardness = hardness
        self.hp = hp
        self.broken_threshold = broken_threshold
        self.attack = attack
        self.damage = damage
        self.area_dc = area_dc
        self.single_dc = single_dc