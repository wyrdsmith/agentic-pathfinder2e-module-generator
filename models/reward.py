from typing import List, Literal
from pydantic import BaseModel, Field

class Reward(BaseModel):
    name: str = Field(default="", description="The name of the item or reward")
    reward_type: Literal["item", "boon", "key_item", "currency"] = Field(default="item", description="Type of reward")
    price: float = Field(default=0, description="Value of reward in gold pieces")
    description: str = Field(default="", description="Detailed description of items and currency awarded")
    url: str = Field(default="", description="URL to the item or reward")