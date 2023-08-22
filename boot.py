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

supervisor.status_bar.console = False
supervisor.status_bar.display = False
usb_hid.disable()

button_pin = board_config.ui_pins["button_c"]
led_pin = board_config.led_pin
has_wifi = board_config.WifiCls is not None

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

	# Button not pressed: default / as requested
	# Button released when LED came on: Dev Mode
	# Button held until LED went off: Serial Mode (WiFiCom) / Dev Mode (P-Com)
	drive_enabled = False
	if button_result == BUTTON_NOT_PRESSED:
		mode = nvm.get_mode()
		if mode == nvm.MODE_DRIVE and nvm.was_requested():
			drive_enabled = True
		elif mode in (nvm.MODE_DEV, nvm.MODE_DRIVE):
			# this was not requested from software so reset it
			nvm.set_mode(nvm.MODE_MENU)
	elif has_wifi and button_result == BUTTON_HELD:
		nvm.set_mode(nvm.MODE_SERIAL)
	elif button_result in (BUTTON_RELEASED, BUTTON_HELD):
		nvm.set_mode(nvm.MODE_DEV)
		drive_enabled = True

	print("Mode:", nvm.get_mode_str())
	if drive_enabled:
		print("CIRCUITPY drive is writeable")
	else:
		storage.remount("/", False)
		print("CIRCUITPY drive is read-only")
