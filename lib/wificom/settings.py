'''
settings.py
Handles the stored settings.
'''

import json

class Settings:
	'''
	Stores settings.
	Init: load json file from filepath. Try to save it if not present.
	`error` property becomes string or None.
	'''
	def __init__(self, filepath):
		self._filepath = filepath
		self._sound_on = True
		self._try_write = True
		self._changed = False
		self.error = None
		try:
			with open(self._filepath, encoding="utf-8") as json_file:
				data = json.load(json_file)
			self._sound_on = data.get("sound_on", True)
		except OSError as e:
			if e.errno == 2:
				self._changed = True
				self.save(error_default=f"{self._filepath} not found: using and saving defaults")
			else:
				self.error = f"Error reading {self._filepath}: {str(e)}"
				self._try_write = False
		except ValueError:
			self.error = f"Syntax error in {self._filepath}"
			self._try_write = False
	def save(self, error_default=None):
		'''
		Write settings back to file. `error` property becomes string or None.
		'''
		self.error = error_default
		if not self._changed:
			return
		if not self._try_write:
			self.error = "Not overwriting bad file"
			return
		data = {"sound_on": self._sound_on}
		try:
			with open(self._filepath, "w", encoding="utf-8") as json_file:
				json.dump(data, json_file)
			self._changed = False
		except OSError as e:
			self.error = "Can't save settings: " + str(e)
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
