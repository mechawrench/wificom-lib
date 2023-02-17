'''
wifi_picow.py
Handles the WiFi connnection for Pico W.
'''
import ssl
import time
from wificom.import_secrets import secrets_wireless_networks, \
	secrets_mqtt_broker, \
	secrets_mqtt_username, \
	secrets_mqtt_password
import wifi
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import supervisor

class Wifi:
	'''
	Handles WiFi connection for supported boards
	'''
	# pylint: disable=too-many-arguments
	def __init__(self):
		return

	# pylint: disable=invalid-name
	def connect(self, ui, led):
		'''
		Connect to a supported board's WiFi network
		'''

		# Initialize networking
		num_retries = 1
		connected = False
		while not connected:
			print("Scanning for networks...")
			for network in secrets_wireless_networks:
				retries = num_retries
				while retries > 0:
					#pylint: disable=consider-using-set-comprehension
					found = set([wifi.ssid for wifi in wifi.radio.start_scanning_networks()])
					if network['ssid'] in found:
						print(f"Connecting to {network['ssid']} \
							(attempt {num_retries-retries+1} of {num_retries})...")
						try:
							wifi.radio.connect(network['ssid'], network['password'])
						except ConnectionError as e:
							print("Failed to connect, retrying: ", e)
						#pylint: disable=no-else-break
						if wifi.radio.ipv4_address is not None:
							connected = True
							break
						else:
							retries -= 1
					else:
						retries -= 1
				if connected:
					break
			if not connected:
				while not ui.is_c_pressed():
					ui.display_text("WiFi Failed\nHold C to change")
					ui.beep_error()
					time.sleep(0.7)
					ui.beep_error()
					time.sleep(0.7)
					ui.beep_error()
					led.frequency = 1
					led.duty_cycle = 0x7d0

				ui.beep_cancel()
				time.sleep(0.5)
				supervisor.reload()



		wifi.radio.stop_scanning_networks()

		pool = socketpool.SocketPool(wifi.radio)

		mqtt_client = MQTT.MQTT(
			broker=secrets_mqtt_broker,
			username=secrets_mqtt_username.lower(),
			password=secrets_mqtt_password,
			socket_pool=pool,
			ssl_context=ssl.create_default_context(),
		)

		return mqtt_client
