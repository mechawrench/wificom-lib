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
secrets_error_display = ""

try:
	from secrets import secrets

	secrets_wireless_networks = secrets["wireless_networks"]
	secrets_user_uuid = secrets["user_uuid"]
	secrets_device_uuid = secrets["device_uuid"]
	secrets_mqtt_broker = secrets["broker"]
	secrets_mqtt_username = secrets["mqtt_username"]
	secrets_mqtt_password = secrets["mqtt_password"]
	secrets_imported = True

except ImportError:
	print("secrets.py is missing, please copy and edit from webapp or secrets.example.py")
	secrets_error_display = "secrets.py missing"
except SyntaxError:
	print("Syntax error in secrets.py")
	secrets_error_display = "secrets.py\nSyntaxError"
except KeyError as e:
	print("Missing field in secrets.py")
	print(e)
	secrets_error_display = "secrets.py\nKeyError: " + str(e)
