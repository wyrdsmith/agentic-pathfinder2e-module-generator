from typing import List
from pydantic import BaseModel, Field

class Hazard(BaseModel):
    name: str = Field(default="", description="The name of the hazard")
    level: int = Field(default=0, description="The level of the hazard")
    hazard_type: str = Field(default="", description="The type of the hazard")
    traits: List[str] = Field(default_factory=list, description="The trait of the hazard")
    description: str = Field(default="", description="The description of the hazard")
    url: str = Field(default="", description="The URL to the hazard's Archives of Nethys page")