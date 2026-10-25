import json;

data = json.load(open('../data/items.json', encoding='utf-8'));

for item in data:
    rawLevel = item['level'];
    if (not rawLevel or rawLevel == ""):
        item['level'] = 0
    else:
        item['level'] = int(rawLevel)

json.dump(data,open('../data/items.json','w',encoding='utf-8'),indent=2);