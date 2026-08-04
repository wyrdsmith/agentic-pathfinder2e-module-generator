from pydantic import BaseModel, Field

class QuestConcept(BaseModel):
    name: str = Field(description="A catchy name for the adventure")
    theme: str = Field(description="The primary theme (e.g., Horror, Investigation, High Fantasy)")
    setting: str = Field(description="The general location (e.g., A bustling city, a dark forest)")
    plot_hook: str = Field(description="The basic premise of the quest and briefly describes the goal or conflict of the quest and its resolution")