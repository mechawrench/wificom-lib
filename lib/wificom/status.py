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
	def ratio(self):
		'''
		Return battery fullness 0-1, or None if charging.
		'''
		reading = self._monitor.value
		if reading >= self._charging:
			return None
		if reading < self._empty:
			reading = self._empty
		if reading > self._full:
			reading = self._full
		return (reading - self._empty) / (self._full - self._empty)
	def meter(self):
		'''
		Return text representing fullness, or a message if charging.
		'''
		sections = 5
		ratio = self.ratio()
		if ratio is None:
			return "(On USB)"
		filled = (int)(sections * ratio + 0.5)
		unfilled = sections - filled
		return "[" + "=" * filled + " " * unfilled + "]"

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
		self._show_battery = True
	def change(self, mode, line2, status, show_battery=True):
		'''
		Set mode, line2 and status and redraw.
		'''
		self._mode = mode
		self._line2 = line2
		self._show_battery = show_battery
		self.do(status)
	def do(self, status):  #pylint:disable=invalid-name
		'''
		Set status and redraw trying digirom then string.
		'''
		try:
			guide = "hold vpet steady" if status.turn == 1 else "push vpet button"
			status = f"{status.signal_type}{status.turn}: {guide}"
		except AttributeError:
			pass
		self._status = status
		self.redraw()
	def redraw(self):
		'''
		Redraw screen.
		'''
		rows = [
			self._mode,
			self._line2,
			self._status,
		]
		if self._show_battery and self._battery_monitor is not None:
			rows[0] += " " + self._battery_monitor.meter()
		self._ui.display_rows(rows)
