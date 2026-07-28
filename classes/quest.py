from typing import List
from classes.act import Act

class Quest:
    name: str #The name of the quest
    theme: str #The theme of the quest
    setting: str #The setting of the quest
    plot_hook: str #The hook to get the players involved
    summary: str #A summary of the quest
    acts: List[Act] #A list of acts in the quest
    player_count: int #The number of players in the quest
    party_level: int #The level of the party in the quest
    xp_value: int #The xp value of the quest

    def __init__(self, name="", theme="", setting="", plot_hook="", summary="", acts=[], player_count=4, party_level=1):
        self.name = name #The name of the quest
        self.theme = theme #The theme of the quest
        self.setting = setting #The setting of the quest
        self.plot_hook = plot_hook #The hook to get the players involved
        self.summary = summary #A summary of the quest
        self.acts = acts #A list of acts in the quest
        self.player_count = player_count #The number of players in the quest
        self.party_level = party_level #The level of the party in the quest
        self.xp_value = 1000 #The xp value of the quest
        