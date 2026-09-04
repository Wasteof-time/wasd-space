import json

json_file = open("settings.json", "r", encoding="utf-8")
json_file = json.load(json_file)

res_x = json_file["screen"]["resolution_x"]
res_y = json_file["screen"]["resolution_y"]
vsync = json_file["screen"]["vsync"]
fs = json_file["screen"]["fullscreen"]
sensitivity = json_file["controls"]["sensitivity"]

player_acceleration = json_file["player"]["acceleration"]
player_max_speed = json_file["player"]["max_speed"]
player_drag = json_file["player"]["drag"]
player_stop_epsilon = json_file["player"]["stop_epsilon"]
player_width = json_file["player"]["width"]
player_height = json_file["player"]["height"]
