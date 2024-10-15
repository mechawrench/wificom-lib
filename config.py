'''
config.py
Stores non-secret configuration options.
'''

config = {}

# Sound on: True or False. Will be ignored after first run if you have a screen.
config["sound_on"] = True

# DigiROMs for punchbag menu.
# Note: adding too many DigiROMs may cause slowness or crashing.
config["digiroms"] = [
	("DMOG battle", "V1-FC03-FD02"),
	("PenOG battle", "V1-211F-000F-080F-EABF"),
	("PenX battle", "X1-0159-4379-2E49-@4009"),
	("Twin battle/event", "IC2-0007-^0^207-0007-@400F" + "-0000" * 16),
]
