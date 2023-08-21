'''
boot.py
'''

import time
import digitalio
import storage
import supervisor
import usb_hid

from wificom import nvm
import board_config

BUTTON_NOT_PRESSED = 0
BUTTON_RELEASED = 1
BUTTON_HELD = 2

STATE_NORMAL = 0
STATE_DRIVE = 1
STATE_SERIAL = 2

supervisor.status_bar.console = False
supervisor.status_bar.display = False
usb_hid.disable()

button_pin = board_config.ui_pins["button_c"]
led_pin = board_config.led_pin

if button_pin is not None:
	led = digitalio.DigitalInOut(led_pin)
	led.switch_to_output()
	# push-to-close button between button_pin and GND
	button = digitalio.DigitalInOut(button_pin)
	button.pull = digitalio.Pull.UP
	if button.value:
		button_result = BUTTON_NOT_PRESSED
	else:
		# button is pressed
		led.value = True
		time_start = time.monotonic()
		while True:
			if button.value:
				button_result = BUTTON_RELEASED
				break
			if time.monotonic() - time_start > 1:
				button_result = BUTTON_HELD
				break
		led.value = False

	# button not pressed: WiFiCom with defaults or menu selection
	# button released when LED came on: WiFiCom dev mode
	# button held until LED went off: serial-only without drive or console
	if button_result == BUTTON_NOT_PRESSED:
		mode = nvm.get_mode()
		if mode in [nvm.MODE_MENU, nvm.MODE_WIFI, nvm.MODE_PUNCHBAG]:
			state = STATE_NORMAL
		elif mode == nvm.MODE_SERIAL:
			state = STATE_SERIAL
		elif mode == nvm.MODE_DRIVE:
			state = STATE_DRIVE
		elif mode == nvm.MODE_DEV:
			# this was not requested from software so reset it
			nvm.set_mode(nvm.MODE_MENU)
			state = STATE_NORMAL
	elif button_result == BUTTON_RELEASED:
		nvm.set_mode(nvm.MODE_DEV)
		state = STATE_DRIVE
	elif button_result == BUTTON_HELD:
		nvm.set_mode(nvm.MODE_SERIAL)
		state = STATE_SERIAL

	print("Mode:", nvm.get_mode_str())
	if state == STATE_DRIVE:
		print("CIRCUITPY drive is writeable")
	else:
		storage.remount("/", False)
		print("CIRCUITPY drive is read-only")
