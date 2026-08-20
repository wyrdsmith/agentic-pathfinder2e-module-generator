from typing import List, Optional
from pydantic import BaseModel, Field

class Discovery(BaseModel):
    skill: str = Field(default="", description="Skill or perception used to discover the NPC's influences")
    dc: int = Field(default=0, description="DC of the skill used to discover the NPC's influences")

class Influence(BaseModel):
    skill: str = Field(default="", description="Skill used to influence the NPC")
    dc: int = Field(default=0, description="DC of the skill used to influence the NPC")

class Thresholds(BaseModel):
    four: str = Field(default="", description="Boons achieved at threshold of four successes")
    six: str = Field(default="", description="Boons achieved at threshold of six successes")
    eight: str = Field(default="", description="Boons achieved at threshold of eight successes")

class Penalty(BaseModel):
    description: str = Field(default="", description="Description of the topic or manner of influence that results in a penalty")
    penalty: str = Field(default="", description="Description of the penalty")

class NPCInfluenceInfo(BaseModel):
    npc_name: str = Field(default="", description="Name of the NPC")
    discoveries: List[Discovery] = Field(default_factory=list, description="List of Discovery objects for the NPC's discoveries")
    influences: List[Influence] = Field(default_factory=list, description="List of Influence objects for the NPC's influences")
    thresholds: Optional[Thresholds] = Field(default=None, description="Thresholds object for the NPC's thresholds")
    resistances: str = Field(default="", description="A string list of resistances to influence for the NPC")
    weaknesses: str = Field(default="", description="A string list of weaknesses to influence for the NPC")
    penalty: Optional[Penalty] = Field(default=None, description="Penalty object for the NPC")