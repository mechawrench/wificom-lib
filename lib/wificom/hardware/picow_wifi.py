'''
wifi.py
Handles the WiFi connnection for Pico W.
'''
from wificom.common.import_secrets import secrets_wifi_ssid, \
	secrets_wifi_password, \
	secrets_mqtt_broker, \
	secrets_mqtt_username, \
	secrets_mqtt_password
import wifi
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import ssl

class Wifi:
	'''
	Handles WiFi connection for supported boards
	'''
	# pylint: disable=too-many-arguments
	def __init__(self):
		return

	def connect(self):
		'''
		Connect to a supported board's WiFi network
		'''
		print("Connecting to WiFi network [" + secrets_wifi_ssid + "]...")

		secrets_payload = {
			'ssid': secrets_wifi_ssid,
			'password': secrets_wifi_password
		}

		wifi.radio.connect(secrets_payload["ssid"], secrets_payload["password"])

		pool = socketpool.SocketPool(wifi.radio)

		mqtt_client = MQTT.MQTT(
			broker=secrets_mqtt_broker,
			username=secrets_mqtt_username.lower(),
			password=secrets_mqtt_password,
			socket_pool=pool,
			ssl_context=ssl.create_default_context(),
		)

		return pool, mqtt_client
