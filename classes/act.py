from typing import List
from classes.scene import Scene

class Act:
    act_number: int #The number of the act in the quest
    summary: str #A summary of what happens in the act
    scenes: List[Scene] #A list of scenes in the act

    def __init__(self, act_number = 1, summary = "", scenes = []):
        self.act_number = act_number
        self.summary = summary
        self.scenes = scenes