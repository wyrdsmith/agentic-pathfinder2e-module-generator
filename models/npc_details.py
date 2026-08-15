from __future__ import annotations
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class NPCDetails(BaseModel):
    appearance: str = Field(default="", description="Description of the NPC's appearance")
    personality: str = Field(default="", description="Description of the NPC's personality")
    behavior: str = Field(default="", description="Description of how the NPC behaves")
    attitude: str = Field(default="", description="NPC's attitude or disposition towards the player characters")
