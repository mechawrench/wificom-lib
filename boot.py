'''
boot.py
'''

import board
import digitalio
import storage
# import usb_cdc
import usb_hid

usb_hid.disable()

if board.board_id == "arduino_nano_rp2040_connect":
	button_pin = board.D3
elif board.board_id == "raspberry_pi_pico":
	button_pin = board.GP3
else:
	button_pin = None

if button_pin is not None:
	# push-to-close button between button_pin and GND
	button = digitalio.DigitalInOut(button_pin)
	button.pull = digitalio.Pull.UP
	if button.value:
		# button is not pressed
		storage.disable_usb_drive()
		# data port not currently supported by WiFiCom
		#usb_cdc.enable(console=False, data=True)
