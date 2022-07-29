'''
rp2040_arduino_nano_connect.py
Handles the connection to the RP2040 Arduino Nano WiFi Network
'''
import board
from wificom.common.import_secrets import secrets_wifi_ssid,secrets_wifi_password
import busio
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_socket as socket


esp32_cs = DigitalInOut(board.CS1)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

spi = busio.SPI(board.SCK1, board.MOSI1, board.MISO1)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

socket.set_interface(esp)


class RP2040ArduinoNanoConnect:
	'''
	Handles WiFi connection for Arduino Nano Connect board
	'''
	def __init__(self):
		secrets_payload = {'ssid': secrets_wifi_ssid, 'password': secrets_wifi_password}
		self.wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets_payload)

	def connect_to_ssid(self):
		'''
		Connect to the RP2040 Arduino Nano WiFi Network
		'''
		print("Connecting to WiFi network [" + secrets_wifi_ssid + "]...")

		self.wifi.connect()

		print("Connected!")

		return True
