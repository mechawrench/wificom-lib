'''
import_secrets.py
Import secrets into variables
'''

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
	from secrets import secrets

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

except ImportError:
	secrets_error = "secrets.py is missing, please copy and edit from webapp or secrets.example.py"
	secrets_error_display = "secrets.py missing"
except SyntaxError:
	secrets_error = "Syntax error in secrets.py"
	secrets_error_display = "secrets.py syntax"
except TypeError as e:
	secrets_error = "Error in wireless_networks in secrets.py: " + str(e)
	secrets_error_display = "secrets.py networks"
except KeyError as e:
	secrets_error = "Missing field in secrets.py: " + str(e)
	secrets_error_display = "secrets " + str(e)
