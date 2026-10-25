from __future__ import annotations
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class NPCConcept(BaseModel):
    identifier: str = Field(default="", description="The one to four word descriptive title of the NPC (e.g., 'young farm boy', 'wise woman', 'the elder', 'the mayor')")
    scenes: list[tuple[int, int]] = Field(default_factory=list, description="A list of scene labels the NPC appears in, where each label is a tuple of (act_number, scene_number)")
    