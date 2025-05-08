'''
boot.py
'''

import digitalio
import storage
import supervisor
import usb_hid

from wificom import modes
import board_config

supervisor.status_bar.console = False
supervisor.status_bar.display = False
usb_hid.disable()

button_pin = board_config.ui_pins["button_c"]

if button_pin is not None:
	# Push-to-close button between button_pin and GND
	button = digitalio.DigitalInOut(button_pin)
	button.pull = digitalio.Pull.UP
	drive_enabled = False
	if button.value:
		# Button not pressed: menu, or as requested by software before reboot
		mode = modes.get_mode()
		if mode == modes.MODE_DRIVE and modes.was_requested():
			drive_enabled = True
		elif mode in (modes.MODE_DEV, modes.MODE_DRIVE, modes.MODE_UNKNOWN):
			# This was not requested from software so reset it
			modes.set_mode(modes.MODE_MENU)
	else:
		# Button pressed: Dev Mode
		modes.set_mode(modes.MODE_DEV)
		drive_enabled = True
	print("Mode:", modes.get_mode_str())
	if drive_enabled:
		print("CIRCUITPY drive is writeable")
	else:
		storage.remount("/", False)
		print("CIRCUITPY drive is read-only")
