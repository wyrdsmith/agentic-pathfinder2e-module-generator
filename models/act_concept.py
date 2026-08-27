from typing import List
from pydantic import BaseModel, Field

class ActConcept(BaseModel):
    summary: str = Field(description="A detailed summary of the events in this act")
