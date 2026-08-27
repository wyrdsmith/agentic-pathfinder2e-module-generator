import json;

data = json.load(open('../data/json/items.json', encoding='utf-8'));

for item in data:
    rawPrice = item['price'];

    if (type(rawPrice) == int or type(rawPrice) == float):
        continue

    if ("Varies" in rawPrice):
        item['price'] = -1
        continue
    
    if rawPrice == "":
        item['price'] = 0
        continue

    parts = rawPrice.split(" ");
    if len(parts) <= 1:
        item['price'] = 0
        continue

    baseValue = parts[0];
    currency = parts[1];

    if (baseValue == ""):
        item['price'] = 0
        continue

    if (currency not in ["cp", "sp", "gp", "pp"]):
        item['price'] = 0
        continue

    if (',' in baseValue):
        baseValue = baseValue.replace(',', '');

    if (baseValue == ""):
        item['price'] = 0;
    
    if (currency == "cp"):
        item['price'] = int(baseValue) / 100;
    
    elif (currency == "sp"):
        item['price'] = int(baseValue) / 10;
    
    elif (currency == "pp"):
        item['price'] = int(baseValue) * 10;

    else:
        item['price'] = int(baseValue);

json.dump(data,open('../data/json/items.json','w',encoding='utf-8'),indent=2);