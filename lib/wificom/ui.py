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
from adafruit_display_text.bitmap_label import Label
from wificom.sound import PIOSound

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
	def __init__(self, display_scl, display_sda, button_a, button_b, button_c, speaker):
		# pylint: disable=too-many-arguments
		self._display = None
		self.display_error = None
		if None in (display_scl, display_sda, button_a, button_b):
			self.display_error = "UI pins not set"
		else:
			try:
				i2c = busio.I2C(display_scl, display_sda)
				display_bus = displayio.I2CDisplay(
					i2c, device_address=SCREEN_ADDRESS)
				self._display = adafruit_displayio_ssd1306.SSD1306(
					display_bus, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
			except Exception as ex:  #pylint: disable=broad-except
				self.display_error = ex
		self._buttons = {}
		if self._display is not None:
			self._buttons["A"] = digitalio.DigitalInOut(button_a)
			self._buttons["B"] = digitalio.DigitalInOut(button_b)
			self._buttons["C"] = digitalio.DigitalInOut(button_c)
			for button_id in "ABC":
				self._buttons[button_id].pull = digitalio.Pull.UP
		else:
			# Physical button C takes the B role
			self._buttons["B"] = digitalio.DigitalInOut(button_c)
			self._buttons["B"].pull = digitalio.Pull.UP
			self._buttons["A"] = None
			self._buttons["C"] = None
		self._speaker = PIOSound(speaker)
		self.audio_base_freq = 1000
	@property
	def has_display(self):
		'''
		Whether we have a display.
		'''
		return self._display is not None
	def display_rows(self, rows, y_start=None):
		'''
		Display rows of text on the screen. Ignored if there is no screen.
		'''
		if not self.has_display:
			return
		if y_start is None:
			y_start = centre_y_start(len(rows))
		group = displayio.Group()
		y = y_start
		for row in rows:
			label = Label(terminalio.FONT, text=row, color=0xFFFFFF, x=0, y=y)
			group.append(label)
			y += TEXT_ROW_Y_STEP
		self._display.show(group)
	def display_text(self, text, y_start=None):
		'''
		Display text on the screen, lines divided with linefeeds.
		Ignored if there is no screen.
		'''
		self.display_rows(text.split("\n"), y_start)
	def clear(self):
		'''
		Clear the screen. Ignored if there is no screen.
		'''
		if not self.has_display:
			return
		group = displayio.Group()
		self._display.show(group)
	def _is_button_pressed(self, button_id):
		button = self._buttons[button_id]
		if button is None:
			return False
		return not button.value
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
	def beep_normal(self):
		'''
		A normal beep.
		'''
		f = self.audio_base_freq
		self._speaker.play_one(f, 0.15)
	def beep_activate(self):
		'''
		Beep for when a menu item is activated.
		'''
		f = self.audio_base_freq
		self._speaker.play_one(f*2, 0.15)
	def beep_error(self):
		'''
		Beep for errors.
		'''
		f = self.audio_base_freq
		self._speaker.play_one(f/2, 0.3)
	def beep_cancel(self):
		'''
		Beep for cancelling out of a menu.
		'''
		f = self.audio_base_freq
		self._speaker.play([(f, 0.15), (f/2, 0.15)])
	def menu(self, options, results, cancel_result):
		'''
		Display a menu with the specified options and return the corresponding result.

		If a result is None, that option cannot be activated.
		Should only be called if there is a screen.
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
			self.display_rows(text_rows, TEXT_MENU_Y_START - selection * TEXT_ROW_Y_STEP)
			time.sleep(0.15)
			while True:
				if self.is_a_pressed():
					selection += 1
					selection %= len(options)
					self.beep_normal()
					break
				if self.is_b_pressed():
					if results[selection] is not None:
						self.beep_activate()
						self.clear()
						return results[selection]
					self.beep_error()
					break
				if self.is_c_pressed():
					if cancel_result is not None:
						self.beep_cancel()
						self.clear()
						return cancel_result
					self.beep_error()
					break
