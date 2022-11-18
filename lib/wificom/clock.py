
import rtc

class Clock:
	def __init__(self, wifi):
		self._wifi = wifi
		self._rtc = rtc.RTC()
		self._is_set = False
	def get_time(self):
		if self._is_set:
			return self._rtc.datetime
		now = self._wifi.get_time()
		if now is None:
			return None
		self._rtc.datetime = now
		self._is_set = True
		return now
