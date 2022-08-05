'''
challenger_wifi.py
Handles the WiFi connection for the Challenger board.
'''
import busio 
from digitalio import DigitalInOut
from digitalio import Direction
from adafruit_espatcontrol import adafruit_espatcontrol
from wificom.common.import_secrets import secrets_wifi_ssid,secrets_wifi_password
import adafruit_espatcontrol.adafruit_espatcontrol_socket as socket

# Get wifi details and more from a secrets.py file
try:
	from secrets import secrets
except ImportError:
	print("WiFi secrets are kept in secrets.py, please add them there!")
	raise


class ChallengerWifi:
	# pylint: disable=too-many-arguments
	def __init__(self, uart_rx, uart_tx, reset_pin, boot_pin):
		self.uart = busio.UART(uart_tx, uart_rx, baudrate=11520, receiver_buffer_size=2048)
		esp_boot = DigitalInOut(boot_pin)
		esp_boot.direction = Direction.OUTPUT
		esp_boot.value = True
		self.esp = adafruit_espatcontrol.ESP_ATcontrol(
			self.uart, 115200, reset_pin=DigitalInOut(reset_pin), rts_pin=False, debug=False
		)
		
		socket.set_interface(self.esp)
	def connect(self):
		self.esp.hard_reset()
		first_pass = True
		connected = False
		while connected is not True:
			try:
				if first_pass:
					print("Connecting to WiFi network [" + secrets_wifi_ssid + "]...")
					secrets_payload = {
						'ssid': secrets_wifi_ssid,
						'password': secrets_wifi_password
					}

					# Check status, attempt reconnect if connect attempt fails
					try:
						esp_status = self.esp.status
						if esp_status == 0:
							self.esp.connect(secrets_payload)
					except RuntimeError:
						self.esp.reset()

					print("Connected to WiFi network!")

					first_pass = False
				connected = True
				return [self.esp, socket]
			except (ValueError, RuntimeError, adafruit_espatcontrol.OKError) as e:
				print("Failed to get wifi data, retrying\n", e)
				print("Resetting ESP module")
				self.esp.hard_reset()
				continue