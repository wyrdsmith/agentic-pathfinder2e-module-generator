from __future__ import annotations
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class Stats(BaseModel):
    level: int = Field(default=0, description="Level of the NPC")
    hp: int = Field(default=0, description="Hit points of the NPC")
    ac: int = Field(default=0, description="Armor class of the NPC")
    perception: int = Field(default=0, description="Perception of the NPC")
    skills: Dict[str, int] = Field(default_factory=dict, description="Dictionary of skills of the NPC")
    saves: Dict[str, int] = Field(default_factory=dict, description="Dictionary of saves of the NPC")
    strike: int = Field(default=0, description="Strike bonus of the NPC")
    damage: str = Field(default="", description="Strike damage of the NPC")
    spellAttack: int = Field(default=0, description="Spell attack bonus of the NPC")
    spellDC: int = Field(default=0, description="Spell DC of the NPC")

class Discovery(BaseModel):
    skill: str = Field(default="", description="Skill or perception used to discover the NPC's influences")
    dc: int = Field(default=0, description="DC of the skill used to discover the NPC's influences")

class Influence(BaseModel):
    skill: str = Field(default="", description="Skill used to influence the NPC")
    dc: int = Field(default=0, description="DC of the skill used to influence the NPC")

class Thresholds(BaseModel):
    four: str = Field(default="", description="Boons achieved at threshold of 4")
    six: str = Field(default="", description="Boons achieved at threshold of 6")
    eight: str = Field(default="", description="Boons achieved at threshold of 8")

class Penalty(BaseModel):
    description: str = Field(default="", description="Description of the topic or manner of influence that results in a penalty")
    penalty: str = Field(default="", description="Description of the penalty")

class SceneRole(BaseModel):
    scene: str = Field(default="", description="Scene number")
    role: str = Field(default="", description="Role the NPC plays in the scene")

class InfluenceData(BaseModel):
    discoveries: List[Discovery] = Field(default_factory=list, description="List of Discovery objects for the NPC's discoveries")
    influences: List[Influence] = Field(default_factory=list, description="List of Influence objects for the NPC's influences")
    thresholds: Optional[Thresholds] = Field(default=None, description="Thresholds object for the NPC's thresholds")
    resistances: str = Field(default="", description="List of resistances to influence for the NPC")
    weaknesses: str = Field(default="", description="List of weaknesses to influence for the NPC")
    penalty: Optional[Penalty] = Field(default=None, description="Penalty object for the NPC")

class NPC(BaseModel):
    name: str = Field(default="", description="Name of the NPC")
    ancestry: str = Field(default="", description="Ancestry of the NPC")
    class_profession: str = Field(default="", description="Class or profession of the NPC")
    appearance: str = Field(default="", description="Description of the NPC's appearance")
    personality: str = Field(default="", description="Description of the NPC's personality")
    behavior: str = Field(default="", description="Description of how the NPC behaves")
    attitude: str = Field(default="", description="NPC's attitude or disposition towards the player characters")
    stats: Optional[Stats] = Field(default=None, description="Stats object of values pulled from creature-stats table")
    influence_data: Optional[InfluenceData] = Field(default=None, description="InfluenceData object of values as defined by InfluenceData class")
    quest_role: str = Field(default="", description="The role the NPC plays in the quest")
    scene_roles: List[SceneRole] = Field(default_factory=list, description="List of roles the NPC plays in each scene")