from os import listdir
from os.path import isfile, join
import json
import sys

path =  sys.argv[1]
onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
print(onlyfiles)

state = {"path": path, "series": []}
for file in onlyfiles:
    state["series"].append({"name": file, "watched": False})

with open('settings/seriesSettings.json', 'w') as settings:
    json.dump(state, settings)
