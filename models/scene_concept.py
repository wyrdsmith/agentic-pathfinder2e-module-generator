from typing import List, Literal
from pydantic import BaseModel, Field

class SceneConcept(BaseModel):
    summary: str = Field(description="A detailed summary of the events that take place in this scene")
    location: str = Field(description="The general location where this scene takes place")
    encounter_type: Literal["combat", "social", "skill challenge", "hazard"] = Field(
        description="The type of encounter in this scene. A combat encounter involves combat between the player characters and enemies, a social encounter involves social interaction between the player characters and npcs, a skill challenge encounter involves a series of skill checks for the player characters to overcome, and a hazard encounter involves the player characters overcoming a hazard. "
    )
    rest_opportunity: Literal["short rest", "long rest", "No rest opportunity"] = Field(description="An opportunity for the player characters to have a short rest (10 minutes) or a long rest (8 hours) in this scene, especially after a combat or hazard encounter. If no rest opportunity is available, return 'No rest opportunity'.")
    

class SceneList(BaseModel):
    scenes: List[SceneConcept] = Field(description="A list of generated scenes for the act")
