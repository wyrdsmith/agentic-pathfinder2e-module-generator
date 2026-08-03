from pydantic import BaseModel, Field

class QuestConcept(BaseModel):
    name: str = Field(description="A catchy name for the adventure")
    theme: str = Field(description="The primary theme (e.g., Horror, Investigation, High Fantasy)")
    setting: str = Field(description="The general location (e.g., A bustling city, a dark forest)")
    plot_hook: str = Field(description="The narrative hook to get the players involved")
    summary: str = Field(description="A summary of the overarching plot that is long enough to be used as a basis for three-act story structure")