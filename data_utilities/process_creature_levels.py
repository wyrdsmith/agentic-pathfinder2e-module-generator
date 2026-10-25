import json;

data = json.load(open('../data/creatures.json', encoding='utf-8'));

for creature in data:
    rawLevel = creature['level'];
    if (not rawLevel or rawLevel == ""):
        creature['level'] = 0
    else:
        creature['level'] = int(rawLevel)

json.dump(data,open('../data/creatures.json','w',encoding='utf-8'),indent=2);