'''
modes.py
Handles the mode selected at startup.
'''

import microcontroller

MAGIC = "wificom03"
LENGTH = len(MAGIC) + 2

MODE_MENU = "m"
MODE_WIFI = "w"
MODE_SERIAL = "s"
MODE_PUNCHBAG = "p"
MODE_DRIVE = "d"
MODE_DEV = "*"

REQUESTED_YES = "y"
REQUESTED_NO = "n"

_MODES = "mwspd*"

def _nvm_str():
	the_bytes = microcontroller.nvm[0:LENGTH]
	try:
		return the_bytes.decode("ascii")
	except UnicodeError:
		return "??"

def get_mode_str():
	'''
	Return the 2-character data, or "??" if MAGIC doesn't match.
	'''
	nvm_str = _nvm_str()
	if nvm_str.startswith(MAGIC):
		return nvm_str[-2:]
	return "??"

def get_mode():
	'''
	Return the currently-set mode, defaulting to MODE_MENU.
	'''
	mode = get_mode_str()[0]
	if mode in _MODES:
		return mode
	return MODE_MENU

def was_requested():
	'''
	Is the request flag set?
	'''
	req = get_mode_str()[1]
	return req == REQUESTED_YES

def set_mode(mode, requested=True):
	'''
	Set a new mode. Return True if NVM was changed, False otherwise.
	'''
	if mode not in _MODES:
		raise ValueError(str(mode) + " not a mode")
	req = REQUESTED_YES if requested else REQUESTED_NO
	new_nvm_str = MAGIC + mode + req
	if new_nvm_str == _nvm_str():
		return False
	microcontroller.nvm[0:LENGTH] = bytes(new_nvm_str, "ascii")
	return True

def clear_request():
	'''
	Clear the request flag. Return True if NVM was changed, False otherwise.
	'''
	return set_mode(get_mode(), False)
