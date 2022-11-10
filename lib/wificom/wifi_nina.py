'''
wifi_nina.py
Handles the WiFi connnection for supported boards.
Currently supported boards:
	- Arduino Nano RP2040 Connect,
	- AirLift co-processor module with RP2040 Board (tested with Pi Pico)
'''
import busio
from digitalio import DigitalInOut
from wificom.import_secrets import secrets_wifi_ssid,secrets_wifi_password, \
	secrets_mqtt_broker, \
	secrets_mqtt_username, \
	secrets_mqtt_password
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_minimqtt.adafruit_minimqtt as MQTT


class Wifi:
	'''
	Handles WiFi connection for supported boards
	'''
	# pylint: disable=too-many-arguments
	def __init__(self, esp32_cs, esp32_busy, esp32_reset, esp32_sck, esp32_mosi, esp32_miso):
		self.esp32_cs = DigitalInOut(esp32_cs)
		self.esp32_ready = DigitalInOut(esp32_busy)
		self.esp32_reset = DigitalInOut(esp32_reset)
		self.spi = busio.SPI(esp32_sck, esp32_mosi, esp32_miso)
		self.esp = adafruit_esp32spi.ESP_SPIcontrol(self.spi, self.esp32_cs, self.esp32_ready, \
			 self.esp32_reset)
		socket.set_interface(self.esp)

	def connect(self):
		'''
		Connect to a supported board's WiFi network
		'''
		print("Connecting to WiFi network [" + secrets_wifi_ssid + "]...")

		secrets_payload = {
			'ssid': secrets_wifi_ssid,
			'password': secrets_wifi_password
		}

		wifi_manager = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(self.esp, secrets_payload)

		# Check status, attempt reconnect if connect attempt fails
		try:
			esp_status = self.esp.status
			if esp_status == 0:
				wifi_manager.connect()
		except RuntimeError:
			wifi_manager.reset()

		print("Connected to WiFi network!")

		mqtt_client = MQTT.MQTT(
			broker=secrets_mqtt_broker,
			username=secrets_mqtt_username.lower(),
			password=secrets_mqtt_password,
		)

		# Return esp to use with mqtt client
		return self.esp, mqtt_client
