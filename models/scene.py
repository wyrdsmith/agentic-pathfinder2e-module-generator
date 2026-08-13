from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from models.encounter import Encounter
from models.npc import NPC

class Scene(BaseModel):
    scene_number: int = Field(default=1, description="The number of the scene in the quest")
    encounter_type: Literal["combat", "social", "skill challenge", "hazard", "none"] = Field(default="none", description="The type of encounter in this scene, or 'none' if roleplay/exploration only")
    summary: str = Field(default="", description="A summary of what happens in the scene")
    introduction: str = Field(default="", description="The introduction of the scene")
    description: str = Field(default="", description="A detailed description of the events of the scene")
    resolution: str = Field(default="", description="The result of the scene after the encounter")
    rest_opportunity: Literal["short rest", "long rest", "no rest opportunity"] = Field(default="no rest opportunity", description="An opportunity for a rest in the scene")
    location: Optional[str] = Field(default=None, description="The location of the scene")
    encounter: Optional[Encounter] = Field(default=None, description="An encounter that takes place in the scene")

        