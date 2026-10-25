import json;

data = json.load(open('../data/json/skill-actions.json', encoding='utf-8'));

sample_tasks = [];

for skill_action in data:
    skill_name = skill_action['skill'];
    skill_action_name = skill_action['name'];
    for sample_task in skill_action['sample_tasks']:
        sample_task['skill'] = skill_name;
        sample_task['action'] = skill_action_name;
        sample_tasks.append(sample_task);

with open('../data/json/skill-action-sample-tasks.json', 'w', encoding='utf-8') as f:
    json.dump(sample_tasks, f, indent=2, ensure_ascii=False);