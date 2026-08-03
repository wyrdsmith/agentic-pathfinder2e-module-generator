from typing import List
from pydantic import BaseModel, Field

class Rewards(BaseModel):
    value: int = Field(default=0, description="Total treasure value of encounter after threat level modification in gold pieces")
    description: str = Field(default="", description="Detailed description of items and currency awarded")
    boons: List[str] = Field(default_factory=list, description="List of boons awarded (strings)")
    key_items: List[str] = Field(default_factory=list, description="List of key items awarded (strings)")
    
    def add_boon(self, boon: str):
        self.boons.append(boon)

    def add_key_item(self, key_item: str):
        self.key_items.append(key_item)