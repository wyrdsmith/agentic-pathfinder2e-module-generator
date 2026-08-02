import json;

data = json.load(open('../data/items.json', encoding='utf-8'));

for item in data:
    rawPrice = item['price'];

    if (type(rawPrice) == int or type(rawPrice) == float):
        continue

    if ("Varies" in rawPrice):
        item['price'] = -1
        continue
    
    if not rawPrice or rawPrice == "":
        item['price'] = 0
        continue

    parts = rawPrice.split(" ");
    if len(parts) <= 1:
        item['price'] = 0
        continue

    baseValue = parts[0];
    currency = parts[1];

    if (not baseValue or baseValue == ""):
        item['price'] = 0
        continue

    if (not currency or currency != "cp" or currency != "sp" or currency != "gp" or currency != "pp"):
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

json.dump(data,open('../data/items.json','w',encoding='utf-8'),indent=2);