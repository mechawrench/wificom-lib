'''
status.py
Handles status monitoring.
'''

import analogio

class BatteryMonitor:
	'''
	Handles the battery monitor.
	'''
	def __init__(self, pin, empty, full, charging):
		self._monitor = analogio.AnalogIn(pin)
		self._empty = empty
		self._full = full
		self._charging = charging

class StatusDisplay:
	'''
	Handles status display for WiFi/Serial/Punchbag.
	'''
	def __init__(self, ui, battery_monitor):  #pylint:disable=invalid-name
		self._ui = ui
		self._battery_monitor = battery_monitor
		self._mode = ""
		self._line2 = ""
		self._status = ""
	def change(self, mode, line2, status):
		'''
		Set mode, line2 and status and redraw.
		'''
		self._mode = mode
		self._line2 = line2
		self.do(status)
	def do(self, status):  #pylint:disable=invalid-name
		'''
		Set status and redraw trying digirom then string.
		'''
		try:
			status = f"{status.signal_type}{status.turn}"
		except AttributeError:
			pass
		self._status = status
		self.redraw()
	def redraw(self):
		'''
		Redraw screen.
		'''
		self._ui.display_rows([
			f"{self._mode}: {self._status}",
			self._line2,
		])
