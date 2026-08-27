from __future__ import annotations
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class NPCSceneRole(BaseModel):
    act_number: int = Field(default=1, description="Act number")
    scene_number: int = Field(default=1, description="Scene number")
    role: str = Field(default="", description="Role the NPC plays in the scene")

class NPCConcept(BaseModel):
    name: str = Field(default="", description="Name of the NPC")
    ancestry: str = Field(default="", description="Ancestry of the NPC")
    class_name: str = Field(default="", description="Class of the NPC")
    quest_role: str = Field(default="", description="The role the NPC plays in the quest")
    scene_roles: str = Field(default_factory=list, description="A description of the scene roles the NPC plays, includes the act number and scene number.")
    