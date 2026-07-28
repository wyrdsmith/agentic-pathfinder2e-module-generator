class Location:
    name: str #Name of the location
    description: str #Description of the location
    gm_information: str #Information about the location not included in the description for the GM's eyes only

    def __init__(self, name="", description="", gm_information=""):
        self.name = name
        self.description = description
        self.gm_information = gm_information