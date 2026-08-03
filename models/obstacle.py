from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field

class ObstacleSkill(BaseModel):
    skill: str = Field(default="", description="The name of the skill")
    difficulty: int = Field(default=10, description="The difficulty of the skill")

class HazardStats(BaseModel):
    level: int = Field(default=0, description="The level of the hazard")
    hazard_type: str = Field(default="attack", description="The type of hazard, either attack, single or area")
    stealth_dc: int = Field(default=0, description="The stealth dc of the hazard")
    disable_dc: int = Field(default=0, description="The disable dc of the hazard")
    ac: int = Field(default=0, description="The ac of the hazard")
    fortitude: int = Field(default=0, description="The fortitude save of the hazard")
    reflex: int = Field(default=0, description="The reflex save of the hazard")
    will: int = Field(default=0, description="The will save of the hazard")
    hardness: int = Field(default=0, description="The hardness of the hazard")
    hp: int = Field(default=0, description="The hp of the hazard")
    broken_threshold: int = Field(default=0, description="The broken threshold of the hazard")
    attack: int = Field(default=0, description="The attack of the hazard")
    damage: str = Field(default="", description="The damage of the hazard")
    area_dc: int = Field(default=0, description="The area dc of the hazard")
    single_dc: int = Field(default=0, description="The single dc of the hazard")

class Obstacle(BaseModel):
    name: str = Field(default="", description="The name of the obstacle")
    description: str = Field(default="", description="The description of the obstacle")
    skills: List[ObstacleSkill] = Field(default_factory=list, description="List of ObstacleSkills required to overcome the obstacle which contains the skill and the difficulty")
    success_resolution: str = Field(default="", description="The resolution if the obstacle is overcome")
    failure_resolution: str = Field(default="", description="The resolution if the obstacle is not overcome")
    is_hazard: bool = Field(default=False, description="Whether the obstacle is hazard that can damage the party")
    hazard_stats: Optional[HazardStats] = Field(default=None, description="The HazardStats object for the obstacle if it is a hazard")