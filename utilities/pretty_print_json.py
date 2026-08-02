import json;
import sys;

file = sys.argv[1];

data = json.load(open(file, encoding='utf-8'));

with open(file,'w',encoding='utf-8') as f:
    json.dump(data,f,indent=2);