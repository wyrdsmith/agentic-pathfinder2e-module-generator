from typing import List
from pydantic import BaseModel, Field
from models.act import Act

class Quest(BaseModel):
    name: str = Field(default="", description="The name of the quest")
    theme: str = Field(default="", description="The theme of the quest")
    setting: str = Field(default="", description="The setting of the quest")
    plot_hook: str = Field(default="", description="The hook to get the players involved")
    summary: str = Field(default="", description="A summary of the quest")
    acts: List[Act] = Field(default_factory=list, description="A list of acts in the quest")
    player_count: int = Field(default=4, description="The number of players in the quest")
    party_level: int = Field(default=1, description="The level of the party in the quest")
    xp_value: int = Field(default=1000, description="The xp value of the quest")

        