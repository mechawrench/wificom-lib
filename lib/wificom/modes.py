'''
modes.py
Handles the mode selected at startup.
'''

import alarm

MAGIC = "wificom_mode_01_"
LENGTH = len(MAGIC) + 2

MODE_MENU = "m"
MODE_WIFI = "w"
MODE_SERIAL = "s"
MODE_PUNCHBAG = "p"
MODE_DRIVE = "d"
MODE_SETTINGS = "~"
MODE_DEV = "*"
MODE_UNKNOWN = "?"

REQUESTED_YES = "y"
REQUESTED_NO = "n"

_MODES = "mwspd*?~"

def _mem_str():
	the_bytes = alarm.sleep_memory[0:LENGTH]
	try:
		return the_bytes.decode("ascii")
	except UnicodeError:
		return "??"

def get_mode_str():
	'''
	Return the 2-character data, or "!!" if MAGIC doesn't match.
	'''
	mem_str = _mem_str()
	if mem_str.startswith(MAGIC):
		return mem_str[-2:]
	return "!!"

def get_mode():
	'''
	Return the currently-set mode, defaulting to MODE_UNKNOWN.
	'''
	mode = get_mode_str()[0]
	if mode in _MODES:
		return mode
	return MODE_UNKNOWN

def was_requested():
	'''
	Is the request flag set?
	'''
	req = get_mode_str()[1]
	return req == REQUESTED_YES

def set_mode(mode, requested=True):
	'''
	Set a new mode.
	'''
	if mode not in _MODES:
		raise ValueError(str(mode) + " not a mode")
	req = REQUESTED_YES if requested else REQUESTED_NO
	new_mem_str = MAGIC + mode + req
	alarm.sleep_memory[0:LENGTH] = bytes(new_mem_str, "ascii")

def clear_request():
	'''
	Clear the request flag.
	'''
	set_mode(get_mode(), False)
