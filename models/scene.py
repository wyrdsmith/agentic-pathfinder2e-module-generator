from typing import List, Optional
from pydantic import BaseModel, Field
from models.encounter import Encounter
from models.npc import NPC

class Scene(BaseModel):
    scene_number: int = Field(default=0, description="The number of the scene in the quest")
    introduction: str = Field(default="", description="The introduction of the scene")
    summary: str = Field(default="", description="A summary of what happens in the scene")
    resolution: str = Field(default="", description="The result of the scene after the encounter")
    time_of_day: str = Field(default="", description="The time of day when the scene takes place")
    time_passed: str = Field(default="", description="The amount of time that passes during the scene")
    rest_opportunity: str = Field(default="", description="An opportunity for a rest in the scene")
    location: Optional[str] = Field(default=None, description="The location of the scene")
    npcs: List[NPC] = Field(default_factory=list, description="A list of npcs in the scene")
    encounter: Optional[Encounter] = Field(default=None, description="An encounter that takes place in the scene")

        