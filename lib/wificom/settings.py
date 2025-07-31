'''
settings.py
Handles the stored settings.
'''

import json

class Settings:
	'''
	Stores settings.
	Init: load json file from filepath. Try to save it if not present, or if keys added.
	`error` property becomes string or None.
	'''
	def __init__(self, filepath):
		self._filepath = filepath
		self._sound_on = True
		self._turn_1_delay = 3
		self._turn_1_delay_options = [0, 3, 5, -1]
		self._try_write = True
		self._changed = False
		self.error = None
		try:
			with open(self._filepath, encoding="utf-8") as json_file:
				data = json.load(json_file)
			if "sound_on" in data:
				self._sound_on = bool(data["sound_on"])
			else:
				self._changed = True
			if "turn_1_delay" in data:
				delay = data["turn_1_delay"]
				_ = delay + 1  # Type check
				self._turn_1_delay = delay
			else:
				self._changed = True
			if "turn_1_delay_options" in data:
				opts = data["turn_1_delay_options"]
				for opt in opts:
					_ = opt + 1  # Type check
				self._turn_1_delay_options = opts
			else:
				self._changed = True
			self.save()  # Save if new keys were added
		except OSError as e:
			if e.errno == 2:
				self._changed = True
				self.save(error_default=f"{self._filepath} not found: creating with defaults")
			else:
				self.error = f"Error reading {self._filepath}: {str(e)}"
				self._try_write = False
		except (ValueError, TypeError) as e:
			self.error = f"Error in {self._filepath}: {str(e)}"
			self._try_write = False
	def save(self, error_default=None):
		'''
		Write settings back to file.
		Return True if there were changes to save, False if not.
		`error` property becomes string or None.
		'''
		self.error = error_default
		if not self._changed:
			return False
		if not self._try_write:
			self.error = "Not overwriting bad file"
			return True
		data = {
			"sound_on": self._sound_on,
			"turn_1_delay": self._turn_1_delay,
			"turn_1_delay_options": self._turn_1_delay_options,
		}
		try:
			with open(self._filepath, "w", encoding="utf-8") as json_file:
				json.dump(data, json_file)
			self._changed = False
		except OSError as e:
			self.error = "Can't save settings: " + str(e)
		return True
	@property
	def sound_on(self):
		'''
		Whether the sound is on.
		'''
		return self._sound_on
	@sound_on.setter
	def sound_on(self, value):
		self._sound_on = value
		self._changed = True
	@property
	def turn_1_button(self):
		'''
		Whether user presses the button for a turn 1 digirom. Read-only.
		'''
		return self._turn_1_delay < 0
	@property
	def turn_1_delay(self):
		'''
		Delay in seconds between receiving a turn 1 digirom and first execution.
		Negative number for button press.
		'''
		return self._turn_1_delay
	@turn_1_delay.setter
	def turn_1_delay(self, value):
		self._turn_1_delay = value
		self._changed = True
	def turn_1_delay_options(self):
		'''
		(Current index, turn 1 delays) for menu.
		List includes current value if not already present.
		'''
		current = self._turn_1_delay
		current_tenths = round(current * 10)
		options = self._turn_1_delay_options[:]  # Copy
		options_tenths = [round(opt * 10) for opt in options]
		try:
			current_index = options_tenths.index(current_tenths)
			return (current_index, options)
		except ValueError:
			return (0, [current] + options)
	def initial_delay(self, turn, on_serial):
		'''
		Delay before first execution of new digirom.
		'''
		delay = self.turn_1_delay
		if turn != 1 or self.turn_1_button:
			delay = 0
		if delay < 1 and on_serial:
			delay = 1
		return delay
