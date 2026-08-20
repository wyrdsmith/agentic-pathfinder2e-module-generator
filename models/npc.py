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

class SceneRole(BaseModel):
    act_number: Optional[int] = Field(default=None, description="Act number the npc appears in")
    scene_number: Optional[int] = Field(default=None, description="Scene number the npc appears in")
    role: str = Field(default="", description="Role the NPC plays in the scene")

class NPC(BaseModel):
    name: str = Field(default="", description="Name of the NPC")
    ancestry: str = Field(default="", description="Ancestry of the NPC")
    class_name: str = Field(default="", description="Class of the NPC")
    appearance: str = Field(default="", description="Description of the NPC's appearance")
    personality: str = Field(default="", description="Description of the NPC's personality")
    behavior: str = Field(default="", description="Description of how the NPC behaves")
    attitude: str = Field(default="", description="NPC's attitude or disposition towards the player characters")
    stats: Optional[Stats] = Field(default=None, description="Stats object of values pulled from creature-stats table")
    quest_role: str = Field(default="", description="The role the NPC plays in the quest")
    scene_roles: List[SceneRole] = Field(default_factory=list, description="List of SceneRole objects of values as defined by SceneRole class")
