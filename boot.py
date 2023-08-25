'''
boot.py
'''

import time
import digitalio
import storage
import supervisor
import usb_hid

from wificom import modes
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
		mode = modes.get_mode()
		if mode == modes.MODE_DRIVE and modes.was_requested():
			drive_enabled = True
		elif mode in (modes.MODE_DEV, modes.MODE_DRIVE, modes.MODE_UNKNOWN):
			# this was not requested from software so reset it
			modes.set_mode(modes.MODE_MENU)
	elif has_wifi and button_result == BUTTON_HELD:
		modes.set_mode(modes.MODE_SERIAL)
	elif button_result in (BUTTON_RELEASED, BUTTON_HELD):
		modes.set_mode(modes.MODE_DEV)
		drive_enabled = True
	print("WiFi:", "enabled" if has_wifi else "disabled")
	print("Mode:", modes.get_mode_str())
	if drive_enabled:
		print("CIRCUITPY drive is writeable")
	else:
		storage.remount("/", False)
		print("CIRCUITPY drive is read-only")
