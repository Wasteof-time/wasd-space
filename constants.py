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
# Highway cruise with no extra input. Raise to make the road always feel faster.
player_default_speed = json_file["player"]["default_speed"]
player_drag = json_file["player"]["drag"]
player_stop_epsilon = json_file["player"]["stop_epsilon"]
player_width = json_file["player"]["width"]
player_height = json_file["player"]["height"]
# Vertical rest pose as a fraction of screen height (0 = top, 1 = bottom).
player_rest_y = json_file["player"]["rest_y"]
# Extra upward travel at max speed, as a fraction of screen height.
# Bigger value = the car sits further up the road when you accelerate.
player_speed_reach = json_file["player"]["speed_reach"]

# Pivot of the roof gun, as a fraction of the weapon sprite (0–1).
# 0.5, 0.75 = center x, three-quarters down. Tweak until the barrel swings cleanly.
weapon_pivot_x = json_file["weapon"]["pivot_x"]
weapon_pivot_y = json_file["weapon"]["pivot_y"]

# Asphalt fill for the whole highway.
_road_hex = json_file["road"]["color"].lstrip("#")
road_color = (
    int(_road_hex[0:2], 16),
    int(_road_hex[2:4], 16),
    int(_road_hex[4:6], 16),
)
road_lane_count = json_file["road"]["lane_count"]
# Multiplier on player speed for highway scroll (stripes and bikes).
road_speed = json_file["road"]["speed"]

# Milliseconds between bike spawns from the top of the road.
bike_spawn_ms = json_file["bike"]["spawn_ms"]
# Fraction of random per-bike speed variation (0 = all bikes match the road).
# Each bike's downward speed is multiplied by a random factor in [1-v, 1+v].
bike_speed_variation = json_file["bike"]["speed_variation"]

# Speed of player bullets, in pixels per second.
bullet_velocity = json_file["bullet"]["velocity"]
# Minimum seconds between shots.
bullet_cooldown = json_file["bullet"]["cooldown"]
# Number of wall bounces a charged ricochet shot survives before leaving.
bullet_ricoshotcount = json_file["bullet"]["ricoshotcount"]
# The ricochet shot flies this many times faster than the normal bullet.
bullet_ricochet_speed_multiplier = json_file["bullet"]["ricochet_speed_multiplier"]
# Seconds of holding right-click required to fully charge a ricochet shot.
bullet_chargetime = json_file["bullet"]["chargetime"]
