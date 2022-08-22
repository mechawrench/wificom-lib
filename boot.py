'''
boot.py
'''

import time
import board
import digitalio
import storage
import usb_cdc
import usb_hid

# pylint: disable=invalid-name
BUTTON_NOT_PRESSED = 0
BUTTON_RELEASED = 1
BUTTON_HELD = 2
# pylint: enable=invalid-name

usb_hid.disable()

if board.board_id == "arduino_nano_rp2040_connect":
	button_pin = board.D3
elif board.board_id == "raspberry_pi_pico":
	button_pin = board.GP3
else:
	button_pin = None

if button_pin is not None:
	led = digitalio.DigitalInOut(board.LED)
	led.switch_to_output()
	# push-to-close button between button_pin and GND
	button = digitalio.DigitalInOut(button_pin)
	button.pull = digitalio.Pull.UP
	if button.value:
		button_state = BUTTON_NOT_PRESSED
	else:
		# button is pressed
		led.value = True
		time_start = time.monotonic()
		while True:
			if button.value:
				button_state = BUTTON_RELEASED
				break
			if time.monotonic() - time_start > 1:
				button_state = BUTTON_HELD
				break
		led.value = False

	# button not pressed: WiFiCom without drive
	# button released when LED came on: WiFiCom with drive
	# button held until LED went off: serial-only without drive or console
	if button_pin is not None and button_state != BUTTON_RELEASED:
		storage.disable_usb_drive()
	if button_state == BUTTON_HELD:
		usb_cdc.enable(console=False, data=True)
