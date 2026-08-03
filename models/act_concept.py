from typing import List
from pydantic import BaseModel, Field

class ActConcept(BaseModel):
    act_number: int = Field(description="The number of the act (1, 2, or 3)")
    summary: str = Field(description="A detailed summary of the events in this act")

class ActList(BaseModel):
    acts: List[ActConcept] = Field(description="A list of exactly 3 acts")
