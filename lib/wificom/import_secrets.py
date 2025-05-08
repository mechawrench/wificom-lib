'''
import_secrets.py
Import secrets into variables
'''

import json

secrets_wireless_networks = ""
secrets_user_uuid = ""
secrets_device_uuid = ""
secrets_mqtt_broker = ""
secrets_mqtt_username = ""
secrets_mqtt_password = ""
secrets_imported = False
secrets_error = ""
secrets_error_display = ""

try:
	with open("secrets.json", encoding="utf-8") as json_file:
		secrets = json.load(json_file)

	secrets_wireless_networks = secrets["wireless_networks"]
	secrets_user_uuid = secrets["user_uuid"]
	secrets_device_uuid = secrets["device_uuid"]
	secrets_mqtt_broker = secrets["broker"]
	secrets_mqtt_username = secrets["mqtt_username"]
	secrets_mqtt_password = secrets["mqtt_password"]

	for network in secrets_wireless_networks:  # raises TypeError if not iterable
		#pylint: disable=pointless-statement
		# check keys exist
		network["ssid"]
		network["password"]

	secrets_imported = True

except OSError:
	secrets_error = "secrets.json cannot be loaded, " + \
		"please copy and edit from webapp or secrets.example.json"
	secrets_error_display = "secrets missing"
except ValueError:
	secrets_error = "Syntax error in secrets.json"
	secrets_error_display = "secrets syntax"
except TypeError as e:
	secrets_error = "Error in wireless_networks in secrets.json: " + str(e)
	secrets_error_display = "secrets networks"
except KeyError as e:
	secrets_error = "Missing field in secrets.json: " + str(e)
	secrets_error_display = "secrets " + str(e)
