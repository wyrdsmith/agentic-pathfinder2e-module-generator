import json;

data = json.load(open('../data/json/skill-actions.json', encoding='utf-8'));

for skill_action in data:
    del skill_action['sample_tasks'];

with open('../data/json/skill-actions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False);