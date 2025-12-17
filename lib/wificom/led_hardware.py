'''
led_hardware.py
Handles the PWM LED and the neopixel.
Separate file for faster importing.
'''

import pwmio
import neopixel

class LedHardware:
	'''
	Handles the PWM LED and the neopixel.
	'''
	def __init__(self, board_config):
		self._led = None
		if board_config.led_pin is not None:
			self._led = pwmio.PWMOut(board_config.led_pin,
				duty_cycle=0x1000, frequency=1000, variable_frequency=True)
		try:
			self._neopixel = neopixel.NeoPixel(**board_config.neopixel, auto_write=False)
		except AttributeError:
			self._neopixel = None
		self._settings = None
	def add_settings(self, settings):
		'''
		Register the settings object (not ready yet at init).
		'''
		self._settings = settings
	@property
	def color(self):
		'''
		Return current color.
		'''
		if self._neopixel is None:
			return None
		return self._neopixel[0]
	def bright(self, color=None):
		'''
		Make LEDs bright, and optionally change neopixel color.
		Don't call before settings are added.
		'''
		if self._led is not None:
			self._led.frequency = 1000
			self._led.duty_cycle = 0xFFFF
		self.change_color(color, self._settings.neopixel_brightness(True) / 100)
	def dim(self, color=None):
		'''
		Make LEDs dim, and optionally change neopixel color.
		Don't call before settings are added.
		'''
		if self._led is not None:
			self._led.frequency = 1000
			self._led.duty_cycle = 0x1000
		self.change_color(color, self._settings.neopixel_brightness(False) / 100)
	def off(self, color=None):
		'''
		Turn LEDs off, and optionally change neopixel color.
		'''
		if self._led is not None:
			self._led.frequency = 1000
			self._led.duty_cycle = 0
		self.change_color(color, 0)
	def change_color(self, color=None, brightness=None):
		'''
		Change neopixel color and/or brightness.
		'''
		if self._neopixel is not None:
			if color is not None:
				self._neopixel.fill(color)
			if brightness is not None:
				self._neopixel.brightness = brightness
			self._neopixel.show()
	def fast_blink(self):
		'''
		Make LED blink quickly.
		'''
		if self._led is not None:
			self._led.frequency = 1
			self._led.duty_cycle = 0x8000
