'''
ui.py
Handles the user interface components.
'''

import time
import busio
import digitalio
import displayio
import terminalio
import adafruit_displayio_ssd1306
from adafruit_display_text.label import Label

SCREEN_WIDTH=128
SCREEN_HEIGHT=32
SCREEN_ADDRESS=0x3c
TEXT_ROW_Y_STEP = 11
TEXT_MENU_Y_START = 8

def centre_y_start(num_rows):
	'''
	Decide where to place text depending on number of rows.
	'''
	if num_rows == 1:
		return 15
	if num_rows == 2:
		return 8
	return 4

class UserInterface:
	'''
	Handles the screen, buttons and menus.
	'''
	def __init__(self, display_scl, display_sda, button_a, button_b, button_c):
		# pylint: disable=too-many-arguments
		i2c = busio.I2C(display_scl, display_sda)
		display_bus = displayio.I2CDisplay(i2c, device_address=SCREEN_ADDRESS)
		self._display = adafruit_displayio_ssd1306.SSD1306(
			display_bus, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
		self._buttons = {}
		self._buttons["A"] = digitalio.DigitalInOut(button_a)
		self._buttons["B"] = digitalio.DigitalInOut(button_b)
		self._buttons["C"] = digitalio.DigitalInOut(button_c)
		for button_id in "ABC":
			self._buttons[button_id].pull = digitalio.Pull.UP
	def display_text(self, rows, y_start=None):
		'''
		Display rows of text on the screen.
		'''
		if y_start is None:
			y_start = centre_y_start(len(rows))
		group = displayio.Group()
		y = y_start
		for row in rows:
			label = Label(terminalio.FONT, text=row, color=0xFFFFFF, x=0, y=y)
			group.append(label)
			y += TEXT_ROW_Y_STEP
		self._display.show(group)
	def clear(self):
		'''
		Clear the screen.
		'''
		group = displayio.Group()
		self._display.show(group)
	def _is_button_pressed(self, button_id):
		return not self._buttons[button_id].value
	def is_a_pressed(self):
		'''
		Check if button A is pressed.
		'''
		return self._is_button_pressed("A")
	def is_b_pressed(self):
		'''
		Check if button B is pressed.
		'''
		return self._is_button_pressed("B")
	def is_c_pressed(self):
		'''
		Check if button C is pressed.
		'''
		return self._is_button_pressed("C")
	def menu(self, options, results, cancel_result):
		'''
		Display a menu with the specified options and return the corresponding result.

		If a result is None, that option cannot be activated.
		'''
		selection = 0
		text_rows = options[:]
		while True:
			# pylint: disable=consider-using-enumerate
			for i in range(len(options)):
				if i == selection:
					text_rows[i] = "> " + options[i]
				else:
					text_rows[i] = "  " + options[i]
			self.display_text(text_rows, TEXT_MENU_Y_START - selection * TEXT_ROW_Y_STEP)
			while True:
				if self.is_a_pressed():
					selection += 1
					selection %= len(options)
					time.sleep(0.15)
					break
				if self.is_b_pressed() and results[selection] is not None:
					self.clear()
					return results[selection]
				if self.is_c_pressed() and cancel_result is not None:
					self.clear()
					return cancel_result
