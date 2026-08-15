from __future__ import annotations
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class Skill(BaseModel):
    name: str = Field(default="", description="Name of the skill")
    modifier: int = Field(default=0, description="The skill modifier")

class Save(BaseModel):
    name: str = Field(default="", description="Name of the save")
    modifier: int = Field(default=0, description="The save modifier")

class Stats(BaseModel):
    level: int = Field(default=0, description="Level of the NPC")
    hp: int = Field(default=0, description="Hit points of the NPC")
    ac: int = Field(default=0, description="Armor class of the NPC")
    perception: int = Field(default=0, description="Perception of the NPC")
    skills: List[Skill] = Field(default_factory=list, description="List of skills of the NPC")
    saves: List[Save] = Field(default_factory=list, description="List of saves of the NPC")
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
    act_number: Optional[int] = Field(default=None, description="Act number the npc appears in")
    scene_number: Optional[int] = Field(default=None, description="Scene number the npc appears in")
    role: str = Field(default="", description="Role the NPC plays in the scene")

class InfluenceInfo(BaseModel):
    discoveries: List[Discovery] = Field(default_factory=list, description="List of Discovery objects for the NPC's discoveries")
    influences: List[Influence] = Field(default_factory=list, description="List of Influence objects for the NPC's influences")
    thresholds: Optional[Thresholds] = Field(default=None, description="Thresholds object for the NPC's thresholds")
    resistances: str = Field(default="", description="A string list of resistances to influence for the NPC")
    weaknesses: str = Field(default="", description="A string list of weaknesses to influence for the NPC")
    penalty: Optional[Penalty] = Field(default=None, description="Penalty object for the NPC")

class NPC(BaseModel):
    name: str = Field(default="", description="Name of the NPC")
    ancestry: str = Field(default="", description="Ancestry of the NPC")
    class_name: str = Field(default="", description="Class of the NPC")
    appearance: str = Field(default="", description="Description of the NPC's appearance")
    personality: str = Field(default="", description="Description of the NPC's personality")
    behavior: str = Field(default="", description="Description of how the NPC behaves")
    attitude: str = Field(default="", description="NPC's attitude or disposition towards the player characters")
    stats: Optional[Stats] = Field(default=None, description="Stats object of values pulled from creature-stats table")
    influence_info: Optional[InfluenceInfo] = Field(default=None, description="InfluenceInfo object of values as defined by InfluenceInfo class")
    quest_role: str = Field(default="", description="The role the NPC plays in the quest")
    scene_roles: List[SceneRole] = Field(default_factory=list, description="List of SceneRole objects of values as defined by SceneRole class")
