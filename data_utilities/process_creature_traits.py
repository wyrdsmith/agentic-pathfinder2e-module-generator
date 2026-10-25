import json;

data = json.load(open('../data/json/creatures.json', encoding='utf-8'));

for creature in data:
    traitsString = creature['trait'];
    if (not traitsString or traitsString == ""):
        creature['traits'] = [];
    else:
        creature['traits'] = [trait.strip() for trait in traitsString.split(',')];
    del creature['trait'];

with open('../data/json/creatures.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False);