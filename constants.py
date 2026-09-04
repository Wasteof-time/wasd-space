import json

json_file = open("settings.json", "r", encoding="utf-8")
json_file = json.load(json_file)

res_x = json_file["screen"]["resolution_x"]
res_y = json_file["screen"]["resolution_y"]
vsync = json_file["screen"]["vsync"]
sensitivity = json_file["controls"]["sensitivity"]
