from __future__ import annotations
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class NPCSceneRole(BaseModel):
    act_number: int = Field(default=1, description="Act number")
    scene_number: int = Field(default=1, description="Scene number")
    role: str = Field(default="", description="Role the NPC plays in the scene")

class NPCSceneRolesList(BaseModel):
    scene_roles: List[NPCSceneRole] = Field(default_factory=list, description="List of scene roles (NPCSceneRole) the NPC plays. A NPCSceneRole consists of an act_number, a scene_number and the role the NPC plays in the scene.")

class NPCConcept(BaseModel):
    name: str = Field(default="", description="Name of the NPC")
    ancestry: str = Field(default="", description="Ancestry of the NPC")
    class_name: str = Field(default="", description="Class of the NPC")
    quest_role: str = Field(default="", description="The role the NPC plays in the quest")
    scene_roles: NPCSceneRolesList = Field(default_factory=list, description="List of NPCSceneRole objects.")

class NPCConceptList(BaseModel):
    npc_concepts: List[NPCConcept] = Field(default_factory=list, description="List of NPC concepts")
    