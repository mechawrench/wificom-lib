'''
wifi_picow.py
Handles the WiFi connnection for Pico W.
'''
import ssl
from wificom.import_secrets import secrets_wifi_ssid, \
	secrets_wifi_password, \
	secrets_mqtt_broker, \
	secrets_mqtt_username, \
	secrets_mqtt_password
import wifi
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import adafruit_ntp

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

		self.pool = socketpool.SocketPool(wifi.radio)

		mqtt_client = MQTT.MQTT(
			broker=secrets_mqtt_broker,
			username=secrets_mqtt_username.lower(),
			password=secrets_mqtt_password,
			socket_pool=self.pool,
			ssl_context=ssl.create_default_context(),
		)

		return mqtt_client

	def get_time(self):
		try:
			ntp = adafruit_ntp.NTP(self.pool, tz_offset=0)
			return ntp.datetime
		except OSError:
			return None
