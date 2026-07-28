from __future__ import annotations
from typing import List

class NPC:
    name: str #Name of the NPC
    ancestry: str #Ancestry of the NPC
    class_profession: str #Class or profession of the NPC
    appearance: str #Description of the NPC's appearance
    personality: str #Description of the NPC's personality
    behavior: str #Description of how the NPC behaves
    attitude: str #NPC's attitude or disposition towards the player characters
    stats: Stats #Stats object of values pulled from creature-stats table
    influence_data: InfluenceData #InfluenceData object of values as defined by InfluenceData class
    quest_role: str #The role the NPC plays in the quest
    scene_roles: List[SceneRole] #List of roles the NPC plays in each scene

    def __init__(self, name="", ancestry="", class_profession="", appearance="", personality="", behavior="", attitude="", stats=None, influence=None, quest_role="", scene_roles=None):
        self.name = name
        self.ancestry = ancestry
        self.class_profession = class_profession
        self.appearance = appearance
        self.personality = personality
        self.behavior = behavior
        self.attitude = attitude
        self.stats = stats
        self.influence_data = influence_data
        self.quest_role = quest_role
        self.scene_roles = scene_roles

class Stats:
    level: int #Level of the NPC
    hp: int #Hit points of the NPC
    ac: int #Armor class of the NPC
    perception: int #Perception of the NPC
    skills: dict[str, int] #Dictionary of skills of the NPC
    saves: dict[str, int] #Dictionary of saves of the NPC
    strike: int #Strike bonus of the NPC
    damage: str #Strike damage of the NPC
    spellAttack: int #Spell attack bonus of the NPC
    spellDC: int #Spell DC of the NPC

    def __init__(self, level=0, hp=0, ac=0, perception=0, skills=None, saves=None, strike=0, damage="", spellAttack=0, spellDC=0):
        self.level = level
        self.hp = hp
        self.ac = ac
        self.perception = perception
        self.skills = skills
        self.saves = saves
        self.strike = strike
        self.damage = damage
        self.spellAttack = spellAttack
        self.spellDC = spellDC

class InfluenceData:
    discoveries: List[Discovery] #List of Discovery objects for the NPC's discoveries
    influences: List[Influence] #List of Influence objects for the NPC's influences
    thresholds: Thresholds #Thresholds object for the NPC's thresholds
    resistances: str #List of resistances to influence for the NPC
    weaknesses: str #List of weaknesses to influence for the NPC
    penalty: Penalty #Penalty object for the NPC

    def __init__(self, discoveries=None, influences=None, thresholds=None, resistances="", weaknesses="", penalty=None):
        self.discoveries = discoveries
        self.influences = influences
        self.thresholds = thresholds
        self.resistances = resistances
        self.weaknesses = weaknesses
        self.penalty = penalty

class Discovery:
    skill: str #Skill or perception used to discover the NPC's influences
    dc: int #DC of the skill used to discover the NPC's influences

    def __init__(self, skill="", dc=0):
        self.skill = skill
        self.dc = dc

class Influence:
    skill: str #Skill used to influence the NPC
    dc: int #DC of the skill used to influence the NPC

    def __init__(self, skill="", dc=0):
        self.skill = skill
        self.dc = dc

class Thresholds:
    four: str #Boons achieved at threshold of 4
    six: str #Boons achieved at threshold of 6
    eight: str #Boons achieved at threshold of 8

    def __init__(self, four="", six="", eight=""):
        self.four = four
        self.six = six
        self.eight = eight

class Penalty:
    description: str #Description of the topic or manner of influence that results in a penalty
    penalty: str #Description of the penalty

    def __init__(self, description="", penalty=""):
        self.description = description
        self.penalty = penalty

class SceneRole:
    scene: str #Scene number
    role: str #Role the NPC plays in the scene

    def __init__(self, scene="", role=""):
        self.scene = scene
        self.role = role