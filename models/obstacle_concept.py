from pydantic import BaseModel, Field
from typing import Literal

class ObstacleSkillConcept(BaseModel):
    skill: str = Field(default="", description="The name of the skill")
    difficulty: Literal["easy", "moderate", "hard"] = Field(default="moderate", description="The difficulty of the skill")

class HazardStatsConcept(BaseModel):
    hazard_type: Literal["area", "attack"] = Field(default="area", description="The type of hazard, either area or attack")
    save_type: Literal["Fortitude", "Reflex", "Will", "AC"] = Field(default="Reflex", description="The save that is rolled to avoid damage by the hazard")
    

class ObstacleConcept(BaseModel):
    name: str = Field(default="", description="The name of the obstacle")
    description: str = Field(default="", description="The description of the obstacle")
    success_resolution: str = Field(default="", description="The resolution if the obstacle is overcome")
    failure_resolution: str = Field(default="", description="The resolution if the obstacle is not overcome")
    is_hazard: bool = Field(default=False, description="Whether the obstacle is hazard that can damage the party")
