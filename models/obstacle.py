from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class ObstacleSkill(BaseModel):
    skill: str = Field(default="", description="The name of the skill")
    difficulty: int = Field(default=10, description="The difficulty of the skill")

class HazardStats(BaseModel):
    level: int = Field(default=0, description="The level of the hazard")
    hazard_type: Literal["area", "attack"] = Field(default="area", description="The type of hazard, either area or attack")
    attack: int = Field(default=0, description="The attack of the hazard")
    damage: str = Field(default="", description="The damage of the hazard")
    save_type: Literal["Fortitude", "Reflex", "Will", "AC"] = Field(default="Reflex", description="The save that is rolled to avoid damage by the hazard")
    area_dc: int = Field(default=0, description="The area dc of the hazard")

class Obstacle(BaseModel):
    name: str = Field(default="", description="The name of the obstacle")
    description: str = Field(default="", description="The description of the obstacle")
    skills: List[ObstacleSkill] = Field(default_factory=list, description="List of ObstacleSkills required to overcome the obstacle which contains the skill and the difficulty")
    success_resolution: str = Field(default="", description="The resolution if the obstacle is overcome")
    failure_resolution: str = Field(default="", description="The resolution if the obstacle is not overcome")
    is_hazard: bool = Field(default=False, description="Whether the obstacle is hazard that can damage the party")
    hazard_stats: Optional[HazardStats] = Field(default=None, description="The HazardStats object for the obstacle if it is a hazard")
