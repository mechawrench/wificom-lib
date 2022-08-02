'''
connect.py
Handles automatic board detection and connection to WiFi
'''
import board

board_id = board.board_id

print("Board ID: ", board_id)

if board_id == "raspberry_pi_pico":
	# pylint: disable=unused-import
	from wificom.hardware.rp2040_pico_airlift import RP2040PicoAirlift, esp
elif board_id == "arduino_nano_rp2040_connect":
	# pylint: disable=unused-import
	from wificom.hardware.rp2040_arduino_nano_connect import RP2040ArduinoNanoConnect, esp

def connect_to_wifi():
	'''
	Connect to WiFi, use appropriate board calls
	'''
	if board_id == "raspberry_pi_pico":
		RP2040PicoAirlift.connect_to_ssid()
	elif board_id == "arduino_nano_rp2040_connect":
		RP2040ArduinoNanoConnect.connect_to_ssid()
	else:
		print("Your board is not currently supported.")
		