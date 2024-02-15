'''
wifi_nina.py
Handles the WiFi connnection for supported boards.
Currently supported boards:
	- Arduino Nano RP2040 Connect,
	- AirLift co-processor module with RP2040 Board (tested with Pi Pico)
'''
import busio
from digitalio import DigitalInOut
from wificom.import_secrets import secrets_mqtt_broker, \
	secrets_mqtt_username, \
	secrets_mqtt_password, \
	secrets_wireless_networks
from adafruit_esp32spi import adafruit_esp32spi
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_minimqtt.adafruit_minimqtt as MQTT

class Wifi:
	'''
	Handles WiFi connection for supported boards
	'''
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
		for network in secrets_wireless_networks:
			for _ in range(3):
				try:
					print("Connecting to", network['ssid'])
					self.esp.connect_AP(network['ssid'], network['password'])

					mqtt_client = MQTT.MQTT(
						broker=secrets_mqtt_broker,
						username=secrets_mqtt_username.lower(),
						password=secrets_mqtt_password,
						keep_alive=15,
						connect_retries=3,
					)

					MQTT.set_socket(socket, self.esp)

					return mqtt_client
				except Exception as e:  # pylint: disable=broad-except
					print(f"Failed to connect: {type(e)} - {e}")
		return None
