from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from models.encounter import Encounter
from models.npc import NPC

class EncounterDetails(BaseModel):
    introduction: str = Field(default="", description="The introduction of the encounter")
    description: str = Field(default="", description="A detailed description of the events of the encounter")
    resolution: str = Field(default="", description="The result of the encounter after the scene")

        