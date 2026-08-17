from typing import List
from pydantic import BaseModel, Field

class Enemy(BaseModel):
    level: int = Field(default=1, description="Level of the enemy creature")
    name: str = Field(default="", description="Name of the enemy creature")
    description: str = Field(default="", description="Description of the enemy creature")
    xp_value: int = Field(default=40, description="XP value of the enemy creature")
    url: str = Field(default="", description="URL to the enemy creature's Archives of Nethys page")