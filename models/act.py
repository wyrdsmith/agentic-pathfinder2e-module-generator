from typing import List
from pydantic import BaseModel, Field
from models.scene import Scene

class Act(BaseModel):
    act_number: int = Field(default=1, description="The number of the act in the quest")
    summary: str = Field(default="", description="A summary of what happens in the act")
    scenes: List[Scene] = Field(default_factory=list, description="A list of scenes in the act")
