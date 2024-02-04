'''
ui.py
Handles the user interface components.
'''

import time
import analogio
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
	Handles the screen, buttons, menus, speaker and LED.
	'''
	#pylint:disable=too-many-instance-attributes
	def __init__(self, display_scl, display_sda, button_a, button_b, button_c, speaker, led_pwm):
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
			except Exception as e:  # pylint: disable=broad-except
				self.display_error = e
		self._buttons = {}
		if self._display is not None:
			self._buttons["A"] = digitalio.DigitalInOut(button_a)
			self._buttons["B"] = digitalio.DigitalInOut(button_b)
			self._buttons["C"] = digitalio.DigitalInOut(button_c)
			for button_id in "ABC":
				self._buttons[button_id].pull = digitalio.Pull.UP
		else:
			# Physical button C can be any button in specified cases
			self._buttons["C"] = digitalio.DigitalInOut(button_c)
			self._buttons["C"].pull = digitalio.Pull.UP
			self._buttons["A"] = self._buttons["C"]
			self._buttons["B"] = self._buttons["C"]
		self._speaker = PIOSound(speaker)
		self.sound_on = True
		self.audio_base_freq = 1000
		self._led = led_pwm
		self._battery_monitor = None
		self._battery_empty = None
		self._battery_full = None
		self._battery_charging = None
	def setup_battery_monitor(self, pin, empty, full, charging):
		'''
		Set up the battery monitor.
		'''
		self._battery_monitor = analogio.AnalogIn(pin)
		self._battery_empty = empty
		self._battery_full = full
		self._battery_charging = charging
	@property
	def sound_on(self):
		'''
		Whether the sound is on.
		'''
		return self._speaker.sound_on
	@sound_on.setter
	def sound_on(self, value):
		self._speaker.sound_on = value
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
	def _is_button_pressed(self, button_id, do_no_display):
		button = self._buttons[button_id]
		if self._display is None and not do_no_display:
			return False
		return not button.value
	def is_a_pressed(self, do_no_display=False):
		'''
		Check if button A is pressed.
		'''
		return self._is_button_pressed("A", do_no_display)
	def is_b_pressed(self, do_no_display=False):
		'''
		Check if button B is pressed.
		'''
		return self._is_button_pressed("B", do_no_display)
	def is_c_pressed(self, do_no_display=False):
		'''
		Check if button C is pressed.
		'''
		return self._is_button_pressed("C", do_no_display)
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
	def beep_ready(self):
		'''
		Beep for when menu/wifi is ready.
		'''
		f = self.audio_base_freq
		self._speaker.play([(f, 0.15), (f*2, 0.15)])
	def beep_failure(self):
		'''
		Beep to indicate failure (blocking).
		'''
		for _ in range(3):
			self.beep_error()
			time.sleep(0.8)
	def led_bright(self):
		'''
		Make LED bright.
		'''
		if self._led is not None:
			self._led.frequency = 1000
			self._led.duty_cycle = 0xFFFF
	def led_dim(self):
		'''
		Make LED dim.
		'''
		if self._led is not None:
			self._led.frequency = 1000
			self._led.duty_cycle = 0x1000
	def led_off(self):
		'''
		Turn LED off.
		'''
		if self._led is not None:
			self._led.frequency = 1000
			self._led.duty_cycle = 0
	def led_fast_blink(self):
		'''
		Make LED blink quickly.
		'''
		if self._led is not None:
			self._led.frequency = 1
			self._led.duty_cycle = 0x8000
	def menu(self, options, results, cancel_result):
		'''
		Display a menu with the specified options and return the corresponding result.

		If a result is None, that option cannot be activated.
		Should only be called if there is a screen.
		'''
		selection = 0
		text_rows = options[:]
		while True:
			for i in range(len(options)):  # pylint: disable=consider-using-enumerate
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
