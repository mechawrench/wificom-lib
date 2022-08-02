import board
import busio
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from wificom.common.import_secrets import *

try:
    from secrets import secrets
except ImportError:
    print("Wifi details not found, update secrets.py")
    raise


#ESP32 Setup on Pico:
esp32_cs = DigitalInOut(board.GP13)
esp32_ready = DigitalInOut(board.GP14)
esp32_reset = DigitalInOut(board.GP15)
spi = busio.SPI(board.GP10, board.GP11, board.GP12)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

socket.set_interface(esp)

class RP2040PicoAirlift:
	def connect_to_ssid():
		print("Connecting to WiFi network [" + secrets['ssid'] + "]...")
		wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets)

		try:
			s = esp.status
			if s == 0:
				wifi.connect()
		except RuntimeError:
				wifi.reset()

		print("Connected!")
		
		return True