from pydantic import BaseModel, Field

class Location(BaseModel):
    name: str = Field(default="", description="Name of the location")
    description: str = Field(default="", description="Description of the location")
    gm_information: str = Field(default="", description="Information about the location not included in the description for the GM's eyes only")