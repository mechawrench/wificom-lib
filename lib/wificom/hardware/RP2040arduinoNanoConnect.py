from . import *
import board
from wificom.common.importSecrets import *
import board
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

wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets)

class RP2040ArduinoNanoConnect:
	def connectToSsid():
		print("Connecting to WiFi network [" + secrets_device_uuid + "]...")

		wifi.connect()

		print("Connected!")
		
		return True