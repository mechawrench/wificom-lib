'''
import_secrets.py
Import secrets into variables
'''
try:
	from secrets import secrets


	secrets_wifi_ssid = secrets["ssid"]
	secrets_wifi_password = secrets["password"]
	secrets_user_uuid = secrets["user_uuid"]
	secrets_device_uuid = secrets["device_uuid"]
	secrets_mqtt_broker = secrets["broker"]
	secrets_mqtt_username = secrets["mqtt_username"]
	secrets_mqtt_password = secrets["mqtt_password"]


except ImportError:
	print("WiFi/MQTT secrets are kept in secrets.py, please add them there!")
	raise
