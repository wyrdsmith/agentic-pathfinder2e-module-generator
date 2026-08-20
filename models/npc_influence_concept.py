from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class DiscoveryConcept(BaseModel):
    skill: str = Field(default="", description="Skill or perception used to discover the NPC's influences")
    difficulty: Literal["easy", "moderate", "hard"] = Field(default="easy", description="Difficulty for the skill used to discover the NPC's influences")

class InfluenceConcept(BaseModel):
    skill: str = Field(default="", description="Skill used to influence the NPC")
    difficulty: Literal["easy", "moderate", "hard"] = Field(default="easy", description="Difficulty for the skill used to influence the NPC")

class NPCInfluenceInfoConcept(BaseModel):
    resistances: str = Field(default="", description="A string list of resistances to influence for the NPC")
    weaknesses: str = Field(default="", description="A string list of weaknesses to influence for the NPC")
    penalty: str = Field(default="", description="Penalty for the NPC")