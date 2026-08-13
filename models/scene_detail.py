from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from models.encounter import Encounter
from models.npc import NPC

class SceneDetail(BaseModel):
    introduction: str = Field(default="", description="The introduction of the scene")
    description: str = Field(default="", description="A detailed description of the events of the scene")
    resolution: str = Field(default="", description="The result of the scene after the encounter")

        