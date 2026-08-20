from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from models.enemy import Enemy
from models.obstacle import Obstacle
from models.hazard import Hazard
from models.rewards import Rewards
from models.npc_influence import NPCInfluenceInfo

class Encounter(BaseModel):
    level: int = Field(default=1, description="Actual level of the encounter after modifiers")
    encounter_type: Literal["combat", "social", "skill challenge", "hazard"] = Field(default="combat", description="Either combat, social, skill challenge or hazard")
    threat_level: Literal["Trivial", "Low", "Moderate", "Severe", "Extreme"] = Field(default="Moderate", description="Either Trivial, Low, Moderate, Severe or Extreme")
    xp_value: int = Field(default=80, description="Based on encounter level after modification by threat level.")
    xp_budget: int = Field(default=80, description="The budget of XP for the encounter after encounter modifiers (threat level and party size) have been applied.")
    introduction: str = Field(default="", description="Line spoken to introduce the encounter")
    resolution: str = Field(default="", description="Line spoken to conclude the encounter")
    description: str = Field(default="", description="Detailed description of the encounter")
    gm_information: str = Field(default="", description="Information about the encounter for the GM's eyes only")
    turns: int = Field(default=0, description="The number of turns the party has to overcome this encounter if it's a social or skill challenge encounter")
    victory_points_required: int = Field(default=0, description="The number of victory points required to overcome this encounter if it's a skill challenge encounter")
    enemies: List[Enemy] = Field(default_factory=list, description="List of enemies in the encounter for combat encounters")
    npc_influence_info: List[NPCInfluenceInfo] = Field(default_factory=list, description="List of NPCInfluenceInfo objects for NPCs in the encounter for social encounters")
    obstacles: List[Obstacle] = Field(default_factory=list, description="List of obstacles in the encounter for skill challenge encounters")
    hazard: Optional[Hazard] = Field(default=None, description="Hazard in the encounter for hazard encounters")
    reward_budget: int = Field(default=0, description="The budget for rewards for the encounter after encounter modifiers (threat level) have been applied.")
    rewards: Optional[Rewards] = Field(default=None, description="Reward object to be filled with rewards data")
