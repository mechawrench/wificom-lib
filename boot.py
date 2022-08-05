'''
boot.py
'''

# import usb_cdc
# usb_cdc.enable(console=False, data=True)

import board
import digitalio
import storage
# import usb_cdc
import usb_hid

usb_hid.disable()

# push-to-close button between D3 and GND
button = digitalio.DigitalInOut(board.D3)
button.pull = digitalio.Pull.UP
if button.value:
	# button is not pressed
	storage.disable_usb_drive()
	#usb_cdc.enable(console=False, data=True)
