import json;

data = json.load(open('../data/json/treasure-level.json', encoding='utf-8'));

treasure_encounters = [];

for level in data:
    threat_levels = ['trivial', 'low', 'moderate', 'severe', 'extreme'];
    for threat_level in threat_levels:
        treasure_encounter = {};
        treasure_encounter['level'] = level['level'];
        treasure_encounter['threat_level'] = threat_level.capitalize();
        treasure_encounter['treasure'] = level[threat_level];
        treasure_encounters.append(treasure_encounter);

json.dump(treasure_encounters,open('../data/json/treasure-encounter.json','w',encoding='utf-8'),indent=2);