import json;

data = json.load(open('../data/json/items.json', encoding='utf-8'));

categories = [];

for item in data:
    if (item['item_category'] not in categories):
        categories.append(item['item_category']);

categoriesJSON = [];

for category in categories:
    categoriesJSON.append({
        "name": category,
        "summary": ""
    });

json.dump(categoriesJSON,open('../data/json/item-categories.json','w',encoding='utf-8'),indent=2);